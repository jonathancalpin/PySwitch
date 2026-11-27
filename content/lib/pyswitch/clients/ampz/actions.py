##############################################################################
#
# Ampz switch action and feedback callback.
#
# The stock PushButtonAction keys its LEDs off its own press state. With Ampz as the authority
# that fights the truth, so these classes split the two jobs: AMPZ_SWITCH only sends, and
# AmpzFeedbackCallback only draws what Ampz has reported (CC value for brightness, label frame
# for text and colour). A press never repaints anything; the echo from Ampz does.
#
##############################################################################

from ...controller.callbacks import Callback
from ...controller.actions import Action
from ...controller.client import ClientParameterMapping
from ...colors import dim_color, DEFAULT_LABEL_COLOR
from adafruit_midi.control_change import ControlChange

from . import AmpzSysexMapping, TYPE_STOMP_LABEL, FAMILY_COLORS


# Switch that sends CC `cc` with value 127 on every press (and 0 on release when momentary) and
# follows Ampz's feedback for its LED and label.
#
#   stomp:     Ampz stomp number 0..9. The label text and colour then come from Ampz; `text` and
#              `color` are ignored once a label frame has arrived.
#   text:      fixed label text for non-stomp switches (looper, tap, tuner)
#   color:     fixed colour for non-stomp switches, and the colour shown for a stomp before
#              its label frame arrives
def AMPZ_SWITCH(cc,
                display = None,
                text = None,
                color = (255, 255, 255),
                momentary = False,
                stomp = None,
                enable_callback = None,
                id = None,
                led_on = 0.3,
                led_half = 0.1,
                led_off = 0.02):
    return Action({
        "callback": AmpzFeedbackCallback(
            cc = cc,
            text = text,
            color = color,
            momentary = momentary,
            stomp = stomp,
            led_on = led_on,
            led_half = led_half,
            led_off = led_off
        ),
        "display": display,
        "useSwitchLeds": True,
        "id": id,
        "enableCallback": enable_callback
    })


class AmpzFeedbackCallback(Callback):

    DIM_HALF = 0.5
    DIM_OFF = 0.2

    def __init__(self, cc, text, color, momentary, stomp, led_on, led_half, led_off):
        super().__init__()

        self._cc = cc
        self._text = text if text is not None else ""
        self._color = color
        self._momentary = momentary
        self._stomp = stomp
        self._led_on = led_on
        self._led_half = led_half
        self._led_off = led_off
        self._appl = None

        self._cc_mapping = ClientParameterMapping.get(
            name = "Ampz CC " + repr(cc),
            response = ControlChange(cc, 0)
        )
        self._cc_mapping.value = None   # fresh boot: nothing known yet
        self.register_mapping(self._cc_mapping)

        self._label_mapping = None
        if stomp is not None:
            self._label_mapping = AmpzSysexMapping("Ampz stomp " + repr(stomp), TYPE_STOMP_LABEL, stomp)
            self.register_mapping(self._label_mapping)

    def init(self, appl, listener = None):
        self._appl = appl
        super().init(appl, listener)

    # Press: tell Ampz. Ampz flips (toggle mode) and echoes the truth.
    def push(self):
        self._appl.client.midi.send(ControlChange(self._cc, 127))

    def release(self):
        if self._momentary:
            self._appl.client.midi.send(ControlChange(self._cc, 0))

    # Values live in the mappings; a page change redraws from them.
    def reset(self):
        pass

    def update_displays(self):
        value = self._cc_mapping.value
        if value is None:
            value = 0

        color = self._color
        text = self._text
        empty = False

        if self._label_mapping is not None:
            received = self._label_mapping.value
            if received is not None:
                family, name = received
                text = name
                if family in FAMILY_COLORS:
                    color = FAMILY_COLORS[family]
                empty = (family == 0)
            else:
                text = ""

        if empty:
            brightness = 0
            back_color = DEFAULT_LABEL_COLOR
        elif value >= 127:
            brightness = self._led_on
            back_color = color
        elif value >= 64:
            brightness = self._led_half
            back_color = dim_color(color, self.DIM_HALF)
        else:
            brightness = self._led_off
            back_color = dim_color(color, self.DIM_OFF)

        self.action.switch_color = color
        self.action.switch_brightness = brightness

        if self.action.label:
            self.action.label.text = text
            self.action.label.back_color = back_color
