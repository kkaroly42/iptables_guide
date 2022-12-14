from enum import Enum
from typing import Dict, List, Optional, Tuple, Union, Any
from abc import abstractmethod


class SignatureComponent:
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
        already_seen = []
        while i < len(self.possible_components) and substr:
            if i not in already_seen:
                result = self.possible_components[i].find_fit(substr)
                if result:
                    if type(result[0]) == list:
                        specs += result[0]
                        substr = result[1]
                    else:
                        specs.append(result[0])
                        substr = result[1]
                    already_seen.append(i)
                    i = 0
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
        table: str,
        chain: str,
        allow_partial_rule=True,
    ):
        self.table = table
        self.signatures = signatures
        self.chain = chain
        self.raw_form = raw_form
        self.components: List[Any] = []
        self.possible_elements: List[Any] = []
        if self.raw_form:
            if allow_partial_rule:
                parsed_components, substr, possible_elements = self.parse_raw_form(
                    allow_partial_rule
                )
            else:
                parsed_components = self.parse_raw_form(allow_partial_rule)
            if parsed_components:
                self.components = parsed_components

    def parse_raw_form(self, keep_best_estimate=True) -> Optional[List[Any]]:
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
                if type(part) == ChainComponent:
                    result = part.find_fit(substr, self.table)  # type: ignore
                    if result:
                        self.chain = result[0]["value"]
                else:
                    result = part.find_fit(substr)  # type: ignore
                if result:
                    if type(part) == TableComponent and self.table == "":
                        self.table = result[0]["value"]
                    if type(part) == RuleSpecification:
                        components += result[0]
                    else:
                        components.append(result[0])
                    substr = result[1]
                i += 1
            if i < len(signature) - 1 and len(substr) == 0:
                possible_elements.append(signature[i].possible_elements(self))
                possible_elements.append(signature[i + 1].possible_elements(self))
            if i == len(signature) and len(substr) == 0:
                if keep_best_estimate:
                    return [components, [], []]
            if keep_best_estimate and len(components) > best_components_length:
                best_components = components
                best_components_length = len(components)
        return (
            [best_components, substr, possible_elements] if keep_best_estimate else None
        )

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

    def run_on_packet(self, packet) -> Tuple[bool, Optional[Any]]:
        conditions_met = True
        run_method = None
        for component in self.components:
            if "type" in component:
                if component["type"] == "condition":
                    if "value" not in component:
                        component["value"] = ""
                    conditions_met = conditions_met and component["condition_method"](
                        packet, component["value"]
                    )
                    if not conditions_met:
                        return False, None
                elif component["type"] == "action":
                    run_method = component["action_method"]
                    method_value = ""
                    if "value" in component:
                        method_value = component["value"]
        if conditions_met and run_method:
            return True, run_method(packet, method_value)

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

    def get_str_form(self):
        raw_parts = [component["str_form"] for component in self.components]
        self.raw_form = " ".join(raw_parts)
        return self.raw_form
