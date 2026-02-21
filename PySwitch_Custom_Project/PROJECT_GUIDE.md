# PySwitch Custom Project -- Project Guide

**MIDI Captain Mini 6** custom firmware and web editor. This guide is the main reference for **context**, **rules**, and **goals**.

---

## 1. Goals

1. **Device firmware:** 3x2 display (6 blocks, 80x120px each), color per switch, CC toggle dim/bright, PC preset radio-button (active preset stays bright, others dim). Page navigation via A+B / B+C combo press. Stable firmware in `deploy_stock/`; deploy with `./deploy-to-device.sh`.
2. **Editor:** Web editor for configuring pages, actions (CC, PC, notes), colors, toggle/momentary modes, and combo paging. Export generates `inputs.py` compatible with `ComboController`.
3. **Optional:** Tap tempo on display, tuner, CC overlay, per-segment LED in editor.

---

## 2. Rules

### 2.1 Before starting work

- **Read ACTION_PLAN.md** -- current phase and task.
- **Read TODOS.md** -- next unchecked item.
- **Read this guide** -- rules and file layout.

### 2.2 When writing code

- **Device firmware:** Only change files in `deploy_stock/` (or `content/` as canonical source). Do NOT use input-rebuild on page change (breaks toggles).
- **Display:** 6 blocks filling the full 240x240 screen, one per button. Background color = switch color. Dim when off, bright when on. No center "PySwitch" label. PT40 font with text wrapping.
- **Page navigation:** A+B = `prev_page()` (backward), B+C = `next_page()` (forward). Uses `ComboController` which overrides `Controller._receive_midi_messages()` with combo-aware input processing. 50ms combo window.
- **Name mangling:** All attributes/methods that subclasses need to access MUST use single underscore (`_name`), not double underscore (`__name`). Double underscore causes Python name mangling which prevents subclass override.
- **PC presets:** Use `group` parameter in `CUSTOM_MESSAGE()` for radio-button behavior. All PC presets on the same channel share a group (e.g. `"pc_ch2"`).

### 2.3 When finishing a task

- Tick the item in TODOS.md.
- Update ACTION_PLAN.md if a phase milestone is reached.

### 2.4 Continuity (Claude Code)

- **Single source for "what's next":** ACTION_PLAN.md.
- **Actionable checklist:** TODOS.md.

---

## 3. Key files

| Purpose | File or folder |
|---------|----------------|
| **What's next / current task** | ACTION_PLAN.md |
| **Todo list** | TODOS.md |
| **Rules + goals (this file)** | PROJECT_GUIDE.md |
| **Scope + implementation plan** | PROJECT_SCOPE_MIDI_CAPTAIN_MINI_6.md |
| **Stable device firmware** | `deploy_stock/` (code.py, inputs.py, display.py, controller, pager, custom) |
| **Canonical source library** | `content/lib/pyswitch/` (controller, custom, pager, colors) |
| **Deploy to device** | `deploy-to-device.sh` |
| **Web editor** | `web-editor/` |
| **Tests** | `test_combo_pager.py` |

---

## 4. Architecture

### Controller hierarchy

```
Controller (controller.py)
  - _receive_midi_messages()   <-- single underscore, overridable
  - _midi, _debug_stats, _max_consecutive_midi_msgs  <-- single underscore, accessible by subclass
  - tick() calls self._receive_midi_messages()

ComboController(Controller) (controller_combo.py)
  - Overrides _receive_midi_messages() with combo-aware version
  - _intercept() checks A/B/C switches for combo presses
  - _check_combo() detects A+B and B+C within 50ms window
  - _process_expired() fires individual actions after window expires
```

### CUSTOM_MESSAGE modes

- **Momentary** (default): sends message on press, message_release on release
- **Toggle** (`toggle=True`): alternates between message and message_release on each press
- **Group/Radio** (`group="name"`): activates self, deactivates all others in same group

### Page system

- `PagerAction` manages page list and enable_callback filtering
- `ComboController` receives pager reference, calls `prev_page()` / `next_page()`
- Each action has an `id` matching a page ID; `enable_callback` shows/hides per page

---

## 5. Deploy workflow

1. Mount device (hold button, volume appears as MIDICAPTAIN).
2. From project root: `./deploy-to-device.sh` or `./deploy-to-device.sh /Volumes/MIDICAPTAIN`.
3. Eject volume and reboot device.

---

## 6. Constraints

- **Device:** `deploy_stock` only; no input-rebuild on page change.
- **Display:** 6 blocks, color = switch color, dim when off, bright when on.
- **Name mangling:** Never use `__` prefix for methods/attrs that subclasses need.
- **Config:** Web editor as primary; device config = `inputs.py` / `display.py` from `deploy_stock`.

---

*Document version: 4.0 (rescoped Feb 2026 -- name mangling fix, combo paging, PC groups)*
