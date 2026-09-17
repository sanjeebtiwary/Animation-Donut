import unittest

from Animation.donut_animation import build_control_packet


class DonutControlPacketTests(unittest.TestCase):
    def test_build_control_packet_defaults(self):
        packet = build_control_packet()
        self.assertEqual(packet["mode"], "auto")
        self.assertEqual(packet["rotate_x"], 0.0)
        self.assertEqual(packet["rotate_y"], 0.0)
        self.assertEqual(packet["rotate_z"], 0.0)
        self.assertEqual(packet["zoom"], 1.0)

    def test_build_control_packet_updates_values(self):
        packet = build_control_packet(mode="manual", rotate_x=12.5, rotate_y=-4.25, rotate_z=3.0, zoom=1.4)
        self.assertEqual(packet["mode"], "manual")
        self.assertEqual(packet["rotate_x"], 12.5)
        self.assertEqual(packet["rotate_y"], -4.25)
        self.assertEqual(packet["rotate_z"], 3.0)
        self.assertEqual(packet["zoom"], 1.4)


if __name__ == "__main__":
    unittest.main()
