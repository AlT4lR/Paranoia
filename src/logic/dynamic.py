# src/logic/dynamic.py
import os
from src.utils.logger import SoulLogger

DYNAMIC_FILE = os.path.join(os.path.dirname(__file__), "dynamic_features.py")

def save_new_capability(feature_name: str, code: str, compiler):
    """Saves code to file and registers it in the compiler."""
    try:
        # Create file if missing
        if not os.path.exists(DYNAMIC_FILE):
            with open(DYNAMIC_FILE, "w") as f: f.write("# Hu Tao's Grimoire\n")

        with open(DYNAMIC_FILE, "a") as f:
            f.write(f"\n# --- Synthesized: {feature_name} ---\n")
            f.write(code + "\n")
        
        # Inject into the compiler registry immediately
        success, msg = compiler.compile_and_run(feature_name, code)
        return success, msg
    except Exception as e:
        SoulLogger.err(f"Dynamic Write Error: {e}")
        return False, str(e)