from enum import Enum
from typing import List, Dict, Union, Optional

import scapy.all
from PySide6.QtCore import QObject, Signal

from IPTables_Guide.model.rule_generator import Rule
from IPTables_Guide.model.parser_entries import (
    SignatureComponent,
    TCPParser,
    UDPParser,
    DestinationParser,
    JumpParser,
    SourceParser,
    StateParser,
    start_strs,
    possible_tables,
    possible_commands,
    possible_chains,
)

from IPTables_Guide.model.rule_generator import (
    TableComponent,
    StartComponent,
    CommandComponent,
    ChainComponent,
    RuleSpecification,
)


# TODO find better solution


class DefaultTableType(Enum):
    def __str__(self):
        return str(self.value)

    FILTER = "FILTER"
    NAT = "NAT"


class DefaultChainType(Enum):
    def __str__(self):
        return str(self.value)

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    PREROUTING = "PREROUTING"
    POSTROUTING = "POSTROUTING"
    FORWARD = "FORWARD"


# TODO create custom classes that can handle adding chains to tables etc.
# For now just alias these types to Dict, but later we should create a
# custom class to allow adding user defined chains and tables
Chain = Dict[str, List[Rule]]

Table = Dict[str, Chain]


class RuleSystem(QObject):
    rule_appended = Signal(str, str)
    rule_inserted = Signal(str, str, int)
    rule_deleted = Signal(str, str, int)

    def __init__(
        self, rule_signatures: Optional[List[List[SignatureComponent]]] = None
    ) -> None:
        super().__init__()
        self._tables: Table = RuleSystem.empty_tables()
        if rule_signatures is not None:
            self._rule_signatures = rule_signatures
        else:
            self._rule_signatures = [
                [
                    StartComponent(start_strs),
                    TableComponent(possible_tables),
                    CommandComponent(possible_commands),
                    ChainComponent(possible_chains),
                    RuleSpecification(
                        [
                            TCPParser(),
                            SourceParser(),
                            DestinationParser(),
                            StateParser(),
                            JumpParser(),
                        ]
                    ),
                ],
                [
                    StartComponent(start_strs),
                    TableComponent(possible_tables),
                    CommandComponent(possible_commands),
                    ChainComponent(possible_chains),
                    RuleSpecification(
                        [
                            UDPParser(),
                            SourceParser(),
                            DestinationParser(),
                            StateParser(),
                            JumpParser(),
                        ]
                    ),
                ],
            ]

    @staticmethod
    def empty_tables() -> Table:
        return {
            "FILTER": {"INPUT": [], "FORWARD": []},
            "NAT": {"PREROUTING": [], "INPUT": [], "POSTROUTING": []},
        }

    def create_rule_from_raw_str(
        self,
        raw: str,
        table: Union[DefaultTableType, str],
        chain: Union[DefaultChainType, str],
    ) -> Rule:
        return Rule(raw, self._rule_signatures, str(table), str(chain))

    # TODO use packets module
    def run_chain_on_raw_packets(
        self,
        input_file_name: str,
        output_file_name: str,
        table: Union[DefaultTableType, str],
        chain: Union[DefaultChainType, str],
    ) -> None:
        input = scapy.all.rdpcap(input_file_name)
        rules = self.get_rules_in_chain(table, chain)
        for packet in input:
            rule_transformed_it = False
            for rule in rules:
                result = rule.run_on_packet(packet)
                if result[0] and result[1]:
                    rule_transformed_it = True
                    if result[1] != "DROP":
                        scapy.all.wrpcap(output_file_name, result[1], append=True)
                    break
            if not rule_transformed_it:
                scapy.all.wrpcap(output_file_name, packet, append=True)

    def get_rule(
        self,
        table: Union[DefaultTableType, str],
        chain: Union[DefaultChainType, str],
        id_: int,
    ) -> Rule:
        try:
            return self._tables[str(table)][str(chain)][id_]
        except IndexError:
            assert False

    def update_rule(
        self,
        table: Union[DefaultTableType, str],
        chain: Union[DefaultChainType, str],
        id: int,
        rule_as_str: str,
    ) -> bool:
        table_str = str(table)
        chain_str = str(chain)
        rule = self.create_rule_from_raw_str(rule_as_str, table, chain)
        if not rule:
            return False
        return self.overwrite_rule(table, chain, id, rule)

    def overwrite_rule(
        self,
        table: Union[DefaultTableType, str],
        chain: Union[DefaultChainType, str],
        id: int,
        rule: Rule,
    ) -> bool:
        table_str = str(table)
        chain_str = str(chain)
        if table_str == str(rule.table) and chain_str == str(rule.chain):
            try:
                self._tables[table_str][chain_str][id] = rule
                return True
            except (IndexError, KeyError):
                return False
        return False

    def append_rule(
        self,
        table: Union[DefaultTableType, str],
        chain: Union[DefaultChainType, str],
        rule: Rule,
    ) -> bool:
        table_str = str(table).upper()
        chain_str = str(chain).upper()
        if (
            table_str == str(rule.table).upper()
            and chain_str == str(rule.chain).upper()
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
        table: Union[DefaultTableType, str],
        chain: Union[DefaultChainType, str],
        rule: Rule,
        rule_num: int,
    ) -> bool:
        table_str = str(table)
        chain_str = str(chain)
        if table_str == str(rule.table) and chain_str == str(rule.chain):
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
        self,
        table: Union[DefaultTableType, str],
        chain: Union[DefaultChainType, str],
        rule_num: int,
    ) -> bool:
        table_str = str(table)
        chain_str = str(chain)
        try:
            del self._tables[table_str][chain_str][rule_num]
            self.rule_deleted.emit(table_str, chain_str, rule_num)
            return True
        except (IndexError, KeyError):
            return False

    def get_rules_in_chain(
        self, table: Union[DefaultTableType, str], chain: Union[DefaultChainType, str]
    ) -> List[Rule]:
        table_str = str(table)
        chain_str = str(chain)
        try:
            return self._tables[table_str][chain_str]
        except KeyError:
            return []

    def get_chain_names(self, table: Union[DefaultTableType, str]) -> List[str]:
        return list(self._tables[str(table)].keys())

    def flush(self, table: DefaultTableType, chain: str):
        pass

    def new_chain(self, table: DefaultTableType, chain: str):
        pass

    def delete_chain(self, table: DefaultTableType, chain: str):
        pass

    def policy(self, table: DefaultTableType, chain: str, target: str):
        pass

    def rename_chain(self, table: DefaultTableType, old_chain: str, new_chain: str):
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
                if len(line) > 0 and line[0] == "#":
                    table, chain = line[1:].split(".")
                else:
                    rule = self.create_rule_from_raw_str(line, table, chain)
                    self.append_rule(
                        DefaultTableType(rule.table.upper()),
                        DefaultChainType(rule.chain.upper()),
                        rule,
                    )

    @property
    def tables(self):
        return self._tables
