from IPTables_Guide.model.rule_system import *
import IPTables_Guide.model.parser_entries as parser_entries
import os


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
        "iptables -t FILTER -A INPUT -p tcp --sport 80", "", ""
    )
    system.append_rule(DefaultTableType("FILTER"), DefaultChainType("INPUT"), rule)
    read_rule = system.get_rule(
        DefaultTableType("FILTER"), DefaultChainType("INPUT"), 0
    )
    assert read_rule.get_str_form() == "iptables -t FILTER -A INPUT -p tcp --sport 80"
    rule_list = system.get_rules_in_chain(
        DefaultTableType("FILTER"), DefaultChainType("INPUT")
    )
    assert (
        rule_list[0].get_str_form() == "iptables -t FILTER -A INPUT -p tcp --sport 80"
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
        "iptables -t FILTER -A INPUT -j DROP -s 192.168.56.1/24 -p tcp --sport 80 -j DROP",
        "",
        "",
    )
    system.append_rule(DefaultTableType("FILTER"), DefaultChainType("INPUT"), rule)
    read_rule = system.get_rule(
        DefaultTableType("FILTER"), DefaultChainType("INPUT"), 0
    )
    assert (
        read_rule.get_str_form()
        == "iptables -t FILTER -A INPUT -p tcp --sport 80 -j DROP -s 192.168.56.1/24"
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
    rule = system.create_rule_from_raw_str("iptables -t FILTER -A INPUT", "", "")
    system.append_rule(DefaultTableType("FILTER"), DefaultChainType("INPUT"), rule)
    read_rule = system.get_rule(
        DefaultTableType("FILTER"), DefaultChainType("INPUT"), 0
    )
    assert read_rule.get_str_form() == "iptables -t FILTER -A INPUT"
    rule_list = system.get_rules_in_chain(
        DefaultTableType("FILTER"), DefaultChainType("INPUT")
    )
    assert rule_list[0].get_str_form() == "iptables -t FILTER -A INPUT"
    rule_b = system.create_rule_from_raw_str(
        "iptables -t FILTER -A INPUT -j DROP", "", ""
    )
    system.insert_rule(DefaultTableType("FILTER"), DefaultChainType("INPUT"), rule_b, 0)
    read_rule = system.get_rule(
        DefaultTableType("FILTER"), DefaultChainType("INPUT"), 0
    )
    assert read_rule.get_str_form() == "iptables -t FILTER -A INPUT -j DROP"
    system.delete_rule(DefaultTableType("FILTER"), DefaultChainType("INPUT"), 0)
    read_rule = system.get_rule(
        DefaultTableType("FILTER"), DefaultChainType("INPUT"), 0
    )
    assert read_rule.get_str_form() == "iptables -t FILTER -A INPUT"
    system.overwrite_rule(
        DefaultTableType("FILTER"), DefaultChainType("INPUT"), 0, rule_b
    )
    read_rule = system.get_rule(
        DefaultTableType("FILTER"), DefaultChainType("INPUT"), 0
    )
    assert read_rule.get_str_form() == "iptables -t FILTER -A INPUT -j DROP"


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
    rule = system.create_rule_from_raw_str("iptables -t FILTER -A INPUT", "", "")
    rule_b = system.create_rule_from_raw_str(
        "iptables -t FILTER -A INPUT -j DROP", "", ""
    )
    system.append_rule(DefaultTableType("FILTER"), DefaultChainType("INPUT"), rule)
    system.append_rule(DefaultTableType("FILTER"), DefaultChainType("INPUT"), rule_b)
    system.write_to_file("test_a.txt")
    system_b = RuleSystem(signatures)
    system_b.read_from_file("test_a.txt")
    read_rule = system.get_rule(
        DefaultTableType("FILTER"), DefaultChainType("INPUT"), 0
    )
    assert read_rule.get_str_form() == "iptables -t FILTER -A INPUT"
    read_rule = system.get_rule(
        DefaultTableType("FILTER"), DefaultChainType("INPUT"), 1
    )
    assert read_rule.get_str_form() == "iptables -t FILTER -A INPUT -j DROP"


def test_pcap_operation():
    try:
        os.remove(os.path.join("pcaps", "out.pcap"))
    except FileNotFoundError:
        pass
    system = RuleSystem()
    rule = system.create_rule_from_raw_str(
        "iptables -t FILTER -A FORWARD -p tcp -j DROP", "", ""
    )
    # rule_b = system.create_rule_from_raw_str("iptables -t nat -A POSTROUTING -p udp -j SNAT --to-source 10.0.0.1", "", "")
    system.append_rule(DefaultTableType("FILTER"), DefaultChainType("FORWARD"), rule)
    system.run_chain_on_raw_packets(
        os.path.join("pcaps", "example.pcap"),
        os.path.join("pcaps", "out.pcap"),
        DefaultTableType("FILTER"),
        DefaultChainType("FORWARD"),
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
        "iptables -t NAT -A PREROUTING -j SNAT --to-source 192.168.56.1",
        "",
        "",
    )
    system.append_rule(DefaultTableType("NAT"), DefaultChainType("PREROUTING"), rule)
    read_rule = system.get_rule(
        DefaultTableType("NAT"), DefaultChainType("PREROUTING"), 0
    )
    assert (
        read_rule.get_str_form()
        == "iptables -t NAT -A PREROUTING -j SNAT --to-source 192.168.56.1"
    )
