##############################################################################
#
# Display Configuration for MIDI Captain Mini 6
# Web Configurator Compatible
#
##############################################################################

from pyswitch.clients.local.callbacks.splashes import SplashesCallback
from micropython import const
from pyswitch.colors import DEFAULT_LABEL_COLOR
from pyswitch.ui.ui import DisplayElement
from pyswitch.ui.ui import DisplayBounds
from pyswitch.ui.elements import DisplayLabel

##############################################################################
# DISPLAY DIMENSIONS (6 equal squares; full screen 240x240)
##############################################################################

_DISPLAY_WIDTH = const(
    240
)
_DISPLAY_HEIGHT = const(
    240
)
_SLOT_WIDTH = const(
    80
)           # 240 / 3
_SLOT_HEIGHT_ROW0 = const(
    120
)    # top row (120 + 120 = 240)
_SLOT_HEIGHT_ROW1 = const(
    120
)    # bottom row
_FOOTER_Y = const(
    120
)            # second row start (buttons A, B, C)

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
    bounds = DisplayBounds(
        x = 0, 
        y = 0, 
        w = _SLOT_WIDTH, 
        h = _SLOT_HEIGHT_ROW0
    )
)

DISPLAY_HEADER_2 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT, 
    bounds = DisplayBounds(
        x = _SLOT_WIDTH, 
        y = 0, 
        w = _SLOT_WIDTH, 
        h = _SLOT_HEIGHT_ROW0
    )
)

DISPLAY_HEADER_3 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT, 
    bounds = DisplayBounds(
        x = _SLOT_WIDTH * 2, 
        y = 0, 
        w = _SLOT_WIDTH, 
        h = _SLOT_HEIGHT_ROW0
    )
)

DISPLAY_FOOTER_1 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT, 
    bounds = DisplayBounds(
        x = 0, 
        y = _FOOTER_Y, 
        w = _SLOT_WIDTH, 
        h = _SLOT_HEIGHT_ROW1
    )
)

DISPLAY_FOOTER_2 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT, 
    bounds = DisplayBounds(
        x = _SLOT_WIDTH, 
        y = _FOOTER_Y, 
        w = _SLOT_WIDTH, 
        h = _SLOT_HEIGHT_ROW1
    )
)

DISPLAY_FOOTER_3 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT, 
    bounds = DisplayBounds(
        x = _SLOT_WIDTH * 2, 
        y = _FOOTER_Y, 
        w = _SLOT_WIDTH, 
        h = _SLOT_HEIGHT_ROW1
    )
)

##############################################################################
# SPLASH CONFIGURATION (6 effect blocks only; center free for overlay later)
##############################################################################

_SPLASH_ELEMENT = DisplayElement(
    bounds = DisplayBounds(
        x = 0, 
        y = 0, 
        w = _DISPLAY_WIDTH, 
        h = _DISPLAY_HEIGHT
    ), 
    children = [
        DISPLAY_HEADER_1,
        DISPLAY_HEADER_2,
        DISPLAY_HEADER_3,
        DISPLAY_FOOTER_1,
        DISPLAY_FOOTER_2,
        DISPLAY_FOOTER_3,
        
    ]
)

Splashes = SplashesCallback(
    _SPLASH_ELEMENT
)
