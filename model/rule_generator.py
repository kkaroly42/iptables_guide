from enum import Enum
from typing import Dict, List


class Table(Enum):
    FILTER = 1
    NAT = 2
    MANGLE = 3


class Chain(Enum):
    INPUT = 1
    OUTPUT = 2
    FORWARD = 3
    PREROUTING = 4
    POSTROUTING = 5


class RuleComponent:
    def __init__(self, raw_form: str):
        parsed_form = self.parse_raw_form(raw_form)
        self.str_form = parsed_form["str_form"]
        self.explanation = parsed_form["explanation"]
        if "value" in parsed_form:
            self.value = parsed_form["value"]
        else:
            self.value = None

    def parse_raw_form(self, raw_form: str) -> Dict[str, str]:
        pass

    def has_value(self) -> bool:
        return self.value is not None


class Rule:
    def __init__(self, table: Table, chain: Chain):
        self.table = table
        self.chain = chain
        self.components = []

    def __init__(self, raw_form):
        parsed_form = self.parse_raw_form(raw_form)

    def parse_raw_form(self, raw_form) -> List[Dict[str, str]]:
        pass

    def check_total_correctness(self) -> bool:
        pass

    def check_partial_correctness(self) -> bool:
        pass

    def delete_element(self, id) -> bool:
        pass

    def get_possible_elements(self) -> List:
        pass

    def set_value(self) -> bool:
        pass

    def get_elements(self):
        pass
