from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Iterable

import scapy  # type: ignore
from scapy.all import rdpcap, wrpcap  # type: ignore
from scapy.layers.inet import IP, TCP, UDP, ICMP  # type: ignore
from scapy.layers.l2 import Ether  # type: ignore
from scapy.packet import Packet as ScapyPacket  # type: ignore


class PacketIndexError(Exception):
    def __init__(self):
        super().__init__("Index out of bounds")


class PacketType(Enum):
    def __str__(self) -> str:
        return str(self.value)

    TCP = "TCP"
    UDP = "UDP"
    # UDP_LITE = "udplite"
    ICMP = "ICMP"
    # ICMPV6 = "icmpv6"
    ESP = "ESP"
    AH = "AH"
    SCTP = "SCTP"
    # MH = "mh"


@dataclass
class Field:
    value: Any
    type_: Callable[[Any], Any]
    explanation: str


LayerConfig = Dict[str, Field]

# TODO dict with explanations and types
# TODO handle options field
FLAGS: Dict[str, LayerConfig] = {
    "Ethernet": {
        "dst": Field(value=None, type_=str, explanation="Example explanation"),
        "src": Field(value=None, type_=str, explanation="Example explanation"),
        "type": Field(value=36864, type_=int, explanation="Example explanation"),
    },
    "IP": {
        "version": Field(value=4, type_=int, explanation="Example explanation"),
        "ihl": Field(value=None, type_=int, explanation="Example explanation"),
        "tos": Field(value=0, type_=int, explanation="Example explanation"),
        "len": Field(value=None, type_=int, explanation="Example explanation"),
        "id": Field(value=1, type_=int, explanation="Example explanation"),
        "flags": Field(value=0, type_=int, explanation="Example explanation"),
        "frag": Field(value=0, type_=int, explanation="Example explanation"),
        "ttl": Field(value=64, type_=int, explanation="Example explanation"),
        "proto": Field(value=0, type_=int, explanation="Example explanation"),
        "chksum": Field(value=None, type_=int, explanation="Example explanation"),
        "src": Field(value=None, type_=str, explanation="Example explanation"),
        "dst": Field(value=None, type_=str, explanation="Example explanation"),
        # TODO "options": Field(value=[], type_=list, explanation="Example explanation"),
    },
    "TCP": {
        "sport": Field(value=20, type_=int, explanation="Example explanation"),
        "dport": Field(value=80, type_=int, explanation="Example explanation"),
        "seq": Field(value=0, type_=int, explanation="Example explanation"),
        "ack": Field(value=0, type_=int, explanation="Example explanation"),
        "dataofs": Field(value=None, type_=int, explanation="Example explanation"),
        "reserved": Field(value=0, type_=int, explanation="Example explanation"),
        "flags": Field(value=2, type_=int, explanation="Example explanation"),
        "window": Field(value=8192, type_=int, explanation="Example explanation"),
        "chksum": Field(value=None, type_=int, explanation="Example explanation"),
        "urgptr": Field(value=0, type_=int, explanation="Example explanation"),
        # TODO "options": Field(value=[], type_=list, explanation="Example explanation"),
    },
    "UDP": {
        "sport": Field(value=53, type_=int, explanation="Example explanation"),
        "dport": Field(value=53, type_=int, explanation="Example explanation"),
        "len": Field(value=None, type_=int, explanation="Example explanation"),
        "chksum": Field(value=None, type_=int, explanation="Example explanation"),
    },
}


# TODO set values
# TODO add ipv6 support
class Packet:
    SCAPY_TYPES: Dict[PacketType, type] = {
        PacketType.TCP: TCP,
        PacketType.UDP: UDP,
        PacketType.ICMP: ICMP,
    }

    def __init__(self, packet: ScapyPacket) -> None:
        self._packet: scapy.packet.Packet = packet

    def write(self, filename: Path) -> Any:
        wrpcap(str(filename), self._packet, append=True)

    def get_type(self) -> Optional[PacketType]:
        if self._packet.haslayer(TCP):
            return PacketType.TCP
        if self._packet.haslayer(UDP):
            return PacketType.UDP
        if self._packet.haslayer(ICMP):
            return PacketType.ICMP
        return None

    def get_fields(self) -> Dict[str, LayerConfig]:
        # TODO add explanation
        d: Dict[str, Dict[str, Field]] = dict()
        payload = self._packet
        while payload:
            ids = [field.name for field in payload.fields_desc]
            ids = list(filter(lambda id: id != "options", ids))
            d[payload.name] = dict()
            for id_ in ids:
                v = (
                    getattr(payload, id_)
                    if id_ != "flags"
                    else getattr(payload, id_).value
                )
                d[payload.name][id_] = Field(
                    value=v,
                    type_=FLAGS[payload.name][id_].type_,
                    explanation=FLAGS[payload.name][id_].explanation,
                )
            payload = payload.payload
        return d


class PacketManager:
    def __init__(self) -> None:
        self._packets: List[Packet] = []

    def add_packet(self, packet: Packet) -> PacketManager:
        self._packets.append(packet)
        return self

    def del_packet(self, id_: int) -> PacketManager:
        if id_ < 0 or id_ >= len(self._packets):
            raise PacketIndexError
        del self._packets[id_]
        return self

    def get(self, id_: int) -> Packet:
        if id_ < 0 or id_ >= len(self._packets):
            raise PacketIndexError
        return self._packets[id_]

    def set(self, id_: int, new_packet: Packet) -> PacketManager:
        if id_ < 0 or id_ >= len(self._packets):
            raise PacketIndexError
        self._packets[id_] = new_packet
        return self

    def clear(self):
        self._packets.clear()

    def read_pcap(self, filename: Path) -> PacketManager:
        assert filename.is_file()
        scapy_packets = rdpcap(str(filename))
        self._packets = list(map(Packet, scapy_packets))
        return self

    def write(self, filename: Path, append: bool) -> None:
        filename.parent.mkdir(parents=True, exist_ok=True)
        if not append:
            filename.unlink(missing_ok=True)
        filename.touch(exist_ok=True)
        for packet in self._packets:
            packet.write(filename)

    def __iter__(self) -> Iterable[Packet]:
        return iter(self._packets)

    def __len__(self):
        return len(self._packets)

    @staticmethod
    def create_packet(
        type_: PacketType,
        ethernet_args: Dict[str, Any],
        internet_layer_args: Dict[str, Any],
        transmission_layer_args: Dict[str, Any],
    ) -> Optional[Packet]:
        if type_ not in Packet.SCAPY_TYPES:
            return None

        return Packet(
            Ether(**ethernet_args)
            / IP(**internet_layer_args)
            / Packet.SCAPY_TYPES[type_](**transmission_layer_args)
        )
