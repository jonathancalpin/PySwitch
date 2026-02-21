"""
ComboCodeGenerator.py

Generates valid inputs.py code for the combo-based page navigation system.
This generates the complete file structure including:
- Imports
- Color definitions
- Helper functions
- Page definitions
- Pages array
- ComboConfig
- Inputs assignment
"""

import libcst
from .misc.CodeGenerator import CodeGenerator


class ComboCodeGenerator:
    """
    Generates inputs.py code for combo page navigation.
    """
    
    # Template for the file header
    HEADER_TEMPLATE = '''##############################################################################
#
# Multi-Device MIDI Controller Configuration
# MIDI Captain Mini 6 with PySwitch + Combo Page Navigation
#
# Page Navigation (via combo detection):
#   A+B pressed together = Page Up
#   B+C pressed together = Page Down
#
##############################################################################
'''

    # Import statements
    IMPORTS_TEMPLATE = '''from pyswitch.hardware.devices.pa_midicaptain_mini_6 import (
    PA_MIDICAPTAIN_MINI_SWITCH_1,
    PA_MIDICAPTAIN_MINI_SWITCH_2,
    PA_MIDICAPTAIN_MINI_SWITCH_3,
    PA_MIDICAPTAIN_MINI_SWITCH_A,
    PA_MIDICAPTAIN_MINI_SWITCH_B,
    PA_MIDICAPTAIN_MINI_SWITCH_C,
)

from pyswitch.clients.local.actions.custom import CUSTOM_MESSAGE
'''

    # Color definitions
    COLORS_TEMPLATE = '''##############################################################################
# COLOR DEFINITIONS (RGB tuples)
##############################################################################

COLOR_RED = (255, 0, 0)
COLOR_ORANGE = (255, 128, 0)
COLOR_YELLOW = (255, 255, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_CYAN = (0, 255, 255)
COLOR_BLUE = (0, 128, 255)
COLOR_PURPLE = (128, 0, 255)
COLOR_PINK = (255, 0, 128)
COLOR_WHITE = (255, 255, 255)
'''

    # Helper functions
    HELPERS_TEMPLATE = '''##############################################################################
# MIDI MESSAGE HELPERS
##############################################################################

def cc_toggle(channel, cc, color, text, page_id, display=None):
    """Create a CC toggle action (on=127, off=0)."""
    ch = channel - 1
    return CUSTOM_MESSAGE(
        message=[0xB0 + ch, cc, 127],
        message_release=[0xB0 + ch, cc, 0],
        color=color,
        text=text,
        id=page_id,
        enable_callback=_pager.enable_callback,
        toggle=True,
        led_brightness=0.3,
        led_brightness_off=0.02,
        display=display,
    )

def cc_momentary(channel, cc, color, text, page_id, display=None):
    """Create a CC momentary action (127 on press, 0 on release)."""
    ch = channel - 1
    return CUSTOM_MESSAGE(
        message=[0xB0 + ch, cc, 127],
        message_release=[0xB0 + ch, cc, 0],
        color=color,
        text=text,
        id=page_id,
        enable_callback=_pager.enable_callback,
        display=display,
    )

def pc_select(channel, pc, color, text, page_id, display=None):
    """Create a Program Change action with radio-button group."""
    ch = channel - 1
    return CUSTOM_MESSAGE(
        message=[0xC0 + ch, pc],
        message_release=None,
        color=color,
        text=text,
        id=page_id,
        enable_callback=_pager.enable_callback,
        display=display,
        group=f"pc_ch{channel}",
        led_brightness=0.3,
        led_brightness_off=0.02,
    )
'''

    def __init__(self):
        pass
    
    def generate_full_file(self, pages_data, combo_config):
        """
        Generate a complete inputs.py file.
        
        Args:
            pages_data: List of page definitions, each with:
                - var_name: Variable name (e.g., "PAGE_LOGIC")
                - data: Page data dict with name, channel, midi_out, color_theme, switches
            combo_config: Combo configuration dict with:
                - enabled: bool
                - combo_switches: list of switch names
                - combo_window_ms: int
        
        Returns:
            Complete inputs.py source code as string
        """
        parts = [
            self.HEADER_TEMPLATE,
            self.IMPORTS_TEMPLATE,
            self.COLORS_TEMPLATE,
            self.HELPERS_TEMPLATE,
        ]
        
        # Generate each page definition
        for page in pages_data:
            parts.append(self._generate_page(page))
        
        # Generate Pages array
        parts.append(self._generate_pages_array(pages_data))
        
        # Generate ComboConfig
        parts.append(self._generate_combo_config(combo_config))
        
        # Generate Inputs assignment
        parts.append(self._generate_inputs_assignment(pages_data))
        
        return '\n'.join(parts)
    
    def _generate_page(self, page):
        """Generate a single page definition."""
        var_name = page.get('var_name', 'PAGE_UNNAMED')
        data = page.get('data', {})
        
        name = data.get('name', 'Page')
        channel = data.get('channel', 1)
        midi_out = data.get('midi_out', 'USB')
        color_theme = data.get('color_theme', [255, 255, 255])
        switches = data.get('switches', [])
        
        # Format color theme
        if isinstance(color_theme, list):
            color_str = f"({color_theme[0]}, {color_theme[1]}, {color_theme[2]})"
        else:
            color_str = str(color_theme)
        
        lines = [
            f'##############################################################################',
            f'# {name.upper()} (Channel {channel})',
            f'##############################################################################',
            f'',
            f'{var_name} = {{',
            f'    "name": "{name}",',
            f'    "channel": {channel},',
            f'    "midi_out": "{midi_out}",',
            f'    "color_theme": {color_str},',
            f'    "switches": [',
        ]
        
        # Add switches
        for switch in switches:
            lines.append(self._generate_switch(switch, channel))
        
        lines.append('    ]')
        lines.append('}')
        lines.append('')
        
        return '\n'.join(lines)
    
    def _generate_switch(self, switch, channel):
        """Generate a switch definition."""
        assignment = switch.get('assignment', 'PA_MIDICAPTAIN_MINI_SWITCH_1')
        actions = switch.get('actions', [])
        
        if not actions:
            # Generate a default action
            return f'''        {{
            "assignment": {assignment},
            "actions": []
        }},'''
        
        # For now, just preserve the action structure
        # In a full implementation, we'd parse and regenerate the action calls
        actions_str = self._format_actions(actions, channel)
        
        return f'''        {{
            "assignment": {assignment},
            "actions": [{actions_str}]
        }},'''
    
    def _format_actions(self, actions, channel):
        """Format action definitions."""
        if not actions:
            return ''
        
        # This is a simplified version - in production, we'd parse
        # the action structure and regenerate proper function calls
        action_strs = []
        for action in actions:
            if isinstance(action, dict):
                action_type = action.get('type', 'cc_toggle')
                cc = action.get('cc', 80)
                color = action.get('color', 'COLOR_WHITE')
                text = action.get('text', 'Action')
                
                action_strs.append(f'{action_type}({channel}, {cc}, {color}, "{text}")')
            else:
                # Already formatted string
                action_strs.append(str(action))
        
        return ', '.join(action_strs)
    
    def _generate_pages_array(self, pages_data):
        """Generate the Pages array."""
        page_names = [p.get('var_name', 'PAGE_UNNAMED') for p in pages_data]
        
        lines = [
            '##############################################################################',
            '# ALL PAGES COLLECTION',
            '##############################################################################',
            '',
            'Pages = [',
        ]
        
        for name in page_names:
            lines.append(f'    {name},')
        
        lines.append(']')
        lines.append('')
        
        return '\n'.join(lines)
    
    def _generate_combo_config(self, combo_config):
        """Generate the ComboConfig dictionary."""
        enabled = combo_config.get('enabled', True)
        switches = combo_config.get('combo_switches', ['A', 'B', 'C'])
        window_ms = combo_config.get('combo_window_ms', 50)
        
        switches_str = ', '.join([f"'{s}'" for s in switches])
        
        lines = [
            '##############################################################################',
            '# COMBO DETECTION CONFIGURATION',
            '##############################################################################',
            '',
            'ComboConfig = {',
            f'    "enabled": {enabled},',
            f'    "combo_switches": [{switches_str}],',
            f'    "combo_window_ms": {window_ms},',
            '}',
            '',
        ]
        
        return '\n'.join(lines)
    
    def _generate_inputs_assignment(self, pages_data):
        """Generate the Inputs assignment."""
        if not pages_data:
            return 'Inputs = []\n'
        
        first_page = pages_data[0].get('var_name', 'PAGE_UNNAMED')
        
        lines = [
            '##############################################################################',
            '# INITIAL INPUTS (First page - required by PySwitch)',
            '##############################################################################',
            '',
            f'Inputs = {first_page}["switches"]',
            '',
        ]
        
        return '\n'.join(lines)
    
    def generate_page_template(self, page_name, display_name, channel=1):
        """
        Generate a new page template with default switches.
        """
        return {
            'var_name': page_name,
            'data': {
                'name': display_name,
                'channel': channel,
                'midi_out': 'USB',
                'color_theme': [255, 255, 255],
                'switches': [
                    {
                        'assignment': 'PA_MIDICAPTAIN_MINI_SWITCH_1',
                        'actions': [{'type': 'cc_toggle', 'cc': 80, 'color': 'COLOR_WHITE', 'text': 'SW1'}]
                    },
                    {
                        'assignment': 'PA_MIDICAPTAIN_MINI_SWITCH_2',
                        'actions': [{'type': 'cc_toggle', 'cc': 81, 'color': 'COLOR_WHITE', 'text': 'SW2'}]
                    },
                    {
                        'assignment': 'PA_MIDICAPTAIN_MINI_SWITCH_3',
                        'actions': [{'type': 'cc_toggle', 'cc': 82, 'color': 'COLOR_WHITE', 'text': 'SW3'}]
                    },
                    {
                        'assignment': 'PA_MIDICAPTAIN_MINI_SWITCH_A',
                        'actions': [{'type': 'cc_toggle', 'cc': 83, 'color': 'COLOR_WHITE', 'text': 'SWA'}]
                    },
                    {
                        'assignment': 'PA_MIDICAPTAIN_MINI_SWITCH_B',
                        'actions': [{'type': 'cc_toggle', 'cc': 84, 'color': 'COLOR_WHITE', 'text': 'SWB'}]
                    },
                    {
                        'assignment': 'PA_MIDICAPTAIN_MINI_SWITCH_C',
                        'actions': [{'type': 'cc_toggle', 'cc': 85, 'color': 'COLOR_WHITE', 'text': 'SWC'}]
                    },
                ]
            }
        }


def generate_default_combo_config():
    """Generate a default combo configuration."""
    return {
        'enabled': True,
        'combo_switches': ['A', 'B', 'C'],
        'combo_window_ms': 50
    }


def generate_default_pages():
    """Generate default page definitions."""
    generator = ComboCodeGenerator()
    return [
        generator.generate_page_template('PAGE_1', 'Page 1', 1),
        generator.generate_page_template('PAGE_2', 'Page 2', 2),
    ]
