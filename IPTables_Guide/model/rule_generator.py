from enum import Enum
from typing import Dict, List, Optional, Tuple, Union
from abc import abstractmethod
import IPTables_Guide.model.parser_entries as parser_entries


class SignatureComponent:
    @abstractmethod
    def find_fit(self, substr: List[str]) -> Optional[Tuple[Dict[str, str], List[str]]]:
        pass


class StartComponent(SignatureComponent):
    def __init__(self, start_strs):
        self.start_strs = start_strs

    def find_fit(self, substr: List[str]) -> Optional[Tuple[Dict[str, str], List[str]]]:
        to_find = substr[0]
        if to_find in self.start_strs:
            return self.start_strs[to_find], substr[1:]
        else:
            return None


class TableComponent(SignatureComponent):
    def __init__(self, tables: Dict[str, Dict[str, str]]):
        self.possible_tables = tables

    def find_fit(self, substr: List[str]) -> Optional[Tuple[Dict[str, str], List[str]]]:
        to_find = " ".join(substr[:2])
        if to_find in self.possible_tables:
            return self.possible_tables[to_find], substr[2:]
        else:
            return None


class RuleSpecification:
    def __init__(self, spec_components):
        self.possible_components = spec_components

    def find_fit(
        self, substr: List[str]
    ) -> Optional[List[Tuple[Dict[str, str], List[str]]]]:
        specs = []
        i = 0
        while i < len(self.possible_components) and substr:
            result = self.possible_components[i].find_fit(substr)
            if result:
                specs.append(result[0])
                substr = result[1]
        return specs if len(specs) > 0 else None


class CommandComponent(SignatureComponent):
    def __init__(self, commands):
        self.possible_commands = commands

    def find_fit(self, substr: List[str]) -> Optional[Tuple[Dict[str, str], List[str]]]:
        to_find = substr[0]
        if to_find in self.possible_commands:
            return self.possible_commands[to_find], substr[1:]
        else:
            return None


class ChainComponent:
    def __init__(self, chains):
        self.possible_chains = chains

    def find_fit(
        self, substr: List[str], table: str
    ) -> Optional[Tuple[Dict[str, str], List[str]]]:
        to_find = substr[0]
        if (
            to_find in self.possible_chains
            and table in self.possible_chains[to_find]["tables"]
        ):
            return self.possible_chains[to_find], substr[1:]
        else:
            return None


class Rule:
    def __init__(
        self,
        raw_form: str,
        signatures: List[
            List[Union[SignatureComponent, ChainComponent, RuleSpecification]]
        ],
        table: Optional[str],
        chain: Optional[str],
    ):
        self.table = table
        self.chain = chain
        self.components = []
        if raw_form != "":
            self.parsed_form = self.parse_raw_form(raw_form)

    def parse_raw_form(self, raw_form, keep_best_estimate = False) -> Optional[List[Dict[str, str]]]:
        for signature in signatures:
            substr = raw_form.split(" ")
            components = []
            while i < len(signature) and substr:
                part = signature[i]
                result = ()
                if type(part) == ChainComponent:
                    result = part.find_fit(substr, self.table)
                else:
                    result = part.find_fit(substr)
                if result:
                    if type(part) == TableComponent and self.table == "":
                        self.table == result["value"]
                    components.append(result[0])
                    substr = result[1]
            if i < len(signature) or substr:
                return components
        return None

    def check_total_correctness(self) -> bool:
        raw_parts = [component["str_form"] for component in self.components]
        actual_raw_form = " ".join(raw_parts)
        return self.parse_raw_form(actual_raw_form) != None

    def check_partial_correctness(self) -> bool:
        pass

    def delete_element(self, id: int) -> bool:
        if len(self.components) > id:
            del self.components[id]
            return True
        return False

    def get_possible_elements(self) -> List:
        pass

    def set_value(self, id: int, value) -> bool:
        if len(self.components) > id and "value" in self.components[id]:
            self.components[id]["value"] = value
            return True
        return False

    def get_elements(self):
        return self.components


signatures = [
    [
        StartComponent(parser_entries.start_strs),
        TableComponent(parser_entries.possible_tables),
        CommandComponent(parser_entries.possible_commands),
        RuleSpecification(None),
    ]
]
