import libcst
import json 

from .InputsExtractor import InputsExtractor
from .SplashesExtractor import SplashesExtractor
from .ComboConfigExtractor import ComboConfigExtractor, PagesExtractor
from .ComboCodeGenerator import ComboCodeGenerator, generate_default_combo_config, generate_default_pages

from .misc.CodeGenerator import CodeGenerator
from .misc.RemoveUnusedImportTransformer import RemoveUnusedImportTransformer
from .misc.AddImportsTransformer import AddImportsTransformer
from .misc.AssignmentNameExtractor import AssignmentNameExtractor
from .misc.AssignmentExtractor import AssignmentExtractor
from .misc.ImportExtractor import ImportExtractor
from .misc.ReplaceAssignmentTransformer import ReplaceAssignmentTransformer
from .misc.AddAssignmentTransformer import AddAssignmentTransformer
from .misc.ClassNameExtractor import ClassNameExtractor

class PySwitchParser:

    def __init__(self, hw_import_path, available_clients_json):
        self.hw_import_path = hw_import_path       
        self.__csts = None
        
        self.clients = json.loads(available_clients_json)

        # Buffers
        self.__available_actions = None
        self.__available_mappings = None
        self.__available_display_imports = None
        
    # Set the parser data from source code
    def from_source(self, inputs_py, display_py):
        self.__csts = {
            "inputs_py": libcst.parse_module(inputs_py),
            "display_py": libcst.parse_module(display_py)
        }

    # Returns a dict holding the sources for the current configuration
    def to_source(self):
        if not self.__csts:
            raise Exception("No data loaded")
        
        self._add_all_possible_imports()
        self._remove_unused_imports()

        return {
            "inputs_py": self.__csts["inputs_py"].code,
            "display_py": self.__csts["display_py"].code
        }
    
    # Delivers code for a node of tree data. Cannot add assignments!
    def code_for_data_node(self, data, format = False):
        if isinstance(data, str):
            return data
        
        node = CodeGenerator(format = format).generate(data.to_py())
        return libcst.parse_module("").code_for_node(node)
    
    # Returns a JSON encoded tree of the Inputs assign in inputs.py
    def inputs(self):
        if not self.__csts:
            raise Exception("No data loaded")
                
        inputs = InputsExtractor(self, self.__csts["inputs_py"]).get("Inputs")
        return json.dumps(inputs)
    
    # Replace the inputs in inputs.py
    def set_inputs(self, inputs):
        if not self.__csts:
            raise Exception("No data loaded")
        
        # Remove first assign as this can lead to endless recursion and is not relevant anyway
        inputs_py = inputs.to_py()
        if "assign" in inputs_py: 
            inputs_py["assign"] = None

        inputs_node = CodeGenerator(
            parser = self, 
            file_id = "inputs_py", 
            insert_before_assign = "Inputs",
            format = True
        ).generate(inputs_py)
        
        self.set_assignment("Inputs", inputs_node, "inputs_py")

    # Searches for an Assign with the given name and returns its node, or None if not found
    def get_assignment(self, name, file_id):
        assignments = AssignmentExtractor().get(self.__csts[file_id])
        
        for a in assignments:
            if a["name"] == name:
                return a["node"]
            
        return None

    #######################################################################################

    # Returns a JSON encoded list of assignments in display.py TODO remove
    def displays(self):
        if not self.__csts:
            raise Exception("No data loaded")
        
        return json.dumps(AssignmentNameExtractor().get(self.__csts["display_py"]))
    
    # Returns a JSON encoded tree of the Splashes assign in display.py
    def splashes(self):
        if not self.__csts:
            raise Exception("No data loaded")
                
        splashes = SplashesExtractor(self, self.__csts["display_py"]).get("Splashes")
        return json.dumps(splashes)

    # Replace the splashes in display.py
    def set_splashes(self, splashes):
        if not self.__csts:
            raise Exception("No data loaded")

        # Remove first assign as this can lead to endless recursion and is not relevant anyway
        splashes_py = splashes.to_py()
        if "assign" in splashes_py: 
            splashes_py["assign"] = None

        splashes_node = CodeGenerator(
            parser = self, 
            file_id = "display_py", 
            insert_before_assign = "Splashes",
            format = True
        ).generate(splashes_py)
        
        self.set_assignment("Splashes", splashes_node, "display_py")

    ########################################################################################
        
    # Adds or replaces the given assignment by name.
    def set_assignment(self, name, call_node, file_id, insert_before_assign = None):
        replacer = ReplaceAssignmentTransformer(name, call_node)
        self.__csts[file_id] = self.__csts[file_id].visit(replacer)
        if replacer.replaced:
            return

        adder = AddAssignmentTransformer(
            name, 
            call_node, 
            insert_before_assign = insert_before_assign, 
            cst = self.__csts[file_id] if not insert_before_assign else None
        )

        self.__csts[file_id] = self.__csts[file_id].visit(adder)

    ########################################################################################

    # Remove unused imports on all files. Does no config update!
    def _remove_unused_imports(self):
        self._remove_unused_import_for_file("inputs_py")
        self._remove_unused_import_for_file("display_py")

    def _remove_unused_import_for_file(self, file_id):
        wrapper = libcst.metadata.MetadataWrapper(self.__csts[file_id])
        visitor = RemoveUnusedImportTransformer(wrapper)
        self.__csts[file_id] = wrapper.module.visit(visitor)

    ########################################################################################

    # Adds all possible imports (actions etc.) Does no config update!
    def _add_all_possible_imports(self):
        self._add_all_possible_imports_inputs()
        self._add_all_possible_imports_display()

    def _add_all_possible_imports_inputs(self):
        if not self.__available_actions:
            self.__available_actions = self._generate_action_imports()

        if not self.__available_mappings:
            self.__available_mappings = self._generate_mapping_imports()    
        
        display_assignments = [
            { 
                "name": assign, 
                "importPath": "display" 
            } 
            for assign in AssignmentNameExtractor().get(self.__csts["display_py"])
        ]

        # Add all imports
        visitor = AddImportsTransformer(self.__available_actions + self.__available_mappings + display_assignments)
        self.__csts["inputs_py"] = self.__csts["inputs_py"].visit(visitor)

    def _add_all_possible_imports_display(self):
        if not self.__available_display_imports:
            self.__available_display_imports = self._generate_display_imports()

        # Add all imports
        visitor = AddImportsTransformer(self.__available_display_imports)
        self.__csts["display_py"] = self.__csts["display_py"].visit(visitor)
            
    # Generates all client specific display assigns (everything from the client's __init__.py file and some standards)
    def _generate_display_imports(self):
        ret = []

        # Load callback definitions from file
        with open('definitions/callbacks.json') as f: available_callbacks_json = f.read()
        
        clients = json.loads(available_callbacks_json)
        
        for client in clients:
            ret += client["callbacks"]

        # Get __init__ classes of clients
        for client in self.clients:
            ret += ClassNameExtractor(
                file = "pyswitch/clients/" + client + "/__init__.py", 
                import_path = "pyswitch.clients." + client
            ).get()
        
        return ret + [
            {
                "name": "const",
                "importPath": "micropython"
            },

            {
                "name": "Colors",
                "importPath": "pyswitch.colors"
            },
            {
                "name": "DEFAULT_LABEL_COLOR",
                "importPath": "pyswitch.colors"
            },

            {
                "name": "DisplayElement",
                "importPath": "pyswitch.ui.ui"
            },
            {
                "name": "DisplayBounds",
                "importPath": "pyswitch.ui.ui"
            },
            {
                "name": "DisplayLabel",
                "importPath": "pyswitch.ui.elements"
            },
            {
                "name": "BidirectionalProtocolState",
                "importPath": "pyswitch.ui.elements"
            },
            {
                "name": "PYSWITCH_VERSION",
                "importPath": "pyswitch.misc"
            }
        ]
    
    # Generates all imports for actions
    def _generate_action_imports(self):
        # Load actions definitions from file
        with open('definitions/actions.json') as f: available_actions_json = f.read()
        
        clients = json.loads(available_actions_json)
        actions = []

        for client in clients:
            actions += client["actions"]

        # Add additional potentially needed imports besides the actions.
        return actions + [
            # Additional imports: Colors
            {
                "name": "Colors",
                "importPath": "pyswitch.colors"
            },
            {
                "name": "DEFAULT_SWITCH_COLOR",
                "importPath": "pyswitch.colors"
            },

            # RIG_SELECT display modes (TODO move to client code)
            {
                "name": "RIG_SELECT_DISPLAY_CURRENT_RIG",
                "importPath": "pyswitch.clients.kemper.actions.rig_select"
            },
            {
                "name": "RIG_SELECT_DISPLAY_TARGET_RIG",
                "importPath": "pyswitch.clients.kemper.actions.rig_select"
            },

            # Fixed FX slot IDs (TODO move to client code)
            {
                "name": "FIXED_SLOT_ID_TRANSPOSE",
                "importPath": "pyswitch.clients.kemper.actions.fixed_fx"
            },
            {
                "name": "FIXED_SLOT_ID_GATE",
                "importPath": "pyswitch.clients.kemper.actions.fixed_fx"
            },
            {
                "name": "FIXED_SLOT_ID_COMP",
                "importPath": "pyswitch.clients.kemper.actions.fixed_fx"
            },
            {
                "name": "FIXED_SLOT_ID_BOOST",
                "importPath": "pyswitch.clients.kemper.actions.fixed_fx"
            },
            {
                "name": "FIXED_SLOT_ID_WAH",
                "importPath": "pyswitch.clients.kemper.actions.fixed_fx"
            },
            {
                "name": "FIXED_SLOT_ID_CHORUS",
                "importPath": "pyswitch.clients.kemper.actions.fixed_fx"
            },
            {
                "name": "FIXED_SLOT_ID_AIR",
                "importPath": "pyswitch.clients.kemper.actions.fixed_fx"
            },
            {
                "name": "FIXED_SLOT_ID_DBL_TRACKER",
                "importPath": "pyswitch.clients.kemper.actions.fixed_fx"
            },

            # Effect slot definitions (TODO move to client code)
            {
                "name": "KemperEffectSlot",
                "importPath": "pyswitch.clients.kemper"
            },

            # Callbacks
            {
                "name": "BinaryParameterCallback",
                "importPath": "pyswitch.controller.callbacks"
            },

            # PushButtonAction
            {
                "name": "PushButtonAction",
                "importPath": "pyswitch.controller.actions"
            },

            # HID Keycodes
            {
                "name": "Keycode",
                "importPath": "adafruit_hid.keycode"
            },
            {
                "name": "PYSWITCH_VERSION",
                "importPath": "pyswitch.misc"
            }
        ]
    
    # Generates all imports for mappings
    def _generate_mapping_imports(self):
        # Load actions definitions from file
        with open('definitions/mappings.json') as f: available_mappings_json = f.read()
        
        clients = json.loads(available_mappings_json)
        mappings = []

        for client in clients:
            mappings = mappings + client["mappings"]

        return mappings
    
    ##############################################################################################

    # Determine the client for an Action instance
    def _determine_import_statement(self, name, cst):
        visitor = ImportExtractor(name)
        cst.visit(visitor)
        return visitor.result

    # Determine the client for a type name. You must pass either cst or file_id.
    def determine_client(self, name, file_id = None, cst = None):
        import_statement = self._determine_import_statement(name, self.__csts[file_id] if file_id else cst)
        
        if not import_statement:
            # No import statement: Perhaps this is defined in inputs.py directly, so we have no client
            return "local"

        for client in self.clients:
            if client in import_statement:
                 return client

        return "local"

    ##############################################################################################
    # COMBO PAGE NAVIGATION SUPPORT
    ##############################################################################################

    def has_combo_config(self):
        """Check if this configuration uses combo-based page navigation."""
        if not self.__csts:
            raise Exception("No data loaded")
        
        extractor = ComboConfigExtractor(self, self.__csts["inputs_py"])
        return extractor.has_combo_config()
    
    def combo_config(self):
        """
        Returns the ComboConfig dictionary as JSON, or None if not found.
        
        Expected format:
        {
            "enabled": True,
            "combo_switches": ['A', 'B', 'C'],
            "combo_window_ms": 50,
        }
        """
        if not self.__csts:
            raise Exception("No data loaded")
        
        extractor = ComboConfigExtractor(self, self.__csts["inputs_py"])
        config = extractor.get_combo_config()
        return json.dumps(config) if config else None
    
    def set_combo_config(self, combo_config):
        """
        Set or update the ComboConfig in inputs.py.
        combo_config should be a dict-like object with to_py() method.
        """
        if not self.__csts:
            raise Exception("No data loaded")
        
        config_py = combo_config.to_py() if hasattr(combo_config, 'to_py') else combo_config
        
        config_node = CodeGenerator(
            parser = self, 
            file_id = "inputs_py", 
            format = True
        ).generate(config_py)
        
        self.set_assignment("ComboConfig", config_node, "inputs_py")
    
    def pages(self):
        """
        Returns all page definitions as JSON.
        
        Returns a list of page objects with structure:
        [
            {
                "var_name": "PAGE_LOGIC",
                "data": {
                    "name": "Logic",
                    "channel": 1,
                    "midi_out": "USB",
                    "color_theme": [0, 0, 255],
                    "switches": [...]
                }
            },
            ...
        ]
        """
        if not self.__csts:
            raise Exception("No data loaded")
        
        extractor = PagesExtractor(self, self.__csts["inputs_py"])
        pages = extractor.get_all_pages()
        return json.dumps(pages)
    
    def pages_order(self):
        """
        Returns the ordered list of page variable names from the Pages array.
        Example: ["PAGE_LOGIC", "PAGE_TONEX", "PAGE_GP5", "PAGE_LOOPER"]
        """
        if not self.__csts:
            raise Exception("No data loaded")
        
        extractor = ComboConfigExtractor(self, self.__csts["inputs_py"])
        pages_list = extractor.get_pages()
        
        # The Pages list contains references to page variables
        # Extract just the names
        if isinstance(pages_list, list):
            return json.dumps(pages_list)
        return json.dumps([])
    
    def set_page(self, page_name, page_data):
        """
        Set or update a specific page definition (e.g., PAGE_LOGIC).
        """
        if not self.__csts:
            raise Exception("No data loaded")
        
        page_py = page_data.to_py() if hasattr(page_data, 'to_py') else page_data
        
        page_node = CodeGenerator(
            parser = self, 
            file_id = "inputs_py", 
            format = True
        ).generate(page_py)
        
        self.set_assignment(page_name, page_node, "inputs_py")
    
    def set_pages_order(self, pages_list):
        """
        Set the Pages array order.
        pages_list should be a list of page variable names.
        """
        if not self.__csts:
            raise Exception("No data loaded")
        
        pages_py = pages_list.to_py() if hasattr(pages_list, 'to_py') else pages_list
        
        pages_node = CodeGenerator(
            parser = self, 
            file_id = "inputs_py", 
            format = True
        ).generate(pages_py)
        
        self.set_assignment("Pages", pages_node, "inputs_py")
    
    def generate_combo_inputs(self, pages_data, combo_config):
        """
        Generate a complete inputs.py file for combo page navigation.
        
        Args:
            pages_data: List of page definitions (as JSON string or list)
            combo_config: Combo configuration (as JSON string or dict)
        
        Returns:
            Complete inputs.py source code as string
        """
        if isinstance(pages_data, str):
            pages_data = json.loads(pages_data)
        if isinstance(combo_config, str):
            combo_config = json.loads(combo_config)
        
        generator = ComboCodeGenerator()
        return generator.generate_full_file(pages_data, combo_config)
    
    def create_combo_config_template(self):
        """
        Generate a default combo configuration template.
        Returns JSON string.
        """
        return json.dumps(generate_default_combo_config())
    
    def create_default_pages_template(self):
        """
        Generate default page definitions.
        Returns JSON string.
        """
        return json.dumps(generate_default_pages())