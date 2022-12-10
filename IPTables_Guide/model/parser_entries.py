import ipaddress
from typing import Dict, List, Optional, Tuple, Union, Any
import scapy.all as all

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
    "PREROUTING": {
        "str_form": "PREROUTING",
        "explanation": "",
        "value": "PREROUTING",
        "tables": ["NAT"],
    },
    "POSTROUTING": {
        "str_form": "POSTROUTING",
        "explanation": "",
        "value": "POSTROUTING",
        "tables": ["NAT"],
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
            return {
                "src_form": "--sport {}".format(value),
                "value": value,
                "type": "condition",
            }, substr


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
            return {
                "src_form": "--dport {}".format(value),
                "value": value,
                "type": "condition",
            }, substr


def check_tcp(packet: Any, value: str):
    return packet.haslayer(all.TCP)


def check_udp(packet: Any, value: str):
    return packet.haslayer(all.UDP)


def check_tcp_src_port(packet: Any, value: str):
    if packet.haslayer(all.TCP):
        try:
            port_as_int = int(value)
            return packet[all.TCP][sport] == port_as_int
        except ValueError:
            return False
    return False


def check_tcp_dport(packet: Any, value: str):
    if packet.haslayer(all.TCP):
        try:
            port_as_int = int(value)
            return packet[all.TCP][dport] == port_as_int
        except ValueError:
            return False
    return False


def check_udp_src_port(packet: Any, value: str):
    if packet.haslayer(all.UDP):
        try:
            port_as_int = int(value)
            return packet[all.UDP][sport] == port_as_int
        except ValueError:
            return False
    return False


def check_udp_dport(packet: Any, value: str):
    if packet.haslayer(all.UDP):
        try:
            port_as_int = int(value)
            return packet[all.UDP][dport] == port_as_int
        except ValueError:
            return False
    return False


def check_source_ip(packet: Any, value: str):
    if packet.haslayer(all.IP):
        if packet[all.IP].src == value:
            return True
        else:
            try:
                network = ipaddress.ip_network(value)
                ip = ipaddress.ip_address(packet[all.IP.src])
                return ip in network
            except ValueError:
                return False


def check_destination_ip(packet: Any, value: str):
    if packet.haslayer(all.IP):
        if packet[all.IP].dst == value:
            return True
        else:
            try:
                network = ipaddress.ip_network(value)
                ip = ipaddress.ip_address(packet[all.IP.dst])
                return ip in network
            except ValueError:
                return False


possible_tcp_options = [
    {
        "str_form": "--sport",
        "parser_method": src_port,
        "type": "condition",
        "condition_method": check_tcp_src_port,
    },
    {
        "str_form": "--dport",
        "parser_method": dst_port,
        "type": "condition",
        "condition_method": check_tcp_dport,
    },
]


def pair_iterator(substr: List[str]):
    i = 0
    while i < len(substr) - 1:
        yield substr[i], substr[i + 1]
        i += 1


def validate_ip(ip: str, delimiter="/") -> bool:
    if delimiter == "/":
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            try:
                ipaddress.ip_network(ip, strict=False)
                return True
            except ValueError:
                return False
    else:
        parts = ip.split(":")
        try:
            ipaddress.ip_address(parts[0])
            if len(parts) == 3:
                int(parts[2])
            return True
        except ValueError:
            return False


class TCPParser:
    def __init__(self, start_string={}, possible_options=[]):
        if start_string:
            self.start_string = start_string
        else:
            self.start_string = {
                "-p tcp": {
                    "str_form": "-p tcp",
                    "type": "condition",
                    "condition_method": check_tcp,
                }
            }
        if possible_options:
            self.possible_options = possible_options
        else:
            self.possible_options = possible_tcp_options

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
    {
        "str_form": "--sport",
        "parser_method": src_port,
        "type": "condition",
        "condition_method": check_udp_src_port,
    },
    {
        "str_form": "--dport",
        "parser_method": dst_port,
        "type": "condition",
        "condition_method": check_udp_dport,
    },
]


class UDPParser:
    def __init__(self, start_string="", possible_options=[]):
        if start_string:
            self.start_string = start_string
        else:
            self.start_string = {
                "-p udp": {
                    "str_form": "-p udp",
                    "type": "condition",
                    "condition_method": check_udp,
                }
            }
        if possible_options:
            self.possible_options = possible_options
        else:
            self.possible_options = possible_tcp_options

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
                        if "parser_method" in option:
                            result, substr = option["parser_method"](substr)
                            spec = option.copy()
                            spec["value"] = result["value"]
                            spec["str_form"] = result["src_form"]
                        else:
                            spec = option
                            substr.remove(element)
                        specs.append(spec)
            return specs, substr
        else:
            return None


def drop_action(packet: Any, value: str):
    return "DROP"


def accept_action(packet: Any, value: str):
    return packet


def snat_action(packet: Any, value: str):
    parts = value.split(":")
    if packet.haslayer(all.IP):
        packet[all.IP].src = parts[0]
        if len(parts) == 2 and parts[1].isdigit():
            if packet.haslayer(all.TCP):
                packet[all.TCP].sport = int(parts[1])
                return packet
            elif packet.haslayer(all.UDP):
                packet[all.UDP].sport = int(parts[1])
                return packet
    return None


def dnat_action(packet: Any, value: str):
    parts = value.split(":")
    if packet.haslayer(all.IP):
        packet[all.IP].dst = parts[0]
        if len(parts) == 2 and parts[1].isdigit():
            if packet.haslayer(all.TCP):
                packet[all.TCP].dport = int(parts[1])
                return packet
            elif packet.haslayer(all.UDP):
                packet[all.UDP].dport = int(parts[1])
                return packet
    return None


class JumpParser:
    def __init__(self):
        self.actions = {
            "DROP": {
                "str_form": "-j DROP",
                "forms": ["--jump DROP"],
                "type": "action",
                "action_method": drop_action,
                "explanation": "",
            },
            "ACCEPT": {
                "str_form": "-j ACCEPT",
                "forms": ["--jump ACCEPT", "--jump ACCEPT"],
                "type": "action",
                "action_method": accept_action,
                "explanation": "",
            },
            "SNAT": {
                "str_form": "-j SNAT --to-source",
                "forms": ["--jump SNAT --to-source"],
                "type": "action",
                "action_method": snat_action,
                "explanation": "",
            },
            "DNAT": {
                "str_form": "-j DNAT --to-destination",
                "forms": "--jump DNAT --to-destination",
                "type": "action",
                "action_method": dnat_action,
                "explanation": "",
            },
        }

    def find_fit(self, substr: List[str]):
        if len(substr) > 1:
            start = substr[0] + " " + substr[1]
            for action in self.actions:
                if action in ["DROP", "ACCEPT"]:
                    if (
                        start == self.actions[action]["str_form"]
                        or start in self.actions[action]["forms"]
                    ):
                        to_return = self.actions[action].copy()
                        to_return["str_form"] = start
                        return to_return, substr[2:]
                else:
                    if len(substr) > 3:
                        start = " ".join(substr[:3])
                        if (
                            start == self.actions[action]["str_form"]
                            or start in self.actions[action]["forms"]
                        ) and validate_ip(substr[3], ":"):
                            to_return = self.actions[action].copy()
                            to_return["value"] = substr[3]
                            to_return["str_form"] += " {}".format(substr[3])
                            print(to_return)
                            return to_return, substr[4:]
        return None


class SourceParser:
    def __init__(self):
        self.start_strings = ["-s", "--source"]
        self.repr_dict = {
            "str_form": "-s",
            "explanation": "",
            "type": "condition",
            "condition_method": check_source_ip,
        }

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
        self.repr_dict = (
            {
                "str_form": "-d",
                "explanation": "",
                "type": "condition",
                "condition_method": check_destination_ip,
            },
        )

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
        self.repr_dict = (
            {"str_form": "--state", "explanation": "", "type": "condition"},
        )

    def find_fit(self, substr: List[str]):
        if len(substr) > 1:
            if substr[0] == self.start_string and substr[1] in self.possible_states:
                to_return = self.repr_dict.copy()
                to_return["value"] = substr[1]
                return to_return, substr[2:]
        return None
