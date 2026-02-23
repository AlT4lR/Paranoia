# src/soul/consciousness.py
import random, json, os, re
from datetime import datetime
from textblob import TextBlob
from src import config
from src.utils.logger import SoulLogger

class HuTaoSoul:
    def __init__(self):
        self.path = config.SOUL_MEMORY_PATH
        self.memory = self._load_memory()

    def _load_memory(self):
        default = {"affection": 50, "traits": {"mischief": 0.7}}
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r') as f: return json.load(f)
            except: pass
        return default

    def _save(self):
        with open(self.path, 'w') as f: json.dump(self.memory, f, indent=4)

    def _apply_nlp(self, text):
        blob = TextBlob(text)
        old_affection = self.memory["affection"]
        if blob.sentiment.polarity > 0.4: self.memory["affection"] = min(100, self.memory["affection"] + 1)
        elif blob.sentiment.polarity < -0.4: self.memory["affection"] = max(0, self.memory["affection"] - 2)
        
        if old_affection != self.memory["affection"]:
             SoulLogger.soul(f"Affection Drift: {old_affection} -> {self.memory['affection']} (Polarity: {blob.sentiment.polarity:.2f})")

    def find_relevant_fact(self, user_input, brain_data):
        """Filters knowledge to find facts related to the user's input words."""
        input_words = set(re.findall(r'\w+', user_input.lower()))
        # Remove common stop words to improve matching
        stop_words = {"do", "you", "know", "about", "the", "what", "is", "of", "a", "me", "tell"}
        keywords = input_words - stop_words
        
        if not keywords: return None
        
        knowledge_pool = [p for p, l in brain_data if l == "knowledge"]
        relevant_matches = []

        for fact in knowledge_pool:
            fact_lower = fact.lower()
            if any(kw in fact_lower for kw in keywords):
                relevant_matches.append(fact)
        
        if relevant_matches:
            return random.choice(relevant_matches)
        return None

    def generate_thought(self, intent, brain_data, user_facts=None, user_input=""):
        self._apply_nlp(user_input)
        user_name = user_facts.get("user_name", config.DEFAULT_USER_NAME) if user_facts else config.DEFAULT_USER_NAME
        now = datetime.now()
        
        SoulLogger.soul(f"Context Filter: Processing '{intent}' with input '{user_input}'")
        
        # 1. Identity Context (Priority)
        if intent == "identity":
            if any(word in user_input.lower() for word in ["me", " i "]):
                return f"You're {user_name}! My most favorite client. Don't tell me you've forgotten already? Aiya!"
            return f"I'm Hu Tao! 77th Director of the Wangsheng Funeral Parlor. Pleased to meet ya!"

        # 2. Time/Date
        elif intent == "time":
            return f"It's {now.strftime('%I:%M %p')}. Perfect time for a stroll!"

        elif intent == "date":
            return f"Today is {now.strftime('%B %d, %Y')}."

        # 3. Knowledge Filtering
        elif intent == "knowledge":
            fact = self.find_relevant_fact(user_input, brain_data)
            if fact:
                SoulLogger.soul("Relevance Filter: Found matching fact.")
                return f"Oh! I know something about that: {fact}"
            else:
                SoulLogger.soul("Relevance Filter: No matching facts found. Fallback to generic.")
                return random.choice([
                    "I've heard of that, but my memory is a bit fuzzy. Want to teach me?",
                    "Hmm, I'll have to ask the spirits about that one later!",
                    f"I'm not sure about that, {user_name}, but it sounds interesting!"
                ])

        # 4. Greetings
        elif intent == "greet":
            return random.choice(["Aiya! Hello!", "Hee-hee, you called?", "Need help with a crossover?"])

        # 5. Fallback
        else:
            SoulLogger.soul("Default Context: Using personality filler.")
            return random.choice([
                "Tell me more about that!",
                "Aiya... you say the most interesting things.",
                "Hmm? I'm listening!",
                "Is that so? Tell me everything!~"
            ])

        self._save()