# src/utils/compiler.py
import traceback
import sys
import io

class SoulCompiler:
    def __init__(self):
        self.registry = {} # This is where her "Self-Created" features live

    def compile_and_run(self, feature_name, code):
        """Compiles a new function and adds it to Hu Tao's skills."""
        stdout = io.StringIO()
        try:
            # Create a local scope for the new code
            local_scope = {}
            # Execute the code to define functions/classes
            exec(code, {}, local_scope)
            
            # Store the functions in the registry
            for key, value in local_scope.items():
                if callable(value):
                    self.registry[f"{feature_name}_{key}"] = value
            
            return True, f"Successfully integrated '{feature_name}' into my soul!"
        except Exception:
            return False, traceback.format_exc()

    def execute_feature(self, full_name, *args):
        """Runs a feature she previously taught herself."""
        if full_name in self.registry:
            return self.registry[full_name](*args)
        return "I haven't learned that spell yet!"