##############################################################################################################################################
#
# Generic MIDI - USB only. No bidirectional protocol.
# For MIDI Captain Mini 6 multi-page controller.
#
##############################################################################################################################################

from pyswitch.controller.midi import MidiRouting
from pyswitch.hardware.devices.pa_midicaptain import PA_MIDICAPTAIN_USB_MIDI

_USB_MIDI = PA_MIDICAPTAIN_USB_MIDI(in_channel=None, out_channel=0)

Communication = {
    "protocol": None,
    "midi": {
        "routings": [
            MidiRouting(source=_USB_MIDI, target=MidiRouting.APPLICATION),
            MidiRouting(source=MidiRouting.APPLICATION, target=_USB_MIDI),
        ]
    }
}
