#!/usr/bin/env python3
"""Test combo pager logic - run with: python test_combo_pager.py"""

# Mock PagerAction
class MockPager:
    def __init__(self):
        self.pages = [{"id": "logic"}, {"id": "tonex"}, {"id": "gp5"}, {"id": "looper"}]
        self.current_page_index = 0
        self.current_page_id = self.pages[0]["id"]
        self.prev_calls = 0
        self.next_calls = 0

    def prev_page(self):
        self.prev_calls += 1
        self.current_page_index = (self.current_page_index - 1) % len(self.pages)
        self.current_page_id = self.pages[self.current_page_index]["id"]
        print(f"  prev_page -> {self.current_page_id}")

    def next_page(self):
        self.next_calls += 1
        self.current_page_index = (self.current_page_index + 1) % len(self.pages)
        self.current_page_id = self.pages[self.current_page_index]["id"]
        print(f"  next_page -> {self.current_page_id}")


# Mock ComboController logic (mirrors actual ComboController._intercept)
class ComboTest:
    IDX_A, IDX_B, IDX_C = 3, 4, 5
    COMBO_WINDOW_MS = 50

    def __init__(self, pager):
        self._pager = pager
        self._pending = {}
        self._suppressed = set()
        self._last_pushed = {}
        self.inputs = [{"pushed": False} for _ in range(6)]  # Simulate 6 switches

    def _get_time_ms(self):
        import time
        return int(time.monotonic() * 1000)

    def _check_combo(self, idx, ts):
        if idx == self.IDX_B and self.IDX_A in self._pending:
            t = self._pending[self.IDX_A][0]
            if ts - t <= self.COMBO_WINDOW_MS:
                return True, True
        if idx == self.IDX_A and self.IDX_B in self._pending:
            t = self._pending[self.IDX_B][0]
            if ts - t <= self.COMBO_WINDOW_MS:
                return True, True
        if idx == self.IDX_C and self.IDX_B in self._pending:
            t = self._pending[self.IDX_B][0]
            if ts - t <= self.COMBO_WINDOW_MS:
                return True, False
        if idx == self.IDX_B and self.IDX_C in self._pending:
            t = self._pending[self.IDX_C][0]
            if ts - t <= self.COMBO_WINDOW_MS:
                return True, False
        return False, None

    def simulate_press(self, idx):
        """Simulate press edge (was not pushed, now pushed)."""
        was = self._last_pushed.get(idx, False)
        self._last_pushed[idx] = True
        self.inputs[idx]["pushed"] = True
        if not was:
            ts = self._get_time_ms()
            combo, is_ab = self._check_combo(idx, ts)
            if combo:
                if self._pager:
                    if is_ab:
                        self._pager.prev_page()   # A+B = backward
                    else:
                        self._pager.next_page()   # B+C = forward
                self._suppressed.add(idx)
                for p in (self.IDX_A, self.IDX_B, self.IDX_C):
                    if p in self._pending:
                        self._suppressed.add(p)
                        del self._pending[p]
                return True
            self._pending[idx] = (ts,)
        return False

    def simulate_release(self, idx):
        """Simulate release edge."""
        self._last_pushed[idx] = False
        self.inputs[idx]["pushed"] = False
        if idx in self._suppressed:
            self._suppressed.discard(idx)
        if idx in self._pending:
            del self._pending[idx]


def test_name_mangling_fix():
    """Test that _receive_midi_messages is properly overridable (single underscore)."""
    import sys, os
    # Verify that ComboController._receive_midi_messages overrides Controller._receive_midi_messages
    # by checking the method resolution order
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "content", "lib"))

    # We can't import the full module (needs CircuitPython libs), but we can check
    # the source code for the fix
    import ast

    controller_path = os.path.join(os.path.dirname(__file__), "content", "lib", "pyswitch", "controller", "controller.py")
    combo_path = os.path.join(os.path.dirname(__file__), "content", "lib", "pyswitch", "controller", "controller_combo.py")

    with open(controller_path) as f:
        controller_src = f.read()
    with open(combo_path) as f:
        combo_src = f.read()

    # Check that controller.py uses single underscore
    assert "def _receive_midi_messages(self):" in controller_src, "Controller should define _receive_midi_messages (single underscore)"
    assert "self._receive_midi_messages()" in controller_src, "Controller.tick() should call self._receive_midi_messages()"
    assert "__receive_midi_messages" not in controller_src, "Controller should NOT have __receive_midi_messages (double underscore)"

    # Check that controller_combo.py uses single underscore
    assert "def _receive_midi_messages(self):" in combo_src, "ComboController should define _receive_midi_messages (single underscore)"
    assert "_Controller__" not in combo_src, "ComboController should NOT use _Controller__ name-mangled references"

    # Check that combo uses _midi, _debug_stats etc (single underscore)
    assert "self._midi" in combo_src, "ComboController should use self._midi (single underscore)"
    assert "self._debug_stats" in combo_src, "ComboController should use self._debug_stats (single underscore)"

    print("  Name mangling fix verified in source code")

    # Also check deploy_stock copy
    ds_controller = os.path.join(os.path.dirname(__file__), "PySwitch_Custom_Project", "deploy_stock", "lib", "pyswitch", "controller", "controller.py")
    ds_combo = os.path.join(os.path.dirname(__file__), "PySwitch_Custom_Project", "deploy_stock", "lib", "pyswitch", "controller", "controller_combo.py")

    with open(ds_controller) as f:
        ds_ctrl_src = f.read()
    with open(ds_combo) as f:
        ds_combo_src = f.read()

    assert "def _receive_midi_messages(self):" in ds_ctrl_src, "deploy_stock Controller should define _receive_midi_messages"
    assert "def _receive_midi_messages(self):" in ds_combo_src, "deploy_stock ComboController should define _receive_midi_messages"
    assert "_Controller__" not in ds_combo_src, "deploy_stock ComboController should NOT use _Controller__ references"

    print("  deploy_stock copy also verified")


def test_combo_direction():
    """Test A+B = prev_page (backward), B+C = next_page (forward)."""
    import time
    pager = MockPager()
    combo = ComboTest(pager)

    print("Test: A+B -> prev_page (backward)")
    combo.simulate_press(3)  # A
    time.sleep(0.01)  # 10ms
    combo.simulate_press(4)  # B
    combo.simulate_release(3)
    combo.simulate_release(4)
    assert pager.prev_calls == 1, f"Expected 1 prev_page, got {pager.prev_calls}"
    assert pager.current_page_id == "looper", f"Expected looper (wrapped backward), got {pager.current_page_id}"
    print(f"  OK: prev_page called, page = {pager.current_page_id}\n")

    print("Test: B+C -> next_page (forward)")
    combo.simulate_press(4)  # B
    time.sleep(0.01)
    combo.simulate_press(5)  # C
    combo.simulate_release(4)
    combo.simulate_release(5)
    assert pager.next_calls == 1, f"Expected 1 next_page, got {pager.next_calls}"
    assert pager.current_page_id == "logic", f"Expected logic (wrapped forward from looper), got {pager.current_page_id}"
    print(f"  OK: next_page called, page = {pager.current_page_id}\n")


def test_single_press_not_combo():
    """Test that a single press (no combo within window) is not treated as combo."""
    import time
    pager = MockPager()
    combo = ComboTest(pager)

    print("Test: Single A press (no combo)")
    combo.simulate_press(3)  # A
    time.sleep(0.06)  # 60ms > 50ms window
    combo.simulate_release(3)
    assert pager.prev_calls == 0, "Single press should not trigger prev_page"
    assert pager.next_calls == 0, "Single press should not trigger next_page"
    print("  OK: no page change on single press\n")


def main():
    print("=" * 50)
    print("PySwitch Combo Pager Tests")
    print("=" * 50)
    print()

    print("1. Name mangling fix verification")
    test_name_mangling_fix()
    print()

    print("2. Combo direction (A+B=prev, B+C=next)")
    test_combo_direction()

    print("3. Single press (no combo)")
    test_single_press_not_combo()

    print("=" * 50)
    print("All tests passed!")
    print("=" * 50)


if __name__ == "__main__":
    main()
