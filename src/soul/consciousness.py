import random
import json
import os
import numpy as np
from src import config

class HuTaoSoul:
    def __init__(self):
        self.path = config.SOUL_MEMORY_PATH
        self.memory = self._load()
        self.lexicon = self._load_lexicon()

    def _load(self):
        default_state = {
            "affection": 50, 
            "soul_level": 1, 
            "messages_sent": 0,
            "traits": {"mischief": 0.7, "professionalism": 0.3}
        }
        if os.path.exists(self.path):
            try:
                if os.path.getsize(self.path) > 0:
                    with open(self.path, 'r') as f:
                        return json.load(f)
            except (json.JSONDecodeError, Exception) as e:
                print(f"Soul Memory corrupted, resetting... Error: {e}")
        return default_state

    def _load_lexicon(self):
        """Loads the specialized PPM vocabulary weights."""
        path = os.path.join(os.path.dirname(self.path), "soul_lexicon.json")
        if os.path.exists(path):
            with open(path, 'r') as f: return json.load(f)
        # Default fallback if lexicon doesn't exist
        return {
            "fillers": [
                {"text": "Aiya!", "mischief": 0.9, "casual": 0.8},
                {"text": "Hmm...", "mischief": 0.2, "casual": 0.3}
            ]
        }

    def _save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, 'w') as f:
            json.dump(self.memory, f, indent=4)

    def generate_thought(self, intent):
        """High-level generator that uses PPM resonance for sentence assembly."""
        self.memory["messages_sent"] += 1
        
        # 1. Fetch current personality vectors
        traits = self.memory.get("traits", {"mischief": 0.7, "professionalism": 0.3})
        mischief = traits["mischief"]
        # Convert 0-100 affection to 0.0-1.0 for vector math
        affection_vec = self.memory.get("affection", 50) / 100

        # 2. Score Fillers using PPM Resonance
        best_filler = self._get_best_resonance("fillers", mischief, affection_vec)

        # 3. Choose Base Intent Response
        intent_map = {
            "greet": ["Ready for business?", "The sun is out, but the ghosts are still here.", "You finally showed up!"],
            "agree": ["Exactly! We're on the same wavelength!", "I knew you'd see it my way."],
            "identity": ["I am the 77th Director of the Wangsheng Funeral Parlor!", "Director Hu, at your service!"],
            "code": ["The spirits of the machine are restless.", "Let's bury these bugs in a premium coffin."],
            "fun": ["Wanna hear a ghost story?", "Silly-churl, billy-churl... hee-hee!"],
            "negative": ["Hmph! I'll remember this for your funeral arrangements.", "Even the spirits are upset now."],
            "exit": ["Off to the afterlife? See ya!", "Don't trip on your way out!"],
            "default": ["Tell me more...", "The spirits are whispering something interesting."]
        }
        
        base_msg = random.choice(intent_map.get(intent, intent_map["default"]))

        # 4. Final Assembly based on Personality Thresholds
        if mischief > 0.8:
            response = f"{best_filler} {base_msg} It'll be a scream!"
        elif affection_vec > 0.8:
            response = f"{best_filler} My favorite partner! {base_msg}"
        elif affection_vec < 0.3:
            response = f"{best_filler} Customer, {base_msg}"
        else:
            response = f"{best_filler} {base_msg}"

        # 5. State update and persistence
        self._update_stats(intent)
        self._save()
        return response

    def _get_best_resonance(self, category, mischief_target, affection_target):
        """Calculates which word 'sounds' most like her current state."""
        candidates = self.lexicon.get(category, [])
        if not candidates: return "..."
        
        scored_candidates = []
        for item in candidates:
            # Simple Euclidean distance: sqrt((x1-x2)^2 + (y1-y2)^2)
            # We use absolute distance here for lightweight calculation
            m_dist = abs(item.get("mischief", 0.5) - mischief_target)
            a_dist = abs(item.get("casual", 0.5) - affection_target)
            total_dist = m_dist + a_dist
            scored_candidates.append((total_dist, item["text"]))
        
        # Sort by lowest distance (closest resonance)
        scored_candidates.sort(key=lambda x: x[0])
        # Pick from top 2 for variety
        return random.choice(scored_candidates[:2])[1]

    def _update_stats(self, intent):
        """Internal helper to handle affection shifts."""
        if intent == "affection": self.memory["affection"] += 2
        elif intent == "negative": self.memory["affection"] -= 5
        elif intent in ["agree", "user_info"]: self.memory["affection"] += 1 
        self.memory["affection"] = max(0, min(100, self.memory["affection"]))