# src/soul/brain.py
import pickle
import os
import shutil
from textblob import TextBlob
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from src import config
from src.utils.logger import SoulLogger

class IntentBrain:
    def __init__(self, soul=None):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self.classifier = LinearSVC()
        # Essential base data to prevent "1-class" training errors
        self.base_data = [
            ("hello", "greet"), ("hi", "greet"), 
            ("bye", "exit"), ("goodbye", "exit"),
            ("yes", "agree"), ("no", "negative")
        ]
        self.data = list(self.base_data)
        self.load_model()

    def nlp_clean(self, text):
        try:
            blob = TextBlob(str(text).lower().strip())
            return " ".join([w.lemmatize() for w in blob.words])
        except:
            return str(text).lower().strip()

    def predict(self, text):
        clean_text = self.nlp_clean(text)
        # 1. Fuzzy Matching
        best_match, highest = None, 0
        for kt, intent in self.data:
            score = SequenceMatcher(None, clean_text, kt).ratio()
            if score > highest: highest, best_match = score, intent
        if highest > 0.85: return best_match
        
        # 2. ML Prediction
        try:
            if not hasattr(self.classifier, "classes_"): return "default"
            X = self.vectorizer.transform([clean_text])
            return self.classifier.predict(X)[0]
        except: return "default"

    def train(self):
        """Saves using an Atomic Write and prevents single-class errors."""
        try:
            # ENSURE AT LEAST 2 CLASSES EXIST
            unique_labels = set([item[1] for item in self.data])
            if len(unique_labels) < 2:
                # If only 1 class, inject base data to fix the model
                for item in self.base_data:
                    if item not in self.data: self.data.append(item)
            
            texts, labels = zip(*[(self.nlp_clean(t), l) for t, l in self.data])
            X = self.vectorizer.fit_transform(texts)
            self.classifier.fit(X, labels)
            
            os.makedirs(os.path.dirname(config.BRAIN_MODEL_PATH), exist_ok=True)
            temp_path = config.BRAIN_MODEL_PATH + ".tmp"
            with open(temp_path, 'wb') as f:
                pickle.dump((self.vectorizer, self.classifier, self.data), f)
            shutil.move(temp_path, config.BRAIN_MODEL_PATH)
            SoulLogger.sys("Brain stabilized and saved.")
        except Exception as e: 
            SoulLogger.err(f"Restoration failed: {e}")

    def load_model(self):
        if os.path.exists(config.BRAIN_MODEL_PATH):
            try:
                with open(config.BRAIN_MODEL_PATH, 'rb') as f:
                    v, c, d = pickle.load(f)
                    self.vectorizer, self.classifier, self.data = v, c, d
                SoulLogger.sys("Brain model loaded.")
            except:
                SoulLogger.err("Brain corruption. Purging file...")
                if os.path.exists(config.BRAIN_MODEL_PATH): os.remove(config.BRAIN_MODEL_PATH)
                self.train()
        else:
            self.train()

    def teach(self, text, intent):
        clean_p = self.nlp_clean(text)
        if (clean_p, intent) not in self.data:
            self.data.append((clean_p, intent))
            self.train()