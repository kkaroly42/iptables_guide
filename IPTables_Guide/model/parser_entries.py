from socket import inet_aton
from typing import Dict, List, Optional, Tuple, Union, Any

start_strs = {
    "iptables": {
        "str_form": "iptables",
        "explanation": "Kezdő parancs.",
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
        "value": "INPUT"
        "explanation": "",
        "tables" : ["FILTER", "NAT"]
    },
    "FORWARD": {
        "str_form": "FORWARD",
        "value": "FORWARD"
        "explanation": "",
    },
    "OUTPUT": {
        "str_form": "OUTPUT",
        "explanation": "",
        "value": "OUTPUT"
        "tables" : ["FILTER", "NAT"]
    }
}

def validate_ip(ip: str):
    try:
        inet_aton(ip)
        return True
    except OSError:
        return False

class TCPParser:
    def __init__(self, start_string, possible_options):
        self.start_string = start_string
        self.possible_options = possible_options

    def find_fit(self, substr: List[str]):         
        return {"protcol filter": {"str_form" : "-p tcp"}}, substr[2:]

class JumpParser:
    def __init__(self, actions):
        self.actions = actions

    def find_fit(self, substr: List[str]):
        start = substr[0] + " " + substr[1]
        for action in self.actions:
            if start == self.actions[action]["str_form"]:
                return self.actions[action], substr[2:]
                    