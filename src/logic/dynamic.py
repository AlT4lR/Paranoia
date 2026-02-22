# src/logic/dynamic.py
import os

DYNAMIC_FILE = os.path.join(os.path.dirname(__file__), "dynamic_features.py")

def save_new_capability(feature_name: str, code: str):
    """Saves a new code snippet that Hu Tao invented for herself."""
    with open(DYNAMIC_FILE, "a") as f:
        f.write(f"\n# Feature: {feature_name}\n{code}\n")
    return f"I've successfully added '{feature_name}' to my repertoire of spells!"

def get_current_capabilities():
    """Reads the dynamic file so Hu Tao knows what she has built."""
    if not os.path.exists(DYNAMIC_FILE):
        return "No custom spells added yet."
    with open(DYNAMIC_FILE, "r") as f:
        return f.read()