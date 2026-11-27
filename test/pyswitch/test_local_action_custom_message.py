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
    from lib.pyswitch.clients.local.actions.custom import *
    from lib.pyswitch.controller.client import Client
    from lib.pyswitch.ui.elements import DisplayLabel
    
    from .mocks_appl import *
    from .mocks_callback import MockEnabledCallback

######################################################


class TestLocalCustomMessage(unittest.TestCase):

    def test(self):
        display = DisplayLabel(layout = {
            "font": "foo",
            "backColor": (0, 0, 0)
        })

        action = CUSTOM_MESSAGE(
            message = [1, 3, 5],
            message_release = [23, 5],
            color = (8, 9, 2),
            led_brightness = 0.5,
            text = "foo2",
            display = display
        )

        switch = MockFootswitch(
            actions = [
                action,
            ]
        )
        
        appl = MockController(
            inputs = [
                switch
            ]
        )
        
        action.init(appl, switch)
        action.update_displays()

        self.assertEqual(switch.color, (8, 9, 2))
        self.assertEqual(switch.brightness, 0.5)

        self.assertEqual(display.text, "foo2")
        self.assertEqual(display.back_color, (8, 9, 2))

        # Trigger
        action.push()

        self.assertEqual(len(appl.client.midi.messages_sent), 1)
        self.assertEqual(list(appl.client.midi.messages_sent[0].__bytes__()), [1, 3, 5])

        action.release()

        self.assertEqual(len(appl.client.midi.messages_sent), 2)
        self.assertEqual(list(appl.client.midi.messages_sent[1].__bytes__()), [23, 5])

    def test_minimal(self):
        action = CUSTOM_MESSAGE(
            message = [1, 3, 5]
        )

        switch = MockFootswitch(
            actions = [
                action,
            ]
        )
        
        appl = MockController(
            inputs = [
                switch
            ]
        )
        
        action.init(appl, switch)
        action.update_displays()

        self.assertEqual(switch.color, (255, 255, 255))
        self.assertEqual(switch.brightness, 0.15)

        # Trigger
        action.push()

        self.assertEqual(len(appl.client.midi.messages_sent), 1)
        self.assertEqual(list(appl.client.midi.messages_sent[0].__bytes__()), [1, 3, 5])

        action.release()

        self.assertEqual(len(appl.client.midi.messages_sent), 1)


######################################################


class TestLocalCustomMessageListen(unittest.TestCase):

    # Builds a listening stomp toggle (CC 83, ch 1) and returns (action, switch, appl, label, mapping)
    def _setup(self, cc = 83, enable_callback = None, listen = True, toggle = True):
        label = DisplayLabel(layout = {
            "font": "foo",
            "backColor": (0, 0, 0)
        })

        action = CUSTOM_MESSAGE(
            message = [0xB0, cc, 127],
            message_release = [0xB0, cc, 0],
            color = (255, 70, 0),
            led_brightness = 0.3,
            led_brightness_off = 0.02,
            text = "DIST",
            display = label,
            toggle = toggle,
            listen = listen,
            enable_callback = enable_callback
        )

        switch = MockFootswitch(actions = [action])
        appl = MockController(inputs = [switch])

        action.init(appl, switch)
        action.update_displays()

        mapping = appl.client.register_calls[0]["mapping"] if appl.client.register_calls else None
        return action, switch, appl, label, mapping

    def _receive(self, appl, mapping, value):
        # Same path as the real client: parse the incoming CC, then notify the registered listener
        msg = MockAdafruitMIDIControlChange.ControlChange(mapping.response.control, value)
        self.assertTrue(mapping.parse(msg))
        for call in appl.client.register_calls:
            if call["mapping"] == mapping:
                call["listener"].parameter_changed(mapping)

    def test_registers_listener_for_its_cc(self):
        action, switch, appl, label, mapping = self._setup()

        self.assertEqual(len(appl.client.register_calls), 1)
        self.assertEqual(mapping.response.control, 83)
        self.assertIsNone(mapping.request)

    def test_incoming_value_sets_state(self):
        action, switch, appl, label, mapping = self._setup()
        self.assertEqual(switch.brightness, 0.02)

        self._receive(appl, mapping, 127)
        self.assertEqual(switch.brightness, 0.3)
        self.assertEqual(label.back_color, (255, 70, 0))

        self._receive(appl, mapping, 0)
        self.assertEqual(switch.brightness, 0.02)

        # Threshold: 64 and up is on
        self._receive(appl, mapping, 64)
        self.assertEqual(switch.brightness, 0.3)
        self._receive(appl, mapping, 63)
        self.assertEqual(switch.brightness, 0.02)

    def test_repeated_value_is_applied_after_local_press(self):
        action, switch, appl, label, mapping = self._setup()

        self._receive(appl, mapping, 0)

        # Pressing the switch turns it on locally and sends 127
        action.push()
        self.assertEqual(list(appl.client.midi.messages_sent[-1].__bytes__()), [0xB0, 83, 127])
        self.assertEqual(switch.brightness, 0.3)

        # The next preset has the effect off: the same 0 as last time must still turn it off
        self._receive(appl, mapping, 0)
        self.assertEqual(switch.brightness, 0.02)

        # And the next press sends "on" again, not a stale "off"
        action.push()
        self.assertEqual(list(appl.client.midi.messages_sent[-1].__bytes__()), [0xB0, 83, 127])

    def test_receiving_does_not_send(self):
        action, switch, appl, label, mapping = self._setup()

        self._receive(appl, mapping, 127)
        self._receive(appl, mapping, 0)

        self.assertEqual(len(appl.client.midi.messages_sent), 0)

    def test_hidden_page_keeps_state_without_touching_leds(self):
        ecb = MockEnabledCallback(output = False)
        action, switch, appl, label, mapping = self._setup(enable_callback = ecb)
        switch.brightness = 0.5   # Something else owns the LEDs while this page is hidden

        self._receive(appl, mapping, 127)
        self.assertEqual(switch.brightness, 0.5)

        # Page becomes visible: Action.update() resets the callback, then redraws
        ecb.output = True
        action.update()
        self.assertEqual(switch.brightness, 0.3)

    def test_non_listening_toggle_still_resets(self):
        action, switch, appl, label, mapping = self._setup(listen = False)

        self.assertEqual(len(appl.client.register_calls), 0)

        action.push()
        self.assertEqual(switch.brightness, 0.3)

        action.callback.reset()
        action.update_displays()
        self.assertEqual(switch.brightness, 0.02)

    def test_listen_ignored_without_toggle(self):
        action, switch, appl, label, mapping = self._setup(toggle = False)

        self.assertEqual(len(appl.client.register_calls), 0)

    def test_listen_ignored_for_non_cc_message(self):
        action = CUSTOM_MESSAGE(
            message = [0xC0, 5],
            toggle = True,
            listen = True
        )
        switch = MockFootswitch(actions = [action])
        appl = MockController(inputs = [switch])
        action.init(appl, switch)

        self.assertEqual(len(appl.client.register_calls), 0)

    def test_other_cc_does_not_match(self):
        action, switch, appl, label, mapping = self._setup(cc = 82)

        msg = MockAdafruitMIDIControlChange.ControlChange(83, 127)
        self.assertFalse(mapping.parse(msg))

    def test_real_client_end_to_end(self):
        # Uses the real Client: incoming CCs go through Client.receive() like on the pedal
        action = CUSTOM_MESSAGE(
            message = [0xB0, 84, 127],
            message_release = [0xB0, 84, 0],
            led_brightness = 0.3,
            led_brightness_off = 0.02,
            toggle = True,
            listen = True
        )
        switch = MockFootswitch(actions = [action])
        client = Client(midi = MockMidiController(), config = {})
        appl = MockController(inputs = [switch], client = client)
        action.init(appl, switch)
        action.update_displays()

        CC = MockAdafruitMIDIControlChange.ControlChange

        self.assertTrue(client.receive(CC(84, 127)))
        self.assertEqual(switch.brightness, 0.3)

        self.assertFalse(client.receive(CC(85, 0)))     # Another CC: not ours
        self.assertEqual(switch.brightness, 0.3)

        for _ in range(50):                             # The listener must stay registered
            client.receive(CC(84, 0))
        self.assertEqual(switch.brightness, 0.02)

        self.assertTrue(client.receive(CC(84, 100)))
        self.assertEqual(switch.brightness, 0.3)

