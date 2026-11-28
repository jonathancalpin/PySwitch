##############################################################################
#
# MIDI Communication Configuration
# MIDI Captain Mini 6 - USB and DIN MIDI both ways, Ampz feedback protocol
#
##############################################################################

from pyswitch.controller.midi import MidiRouting
from pyswitch.hardware.devices.pa_midicaptain import (
    PA_MIDICAPTAIN_USB_MIDI,
    PA_MIDICAPTAIN_DIN_MIDI
)
from pyswitch.clients.ampz.protocol import AmpzProtocol
from pyswitch.clients.ampz.sysex_repair import SysExRepairInput

# USB MIDI
_USB_MIDI = PA_MIDICAPTAIN_USB_MIDI(
    in_channel = None,
    out_channel = 0
)

# DIN MIDI (5-pin)
# in_filter: a Bluetooth DIN adapter eats the F0 of two Ampz frames in three; the repair puts it back.
_DIN_MIDI = PA_MIDICAPTAIN_DIN_MIDI(
    out_channel = 0,
    in_filter = SysExRepairInput
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
            # Ampz's feedback can arrive on the MIDI IN jack too (a Bluetooth DIN adapter, for example).
            MidiRouting(
                source = _DIN_MIDI,
                target = MidiRouting.APPLICATION
            ),
        ]
    },
    # Asks Ampz for a full state dump at boot (and every 3 s until Ampz answers).
    "protocol": AmpzProtocol()
}
