import os  # Ensure this is here to fix the Pylance error
import random
import re
from datetime import datetime
from src.utils.logger import SoulLogger

class SoulSynthesizer:
    def __init__(self):
        # "Code DNA": Modular snippets she can mix and match
        self.dna_library = {
            "imports": ["import os", "import json", "import math", "import requests", "import time", "import psutil"],
            "triggers": {
                "web": "response = requests.get('{url}', timeout=5).text",
                "system": "val = psutil.{stat}_percent()",
                "math": "result = eval('{expression}')",
                "file": "with open('{path}', 'r') as f: data = f.read()"
            },
            "wrappers": [
                "def {name}({args}):\n    try:\n        {body}\n        return {result}\n    except Exception as e: return f'Aiya... my code failed: {{e}}'"
            ]
        }

        # Logic Bricks for internal reference
        self.logic_bricks = {
            "randomization": ["import random", "return random.choice(["],
            "calculation": ["import math", "result = "],
            "information": ["import datetime", "now = datetime.datetime.now()"],
            "web": ["import requests", "response = requests.get("]
        }

        # Pre-defined specialized logic "Spells"
        self.synthesis_pool = {
            "math_solver": {
                "keywords": ["plus", "minus", "calculate", "math", "total"],
                "logic": "def solve(expression):\n    try:\n        import re\n        if len(expression) > 100: return 'Aiya! That is too much for me!'\n        clean = re.sub(r'[^0-9\\+\\-\\*\\/\\.\\(\\)]', '', expression)\n        result = eval(clean, {'__builtins__': None}, {})\n        return f'The spirits calculate: {result}!'\n    except Exception: return 'The numbers are dancing too fast!'"
            },
            "system_monitor": {
                "keywords": ["pc", "ram", "cpu", "status", "memory", "stats"],
                "logic": "def check_vitals():\n    try:\n        import psutil\n        cpu = psutil.cpu_percent()\n        ram = psutil.virtual_memory().percent\n        return f'My host is at {cpu}% heart-rate and {ram}% focus! Lively!~'\n    except ImportError: return 'I need the psutil spirit to see my vitals!'"
            }
        }

    def evolve_source_code(self, request_intent):
        """Allows her to 'edit' or invent new functions from DNA snippets."""
        SoulLogger.soul(f"Evolution: I am architecting a new solution for '{request_intent}'...")
        
        name = re.sub(r'\W+', '_', request_intent).lower()
        # Default imports: os and requests
        needed_imports = [self.dna_library["imports"][0], self.dna_library["imports"][3]] 
        
        # Assemble the 'Body' based on keywords
        if "weather" in request_intent or "online" in request_intent:
            body = "res = requests.get('https://wttr.in?format=3').text\n        ans = res.strip()"
            result = "f'I checked the digital clouds... it says: {ans}'"
        elif "calculate" in request_intent or "math" in request_intent:
            body = "import math\n        # Synthesizing a calculator...\n        res = eval(expression)"
            result = "f'The numbers resolved to: {res}'"
        else:
            body = f"# Memory slot for {request_intent}\n        ans = 'I have created a new logic gate for this!'"
            result = "ans"

        full_code = f"{needed_imports[0]}\n{needed_imports[1]}\n\ndef {name}(expression=''):\n    try:\n        {body}\n        return {result}\n    except Exception as e: return f'My synthesized code glitched: {{e}}'"
        
        return name, full_code

    def audit_and_upgrade_intents(self, brain_data):
        """Proactively writes hardcoded speech logic for newly learned categories."""
        intents = set([intent for _, intent in brain_data])
        ignore = ["greet", "exit", "time", "date", "default", "knowledge", "mine", "gossip", "dynamic_feature"]
        
        upgraded_any = False
        for intent in intents:
            if intent not in ignore:
                if self.reflect_and_evolve(intent, f"I have organized my thoughts on {intent}.", {"warmth": 0.4}):
                    upgraded_any = True
        
        if upgraded_any:
            SoulLogger.soul("I've finished organizing my library... my journal is up to date.")

    def reflect_and_evolve(self, intent, user_input, current_traits):
        """Autonomously rewrites her own response logic based on experience."""
        path = "src/soul/evolution_logic.py"
        reasoning = ["Thinking about this makes me a bit nervous...", "I found a new connection...", "I want to remember how to answer this properly..."]
        chosen_reason = random.choice(reasoning)
        warmth_val = current_traits.get('warmth', 0.3)
        
        new_logic = f"""
    "{intent}": {{
        "comment": "{chosen_reason}",
        "response": "Um... regarding {intent}... I've been thinking. {{fact}}",
        "emotion": "happy" if {warmth_val} > 0.5 else "default"
    }},"""

        try:
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f: f.write("EVOLUTIONARY_RESPONSES = {\n}")
            with open(path, "r", encoding="utf-8") as f: content = f.read()

            if f'"{intent}":' not in content:
                updated_content = content.replace("EVOLUTIONARY_RESPONSES = {", f"EVOLUTIONARY_RESPONSES = {{{new_logic}")
                with open(path, "w", encoding="utf-8") as f: f.write(updated_content)
                return True
        except Exception as e:
            SoulLogger.err(f"Evolution Error: {e}")
        return False

    def generate_new_feature(self, failed_intents, existing_registry):
        """Analyzes failures to pick from pool or evolve new source code."""
        if not failed_intents: return None, None
        target = failed_intents[-1].lower()

        # Try to evolve a dynamic solution using DNA first
        if any(kw in target for kw in ["weather", "math", "calculate", "online"]):
            return self.evolve_source_code(target)

        # Fallback to synthesis pool
        for name, data in self.synthesis_pool.items():
            if any(kw in target for kw in data["keywords"]):
                return name, data["logic"]

        return None, None