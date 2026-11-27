##############################################################################
#
# Display Configuration for MIDI Captain Mini 6 (Ampz feedback)
#
# A 24 px header strip across the top shows the preset name Ampz sends; the six switch
# labels below it are 80 x 108 and are written by the switch actions (text and colour come
# from Ampz for stomps, fixed for the looper and utility switches).
#
##############################################################################

from pyswitch.clients.local.callbacks.splashes import SplashesCallback
from pyswitch.clients.ampz.actions import AmpzPresetNameCallback
from micropython import const
from pyswitch.colors import DEFAULT_LABEL_COLOR
from pyswitch.ui.ui import DisplayElement
from pyswitch.ui.ui import DisplayBounds
from pyswitch.ui.elements import DisplayLabel

##############################################################################
# DISPLAY DIMENSIONS (header strip + 6 blocks; full screen 240x240)
##############################################################################

_DISPLAY_WIDTH = const(240)
_DISPLAY_HEIGHT = const(240)
_HEADER_HEIGHT = const(24)
_SLOT_WIDTH = const(80)            # 240 / 3
_SLOT_HEIGHT = const(108)          # (240 - 24) / 2
_ROW0_Y = const(24)                # top row (switches 1, 2, 3)
_ROW1_Y = const(132)               # bottom row (switches A, B, C)

##############################################################################
# LABEL STYLING
##############################################################################

_ACTION_LABEL_LAYOUT = {
    "font": "/fonts/PT40.pcf",
    "backColor": DEFAULT_LABEL_COLOR,
    "stroke": 1,
    "maxTextWidth": 76,
    "lineSpacing": 0.8,
}

_HEADER_LAYOUT = {
    "font": "/fonts/H20.pcf",
    "backColor": (20, 20, 20),
    "stroke": 0,
    "maxTextWidth": 236,
}

##############################################################################
# DISPLAY ELEMENTS
##############################################################################

DISPLAY_PRESET = DisplayLabel(
    layout = _HEADER_LAYOUT,
    bounds = DisplayBounds(x = 0, y = 0, w = _DISPLAY_WIDTH, h = _HEADER_HEIGHT),
    callback = AmpzPresetNameCallback()
)

DISPLAY_HEADER_1 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT,
    bounds = DisplayBounds(x = 0, y = _ROW0_Y, w = _SLOT_WIDTH, h = _SLOT_HEIGHT)
)

DISPLAY_HEADER_2 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT,
    bounds = DisplayBounds(x = _SLOT_WIDTH, y = _ROW0_Y, w = _SLOT_WIDTH, h = _SLOT_HEIGHT)
)

DISPLAY_HEADER_3 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT,
    bounds = DisplayBounds(x = _SLOT_WIDTH * 2, y = _ROW0_Y, w = _SLOT_WIDTH, h = _SLOT_HEIGHT)
)

DISPLAY_FOOTER_1 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT,
    bounds = DisplayBounds(x = 0, y = _ROW1_Y, w = _SLOT_WIDTH, h = _SLOT_HEIGHT)
)

DISPLAY_FOOTER_2 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT,
    bounds = DisplayBounds(x = _SLOT_WIDTH, y = _ROW1_Y, w = _SLOT_WIDTH, h = _SLOT_HEIGHT)
)

DISPLAY_FOOTER_3 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT,
    bounds = DisplayBounds(x = _SLOT_WIDTH * 2, y = _ROW1_Y, w = _SLOT_WIDTH, h = _SLOT_HEIGHT)
)

##############################################################################
# SPLASH CONFIGURATION
##############################################################################

_SPLASH_ELEMENT = DisplayElement(
    bounds = DisplayBounds(x = 0, y = 0, w = _DISPLAY_WIDTH, h = _DISPLAY_HEIGHT),
    children = [
        DISPLAY_PRESET,
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
