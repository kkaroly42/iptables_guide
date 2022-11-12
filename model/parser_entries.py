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
    "": {
        "str_form": "-A",
        "explanation": "Az append kapcsoló a lánc végére fűzi be az új szabályt.",
    },
    "-I": {
        "str_form": "-I",
        "explanation": "Az insert kapcsoló a láncon belül megadott helyre szúrja be az új szabályt.",
    },
}
