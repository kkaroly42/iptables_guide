from .packets import Packet, PacketType, PacketManager

from typing import Dict, Optional

DUMMY_TCP_PACKET: Optional[Packet] = PacketManager.create_packet(PacketType.TCP, {}, {}, {})
DUMMY_UDP_PACKET: Optional[Packet] = PacketManager.create_packet(PacketType.UDP, {}, {}, {})

assert DUMMY_TCP_PACKET
assert DUMMY_UDP_PACKET

DUMMY_PACKETS: Dict[PacketType, Packet] = {
    PacketType.TCP: DUMMY_TCP_PACKET,
    PacketType.UDP: DUMMY_UDP_PACKET,
}
