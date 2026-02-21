##############################################################################
#
# MVP Display - MIDI Captain Mini 6
# 3x2 layout (6 blocks), 240x240, color per switch, toggle dim/bright
#
##############################################################################

from micropython import const
from pyswitch.colors import DEFAULT_LABEL_COLOR
from pyswitch.ui.ui import DisplayElement, DisplayBounds
from pyswitch.ui.elements import DisplayLabel
from pyswitch.clients.local.callbacks.splashes import SplashesCallback

_DISPLAY_WIDTH = const(240)
_DISPLAY_HEIGHT = const(240)
_SLOT_WIDTH = const(80)
_SLOT_HEIGHT = const(120)
_FOOTER_Y = const(120)

_ACTION_LABEL_LAYOUT = {
    "font": "/fonts/PT40.pcf",
    "backColor": DEFAULT_LABEL_COLOR,
    "stroke": 1,
    "maxTextWidth": 76,
}

DISPLAY_HEADER_1 = DisplayLabel(
    layout=_ACTION_LABEL_LAYOUT,
    bounds=DisplayBounds(0, 0, _SLOT_WIDTH, _SLOT_HEIGHT)
)
DISPLAY_HEADER_2 = DisplayLabel(
    layout=_ACTION_LABEL_LAYOUT,
    bounds=DisplayBounds(_SLOT_WIDTH, 0, _SLOT_WIDTH, _SLOT_HEIGHT)
)
DISPLAY_HEADER_3 = DisplayLabel(
    layout=_ACTION_LABEL_LAYOUT,
    bounds=DisplayBounds(_SLOT_WIDTH * 2, 0, _SLOT_WIDTH, _SLOT_HEIGHT)
)
DISPLAY_FOOTER_1 = DisplayLabel(
    layout=_ACTION_LABEL_LAYOUT,
    bounds=DisplayBounds(0, _FOOTER_Y, _SLOT_WIDTH, _SLOT_HEIGHT)
)
DISPLAY_FOOTER_2 = DisplayLabel(
    layout=_ACTION_LABEL_LAYOUT,
    bounds=DisplayBounds(_SLOT_WIDTH, _FOOTER_Y, _SLOT_WIDTH, _SLOT_HEIGHT)
)
DISPLAY_FOOTER_3 = DisplayLabel(
    layout=_ACTION_LABEL_LAYOUT,
    bounds=DisplayBounds(_SLOT_WIDTH * 2, _FOOTER_Y, _SLOT_WIDTH, _SLOT_HEIGHT)
)

Splashes = SplashesCallback(
    DisplayElement(
        bounds=DisplayBounds(0, 0, _DISPLAY_WIDTH, _DISPLAY_HEIGHT),
        children=[
            DISPLAY_HEADER_1,
            DISPLAY_HEADER_2,
            DISPLAY_HEADER_3,
            DISPLAY_FOOTER_1,
            DISPLAY_FOOTER_2,
            DISPLAY_FOOTER_3,
        ]
    )
)
