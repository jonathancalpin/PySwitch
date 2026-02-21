# combo_detector.py
# Combo Button Detection for PySwitch
# Add this file to: lib/pyswitch/controller/combo_detector.py
"""
Detects simultaneous button presses within a time window and triggers
page navigation instead of individual button actions.

Integration with PySwitch:
- Works with SwitchController objects
- Intercepts switch processing to implement combo detection
- Defers individual actions when combo is pending

Usage in Controller:
    from .combo_detector import ComboDetector
    
    # In __init__:
    self.combo = ComboDetector(
        combo_switches=['A', 'B', 'C'],
        on_combo_ab=self.page_manager.next_page,
        on_combo_bc=self.page_manager.prev_page
    )
    
    # In __receive_midi_messages, before input.process():
    for input in self.inputs:
        if self.combo.intercept(input):
            continue  # Skip normal processing
        input.process()
    
    # Check for expired pending presses:
    self.combo.process_expired(self.inputs)
"""

import time


class ComboDetector:
    """
    Detects when two adjacent buttons are pressed simultaneously (within a time window)
    and triggers page changes instead of individual button actions.
    
    Designed for MIDI Captain Mini 6 layout:
        [1] [2] [3]
        [A] [B] [C]
    
    Combos:
        A+B = Page Up (next page)
        B+C = Page Down (previous page)
    """
    
    # Time window in milliseconds for detecting simultaneous press
    DEFAULT_COMBO_WINDOW_MS = 50
    
    def __init__(self, combo_switches=None, combo_window_ms=None,
                 on_combo_ab=None, on_combo_bc=None):
        """
        Initialize the combo detector.
        
        Args:
            combo_switches: List of switch names that participate in combos (e.g., ['A', 'B', 'C'])
            combo_window_ms: Time window for combo detection (default 50ms)
            on_combo_ab: Callback for A+B combo (page up)
            on_combo_bc: Callback for B+C combo (page down)
        """
        self.combo_switches = set(combo_switches or ['A', 'B', 'C'])
        self.combo_window_ms = combo_window_ms or self.DEFAULT_COMBO_WINDOW_MS
        
        # Callbacks
        self.on_combo_ab = on_combo_ab
        self.on_combo_bc = on_combo_bc
        
        # State tracking
        self.pending_presses = {}  # {switch_name: (timestamp_ms, switch_controller)}
        self.suppressed_switches = set()  # Switch names currently suppressed
        self.last_pushed_state = {}  # Track previous pushed state for edge detection
        
    def _get_time_ms(self):
        """Get current time in milliseconds."""
        return int(time.monotonic() * 1000)
    
    def _get_switch_name(self, switch_controller):
        """
        Extract the switch name from a SwitchController.
        Returns None if not identifiable.
        """
        # SwitchController stores the config internally, but we can access
        # the assignment through the actions or by checking stored reference
        # The switch name is in the original config dict
        
        # Try to get name from the switch model's string representation
        # or from stored config
        try:
            # The hardware switch assignment has a "name" field
            # We need to access it through the stored config
            # This is set when SwitchController is created
            if hasattr(switch_controller, '_SwitchController__switch'):
                switch = switch_controller._SwitchController__switch
                # Check if the switch object or its parent config has a name
                if hasattr(switch, 'name'):
                    return switch.name
            
            # Fallback: Try to infer from pixels assignment (position-based)
            # Mini 6 layout: pixels 0-2=1, 3-5=2, 6-8=3, 9-11=A, 12-14=B, 15-17=C
            if hasattr(switch_controller, 'pixels') and switch_controller.pixels:
                first_pixel = switch_controller.pixels[0]
                pixel_map = {
                    0: '1', 3: '2', 6: '3',
                    9: 'A', 12: 'B', 15: 'C'
                }
                return pixel_map.get(first_pixel)
                
        except Exception:
            pass
        
        return None
    
    def _check_combo(self, switch_name, timestamp_ms):
        """
        Check if this switch press completes a combo.
        
        Returns:
            Tuple of (combo_detected, action_to_call) or (False, None)
        """
        # A+B combo
        if switch_name == 'A' and 'B' in self.pending_presses:
            pending_time, _ = self.pending_presses['B']
            if timestamp_ms - pending_time <= self.combo_window_ms:
                return True, self.on_combo_ab
        
        if switch_name == 'B' and 'A' in self.pending_presses:
            pending_time, _ = self.pending_presses['A']
            if timestamp_ms - pending_time <= self.combo_window_ms:
                return True, self.on_combo_ab
        
        # B+C combo
        if switch_name == 'B' and 'C' in self.pending_presses:
            pending_time, _ = self.pending_presses['C']
            if timestamp_ms - pending_time <= self.combo_window_ms:
                return True, self.on_combo_bc
        
        if switch_name == 'C' and 'B' in self.pending_presses:
            pending_time, _ = self.pending_presses['B']
            if timestamp_ms - pending_time <= self.combo_window_ms:
                return True, self.on_combo_bc
        
        return False, None
    
    def intercept(self, switch_controller):
        """
        Intercept switch processing to detect combos.
        Call this BEFORE switch_controller.process().
        
        Args:
            switch_controller: The SwitchController to check
            
        Returns:
            True if normal processing should be skipped (combo handling in progress)
            False if normal processing should continue
        """
        switch_name = self._get_switch_name(switch_controller)
        
        # Not a combo-capable switch, let it process normally
        if switch_name is None or switch_name not in self.combo_switches:
            return False
        
        # Get current pushed state
        is_pushed = switch_controller.pushed
        was_pushed = self.last_pushed_state.get(switch_name, False)
        self.last_pushed_state[switch_name] = is_pushed
        
        timestamp_ms = self._get_time_ms()
        
        # Detect press edge (transition from not-pushed to pushed)
        if is_pushed and not was_pushed:
            # New press detected
            combo_detected, action = self._check_combo(switch_name, timestamp_ms)
            
            if combo_detected:
                # Combo completed!
                print(f"[Combo] Detected: {switch_name} combo triggered")
                
                # Mark both switches as suppressed
                self.suppressed_switches.add(switch_name)
                
                # Find and suppress the partner
                for partner in list(self.pending_presses.keys()):
                    self.suppressed_switches.add(partner)
                    del self.pending_presses[partner]
                
                # Execute combo action
                if action:
                    action()
                
                return True  # Skip normal processing
            
            # No combo yet - register as pending
            self.pending_presses[switch_name] = (timestamp_ms, switch_controller)
            return True  # Defer processing until combo window expires
        
        # Detect release edge
        if not is_pushed and was_pushed:
            # Switch released
            if switch_name in self.suppressed_switches:
                # This switch was part of a combo, suppress its release action too
                self.suppressed_switches.discard(switch_name)
                return True  # Skip normal processing
        
        # If switch is suppressed, skip processing
        if switch_name in self.suppressed_switches:
            return True
        
        # If switch has a pending press, skip processing (waiting for combo window)
        if switch_name in self.pending_presses:
            return True
        
        return False  # Allow normal processing
    
    def process_expired(self, inputs):
        """
        Check for expired pending presses and trigger their individual actions.
        Call this each tick after processing all inputs.
        
        Args:
            inputs: List of all SwitchController objects
        """
        timestamp_ms = self._get_time_ms()
        expired = []
        
        for switch_name, (press_time, switch_controller) in list(self.pending_presses.items()):
            if timestamp_ms - press_time > self.combo_window_ms:
                # Combo window expired without a combo
                expired.append((switch_name, switch_controller))
                del self.pending_presses[switch_name]
        
        # Trigger the delayed individual actions for expired presses
        for switch_name, switch_controller in expired:
            print(f"[Combo] Window expired for {switch_name}, triggering individual action")
            # Call the switch's normal process method
            # The switch is still pushed, so process() will detect the push
            switch_controller.process()
    
    def reset(self):
        """Reset all combo state."""
        self.pending_presses.clear()
        self.suppressed_switches.clear()
        self.last_pushed_state.clear()
