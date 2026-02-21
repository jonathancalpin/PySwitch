from ....controller.callbacks import Callback
from ....controller.actions import Action
from ....colors import Colors, dim_color
from adafruit_midi.midi_message import MIDIMessage

# Sends a single raw, arbitrary MIDI message.
#
# If toggle is True: each press toggles between sending message (on) and message_release (off).
# Release does nothing. Use for CC latch/toggle (e.g. effect on/off).
#
# If group is set (string): radio-button behavior. When pressed, this action becomes active
# and all other actions in the same group become inactive. Use for PC preset selection.
#
# The messages have to be raw bytes, so don't forget to also add the status and (in case of SysEx) closing bytes!
def CUSTOM_MESSAGE(message,                 # Raw MIDI message bytes (as list, for example [176, 80, 127] for CC on). You can use hex values in format 0xab, too.
                   message_release = None,  # Raw MIDI message to be sent on release (momentary) or when toggling off (toggle mode). Default: None
                   text = "",
                   color = Colors.WHITE,
                   led_brightness = 0.15,   # LED brightness when on, in range [0..1]
                   led_brightness_off = None,  # When toggle: brightness when off [0..1]. If None, uses 0.04 (dim). Use 0 for off.
                   display = None,
                   use_leds = True,
                   id = None,
                   enable_callback = None,
                   toggle = False,          # If True, each press toggles on/off (sends message then message_release). Release does nothing.
                   group = None             # If set (string), radio-button behavior: pressing activates this, deactivates others in same group.
    ):
    if led_brightness_off is None:
        led_brightness_off = 0.04
    return Action({
        "callback": _CustomMessageCallback(
            message = message,
            message_release = message_release,
            color = color,
            led_brightness = led_brightness,
            led_brightness_off = led_brightness_off,
            text = text,
            toggle = toggle,
            group = group
        ),
        "display": display,
        "useSwitchLeds": use_leds,
        "id": id,
        "enableCallback": enable_callback
    })


class _CustomMessageCallback(Callback):
    class _RawMessage(MIDIMessage):
        def __init__(self, data):
            super().__init__()
            self.__data = bytearray(data)

        def __bytes__(self):
            return self.__data

    def __init__(self,
                 message,
                 message_release,
                 color,
                 led_brightness,
                 led_brightness_off,
                 text,
                 toggle = False,
                 group = None
        ):
        super().__init__()

        self.__message = message
        self.__message_release = message_release
        self.__color = color
        self.__text = text
        self.__led_brightness = led_brightness
        self.__led_brightness_off = led_brightness_off
        self.__toggle = toggle
        self.__group = group
        self.__state = False  # For toggle/group: False = off/inactive, True = on/active

    def init(self, appl, listener = None):
        self.__appl = appl
        if self.__group:
            key = "_custom_group_" + self.__group
            if key not in appl.shared:
                appl.shared[key] = []
            appl.shared[key].append(self)

    def push(self):
        if self.__group:
            # Radio-button: activate self, deactivate others in group
            key = "_custom_group_" + self.__group
            for cb in self.__appl.shared.get(key, []):
                cb.__state = False
            self.__state = True
            self.__appl.client.midi.send(self._RawMessage(self.__message))
        elif self.__toggle:
            self.__state = not self.__state
            msg = self.__message if self.__state else self.__message_release
            if msg is not None:
                self.__appl.client.midi.send(self._RawMessage(msg))
        else:
            self.__appl.client.midi.send(self._RawMessage(self.__message))

    def release(self):
        if self.__group:
            pass  # Radio mode: no action on release
        elif self.__toggle:
            pass  # Toggle mode: no action on release
        elif self.__message_release:
            self.__appl.client.midi.send(self._RawMessage(self.__message_release))

    def reset(self):
        if self.__group:
            self.__state = False

    def update_displays(self):
        self.action.switch_color = self.__color
        if self.__toggle or self.__group:
            self.action.switch_brightness = (
                self.__led_brightness if self.__state
                else self.__led_brightness_off
            )
        else:
            self.action.switch_brightness = self.__led_brightness

        if self.action.label:
            self.action.label.text = self.__text
            if self.__toggle or self.__group:
                self.action.label.back_color = (
                    self.__color if self.__state
                    else dim_color(self.__color, 0.3)
                )
            else:
                self.action.label.back_color = self.__color
