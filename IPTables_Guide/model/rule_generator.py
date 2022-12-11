from __future__ import annotations

from typing import List, Optional, Tuple, Any, Dict

from overrides import override

from abc import abstractmethod

from IPTables_Guide.model.utils import ParserHelper, FlagDetail


class SignatureComponent:
    @abstractmethod
    def possible_elements(self, components: List[Any]) -> Any:
        raise NotImplementedError

    @abstractmethod
    def find_fit(self, substr: List[str]) -> Optional[ParserHelper]:
        raise NotImplementedError


class StartComponent(SignatureComponent):
    def __init__(self, start_strs: Dict[str, FlagDetail]) -> None:
        self.start_strs = start_strs

    @override
    def find_fit(self, substr: List[str]) -> Optional[ParserHelper]:
        to_find = substr[0]
        if to_find in self.start_strs:
            return ParserHelper(parsed=self.start_strs[to_find], others=substr[1:])
        else:
            return None

    @override
    def possible_elements(self, components: List[Any]) -> Any:
        if len(components) == 0:
            return self.start_strs
        return None


class TableComponent(SignatureComponent):
    def __init__(self, tables: Dict[str, FlagDetail]):
        self.possible_tables = tables

    def find_fit(self, substr: List[str]) -> Optional[ParserHelper]:
        to_find = " ".join(substr[:2])
        if to_find in self.possible_tables:
            return ParserHelper(parsed=self.possible_tables[to_find], others=substr[2:])
        return None

    def possible_elements(self, components: List[Any]) -> Any:
        for component in components:
            for table in self.possible_tables:
                if component == self.possible_tables[table]:
                    return None
        return self.possible_tables


class RuleSpecification(SignatureComponent):
    def __init__(self, spec_components: List[SignatureComponent]):
        self.possible_components = spec_components

    @override
    def find_fit(self, substr: List[str]) -> Optional[ParserHelper]:
        specs = []
        i = 0
        already_seen = set()
        while i < len(self.possible_components) and substr:
            if i not in already_seen:
                result = self.possible_components[i].find_fit(substr)
                if result:
                    if type(result[0]) == list:
                        specs += result[0]
                        substr = result[1]
                    else:
                        assert isinstance(result[0], dict)
                        specs.append(result[0])
                        substr = result[1]
                    already_seen.add(i)
                    i = 0
            i += 1
        return ParserHelper(specs, substr) if len(specs) > 0 else None

    def possible_elements(self, components: List[Any]) -> Any:
        pass


class CommandComponent(SignatureComponent):
    def __init__(self, commands):
        self.possible_commands = commands

    def find_fit(self, substr: List[str]) -> Optional[ParserHelper]:
        to_find = substr[0]
        if to_find in self.possible_commands:
            return ParserHelper(self.possible_commands[to_find], substr[1:])
        return None

    def possible_elements(self, components: List[Any]) -> Any:
        for component in components:
            for command in self.possible_commands:
                if component == self.possible_commands[command]:
                    return None
        return self.possible_commands


class ChainComponent(SignatureComponent):
    def __init__(self, chains: Dict[str, FlagDetail]):
        self.possible_chains = chains
        self._table = ""

    def table(self, table: str) -> ChainComponent:
        self._table = table
        return self

    def find_fit(self, substr: List[str]) -> Optional[ParserHelper]:
        to_find = substr[0]
        if (
            to_find in self.possible_chains
            and self._table in self.possible_chains[to_find]["tables"]
        ):
            return ParserHelper(self.possible_chains[to_find], substr[1:])
        return None

    def possible_elements(self, components: List[Any]) -> Any:
        for component in components:
            for command in self.possible_chains:
                if component == self.possible_chains[command]:
                    return None
        return self.possible_chains


class Rule:
    def __init__(
        self,
        raw_form: str,
        signatures: List[List[SignatureComponent]],
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
                tmp = self.parse_raw_form(allow_partial_rule)
                assert tmp is not None
                parsed_components, substr, possible_elements = tmp
            else:
                parsed_components = self.parse_raw_form(allow_partial_rule)
            if parsed_components:
                self.components = parsed_components

    def parse_raw_form(self, keep_best_estimate: bool = True) -> Optional[List[Any]]:
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
                if isinstance(part, ChainComponent):
                    part.table(self.table)
                    result = part.find_fit(substr)
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
                possible_elements.append(
                    signature[i].possible_elements(self.components)
                )
                possible_elements.append(
                    signature[i + 1].possible_elements(self.components)
                )
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
        self.raw_form = " ".join(raw_parts)
        return self.parse_raw_form(True) is not None

    def check_partial_correctness(self) -> bool:
        raw_parts = [component["str_form"] for component in self.components]
        self.raw_form = " ".join(raw_parts)
        result = self.parse_raw_form(True)
        if result:
            self.possible_elements = result[2]
        return self.parse_raw_form(True) is not None

    def run_on_packet(self, packet) -> Tuple[bool, Optional[Any]]:
        conditions_met = True
        run_method = None
        method_value = ""
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
        return False, None

    def delete_element(self, id_: int) -> bool:
        if len(self.components) > id_:
            del self.components[id_]
            return True
        return False

    def get_possible_elements(self) -> List[Any]:
        return self.possible_elements

    def set_value(self, id_: int, value) -> bool:
        if len(self.components) > id_ and "value" in self.components[id_]:
            self.components[id_]["value"] = value
            return True
        return False

    def get_elements(self) -> List[Any]:
        return self.components

    def get_str_form(self):
        raw_parts = [component["str_form"] for component in self.components]
        self.raw_form = " ".join(raw_parts)
        return self.raw_form
