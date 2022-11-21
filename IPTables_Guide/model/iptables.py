from typing import Dict, List, Any, Optional

from PySide6.QtCore import QObject, Signal

from IPTables_Guide.model.rule_system import Rule
from IPTables_Guide.model.rule_system import RuleSystem, Table, Chain


class Iptables(QObject):
    rule_appended = Signal(Table, Chain)
    rule_inserted = Signal(int, Table, Chain)
    rule_deleted = Signal(int, Table, Chain)

    def __init__(
        self,
        table: Optional[Table] = None,
        chain: Optional[Chain] = None,
        rule_system: Optional[RuleSystem] = None,
    ):
        super().__init__()
        self._tables: Dict[str, Dict[str, List[Rule]]] = RuleSystem.empty_tables()
        # if table != None and chain != None and rule_system != None:
        #     self._tables[table.value][chain.value] = rule_system

    @staticmethod
    def empty_tables() -> Dict[str, Dict[str, List[Rule]]]:
        tables = {
            Table.FILTER.value: {
                "INPUT": [],
                "FORWARD": [],
            },
            Table.NAT.value: {
                "PREROUTING": [],
                "INPUT": [],
                "FORWARD": [],
                "POSTROUTING": [],
            },
            Table.MANGLE.value: {
                "PREROUTING": [],
                "INPUT": [],
                "FORWARD": [],
                "OUTPUT": [],
                "POSTROUTING": [],
            },
        }

        return tables

    def append_rule(self, table: Table, chain: Chain, rule: Rule):
        if chain.value in self.get_chain_names(table.value):
            self._tables[table.value][chain.value].append(rule)
            self.rule_appended.emit(table, chain)

    def insert_rule(self, table: Table, chain: Chain, rule: Rule, rule_num: int):
        if chain.value in self.get_chain_names(table.value):
            self._tables[table.value][chain.value].insert(rule_num, rule)
            self.rule_inserted.emit(rule_num, table, chain)

    def delete_rule(self, table: Table, chain: Chain, rule_num: int):
        if chain.value in self.get_chain_names(table.value):
            del self._tables[table.value][chain.value][rule_num]
            self.rule_deleted.emit(rule_num, table, chain)

    def get_chain_names(self, table: Table) -> List[str]:
        return list(self._tables[table].keys())

    def replace(
        self, table: Table, chain: str, rule_num: int, rule_specs: Dict[str, Any]
    ):
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
