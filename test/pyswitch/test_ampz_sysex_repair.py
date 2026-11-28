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
    from lib.pyswitch.clients.ampz import LINK


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


# What the adapter does to CCs (raw UART capture, 2026-11-27): running status, and timestamp
# bytes dropped between a CC's number and its value.
class TestRunningStatusRepair(unittest.TestCase):

    def test_running_status_ccs_get_their_status_back(self):
        before = LINK.errors
        wire = bytes([0xB0, 0x53, 0x00, 0x52, 0x00, 0x5A, 0x00])
        self.assertEqual(_drain([wire]), bytes([0xB0, 0x53, 0x00, 0xB0, 0x52, 0x00, 0xB0, 0x5A, 0x00]))
        self.assertEqual(LINK.errors, before)

    def test_running_status_program_changes(self):
        self.assertEqual(_drain([bytes([0xC0, 0x0E, 0x0F])]), bytes([0xC0, 0x0E, 0xC0, 0x0F]))

    def test_leaked_byte_between_cc_number_and_value_is_ignored(self):
        self.assertEqual(_drain([bytes([0xB0, 0x52, 0xAB, 0x00])]), bytes([0xB0, 0x52, 0x00]))

    def test_leaked_byte_in_status_range_inside_a_cc_is_ignored(self):
        wire = bytes([0xB0, 0x52, 0xB0, 0x00, 0x5A, 0x00])
        self.assertEqual(_drain([wire]), bytes([0xB0, 0x52, 0x00, 0xB0, 0x5A, 0x00]))

    def test_leaks_between_running_status_ccs_keep_the_running_status(self):
        wire = bytes([0xB0, 0x53, 0x00, 0xAB, 0x52, 0x00, 0xF7, 0x5A, 0x00])
        self.assertEqual(_drain([wire]), bytes([0xB0, 0x53, 0x00, 0xB0, 0x52, 0x00, 0xB0, 0x5A, 0x00]))

    def test_frame_without_f0_after_running_status_ccs(self):
        wire = bytes([0xB0, 0x53, 0x00, 0x52, 0x00]) + FRAME_3[1:]
        self.assertEqual(_drain([wire]), bytes([0xB0, 0x53, 0x00, 0xB0, 0x52, 0x00]) + FRAME_3)

    def test_sysex_cancels_running_status_so_data_after_it_is_an_error_not_a_cc(self):
        before = LINK.errors
        wire = bytes([0xB0, 0x53, 0x00]) + FRAME_3 + bytes([0x52, 0x00])
        self.assertEqual(_drain([wire]), bytes([0xB0, 0x53, 0x00]) + FRAME_3)
        self.assertGreater(LINK.errors, before)

    def test_running_status_split_across_reads(self):
        self.assertEqual(_drain([bytes([0xB0, 0x53, 0x00, 0x52]), bytes([0x00])]),
                         bytes([0xB0, 0x53, 0x00, 0xB0, 0x52, 0x00]))

    def test_the_captured_burst_decodes_to_every_cc(self):
        wire = bytes.fromhex("ee b0 53 00 f2 b0 52 b0 00 5a 00 54 00 59 b0 00 57 00 50 00 51 b0 00 5b 00 56 00 3c b0 00 3d 00 3e 00 3f b0 00 64 00 c0 0f")
        out = _drain([wire])
        ccs = [out[i + 1] for i in range(0, len(out) - 2) if out[i] == 0xB0 and out[i + 2] == 0x00]
        self.assertEqual(ccs, [0x53, 0x52, 0x5A, 0x54, 0x59, 0x57, 0x50, 0x51, 0x5B, 0x56, 0x3C, 0x3D, 0x3E, 0x3F, 0x64])
        self.assertEqual(out[-2:], bytes([0xC0, 0x0F]))


# adafruit_midi discards a SysEx that is not complete within one read, and a 31250-baud link
# delivers most frames in several reads. The filter hands over whole messages only.
class TestWholeMessagesOnly(unittest.TestCase):

    def test_partial_frame_is_held_until_its_end_arrives(self):
        port = _Port([FRAME_3[:5], FRAME_3[5:8], FRAME_3[8:]])
        r = SysExRepairInput(port)
        self.assertIsNone(r.read(100))
        self.assertIsNone(r.read(100))
        self.assertEqual(r.read(100), FRAME_3)

    def test_complete_messages_before_a_partial_frame_are_released_at_once(self):
        cc = bytes([0xB0, 0x53, 0x00])
        port = _Port([cc + FRAME_3[:6], FRAME_3[6:]])
        r = SysExRepairInput(port)
        self.assertEqual(r.read(100), cc)
        self.assertEqual(r.read(100), FRAME_3)

    def test_partial_cc_is_held(self):
        port = _Port([bytes([0xB0, 0x53]), bytes([0x7F])])
        r = SysExRepairInput(port)
        self.assertIsNone(r.read(100))
        self.assertEqual(r.read(100), bytes([0xB0, 0x53, 0x7F]))

    def test_frame_split_at_every_byte(self):
        wire = bytes([0xB0, 0x53, 0x00]) + FRAME_3 + FRAME_3[1:] + bytes([0x9A]) + bytes([0xC0, 0x05])
        want = bytes([0xB0, 0x53, 0x00]) + FRAME_3 + FRAME_3 + bytes([0xC0, 0x05])
        self.assertEqual(_drain([bytes([b]) for b in wire]), want)
