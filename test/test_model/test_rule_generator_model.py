from IPTables_Guide.model.rule_generator import *
from IPTables_Guide.model.parser_entries import *


def test_CommandComponent():
    commands = {
        "-A": {
            "str_form": "-A",
        }
    }

    component = CommandComponent(commands)
    assert component.find_fit(["hello"]) is None
    assert component.find_fit(["-A"]) == ({"str_form": "-A"}, [])
    assert component.find_fit(["-A", "hi"]) == ({"str_form": "-A"}, ["hi"])

    rule_a = MockRule([{"str_form": "-A"}])
    rule_b = MockRule([])

    assert component.possible_elements(rule_a.components) is None
    assert component.possible_elements(rule_b.components) == commands


class MockRule:
    def __init__(self, components):
        self.components = components


def test_StartComponent():
    start_strings = {"hi": {"str_form": "hi"}}
    component = StartComponent(start_strings)
    assert component.find_fit(["hi", "table", "..."]) == (
        {"str_form": "hi"},
        ["table", "..."],
    )
    assert component.find_fit(["table", "..."]) is None
    rule_a = MockRule([{"str_form": "hi"}])
    rule_b = MockRule([])

    assert component.possible_elements(rule_a.components) is None
    assert component.possible_elements(rule_b.components) == {"hi": {"str_form": "hi"}}


def test_ChainComponent():
    possible_chains = {"test_chain": {"tables": ["test_table"]}}
    component = ChainComponent(possible_chains).table("test_table")
    assert component.find_fit(["test_chain", "..."]) == (
        {"tables": ["test_table"]},
        ["..."],
    )
    component.table("not existing table")
    assert component.find_fit(["test_chain", "..."]) is None
    component.table("...")
    assert component.find_fit(["not_existing_chain"]) == None

    rule_a = MockRule([{"tables": ["test_table"]}])
    rule_b = MockRule([])

    assert component.possible_elements(rule_a.components) == None
    assert component.possible_elements(rule_b.components) == possible_chains


class MockRuleSpec(SignatureComponent):
    def __init__(self, consume_chars):
        self.consume_chars = consume_chars

    @override
    def find_fit(self, substr):
        if self.consume_chars == 0:
            return None
        return [{"test": "value"}], substr[self.consume_chars :]

    def possible_elements(self, components: List[Any]) -> Any:
        pass


def test_RuleSpecification():
    spec_components = [MockRuleSpec(0)]
    component = RuleSpecification(spec_components)
    assert component.find_fit(["hello", "123", "testing"]) is None

    spec_components = [MockRuleSpec(1), MockRuleSpec(2)]
    component = RuleSpecification(spec_components)
    assert component.find_fit(["hello", "123", "testing", "apple"]) == (
        [{"test": "value"}, {"test": "value"}],
        ["apple"],
    )


def test_TableComponent():
    possible_tables = {
        "-t NAT": {
            "str_form": "-t NAT",
            "explanation": "Hello",
            "value": "NAT",
        },
        "-t test_table": {"hello": "unit_test"},
    }

    component = TableComponent(possible_tables)
    result = component.find_fit(["-t", "test_table", "Nobody", "expects"])
    assert result == (possible_tables["-t test_table"], ["Nobody", "expects"])

    result = component.find_fit(["Nobody", "expects", "the"])
    assert result is None

    rule_a = MockRule([{"hello": "unit_test"}])
    rule_b = MockRule([])

    assert component.possible_elements(rule_a.components) is None
    assert component.possible_elements(rule_b.components) == possible_tables


class MockComponent(SignatureComponent):
    def __init__(self, match):
        self.match = match

    def find_fit(self, substr: List[str]) -> Optional[ParserHelper]:
        if substr[0] in self.match:
            return ParserHelper(
                FlagDetail(found="test", str_form=substr[0]), substr[1:]
            )
        else:
            return None

    def possible_elements(self, components: List[Any]) -> Any:
        pass


def test_Rule():
    signatures = [
        [
            MockComponent(["random", "string", "iptables"]),
            MockComponent(["-t"]),
            MockComponent(["filter"]),
        ]
    ]
    rule = Rule("iptables -t filter FORWARD -p tcp -j DROP", signatures, "", "", False)
    assert rule.get_elements() == []
    assert rule.parse_raw_form(True) == [
        [
            {"found": "test", "str_form": "iptables"},
            {"found": "test", "str_form": "-t"},
            {"found": "test", "str_form": "filter"},
        ],
        ["FORWARD", "-p", "tcp", "-j", "DROP"],
        [],
    ]
    signatures_2 = [
        [MockComponent(["random", "string", "iptables"]), MockComponent(["-t"])]
    ]
    rule.components = [
        {"str_form": "", "value": "delete me"},
        {"str_form": "-t ", "value": "delete me"},
    ]
    assert rule.delete_element(0)
    assert rule.components == [{"str_form": "-t ", "value": "delete me"}]
    assert not rule.delete_element(100)
    assert rule.set_value(0, "don't delete me")
    assert rule.components == [{"str_form": "-t ", "value": "don't delete me"}]
    assert not rule.set_value(100, "wont work")
