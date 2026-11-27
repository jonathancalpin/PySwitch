##############################################################################
#
# MIDI Communication Configuration
# MIDI Captain Mini 6 - USB and DIN MIDI, Ampz feedback protocol
#
##############################################################################

from pyswitch.controller.midi import MidiRouting
from pyswitch.hardware.devices.pa_midicaptain import (
    PA_MIDICAPTAIN_USB_MIDI,
    PA_MIDICAPTAIN_DIN_MIDI
)
from pyswitch.clients.ampz.protocol import AmpzProtocol

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
    },
    # Asks Ampz for a full state dump at boot (and every 3 s until Ampz answers).
    "protocol": AmpzProtocol()
}
