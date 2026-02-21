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
# Button Layout:
#   [1] [2] [3]   <- Top row
#   [A] [B] [C]   <- Bottom row (A+B and B+C are combo triggers)
#
##############################################################################

# Import hardware definitions (correct import path - no '_6' suffix)
from pyswitch.hardware.devices.pa_midicaptain_mini_6 import (
    PA_MIDICAPTAIN_MINI_SWITCH_1,
    PA_MIDICAPTAIN_MINI_SWITCH_2,
    PA_MIDICAPTAIN_MINI_SWITCH_3,
    PA_MIDICAPTAIN_MINI_SWITCH_A,
    PA_MIDICAPTAIN_MINI_SWITCH_B,
    PA_MIDICAPTAIN_MINI_SWITCH_C,
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
# HELPER FUNCTIONS FOR ACTION CREATION
##############################################################################

def cc_toggle(channel, cc, color, text):
    """Create a CC toggle action (on=127, off=0)."""
    return {
        "type": "custom",
        "mode": "toggle",
        "color": list(color),
        "text": text,
        "messages": [{"type": "cc", "channel": channel, "control": cc, "value": 127}],
        "messagesOff": [{"type": "cc", "channel": channel, "control": cc, "value": 0}]
    }

def cc_momentary(channel, cc, color, text):
    """Create a CC momentary action (127 on press, 0 on release)."""
    return {
        "type": "custom",
        "mode": "momentary",
        "color": list(color),
        "text": text,
        "messages": [{"type": "cc", "channel": channel, "control": cc, "value": 127}],
        "messagesOff": [{"type": "cc", "channel": channel, "control": cc, "value": 0}]
    }

def pc_select(channel, pc, color, text):
    """Create a Program Change action."""
    return {
        "type": "custom",
        "mode": "oneshot",
        "color": list(color),
        "text": text,
        "messages": [{"type": "pc", "channel": channel, "program": pc}],
        "messagesOff": []
    }

##############################################################################
# PAGE 1: LOGIC PRO X - DAW EFFECTS
##############################################################################

PAGE_LOGIC = {
    "name": "Logic",
    "channel": 1,
    "midi_out": "USB",
    "color_theme": COLOR_BLUE,
    "switches": [
        # Top Row
        {
            "assignment": PA_MIDICAPTAIN_MINI_SWITCH_1,
            "actions": [cc_toggle(1, 80, COLOR_BLUE, "Comp")]
        },
        {
            "assignment": PA_MIDICAPTAIN_MINI_SWITCH_2,
            "actions": [cc_toggle(1, 81, COLOR_CYAN, "EQ")]
        },
        {
            "assignment": PA_MIDICAPTAIN_MINI_SWITCH_3,
            "actions": [cc_toggle(1, 82, COLOR_GREEN, "Delay")]
        },
        # Bottom Row
        {
            "assignment": PA_MIDICAPTAIN_MINI_SWITCH_A,
            "actions": [cc_toggle(1, 83, COLOR_PURPLE, "Reverb")]
        },
        {
            "assignment": PA_MIDICAPTAIN_MINI_SWITCH_B,
            "actions": [cc_toggle(1, 84, COLOR_PINK, "Chorus")]
        },
        {
            "assignment": PA_MIDICAPTAIN_MINI_SWITCH_C,
            "actions": [cc_momentary(1, 85, COLOR_WHITE, "Tap")]
        },
    ]
}

##############################################################################
# PAGE 2: TONEX ONE (via USB MIDI to Builty ESP32 Controller)
##############################################################################

PAGE_TONEX = {
    "name": "ToneX",
    "channel": 2,
    "midi_out": "USB",
    "color_theme": COLOR_RED,
    "switches": [
        # Top row: Preset selection (Program Change)
        {
            "assignment": PA_MIDICAPTAIN_MINI_SWITCH_1,
            "actions": [pc_select(2, 0, COLOR_GREEN, "Clean")]
        },
        {
            "assignment": PA_MIDICAPTAIN_MINI_SWITCH_2,
            "actions": [pc_select(2, 1, COLOR_ORANGE, "Crunch")]
        },
        {
            "assignment": PA_MIDICAPTAIN_MINI_SWITCH_3,
            "actions": [pc_select(2, 2, COLOR_RED, "Lead")]
        },
        # Bottom row: Effect toggles
        {
            "assignment": PA_MIDICAPTAIN_MINI_SWITCH_A,
            "actions": [cc_toggle(2, 50, COLOR_BLUE, "Mod")]
        },
        {
            "assignment": PA_MIDICAPTAIN_MINI_SWITCH_B,
            "actions": [cc_toggle(2, 51, COLOR_CYAN, "Delay")]
        },
        {
            "assignment": PA_MIDICAPTAIN_MINI_SWITCH_C,
            "actions": [cc_toggle(2, 52, COLOR_PURPLE, "Reverb")]
        },
    ]
}

##############################################################################
# PAGE 3: VALETON GP-5 (via 5-pin DIN MIDI)
##############################################################################

PAGE_GP5 = {
    "name": "GP-5",
    "channel": 3,
    "midi_out": "DIN",  # GP-5 uses 5-pin DIN MIDI
    "color_theme": COLOR_GREEN,
    "switches": [
        # Top row: Preset selection
        {
            "assignment": PA_MIDICAPTAIN_MINI_SWITCH_1,
            "actions": [pc_select(3, 0, COLOR_GREEN, "Preset1")]
        },
        {
            "assignment": PA_MIDICAPTAIN_MINI_SWITCH_2,
            "actions": [pc_select(3, 1, COLOR_GREEN, "Preset2")]
        },
        {
            "assignment": PA_MIDICAPTAIN_MINI_SWITCH_3,
            "actions": [pc_select(3, 2, COLOR_GREEN, "Preset3")]
        },
        # Bottom row: Effect toggles (check GP-5 MIDI CC implementation)
        {
            "assignment": PA_MIDICAPTAIN_MINI_SWITCH_A,
            "actions": [cc_toggle(3, 19, COLOR_ORANGE, "FX1")]
        },
        {
            "assignment": PA_MIDICAPTAIN_MINI_SWITCH_B,
            "actions": [cc_toggle(3, 20, COLOR_CYAN, "FX2")]
        },
        {
            "assignment": PA_MIDICAPTAIN_MINI_SWITCH_C,
            "actions": [cc_toggle(3, 21, COLOR_PURPLE, "FX3")]
        },
    ]
}

##############################################################################
# PAGE 4: LOOPER CONTROLS
##############################################################################

PAGE_LOOPER = {
    "name": "Looper",
    "channel": 4,
    "midi_out": "USB",
    "color_theme": COLOR_PURPLE,
    "switches": [
        # Top row: Record, Play, Stop
        {
            "assignment": PA_MIDICAPTAIN_MINI_SWITCH_1,
            "actions": [cc_momentary(4, 60, COLOR_RED, "REC")]
        },
        {
            "assignment": PA_MIDICAPTAIN_MINI_SWITCH_2,
            "actions": [cc_momentary(4, 61, COLOR_GREEN, "PLAY")]
        },
        {
            "assignment": PA_MIDICAPTAIN_MINI_SWITCH_3,
            "actions": [cc_momentary(4, 62, COLOR_YELLOW, "STOP")]
        },
        # Bottom row: Undo, Half-speed, Clear
        {
            "assignment": PA_MIDICAPTAIN_MINI_SWITCH_A,
            "actions": [cc_momentary(4, 63, COLOR_ORANGE, "UNDO")]
        },
        {
            "assignment": PA_MIDICAPTAIN_MINI_SWITCH_B,
            "actions": [cc_toggle(4, 64, COLOR_CYAN, "1/2SPD")]
        },
        {
            "assignment": PA_MIDICAPTAIN_MINI_SWITCH_C,
            "actions": [cc_momentary(4, 65, COLOR_WHITE, "CLEAR")]
        },
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
    "combo_switches": ['A', 'B', 'C'],  # Which switches participate in combos
    "combo_window_ms": 50,               # Time window for simultaneous detection
}

##############################################################################
# INITIAL SWITCHES (First page loaded at startup)
# This is what PySwitch expects as the 'Switches' variable
##############################################################################

Switches = PAGE_LOGIC["switches"]

##############################################################################
# GLOBAL CONFIGURATION
##############################################################################

Config = {
    "updateInterval": 200,
    "maxConsecutiveMidiMessages": 10,
    "debugStats": False,
    "comboDetection": ComboConfig,
}
