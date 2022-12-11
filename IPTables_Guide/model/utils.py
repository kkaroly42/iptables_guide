from typing import Callable, TypedDict, List, NamedTuple


# TODO maybe add a way to check if the key is set
class FlagDetail(TypedDict, total=False):
    str_form: str
    src_form: str
    explanation: str
    value: str
    tables: List[str]
    type: str
    parser_method: Callable
    condition_method: Callable
    action_method: Callable
    forms: List[str]
    found: str


# TODO
class ParserHelper(NamedTuple):
    parsed: FlagDetail | List[FlagDetail]
    others: List[str]
