"""
ComboConfigExtractor.py

Extracts combo configuration and page definitions from custom PySwitch inputs.py
for the combo-based page navigation system.
"""

from .misc.CodeExtractor import CodeExtractor
from .misc.AssignmentExtractor import AssignmentExtractor
import json


class ComboConfigExtractor(CodeExtractor):
    """
    Extracts ComboConfig and Pages from the custom PySwitch inputs.py format.
    
    Expected format in inputs.py:
    
    ComboConfig = {
        "enabled": True,
        "combo_switches": ['A', 'B', 'C'],
        "combo_window_ms": 50,
    }
    
    Pages = [
        PAGE_LOGIC,
        PAGE_TONEX,
        ...
    ]
    
    PAGE_LOGIC = {
        "name": "Logic",
        "channel": 1,
        "midi_out": "USB",
        "color_theme": (0, 0, 255),
        "switches": [...]
    }
    """
    
    def __init__(self, parser, cst):
        super().__init__(cst)
        self.parser = parser
        
    def get_combo_config(self):
        """
        Extract the ComboConfig dictionary from inputs.py.
        Returns None if not found.
        """
        try:
            config = self.get("ComboConfig")
            return config
        except:
            return None
    
    def get_pages(self):
        """
        Extract the Pages list from inputs.py.
        Returns an empty list if not found.
        """
        try:
            pages = self.get("Pages")
            return pages if pages else []
        except:
            return []
    
    def has_combo_config(self):
        """Check if this inputs.py uses the combo page system."""
        assignments = AssignmentExtractor().get(self.cst)
        
        for a in assignments:
            if a["name"] == "ComboConfig":
                return True
        return False
    
    def has_pages(self):
        """Check if this inputs.py has a Pages array."""
        assignments = AssignmentExtractor().get(self.cst)
        
        for a in assignments:
            if a["name"] == "Pages":
                return True
        return False


class PagesExtractor(CodeExtractor):
    """
    Extracts individual page definitions (PAGE_XXX dictionaries).
    """
    
    def __init__(self, parser, cst):
        super().__init__(cst)
        self.parser = parser
        
    def get_page(self, page_name):
        """
        Extract a specific page definition by name (e.g., "PAGE_LOGIC").
        """
        try:
            return self.get(page_name)
        except:
            return None
    
    def get_all_pages(self):
        """
        Find all PAGE_* definitions in the file.
        Returns a list of tuples: (name, page_data)
        """
        assignments = AssignmentExtractor().get(self.cst)
        pages = []
        
        for a in assignments:
            if a["name"].startswith("PAGE_"):
                try:
                    page_data = self.get(a["name"])
                    pages.append({
                        "var_name": a["name"],
                        "data": page_data
                    })
                except:
                    pass
                    
        return pages
