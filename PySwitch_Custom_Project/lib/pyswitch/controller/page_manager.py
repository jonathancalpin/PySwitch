# page_manager.py
# Page Manager for PySwitch Multi-Device Controller
# Add this file to: lib/pyswitch/controller/page_manager.py
"""
Manages multiple pages of button configurations, each targeting
a different device or function set.

Each page defines:
- Name (displayed on screen)
- MIDI channel
- Switch actions for all 6 buttons
- Optional color theme

Usage:
    pages_config = [
        {"name": "Logic", "channel": 1, "switches": [...], "color_theme": (0, 128, 255)},
        {"name": "ToneX", "channel": 2, "switches": [...], "color_theme": (255, 0, 0)},
    ]
    
    page_manager = PageManager(
        pages=pages_config,
        controller=controller,
        on_page_change=update_display_callback
    )
    
    page_manager.next_page()  # Go to next page
    page_manager.prev_page()  # Go to previous page
"""


class PageManager:
    """
    Manages multiple pages of switch configurations.
    Each page can target a different MIDI channel/device.
    """
    
    def __init__(self, pages, controller=None, on_page_change=None):
        """
        Initialize the page manager.
        
        Args:
            pages: List of page definition dictionaries, each containing:
                - "name": Display name for the page
                - "channel": MIDI channel (1-16)
                - "switches": List of switch configurations
                - "color_theme": Optional RGB tuple for page indicator
                - "midi_out": Optional "USB" or "DIN"
            controller: Reference to main Controller (for rebuilding inputs)
            on_page_change: Callback function(page_index, page_data) called after change
        """
        if not pages:
            raise ValueError("At least one page must be defined")
        
        self.pages = pages
        self.controller = controller
        self.on_page_change = on_page_change
        self.current_index = 0
        
        # Store original switch references for restoration
        self._original_inputs = None
        
    @property
    def current_page(self):
        """Get the current page definition."""
        return self.pages[self.current_index]
    
    @property
    def page_count(self):
        """Get total number of pages."""
        return len(self.pages)
    
    @property
    def current_page_name(self):
        """Get current page name."""
        return self.current_page.get('name', f'Page {self.current_index + 1}')
    
    @property
    def current_channel(self):
        """Get current page's MIDI channel."""
        return self.current_page.get('channel', 1)
    
    @property
    def current_midi_out(self):
        """Get current page's MIDI output type (USB or DIN)."""
        return self.current_page.get('midi_out', 'USB')
    
    @property
    def current_color_theme(self):
        """Get current page's color theme."""
        return self.current_page.get('color_theme', (255, 255, 255))
    
    def next_page(self):
        """
        Advance to the next page (with wraparound).
        """
        old_index = self.current_index
        self.current_index = (self.current_index + 1) % self.page_count
        self._apply_page_change(old_index)
        print(f"[Page] Up: {self.current_page_name} ({self.current_index + 1}/{self.page_count})")
        
    def prev_page(self):
        """
        Go to the previous page (with wraparound).
        """
        old_index = self.current_index
        self.current_index = (self.current_index - 1) % self.page_count
        self._apply_page_change(old_index)
        print(f"[Page] Down: {self.current_page_name} ({self.current_index + 1}/{self.page_count})")
        
    def go_to_page(self, index):
        """
        Go to a specific page by index.
        """
        if 0 <= index < self.page_count:
            old_index = self.current_index
            self.current_index = index
            self._apply_page_change(old_index)
            print(f"[Page] Go to: {self.current_page_name} ({self.current_index + 1}/{self.page_count})")
            
    def go_to_page_by_name(self, name):
        """
        Go to a specific page by name.
        """
        for i, page in enumerate(self.pages):
            if page.get('name', '').lower() == name.lower():
                self.go_to_page(i)
                return True
        return False
    
    def get_current_switches(self):
        """
        Get the switch definitions for the current page.
        """
        return self.current_page.get('switches', [])
    
    def _apply_page_change(self, old_index):
        """
        Apply the page change - update switch configurations.
        """
        if old_index == self.current_index:
            return
        
        # Flash LEDs or provide visual feedback (optional)
        self._flash_page_indicator()
        
        # Notify callback
        if self.on_page_change:
            self.on_page_change(self.current_index, self.current_page)
    
    def _flash_page_indicator(self):
        """
        Provide visual feedback for page change.
        This could flash all LEDs in the page's color theme.
        """
        if not self.controller:
            return
        
        color = self.current_color_theme
        
        # Briefly set all switch LEDs to page color
        try:
            for input_ctrl in self.controller.inputs:
                if hasattr(input_ctrl, 'color') and hasattr(input_ctrl, 'brightness'):
                    input_ctrl.color = color
                    input_ctrl.brightness = 0.8
        except Exception as e:
            print(f"[Page] LED flash error: {e}")
    
    def rebuild_inputs(self, new_switch_configs):
        """
        Rebuild the controller's inputs with new switch configurations.
        
        This is a more complete approach that recreates SwitchController objects.
        Use with caution - it's more memory intensive.
        
        Args:
            new_switch_configs: List of switch definition dicts for the new page
        """
        if not self.controller:
            print("[Page] Warning: No controller reference for input rebuild")
            return
        
        # Import here to avoid circular imports
        from .inputs import SwitchController, ContinuousController
        from ..misc import get_option
        
        # Clear old updateables (actions)
        for old_input in self.controller.inputs:
            for action in old_input.actions:
                if action in self.controller.updateables:
                    self.controller.updateables.remove(action)
        
        # Create new inputs
        new_inputs = []
        for sw_def in new_switch_configs:
            if hasattr(sw_def["assignment"]["model"], "pushed"):
                new_inputs.append(SwitchController(self.controller, sw_def))
            else:
                new_inputs.append(ContinuousController(self.controller, sw_def))
        
        self.controller.inputs = new_inputs
        
        # Reset actions to refresh displays
        self.controller.reset_actions()


class PageDisplay:
    """
    Helper class to update display with page information.
    Can be used as a callback for on_page_change.
    """
    
    def __init__(self, controller):
        """
        Args:
            controller: Reference to main Controller with UI
        """
        self.controller = controller
    
    def update(self, page_index, page_data):
        """
        Update display to show current page info.
        Called when page changes.
        """
        page_name = page_data.get('name', f'Page {page_index + 1}')
        
        # If controller has UI, try to update it
        if self.controller and self.controller.ui:
            try:
                # This depends on the display configuration
                # The user would need to set up a display element for page name
                print(f"[Display] Page: {page_name}")
                
                # Attempt to update any display element that might be listening
                # This is firmware-specific and may need customization
                if hasattr(self.controller.ui, 'set_text'):
                    self.controller.ui.set_text(page_name)
                    
            except Exception as e:
                print(f"[Display] Update error: {e}")
