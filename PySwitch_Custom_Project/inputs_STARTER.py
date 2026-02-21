##############################################################################
#
# STARTER Configuration - Works with Stock PySwitch 2.4.8
# MIDI Captain Mini 6 - Generic MIDI CC Controller
#
# This is a simple working config to get you started while
# the custom combo/page features are being developed.
#
# Layout:
#   [1] CC#80   [2] CC#81   [3] CC#82
#   [A] CC#83   [B] CC#84   [C] CC#85
#
# All buttons: Channel 1, Toggle mode (press=ON, press again=OFF)
#
##############################################################################

# Correct import path (no '_6' suffix in constant names)
from pyswitch.hardware.devices.pa_midicaptain_mini_6 import (
    PA_MIDICAPTAIN_MINI_SWITCH_1,
    PA_MIDICAPTAIN_MINI_SWITCH_2,
    PA_MIDICAPTAIN_MINI_SWITCH_3,
    PA_MIDICAPTAIN_MINI_SWITCH_A,
    PA_MIDICAPTAIN_MINI_SWITCH_B,
    PA_MIDICAPTAIN_MINI_SWITCH_C,
)

##############################################################################
# SWITCH DEFINITIONS
##############################################################################

Switches = [
    # ==================== TOP ROW ====================
    
    # Button 1 - Red
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_1,
        "actions": [
            {
                "type": "custom",
                "mode": "toggle",
                "color": [255, 0, 0],
                "text": "FX 1",
                "messages": [
                    {"type": "cc", "channel": 1, "control": 80, "value": 127}
                ],
                "messagesOff": [
                    {"type": "cc", "channel": 1, "control": 80, "value": 0}
                ]
            }
        ]
    },

    # Button 2 - Orange
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_2,
        "actions": [
            {
                "type": "custom",
                "mode": "toggle",
                "color": [255, 128, 0],
                "text": "FX 2",
                "messages": [
                    {"type": "cc", "channel": 1, "control": 81, "value": 127}
                ],
                "messagesOff": [
                    {"type": "cc", "channel": 1, "control": 81, "value": 0}
                ]
            }
        ]
    },

    # Button 3 - Yellow
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_3,
        "actions": [
            {
                "type": "custom",
                "mode": "toggle",
                "color": [255, 255, 0],
                "text": "FX 3",
                "messages": [
                    {"type": "cc", "channel": 1, "control": 82, "value": 127}
                ],
                "messagesOff": [
                    {"type": "cc", "channel": 1, "control": 82, "value": 0}
                ]
            }
        ]
    },

    # ==================== BOTTOM ROW ====================
    
    # Button A - Green
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_A,
        "actions": [
            {
                "type": "custom",
                "mode": "toggle",
                "color": [0, 255, 0],
                "text": "FX 4",
                "messages": [
                    {"type": "cc", "channel": 1, "control": 83, "value": 127}
                ],
                "messagesOff": [
                    {"type": "cc", "channel": 1, "control": 83, "value": 0}
                ]
            }
        ]
    },

    # Button B - Blue
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_B,
        "actions": [
            {
                "type": "custom",
                "mode": "toggle",
                "color": [0, 128, 255],
                "text": "FX 5",
                "messages": [
                    {"type": "cc", "channel": 1, "control": 84, "value": 127}
                ],
                "messagesOff": [
                    {"type": "cc", "channel": 1, "control": 84, "value": 0}
                ]
            }
        ]
    },

    # Button C - Purple
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_C,
        "actions": [
            {
                "type": "custom",
                "mode": "toggle",
                "color": [128, 0, 255],
                "text": "FX 6",
                "messages": [
                    {"type": "cc", "channel": 1, "control": 85, "value": 127}
                ],
                "messagesOff": [
                    {"type": "cc", "channel": 1, "control": 85, "value": 0}
                ]
            }
        ]
    },
]
