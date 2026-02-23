# src/soul/consciousness.py
import random
import json
import os
import re
from datetime import datetime
from src import config
from src.utils.logger import SoulLogger

class HuTaoSoul:
    # ... (__init__, _load_memory, _load_lexicon, _save, _get_best_resonance stay the same) ...
    def __init__(self):
        self.path = config.SOUL_MEMORY_PATH
        self.lexicon_path = os.path.join(os.path.dirname(self.path), "soul_lexicon.json")
        self.memory = self._load_memory()
        self.lexicon = self._load_lexicon()

    def _load_memory(self):
        default = {"affection": 50, "soul_level": 1, "messages_sent": 0, "traits": {"mischief": 0.7, "professionalism": 0.3}}
        if os.path.exists(self.path) and os.path.getsize(self.path) > 0:
            try:
                with open(self.path, 'r') as f: return json.load(f)
            except: pass
        return default

    def _load_lexicon(self):
        if os.path.exists(self.lexicon_path):
            with open(self.lexicon_path, 'r') as f: return json.load(f)
        return {"fillers": [{"text": "Aiya!", "mischief": 0.9, "casual": 0.8}]}

    def _save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, 'w') as f: json.dump(self.memory, f, indent=4)

    def _get_best_resonance(self, category, mischief_target, affection_target):
        candidates = self.lexicon.get(category, [])
        if not candidates: return "..."
        scored = []
        for item in candidates:
            dist = abs(item.get("mischief", 0.5) - mischief_target) + abs(item.get("casual", 0.5) - affection_target)
            scored.append((dist, item["text"]))
        scored.sort(key=lambda x: x[0])
        return random.choice(scored[:2])[1]

    def generate_thought(self, intent, brain_data, user_facts=None, user_input=""):
        self.memory["messages_sent"] += 1
        traits = self.memory.get("traits", {"mischief": 0.7, "professionalism": 0.3})
        m_target = traits["mischief"]
        a_vec = self.memory.get("affection", 50) / 100 
        
        filler = self._get_best_resonance("fillers", m_target, a_vec)
        user_name = user_facts.get("user_name", "my favorite client") if user_facts else "my favorite client"

        # --- 1. CONTEXTUAL KNOWLEDGE RETRIEVAL ---
        if intent == "knowledge":
            all_facts = [phrase for phrase, label in brain_data if label == "knowledge"]
            
            # Check if user specifically asked for 'gossip' or 'news'
            is_news_request = any(x in user_input.lower() for x in ["news", "gossip", "hear", "latest"])
            news_facts = [f for f in all_facts if "Did you hear" in f]
            
            if is_news_request and news_facts:
                base_msg = random.choice(news_facts)
                SoulLogger.soul("Context Match: Prioritizing news gossip over deep history.")
            elif all_facts:
                # Pick a random fact but CLEAN it before saying it
                base_msg = random.choice(all_facts)
                base_msg = re.sub(r'\[.*?\]|\(.*?\)', '', base_msg).strip()
            else:
                base_msg = "The spirits are being quiet... I don't have any news yet!"

        # --- 2. TEMPORAL & PERSONA ---
        elif intent == "time":
            base_msg = f"It's {datetime.now().strftime('%I:%M %p')}. Perfect for a little break!"
        elif intent == "greet":
            base_msg = "Aiya! You're back! Ready for business?"
        elif intent == "identity":
            base_msg = f"You're {user_name}! And I'm the Director! Don't forget it!"
        
        # --- 3. FALLBACK ---
        else:
            intent_map = {
                "fun": ["Wanna hear a joke?", "Hee-hee! Settle in for a story."],
                "affection": ["You're so sweet!", "My favorite client~"],
                "default": ["Tell me more!", "The spirits are whispering something interesting..."]
            }
            base_msg = random.choice(intent_map.get(intent, intent_map["default"]))

        response = f"{filler} {base_msg}"
        self._save()
        return response