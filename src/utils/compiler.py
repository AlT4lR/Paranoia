# src/utils/compiler.py
import traceback
import json
import os
from src import config
from src.utils.logger import SoulLogger

class SoulCompiler:
    def __init__(self):
        self.registry = {} 
        # Path to the permanent storage file
        self.storage_path = os.path.join(config.DATA_DIR, "synthesized_spells.json")
        self.load_registry() 

    def load_registry(self):
        """Reloads all saved features from disk when the app starts."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    saved_spells = json.load(f)
                    for name, code in saved_spells.items():
                        # We compile them back into the registry, but set save=False 
                        # so we don't create an infinite loop of saving.
                        self.compile_and_run(name, code, save=False)
                SoulLogger.sys(f"Memory Restored: Loaded {len(saved_spells)} skills.")
            except Exception as e:
                SoulLogger.err(f"Failed to load spells: {e}")

    def _save_spell_to_disk(self, feature_name, code):
        """Helper to physically write the new code to the JSON file."""
        data = {}
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except: 
                data = {} # If file is empty or corrupt, start fresh
        
        data[feature_name] = code
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        SoulLogger.sys(f"Skill '{feature_name}' written to grimoire.")

    def compile_and_run(self, feature_name, code, save=True):
        """Runs the code in a sandbox and registers its functions."""
        try:
            local_scope = {}
            # Executes the string as Python code
            exec(code, {}, local_scope)
            
            added_any = False
            for key, value in local_scope.items():
                if callable(value):
                    # Registers the function so it can be called by name
                    self.registry[f"{feature_name}_{key}"] = value
                    added_any = True
            
            if added_any:
                if save:
                    self._save_spell_to_disk(feature_name, code)
                return True, f"Integrated {feature_name} successfully."
            return False, "No callable functions found in code."
        except Exception:
            return False, traceback.format_exc()

    def execute_feature(self, full_name, *args):
        """Triggers a saved skill."""
        if full_name in self.registry:
            try:
                return self.registry[full_name](*args)
            except Exception as e:
                return f"Aiya! My new spell fizzled: {e}"
        return "I haven't synthesized that power yet!"