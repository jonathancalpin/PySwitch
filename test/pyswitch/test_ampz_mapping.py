import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

# Import subject under test
with patch.dict(sys.modules, {
    "micropython": MockMicropython,
    "displayio": MockDisplayIO(),
    "adafruit_display_text": MockAdafruitDisplayText(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "adafruit_midi.program_change": MockAdafruitMIDIProgramChange(),
    "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
    "gc": MockGC()
}):
    from adafruit_midi.system_exclusive import SystemExclusive
    from adafruit_midi.control_change import ControlChange

    from lib.pyswitch.clients.ampz import *


class TestAmpzMapping(unittest.TestCase):

    def test_stomp_label_parses_colour_and_name(self):
        m = AmpzSysexMapping("s3", TYPE_STOMP_LABEL, 3)
        msg = SystemExclusive(manufacturer_id = [0x7D], data = [0x41, 0x7A, 0x01, 0x01, 0x03, 0x00, 0x02, 0x4B, 0x6C, 0x65, 0x61, 0x72])
        self.assertTrue(m.parse(msg))
        self.assertEqual(m.value, (2, "Klear"))

    def test_other_index_or_type_is_ignored(self):
        m = AmpzSysexMapping("s3", TYPE_STOMP_LABEL, 3)
        self.assertFalse(m.parse(SystemExclusive(manufacturer_id = [0x7D], data = [0x41, 0x7A, 0x01, 0x01, 0x04, 0x00, 0x02, 0x41])))
        self.assertFalse(m.parse(SystemExclusive(manufacturer_id = [0x7D], data = [0x41, 0x7A, 0x01, 0x03, 0x00, 0x00, 0x41])))
        self.assertFalse(m.parse(SystemExclusive(manufacturer_id = [0x00, 0x20, 0x33], data = [0x01, 0x02])))
        self.assertFalse(m.parse(ControlChange(83, 127)))

    def test_three_byte_manufacturer_split_parses_the_same(self):
        m = AmpzSysexMapping("s0", TYPE_STOMP_LABEL, 0)
        msg = SystemExclusive(manufacturer_id = [0x7D, 0x41, 0x7A], data = [0x01, 0x01, 0x00, 0x00, 0x09, 0x44, 0x6C, 0x79])
        self.assertTrue(m.parse(msg))
        self.assertEqual(m.value, (9, "Dly"))

    def test_trailing_terminator_is_stripped(self):
        m = AmpzSysexMapping("p", TYPE_PRESET_NAME, 0)
        self.assertTrue(m.parse(SystemExclusive(manufacturer_id = [0x7D], data = [0x41, 0x7A, 0x01, 0x03, 0x00, 0x00, 0x47, 0x69, 0x67, 0xF7])))
        self.assertEqual(m.value, "Gig")
        self.assertTrue(m.parse(SystemExclusive(manufacturer_id = [0x7D], data = [0x41, 0x7A, 0x01, 0x03, 0x00, 0x00, 0x47, 0x69, 0x67, 0x00])))
        self.assertEqual(m.value, "Gig")

    def test_empty_stomp_label(self):
        m = AmpzSysexMapping("s1", TYPE_STOMP_LABEL, 1)
        self.assertTrue(m.parse(SystemExclusive(manufacturer_id = [0x7D], data = [0x41, 0x7A, 0x01, 0x01, 0x01, 0x00, 0x00])))
        self.assertEqual(m.value, (0, ""))

    def test_hello_reply_parses_to_one(self):
        m = AmpzSysexMapping("h", TYPE_HELLO_REPLY, 0)
        self.assertTrue(m.parse(SystemExclusive(manufacturer_id = [0x7D], data = [0x41, 0x7A, 0x01, 0x7E, 0x00, 0x00, 0x00, 0x01])))
        self.assertEqual(m.value, 1)

    def test_family_colors_cover_zero_to_eleven(self):
        self.assertEqual(sorted(FAMILY_COLORS.keys()), list(range(12)))

    def test_frame_builder_matches_the_contract(self):
        f = ampz_frame(TYPE_HELLO_REQUEST, 0, [0x00, 0x00])
        self.assertEqual(list(f.manufacturer_id), [0x7D])
        self.assertEqual(list(f.data), [0x41, 0x7A, 0x01, 0x7F, 0x00, 0x00, 0x00, 0x00])
