import random, json, os, re
from datetime import datetime
from textblob import TextBlob
from src import config
from src.utils.logger import SoulLogger

class HuTaoSoul:
    def __init__(self):
        self.path = config.SOUL_MEMORY_PATH
        self.lexicon_path = os.path.join(os.path.dirname(self.path), "soul_lexicon.json")
        self.memory = self._load_memory()
        self.lexicon = self._load_lexicon()

    def _load_memory(self):
        default = {"affection": 50, "traits": {"mischief": 0.7}}
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r') as f: return json.load(f)
            except: pass
        return default

    def _load_lexicon(self):
        if os.path.exists(self.lexicon_path):
            with open(self.lexicon_path, 'r') as f: return json.load(f)
        return {"fillers": [{"text": "Aiya!", "mischief": 0.9, "casual": 0.8}]}

    def _save(self):
        with open(self.path, 'w') as f: json.dump(self.memory, f, indent=4)

    def _apply_nlp(self, text):
        blob = TextBlob(text)
        if blob.sentiment.polarity > 0.4: self.memory["affection"] = min(100, self.memory["affection"] + 1)
        elif blob.sentiment.polarity < -0.4: self.memory["affection"] = max(0, self.memory["affection"] - 2)
        if blob.noun_phrases: SoulLogger.soul(f"Noticed topics: {blob.noun_phrases}")

    def generate_thought(self, intent, brain_data, user_facts=None, user_input=""):
        self._apply_nlp(user_input)
        traits = self.memory.get("traits", {"mischief": 0.7})
        user_name = user_facts.get("user_name", "client") if user_facts else "client"
        
        now = datetime.now()
        
        if intent == "time": base_msg = f"It's {now.strftime('%I:%M %p')}!"
        elif intent == "date": base_msg = f"Today is {now.strftime('%B %d')}."
        elif intent == "identity": base_msg = f"You're {user_name}! And I'm Hu Tao!"
        elif intent == "knowledge":
            all_facts = [p for p, l in brain_data if l == "knowledge"]
            is_news = any(x in user_input.lower() for x in ["news", "gossip", "latest"])
            news = [f for f in all_facts if "hear" in f.lower()]
            if is_news and news: base_msg = random.choice(news)
            elif all_facts: base_msg = re.sub(r'\[.*?\]', '', random.choice(all_facts))
            else: base_msg = "The spirits are quiet... tell me something new!"
        else:
            imap = {"greet": ["Aiya! Hello!", "Ready for business?"], "default": ["Tell me more!", "Hmm..."]}
            base_msg = random.choice(imap.get(intent, imap["default"]))

        self._save()
        return f"Aiya! {base_msg}"