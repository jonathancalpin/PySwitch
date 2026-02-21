# controller_combo.py
# A+B = prev_page (backward), B+C = next_page (forward).
# Time-window: press second button within 200ms.
# No Hold B - paging only via combo.

import time
from .controller import Controller
from ..misc import do_print


class ComboController(Controller):
    IDX_A = 3
    IDX_B = 4
    IDX_C = 5
    COMBO_WINDOW_MS = 200

    def __init__(self, pager=None, **kwargs):
        super().__init__(**kwargs)
        # Don't trust the passed pager reference - CircuitPython may
        # give us a different instance than the one that was initialized.
        # Instead, find the actual PagerAction from the initialized inputs.
        self._pager = None
        if pager is not None:
            from ..clients.local.actions.pager import PagerAction
            for inp in self.inputs:
                for action in inp.actions:
                    if isinstance(action, PagerAction):
                        self._pager = action
                        break
                if self._pager:
                    break
        self._pending = {}
        self._suppressed = set()
        self._last_pushed = {}
        self._combo_debug = True

    def _get_time_ms(self):
        return int(time.monotonic() * 1000)

    def _check_combo(self, idx, timestamp_ms):
        if idx == self.IDX_B and self.IDX_A in self._pending:
            t = self._pending[self.IDX_A][0]
            if timestamp_ms - t <= self.COMBO_WINDOW_MS:
                return True, True
        if idx == self.IDX_A and self.IDX_B in self._pending:
            t = self._pending[self.IDX_B][0]
            if timestamp_ms - t <= self.COMBO_WINDOW_MS:
                return True, True
        if idx == self.IDX_C and self.IDX_B in self._pending:
            t = self._pending[self.IDX_B][0]
            if timestamp_ms - t <= self.COMBO_WINDOW_MS:
                return True, False
        if idx == self.IDX_B and self.IDX_C in self._pending:
            t = self._pending[self.IDX_C][0]
            if timestamp_ms - t <= self.COMBO_WINDOW_MS:
                return True, False
        return False, None

    def _intercept(self, idx):
        if idx not in (self.IDX_A, self.IDX_B, self.IDX_C):
            return False

        inp = self.inputs[idx]
        is_pushed = inp.pushed
        was_pushed = self._last_pushed.get(idx, False)
        self._last_pushed[idx] = is_pushed

        ts = self._get_time_ms()

        if is_pushed and not was_pushed:
            if self._combo_debug:
                do_print("COMBO: press idx=" + str(idx) + " ts=" + str(ts) + " pending=" + str(list(self._pending.keys())))
            combo, is_ab = self._check_combo(idx, ts)
            if combo:
                if self._combo_debug:
                    do_print("COMBO: DETECTED! is_ab=" + str(is_ab) + " pager=" + str(self._pager is not None))
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
            return True

        if not is_pushed and was_pushed:
            if idx in self._suppressed:
                self._suppressed.discard(idx)
                return True
            return False

        if idx in self._suppressed:
            return True
        if idx in self._pending:
            return True
        return False

    def _process_expired(self):
        ts = self._get_time_ms()
        expired = []
        for idx in list(self._pending.keys()):
            t = self._pending[idx][0]
            if ts - t > self.COMBO_WINDOW_MS:
                expired.append(idx)
                del self._pending[idx]
        if expired:
            do_print("COMBO: expired=" + str(expired) + " (solo press)")
        for idx in expired:
            if idx < len(self.inputs):
                self.inputs[idx].process()

    def _receive_midi_messages(self):
        if self._combo_debug:
            do_print("COMBO: _receive_midi_messages OVERRIDE active, pager=" + str(self._pager is not None))
            self._combo_debug = False
        cnt = 0
        while True:
            if self._debug_stats:
                self._measurement_process_jitter.finish()

            for i in range(len(self.inputs)):
                if self._intercept(i):
                    continue
                self.inputs[i].process()

            self._process_expired()

            if self._debug_stats:
                self._measurement_process_jitter.start()

            midimsg = self._midi.receive()
            self.client.receive(midimsg)

            cnt += 1
            if not midimsg or cnt > self._max_consecutive_midi_msgs:
                break
