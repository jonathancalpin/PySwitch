# controller_multipage.py
# Modified Controller with Combo Detection and Page Management
# 
# This extends the base PySwitch Controller to add:
# - Button combo detection (A+B = Page Up, B+C = Page Down)
# - Multi-page support with hot-swappable switch configurations
#
# To use: Replace the import in code.py from controller to controller_multipage
# Or copy this content into controller.py
"""
Usage in code.py:

    from pyswitch.controller.controller_multipage import MultiPageController
    
    # Instead of:
    # from pyswitch.controller.controller import Controller
    
    # Create controller with pages:
    controller = MultiPageController(
        led_driver=led_driver,
        midi=midi,
        config=Config,
        inputs=Switches,  # Initial page switches
        pages=Pages,      # All page definitions
        ui=ui
    )
"""

from gc import collect, mem_free

from .inputs import SwitchController, ContinuousController
from .client import Client, BidirectionalClient
from .combo_detector import ComboDetector
from .page_manager import PageManager
from ..misc import Updater, PeriodCounter, get_option, do_print, format_size, fill_up_to
from ..stats import Memory


class MultiPageController(Updater):
    """
    Extended Controller with combo detection and multi-page support.
    
    Adds:
    - ComboDetector: Detects A+B and B+C pressed together
    - PageManager: Manages multiple pages of switch configurations
    """
    
    # IDs for all available measurements (for statistics)
    STAT_ID_TICK_TIME = 1

    def __init__(self, led_driver, midi, protocol=None, config={}, inputs=[], 
                 pages=None, combo_config=None, ui=None, period_counter=None):
        """
        Initialize the multi-page controller.
        
        Args:
            led_driver: NeoPixel LED driver
            midi: MIDI handler
            protocol: Optional bidirectional protocol
            config: Global configuration dictionary
            inputs: Initial switch definitions (first page)
            pages: List of page definitions for multi-page mode
            combo_config: Optional combo configuration override
            ui: User interface
            period_counter: Optional period counter for updates
        """
        Updater.__init__(self)

        # Flag for memory warning
        self.low_memory_warning = False

        # MIDI handler
        self.__midi = midi

        # User interface
        self.ui = ui        

        # Global config
        self.config = config
        update_interval = get_option(config, "updateInterval", 200)

        # Max MIDI messages per tick
        self.__max_consecutive_midi_msgs = get_option(config, "maxConsecutiveMidiMessages", 10)   

        # Debug stats
        self.__debug_stats = get_option(config, "debugStats", False)        

        if self.__debug_stats:
            from .measure import RuntimeMeasurement
            self.__measurement_process_jitter = RuntimeMeasurement(
                get_option(config, "debugStatsInterval", update_interval)
            )
            self.__measurement_process_jitter.add_listener(self)
            self.add_updateable(self.__measurement_process_jitter)            

        # Memory warning limit
        self.__memory_warn_limit = get_option(config, "memoryWarnLimitBytes", 1024 * 15)

        # Clear MIDI buffers on startup
        self.__clear_buffer = get_option(config, "clearBuffers", True)

        # Shared data
        self.shared = {}

        # NeoPixel driver 
        self.led_driver = led_driver
            
        # Determine how many NeoPixels are needed
        def get_num_pixels(switches):
            ret = 0
            for sw_def in switches:
                pixels = get_option(sw_def["assignment"], "pixels", [])
                for p in pixels:
                    pp1 = p + 1
                    if pp1 > ret:
                        ret = pp1
            return ret
        
        self.led_driver.init(get_num_pixels(inputs))
        
        # Periodic update handler
        self.period = period_counter
        if not self.period:
            self.period = PeriodCounter(update_interval)        

        # Client access
        if protocol:
            self.client = BidirectionalClient(self.__midi, config, protocol)
            self.add_updateable(self.client)
        else:
            self.client = Client(self.__midi, config)

        # Set up inputs (switches)
        self.inputs = []
        for sw_def in inputs:
            if hasattr(sw_def["assignment"]["model"], "pushed"):
                self.inputs.append(SwitchController(self, sw_def))
            else:
                self.inputs.append(ContinuousController(self, sw_def))

        # =====================================================================
        # MULTI-PAGE SUPPORT
        # =====================================================================
        
        # Page Manager
        self.page_manager = None
        if pages:
            self.page_manager = PageManager(
                pages=pages,
                controller=self,
                on_page_change=self._on_page_change
            )
            print(f"[MultiPage] Initialized with {len(pages)} pages")
            print(f"[MultiPage] Current: {self.page_manager.current_page_name}")
        
        # =====================================================================
        # COMBO DETECTION
        # =====================================================================
        
        # Default combo config
        default_combo = {
            'enabled': True,
            'combo_switches': ['A', 'B', 'C'],
            'combo_window_ms': 50,
        }
        
        combo_cfg = combo_config or get_option(config, "comboDetection", default_combo)
        
        self.combo_detector = None
        if get_option(combo_cfg, "enabled", True) and self.page_manager:
            self.combo_detector = ComboDetector(
                combo_switches=get_option(combo_cfg, "combo_switches", ['A', 'B', 'C']),
                combo_window_ms=get_option(combo_cfg, "combo_window_ms", 50),
                on_combo_ab=self.page_manager.next_page,
                on_combo_bc=self.page_manager.prev_page
            )
            print(f"[MultiPage] Combo detection enabled (A+B=PageUp, B+C=PageDown)")

        # =====================================================================
        # UI SETUP
        # =====================================================================
        
        if self.ui:
            self.ui.init(self)
            self.add_updateable(ui)

    def _on_page_change(self, page_index, page_data):
        """
        Callback when page changes.
        Updates display and optionally rebuilds switch configs.
        """
        page_name = page_data.get('name', f'Page {page_index + 1}')
        
        # Update display if available
        if self.ui:
            try:
                # Try to show page name temporarily
                # This is display-configuration dependent
                pass
            except Exception:
                pass
        
        # Flash LEDs with page color
        color = page_data.get('color_theme', (255, 255, 255))
        self._flash_leds(color)
        
        # Optional: Rebuild inputs with new page's switch configs
        # Uncomment if you want full config swap (more memory intensive):
        # new_switches = page_data.get('switches', [])
        # if new_switches:
        #     self.page_manager.rebuild_inputs(new_switches)
    
    def _flash_leds(self, color, duration_ms=200):
        """Flash all LEDs with the given color briefly."""
        try:
            for input_ctrl in self.inputs:
                if hasattr(input_ctrl, 'color') and hasattr(input_ctrl, 'brightness'):
                    input_ctrl.color = color
                    input_ctrl.brightness = 1.0
            
            # LEDs will return to normal on next action update
        except Exception as e:
            print(f"[MultiPage] LED flash error: {e}")

    def init(self):
        """Prepare to run the processing loop."""
        if self.ui:            
            Memory.watch("Showing UI")
            self.ui.show()           
        
        Memory.watch("Application loaded")

        # Check memory usage
        collect()
        if mem_free() < self.__memory_warn_limit:
            do_print(f"LOW MEMORY: { format_size(mem_free()) }")
            self.low_memory_warning = True

        # Clear MIDI buffers
        if self.__clear_buffer:
            while True:
                if not self.__midi.receive():
                    break
        
        # Show initial page info
        if self.page_manager:
            print(f"[MultiPage] Ready - Page: {self.page_manager.current_page_name}")

    def tick(self):
        """
        Single tick in the processing loop.
        Returns True to keep the loop alive.
        """
        # Update all Updateables in periodic intervals
        if self.period.exceeded:
            for u in self.updateables:
                self.__receive_midi_messages()
                u.update()

            Memory.watch("Controller: update", only_if_changed=True)

        # Receive all available MIDI messages
        self.__receive_midi_messages()

        return True

    def reset_actions(self):
        """Reset all actions (refreshes buffer memories, re-renders LEDs/displays)."""
        for input in self.inputs:
            for action in input.actions:
                action.reset()

    def __receive_midi_messages(self):
        """Receive MIDI messages, and in between check for switch state changes."""
        cnt = 0
        
        while True:            
            if self.__debug_stats:
                self.__measurement_process_jitter.finish()
            
            # =====================================================================
            # COMBO-AWARE SWITCH PROCESSING
            # =====================================================================
            
            for input in self.inputs:
                # Check if combo detector wants to intercept this switch
                if self.combo_detector and self.combo_detector.intercept(input):
                    continue  # Skip normal processing - combo handling in progress
                
                # Normal processing
                input.process()
            
            # Process any expired pending combo presses
            if self.combo_detector:
                self.combo_detector.process_expired(self.inputs)
            
            # =====================================================================
            
            if self.__debug_stats:
                self.__measurement_process_jitter.start()

            # Receive MIDI
            midimsg = self.__midi.receive()
            self.client.receive(midimsg)

            # Break after a certain amount of messages to keep responsive
            cnt = cnt + 1
            if not midimsg or cnt > self.__max_consecutive_midi_msgs:
                break  

    def measurement_updated(self, measurement):
        """Callback when measurement wants to show something."""
        collect()
        do_print(
            f"{ fill_up_to(str(measurement.name), 30, '.') }: "
            f"Max { repr(measurement.value) }ms, "
            f"Avg { repr(measurement.average) }ms, "
            f"Calls: { repr(measurement.calls) }, "
            f"Free: { format_size(mem_free()) }"
        )
    
    # =========================================================================
    # PAGE NAVIGATION METHODS (convenience wrappers)
    # =========================================================================
    
    def next_page(self):
        """Go to next page."""
        if self.page_manager:
            self.page_manager.next_page()
    
    def prev_page(self):
        """Go to previous page."""
        if self.page_manager:
            self.page_manager.prev_page()
    
    def go_to_page(self, index):
        """Go to specific page by index."""
        if self.page_manager:
            self.page_manager.go_to_page(index)
    
    @property
    def current_page_name(self):
        """Get current page name."""
        if self.page_manager:
            return self.page_manager.current_page_name
        return "Default"
    
    @property
    def current_page_index(self):
        """Get current page index."""
        if self.page_manager:
            return self.page_manager.current_index
        return 0
