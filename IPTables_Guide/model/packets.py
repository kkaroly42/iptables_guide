import scapy  # type: ignore

from scapy.all import rdpcap, wrpcap  # type: ignore
from scapy.layers.inet import IP, TCP, UDP, ICMP  # type: ignore

from enum import Enum


from typing import List, Dict, Any, Optional


class PacketType(Enum):
    TCP = "tcp"
    UDP = "udp"
    # UDP_LITE = "udplite"
    ICMP = "icmp"
    # ICMPV6 = "icmpv6"
    ESP = "esp"
    AH = "ah"
    SCTP = "sctp"
    # MH = "mh"


# TODO set values
# TODO add ipv6 support
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
        payload = self._packet
        while payload:
            ids = [field.name for field in payload.fields_desc]
            d[payload.name] = {id: getattr(payload, id) for id in ids}
            payload = payload.payload
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
