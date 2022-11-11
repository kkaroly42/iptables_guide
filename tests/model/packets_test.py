import unittest

import IPTables_Guide.model.packets as packets

class TCP(unittest.TestCase):
    def test_1(self):
        pk = packets.create_packet(packets.PacketType.TCP, {"ttl": 128}, {"ack": 1})
        self.assertIsNotNone(pk)
        self.assertEqual(pk.get_type(), packets.PacketType.TCP)
        fields = pk.get_fields()
        self.assertEqual(fields["IP"]["ttl"], 128)
        self.assertEqual(fields["TCP"]["ack"], 1)

class UDP(unittest.TestCase):
    def test_1(self):
        port = 60
        pk = packets.create_packet(packets.PacketType.UDP, {"flags": 1}, {"sport": port, "dport": port})
        self.assertIsNotNone(pk)
        self.assertEqual(pk.get_type(), packets.PacketType.UDP)
        fields = pk.get_fields()
        self.assertEqual(fields["IP"]["flags"], 1)
        self.assertEqual(fields["UDP"]["sport"], port)
        self.assertEqual(fields["UDP"]["dport"], port)

class ICMP(unittest.TestCase):
    def test_1(self):
        pk = packets.create_packet(packets.PacketType.ICMP, {"flags": 1, "ttl": 128}, {"type": 0})
        self.assertIsNotNone(pk)
        self.assertEqual(pk.get_type(), packets.PacketType.ICMP)
        fields = pk.get_fields()
        self.assertEqual(fields["IP"]["flags"], 1)
        self.assertEqual(fields["IP"]["ttl"], 128)
        self.assertEqual(fields["ICMP"]["type"], 0)

if __name__ == "__main__":
    unittest.main()