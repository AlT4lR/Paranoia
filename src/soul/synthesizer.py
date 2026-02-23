# src/soul/synthesizer.py
import random
from src.utils.logger import SoulLogger

class SoulSynthesizer:
    def __init__(self):
        # A pool of "Spells" (Features) she can invent if she feels she needs them
        self.synthesis_pool = {
            "math_solver": {
                "keywords": ["plus", "minus", "calculate", "math", "total"],
                "code": """def solve(expression):
    try:
        # A simple safe math evaluator
        import re
        clean = re.sub(r'[^0-9\\+\\-\\*\\/\\.\\(\\)]', '', expression)
        result = eval(clean)
        return f"Aiya! I did the math in my head: {result}!"
    except:
        return "The numbers are dancing too fast for me to catch! Give me a simpler equation."
"""
            },
            "fortune_teller": {
                "keywords": ["future", "fortune", "luck", "predict"],
                "code": """def predict():
    fortunes = [
        "Business will be booming! (For the Parlor, at least~)",
        "Spirits say: Watch your step near Wuwang Hill.",
        "A butterfly brings good luck today!",
        "The tea leaves are blurry... try again after a snack."
    ]
    import random
    return f"Let me see... {random.choice(fortunes)}"
"""
            },
            "system_check": {
                "keywords": ["cpu", "ram", "memory", "stats", "pc"],
                "code": """def check_vitals():
    import psutil
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    return f"My physical host is at {cpu}% heart-rate and {ram}% focus! I'm feeling lively!~"
"""
            }
        }

    def generate_new_feature(self, failed_intents, existing_registry):
        """Looks at what the user wanted and finds a matching spell to 'invent'."""
        for feature_name, data in self.synthesis_pool.items():
            # Don't synthesize something she already knows
            if any(feature_name in key for key in existing_registry.keys()):
                continue
            
            # If the user has used keywords related to this feature in the past
            if any(kw in " ".join(failed_intents).lower() for kw in data["keywords"]):
                SoulLogger.soul(f"Synthesis Idea: User wants '{feature_name}'. Beginning incantation...")
                return feature_name, data["code"]
        
        # If no specific match, just pick something random to grow
        untaught = [k for k in self.synthesis_pool.keys() if not any(k in reg for reg in existing_registry.keys())]
        if untaught:
            name = random.choice(untaught)
            return name, self.synthesis_pool[name]["code"]
            
        return None, None