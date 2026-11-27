##############################################################################
#
# MIDI Communication Configuration
# MIDI Captain Mini 6 - USB and DIN MIDI, both directions
#
# Switch presses go out on USB and on the MIDI out jack. Messages coming in on
# USB or the MIDI in jack reach the application, so the host (Ampz) can keep the
# stomp LEDs in sync over either connection (for example a Bluetooth MIDI
# adapter on the jacks). There is deliberately no routing from one port straight
# to another: MIDI thru would echo the host's messages back to it.
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

# DIN MIDI (TRS jacks on the Mini 6)
_DIN_MIDI = PA_MIDICAPTAIN_DIN_MIDI(
    in_channel = None,
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
                source = _DIN_MIDI,
                target = MidiRouting.APPLICATION
            ),
            MidiRouting(
                source = MidiRouting.APPLICATION,
                target = _DIN_MIDI
            ),
        ]
    }
}
