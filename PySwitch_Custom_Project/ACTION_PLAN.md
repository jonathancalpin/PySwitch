# MIDI Captain Mini 6 -- Action Plan

**Purpose:** Single source of truth for "what we're doing now" and "what's next."

---

## Current status

| Field | Value |
|-------|-------|
| **Current phase** | Phase 4: Web editor review |
| **Last completed** | Phase 1-2 code fixes, Phase 5 docs, Phase 6 tests |
| **Source for device** | `deploy_stock/` (ComboController + PagerAction) |

---

## Completed work (Feb 2026)

### Phase 1: Name mangling fix (DONE)

Fixed the root cause of "pages don't cycle" -- Python name mangling. `Controller.__receive_midi_messages` (double underscore) gets mangled to `_Controller__receive_midi_messages`, so `ComboController.__receive_midi_messages` (mangled to `_ComboController__receive_midi_messages`) was **never called** by `Controller.tick()`.

**Fix applied to 5 files:**
- `deploy_stock/lib/pyswitch/controller/controller.py` -- `__` -> `_` for method + 4 attrs
- `deploy_stock/lib/pyswitch/controller/controller_combo.py` -- `__` -> `_`, removed `_Controller__` hacks
- `content/lib/pyswitch/controller/controller.py` -- same as above
- `content/lib/pyswitch/controller/controller_combo.py` -- same + fixed reversed A+B/B+C direction
- `deploy/lib/pyswitch/controller/controller.py` -- same

### Phase 2: PC preset active state (DONE)

Added `group` parameter to `CUSTOM_MESSAGE()` for radio-button behavior. When `group` is set:
- Pressing activates self (bright LED + bright display block)
- Deactivates all others in the same group (dim LED + dim display block)
- No action on release

**Files modified:**
- `deploy_stock/lib/pyswitch/clients/local/actions/custom.py`
- `content/lib/pyswitch/clients/local/actions/custom.py`
- `deploy/lib/pyswitch/clients/local/actions/custom.py`
- `deploy_stock/inputs.py` -- `pc_select()` passes `group=f"pc_ch{channel}"`
- `content/inputs.py` -- same
- `deploy/inputs.py` -- same

### Phase 3: Display layout (DONE -- pre-existing)

3x2 layout filling 240x240 screen already implemented in `deploy_stock/display.py`.

### Phase 5: Documentation (DONE)

All docs rewritten to reflect current state.

### Phase 6: Tests (DONE)

`test_combo_pager.py` passes -- verifies:
1. Source code uses single underscore (no `__receive_midi_messages`, no `_Controller__`)
2. A+B = prev_page (backward), B+C = next_page (forward)
3. Single press does not trigger combo

---

## Next tasks (in order)

1. **Deploy and verify on device:** Deploy `deploy_stock/` to hardware. Verify combo paging, CC toggle, PC preset radio behavior, 3x2 display.
2. **Web editor audit (Phase 4):** Review web editor templates and JS to verify combo paging export, action editor, and `group` parameter support.
3. **Optional features:** Tap tempo, tuner, CC overlay, per-segment LED.

---

## Key files

| What | Where |
|------|-------|
| **Todo list** | `TODOS.md` |
| **Rules + goals** | `PROJECT_GUIDE.md` |
| **Device firmware** | `deploy_stock/` |
| **Deploy script** | `deploy-to-device.sh` |
| **Scope** | `PROJECT_SCOPE_MIDI_CAPTAIN_MINI_6.md` |
| **Tests** | `test_combo_pager.py` |

---

## Constraints

- Deploy from `deploy_stock/` only.
- No input-rebuild on page change.
- Single underscore for overridable methods/attrs (never double underscore).
- Web editor as primary config tool.
