##############################################################################
#
# MIDI Communication Configuration
# MIDI Captain Mini 6 - USB and DIN MIDI
#
##############################################################################

from pyswitch.controller.midi import MidiRouting
from pyswitch.hardware.devices.pa_midicaptain import (
    PA_MIDICAPTAIN_USB_MIDI,
    PA_MIDICAPTAIN_DIN_MIDI
)

# USB MIDI
_USB_MIDI = PA_MIDICAPTAIN_USB_MIDI(
    in_channel = None,
    out_channel = 0
)

# DIN MIDI (5-pin)
_DIN_MIDI = PA_MIDICAPTAIN_DIN_MIDI(
    out_channel = 0
)

Communication = {
    "midi": {
        "routings": [
            MidiRouting(
                source = _USB_MIDI,
                target = MidiRouting.APPLICATION
            ),
            MidiRouting(
                source = MidiRouting.APPLICATION,
                target = _USB_MIDI
            ),
            MidiRouting(
                source = MidiRouting.APPLICATION,
                target = _DIN_MIDI
            ),
        ]
    }
}
