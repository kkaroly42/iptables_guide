from IPTables_Guide.model.rule_system import *
import IPTables_Guide.model.parser_entries as parser_entries


def gen_rules_to_file():
    tcp = TCPParser()
    j_drop = JumpParser()
    signatures = [
        [
            StartComponent(start_strs),
            TableComponent(possible_tables),
            CommandComponent(parser_entries.possible_commands),
            ChainComponent(possible_chains),
            RuleSpecification([tcp, j_drop]),
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
        "iptables -t filter -A INPUT -p tcp --sport 1222 -j DROP", "", ""
    )
    rule_b = system.create_rule_from_raw_str(
        "iptables -t nat -A PREROUTING -p tcp --dport 5001 -j DNAT --to-destination 192.168.0.11",
        "",
        "",
    )
    system.append_rule(Table("FILTER"), Chain("INPUT"), rule)
    system.append_rule(Table("NAT"), Chain("PREROUTING"), rule_b)
    system.write_to_file(".ci_input.txt")


if __name__ == "__main__":
    gen_rules_to_file()
