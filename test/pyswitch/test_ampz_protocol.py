import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

# Import subject under test
with patch.dict(sys.modules, {
    "micropython": MockMicropython,
    "displayio": MockDisplayIO(),
    "adafruit_display_text": MockAdafruitDisplayText(),
    "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
    "usb_midi": MockUsbMidi(),
    "adafruit_midi": MockAdafruitMIDI(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.program_change": MockAdafruitMIDIProgramChange(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "gc": MockGC()
}):
    from .mocks_appl import *
    from .mocks_ui import *

    from adafruit_midi.system_exclusive import SystemExclusive
    from adafruit_midi.control_change import ControlChange

    from lib.pyswitch.controller.controller import Controller
    from lib.pyswitch.clients.ampz import TYPE_PRESET_NAME, TYPE_HELLO_REPLY, TYPE_HELLO_REQUEST, LINK
    from lib.pyswitch.clients.ampz.protocol import AmpzProtocol
    from lib.pyswitch.clients.ampz.actions import AmpzPresetNameCallback


def _frame(type, index, payload):
    return SystemExclusive(manufacturer_id = [0x7D], data = [0x41, 0x7A, 0x01, type, index, 0x00] + payload)


class TestAmpzProtocol(unittest.TestCase):

    def _protocol(self):
        period = MockPeriodCounter()
        midi = MockMidiController()
        p = AmpzProtocol(period_counter = period)
        p.init(midi, MockClient())
        return p, period, midi

    def test_default_retry_is_three_seconds(self):
        p = AmpzProtocol()
        self.assertEqual(p.retry_period.interval, 3000)

    def test_hello_repeats_every_3s_until_reply(self):
        p, period, midi = self._protocol()

        period.exceed_next_time = True
        p.update()
        self.assertEqual(len(midi.messages_sent), 1)
        self.assertEqual(list(midi.messages_sent[0].data), [0x41, 0x7A, 0x01, TYPE_HELLO_REQUEST, 0x00, 0x02, 0x00, 0x00])

        p.update()                                     # period not exceeded: quiet
        self.assertEqual(len(midi.messages_sent), 1)

        period.exceed_next_time = True
        p.update()                                     # still no reply: ask again
        self.assertEqual(len(midi.messages_sent), 2)

        self.assertTrue(p.receive(_frame(TYPE_HELLO_REPLY, 0, [0x00, 0x01])))
        period.exceed_next_time = True
        p.update()                                     # alive: no more requests
        self.assertEqual(len(midi.messages_sent), 2)

    def test_reply_sets_alive_and_is_consumed(self):
        p, _, _ = self._protocol()
        self.assertEqual(p.get_color(), (255, 0, 0))
        self.assertTrue(p.receive(_frame(TYPE_HELLO_REPLY, 0, [0x00, 0x01])))
        self.assertTrue(p.alive)
        self.assertEqual(p.get_color(), (0, 255, 0))

    def test_unrelated_messages_are_not_consumed(self):
        p, _, _ = self._protocol()
        self.assertFalse(p.receive(SystemExclusive(manufacturer_id = [0x00, 0x20, 0x33], data = [0x01, 0x02])))
        self.assertFalse(p.receive(ControlChange(83, 127)))
        self.assertFalse(p.receive(None))
        self.assertFalse(p.alive)

    def test_never_bidirectional_never_feedback(self):
        p, _, _ = self._protocol()
        self.assertFalse(p.is_bidirectional(object()))
        self.assertFalse(p.feedback_value(object()))


class TestAmpzPresetName(unittest.TestCase):

    def test_label_shows_received_name_or_default(self):
        appl = Controller(
            led_driver = MockNeoPixelDriver(),
            midi = MockMidiController(),
            inputs = [MockInputControllerDefinition()]
        )
        cb = AmpzPresetNameCallback()
        cb.init(appl)
        label = MockDisplayLabel()

        cb.update_label(label)
        self.assertEqual(label.text, "Ampz")

        appl.client.receive(_frame(TYPE_PRESET_NAME, 0, [ord(c) for c in "Gig Lead"]))
        cb.update_label(label)
        self.assertEqual(label.text, "Gig Lead")

    def test_link_errors_trigger_one_rerequest_once_the_link_is_quiet(self):
        clock = [10000]
        period = MockPeriodCounter()
        midi = MockMidiController()
        p = AmpzProtocol(period_counter = period, now = lambda: clock[0])
        p.init(midi, MockClient())
        p.receive(_frame(TYPE_HELLO_REPLY, 0, [0x00, 0x01]))
        p.update()
        self.assertEqual(len(midi.messages_sent), 0)
        LINK.lost()
        p.update()                      # error just happened: wait for the burst to end
        self.assertEqual(len(midi.messages_sent), 0)
        clock[0] += 300
        LINK.lost()                     # still arriving
        p.update()
        self.assertEqual(len(midi.messages_sent), 0)
        clock[0] += 400                 # quiet for 400 ms
        p.update()
        self.assertEqual(len(midi.messages_sent), 1)
        self.assertEqual(list(midi.messages_sent[0].data), [0x41, 0x7A, 0x01, TYPE_HELLO_REQUEST, 0x00, 0x02, 0x00, 0x00])
        p.update()                      # nothing new: no second request
        self.assertEqual(len(midi.messages_sent), 1)
        LINK.lost()                     # the re-sent dump itself was damaged
        clock[0] += 500                 # quiet, but inside the one-second floor
        p.update()
        self.assertEqual(len(midi.messages_sent), 1)
        clock[0] += 600
        p.update()
        self.assertEqual(len(midi.messages_sent), 2)

    def test_rerequest_repeats_until_the_reply_arrives(self):
        clock = [50000]
        period = MockPeriodCounter()
        midi = MockMidiController()
        p = AmpzProtocol(period_counter = period, now = lambda: clock[0])
        p.init(midi, MockClient())
        p.receive(_frame(TYPE_HELLO_REPLY, 0, [0x00, 0x01]))
        LINK.lost()
        p.update()
        clock[0] += 500
        p.update()
        self.assertEqual(len(midi.messages_sent), 1)      # first request
        clock[0] += 1100
        p.update()
        self.assertEqual(len(midi.messages_sent), 2)      # no reply: ask again
        clock[0] += 1100
        p.update()
        self.assertEqual(len(midi.messages_sent), 3)
        p.receive(_frame(TYPE_HELLO_REPLY, 0, [0x00, 0x01]))   # Ampz answered
        clock[0] += 5000
        p.update()
        self.assertEqual(len(midi.messages_sent), 3)      # satisfied

    def test_rerequest_gives_up_after_five_tries(self):
        clock = [90000]
        period = MockPeriodCounter()
        midi = MockMidiController()
        p = AmpzProtocol(period_counter = period, now = lambda: clock[0])
        p.init(midi, MockClient())
        p.receive(_frame(TYPE_HELLO_REPLY, 0, [0x00, 0x01]))
        LINK.lost()
        for _ in range(12):
            clock[0] += 1100
            p.update()
        self.assertEqual(len(midi.messages_sent), 5)
