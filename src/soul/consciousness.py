import random
import json
import os
from src import config

class HuTaoSoul:
    def __init__(self):
        self.path = config.SOUL_MEMORY_PATH
        self.memory = self._load()

    def _load(self):
        default_state = {"affection": 50, "soul_level": 1, "messages_sent": 0}
        if os.path.exists(self.path):
            try:
                if os.path.getsize(self.path) > 0:
                    with open(self.path, 'r') as f:
                        return json.load(f)
            except (json.JSONDecodeError, Exception) as e:
                print(f"Soul Memory corrupted or empty, resetting... Error: {e}")
        return default_state

    def _save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, 'w') as f:
            json.dump(self.memory, f, indent=4)

    def generate_thought(self, intent):
        """Generates a personality-driven response based on the predicted intent."""
        self.memory["messages_sent"] += 1
        
        # Intent-to-Dialogue Mapping
        templates = {
            "greet": [
                "Aiya! You finally showed up!", 
                "Director Hu at your service! Ready for business?",
                "Hee-hee! Did you bring me any interesting ghost stories?"
            ],
            "agree": [
                "Exactly! We're on the same wavelength!",
                "I knew you'd see it my way. Want a commemorative butterfly?",
                "Hee-hee, great minds think alike!"
            ],
            "disagree": [
                "Aww, you're no fun! Even the spirits think you're being too serious.",
                "Hmph! Well, I'll just have to convince you later.",
                "To each their own, I suppose... but my way is more exciting!"
            ],
            "identity": [
                "I'm Hu Tao, the 77th Director of the Wangsheng Funeral Parlor!",
                "Director Hu, at your service! I manage the border between life and death."
            ],
            "user_info": [
                "Oh! A new name to write in my ledger... just kidding! Nice to meet you!",
                "Aiya, what a lively name! I'll be sure to remember it."
            ],
            "code": [
                "Let's bury these bugs underground!", 
                "Coding? It's like writing poems for machines!"
            ],
            "fun": [
                "Wanna hear a ghost story?", 
                "Silly-churl, billy-churl, silly-billy hilichurl... hee-hee!"
            ],
            "affection": [
                "Hee-hee, you're making my heart flutter like a butterfly!", 
                "Careful, or I'll haunt you with love!"
            ],
            "negative": [
                "Hmph! I'll remember this for your funeral arrangements.", 
                "Even the spirits are upset now."
            ],
            "exit": [
                "Off to the afterlife? See ya!", 
                "Don't trip on your way out!"
            ],
            "default": [
                "Oh? Tell me more...", 
                "The spirits are whispering something interesting."
            ]
        }

        # Dynamic Prefix
        prefix = ""
        if self.memory["affection"] > 80: 
            prefix = "Partner, "
        elif self.memory["affection"] < 30: 
            prefix = "Customer, "

        response = prefix + random.choice(templates.get(intent, templates["default"]))
        
        # Affection Logic
        if intent == "affection": 
            self.memory["affection"] += 2
        elif intent == "negative": 
            self.memory["affection"] -= 5
        elif intent in ["agree", "user_info"]:
            self.memory["affection"] += 1 

        self.memory["affection"] = max(0, min(100, self.memory["affection"]))
        self._save()
        return response