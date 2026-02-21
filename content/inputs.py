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


def cc_toggle(channel, cc, color, text, page_id, display=None):
    ch = channel - 1
    return CUSTOM_MESSAGE(
        message=[0xB0 + ch, cc, 127],
        message_release=[0xB0 + ch, cc, 0],
        color=color,
        text=text,
        id=page_id,
        enable_callback=_pager.enable_callback,
        toggle=True,
        led_brightness=0.3,
        led_brightness_off=0.02,
        display=display,
    )


def cc_momentary(channel, cc, color, text, page_id, display=None):
    ch = channel - 1
    return CUSTOM_MESSAGE(
        message=[0xB0 + ch, cc, 127],
        message_release=[0xB0 + ch, cc, 0],
        color=color,
        text=text,
        id=page_id,
        enable_callback=_pager.enable_callback,
        display=display,
    )


def pc_select(channel, pc, color, text, page_id, display=None):
    ch = channel - 1
    return CUSTOM_MESSAGE(
        message=[0xC0 + ch, pc],
        message_release=None,
        color=color,
        text=text,
        id=page_id,
        enable_callback=_pager.enable_callback,
        display=display,
        group=f"pc_ch{channel}",
        led_brightness=0.3,
        led_brightness_off=0.02,
    )


Inputs = [
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_1,
        "actions": [
            cc_toggle(1, 80, Colors.BLUE, "Comp", "logic", DISPLAY_HEADER_1),
            pc_select(2, 0, Colors.GREEN, "Clean", "tonex", DISPLAY_HEADER_1),
            pc_select(3, 0, Colors.GREEN, "Pst1", "gp5", DISPLAY_HEADER_1),
            cc_momentary(4, 60, Colors.RED, "REC", "looper", DISPLAY_HEADER_1),
        ],
        "actionsHold": [_pager],
        "holdTimeMillis": 99999,
    },
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_2,
        "actions": [
            cc_toggle(1, 81, Colors.TURQUOISE, "EQ", "logic", DISPLAY_HEADER_2),
            pc_select(2, 1, Colors.ORANGE, "Crunch", "tonex", DISPLAY_HEADER_2),
            pc_select(3, 1, Colors.GREEN, "Pst2", "gp5", DISPLAY_HEADER_2),
            cc_momentary(4, 61, Colors.GREEN, "PLAY", "looper", DISPLAY_HEADER_2),
        ],
    },
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_3,
        "actions": [
            cc_toggle(1, 82, Colors.GREEN, "Delay", "logic", DISPLAY_HEADER_3),
            pc_select(2, 2, Colors.RED, "Lead", "tonex", DISPLAY_HEADER_3),
            pc_select(3, 2, Colors.GREEN, "Pst3", "gp5", DISPLAY_HEADER_3),
            cc_momentary(4, 62, Colors.YELLOW, "STOP", "looper", DISPLAY_HEADER_3),
        ],
    },
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_A,
        "actions": [
            cc_toggle(1, 83, Colors.PURPLE, "Reverb", "logic", DISPLAY_FOOTER_1),
            cc_toggle(2, 50, Colors.BLUE, "Mod", "tonex", DISPLAY_FOOTER_1),
            cc_toggle(3, 19, Colors.ORANGE, "FX1", "gp5", DISPLAY_FOOTER_1),
            cc_momentary(4, 63, Colors.ORANGE, "UNDO", "looper", DISPLAY_FOOTER_1),
        ],
    },
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_B,
        "actions": [
            cc_toggle(1, 84, Colors.PINK, "Chorus", "logic", DISPLAY_FOOTER_2),
            cc_toggle(2, 51, Colors.TURQUOISE, "Delay", "tonex", DISPLAY_FOOTER_2),
            cc_toggle(3, 20, Colors.TURQUOISE, "FX2", "gp5", DISPLAY_FOOTER_2),
            cc_toggle(4, 64, Colors.TURQUOISE, "1/2", "looper", DISPLAY_FOOTER_2),
        ],
    },
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_C,
        "actions": [
            cc_momentary(1, 85, Colors.WHITE, "Tap", "logic", DISPLAY_FOOTER_3),
            cc_toggle(2, 52, Colors.PURPLE, "Reverb", "tonex", DISPLAY_FOOTER_3),
            cc_toggle(3, 21, Colors.PURPLE, "FX3", "gp5", DISPLAY_FOOTER_3),
            cc_momentary(4, 65, Colors.WHITE, "CLR", "looper", DISPLAY_FOOTER_3),
        ],
    },
]
