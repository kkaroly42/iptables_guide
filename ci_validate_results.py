from typing import List


filter_expected = ["-A INPUT -p tcp -m tcp --sport 1222 -j DROP"]
nat_expected = [
    "-A PREROUTING -p tcp -m tcp --dport 5001 -j DNAT --to-destination 192.168.0.11"
]


def read_from_file(filename: str) -> List[str]:
    f = open(filename, "r")
    f_content = f.readlines()
    f.close()
    return f_content


def get_rules_from_filter(ips_content: List[str]) -> List[str]:
    relevant_content = []
    start_relevant = False
    for line in ips_content:
        if start_relevant and ("COMMIT" in line):
            break
        if start_relevant:
            relevant_content.append(line)
        if "*filter" in line:
            start_relevant = True
    return relevant_content


def get_rules_from_nat(ips_content: List[str]) -> List[str]:
    relevant_content = []
    start_relevant = False
    for line in ips_content:
        if start_relevant and ("COMMIT" in line):
            break
        if start_relevant:
            relevant_content.append(line)
        if "*nat" in line:
            start_relevant = True
    return relevant_content


def validate(filter_rules: List[str], nat_rules: List[str]):
    filter_rules = [x.strip("\n") for x in filter_rules]
    nat_rules = [x.strip("\n") for x in nat_rules]
    for frule in filter_expected:
        assert frule in filter_rules
    for nrule in nat_expected:
        assert nrule in nat_rules


if __name__ == "__main__":
    ips_content = read_from_file(".ci_results.txt")
    filter_rules = get_rules_from_filter(ips_content)
    nat_rules = get_rules_from_nat(ips_content)
    validate(filter_rules, nat_rules)
