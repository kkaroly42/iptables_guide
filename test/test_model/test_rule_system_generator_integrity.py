from IPTables_Guide.model.rule_system import *
import IPTables_Guide.model.parser_entries as parser_entries
import os
import scapy.all


def test_tcp():
    tcp = TCPParser()
    j_drop = JumpParser()
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
    system = RuleSystem()
    rule = system.create_rule_from_raw_str(
        "iptables -t filter -A INPUT -p tcp --sport 80", "", ""
    )
    system.append_rule(Table("FILTER"), Chain("INPUT"), rule)
    read_rule = system.get_rule(Table("FILTER"), Chain("INPUT"), 0)
    assert read_rule.get_str_form() == "iptables -t filter -A INPUT -p tcp --sport 80"
    rule_list = system.get_rules_in_chain(Table("FILTER"), Chain("INPUT"))
    assert (
        rule_list[0].get_str_form() == "iptables -t filter -A INPUT -p tcp --sport 80"
    )


def test_ip():
    tcp = TCPParser()
    j_drop = JumpParser()
    source_parser = SourceParser()
    signatures = [
        [
            StartComponent(start_strs),
            TableComponent(possible_tables),
            CommandComponent(parser_entries.possible_commands),
            ChainComponent(possible_chains),
            RuleSpecification([j_drop, tcp, source_parser]),
        ],
        [
            StartComponent(start_strs),
            TableComponent(possible_tables),
            CommandComponent(parser_entries.possible_commands),
            ChainComponent(possible_chains),
        ],
    ]
    system = RuleSystem()
    rule = system.create_rule_from_raw_str(
        "iptables -t filter -A INPUT -j DROP -s 192.168.56.1/24 -p tcp --sport 80 -j DROP",
        "",
        "",
    )
    system.append_rule(Table("FILTER"), Chain("INPUT"), rule)
    read_rule = system.get_rule(Table("FILTER"), Chain("INPUT"), 0)
    assert (
        read_rule.get_str_form()
        == "iptables -t filter -A INPUT -p tcp --sport 80 -j DROP -s 192.168.56.1/24"
    )


def test_simple_rule():
    tcp = TCPParser()
    j_drop = JumpParser()
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
    rule = system.create_rule_from_raw_str("iptables -t filter -A INPUT", "", "")
    system.append_rule(Table("FILTER"), Chain("INPUT"), rule)
    read_rule = system.get_rule(Table("FILTER"), Chain("INPUT"), 0)
    assert read_rule.get_str_form() == "iptables -t filter -A INPUT"
    rule_list = system.get_rules_in_chain(Table("FILTER"), Chain("INPUT"))
    assert rule_list[0].get_str_form() == "iptables -t filter -A INPUT"
    rule_b = system.create_rule_from_raw_str(
        "iptables -t filter -A INPUT -j DROP", "", ""
    )
    system.insert_rule(Table("FILTER"), Chain("INPUT"), rule_b, 0)
    read_rule = system.get_rule(Table("FILTER"), Chain("INPUT"), 0)
    assert read_rule.get_str_form() == "iptables -t filter -A INPUT -j DROP"
    system.delete_rule(Table("FILTER"), Chain("INPUT"), 0)
    read_rule = system.get_rule(Table("FILTER"), Chain("INPUT"), 0)
    assert read_rule.get_str_form() == "iptables -t filter -A INPUT"
    system.overwrite_rule(Table("FILTER"), Chain("INPUT"), 0, rule_b)
    read_rule = system.get_rule(Table("FILTER"), Chain("INPUT"), 0)
    assert read_rule.get_str_form() == "iptables -t filter -A INPUT -j DROP"


def test_file_operation():
    tcp = TCPParser()
    j_drop = JumpParser()
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
    rule = system.create_rule_from_raw_str("iptables -t filter -A INPUT", "", "")
    rule_b = system.create_rule_from_raw_str(
        "iptables -t filter -A INPUT -j DROP", "", ""
    )
    system.append_rule(Table("FILTER"), Chain("INPUT"), rule)
    system.append_rule(Table("FILTER"), Chain("INPUT"), rule_b)
    system.write_to_file("test_a.txt")
    system_b = RuleSystem(signatures)
    system_b.read_from_file("test_a.txt")
    read_rule = system.get_rule(Table("FILTER"), Chain("INPUT"), 0)
    assert read_rule.get_str_form() == "iptables -t filter -A INPUT"
    read_rule = system.get_rule(Table("FILTER"), Chain("INPUT"), 1)
    assert read_rule.get_str_form() == "iptables -t filter -A INPUT -j DROP"


def test_pcap_operation():
    try:
        os.remove(os.path.join("pcaps", "out.pcap"))
    except FileNotFoundError:
        pass
    system = RuleSystem()
    rule = system.create_rule_from_raw_str(
        "iptables -t filter -A FORWARD -p tcp -j DROP", "", ""
    )
    # rule_b = system.create_rule_from_raw_str("iptables -t nat -A POSTROUTING -p udp -j SNAT --to-source 10.0.0.1", "", "")
    system.append_rule(Table("FILTER"), Chain("FORWARD"), rule)
    system.run_chain_on_raw_packets(
        os.path.join("pcaps", "example.pcap"),
        os.path.join("pcaps", "out.pcap"),
        Table("FILTER"),
        Chain("FORWARD"),
    )
    with open(os.path.join("pcaps", "out.pcap"), "rb") as f_1:
        with open(os.path.join("pcaps", "expected.pcap"), "rb") as f_2:
            assert f_1.read() == f_2.read()


def test_nat():
    tcp = TCPParser()
    j_drop = JumpParser()
    source_parser = SourceParser()
    system = RuleSystem()
    rule = system.create_rule_from_raw_str(
        "iptables -t nat -A PREROUTING -j SNAT --to-source 192.168.56.1",
        "",
        "",
    )
    system.append_rule(Table("NAT"), Chain("PREROUTING"), rule)
    read_rule = system.get_rule(Table("NAT"), Chain("PREROUTING"), 0)
    assert (
        read_rule.get_str_form()
        == "iptables -t nat -A PREROUTING -j SNAT --to-source 192.168.56.1"
    )
