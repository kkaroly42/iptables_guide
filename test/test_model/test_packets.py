import unittest

from IPTables_Guide.model.packets import PacketManager, PacketType


def test_tcp():
    pm = PacketManager()
    pk = PacketManager.create_packet(PacketType.TCP, {}, {"ttl": 128}, {"ack": 1})
    pm.add_packet(pk)
    assert pk is not None
    assert pk.get_type() == PacketType.TCP
    assert pk.get_type() == pm.get(0).get_type()
    fields = pk.get_fields()
    assert fields["IP"]["ttl"].value == 128
    assert fields["TCP"]["ack"].value == 1


def test_udp():
    pm = PacketManager()
    port = 60
    dport = 61
    pk = PacketManager.create_packet(PacketType.UDP, {}, {"flags": 1}, {"sport": port, "dport": dport})
    pm.add_packet(pk)
    assert pk is not None
    assert pk.get_type() == PacketType.UDP
    assert pk.get_type() == pm.get(0).get_type()
    fields = pk.get_fields()
    assert fields["IP"]["flags"].value == 1
    assert fields["UDP"]["sport"].value == port
    assert fields["UDP"]["dport"].value == dport

# the model currently does not suppoer icmp
# def test_icmp():
#     pm = PacketManager()
#     pk = PacketManager.create_packet(PacketType.ICMP, {}, {"flags": 1, "ttl": 128}, {"type": 0})
#     pm.add_packet(pk)
#     assert pk is not None
#     assert pk.get_type() == PacketType.ICMP
#     assert pk.get_type() == pm.get(0).get_type()
#     fields = pk.get_fields()
#     assert fields["IP"]["flags"].value == 1
#     assert fields["IP"]["ttl"].value == 128
#     assert fields["ICMP"]["type"].value == 0


if __name__ == "__main__":
    unittest.main()
