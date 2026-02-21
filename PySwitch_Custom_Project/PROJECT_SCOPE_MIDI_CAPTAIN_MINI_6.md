# MIDI Captain Mini 6 -- Firmware & Web Editor Scope

---

## Current State (Feb 2026)

### What works

- **Display:** 3x2 grid (6 blocks of 80x120px) fills the full 240x240 screen. PT40 font with text wrapping. Background color matches switch color. No center "PySwitch" label.
- **CC toggle:** Each press toggles on/off. LED and display block bright when on, dim when off.
- **CC momentary:** Sends value on press, release value on release.
- **PC preset (radio-button):** `group` parameter in `CUSTOM_MESSAGE()` provides radio-button behavior. Pressing a preset activates it (bright) and deactivates others in the same group (dim). Groups are per-channel (e.g. `"pc_ch2"`).
- **Combo paging:** A+B = `prev_page()` (backward), B+C = `next_page()` (forward). Uses `ComboController` which overrides `Controller._receive_midi_messages()`. 50ms combo window. Individual presses still work after window expires.
- **Pages:** Logic (Blue, Ch1) -> ToneX (Red, Ch2) -> GP-5 (Green, Ch3) -> Looper (Purple, Ch4).
- **Deploy:** `./deploy-to-device.sh` copies from `deploy_stock/` to device volume.

### What was fixed (Feb 2026)

- **Name mangling bug:** `Controller.__receive_midi_messages` used double underscore, which Python mangles to `_Controller__receive_midi_messages`. `ComboController.__receive_midi_messages` became `_ComboController__receive_midi_messages` -- a different name. So `Controller.tick()` always called the base version, and combo paging never worked. **Fix:** Renamed to `_receive_midi_messages` (single underscore = protected, overridable). Also renamed `__midi`, `__debug_stats`, `__max_consecutive_midi_msgs`, `__measurement_process_jitter` to single underscore so `ComboController` can access them directly instead of using `_Controller__` hacks.
- **Content copy page direction:** The `content/` copy had A+B and B+C reversed compared to `deploy_stock/`. Fixed to match: A+B = prev, B+C = next.

### What needs work

- **Web editor:** Needs audit to verify combo paging export, action editor support, and the new `group` parameter can be configured.
- **Emulator:** LED/display sync on button press needs verification.
- **Optional:** Tap tempo display, tuner, CC overlay, per-segment LED control.

---

## Architecture

### Files

| Component | deploy_stock/ | content/ |
|-----------|--------------|----------|
| Controller base | `lib/pyswitch/controller/controller.py` | `lib/pyswitch/controller/controller.py` |
| Combo controller | `lib/pyswitch/controller/controller_combo.py` | `lib/pyswitch/controller/controller_combo.py` |
| Custom actions | `lib/pyswitch/clients/local/actions/custom.py` | `lib/pyswitch/clients/local/actions/custom.py` |
| Inputs config | `inputs.py` | `inputs.py` |
| Display config | `display.py` | `display.py` |

### Key design decisions

1. **Single underscore for overridable members.** Any method or attribute that a subclass needs to access or override uses `_name` (single underscore). Double underscore (`__name`) is reserved for truly private members that should never be accessed by subclasses (e.g. `__memory_warn_limit`, `__clear_buffer`).

2. **ComboController overrides `_receive_midi_messages`.** The base `Controller.tick()` calls `self._receive_midi_messages()`. Because it uses single underscore, Python's method resolution order finds `ComboController._receive_midi_messages()` when the instance is a `ComboController`.

3. **Group-based radio buttons.** PC presets share a group key stored in `appl.shared`. When one is pressed, it iterates the group list and deactivates all others. This is simpler than a dedicated PresetCallback and reuses the existing CUSTOM_MESSAGE infrastructure.

---

## Phase Summary

- [x] **Phase 1:** Fix name mangling bug (controller `__` -> `_`)
- [x] **Phase 2:** PC preset active state (group/radio behavior)
- [x] **Phase 3:** Display layout (3x2 full screen, already done)
- [ ] **Phase 4:** Web editor review and fixes
- [x] **Phase 5:** Project documentation rescope
- [x] **Phase 6:** Tests (combo pager tests pass)

---

*Updated: February 2026*
