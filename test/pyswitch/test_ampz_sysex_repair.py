import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

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
    from lib.pyswitch.clients.ampz.sysex_repair import SysExRepairInput


class _Port:
    def __init__(self, chunks):
        self.chunks = [bytes(c) for c in chunks]
        self.in_waiting = 0

    def read(self, nbytes = None):
        return self.chunks.pop(0) if self.chunks else None


def _drain(chunks):
    port = _Port(chunks)
    r = SysExRepairInput(port)
    out = bytearray()
    for _ in range(len(chunks)):
        got = r.read(100)
        if got:
            out += got
    return bytes(out)


FRAME_3 = bytes([0xF0, 0x7D, 0x41, 0x7A, 0x01, 0x01, 0x03, 0x00, 0x00, 0xF7])


# What the Bluetooth DIN adapter does to two frames out of three: F0 eaten, timestamp leaked after F7.
class TestSysExRepairInput(unittest.TestCase):

    def test_intact_traffic_passes_unchanged(self):
        clean = bytes([0xB0, 0x53, 0x7F, 0xC0, 0x02]) + FRAME_3 + bytes([0xB0, 0x52, 0x00])
        self.assertEqual(_drain([clean]), clean)

    def test_frame_without_f0_is_reframed_and_leaked_byte_dropped(self):
        broken = FRAME_3[1:] + bytes([0x94])
        self.assertEqual(_drain([broken]), FRAME_3)

    def test_two_broken_frames_then_an_intact_one(self):
        f0 = bytes([0xF0, 0x7D, 0x41, 0x7A, 0x01, 0x01, 0x00, 0x00, 0x00, 0xF7])
        f1 = bytes([0xF0, 0x7D, 0x41, 0x7A, 0x01, 0x01, 0x01, 0x00, 0x00, 0xF7])
        f2 = bytes([0xF0, 0x7D, 0x41, 0x7A, 0x01, 0x01, 0x02, 0x00, 0x02, 0x4B, 0x6C, 0xF7])
        wire = f0[1:] + bytes([0x94]) + f1[1:] + bytes([0x99]) + f2
        self.assertEqual(_drain([wire]), f0 + f1 + f2)

    def test_leaked_byte_that_looks_like_a_cc_status_before_a_frame_is_dropped(self):
        wire = bytes([0xB4]) + FRAME_3[1:]
        self.assertEqual(_drain([wire]), FRAME_3)

    def test_timestamp_inside_a_frame_is_dropped(self):
        wire = FRAME_3[:-1] + bytes([0x9A]) + FRAME_3[-1:]
        self.assertEqual(_drain([wire]), FRAME_3)

    def test_prefix_split_across_reads(self):
        wire = FRAME_3[1:]
        self.assertEqual(_drain([wire[:2], wire[2:5], wire[5:]]), FRAME_3)

    def test_cc_split_across_reads(self):
        self.assertEqual(_drain([bytes([0xB0]), bytes([0x53, 0x7F])]), bytes([0xB0, 0x53, 0x7F]))

    def test_stray_end_and_realtime_bytes_are_dropped(self):
        wire = bytes([0xF7, 0xF8, 0xFE]) + bytes([0xB0, 0x53, 0x00]) + bytes([0xF7])
        self.assertEqual(_drain([wire]), bytes([0xB0, 0x53, 0x00]))

    def test_second_frame_start_inside_an_unterminated_frame_closes_it(self):
        lost_end = FRAME_3[:-1]            # F7 never arrived
        self.assertEqual(_drain([lost_end + FRAME_3]), FRAME_3 + FRAME_3)

    def test_prefix_arriving_inside_an_unterminated_frame_without_f0(self):
        wire = FRAME_3[:-1] + FRAME_3[1:]   # previous F7 lost AND next F0 eaten
        self.assertEqual(_drain([wire]), FRAME_3 + FRAME_3)

    def test_empty_read_returns_none(self):
        r = SysExRepairInput(_Port([]))
        self.assertIsNone(r.read(10))
