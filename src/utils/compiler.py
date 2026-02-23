# src/utils/compiler.py
import traceback
import io
import contextlib

class SoulCompiler:
    def __init__(self):
        self.registry = {} # Stores her 'learned' functions

    def compile_and_run(self, feature_name, code):
        """Compiles code and registers all functions inside it."""
        try:
            local_scope = {}
            exec(code, {}, local_scope)
            
            added_any = False
            for key, value in local_scope.items():
                if callable(value):
                    # We store it as featureName_functionName
                    self.registry[f"{feature_name}_{key}"] = value
                    added_any = True
            
            if added_any:
                return True, f"Integrated {feature_name} successfully."
            return False, "No callable functions found in code."
        except Exception:
            return False, traceback.format_exc()

    def execute_feature(self, full_name, *args):
        """Runs a synthesized feature."""
        if full_name in self.registry:
            try:
                # Run the function and return result
                return self.registry[full_name](*args)
            except Exception as e:
                return f"Aiya! My new spell fizzled: {e}"
        return "I haven't synthesized that power yet!"