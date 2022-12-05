from socket import inet_aton
from typing import Dict, List, Optional, Tuple, Union, Any

start_strs = {
    "iptables": {
        "str_form": "iptables",
        "explanation": "Ezzel a kapcsolóval azt jelöljük meg, hogy a NAT(Network Address Translation) táblára fog vonatkozni az aktuális szabály.",
        "value": "NAT",
    }
}

possible_tables = {
    "-t NAT": {
        "str_form": "-t NAT",
        "explanation": "Ezzel a kapcsolóval azt jelöljük meg, hogy a NAT(Network Address Translation) táblára fog vonatkozni az aktuális szabály.",
        "value": "NAT",
    },
    "-t FILTER": {
        "str_form": "-t FILTER",
        "explanation": "Ezzel a kapcsolóval azt jelöljük meg, hogy a FILTER táblára fog vonatkozni az aktuális szabály.",
        "value": "FILTER",
    },
}

possible_commands = {
    "-A": {
        "str_form": "-A",
        "explanation": "Az append kapcsoló a lánc végére fűzi be az új szabályt.",
    },
    "-I": {
        "str_form": "-I",
        "explanation": "Az insert kapcsoló a láncon belül megadott helyre szúrja be az új szabályt.",
    },
}

possible_chains = {
    "INPUT": {
        "str_form": "INPUT",
        "value": "INPUT",
        "explanation": "",
        "tables": ["FILTER", "NAT"],
    },
    "FORWARD": {
        "str_form": "FORWARD",
        "value": "FORWARD",
        "explanation": "",
        "tables": ["FILTER"],
    },
    "OUTPUT": {
        "str_form": "OUTPUT",
        "explanation": "",
        "value": "OUTPUT",
        "tables": ["FILTER", "NAT"],
    },
}


def src_port(substr: List[str]):
    pairs = pair_iterator(substr)
    value = 0
    for pair in pairs:
        if pair[0] == "--sport":
            try:
                value = int(pair[1])
            except ValueError:
                return None
            substr.remove("--sport")
            substr.remove(pair[1])
            return {"src_form": "--sport {}".format(value), "value": value}, substr


def dst_port(substr: List[str]):
    pairs = pair_iterator(substr)
    value = 0
    for pair in pairs:
        if pair[0] == "--dport":
            try:
                value = int(pair[1])
            except ValueError:
                return None
            substr.remove("--dport")
            substr.remove(pair[1])
            return {"src_form": "--dport {}".format(value), "value": value}, substr


possible_tcp_options = [
    {"str_form": "--sport", "parser_method": src_port},
    {"str_form": "--dport", "parser_method": dst_port},
]


def pair_iterator(substr: List[str]):
    i = 0
    while i < len(substr) - 1:
        yield substr[i], substr[i + 1]
        i += 1


def validate_ip(ip: str):
    ip_and_mask = ip.split("/")
    try:
        inet_aton(ip_and_mask[0])
        if len(ip_and_mask) == 2:
            return ip_and_mask[1].isdigit()
        elif len(ip_and_mask) == 1:
            return True
        return False
    except OSError:
        return False


class TCPParser:
    def __init__(self, start_string, possible_options):
        self.start_string = start_string
        self.possible_options = possible_options

    def find_fit(self, substr: List[str]):
        specs = []
        pairs = pair_iterator(substr)
        for pair in pairs:
            unified_pair = " ".join(pair)
            if unified_pair in self.start_string:
                specs.append(self.start_string[unified_pair])
                substr.remove(pair[0])
                substr.remove(pair[1])
                pairs.close()
        if specs:
            for option in self.possible_options:
                for element in substr:
                    if option["str_form"] == element:
                        spec = option.copy()
                        if "parser_method" in option:
                            result, substr = option["parser_method"](substr)
                            spec["value"] = result["value"]
                            spec["str_form"] = result["src_form"]
                        else:
                            substr.remove(element)
                        specs.append(spec)
            return specs, substr
        else:
            return None


possible_udp_options = [
    {"str_form": "--sport", "parser_method": src_port},
    {"str_form": "--dport", "parser_method": dst_port},
]


class UDPParser:
    def __init__(self, start_string, possible_options):
        self.start_string = start_string
        self.possible_options = possible_options

    def find_fit(self, substr: List[str]):
        specs = []
        pairs = pair_iterator(substr)
        for pair in pairs:
            unified_pair = " ".join(pair)
            if unified_pair in self.start_string:
                specs.append(self.start_string[unified_pair])
                substr.remove(pair[0])
                substr.remove(pair[1])
                pairs.close()
        if specs:
            for option in self.possible_options:
                for element in substr:
                    print(option)
                    if option["str_form"] == element:
                        if "parser_method" in option:
                            result, substr = option["parser_method"](substr)
                            spec = option.copy()
                            spec["value"] = result["value"]
                            spec["str_form"] = result["src_form"]
                        else:
                            spec = option
                            substr.remove(element)
                    specs.append(spec)
            print("returning:", specs)
            return specs, substr
        else:
            return None


class JumpParser:
    def __init__(self, actions):
        self.actions = actions

    def find_fit(self, substr: List[str]):
        if len(substr) > 1:
            start = substr[0] + " " + substr[1]
            for action in self.actions:
                if start == self.actions[action]["str_form"]:
                    return self.actions[action], substr[2:]
        return None


class SourceParser:
    def __init__(self):
        self.start_strings = ["-s", "--source"]
        self.repr_dict = {"str_form": "-s", "explanation": ""}

    def find_fit(self, substr: List[str]):
        if len(substr) > 1:
            if substr[0] in self.start_strings and validate_ip(substr[1]):
                to_return = self.repr_dict.copy()
                to_return["str_form"] = to_return["str_form"] + " " + substr[1]
                to_return["value"] = substr[1]
                return to_return, substr[2:]
        return None


class DestinationParser:
    def __init__(self):
        self.start_strings = ["-d", "--destination"]
        self.repr_dict = ({"str_form": "-d", "explanation": ""},)

    def find_fit(self, substr: List[str]):
        if len(substr) > 1:
            if substr[0] in self.start_strings and validate_ip(substr[1]):
                to_return = self.repr_dict.copy()
                to_return["value"] = substr[1]
                return to_return, substr[2:]
        return None


class InputInterfaceParser:
    def __init__(self):
        self.start_strings = ["-i", "--in-interface"]
        self.repr_dict = ({"str_form": "-i", "explanation": ""},)

    def find_fit(self, substr: List[str]):
        if len(substr) > 1:
            if substr[0] in self.start_strings:
                to_return = self.repr_dict.copy()
                to_return["value"] = substr[1]
                return to_return, substr[2:]
        return None


class OutputInterfaceParser:
    def __init__(self):
        self.start_strings = ["-o", "--out-interface"]
        self.repr_dict = ({"str_form": "-o", "explanation": ""},)

    def find_fit(self, substr: List[str]):
        if len(substr) > 1:
            if substr[0] in self.start_strings:
                to_return = self.repr_dict.copy()
                to_return["value"] = substr[1]
                return to_return, substr[2:]
        return None


class StateParser:
    def __init__(self):
        self.start_string = "--state"
        self.possible_states = ["INVALID", "ESTABLISHED", "NEW", "RELATED"]
        self.repr_dict = ({"str_form": "--state", "explanation": ""},)

    def find_fit(self, substr: List[str]):
        if len(substr) > 1:
            if substr[0] == self.start_string and substr[1] in self.possible_states:
                to_return = self.repr_dict.copy()
                to_return["value"] = substr[1]
                return to_return, substr[2:]
        return None
