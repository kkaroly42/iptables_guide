# from rule_generator import Rule
from rule_system import RuleSystem, Table, Chain

from typing import Dict, List, Any, Optional

class Rule: # Remove once the original module can be included!
    pass

class Packet: # Remove once the original module can be included!
    pass

class Iptables:
    def __init__(self, table: Optional[Table], chain: Optional[Chain], rule_system: Optional[RuleSystem]):
        self._tables: Dict[str, Dict[str, List[Rule]]] = RuleSystem.empty_tables()
        if (table != None and chain != None and rule_system != None):   
            self._tables[table.value][chain.value] = rule_system

    @staticmethod
    def empty_tables() -> Dict[str, Dict[str, RuleSystem]]:
        tables = {
            Table.FILTER.value: {
                "INPUT": RuleSystem([], Table.FILTER, Chain.INPUT),
                "FORWARD": RuleSystem([], Table.FILTER, Chain.FORWARD)
            },
            Table.NAT.value: {
                "PREROUTING": RuleSystem([], Table.NAT, Chain.PREROUTING),
                "INPUT": RuleSystem([], Table.NAT, Chain.INPUT),
                "FORWARD": RuleSystem([], Table.NAT, Chain.FORWARD),
                "POSTROUTING": RuleSystem([], Table.NAT, Chain.POSTROUTING)
            },
            Table.MANGLE.value: {
                "PREROUTING": RuleSystem([], Table.MANGLE, Chain.PREROUTING),
                "INPUT": RuleSystem([], Table.MANGLE, Chain.INPUT),
                "FORWARD": RuleSystem([], Table.MANGLE, Chain.FORWARD),
                "OUTPUT": RuleSystem([], Table.MANGLE, Chain.OUTPUT),
                "POSTROUTING": RuleSystem([], Table.MANGLE, Chain.POSTROUTING)
            },
        }

        return tables
    
    def append_rule(self, table: Table, chain: Chain, rule: Rule):
        if chain.value in self.get_chain_names(table.value):
            self._tables[table.value][chain.value].append_rule(rule)

    def insert_rule(self, table: Table, chain: Chain, rule: Rule, rule_num: int):
        if chain.value in self.get_chain_names(table.value):
            self._tables[table.value][chain.value].insert_rule(rule_num, rule)

    def delete_rule(self, table: Table, chain: Chain, rule_num: int):
        if chain.value in self.get_chain_names(table.value):
            self._tables[table.value][chain.value].delete_rule(rule_num)
    
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

    # def write_to_file(self):
    #     pass

    # def read_from_file(self):
    #     pass
