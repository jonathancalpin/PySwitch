# MIDI Captain Mini 6 -- Todo List

**Source:** Derived from ACTION_PLAN.md.

---

## Phase 1: Name mangling fix

- [x] Rename `__receive_midi_messages` -> `_receive_midi_messages` in `controller.py` (all 3 copies)
- [x] Rename `__midi`, `__debug_stats`, `__max_consecutive_midi_msgs`, `__measurement_process_jitter` -> single underscore in `controller.py`
- [x] Rename `__receive_midi_messages` -> `_receive_midi_messages` in `controller_combo.py` (both copies)
- [x] Remove `_Controller__` hacks from `controller_combo.py`
- [x] Rename combo private attrs (`__pager`, `__pending`, `__suppressed`, `__last_pushed`) -> single underscore
- [x] Fix reversed A+B/B+C direction in `content/controller_combo.py`

---

## Phase 2: PC preset active state

- [x] Add `group` parameter to `CUSTOM_MESSAGE()` function
- [x] Implement radio-button logic in `_CustomMessageCallback.push()`
- [x] Register callbacks by group in `_CustomMessageCallback.init()`
- [x] Update `update_displays()` to use bright/dim based on group state
- [x] Add `reset()` to clear group state
- [x] Update `pc_select()` helper in `inputs.py` to pass `group=f"pc_ch{channel}"`

---

## Phase 3: Display layout

- [x] 3x2 grid filling full 240x240 screen (already implemented)
- [x] No center "PySwitch" label
- [x] PT40 font with text wrapping
- [x] Background color matches switch color

---

## Phase 4: Web editor review

- [ ] Audit web editor combo paging export (generates ComboController import + ComboPager wiring)
- [ ] Audit action editor for CC values, PC values, color selection, toggle on/off
- [ ] Audit whether `group` parameter can be configured in editor
- [ ] Document gaps and create targeted fixes if needed

---

## Phase 5: Documentation

- [x] Rewrite PROJECT_GUIDE.md
- [x] Rewrite PROJECT_SCOPE_MIDI_CAPTAIN_MINI_6.md
- [x] Rewrite ACTION_PLAN.md
- [x] Rewrite TODOS.md

---

## Phase 6: Tests

- [x] Update test_combo_pager.py with name mangling verification
- [x] Update test_combo_pager.py with correct A+B/B+C direction
- [x] Add single-press-not-combo test
- [x] All tests pass

---

## On-device verification (next)

- [ ] Deploy `deploy_stock/` to device
- [ ] Verify A+B = prev_page (backward)
- [ ] Verify B+C = next_page (forward)
- [ ] Verify individual A/B/C presses still work after 50ms window
- [ ] Verify CC toggle dim/bright
- [ ] Verify PC preset radio-button (pressing one dims others)
- [ ] Verify 3x2 display with page colors

---

## Optional (future)

- [ ] Tap tempo value on display
- [ ] Tuner on display
- [ ] CC overlay (show CC# and value temporarily)
- [ ] Per-segment LED control in editor
