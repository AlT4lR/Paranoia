import pickle
import os
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from src import config

class IntentBrain:
    def __init__(self):
        # Initialize the core ML components
        self.vectorizer = TfidfVectorizer()
        self.classifier = LinearSVC()
        
        # Base knowledge - Hu Tao's starting memory
        # Merged the 'user_info' patterns directly into the initial data list
        self.data = [
            # Greetings
            ("hello", "greet"), ("hi", "greet"), ("heya", "greet"),
            # Identity
            ("who are you", "identity"), ("what is your name", "identity"), 
            ("tell me about yourself", "identity"),
            # User Information
            ("i am", "user_info"), ("my name is", "user_info"), 
            ("call me", "user_info"), ("this is", "user_info"),
            # Coding
            ("write code", "code"), ("python", "code"), ("how to code", "code"),
            # Fun/Miscellaneous
            ("joke", "fun"), ("story", "fun"), ("sheesh", "fun"),
            # Exit
            ("bye", "exit"), ("goodbye", "exit"),
            # Status
            ("what are you doing", "activity"), ("status", "activity")
        ]
        
        # Load existing model if available, otherwise train from base data
        self.load_model()

    def train(self):
        """Trains the ML model and saves it to a file."""
        try:
            texts, labels = zip(*self.data)
            X = self.vectorizer.fit_transform(texts)
            self.classifier.fit(X, labels)
            
            # Ensure the directory exists before saving
            os.makedirs(os.path.dirname(config.BRAIN_MODEL_PATH), exist_ok=True)
            
            # Save the brain state
            with open(config.BRAIN_MODEL_PATH, 'wb') as f:
                pickle.dump((self.vectorizer, self.classifier, self.data), f)
        except Exception as e:
            print(f"Brain Training Error: {e}")

    def load_model(self):
        """Loads the brain from disk if it exists."""
        if os.path.exists(config.BRAIN_MODEL_PATH):
            try:
                with open(config.BRAIN_MODEL_PATH, 'rb') as f:
                    self.vectorizer, self.classifier, self.data = pickle.load(f)
            except Exception:
                # If the file is corrupted or version-mismatched, retrain
                self.train()
        else:
            self.train()

    def predict(self, text):
        text_lower = text.lower().strip()
        
        # 1. Passive Learning / Similarity check
        # This helps the bot learn variations of known phrases automatically
        best_match_intent = None
        highest_score = 0
        for known_text, intent in self.data:
            score = SequenceMatcher(None, text_lower, known_text).ratio()
            if score > highest_score:
                highest_score = score
                best_match_intent = intent
        
        # If it's very close but not exact, learn it and return immediately
        if 0.80 <= highest_score < 1.0:
            self.teach(text_lower, best_match_intent)
            return best_match_intent
        
        # 2. Standard ML Prediction
        # If similarity is low, let the LinearSVC classifier decide
        try:
            X = self.vectorizer.transform([text_lower])
            prediction = self.classifier.predict(X)[0]
            return prediction
        except Exception:
            return "unknown"

    def teach(self, text, intent):
        """Updates the brain's data and retrains the model."""
        text_lower = text.lower().strip()
        
        # Avoid duplicate entries in training data
        if (text_lower, intent) not in self.data:
            print(f"Brain: Learning that '{text_lower}' means '{intent}'")
            self.data.append((text_lower, intent))
            self.train() # Retrains and saves immediately to disk