# src/logic/dynamic.py
import os
from src.utils.logger import SoulLogger

# This is where her "learned" Python code lives
DYNAMIC_FILE = os.path.join(os.path.dirname(__file__), "dynamic_features.py")

def save_new_capability(feature_name: str, code: str, compiler):
    """Saves code to the file AND injects it into the active Soul Compiler."""
    try:
        # 1. Save to Disk (Persistence)
        with open(DYNAMIC_FILE, "a") as f:
            f.write(f"\n\n# --- Feature: {feature_name} ---\n")
            f.write(code)
        
        # 2. Inject into Memory (Instant usage)
        success, message = compiler.compile_and_run(feature_name, code)
        
        if success:
            SoulLogger.sys(f"Soul Growth: Feature '{feature_name}' synthesized and active.")
            return True, f"I've successfully added '{feature_name}' to my repertoire!"
        else:
            SoulLogger.err(f"Synthesis Failure: {message}")
            return False, "Aiya... I tried to learn a new trick but I got the syntax wrong."
            
    except Exception as e:
        SoulLogger.err(f"Dynamic Save Error: {e}")
        return False, str(e)

def get_current_capabilities():
    if not os.path.exists(DYNAMIC_FILE):
        return "I haven't synthesized any custom spells yet."
    with open(DYNAMIC_FILE, "r") as f:
        return f.read()