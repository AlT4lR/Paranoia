import os
import re
from src.utils.logger import SoulLogger

# The path to the Grimoire where Hu Tao stores her self-taught "spells"
DYNAMIC_FILE = os.path.join(os.path.dirname(__file__), "dynamic_features.py")

def save_new_capability(feature_name: str, code: str, compiler):
    """
    Saves synthesized code to the persistent grimoire. 
    If the feature exists, she refactors it; if not, she etches it.
    Then, it immediately injects the logic into the live system.
    """
    try:
        current_content = ""
        is_new_file = not os.path.exists(DYNAMIC_FILE)
        
        if not is_new_file:
            with open(DYNAMIC_FILE, "r", encoding="utf-8") as f:
                current_content = f.read()

        # 1. EVOLUTION LOGIC: Refactor or Append
        # Look for the function signature to see if we've taught her this before
        func_pattern = f"def {feature_name}\("
        
        if re.search(func_pattern, current_content):
            SoulLogger.sys(f"Evolution: Refactoring existing feature '{feature_name}'...")
            # We append with a 'Refactored' tag. 
            # Note: Python will use the last defined version of a function in a file.
            new_entry = f"\n\n# --- Refactored Version: {feature_name} ---\n{code}\n"
        else:
            SoulLogger.sys(f"Evolution: Etching new capability '{feature_name}'...")
            new_entry = f"\n\n{code}\n"

        # 2. PHYSICAL PERSISTENCE
        with open(DYNAMIC_FILE, "a", encoding="utf-8") as f:
            if is_new_file:
                f.write("# --- HU TAO'S DYNAMIC GRIMOIRE ---\n")
                f.write("# This file contains self-taught Python functions.\n")
                f.write("# Handle with care; the spirits are sensitive to syntax errors!\n")
            
            f.write(new_entry)

        # 3. LIVE INJECTION
        # The compiler handles the 'exec()' and adds it to the active intent registry
        success, msg = compiler.compile_and_run(feature_name, code)
        
        if success:
            SoulLogger.soul(f"Incantation successful! '{feature_name}' is now live in memory.")
        else:
            SoulLogger.err(f"Incantation failed for '{feature_name}': {msg}")
            
        return success, msg
        
    except Exception as e:
        SoulLogger.err(f"Dynamic Write Error: {e}")
        return False, str(e)