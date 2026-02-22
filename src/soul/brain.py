import pickle
import os
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from src import config

class IntentBrain:
    def __init__(self, soul=None):
        # 1. Core ML components
        self.vectorizer = TfidfVectorizer()
        self.classifier = LinearSVC()
        self.soul = soul # Reference to HuTaoSoul to update memory
        
        # 2. Base knowledge
        self.data = [
            ("hello", "greet"), ("hi", "greet"), ("heya", "greet"),
            ("who are you", "identity"), ("what is your name", "identity"), 
            ("tell me about yourself", "identity"),
            ("i am", "user_info"), ("my name is", "user_info"), 
            ("write code", "code"), ("python", "code"),
            ("joke", "fun"), ("story", "fun"), ("sheesh", "fun"),
            ("bye", "exit"), ("status", "activity")
        ]
        
        self.load_model()

    def absorb_style(self, text):
        """Analyzes text to see if it matches Hu Tao's voice and updates traits."""
        if not self.soul:
            return

        text_lower = text.lower()
        mischief_markers = ["aiya", "hee-hee", "prank", "silly", "ghost", "hilichurl"]
        serious_markers = ["funeral", "parlor", "business", "rites", "tradition", "client"]
        
        m_score = sum(1 for word in mischief_markers if word in text_lower)
        s_score = sum(1 for word in serious_markers if word in text_lower)
        
        # Get current traits from soul memory
        traits = self.soul.memory.get("traits", {"mischief": 0.5, "professionalism": 0.5})
        
        if m_score > s_score:
            print("Hu Tao: 'I'm feeling more mischievous after reading that!'")
            traits["mischief"] = min(1.0, traits["mischief"] + 0.1)
            traits["professionalism"] = max(0.0, traits["professionalism"] - 0.1)
        elif s_score > m_score:
            print("Hu Tao: 'Ah, business talk. Let's be professional.'")
            traits["professionalism"] = min(1.0, traits["professionalism"] + 0.1)
            traits["mischief"] = max(0.0, traits["mischief"] - 0.1)

        # Save the updated traits back to the soul's memory
        self.soul.memory["traits"] = traits
        self.soul._save()

    def predict(self, text):
        """Predicts intent and learns style simultaneously."""
        # Run style analysis first
        self.absorb_style(text)
        
        text_lower = text.lower().strip()
        
        # 1. Passive Learning / Similarity check
        best_match_intent = None
        highest_score = 0
        for known_text, intent in self.data:
            score = SequenceMatcher(None, text_lower, known_text).ratio()
            if score > highest_score:
                highest_score = score
                best_match_intent = intent
        
        if 0.80 <= highest_score < 1.0:
            self.teach(text_lower, best_match_intent)
            return best_match_intent
        
        # 2. Standard ML Prediction
        try:
            X = self.vectorizer.transform([text_lower])
            return self.classifier.predict(X)[0]
        except Exception:
            return "unknown"

    def train(self):
        """Trains the ML model and saves it to a file."""
        try:
            texts, labels = zip(*self.data)
            X = self.vectorizer.fit_transform(texts)
            self.classifier.fit(X, labels)
            os.makedirs(os.path.dirname(config.BRAIN_MODEL_PATH), exist_ok=True)
            with open(config.BRAIN_MODEL_PATH, 'wb') as f:
                pickle.dump((self.vectorizer, self.classifier, self.data), f)
        except Exception as e:
            print(f"Brain Training Error: {e}")

    def load_model(self):
        if os.path.exists(config.BRAIN_MODEL_PATH):
            try:
                with open(config.BRAIN_MODEL_PATH, 'rb') as f:
                    self.vectorizer, self.classifier, self.data = pickle.load(f)
            except Exception:
                self.train()
        else:
            self.train()

    def teach(self, text, intent):
        text_lower = text.lower().strip()
        if (text_lower, intent) not in self.data:
            print(f"Brain: Learning that '{text_lower}' means '{intent}'")
            self.data.append((text_lower, intent))
            self.train()