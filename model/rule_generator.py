from enum import Enum
from typing import Dict, List, Optional, Tuple, Union, Any
from abc import abstractmethod
import parser_entries


class SignatureComponent:
    @abstractmethod
    def find_fit(self, substr: List[str]) -> Optional[Tuple[Dict[str, str], List[str]]]:
        pass
    
    @abstractmethod
    def possible_elements(self, rule):
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
    
    def possible_elements(self, rule):
        if len(rule.components) == 0:
            return self.start_strs
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
    
    def possible_elements(self, rule):
        for component in rule.components:
            for table in self.possible_tables:
                if component == self.possible_tables[table]:
                    return None
        return self.possible_tables


class RuleSpecification:
    def __init__(self, spec_components):
        self.possible_components = spec_components

    def find_fit(self, substr: List[str]) -> Optional[Tuple[List[Any], List[str]]]:
        specs = []
        i = 0
        while i < len(self.possible_components) and substr:
            result = self.possible_components[i].find_fit(substr)
            if result:
                specs += result[0]
                substr = result[1]
            i += 1
        return (specs, substr) if len(specs) > 0 else None
    
    def possible_elements(self, rule):
        pass


class CommandComponent(SignatureComponent):
    def __init__(self, commands):
        self.possible_commands = commands

    def find_fit(self, substr: List[str]) -> Optional[Tuple[Dict[str, str], List[str]]]:
        to_find = substr[0]
        if to_find in self.possible_commands:
            return self.possible_commands[to_find], substr[1:]
        else:
            return None
    
    def possible_elements(self, rule):
        for component in rule.components:
            for command in self.possible_commands:
                if component == self.possible_commands[command]:
                    return None
        return self.possible_commands


class ChainComponent:
    def __init__(self, chains):
        self.possible_chains = chains

    def find_fit(
        self, substr: List[str], table: Optional[str] = ""
    ) -> Optional[Tuple[Dict[str, str], List[str]]]:
        to_find = substr[0]
        if (
            to_find in self.possible_chains
            and table in self.possible_chains[to_find]["tables"]
        ):
            return self.possible_chains[to_find], substr[1:]
        else:
            return None
    
    def possible_elements(self, rule):
        for component in rule.components:
            for command in self.possible_chains:
                if component == self.possible_chains[command]:
                    return None
        return self.possible_chains

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
        self.signatures = signatures
        self.chain = chain
        self.raw_form = raw_form
        self.components : List[Any] = []
        self.possible_elements : List[Any] = []
        if self.raw_form:
            parsed_components = self.parse_raw_form()
            if parsed_components:
                self.components = parsed_components

    def parse_raw_form(
        self, keep_best_estimate=False
    ) -> Optional[List[Any]]:
        best_components = []
        best_components_length = 0
        possible_elements = []
        substr = []
        for signature in self.signatures:
            substr = self.raw_form.split(" ")
            components = []
            i = 0
            while i < len(signature) and substr:
                part = signature[i]
                result: Any = ()
                #print(substr)
                if type(part) == ChainComponent:
                    result = part.find_fit(substr, self.table)
                    self.chain = result[0]["value"]
                else:
                    result = part.find_fit(substr)
                if result:
                    if type(part) == TableComponent and self.table == "":
                        self.table = result[0]["value"]
                    components.append(result[0])
                    substr = result[1]
                i += 1
            if (i < len(signature)-1 and len(substr) == 0):
                possible_elements.append(signature[i].possible_elements(self))
                possible_elements.append(signature[i+1].possible_elements(self))
            if i == len(signature)-1 and len(substr) == 0:
                return components
            if keep_best_estimate and len(components) > best_components_length:
                best_components = components
                best_components_length = len(components)
        return [best_components, substr, possible_elements] if keep_best_estimate else None

    def check_total_correctness(self) -> bool:
        raw_parts = [component["str_form"] for component in self.components]
        actual_raw_form = " ".join(raw_parts)
        return self.parse_raw_form(actual_raw_form) != None

    def check_partial_correctness(self) -> bool:
        raw_parts = [component["str_form"] for component in self.components]
        self.raw_form = " ".join(raw_parts)
        result = self.parse_raw_form(True)
        if result:
            self.possible_elements = result[2]
        return self.parse_raw_form(True) != None

    def delete_element(self, id: int) -> bool:
        if len(self.components) > id:
            del self.components[id]
            return True
        return False

    def get_possible_elements(self) -> List:
        return self.possible_elements

    def set_value(self, id: int, value) -> bool:
        if len(self.components) > id and "value" in self.components[id]:
            self.components[id]["value"] = value
            return True
        return False

    def get_elements(self):
        return self.components
