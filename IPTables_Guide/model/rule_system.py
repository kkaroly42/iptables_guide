from enum import Enum
from typing import List, Dict, Optional

# from IPTables_Guide.model.packets import *
from IPTables_Guide.model.rule_generator import *


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


class Packet:  # Remove once the original module can be included!
    pass


class RuleSystem:
    def __init__(self, rule_signatures):
        self._tables: Dict[str, Dict[str, List[Rule]]] = RuleSystem.empty_tables()
        self._rule_signatures = rule_signatures

    #    def __init__(self, table: Table, chain: Chain, rules: List[Rule]):
    #        self._tables: Dict[str, Dict[str, List[Rule]]] = RuleSystem.empty_tables()
    #        self._tables[table.value][chain.value] = rules

    @staticmethod
    def empty_tables() -> Dict[str, Dict[str, List[Rule]]]:
        tables = {
            Table.FILTER.value: {"INPUT": [], "FORWARD": []},
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

    def create_rule_from_raw_str(
        self, raw: str, table: Table, chain: Chain
    ) -> Optional[Rule]:
        return Rule(raw, self._rule_signatures, table, chain)

    def run_on_packet(self, packet: Packet) -> Packet:
        pass

    def get_rule(self, table: Table, chain: Chain, id: int) -> Optional[Rule]:
        try:
            return self._tables[table.value.lower()][chain.value.upper()][id]
        except IndexError:
            return None

    def update_rule(
        self, table: Table, chain: Chain, id: int, rule_as_str: str
    ) -> bool:
        table_str = table.value.lower()
        chain_str = chain.value.upper()
        rule = self.create_rule_from_raw_str(rule_as_str, table, chain)
        if not rule:
            return False
        return self.overwrite_rule(table, chain, id, rule)

    def overwrite_rule(self, table: Table, chain: Chain, id: int, rule: Rule) -> bool:
        table_str = table.value.lower()
        chain_str = chain.value.upper()
        if table_str == rule.table.lower() and chain_str == rule.chain.upper():
            try:
                self._tables[table_str][chain_str][id] = rule
                return True
            except (IndexError, KeyError):
                return False
        return False

    def append_rule(self, table: Table, chain: Chain, rule: Rule) -> bool:
        table_str = table.value.lower()
        chain_str = chain.value.upper()
        if table_str == rule.table.lower() and chain_str == rule.chain.upper():
            try:
                self._tables[table_str][chain_str].append(rule)
                return True
            except (IndexError, KeyError):
                return False
        return False

    def insert_rule(
        self, table: Table, chain: Chain, rule: Rule, rule_num: int
    ) -> bool:
        table_str = table.value.lower()
        chain_str = chain.value.upper()
        if table_str == rule.table.lower() and chain_str == rule.chain.upper():
            try:
                self._tables[table_str][chain_str] = (
                    self._tables[table_str][chain_str][0:rule_num]
                    + [rule]
                    + self._tables[table_str][chain_str][rule_num:]
                )
                return True
            except (IndexError, KeyError):
                return False
        return False

    def delete_rule(self, table: Table, chain: Chain, rule_num: int) -> bool:
        table_str = table.value.lower()
        chain_str = chain.value.upper()
        try:
            del self._tables[table_str][chain_str][rule_num]
            return True
        except (IndexError, KeyError):
            return False

    def get_rules_in_chain(self, table: Table, chain: Chain) -> Optional[List[Rule]]:
        table_str = table.value.lower()
        chain_str = chain.value.upper()
        try:
            return self._tables[table_str][chain_str]
        except KeyError:
            return None

    def get_chain_names(self, table: Table) -> List[str]:
        return list(self._tables[table].keys())

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

    def write_to_file(self, file_name):
        with open(file_name, "w") as f:
            for table in self._tables:
                for chain in self._tables[table]:
                    if self._tables[table][chain]:
                        f.write("#{}.{}\n".format(table, chain))
                    rules = [
                        rule.get_str_form() + "\n"
                        for rule in self._tables[table][chain]
                    ]
                    f.writelines(rules)

    def read_from_file(self, file_name):
        table = ""
        chain = ""
        with open(file_name, "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                print(line)
                if line[0] == "#":
                    table, chain = line[1:].split(".")
                else:
                    rule = self.create_rule_from_raw_str(line, table, chain)
                    self.append_rule(
                        Table(rule.table.lower()), Chain(rule.chain.lower()), rule
                    )
