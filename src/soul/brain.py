import pickle
import os
import random
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from src import config

class IntentBrain:
    def __init__(self, soul=None):
        # 1. Core ML components (using ngrams from v1 for better context)
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self.classifier = LinearSVC()
        self.soul = soul # Reference to HuTaoSoul to update memory
        
        # 2. Expanded Base Knowledge
        self.data = [
            ("hello", "greet"), ("hi", "greet"), ("heya", "greet"),
            ("who are you", "identity"), ("what is your name", "identity"), 
            ("tell me about yourself", "identity"),
            ("i am", "user_info"), ("my name is", "user_info"), 
            ("write code", "code"), ("python", "code"), ("bugs", "code"),
            ("joke", "fun"), ("story", "fun"), ("sheesh", "fun"),
            ("bye", "exit"), ("goodbye", "exit"), ("status", "activity")
        ]
        
        self.load_model()

    def absorb_style(self, text):
        """Analyzes text to update Hu Tao's traits (Mischief vs professionalism)."""
        if not self.soul or not hasattr(self.soul, 'memory'):
            return

        text_lower = text.lower()
        mischief_markers = ["aiya", "hee-hee", "prank", "silly", "ghost", "hilichurl", "mischief"]
        serious_markers = ["funeral", "parlor", "business", "rites", "tradition", "client", "work"]
        
        m_score = sum(1 for word in mischief_markers if word in text_lower)
        s_score = sum(1 for word in serious_markers if word in text_lower)
        
        # Extract traits from the soul reference
        traits = self.soul.memory.get("traits", {"mischief": 0.5, "professionalism": 0.5})
        
        if m_score > s_score:
            print("Soul: Absorbing mischievous energy from user input...")
            traits["mischief"] = min(1.0, traits["mischief"] + 0.05)
            traits["professionalism"] = max(0.0, traits["professionalism"] - 0.05)
        elif s_score > m_score:
            print("Soul: Anchoring to professional business rites...")
            traits["professionalism"] = min(1.0, traits["professionalism"] + 0.05)
            traits["mischief"] = max(0.0, traits["mischief"] - 0.05)

        # Sync back to soul and persist
        self.soul.memory["traits"] = traits
        if hasattr(self.soul, '_save'):
            self.soul._save()

    def predict(self, text):
        """High-level prediction combining fuzzy matching, style absorption, and SVM."""
        text_lower = text.lower().strip()
        
        # 1. Update personality based on user tone
        self.absorb_style(text_lower)
        
        # 2. Sequence Matching (Fuzzy/Exact Match)
        best_match_intent = None
        highest_score = 0
        for known_text, intent in self.data:
            score = SequenceMatcher(None, text_lower, known_text).ratio()
            if score > highest_score:
                highest_score = score
                best_match_intent = intent
        
        # Immediate return for high confidence matches
        if highest_score >= 0.95: 
            return best_match_intent
        
        # "Passive Learning": If it's close, teach it to the brain
        if 0.85 <= highest_score < 0.95:
            self.teach(text_lower, best_match_intent)
            return best_match_intent
        
        # 3. SVM ML Prediction for complex phrasing
        try:
            X = self.vectorizer.transform([text_lower])
            return self.classifier.predict(X)[0]
        except Exception:
            return "default"

    def train(self):
        """Trains the Vectorizer and SVC, then pickles the brain."""
        try:
            if not self.data: return
            
            texts, labels = zip(*self.data)
            X = self.vectorizer.fit_transform(texts)
            self.classifier.fit(X, labels)
            
            os.makedirs(os.path.dirname(config.BRAIN_MODEL_PATH), exist_ok=True)
            with open(config.BRAIN_MODEL_PATH, 'wb') as f:
                pickle.dump((self.vectorizer, self.classifier, self.data), f)
        except Exception as e:
            print(f"Brain Training Error: {e}")

    def load_model(self):
        """Loads the saved brain state or triggers initial training."""
        if os.path.exists(config.BRAIN_MODEL_PATH):
            try:
                with open(config.BRAIN_MODEL_PATH, 'rb') as f:
                    v, c, d = pickle.load(f)
                    self.vectorizer, self.classifier, self.data = v, c, d
            except Exception:
                self.train()
        else:
            self.train()

    def teach(self, text, intent):
        """Adds new patterns to the brain and triggers a retraining cycle."""
        text_lower = text.lower().strip()
        if not any(text_lower == d[0] for d in self.data):
            print(f"Brain: New pattern recognized! Learning '{text_lower}' as '{intent}'")
            self.data.append((text_lower, intent))
            self.train()