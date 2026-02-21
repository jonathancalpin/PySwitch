##############################################################################
#
# code.py for Multi-Page MIDI Controller
# MIDI Captain Mini 6 with PySwitch
#
# This is a modified code.py that uses the MultiPageController
# with combo detection for page navigation.
#
# To use:
# 1. Copy your custom lib/pyswitch/controller/ files to the device
# 2. Copy this file as 'code.py' to the device root
# 3. Copy your inputs.py (e.g., inputs_multidevice.py renamed) to device root
#
##############################################################################

# Import the multi-page controller instead of standard controller
from pyswitch.controller.controller_multipage import MultiPageController

# Import your input configuration
from inputs import Switches, Pages, Config

# Import display configuration (create a display.py or use empty list)
try:
    from display import Displays
except ImportError:
    Displays = []

# Import communication settings
try:
    from communication import Communication
except ImportError:
    Communication = {}

# Hardware imports
from pyswitch.hardware.adafruit import AdafruitNeoPixelDriver, AdafruitMidi

##############################################################################
# HARDWARE INITIALIZATION
##############################################################################

# LED driver for NeoPixels
led_driver = AdafruitNeoPixelDriver()

# MIDI handler
midi = AdafruitMidi()

# Optional: User interface (display)
ui = None
try:
    from pyswitch.ui import UserInterface
    if Displays:
        ui = UserInterface(Displays)
except ImportError:
    pass

##############################################################################
# CREATE MULTI-PAGE CONTROLLER
##############################################################################

controller = MultiPageController(
    led_driver=led_driver,
    midi=midi,
    config=Config,
    inputs=Switches,    # Initial switch configuration (first page)
    pages=Pages,        # All page definitions for page switching
    ui=ui
)

##############################################################################
# MAIN LOOP
##############################################################################

# Initialize
controller.init()

# Run forever
while True:
    controller.tick()
