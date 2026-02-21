##############################################################################
#
# Display Configuration for MIDI Captain Mini 6
# Web Configurator Compatible
#
##############################################################################

from micropython import const
from pyswitch.colors import DEFAULT_LABEL_COLOR
from pyswitch.ui.ui import DisplayElement, DisplayBounds
from pyswitch.ui.elements import DisplayLabel
from pyswitch.clients.local.callbacks.splashes import SplashesCallback

##############################################################################
# DISPLAY DIMENSIONS (6 equal squares; full screen 240x240)
##############################################################################

_DISPLAY_WIDTH = const(240)
_DISPLAY_HEIGHT = const(240)
_SLOT_WIDTH = const(80)           # 240 / 3
_SLOT_HEIGHT_ROW0 = const(120)    # top row (120 + 120 = 240)
_SLOT_HEIGHT_ROW1 = const(120)    # bottom row
_FOOTER_Y = const(120)            # second row start (buttons A, B, C)

##############################################################################
# LABEL STYLING (PT40; backColor for dim/bright; maxTextWidth = multi-line)
##############################################################################

_ACTION_LABEL_LAYOUT = {
    "font": "/fonts/PT40.pcf",
    "backColor": DEFAULT_LABEL_COLOR,
    "stroke": 1,
    "maxTextWidth": 76,
    "lineSpacing": 0.8,
}  # 80x120 slots: PT40 + wrap fits

##############################################################################
# DISPLAY ELEMENTS (6 effect blocks; center free for overlay later)
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

Splashes = SplashesCallback(_SPLASH_ELEMENT)
