##############################################################################
#
# Multi-Device MIDI Controller Configuration
# MIDI Captain Mini 6 with PySwitch + Combo Page Navigation
#
# Pages:
#   1. Logic Pro X - DAW effect bypasses (USB MIDI, Channel 1)
#   2. ToneX One - Presets and effects (USB MIDI, Channel 2)
#   3. Valeton GP-5 - Presets and effects (DIN MIDI, Channel 3)
#   4. Looper - Transport controls (USB MIDI, Channel 4)
#
# Page Navigation (via combo detection):
#   A+B pressed together = Page Up (next page)
#   B+C pressed together = Page Down (previous page)
#
##############################################################################

from pyswitch.hardware.devices.pa_midicaptain_mini_6 import (
    PA_MIDICAPTAIN_MINI_SWITCH_1,
    PA_MIDICAPTAIN_MINI_SWITCH_2,
    PA_MIDICAPTAIN_MINI_SWITCH_3,
    PA_MIDICAPTAIN_MINI_SWITCH_A,
    PA_MIDICAPTAIN_MINI_SWITCH_B,
    PA_MIDICAPTAIN_MINI_SWITCH_C,
)

from pyswitch.clients.local.actions.custom import CUSTOM_MESSAGE
from display import (
    DISPLAY_HEADER_1,
    DISPLAY_HEADER_2,
    DISPLAY_HEADER_3,
    DISPLAY_FOOTER_1,
    DISPLAY_FOOTER_2,
    DISPLAY_FOOTER_3,
)

##############################################################################
# COLOR DEFINITIONS (RGB tuples)
##############################################################################

COLOR_RED = (255, 0, 0)
COLOR_ORANGE = (255, 128, 0)
COLOR_YELLOW = (255, 255, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_CYAN = (0, 255, 255)
COLOR_BLUE = (0, 128, 255)
COLOR_PURPLE = (128, 0, 255)
COLOR_PINK = (255, 0, 128)
COLOR_WHITE = (255, 255, 255)

##############################################################################
# MIDI MESSAGE HELPERS
# Raw MIDI bytes format:
#   CC:  [0xB0 + channel, cc_number, value]  (channel is 0-indexed)
#   PC:  [0xC0 + channel, program_number]
##############################################################################

def cc_toggle(channel, cc, color, text, display=None):
    """Create a CC toggle action (on=127, off=0). Each press toggles; LED/display dim when off."""
    ch = channel - 1
    return CUSTOM_MESSAGE(
        message = [0xB0 + ch, cc, 127],
        message_release = [0xB0 + ch, cc, 0],
        color = color,
        text = text,
        display = display,
        led_brightness_off = 0.3,
        toggle = True,
    )

def cc_momentary(channel, cc, color, text, display=None):
    """Create a CC momentary action (127 on press, 0 on release)."""
    ch = channel - 1
    return CUSTOM_MESSAGE(
        message = [0xB0 + ch, cc, 127],
        message_release = [0xB0 + ch, cc, 0],
        color = color,
        text = text,
        display = display,
    )

def pc_select(channel, pc, color, text, display=None):
    """Create a Program Change action."""
    ch = channel - 1
    return CUSTOM_MESSAGE(
        message = [0xC0 + ch, pc],
        message_release = None,
        color = color,
        text = text,
        display = display,
        group = f"pc_ch{channel}",
    )

##############################################################################
# PAGE 1: LOGIC PRO X - DAW EFFECTS (Channel 1)
##############################################################################

PAGE_LOGIC = {
    "name": "Logic",
    "channel": 1,
    "midi_out": "USB",
    "color_theme": COLOR_BLUE,
    "switches": [
        {"assignment": PA_MIDICAPTAIN_MINI_SWITCH_1, "actions": [cc_toggle(1, 80, COLOR_BLUE, "Comp", DISPLAY_HEADER_1)]},
        {"assignment": PA_MIDICAPTAIN_MINI_SWITCH_2, "actions": [cc_toggle(1, 81, COLOR_CYAN, "EQ", DISPLAY_HEADER_2)]},
        {"assignment": PA_MIDICAPTAIN_MINI_SWITCH_3, "actions": [cc_toggle(1, 82, COLOR_GREEN, "Delay", DISPLAY_HEADER_3)]},
        {"assignment": PA_MIDICAPTAIN_MINI_SWITCH_A, "actions": [cc_toggle(1, 83, COLOR_PURPLE, "Reverb", DISPLAY_FOOTER_1)]},
        {"assignment": PA_MIDICAPTAIN_MINI_SWITCH_B, "actions": [cc_toggle(1, 84, COLOR_PINK, "Chorus", DISPLAY_FOOTER_2)]},
        {"assignment": PA_MIDICAPTAIN_MINI_SWITCH_C, "actions": [cc_momentary(1, 85, COLOR_WHITE, "Tap", DISPLAY_FOOTER_3)]},
    ]
}

##############################################################################
# PAGE 2: TONEX ONE (Channel 2)
##############################################################################

PAGE_TONEX = {
    "name": "ToneX",
    "channel": 2,
    "midi_out": "USB",
    "color_theme": COLOR_RED,
    "switches": [
        {"assignment": PA_MIDICAPTAIN_MINI_SWITCH_1, "actions": [pc_select(2, 0, COLOR_GREEN, "Clean", DISPLAY_HEADER_1)]},
        {"assignment": PA_MIDICAPTAIN_MINI_SWITCH_2, "actions": [pc_select(2, 1, COLOR_ORANGE, "Crunch", DISPLAY_HEADER_2)]},
        {"assignment": PA_MIDICAPTAIN_MINI_SWITCH_3, "actions": [pc_select(2, 2, COLOR_RED, "Lead", DISPLAY_HEADER_3)]},
        {"assignment": PA_MIDICAPTAIN_MINI_SWITCH_A, "actions": [cc_toggle(2, 50, COLOR_BLUE, "Mod", DISPLAY_FOOTER_1)]},
        {"assignment": PA_MIDICAPTAIN_MINI_SWITCH_B, "actions": [cc_toggle(2, 51, COLOR_CYAN, "Delay", DISPLAY_FOOTER_2)]},
        {"assignment": PA_MIDICAPTAIN_MINI_SWITCH_C, "actions": [cc_toggle(2, 52, COLOR_PURPLE, "Reverb", DISPLAY_FOOTER_3)]},
    ]
}

##############################################################################
# PAGE 3: VALETON GP-5 (Channel 3, DIN MIDI)
##############################################################################

PAGE_GP5 = {
    "name": "GP-5",
    "channel": 3,
    "midi_out": "DIN",
    "color_theme": COLOR_GREEN,
    "switches": [
        {"assignment": PA_MIDICAPTAIN_MINI_SWITCH_1, "actions": [pc_select(3, 0, COLOR_GREEN, "Pst 1", DISPLAY_HEADER_1)]},
        {"assignment": PA_MIDICAPTAIN_MINI_SWITCH_2, "actions": [pc_select(3, 1, COLOR_GREEN, "Pst 2", DISPLAY_HEADER_2)]},
        {"assignment": PA_MIDICAPTAIN_MINI_SWITCH_3, "actions": [pc_select(3, 2, COLOR_GREEN, "Pst 3", DISPLAY_HEADER_3)]},
        {"assignment": PA_MIDICAPTAIN_MINI_SWITCH_A, "actions": [cc_toggle(3, 19, COLOR_ORANGE, "FX1", DISPLAY_FOOTER_1)]},
        {"assignment": PA_MIDICAPTAIN_MINI_SWITCH_B, "actions": [cc_toggle(3, 20, COLOR_CYAN, "FX2", DISPLAY_FOOTER_2)]},
        {"assignment": PA_MIDICAPTAIN_MINI_SWITCH_C, "actions": [cc_toggle(3, 21, COLOR_PURPLE, "FX3", DISPLAY_FOOTER_3)]},
    ]
}

##############################################################################
# PAGE 4: LOOPER CONTROLS (Channel 4)
##############################################################################

PAGE_LOOPER = {
    "name": "Looper",
    "channel": 4,
    "midi_out": "USB",
    "color_theme": COLOR_PURPLE,
    "switches": [
        {"assignment": PA_MIDICAPTAIN_MINI_SWITCH_1, "actions": [cc_momentary(4, 60, COLOR_RED, "REC", DISPLAY_HEADER_1)]},
        {"assignment": PA_MIDICAPTAIN_MINI_SWITCH_2, "actions": [cc_momentary(4, 61, COLOR_GREEN, "PLAY", DISPLAY_HEADER_2)]},
        {"assignment": PA_MIDICAPTAIN_MINI_SWITCH_3, "actions": [cc_momentary(4, 62, COLOR_YELLOW, "STOP", DISPLAY_HEADER_3)]},
        {"assignment": PA_MIDICAPTAIN_MINI_SWITCH_A, "actions": [cc_momentary(4, 63, COLOR_ORANGE, "UNDO", DISPLAY_FOOTER_1)]},
        {"assignment": PA_MIDICAPTAIN_MINI_SWITCH_B, "actions": [cc_toggle(4, 64, COLOR_CYAN, "1/2", DISPLAY_FOOTER_2)]},
        {"assignment": PA_MIDICAPTAIN_MINI_SWITCH_C, "actions": [cc_momentary(4, 65, COLOR_WHITE, "CLR", DISPLAY_FOOTER_3)]},
    ]
}

##############################################################################
# ALL PAGES COLLECTION
##############################################################################

Pages = [
    PAGE_LOGIC,
    PAGE_TONEX,
    PAGE_GP5,
    PAGE_LOOPER,
]

##############################################################################
# COMBO DETECTION CONFIGURATION
##############################################################################

ComboConfig = {
    "enabled": True,
    "combo_switches": ['A', 'B', 'C'],
    "combo_window_ms": 50,
}

##############################################################################
# INITIAL INPUTS (First page - required by PySwitch)
##############################################################################

Inputs = PAGE_LOGIC["switches"]
