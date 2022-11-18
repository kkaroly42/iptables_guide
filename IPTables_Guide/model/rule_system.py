from enum import Enum
from typing import List, Dict, Optional
# from IPTables_Guide.model.packets import Packet
# from rule_generator import Rule

# Remove once the real class can be imported
class Rule:
    pass

class Packet:
    pass

class Table(Enum):
    FILTER = "filter"
    NAT = "nat"
    MANGLE = "mangle"

class Chain(Enum):
    INPUT = "input"
    OUTPUT = "output"
    PREROUTING = "prerouting"
    POSTROUTING = "postrouting"
    FORWARD = "forward"

class RuleSystem:
    _validChains: Dict[Table, List[Chain]] = {
        Table.FILTER: [Chain.INPUT, Chain.FORWARD],
        Table.NAT: [Chain.INPUT, Chain.FORWARD, Chain.PREROUTING, Chain.POSTROUTING],
        Table.MANGLE: [Chain.INPUT, Chain.OUTPUT, Chain.FORWARD, Chain.PREROUTING, Chain.POSTROUTING]
    }
    
    def __init__(
        self,
        rules: List[Rule],
        table: Optional[Table], # Could be str instead of Enum
        chain: Optional[Chain] # Could be str instead of Enum
    ):
        self.rules = rules

        self.table = table,
        if (chain != None and table != None): # OPTIONAL
            if (chain not in self._validChains[table]):
                raise ValueError() 
        self.chain = chain,

    def get_rule(self, id) -> Rule:
        pass

    def update_rule(self, id, rule: Rule) -> bool:
        pass

    def delete_rule(self, id) -> bool:
        pass

    def append_rule(self, rule: Rule):
        self.rules.append(rule)

    def insert_rule(self, rule_num: int, rule: Rule):
        self.rules.insert(rule_num, rule)

    def delete_rule(self, rule_num: int):
        del self.rules[rule_num]

    def run_on_packet(self, packet) -> Packet:
        pass

    def write_to_file(self, path: str) -> bool:
        pass

    def read_from_file(self, path: str) -> bool:
        pass