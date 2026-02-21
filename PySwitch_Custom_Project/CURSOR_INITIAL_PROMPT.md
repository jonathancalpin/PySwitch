# CURSOR / CLAUDE CODE – INITIAL PROMPT (Rescoped)

Copy this (and optionally attach ACTION_PLAN.md + PROJECT_SCOPE_MIDI_CAPTAIN_MINI_6.md) when starting work on this project.

---

## PROJECT CONTEXT

I'm modifying the **PySwitch** firmware for the **PaintAudio MIDI Captain Mini 6** foot controller (CircuitPython on RP2040). The goal is a multi-page MIDI controller with a clear display and predictable toggles.

**Target behavior:**

1. **Display:** Even 3×2 grid (6 blocks). Each block:
   - Background color matches the switch color.
   - **Toggle buttons:** brighter when on, dimmer when off (dim when off).
   - **Preset/PC:** stays “active” (bright) when that preset is selected.
2. **Page change:** HOLD Button B to cycle pages (Logic → ToneX → GP-5 → Looper).  
   The **web editor** should allow configuring **A+B** and **B+C** for page up/down (device may use hold-B for now).
3. **Editor:** Easy adjustment of **CC, PC, notes, toggle**, and **colors** per action/page.

**Stable device firmware:** `deploy_stock/` – standard Controller, PagerAction (hold B), display labels wired, CUSTOM_MESSAGE with toggle dim. Do **not** use input-rebuild on page change (it broke toggles). Deploy with `./deploy-to-device.sh`.

---

## HARDWARE

- **Device:** PaintAudio MIDI Captain Mini 6  
- **MCU:** RP2040 (CircuitPython, PySwitch)  
- **Buttons:** 6 footswitches – top row 1,2,3; bottom row A,B,C  
- **Display:** TFT (e.g. ST7789, 240×135 or 240×240)  
- **Outputs:** USB MIDI, 5-pin DIN MIDI  

---

## KEY FILES

| Purpose | Location |
|--------|----------|
| Device entry | `deploy_stock/code.py` → `import pyswitch.process` |
| Device config | `deploy_stock/inputs.py`, `deploy_stock/display.py` |
| Main loop | `deploy_stock/lib/pyswitch/process.py` (standard Controller) |
| Controller | `deploy_stock/lib/pyswitch/controller/controller.py` |
| Paging | `deploy_stock/lib/pyswitch/clients/local/actions/pager.py` |
| Toggle + display | `deploy_stock/lib/pyswitch/clients/local/actions/custom.py` |
| Deploy | `deploy-to-device.sh` (copies from `deploy_stock` to volume) |
| **Todo list** | `TODOS.md` |
| **Rules + goals** | `PROJECT_GUIDE.md` |
| Scope / plan | `ACTION_PLAN.md`, `PROJECT_SCOPE_MIDI_CAPTAIN_MINI_6.md` |
| Rescope / Claude Code | `RESCOPE_AND_CLAUDE_CODE.md` |

---

## CONSTRAINTS

- **Memory:** RP2040 RAM is limited; avoid heavy per-page input rebuilds.
- **Config:** Prefer web editor; device uses `inputs.py` / `display.py` from `deploy_stock`.
- **Parity:** Emulator should match device for display, LEDs, toggle/preset where possible.
- **Display:** 6 effect names, color block = switch color, dim when off, bright when on.

---

## CONTINUITY

- **ACTION_PLAN.md** = single source for current phase and next tasks. Check it first when starting work.
- After completing a task, update ACTION_PLAN and (if needed) PROJECT_SCOPE and this prompt.
- To rescope (in Cursor or Claude Code), use **RESCOPE_AND_CLAUDE_CODE.md** and keep all three docs in sync.

---

## TESTING

1. Connect MIDI Captain (e.g. hold Button 1) to mount USB volume.  
2. Run `./deploy-to-device.sh` from PySwitch_Custom_Project.  
3. Eject volume and reboot device.  
4. Check: 3×2 display, names/colors, toggle dim/bright, hold B = page change.
