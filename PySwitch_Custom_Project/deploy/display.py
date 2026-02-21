##############################################################################
#
# Display Configuration for MIDI Captain Mini 6
# Multi-Page Controller with Page Name Display
#
# Layout (240x135 display): 6 effect blocks only; center free for overlay later
#   ┌────────┬────────┬────────┐
#   │Header 1│Header 2│Header 3│  <- Top row buttons (1, 2, 3)
#   ├────────┴────────┴────────┤
#   │Footer 1│Footer 2│Footer 3│  <- Bottom row buttons (A, B, C)
#   └────────┴────────┴────────┘
#
##############################################################################

from micropython import const
from pyswitch.colors import DEFAULT_LABEL_COLOR
from pyswitch.ui.ui import DisplayElement, DisplayBounds
from pyswitch.ui.elements import DisplayLabel
from pyswitch.clients.local.callbacks.splashes import SplashesCallback

##############################################################################
# DISPLAY DIMENSIONS (6 equal squares: 3 cols x 2 rows, 240x240)
##############################################################################

_DISPLAY_WIDTH = const(240)
_DISPLAY_HEIGHT = const(240)

_SLOT_WIDTH = const(80)           # 240 / 3
_SLOT_HEIGHT_ROW0 = const(120)    # top row (120 + 120 = 240)
_SLOT_HEIGHT_ROW1 = const(120)    # bottom row
_FOOTER_Y = const(120)             # second row start (A, B, C)

##############################################################################
# LABEL STYLING (smaller font + wrap so text fits; backColor for dim/bright on toggle)
##############################################################################

_ACTION_LABEL_LAYOUT = {
    "font": "/fonts/PT40.pcf",
    "backColor": DEFAULT_LABEL_COLOR,
    "stroke": 1,
    "maxTextWidth": 76,
    "lineSpacing": 0.8,
}

##############################################################################
# HEADER ROW (Top buttons: 1, 2, 3)
##############################################################################

DISPLAY_HEADER_1 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT,
    bounds = DisplayBounds(0, 0, _SLOT_WIDTH, _SLOT_HEIGHT_ROW0)
)

DISPLAY_HEADER_2 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT,
    bounds = DisplayBounds(_SLOT_WIDTH, 0, _SLOT_WIDTH, _SLOT_HEIGHT_ROW0)
)

DISPLAY_HEADER_3 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT,
    bounds = DisplayBounds(_SLOT_WIDTH * 2, 0, _SLOT_WIDTH, _SLOT_HEIGHT_ROW0)
)

##############################################################################
# FOOTER ROW (Bottom buttons: A, B, C)
##############################################################################

DISPLAY_FOOTER_1 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT,
    bounds = DisplayBounds(0, _FOOTER_Y, _SLOT_WIDTH, _SLOT_HEIGHT_ROW1)
)

DISPLAY_FOOTER_2 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT,
    bounds = DisplayBounds(_SLOT_WIDTH, _FOOTER_Y, _SLOT_WIDTH, _SLOT_HEIGHT_ROW1)
)

DISPLAY_FOOTER_3 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT,
    bounds = DisplayBounds(_SLOT_WIDTH * 2, _FOOTER_Y, _SLOT_WIDTH, _SLOT_HEIGHT_ROW1)
)

##############################################################################
# SPLASH CONFIGURATION (6 effect blocks only; center free for overlay later)
##############################################################################

_SPLASH_ELEMENT = DisplayElement(
    bounds = DisplayBounds(0, 0, _DISPLAY_WIDTH, _DISPLAY_HEIGHT),
    children = [
        DISPLAY_HEADER_1,
        DISPLAY_HEADER_2,
        DISPLAY_HEADER_3,
        DISPLAY_FOOTER_1,
        DISPLAY_FOOTER_2,
        DISPLAY_FOOTER_3,
    ]
)

# Wrap in callback (required by UiController)
Splashes = SplashesCallback(_SPLASH_ELEMENT)
