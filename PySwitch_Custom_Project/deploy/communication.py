##############################################################################
#
# MIDI Communication Configuration
# MIDI Captain Mini 6 - Multi-Device Controller
#
# Supports both USB MIDI and DIN (5-pin) MIDI output
# Routes application messages to both outputs
#
##############################################################################

from pyswitch.controller.midi import MidiRouting
from pyswitch.hardware.devices.pa_midicaptain import (
    PA_MIDICAPTAIN_USB_MIDI,
    PA_MIDICAPTAIN_DIN_MIDI
)

##############################################################################
# MIDI DEVICE CONFIGURATION
##############################################################################

# USB MIDI - For Logic Pro, ToneX, Looper (pages 1, 2, 4)
# Note: out_channel=0 means channel 1 (0-indexed), but messages can override
_USB_MIDI = PA_MIDICAPTAIN_USB_MIDI(
    in_channel = None,      # Receive on all channels
    out_channel = 0         # Default to channel 1 (0-indexed)
)

# DIN MIDI (5-pin) - For GP-5 (page 3)
_DIN_MIDI = PA_MIDICAPTAIN_DIN_MIDI(
    out_channel = 0         # Default to channel 1 (0-indexed)
)

##############################################################################
# COMMUNICATION CONFIGURATION
##############################################################################

Communication = {

    # No bidirectional protocol for generic MIDI
    # (Remove or comment out for Kemper: "protocol": KemperBidirectionalProtocol())
    
    # MIDI Routing Configuration
    "midi": {
        "routings": [
            # ============================================================
            # USB MIDI ROUTING
            # ============================================================
            
            # Receive MIDI from USB (for bidirectional feedback)
            MidiRouting(
                source = _USB_MIDI,
                target = MidiRouting.APPLICATION
            ),
            
            # Send MIDI to USB
            MidiRouting(
                source = MidiRouting.APPLICATION,
                target = _USB_MIDI
            ),
            
            # ============================================================
            # DIN MIDI ROUTING (5-pin output)
            # ============================================================
            
            # Send MIDI to DIN output (for GP-5, etc.)
            MidiRouting(
                source = MidiRouting.APPLICATION,
                target = _DIN_MIDI
            ),
            
            # ============================================================
            # MIDI THROUGH (Optional - uncomment if needed)
            # ============================================================
            
            # USB to DIN through
            # MidiRouting(
            #     source = _USB_MIDI,
            #     target = _DIN_MIDI
            # ),
            
            # DIN to USB through
            # MidiRouting(
            #     source = _DIN_MIDI,
            #     target = _USB_MIDI
            # ),
        ]
    }
}
