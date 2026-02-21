##############################################################################
#
# MVP - MIDI Captain Mini 6
# 4 pages: Logic, ToneX, GP-5, Looper
# Page change: A+B = page down, B+C = page up (combo only)
#
##############################################################################

from pyswitch.hardware.devices.pa_midicaptain_mini_6 import *
from pyswitch.clients.local.actions.pager import PagerAction
from pyswitch.clients.local.actions.custom import CUSTOM_MESSAGE
from pyswitch.colors import Colors
from display import (
    DISPLAY_HEADER_1, DISPLAY_HEADER_2, DISPLAY_HEADER_3,
    DISPLAY_FOOTER_1, DISPLAY_FOOTER_2, DISPLAY_FOOTER_3,
)

_pager = PagerAction(
    pages=[
        {"id": "logic", "color": Colors.BLUE, "text": "Logic"},
        {"id": "tonex", "color": Colors.RED, "text": "ToneX"},
        {"id": "gp5", "color": Colors.GREEN, "text": "GP-5"},
        {"id": "looper", "color": Colors.PURPLE, "text": "Looper"},
    ],
    led_brightness=0.3,
    display=DISPLAY_FOOTER_2,
)

ComboPager = _pager


Inputs = [
    # Switch 1 (top-left)
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_1,
        "actions": [
            CUSTOM_MESSAGE(
                message=[0xB0, 80, 127], message_release=[0xB0, 80, 0],
                color=Colors.BLUE, text="Comp", toggle=True,
                led_brightness=0.3, led_brightness_off=0.02,
                id="logic", enable_callback=_pager.enable_callback,
                display=DISPLAY_HEADER_1,
            ),
            CUSTOM_MESSAGE(
                message=[0xC1, 0], message_release=None,
                color=Colors.GREEN, text="Clean",
                group="pc_ch2", led_brightness=0.3, led_brightness_off=0.02,
                id="tonex", enable_callback=_pager.enable_callback,
                display=DISPLAY_HEADER_1,
            ),
            CUSTOM_MESSAGE(
                message=[0xC2, 0], message_release=None,
                color=Colors.GREEN, text="Pst1",
                group="pc_ch3", led_brightness=0.3, led_brightness_off=0.02,
                id="gp5", enable_callback=_pager.enable_callback,
                display=DISPLAY_HEADER_1,
            ),
            CUSTOM_MESSAGE(
                message=[0xB3, 60, 127], message_release=[0xB3, 60, 0],
                color=Colors.RED, text="REC",
                id="looper", enable_callback=_pager.enable_callback,
                display=DISPLAY_HEADER_1,
            ),
        ],
        "actionsHold": [_pager],
        "holdTimeMillis": 99999,
    },
    # Switch 2 (top-center)
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_2,
        "actions": [
            CUSTOM_MESSAGE(
                message=[0xB0, 81, 127], message_release=[0xB0, 81, 0],
                color=Colors.TURQUOISE, text="EQ", toggle=True,
                led_brightness=0.3, led_brightness_off=0.02,
                id="logic", enable_callback=_pager.enable_callback,
                display=DISPLAY_HEADER_2,
            ),
            CUSTOM_MESSAGE(
                message=[0xC1, 1], message_release=None,
                color=Colors.ORANGE, text="Crunch",
                group="pc_ch2", led_brightness=0.3, led_brightness_off=0.02,
                id="tonex", enable_callback=_pager.enable_callback,
                display=DISPLAY_HEADER_2,
            ),
            CUSTOM_MESSAGE(
                message=[0xC2, 1], message_release=None,
                color=Colors.GREEN, text="Pst2",
                group="pc_ch3", led_brightness=0.3, led_brightness_off=0.02,
                id="gp5", enable_callback=_pager.enable_callback,
                display=DISPLAY_HEADER_2,
            ),
            CUSTOM_MESSAGE(
                message=[0xB3, 61, 127], message_release=[0xB3, 61, 0],
                color=Colors.GREEN, text="PLAY",
                id="looper", enable_callback=_pager.enable_callback,
                display=DISPLAY_HEADER_2,
            ),
        ],
    },
    # Switch 3 (top-right)
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_3,
        "actions": [
            CUSTOM_MESSAGE(
                message=[0xB0, 82, 127], message_release=[0xB0, 82, 0],
                color=Colors.GREEN, text="Delay", toggle=True,
                led_brightness=0.3, led_brightness_off=0.02,
                id="logic", enable_callback=_pager.enable_callback,
                display=DISPLAY_HEADER_3,
            ),
            CUSTOM_MESSAGE(
                message=[0xC1, 2], message_release=None,
                color=Colors.RED, text="Lead",
                group="pc_ch2", led_brightness=0.3, led_brightness_off=0.02,
                id="tonex", enable_callback=_pager.enable_callback,
                display=DISPLAY_HEADER_3,
            ),
            CUSTOM_MESSAGE(
                message=[0xC2, 2], message_release=None,
                color=Colors.GREEN, text="Pst3",
                group="pc_ch3", led_brightness=0.3, led_brightness_off=0.02,
                id="gp5", enable_callback=_pager.enable_callback,
                display=DISPLAY_HEADER_3,
            ),
            CUSTOM_MESSAGE(
                message=[0xB3, 62, 127], message_release=[0xB3, 62, 0],
                color=Colors.YELLOW, text="STOP",
                id="looper", enable_callback=_pager.enable_callback,
                display=DISPLAY_HEADER_3,
            ),
        ],
    },
    # Switch A (bottom-left)
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_A,
        "actions": [
            CUSTOM_MESSAGE(
                message=[0xB0, 83, 127], message_release=[0xB0, 83, 0],
                color=Colors.PURPLE, text="Reverb", toggle=True,
                led_brightness=0.3, led_brightness_off=0.02,
                id="logic", enable_callback=_pager.enable_callback,
                display=DISPLAY_FOOTER_1,
            ),
            CUSTOM_MESSAGE(
                message=[0xB1, 50, 127], message_release=[0xB1, 50, 0],
                color=Colors.BLUE, text="Mod", toggle=True,
                led_brightness=0.3, led_brightness_off=0.02,
                id="tonex", enable_callback=_pager.enable_callback,
                display=DISPLAY_FOOTER_1,
            ),
            CUSTOM_MESSAGE(
                message=[0xB2, 19, 127], message_release=[0xB2, 19, 0],
                color=Colors.ORANGE, text="FX1", toggle=True,
                led_brightness=0.3, led_brightness_off=0.02,
                id="gp5", enable_callback=_pager.enable_callback,
                display=DISPLAY_FOOTER_1,
            ),
            CUSTOM_MESSAGE(
                message=[0xB3, 63, 127], message_release=[0xB3, 63, 0],
                color=Colors.ORANGE, text="UNDO",
                id="looper", enable_callback=_pager.enable_callback,
                display=DISPLAY_FOOTER_1,
            ),
        ],
    },
    # Switch B (bottom-center)
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_B,
        "actions": [
            CUSTOM_MESSAGE(
                message=[0xB0, 84, 127], message_release=[0xB0, 84, 0],
                color=Colors.PINK, text="Chorus", toggle=True,
                led_brightness=0.3, led_brightness_off=0.02,
                id="logic", enable_callback=_pager.enable_callback,
                display=DISPLAY_FOOTER_2,
            ),
            CUSTOM_MESSAGE(
                message=[0xB1, 51, 127], message_release=[0xB1, 51, 0],
                color=Colors.TURQUOISE, text="Delay", toggle=True,
                led_brightness=0.3, led_brightness_off=0.02,
                id="tonex", enable_callback=_pager.enable_callback,
                display=DISPLAY_FOOTER_2,
            ),
            CUSTOM_MESSAGE(
                message=[0xB2, 20, 127], message_release=[0xB2, 20, 0],
                color=Colors.TURQUOISE, text="FX2", toggle=True,
                led_brightness=0.3, led_brightness_off=0.02,
                id="gp5", enable_callback=_pager.enable_callback,
                display=DISPLAY_FOOTER_2,
            ),
            CUSTOM_MESSAGE(
                message=[0xB3, 64, 127], message_release=[0xB3, 64, 0],
                color=Colors.TURQUOISE, text="Half", toggle=True,
                led_brightness=0.3, led_brightness_off=0.02,
                id="looper", enable_callback=_pager.enable_callback,
                display=DISPLAY_FOOTER_2,
            ),
        ],
    },
    # Switch C (bottom-right)
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_C,
        "actions": [
            CUSTOM_MESSAGE(
                message=[0xB0, 85, 127], message_release=[0xB0, 85, 0],
                color=Colors.WHITE, text="Tap",
                id="logic", enable_callback=_pager.enable_callback,
                display=DISPLAY_FOOTER_3,
            ),
            CUSTOM_MESSAGE(
                message=[0xB1, 52, 127], message_release=[0xB1, 52, 0],
                color=Colors.PURPLE, text="Reverb", toggle=True,
                led_brightness=0.3, led_brightness_off=0.02,
                id="tonex", enable_callback=_pager.enable_callback,
                display=DISPLAY_FOOTER_3,
            ),
            CUSTOM_MESSAGE(
                message=[0xB2, 21, 127], message_release=[0xB2, 21, 0],
                color=Colors.PURPLE, text="FX3", toggle=True,
                led_brightness=0.3, led_brightness_off=0.02,
                id="gp5", enable_callback=_pager.enable_callback,
                display=DISPLAY_FOOTER_3,
            ),
            CUSTOM_MESSAGE(
                message=[0xB3, 65, 127], message_release=[0xB3, 65, 0],
                color=Colors.WHITE, text="CLR",
                id="looper", enable_callback=_pager.enable_callback,
                display=DISPLAY_FOOTER_3,
            ),
        ],
    },
]
