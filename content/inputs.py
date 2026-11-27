##############################################################################
#
# Ampz (iOS) - MIDI Captain Mini 6
# 3 pages: Stomp A, Stomp B, Looper     (all MIDI channel 1)
# Presets and scenes live on the Chocolate Plus.
# Page change: A+B = previous page, B+C = next page (combo only, wraps)
#
# Stomp A   [1] DIST 83    [2] DELAY 82   [3] BOOST (EQ) 90
#           [A] CHORUS 84 (hold = TUNER 68)  [B] TREM 89  [C] PHASER 87
# Stomp B   [1] PITCH 80   [2] WAH 81     [3] Tap 85
#           [A] FLANGER 91 (hold = TUNER 68)    [B] COMP 86    [C] REVERB 88
# Looper    [1] REC 60    [2] PLAY 61   [3] STOP 62
#           [A] UNDO 63 (hold = CLEAR 100)  [B] SCN- 104  [C] SCN+ 105
#
# TIMING: switches 1, 2, 3 send instantly on press. A, B, C wait 150 ms for the
# paging combo, and A / C also carry hold actions (they send on release). Keep
# time-critical functions (Tap, looper REC / PLAY / STOP) on the top row.
#
# Stomp switches send 127 (on) / 0 (off): learn them in Ampz as Stomp Mappings
# in LATCH mode. Everything else sends 127 on press: learn as Action Mappings.
#
# STATE SYNC: stomp switches also listen (listen = True) for their own CC coming
# back from Ampz, over USB or the MIDI in jack: >= 64 lights the switch, < 64
# turns it off. Ampz sends every stomp's state after a preset change, so the LEDs
# follow presets. See PySwitch_Custom_Project/AMPZ_STATE_SYNC.md.
#
##############################################################################

from pyswitch.clients.local.actions.custom import CUSTOM_MESSAGE
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
    display = DISPLAY_FOOTER_2, 
    led_brightness = 0.3
)

ComboPager = _pager


Inputs = [
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_1,
        "actions": [
            CUSTOM_MESSAGE(
                message = [0xB0, 83, 127], 
                message_release = [0xB0, 83, 0], 
                color = (255, 70, 0), 
                led_brightness = 0.3, 
                led_brightness_off = 0.02, 
                display = DISPLAY_HEADER_1, 
                toggle = True, 
                listen = True, 
                text = 'DIST', 
                id = 'stompa', 
                enable_callback = _pager.enable_callback
            ),
            CUSTOM_MESSAGE(
                message = [0xB0, 80, 127], 
                message_release = [0xB0, 80, 0], 
                color = (140, 255, 0), 
                led_brightness = 0.3, 
                led_brightness_off = 0.02, 
                display = DISPLAY_HEADER_1, 
                toggle = True, 
                listen = True, 
                text = 'PITCH', 
                id = 'stompb', 
                enable_callback = _pager.enable_callback
            ),
            CUSTOM_MESSAGE(
                message = [0xB0, 60, 127], 
                color = Colors.RED, 
                led_brightness = 0.3, 
                led_brightness_off = 0.02, 
                display = DISPLAY_HEADER_1, 
                text = 'REC', 
                id = 'looper', 
                enable_callback = _pager.enable_callback
            ),
            
        ],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_2,
        "actions": [
            CUSTOM_MESSAGE(
                message = [0xB0, 82, 127], 
                message_release = [0xB0, 82, 0], 
                color = Colors.GREEN, 
                led_brightness = 0.3, 
                led_brightness_off = 0.02, 
                display = DISPLAY_HEADER_2, 
                toggle = True, 
                listen = True, 
                text = 'DELAY', 
                id = 'stompa', 
                enable_callback = _pager.enable_callback
            ),
            CUSTOM_MESSAGE(
                message = [0xB0, 81, 127], 
                message_release = [0xB0, 81, 0], 
                color = (0, 180, 255), 
                led_brightness = 0.3, 
                led_brightness_off = 0.02, 
                display = DISPLAY_HEADER_2, 
                toggle = True, 
                listen = True, 
                text = 'WAH', 
                id = 'stompb', 
                enable_callback = _pager.enable_callback
            ),
            CUSTOM_MESSAGE(
                message = [0xB0, 61, 127], 
                color = Colors.GREEN, 
                led_brightness = 0.3, 
                led_brightness_off = 0.02, 
                display = DISPLAY_HEADER_2, 
                text = 'PLAY', 
                id = 'looper', 
                enable_callback = _pager.enable_callback
            ),
            
        ],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_3,
        "actions": [
            CUSTOM_MESSAGE(
                message = [0xB0, 90, 127], 
                message_release = [0xB0, 90, 0], 
                color = Colors.YELLOW, 
                led_brightness = 0.3, 
                led_brightness_off = 0.02, 
                display = DISPLAY_HEADER_3, 
                toggle = True, 
                listen = True, 
                text = 'BOOST', 
                id = 'stompa', 
                enable_callback = _pager.enable_callback
            ),
            CUSTOM_MESSAGE(
                message = [0xB0, 85, 127], 
                color = Colors.WHITE, 
                led_brightness = 0.3, 
                led_brightness_off = 0.02, 
                display = DISPLAY_HEADER_3, 
                text = 'Tap', 
                id = 'stompb', 
                enable_callback = _pager.enable_callback
            ),
            CUSTOM_MESSAGE(
                message = [0xB0, 62, 127], 
                color = Colors.YELLOW, 
                led_brightness = 0.3, 
                led_brightness_off = 0.02, 
                display = DISPLAY_HEADER_3, 
                text = 'STOP', 
                id = 'looper', 
                enable_callback = _pager.enable_callback
            ),
            
        ],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_A,
        "actions": [
            CUSTOM_MESSAGE(
                message = [0xB0, 84, 127], 
                message_release = [0xB0, 84, 0], 
                color = (150, 0, 255), 
                led_brightness = 0.3, 
                led_brightness_off = 0.02, 
                display = DISPLAY_FOOTER_1, 
                toggle = True, 
                listen = True, 
                text = 'CHORUS', 
                id = 'stompa', 
                enable_callback = _pager.enable_callback
            ),
            CUSTOM_MESSAGE(
                message = [0xB0, 91, 127], 
                message_release = [0xB0, 91, 0], 
                color = (150, 0, 255), 
                led_brightness = 0.3, 
                led_brightness_off = 0.02, 
                display = DISPLAY_FOOTER_1, 
                toggle = True, 
                listen = True, 
                text = 'FLANGER', 
                id = 'stompb', 
                enable_callback = _pager.enable_callback
            ),
            CUSTOM_MESSAGE(
                message = [0xB0, 63, 127], 
                color = (255, 70, 0), 
                led_brightness = 0.3, 
                led_brightness_off = 0.02, 
                display = DISPLAY_FOOTER_1, 
                text = 'UNDO', 
                id = 'looper', 
                enable_callback = _pager.enable_callback
            ),
            
        ],
        "actionsHold": [
            CUSTOM_MESSAGE(
                message = [0xB0, 68, 127], 
                color = Colors.WHITE, 
                led_brightness = 0.3, 
                led_brightness_off = 0.02, 
                use_leds = False, 
                text = 'TUNER', 
                id = 'stompa', 
                enable_callback = _pager.enable_callback
            ),
            CUSTOM_MESSAGE(
                message = [0xB0, 68, 127], 
                color = Colors.WHITE, 
                led_brightness = 0.3, 
                led_brightness_off = 0.02, 
                use_leds = False, 
                text = 'TUNER', 
                id = 'stompb', 
                enable_callback = _pager.enable_callback
            ),
            CUSTOM_MESSAGE(
                message = [0xB0, 100, 127], 
                color = Colors.WHITE, 
                led_brightness = 0.3, 
                led_brightness_off = 0.02, 
                text = 'CLEAR', 
                id = 'looper', 
                enable_callback = _pager.enable_callback
            ),
            
        ],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_B,
        "actions": [
            CUSTOM_MESSAGE(
                message = [0xB0, 89, 127], 
                message_release = [0xB0, 89, 0], 
                color = (255, 0, 150), 
                led_brightness = 0.3, 
                led_brightness_off = 0.02, 
                display = DISPLAY_FOOTER_2, 
                toggle = True, 
                listen = True, 
                text = 'TREM', 
                id = 'stompa', 
                enable_callback = _pager.enable_callback
            ),
            CUSTOM_MESSAGE(
                message = [0xB0, 86, 127], 
                message_release = [0xB0, 86, 0], 
                color = Colors.BLUE, 
                led_brightness = 0.3, 
                led_brightness_off = 0.02, 
                display = DISPLAY_FOOTER_2, 
                toggle = True, 
                listen = True, 
                text = 'COMP', 
                id = 'stompb', 
                enable_callback = _pager.enable_callback
            ),
            CUSTOM_MESSAGE(
                message = [0xB0, 104, 127], 
                color = (255, 170, 0), 
                led_brightness = 0.3, 
                led_brightness_off = 0.02, 
                display = DISPLAY_FOOTER_2, 
                text = 'SCN-', 
                id = 'looper', 
                enable_callback = _pager.enable_callback
            ),
            
        ],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_C,
        "actions": [
            CUSTOM_MESSAGE(
                message = [0xB0, 87, 127], 
                message_release = [0xB0, 87, 0], 
                color = (90, 40, 255), 
                led_brightness = 0.3, 
                led_brightness_off = 0.02, 
                display = DISPLAY_FOOTER_3, 
                toggle = True, 
                listen = True, 
                text = 'PHASER', 
                id = 'stompa', 
                enable_callback = _pager.enable_callback
            ),
            CUSTOM_MESSAGE(
                message = [0xB0, 88, 127], 
                message_release = [0xB0, 88, 0], 
                color = (0, 255, 150), 
                led_brightness = 0.3, 
                led_brightness_off = 0.02, 
                display = DISPLAY_FOOTER_3, 
                toggle = True, 
                listen = True, 
                text = 'REVERB', 
                id = 'stompb', 
                enable_callback = _pager.enable_callback
            ),
            CUSTOM_MESSAGE(
                message = [0xB0, 105, 127], 
                color = (255, 170, 0), 
                led_brightness = 0.3, 
                led_brightness_off = 0.02, 
                display = DISPLAY_FOOTER_3, 
                text = 'SCN+', 
                id = 'looper', 
                enable_callback = _pager.enable_callback
            ),
            
        ],
        "actionsHold": [
            _pager,
            
        ],
        "holdTimeMillis": 99999,
        
    },
    
]
