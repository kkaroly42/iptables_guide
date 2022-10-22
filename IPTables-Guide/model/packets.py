import scapy  # type: ignore

from scapy.all import rdpcap, wrpcap  # type: ignore
from scapy.layers.inet import IP, TCP, UDP, ICMP  # type: ignore
from enum import Enum


from typing import List, Dict, Any, Optional


class PacketType(Enum):
    TCP = 1
    UDP = 2
    ICMP = 3


# TODO set values
class Packet:
    def __init__(self, packet: scapy.packet.Packet):
        self._packet: scapy.packet.Packet = packet

    def write(self, filename: str, append: bool = True) -> Any:
        wrpcap(filename, self._packet, append)

    def get_type(self) -> Optional[PacketType]:
        if self._packet.haslayer(TCP):
            return PacketType.TCP
        if self._packet.haslayer(UDP):
            return PacketType.UDP
        if self._packet.haslayer(ICMP):
            return PacketType.ICMP
        return None

    def get_fields(self) -> Dict[str, Dict[str, Any]]:
        # TODO add explanation
        d = dict()
        for layer in self._packet:
            ids = [field.name for field in layer.fields_desc]
            d[layer.name] = {id: getattr(layer, id) for id in ids}
        return d


def read_pcap(filename: str) -> List[scapy.packet.Packet]:
    packets = rdpcap(filename)
    return list(map(Packet, packets))


def create_packet(
    type: PacketType, layer1_args: Dict[str, Any], layer2_args: Dict[str, Any]
) -> Optional[scapy.packet.Packet]:
    if type == PacketType.TCP:
        return Packet(IP(**layer1_args) / TCP(**layer2_args))
    if type == PacketType.UDP:
        return Packet(IP(**layer1_args) / UDP(**layer2_args))
    if type == PacketType.ICMP:
        return Packet(IP(**layer1_args) / ICMP(**layer2_args))
    return None
