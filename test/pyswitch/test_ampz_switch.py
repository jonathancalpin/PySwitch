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
    from lib.pyswitch.colors import dim_color
    from lib.pyswitch.clients.ampz import TYPE_STOMP_LABEL, FAMILY_COLORS
    from lib.pyswitch.clients.ampz.actions import AMPZ_SWITCH


def _label_frame(stomp, colour, name):
    return SystemExclusive(
        manufacturer_id = [0x7D],
        data = [0x41, 0x7A, 0x01, TYPE_STOMP_LABEL, stomp, 0x00, colour] + [ord(c) for c in name]
    )


class TestAmpzSwitch(unittest.TestCase):

    def _build(self, action):
        switch = MockSwitch()
        led_driver = MockNeoPixelDriver()
        appl = Controller(
            led_driver = led_driver,
            midi = MockMidiController(),
            inputs = [
                {
                    "assignment": {
                        "model": switch,
                        "pixels": [0]
                    },
                    "actions": [action]
                },
                MockInputControllerDefinition()
            ]
        )
        appl.init()
        appl.tick()
        return appl, switch, led_driver

    def _press(self, appl, switch):
        switch.shall_be_pushed = True
        appl.tick()
        appl.tick()

    def _release(self, appl, switch):
        switch.shall_be_pushed = False
        appl.tick()
        appl.tick()

    def _stomp_switch(self, label, cc = 83, stomp = 0):
        return AMPZ_SWITCH(cc = cc, display = label, stomp = stomp, color = (255, 255, 255))

    # ---------------------------------------------------------------------------------------

    def test_press_sends_127_and_release_sends_nothing_when_latching(self):
        label = MockDisplayLabel()
        appl, switch, _ = self._build(self._stomp_switch(label, cc = 20, stomp = 0))

        self._press(appl, switch)
        self.assertEqual(len(appl._midi.messages_sent), 1)
        self.assertEqual(appl._midi.messages_sent[0].control, 20)
        self.assertEqual(appl._midi.messages_sent[0].value, 127)

        self._release(appl, switch)
        self.assertEqual(len(appl._midi.messages_sent), 1)

    def test_momentary_release_sends_zero(self):
        action = AMPZ_SWITCH(cc = 21, text = "REC", color = (255, 0, 0), momentary = True)
        appl, switch, _ = self._build(action)

        self._press(appl, switch)
        self._release(appl, switch)
        self.assertEqual([(m.control, m.value) for m in appl._midi.messages_sent], [(21, 127), (21, 0)])

    def test_received_cc_drives_led_and_label_colour(self):
        label = MockDisplayLabel()
        appl, _, _ = self._build(self._stomp_switch(label, cc = 22, stomp = 1))
        appl.client.receive(_label_frame(1, 2, "Dist"))

        appl.client.receive(ControlChange(22, 127))
        self.assertAlmostEqual(appl.inputs[0].brightness, 0.3)
        self.assertEqual(appl.inputs[0].color, FAMILY_COLORS[2])
        self.assertEqual(label.back_color, FAMILY_COLORS[2])

        appl.client.receive(ControlChange(22, 64))
        self.assertAlmostEqual(appl.inputs[0].brightness, 0.1)
        self.assertEqual(label.back_color, dim_color(FAMILY_COLORS[2], 0.5))

        appl.client.receive(ControlChange(22, 0))
        self.assertAlmostEqual(appl.inputs[0].brightness, 0.02)
        self.assertEqual(label.back_color, dim_color(FAMILY_COLORS[2], 0.2))

    def test_label_frame_sets_text_and_family_colour(self):
        label = MockDisplayLabel()
        appl, _, _ = self._build(self._stomp_switch(label, cc = 23, stomp = 2))
        appl.client.receive(_label_frame(2, 2, "Klear"))
        self.assertEqual(label.text, "Klear")
        self.assertEqual(appl.inputs[0].color, FAMILY_COLORS[2])

    def test_empty_stomp_blanks_label_and_led(self):
        label = MockDisplayLabel()
        appl, _, _ = self._build(self._stomp_switch(label, cc = 24, stomp = 3))
        appl.client.receive(ControlChange(24, 127))
        appl.client.receive(_label_frame(3, 2, "Klear"))
        self.assertEqual(label.text, "Klear")

        appl.client.receive(_label_frame(3, 0, ""))
        self.assertEqual(label.text, "")
        self.assertEqual(label.back_color, FAMILY_COLORS[0])
        self.assertAlmostEqual(appl.inputs[0].brightness, 0)

    def test_cc_before_label_uses_default_colour(self):
        label = MockDisplayLabel()
        appl, _, _ = self._build(self._stomp_switch(label, cc = 25, stomp = 4))
        appl.client.receive(ControlChange(25, 127))
        self.assertAlmostEqual(appl.inputs[0].brightness, 0.3)
        self.assertEqual(appl.inputs[0].color, (255, 255, 255))
        self.assertEqual(label.back_color, (255, 255, 255))
        self.assertEqual(label.text, "")

    def test_release_does_not_touch_led(self):
        label = MockDisplayLabel()
        action = AMPZ_SWITCH(cc = 26, display = label, text = "PLAY", color = (0, 255, 0), momentary = True)
        appl, switch, _ = self._build(action)
        appl.client.receive(ControlChange(26, 127))
        self.assertAlmostEqual(appl.inputs[0].brightness, 0.3)

        self._press(appl, switch)
        self._release(appl, switch)
        self.assertAlmostEqual(appl.inputs[0].brightness, 0.3)
        self.assertEqual(label.text, "PLAY")
        self.assertEqual(label.back_color, (0, 255, 0))

    def test_page_change_redraws_from_kept_values(self):
        label = MockDisplayLabel()
        appl, _, _ = self._build(self._stomp_switch(label, cc = 27, stomp = 5))
        appl.client.receive(_label_frame(5, 9, "Dly"))
        appl.client.receive(ControlChange(27, 64))

        # What a page change does per action: reset, then redraw.
        action = appl.inputs[0].actions[0]
        action.reset()
        action.update_displays()
        self.assertEqual(label.text, "Dly")
        self.assertAlmostEqual(appl.inputs[0].brightness, 0.1)
        self.assertEqual(label.back_color, dim_color(FAMILY_COLORS[9], 0.5))

    def test_hold_actions_can_leave_the_leds_alone(self):
        action = AMPZ_SWITCH(cc = 68, text = "TUNER", use_leds = False)
        self.assertFalse(action.uses_switch_leds)
        self.assertTrue(AMPZ_SWITCH(cc = 68, text = "TUNER").uses_switch_leds)

    def test_press_never_changes_display(self):
        label = MockDisplayLabel()
        appl, switch, _ = self._build(self._stomp_switch(label, cc = 28, stomp = 6))
        self.assertAlmostEqual(appl.inputs[0].brightness, 0.02)

        self._press(appl, switch)
        self.assertAlmostEqual(appl.inputs[0].brightness, 0.02)
        self.assertEqual(label.back_color, dim_color((255, 255, 255), 0.2))
