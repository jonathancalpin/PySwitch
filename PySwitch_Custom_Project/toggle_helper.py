##############################################################################
#
# Toggle Helper for CUSTOM_MESSAGE
# Converts momentary CUSTOM_MESSAGE to toggle behavior
#
##############################################################################

from pyswitch.controller.callbacks import Callback
from pyswitch.controller.actions import Action
from pyswitch.colors import Colors
from adafruit_midi.midi_message import MIDIMessage


class _ToggleMessageCallback(Callback):
    """Callback that toggles between ON (127) and OFF (0) on each press."""
    
    class _RawMessage(MIDIMessage):
        def __init__(self, data):
            self.__data = bytearray(data)

        def __bytes__(self):
            return self.__data
    
    def __init__(self, message_base, color, led_brightness, text):
        """
        message_base: Base MIDI message (e.g., [0xB0, 80]) - value will be added
        """
        super().__init__()
        self.__message_base = message_base
        self.__color = color
        self.__text = text
        self.__led_brightness = led_brightness
        self.__state = False  # False = OFF, True = ON
        self.__appl = None
    
    def init(self, appl, listener=None):
        self.__appl = appl
    
    def push(self):
        # Toggle state
        self.__state = not self.__state
        
        # Create message with value: 127 if ON, 0 if OFF
        value = 127 if self.__state else 0
        message = list(self.__message_base) + [value]
        
        # Send MIDI message
        self.__appl.client.midi.send(self._RawMessage(message))
    
    def release(self):
        # Do nothing on release for toggle mode
        pass
    
    def update_displays(self):
        self.action.switch_color = self.__color
        self.action.switch_brightness = self.__led_brightness

        if self.action.label:
            self.action.label.text = self.__text
            self.action.label.back_color = self.__color


def CUSTOM_MESSAGE_TOGGLE(message_base,      # Base MIDI message without value (e.g., [0xB0, 80])
                          text = "",
                          color = Colors.WHITE,
                          led_brightness = 0.15,
                          display = None,
                          use_leds = True,
                          id = None,
                          enable_callback = None
    ):
    """
    Creates a toggle action that sends 127 on first press (ON), 0 on second press (OFF).
    
    Example:
        CUSTOM_MESSAGE_TOGGLE(
            message_base = [0xB0, 80],  # CC#80 on Channel 1
            text = "Comp",
            color = Colors.BLUE
        )
    """
    return Action({
        "callback": _ToggleMessageCallback(
            message_base = message_base,
            color = color,
            led_brightness = led_brightness,
            text = text
        ),
        "display": display,
        "useSwitchLeds": use_leds,
        "id": id,
        "enableCallback": enable_callback
    })
