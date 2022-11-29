from enum import Enum
from typing import List, Dict, Optional, Union

from PySide6.QtCore import QObject, Signal

from IPTables_Guide.model.rule_generator import (
    Rule,
    StartComponent,
    TableComponent,
    CommandComponent,
    ChainComponent,
    RuleSpecification,
)
from IPTables_Guide.model.parser_entries import (
    start_strs,
    possible_chains,
    possible_commands,
    possible_tables,
    JumpParser,
)


class Table(Enum):
    FILTER = "FILTER"
    NAT = "NAT"
    MANGLE = "MANGLE"


def table_to_str(table: Union[Table, str]) -> str:
    return table if isinstance(table, str) else table.value


def table_to_value(table: Union[Table, str]) -> Table:
    if isinstance(table, Table):
        return table
    table = table.upper()
    assert table in [e.value.upper() for e in Table]
    for e in Table:
        if e.value.upper() == table:
            return e
    assert False


class Chain(Enum):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    PREROUTING = "PREROUTING"
    POSTROUTING = "POSTROUTING"
    FORWARD = "FORWARD"


def chain_to_str(chain: Union[Chain, str]) -> str:
    return chain if isinstance(chain, str) else chain.value


def chain_to_value(chain: Union[Chain, str]) -> Chain:
    if isinstance(chain, Chain):
        return chain
    chain = chain.upper()
    assert chain in [e.value.upper() for e in Chain]
    for e in Chain:
        if e.value.upper() == chain:
            return e
    assert False


class Packet:  # Remove once the original module can be included!
    pass


default_sigantures: List[List] = [
    [
        StartComponent(start_strs),
        TableComponent(possible_tables),
        CommandComponent(possible_commands),
        ChainComponent(possible_chains),
        RuleSpecification([JumpParser({"DROP": {"str_form": "-j DROP"}})]),
    ],
    [
        StartComponent(start_strs),
        TableComponent(possible_tables),
        CommandComponent(possible_commands),
        ChainComponent(possible_chains),
    ],
]


class RuleSystem(QObject):
    rule_appended = Signal(str, str)
    rule_inserted = Signal(str, str, int)
    rule_deleted = Signal(str, str, int)

    def __init__(self, rule_signatures: List[List] = default_sigantures):
        super().__init__()
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
        self, raw: str, table: Union[Table, str], chain: Union[Chain, str]
    ) -> Rule:
        return Rule(
            raw, self._rule_signatures, table_to_str(table), chain_to_str(chain)
        )

    def run_on_packet(self, packet: Packet) -> Packet:
        pass

    def get_rule(
        self, table: Union[Table, str], chain: Union[Chain, str], id: int
    ) -> Rule:
        try:
            return self._tables[table_to_str(table).upper()][
                chain_to_str(chain).upper()
            ][id]
        except IndexError:
            assert False

    def update_rule(
        self,
        table: Union[Table, str],
        chain: Union[Chain, str],
        id: int,
        rule_as_str: str,
    ) -> bool:
        table_str = table_to_str(table).upper()
        chain_str = chain_to_str(chain).upper()
        rule = self.create_rule_from_raw_str(rule_as_str, table, chain)
        if not rule:
            return False
        return self.overwrite_rule(table, chain, id, rule)

    def overwrite_rule(
        self, table: Union[Table, str], chain: Union[Chain, str], id: int, rule: Rule
    ) -> bool:
        table_str = table_to_str(table).upper()
        chain_str = chain_to_str(chain).upper()
        if (
            table_str == table_to_str(rule.table).upper()
            and chain_str == chain_to_str(rule.chain).upper()
        ):
            try:
                self._tables[table_str][chain_str][id] = rule
                return True
            except (IndexError, KeyError):
                return False
        return False

    def append_rule(
        self, table: Union[Table, str], chain: Union[Chain, str], rule: Rule
    ) -> bool:
        table_str = table_to_str(table).upper()
        chain_str = chain_to_str(chain).upper()
        if (
            table_str == table_to_str(rule.table).upper()
            and chain_str == chain_to_str(rule.chain).upper()
        ):
            try:
                self._tables[table_str][chain_str].append(rule)
                self.rule_appended.emit(table_str, chain_str)
                return True
            except (IndexError, KeyError):
                return False
        return False

    def insert_rule(
        self,
        table: Union[Table, str],
        chain: Union[Chain, str],
        rule: Rule,
        rule_num: int,
    ) -> bool:
        table_str = table_to_str(table).upper()
        chain_str = chain_to_str(chain).upper()
        if (
            table_str == table_to_str(rule.table).upper()
            and chain_str == chain_to_str(rule.chain).upper()
        ):
            try:
                self._tables[table_str][chain_str] = (
                    self._tables[table_str][chain_str][0:rule_num]
                    + [rule]
                    + self._tables[table_str][chain_str][rule_num:]
                )
                self.rule_inserted.emit(table_str, chain_str, rule_num)
                return True
            except (IndexError, KeyError):
                return False
        return False

    def delete_rule(
        self, table: Union[Table, str], chain: Union[Chain, str], rule_num: int
    ) -> bool:
        table_str = table_to_str(table).upper()
        chain_str = chain_to_str(chain).upper()
        try:
            del self._tables[table_str][chain_str][rule_num]
            self.rule_deleted.emit(table_str, chain_str, rule_num)
            return True
        except (IndexError, KeyError):
            return False

    def get_rules_in_chain(
        self, table: Union[Table, str], chain: Union[Chain, str]
    ) -> List[Rule]:
        table_str = table_to_str(table).upper()
        chain_str = chain_to_str(chain).upper()
        try:
            return self._tables[table_str][chain_str]
        except KeyError:
            return []

    def get_chain_names(self, table: Union[Table, str]) -> List[str]:
        return list(self._tables[table_to_str(table)].keys())

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
                    print("hey", self._tables[table][chain])
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
                if len(line) > 0 and line[0] == "#":
                    table, chain = line[1:].split(".")
                else:
                    rule = self.create_rule_from_raw_str(line, table, chain)
                    self.append_rule(
                        Table(rule.table.upper()), Chain(rule.chain.upper()), rule
                    )
