from enum import Enum
from typing import List, Dict, Optional
# from IPTables_Guide.model.packets import Packet
# from rule_generator import Rule

# Remove once the real class can be imported
class Rule:
    pass

class Packet:
    pass

class Table(Enum):
    FILTER = "filter"
    NAT = "nat"
    MANGLE = "mangle"

class Chain(Enum):
    INPUT = "input"
    OUTPUT = "output"
    PREROUTING = "prerouting"
    POSTROUTING = "postrouting"
    FORWARD = "forward"

class Rule: # Remove once the original module can be included!
    pass

class Packet: # Remove once the original module can be included!
    pass

class RuleSystem:
    def __init__(self):
        self._tables: Dict[str, Dict[str, List[Rule]]] = RuleSystem.empty_tables()

    def __init__(self, table: Table, chain: Chain, rules: List[Rule]):
        self._tables: Dict[str, Dict[str, List[Rule]]] = RuleSystem.empty_tables()
        self._tables[table.value][chain.value] = rules

    @staticmethod
    def empty_tables() -> Dict[str, Dict[str, List[Rule]]]:
        tables = {
            Table.FILTER.value: {
                "INPUT": [],
                "FORWARD": []
            },
            Table.NAT.value: {
                "PREROUTING": [],
                "INPUT": [],
                "FORWARD": [],
                "POSTROUTING": []
            },
            Table.MANGLE.value: {
                "PREROUTING": [],
                "INPUT": [],
                "FORWARD": [],
                "OUTPUT": [],
                "POSTROUTING": []
            },
        }

        return tables

    def run_on_packet(self, packet: Packet) -> Packet:
        pass

    def get_rule(self, id: int) -> Rule:
        pass

    def update_rule(id, rule: Rule) -> bool:
        pass
    
    def append_rule(self, table: Table, chain: Chain, rule: Rule):
        if chain.value in self.get_chain_names(table.value):
            self._tables[table.value][chain.value].append(rule)

    def insert_rule(self, table: Table, chain: Chain, rule: Rule, rule_num: int):
        if chain.value in self.get_chain_names(table.value):
            self._tables[table.value][chain.value].insert(rule_num, rule)

    def delete_rule(self, table: Table, chain: Chain, rule_num: int):
        if chain.value in self.get_chain_names(table.value):
            del self._tables[table.value][chain.value][rule_num]
    
    def get_chain_names(self, table: Table) -> List[str]:
        return list(self._tables[table].keys())

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

    def write_to_file(self):
        pass

    def read_from_file(self):
        pass
