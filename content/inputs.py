##############################################################################
#
# Ampz (iOS) - MIDI Captain Mini 6, with feedback from Ampz
# 3 pages: Stomp A, Stomp B, Looper     (all MIDI channel 1)
# Presets and scenes live on the Chocolate Plus (and SCN-/SCN+ on the Looper page).
# Page change: A+B = previous page, B+C = next page (combo only, wraps)
#
# Every stomp switch is an Ampz STOMP NUMBER, not an effect. Ampz sends each stomp's name,
# family colour and state, so the labels and LEDs follow the loaded preset:
#
# Stomp A   [1] stomp 1 CC 83   [2] stomp 2 CC 82   [3] stomp 3 CC 90
#           [A] stomp 4 CC 84 (hold = TUNER 68)  [B] stomp 5 CC 89  [C] stomp 6 CC 87
# Stomp B   [1] stomp 7 CC 80   [2] stomp 8 CC 81   [3] Tap 85
#           [A] stomp 9 CC 91 (hold = TUNER 68)   [B] stomp 10 CC 86  [C] TUNER 68
# Looper    [1] REC 60    [2] PLAY 61   [3] STOP 62
#           [A] UNDO 63 (hold = CLEAR 100)  [B] SCN- 104  [C] SCN+ 105
#
# TIMING: switches 1, 2, 3 send instantly on press. A, B, C wait 150 ms for the
# paging combo, and A also carries hold actions (they send on release). Keep
# time-critical functions (Tap, looper REC / PLAY / STOP) on the top row.
#
# Stomp switches always send 127: learn them in Ampz as Stomp Mappings in TOGGLE mode
# (the default). Ampz flips the pedal and echoes the true state (0 off, 64 half, 127 on),
# which is what lights the LED. Looper switches send 127 on press and 0 on release; their
# LEDs follow Ampz's looper (REC red, dim red while overdubbing, PLAY green, STOP lit when
# stopped, UNDO lit when there is something to undo). Tap, TUNER, SCN-, SCN+ and CLEAR get
# no feedback and sit at their dim fixed colour.
#
##############################################################################

from pyswitch.clients.ampz.actions import AMPZ_SWITCH
from pyswitch.clients.local.actions.pager import PagerAction
from pyswitch.colors import Colors
from display import DISPLAY_HEADER_1
from display import DISPLAY_HEADER_2
from display import DISPLAY_HEADER_3
from display import DISPLAY_FOOTER_1
from display import DISPLAY_FOOTER_2
from display import DISPLAY_FOOTER_3
from pyswitch.hardware.devices.pa_midicaptain_mini_6 import *

_pager = PagerAction(
    pages = [
        {
            "id": "stompa",
            "color": Colors.BLUE,
            "text": "Stomp A",
        },
        {
            "id": "stompb",
            "color": Colors.TURQUOISE,
            "text": "Stomp B",
        },
        {
            "id": "looper",
            "color": Colors.RED,
            "text": "Looper",
        },
    ],
    led_brightness = 0.3
)

ComboPager = _pager

_WHITE = Colors.WHITE
_SCENE = Colors.TURQUOISE


def _stomp(cc, stomp, display, page):
    return AMPZ_SWITCH(
        cc = cc,
        stomp = stomp,
        display = display,
        color = _WHITE,
        id = page,
        enable_callback = _pager.enable_callback
    )


def _button(cc, text, color, display, page, momentary = True, use_leds = True):
    return AMPZ_SWITCH(
        cc = cc,
        text = text,
        color = color,
        display = display,
        momentary = momentary,
        use_leds = use_leds,
        id = page,
        enable_callback = _pager.enable_callback
    )


Inputs = [
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_1,
        "actions": [
            _stomp(83, 0, DISPLAY_HEADER_1, 'stompa'),
            _stomp(80, 6, DISPLAY_HEADER_1, 'stompb'),
            _button(60, 'REC', Colors.RED, DISPLAY_HEADER_1, 'looper'),
        ],
    },
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_2,
        "actions": [
            _stomp(82, 1, DISPLAY_HEADER_2, 'stompa'),
            _stomp(81, 7, DISPLAY_HEADER_2, 'stompb'),
            _button(61, 'PLAY', Colors.GREEN, DISPLAY_HEADER_2, 'looper'),
        ],
    },
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_3,
        "actions": [
            _stomp(90, 2, DISPLAY_HEADER_3, 'stompa'),
            _button(85, 'Tap', _WHITE, DISPLAY_HEADER_3, 'stompb'),
            _button(62, 'STOP', Colors.ORANGE, DISPLAY_HEADER_3, 'looper'),
        ],
    },
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_A,
        "actions": [
            _stomp(84, 3, DISPLAY_FOOTER_1, 'stompa'),
            _stomp(91, 8, DISPLAY_FOOTER_1, 'stompb'),
            _button(63, 'UNDO', Colors.YELLOW, DISPLAY_FOOTER_1, 'looper'),
        ],
        "actionsHold": [
            _button(68, 'TUNER', _WHITE, None, 'stompa', momentary = False, use_leds = False),
            _button(68, 'TUNER', _WHITE, None, 'stompb', momentary = False, use_leds = False),
            _button(100, 'CLEAR', _WHITE, None, 'looper', momentary = False, use_leds = False),
        ],
    },
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_B,
        "actions": [
            _stomp(89, 4, DISPLAY_FOOTER_2, 'stompa'),
            _stomp(86, 9, DISPLAY_FOOTER_2, 'stompb'),
            _button(104, 'SCN-', _SCENE, DISPLAY_FOOTER_2, 'looper'),
        ],
    },
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_C,
        "actions": [
            _stomp(87, 5, DISPLAY_FOOTER_3, 'stompa'),
            _button(68, 'TUNER', Colors.LIGHT_BLUE, DISPLAY_FOOTER_3, 'stompb'),
            _button(105, 'SCN+', _SCENE, DISPLAY_FOOTER_3, 'looper'),
        ],
        "actionsHold": [
            _pager,
        ],
        "holdTimeMillis": 99999,
    },
]
