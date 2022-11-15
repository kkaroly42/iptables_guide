import sys

sys.path.append("./model/")
from IPTables_Guide.model.rule_generator import *


def test_CommandComponent():
    commands = {
        "-A": {
            "str_form": "-A",
        }
    }

    component = CommandComponent(commands)
    assert component.find_fit(["hello"]) == None
    assert component.find_fit(["-A"]) == ({"str_form": "-A"}, [])
    assert component.find_fit(["-A", "hi"]) == ({"str_form": "-A"}, ["hi"])


def test_StartComponent():
    start_strings = {"hi": {"str_form": "hi"}}
    component = StartComponent(start_strings)
    assert component.find_fit(["hi", "table", "..."]) == (
        {"str_form": "hi"},
        ["table", "..."],
    )
    assert component.find_fit(["table", "..."]) == None


def test_ChainComponent():
    possible_chains = {"test_chain": {"tables": ["test_table"]}}
    component = ChainComponent(possible_chains)
    assert component.find_fit(["test_chain", "..."], "test_table") == (
        {"tables": ["test_table"]},
        ["..."],
    )
    assert component.find_fit(["test_chain", "..."], "not_existing_table") == None
    assert component.find_fit(["not_existing_chain", "..."], "test_table") == None
