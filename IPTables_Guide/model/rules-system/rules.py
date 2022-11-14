from packets import PacketType

from enum import Enum
from typing import Dict, List, Optional

class Table:
    FILTER = "filter"
    NAT = "nat"
    MANGLE = "mangle"
    RAW = "raw"
    SECURITY = "security"


class Rule:
    flags: Dict[str, str] = {
    "_protocol": "-p {}",
    "_src": "-s {}",
    "_dest": "-d {}",
    "_match": "-m {}",
    "_jump": "-j {}",
    "_goto": "-g {}",
    "_sport": "--sport {}",
    "_dport": "--dport {}",
    "_in_interface": "-i {}",
    "_out_interface": "-o {}",
    "_ipv6": "-6"
}
    def __init__(
        self,
        iptables: Iptables,
        protocol: Optional[PacketType],
        src: Optional[str],
        dest: Optional[str],
        match: Optional[str],
        jump: Optional[str],
        goto: Optional[str],
        chain: Optional[str],
        sport: Optional[str],
        dport: Optional[str],
        in_interface: Optional[str],
        out_interface: Optional[str],
        table: Table = Table.FILTER,
        ipv6: bool = False,
    ):
        self._iptables = iptables
        chains = iptables.get_chain_names(table)
        self._protocol: Optional[PacketType] = protocol
        self._src: Optional[str] = src,
        self._dest: Optional[str] = dest,
        self._match: str = match
        # maybe check if jump  != chain
        if jump not in chains:
            raise ValueError()
        self._jump: Optional[str] = jump
        if goto not in chains:
            raise ValueError()
        self._goto = goto
        if chain not in chains:
            raise ValueError()
        self._chain: Optional[str] = chain
        self._sport: Optional[str] = sport
        self._dport: Optional[str] = dport
        self._table: Table = table
        self._ipv6: bool = ipv6

    def __str__(self):
        s = ""
        for k, v in self.__dict__.items():
            if k not in Rule.flags or v is None:
                continue
        s += Rule.flags[k].format(v) + " "
        s = s[0:len(s)-1]
        return s


class Iptables:
    def __init__(self):
        self._tables: Dict[str, Dict[str, List[Rule]]] = {
            str(Table.FILTER): {
                "INPUT": [],
                "FORWARD": []
            },
            str(Table.NAT): {
                "PREROUTING": [],
                "INPUT": [],
                "FORWARD": [],
                "POSTROUTING": []
            },
            str(Table.MANGLE): {
                "PREROUTING": [],
                "INPUT": [],
                "FORWARD": [],
                "OUTPUT": [],
                "POSTROUTING": []
            },
            str(Table.RAW): {
                "PREROUTING": [],
                "OUTPUT": []
            },
            str(Table.SECURITY): {
                "INPUT": [],
                "OUTPUT": [],
                "FORWARD": []
            }
        }
    
    def append(self, table: Table, chain: str, rule_specs: Dict[str, Any]):
        if chain in self.get_chain_names(table):
            self._tables[table][chain].append(Rule(**rule_specs))
    
    def delete(self, table: Table, chain: str, rule_num: int):
        if chain in self.get_chain_names(table):
            del self._tables[table][chain][rule_num]

    def insert(self, table: Table, chain: str, rule_specs: Dict[str, Any], rule_num):
        if chain in self.get_chain_names(table):
            self._tables[table][chain].insert(rule_num, Rule(**rule_specs))

    def replace(self, table: Table, chain: str, rule_num: int, rule_specs: Dict[str, Any]):
        pass

    def flush(self, table: Table, chain: str):
        pass

    def new_chain(self, table: Table, chain: str):
        pass

    def delete_chain(self, table: Table, chain: str):
        pass

    def policy(self, table: Table, chain: str, target: str):
        pass

    def rename_chain(self, table: Table, old_chain: str, new_chain: str):
        pass

    def write(self):
        pass

    def read(self):
        pass

    def get_chain_names(self, table: Table) -> List[str]:
        return list(self._tables[table].keys())
