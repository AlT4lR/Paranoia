import random
import json
import os
from src import config

class HuTaoSoul:
    def __init__(self):
        self.path = config.SOUL_MEMORY_PATH
        self.memory = self._load()

    def _load(self):
        # Merged default state including traits from the partial update
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

    def _save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, 'w') as f:
            json.dump(self.memory, f, indent=4)

    def generate_thought(self, intent):
        """Generates a personality-driven response based on intent and internal traits."""
        self.memory["messages_sent"] += 1
        
        traits = self.memory.get("traits", {"mischief": 0.7, "professionalism": 0.3})
        affection = self.memory.get("affection", 50)

        # 1. Determine the Filler (based on Mischief trait)
        if traits["mischief"] > 0.6:
            filler = random.choice(["Aiya!", "Hee-hee~", "Silly-churl!", "Oh?"])
        else:
            filler = random.choice(["Hmm...", "Well now...", "Listen closely.", "Business first."])

        # 2. Intent-to-Core-Concept Mapping
        templates = {
            "greet": ["Ready to do some business?", "The sun is out, but the ghosts are still here.", "You finally showed up!"],
            "agree": ["Exactly! We're on the same wavelength!", "I knew you'd see it my way.", "Great minds think alike!"],
            "disagree": ["Aww, you're no fun!", "Hmph! I'll just have to convince you later.", "To each their own... but my way is better!"],
            "identity": ["I am the 77th Director of the Wangsheng Funeral Parlor, obviously!", "Director Hu, at your service!"],
            "code": ["The spirits of the machine are restless.", "Let's put these bugs in a premium coffin.", "Coding? It's like writing poems for machines!"],
            "fun": ["Wanna hear a ghost story?", "Silly-churl, billy-churl... hee-hee!"],
            "affection": ["You're making my heart flutter like a butterfly!", "Careful, or I'll haunt you with love!"],
            "negative": ["Hmph! I'll remember this for your funeral arrangements.", "Even the spirits are upset now."],
            "exit": ["Off to the afterlife? See ya!", "Don't trip on your way out!"],
            "default": ["Tell me more...", "The spirits are whispering something interesting."]
        }

        base_msg = random.choice(templates.get(intent, templates["default"]))

        # 3. Dynamic Prefix & Final Assembly
        if affection > 80:
            final_speech = f"{filler} My dear partner, {base_msg}"
        elif affection < 30:
            final_speech = f"{filler} Customer, {base_msg}"
        else:
            final_speech = f"{filler} {base_msg}"

        # 4. Update State Logic
        self._update_stats(intent)
        self._save()

        return final_speech

    def _update_stats(self, intent):
        """Internal helper to handle affection and trait shifts."""
        if intent == "affection": 
            self.memory["affection"] += 2
        elif intent == "negative": 
            self.memory["affection"] -= 5
        elif intent in ["agree", "user_info"]:
            self.memory["affection"] += 1 
            
        # Ensure bounds
        self.memory["affection"] = max(0, min(100, self.memory["affection"]))