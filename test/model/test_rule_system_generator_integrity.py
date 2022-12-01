from IPTables_Guide.model.rule_system import (
    JumpParser,
    StartComponent,
    TableComponent,
    CommandComponent,
    ChainComponent,
    possible_chains,
    possible_commands,
    possible_tables,
    start_strs,
    RuleSpecification,
    RuleSystem,
    Table,
    Chain,
)
import IPTables_Guide.model.parser_entries as parser_entries
from IPTables_Guide.model.parser_entries import TCPParser, possible_tcp_options


def test_tcp():
    tcp = TCPParser({"-p tcp": {"str_form": "-p tcp"}}, possible_tcp_options)
    j_drop = JumpParser({"DROP": {"str_form": "-j DROP"}})
    signatures = [
        [
            StartComponent(start_strs),
            TableComponent(possible_tables),
            CommandComponent(parser_entries.possible_commands),
            ChainComponent(possible_chains),
            RuleSpecification([j_drop, tcp]),
        ],
        [
            StartComponent(start_strs),
            TableComponent(possible_tables),
            CommandComponent(parser_entries.possible_commands),
            ChainComponent(possible_chains),
        ],
    ]
    system = RuleSystem(signatures)
    rule = system.create_rule_from_raw_str(
        "iptables -t FILTER -A INPUT -p tcp --sport 80", "", ""
    )
    system.append_rule(Table("FILTER"), Chain("INPUT"), rule)
    read_rule = system.get_rule(Table("FILTER"), Chain("INPUT"), 0)
    assert read_rule.get_str_form() == "iptables -t FILTER -A INPUT -p tcp --sport 80"
    rule_list = system.get_rules_in_chain(Table("FILTER"), Chain("INPUT"))
    assert (
        rule_list[0].get_str_form() == "iptables -t FILTER -A INPUT -p tcp --sport 80"
    )


def test_simple_rule():
    tcp = TCPParser({"-p tcp": {"str_form": ["-p", "tcp"]}}, [])
    j_drop = JumpParser({"DROP": {"str_form": "-j DROP"}})
    signatures = [
        [
            StartComponent(start_strs),
            TableComponent(possible_tables),
            CommandComponent(parser_entries.possible_commands),
            ChainComponent(possible_chains),
            RuleSpecification([j_drop]),
        ],
        [
            StartComponent(start_strs),
            TableComponent(possible_tables),
            CommandComponent(parser_entries.possible_commands),
            ChainComponent(possible_chains),
        ],
    ]
    system = RuleSystem(signatures)
    rule = system.create_rule_from_raw_str("iptables -t FILTER -A INPUT", "", "")
    system.append_rule(Table("FILTER"), Chain("INPUT"), rule)
    read_rule = system.get_rule(Table("FILTER"), Chain("INPUT"), 0)
    assert read_rule.get_str_form() == "iptables -t FILTER -A INPUT"
    rule_list = system.get_rules_in_chain(Table("FILTER"), Chain("INPUT"))
    assert rule_list[0].get_str_form() == "iptables -t FILTER -A INPUT"
    rule_b = system.create_rule_from_raw_str(
        "iptables -t FILTER -A INPUT -j DROP", "", ""
    )
    system.insert_rule(Table("FILTER"), Chain("INPUT"), rule_b, 0)
    read_rule = system.get_rule(Table("FILTER"), Chain("INPUT"), 0)
    assert read_rule.get_str_form() == "iptables -t FILTER -A INPUT -j DROP"
    system.delete_rule(Table("FILTER"), Chain("INPUT"), 0)
    read_rule = system.get_rule(Table("FILTER"), Chain("INPUT"), 0)
    assert read_rule.get_str_form() == "iptables -t FILTER -A INPUT"
    system.overwrite_rule(Table("FILTER"), Chain("INPUT"), 0, rule_b)
    read_rule = system.get_rule(Table("FILTER"), Chain("INPUT"), 0)
    assert read_rule.get_str_form() == "iptables -t FILTER -A INPUT -j DROP"


def test_file_operation():
    tcp = TCPParser({"-p tcp": {"str_form": ["-p", "tcp"]}}, [])
    j_drop = JumpParser({"DROP": {"str_form": "-j DROP"}})
    signatures = [
        [
            StartComponent(start_strs),
            TableComponent(possible_tables),
            CommandComponent(parser_entries.possible_commands),
            ChainComponent(possible_chains),
            RuleSpecification([j_drop]),
        ],
        [
            StartComponent(start_strs),
            TableComponent(possible_tables),
            CommandComponent(parser_entries.possible_commands),
            ChainComponent(possible_chains),
        ],
    ]
    system = RuleSystem(signatures)
    rule = system.create_rule_from_raw_str("iptables -t FILTER -A INPUT", "", "")
    rule_b = system.create_rule_from_raw_str(
        "iptables -t FILTER -A INPUT -j DROP", "", ""
    )
    system.append_rule(Table("FILTER"), Chain("INPUT"), rule)
    system.append_rule(Table("FILTER"), Chain("INPUT"), rule_b)
    system.write_to_file(".test_a.txt")
    system_b = RuleSystem(signatures)
    system_b.read_from_file(".test_a.txt")
    read_rule = system.get_rule(Table("FILTER"), Chain("INPUT"), 0)
    assert read_rule.get_str_form() == "iptables -t FILTER -A INPUT"
    read_rule = system.get_rule(Table("FILTER"), Chain("INPUT"), 1)
    assert read_rule.get_str_form() == "iptables -t FILTER -A INPUT -j DROP"
