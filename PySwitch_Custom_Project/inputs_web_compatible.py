##############################################################################
#
# Multi-Page MIDI Controller with Combo Navigation
# MIDI Captain Mini 6
#
# Page Navigation:
#   A+B pressed together = Previous Page
#   B+C pressed together = Next Page
#
# Pages:
#   1. Logic Pro X (Channel 1) - Blue
#   2. ToneX (Channel 2) - Red
#   3. GP-5 (Channel 3) - Green
#   4. Looper (Channel 4) - Purple
#
# Web Editor: Can edit CC/PC values, colors, and labels.
#             Page navigation: combo_pager (device) or PagerAction (web).
#             Toggle: built-in CUSTOM_MESSAGE(..., toggle=True).
#
##############################################################################

from pyswitch.hardware.devices.pa_midicaptain_mini_6 import *
from pyswitch.clients.local.actions.custom import CUSTOM_MESSAGE
from pyswitch.colors import Colors

# Import display elements
try:
    from display import (
        DISPLAY_HEADER_1, DISPLAY_HEADER_2, DISPLAY_HEADER_3,
        DISPLAY_FOOTER_1, DISPLAY_FOOTER_2, DISPLAY_FOOTER_3,
        DISPLAY_PAGE_NAME
    )
except ImportError:
    # Fallback for web editor
    DISPLAY_HEADER_1 = None
    DISPLAY_HEADER_2 = None
    DISPLAY_HEADER_3 = None
    DISPLAY_FOOTER_1 = None
    DISPLAY_FOOTER_2 = None
    DISPLAY_FOOTER_3 = None
    DISPLAY_PAGE_NAME = None

# Import combo pager (optional for web editor)
try:
    from combo_pager import ComboPager, ComboSwitchAction, ComboEnableCallback
    _COMBO_AVAILABLE = True
except ImportError:
    # Fallback: Use standard PagerAction for web editor
    from pyswitch.clients.local.actions.pager import PagerAction
    _COMBO_AVAILABLE = False

# CC actions use CUSTOM_MESSAGE(..., toggle=True) for latch - web editor can edit these

##############################################################################
# PAGE DEFINITIONS
##############################################################################

if _COMBO_AVAILABLE:
    _pager = ComboPager(
        pages = [
            {
                "id": "logic",
                "color": Colors.BLUE,
                "text": "Logic Pro X"
            },
            {
                "id": "tonex",
                "color": Colors.RED,
                "text": "ToneX"
            },
            {
                "id": "gp5",
                "color": Colors.GREEN,
                "text": "GP-5"
            },
            {
                "id": "looper",
                "color": Colors.PURPLE,
                "text": "Looper"
            },
        ],
        combo_window_ms = 80,
        led_brightness = 0.3
    )
    _enable_A = ComboEnableCallback(_pager, 'A')
    _enable_B = ComboEnableCallback(_pager, 'B')
    _enable_C = ComboEnableCallback(_pager, 'C')
else:
    # Fallback for web editor
    _pager = PagerAction(
        pages = [
            {"id": "logic", "color": Colors.BLUE, "text": "Logic Pro X"},
            {"id": "tonex", "color": Colors.RED, "text": "ToneX"},
            {"id": "gp5", "color": Colors.GREEN, "text": "GP-5"},
            {"id": "looper", "color": Colors.PURPLE, "text": "Looper"},
        ],
        led_brightness = 0.3
    )
    _enable_A = _pager.enable_callback
    _enable_B = _pager.enable_callback
    _enable_C = _pager.enable_callback

##############################################################################
# SWITCH DEFINITIONS
##############################################################################

Inputs = [
    # ========== SWITCH 1 (Top Left) ==========
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_1,
        "actions": [
            # Logic: CC#80 Compressor (Channel 1) - TOGGLE
            CUSTOM_MESSAGE(
                message = [0xB0, 80, 127],
                message_release = [0xB0, 80, 0],
                color = Colors.BLUE,
                text = "Comp",
                display = DISPLAY_HEADER_1,
                id = "logic",
                enable_callback = _pager.enable_callback,
                toggle = True
            ),
            # ToneX: PC#0 Clean (Channel 2)
            CUSTOM_MESSAGE(
                message = [0xC1, 0],
                message_release = None,
                color = Colors.GREEN,
                text = "Clean",
                display = DISPLAY_HEADER_1,
                id = "tonex",
                enable_callback = _pager.enable_callback
            ),
            # GP-5: PC#0 Preset 1 (Channel 3)
            CUSTOM_MESSAGE(
                message = [0xC2, 0],
                message_release = None,
                color = Colors.GREEN,
                text = "Pst1",
                display = DISPLAY_HEADER_1,
                id = "gp5",
                enable_callback = _pager.enable_callback
            ),
            # Looper: CC#60 Record (Channel 4) - TOGGLE
            CUSTOM_MESSAGE(
                message = [0xB3, 60, 127],
                message_release = [0xB3, 60, 0],
                color = Colors.RED,
                text = "REC",
                display = DISPLAY_HEADER_1,
                id = "looper",
                enable_callback = _pager.enable_callback,
                toggle = True
            ),
        ]
    },

    # ========== SWITCH 2 (Top Center) ==========
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_2,
        "actions": [
            # Logic: CC#81 EQ (Channel 1) - TOGGLE
            CUSTOM_MESSAGE(
                message = [0xB0, 81, 127],
                message_release = [0xB0, 81, 0],
                color = Colors.TURQUOISE,
                text = "EQ",
                display = DISPLAY_HEADER_2,
                id = "logic",
                enable_callback = _pager.enable_callback,
                toggle = True
            ),
            # ToneX: PC#1 Crunch (Channel 2)
            CUSTOM_MESSAGE(
                message = [0xC1, 1],
                message_release = None,
                color = Colors.ORANGE,
                text = "Crunch",
                display = DISPLAY_HEADER_2,
                id = "tonex",
                enable_callback = _pager.enable_callback
            ),
            # GP-5: PC#1 Preset 2 (Channel 3)
            CUSTOM_MESSAGE(
                message = [0xC2, 1],
                message_release = None,
                color = Colors.GREEN,
                text = "Pst2",
                display = DISPLAY_HEADER_2,
                id = "gp5",
                enable_callback = _pager.enable_callback
            ),
            # Looper: CC#61 Play (Channel 4) - TOGGLE
            CUSTOM_MESSAGE(
                message = [0xB3, 61, 127],
                message_release = [0xB3, 61, 0],
                color = Colors.GREEN,
                text = "PLAY",
                display = DISPLAY_HEADER_2,
                id = "looper",
                enable_callback = _pager.enable_callback,
                toggle = True
            ),
        ]
    },

    # ========== SWITCH 3 (Top Right) ==========
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_3,
        "actions": [
            # Logic: CC#82 Delay (Channel 1) - TOGGLE
            CUSTOM_MESSAGE(
                message = [0xB0, 82, 127],
                message_release = [0xB0, 82, 0],
                color = Colors.GREEN,
                text = "Delay",
                display = DISPLAY_HEADER_3,
                id = "logic",
                enable_callback = _pager.enable_callback,
                toggle = True
            ),
            # ToneX: PC#2 Lead (Channel 2)
            CUSTOM_MESSAGE(
                message = [0xC1, 2],
                message_release = None,
                color = Colors.RED,
                text = "Lead",
                display = DISPLAY_HEADER_3,
                id = "tonex",
                enable_callback = _pager.enable_callback
            ),
            # GP-5: PC#2 Preset 3 (Channel 3)
            CUSTOM_MESSAGE(
                message = [0xC2, 2],
                message_release = None,
                color = Colors.GREEN,
                text = "Pst3",
                display = DISPLAY_HEADER_3,
                id = "gp5",
                enable_callback = _pager.enable_callback
            ),
            # Looper: CC#62 Stop (Channel 4) - TOGGLE
            CUSTOM_MESSAGE(
                message = [0xB3, 62, 127],
                message_release = [0xB3, 62, 0],
                color = Colors.YELLOW,
                text = "STOP",
                display = DISPLAY_HEADER_3,
                id = "looper",
                enable_callback = _pager.enable_callback,
                toggle = True
            ),
        ]
    },

    # ========== SWITCH A (Bottom Left) - Part of A+B combo ==========
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_A,
        "actions": (
            # Combo detector - only if available
            ([ComboSwitchAction(_pager, 'A')] if _COMBO_AVAILABLE else []) +
            [
            # Logic: CC#83 Reverb (Channel 1) - TOGGLE
            CUSTOM_MESSAGE(
                message = [0xB0, 83, 127],
                message_release = [0xB0, 83, 0],
                color = Colors.PURPLE,
                text = "Reverb",
                display = DISPLAY_FOOTER_1,
                id = "logic",
                enable_callback = _enable_A,
                toggle = True
            ),
            # ToneX: CC#50 Mod (Channel 2) - TOGGLE
            CUSTOM_MESSAGE(
                message = [0xB1, 50, 127],
                message_release = [0xB1, 50, 0],
                color = Colors.BLUE,
                text = "Mod",
                display = DISPLAY_FOOTER_1,
                id = "tonex",
                enable_callback = _enable_A,
                toggle = True
            ),
            # GP-5: CC#19 FX1 (Channel 3) - TOGGLE
            CUSTOM_MESSAGE(
                message = [0xB2, 19, 127],
                message_release = [0xB2, 19, 0],
                color = Colors.ORANGE,
                text = "FX1",
                display = DISPLAY_FOOTER_1,
                id = "gp5",
                enable_callback = _enable_A,
                toggle = True
            ),
            # Looper: CC#63 Undo (Channel 4) - TOGGLE
            CUSTOM_MESSAGE(
                message = [0xB3, 63, 127],
                message_release = [0xB3, 63, 0],
                color = Colors.ORANGE,
                text = "UNDO",
                display = DISPLAY_FOOTER_1,
                id = "looper",
                enable_callback = _enable_A,
                toggle = True
            ),
        ])
    },

    # ========== SWITCH B (Bottom Center) - Part of A+B and B+C combos ==========
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_B,
        "actions": (
            # PagerAction (fallback) or Combo detector - ensures pager is inited so display/LEDs sync in emulator
            ([_pager] if not _COMBO_AVAILABLE else [ComboSwitchAction(_pager, 'B')]) +
            [
            # Logic: CC#84 Chorus (Channel 1) - TOGGLE
            CUSTOM_MESSAGE(
                message = [0xB0, 84, 127],
                message_release = [0xB0, 84, 0],
                color = Colors.PINK,
                text = "Chorus",
                display = DISPLAY_FOOTER_2,
                id = "logic",
                enable_callback = _enable_B,
                toggle = True
            ),
            # ToneX: CC#51 Delay (Channel 2) - TOGGLE
            CUSTOM_MESSAGE(
                message = [0xB1, 51, 127],
                message_release = [0xB1, 51, 0],
                color = Colors.TURQUOISE,
                text = "Delay",
                display = DISPLAY_FOOTER_2,
                id = "tonex",
                enable_callback = _enable_B,
                toggle = True
            ),
            # GP-5: CC#20 FX2 (Channel 3) - TOGGLE
            CUSTOM_MESSAGE(
                message = [0xB2, 20, 127],
                message_release = [0xB2, 20, 0],
                color = Colors.TURQUOISE,
                text = "FX2",
                display = DISPLAY_FOOTER_2,
                id = "gp5",
                enable_callback = _enable_B,
                toggle = True
            ),
            # Looper: CC#64 Half Speed (Channel 4) - TOGGLE
            CUSTOM_MESSAGE(
                message = [0xB3, 64, 127],
                message_release = [0xB3, 64, 0],
                color = Colors.TURQUOISE,
                text = "1/2",
                display = DISPLAY_FOOTER_2,
                id = "looper",
                enable_callback = _enable_B,
                toggle = True
            ),
        ])
    },

    # ========== SWITCH C (Bottom Right) - Part of B+C combo ==========
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_C,
        "actions": (
            # Combo detector - only if available
            ([ComboSwitchAction(_pager, 'C')] if _COMBO_AVAILABLE else []) +
            [
            # Logic: CC#85 Tap Tempo (Channel 1) - TOGGLE
            CUSTOM_MESSAGE(
                message = [0xB0, 85, 127],
                message_release = [0xB0, 85, 0],
                color = Colors.WHITE,
                text = "Tap",
                display = DISPLAY_FOOTER_3,
                id = "logic",
                enable_callback = _enable_C,
                toggle = True
            ),
            # ToneX: CC#52 Reverb (Channel 2) - TOGGLE
            CUSTOM_MESSAGE(
                message = [0xB1, 52, 127],
                message_release = [0xB1, 52, 0],
                color = Colors.PURPLE,
                text = "Reverb",
                display = DISPLAY_FOOTER_3,
                id = "tonex",
                enable_callback = _enable_C,
                toggle = True
            ),
            # GP-5: CC#21 FX3 (Channel 3) - TOGGLE
            CUSTOM_MESSAGE(
                message = [0xB2, 21, 127],
                message_release = [0xB2, 21, 0],
                color = Colors.PURPLE,
                text = "FX3",
                display = DISPLAY_FOOTER_3,
                id = "gp5",
                enable_callback = _enable_C,
                toggle = True
            ),
            # Looper: CC#65 Clear (Channel 4) - TOGGLE
            CUSTOM_MESSAGE(
                message = [0xB3, 65, 127],
                message_release = [0xB3, 65, 0],
                color = Colors.WHITE,
                text = "CLR",
                display = DISPLAY_FOOTER_3,
                id = "looper",
                enable_callback = _enable_C,
                toggle = True
            ),
        ])
    },
]
