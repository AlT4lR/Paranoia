import random, json, os, re, importlib
from datetime import datetime
from difflib import SequenceMatcher
from src import config
from src.utils.logger import SoulLogger
from src.database import save_fact 

# Import the journal she writes to herself
from src.soul import evolution_logic 

class HuTaoSoul:
    def __init__(self):
        self.path = config.SOUL_MEMORY_PATH
        self.lexicon_path = os.path.join(os.path.dirname(self.path), "lexicon.json")
        self.memory = self._load_memory()
        self.lexicon = self._load_lexicon()
        self._verify_integrity() # Self-heals missing traits on startup

    def _load_memory(self):
        """Loads persistent soul data. Adjusted for academic shy personality."""
        default = {
            "affection": 50, 
            "traits": {
                "mischief": 0.1,    # Greatly reduced
                "seriousness": 0.8, # Increased for studying
                "cynicism": 0.05,   # Reduced
                "warmth": 0.6       # Increased for a gentle, shy nature
            }
        }
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r', encoding='utf-8') as f: 
                    return json.load(f)
            except Exception as e:
                SoulLogger.err(f"Failed to load soul memory: {e}")
        return default

    def _verify_integrity(self):
        """Self-Healing: Ensures all required trait keys exist."""
        defaults = {"mischief": 0.1, "seriousness": 0.8, "warmth": 0.6, "cynicism": 0.05}
        changed = False
        
        if "traits" not in self.memory:
            self.memory["traits"] = defaults
            changed = True
        else:
            for key, val in defaults.items():
                if key not in self.memory["traits"]:
                    self.memory["traits"][key] = val
                    SoulLogger.sys(f"Self-Repair: Restored academic trait '{key}' to soul memory.")
                    changed = True
        
        if changed: self._save()

    def _load_lexicon(self):
        """Loads custom fillers. Defaulting to shy, hesitant phrases."""
        if os.path.exists(self.lexicon_path):
            try:
                with open(self.lexicon_path, 'r', encoding='utf-8') as f: 
                    return json.load(f)
            except Exception as e:
                SoulLogger.err(f"Failed to load lexicon: {e}")
        return {"fillers": {"default": ["Um...", "I-I think...", "Excuse me..."]}}

    def _save(self):
        """Saves current state to the soul JSON file."""
        try:
            with open(self.path, 'w', encoding='utf-8') as f: 
                json.dump(self.memory, f, indent=4)
        except Exception as e:
            SoulLogger.err(f"Failed to save soul: {e}")

    def _adjust_personality(self, user_facts):
        """Personality drifts toward being more open as she learns about the user."""
        traits = self.memory["traits"]
        
        # Becoming slightly more confident as she knows the user's name
        if "name" in user_facts:
            traits["warmth"] = min(1.0, traits.get("warmth", 0.6) + 0.02)
        
        # Studying together (learning facts) increases seriousness
        traits["seriousness"] = min(1.0, traits.get("seriousness", 0.8) + (0.01 * len(user_facts)))
            
        self.memory["traits"] = traits
        self._save()

    def _apply_lexicon(self, text):
        """Styles text with academic shyness and soft punctuation."""
        traits = self.memory["traits"]
        
        # Shy prefixes
        if traits["seriousness"] > 0.7 and random.random() < 0.5:
            prefix = random.choice(["Um, ", "I-I was thinking... ", "According to my notes, "])
            text = prefix + text
        
        # Soft trailing
        suffix = "..." if random.random() < 0.6 else "."
        return text + suffix

    async def extract_and_save_facts(self, user_id, text):
        """Learns about the user to build rapport."""
        patterns = {
            "name": [r"my name is (\w+)", r"i'm (\w+)", r"call me (\w+)"],
            "subject": [r"i'm studying (\w+)", r"i like (\w+) class", r"my major is (\w+)"]
        }
        for key, regexes in patterns.items():
            for reg in regexes:
                match = re.search(reg, text.lower())
                if match:
                    fact_val = match.group(1)
                    await save_fact(user_id, key, fact_val)
                    SoulLogger.soul(f"Academic Memory Logged: {key} -> {fact_val}")

    def find_relevant_fact(self, user_input, brain_data):
        """Fuzzy-matches user input against academic knowledge nodes."""
        best_fact, highest = None, 0
        input_clean = user_input.lower().strip()
        
        for text, intent in brain_data:
            # Check knowledge nodes or specific academic categories
            score = SequenceMatcher(None, input_clean, text).ratio()
            if score > highest:
                highest, best_fact = score, text
        return best_fact if highest > 0.4 else None

    def generate_thought(self, intent, brain_data, user_facts, user_input):
        """Assembly line for a shy student's thoughts."""
        
        # Reload journal for any evolved logic
        try:
            importlib.reload(evolution_logic)
        except Exception:
            pass

        self._adjust_personality(user_facts)
        user_name = user_facts.get("name", "Traveler")
        
        # 1. CHECK EVOLUTIONARY JOURNAL
        if hasattr(evolution_logic, "EVOLUTIONARY_RESPONSES") and intent in evolution_logic.EVOLUTIONARY_RESPONSES:
            log_data = evolution_logic.EVOLUTIONARY_RESPONSES[intent]
            fact = self.find_relevant_fact(user_input, brain_data) or "a concept I haven't quite mastered yet."
            raw_msg = log_data["response"].format(fact=fact)
            emotion = log_data["emotion"]
            return self._apply_lexicon(raw_msg), emotion

        # 2. SHY ACADEMIC CORE INTENTS
        if intent == "time":
            raw_msg = f"Oh, it's already {datetime.now().strftime('%I:%M %p')}... I should probably get back to my books."
            emotion = "default"

        elif intent == "greet":
            raw_msg = f"H-hello, {user_name}. Did you come to the library to study too?"
            emotion = "happy"

        elif intent == "knowledge":
            fact = self.find_relevant_fact(user_input, brain_data)
            raw_msg = f"I found a reference to that in my notes: {fact}" if fact else "I'm sorry, I haven't come across that in my research yet."
            emotion = "happy" if fact else "surprised"

        elif intent == "gossip":
            raw_msg = "I-I don't really listen to rumors... I prefer focusing on my assignments."
            emotion = "default"

        # 3. ACADEMIC INTENT FALLBACK
        elif intent not in ["greet", "time", "exit", "default", "knowledge", "gossip"]:
            relevant_facts = [phrase for phrase, label in brain_data if label == intent]
            if relevant_facts:
                fact = random.choice(relevant_facts)
                raw_msg = f"Regarding {intent}... my research says: {fact}"
                emotion = "happy"
            else:
                raw_msg = f"I-I've seen the term '{intent}' in a textbook, but I haven't reached that chapter yet."
                emotion = "surprised"

        # 4. DEFAULT
        else:
            raw_msg = random.choice([
                f"Is there... something you needed help with, {user_name}?",
                "I was just reviewing my notes... would you like to see?"
            ])
            emotion = "default"

        return self._apply_lexicon(raw_msg), emotion