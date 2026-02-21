================================================================================
PySwitch Multi-Page Firmware
MIDI Captain Mini 6
================================================================================

This folder contains the complete firmware ready to copy to your MIDI Captain.

FEATURES:
- Combo detection: A+B = Page Up, B+C = Page Down
- 4 pages: Logic Pro, ToneX, GP-5, Looper
- USB and DIN MIDI output
- Compatible with PySwitch web interface

================================================================================
INSTALLATION
================================================================================

1. Connect MIDI Captain while holding Button 1 (mounts as USB drive)

2. BACKUP your current files (optional but recommended)

3. Delete ALL files on the MIDICAPTAIN drive

4. Copy EVERYTHING from this folder to the MIDICAPTAIN drive:
   - boot.py
   - code.py
   - communication.py
   - config.py
   - display.py
   - inputs.py
   - fonts/ (entire folder)
   - lib/ (entire folder)

5. Safely eject the USB drive

6. Power cycle the MIDI Captain

================================================================================
TESTING
================================================================================

After installation:

1. The display should show "PySwitch" and the first page name "Logic"

2. Press A+B together (within 50ms) - should change to page 2 "ToneX"

3. Press B+C together - should go back to page 1 "Logic"

4. Individual buttons should send MIDI CC/PC messages

SERIAL CONSOLE (for debugging):
   Mac: screen /dev/tty.usbmodem* 115200
   Press Ctrl+A then K to exit screen

MIDI MONITOR:
   Use a MIDI monitor app to verify messages are being sent

================================================================================
PAGE CONFIGURATION
================================================================================

Page 1: Logic Pro X (USB MIDI, Channel 1)
  [1] CC#80 Comp    [2] CC#81 EQ     [3] CC#82 Delay
  [A] CC#83 Reverb  [B] CC#84 Chorus [C] CC#85 Tap

Page 2: ToneX (USB MIDI, Channel 2)
  [1] PC#0 Clean    [2] PC#1 Crunch  [3] PC#2 Lead
  [A] CC#50 Mod     [B] CC#51 Delay  [C] CC#52 Reverb

Page 3: GP-5 (DIN MIDI, Channel 3)
  [1] PC#0 Preset1  [2] PC#1 Preset2 [3] PC#2 Preset3
  [A] CC#19 FX1     [B] CC#20 FX2    [C] CC#21 FX3

Page 4: Looper (USB MIDI, Channel 4)
  [1] CC#60 REC     [2] CC#61 PLAY   [3] CC#62 STOP
  [A] CC#63 UNDO    [B] CC#64 1/2    [C] CC#65 CLR

================================================================================
CUSTOMIZATION
================================================================================

To modify pages or MIDI mappings, edit: inputs.py

To adjust combo timing, edit: config.py
  - combo_window_ms: Detection window in milliseconds (default: 50)

To change display layout, edit: display.py

To modify MIDI routing, edit: communication.py

================================================================================
WEB INTERFACE
================================================================================

This firmware is compatible with the PySwitch web interface:
https://pyswitch.tunetown.de/

Connect via USB MIDI and use the web app to modify configurations.

================================================================================
TROUBLESHOOTING
================================================================================

Problem: Device doesn't boot
Solution: Check serial console for errors, verify all files copied correctly

Problem: Combo detection too sensitive/not sensitive enough
Solution: Adjust combo_window_ms in config.py (try 30-100ms)

Problem: No MIDI output
Solution: Check communication.py routing, verify MIDI cables/connections

Problem: Display shows errors
Solution: Connect to serial console to see full error messages

================================================================================
RESOURCES
================================================================================

PySwitch GitHub: https://github.com/Tunetown/PySwitch
PySwitch Web: https://pyswitch.tunetown.de/

================================================================================
