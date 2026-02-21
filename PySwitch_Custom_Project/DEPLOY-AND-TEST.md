# Load update on device and test with emulator

## 1. Load the update on the device

1. **Put the MIDI Captain Mini 6 in USB storage mode**  
   (e.g. hold the button during plug-in, or use bootloader mode so the device appears as a drive.)

2. **Wait until the volume appears**  
   - macOS: Often `MIDICAPTAIN` or `CIRCUITPY` under `/Volumes/`.  
   - Check in Finder or run: `ls /Volumes/`

3. **Run the deploy script** from the project root:
   ```bash
   cd "/Volumes/Mini External/PySwitch-main/PySwitch_Custom_Project"
   ./deploy-to-device.sh
   ```
   If your volume has a different name:
   ```bash
   ./deploy-to-device.sh /Volumes/CIRCUITPY
   ```

4. **Eject the volume** (Finder: Eject, or `diskutil eject /Volumes/MIDICAPTAIN`).

5. **Unplug and replug the device** (or press reset) so it runs the new firmware.

---

## 2. What gets copied

| File | Purpose |
|------|--------|
| `display.py` | New layout: 6 effect blocks, full 240×135, no center “PySwitch 2.4.8”, PT40 font. |
| `lib/pyswitch/clients/local/actions/custom.py` | Toggle + dim effect block when off. |
| `lib/pyswitch/controller/actions/__init__.py` | `update_displays()` after push; per-segment brightness. |
| `fonts/PT40.pcf` | Font used by the new display (if missing on device). |

Source is **deploy_stock**. If you normally use **deploy** (combo navigation), your existing `inputs.py` is unchanged; only display and lib files above are updated.

---

## 3. Test on the device

- **Display:** Two rows of 3 effect blocks, no big center text; larger effect names.  
- **Buttons:** Press effect buttons; LEDs and display blocks should update (toggle on/off).  
- **Dim when off:** Toggling an effect off should dim its display block; on again should brighten it.

---

## 4. Test emulator sync

1. Open the **web editor** (localhost) and load the **MIDI Captain Mini 6** view.  
2. Load the same config as on the device (e.g. open from device or use the same template).  
3. **In the emulator:** Press buttons; LED rings and the 6 effect blocks should update (toggle, dim/bright).  
4. **On the device:** Press buttons; same behavior.  
5. **Sync:** If you have a way to send state device → emulator (e.g. MIDI or future feature), compare; otherwise confirm that emulator and device both behave correctly for the same config.

---

## 5. If the volume name is different

List volumes:
```bash
ls /Volumes/
```

Then run:
```bash
./deploy-to-device.sh /Volumes/YourVolumeName
```
