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
        # Expanded base data for better context separation
        self.base_data = [
            ("hello", "greet"), ("hi", "greet"), ("hey", "greet"),
            ("bye", "exit"), ("goodbye", "exit"), ("see ya", "exit"),
            ("yes", "agree"), ("no", "negative"),
            ("what time is it", "time"), ("tell me the time", "time"),
            ("what day is it", "date"), ("today's date", "date"),
            ("who are you", "identity"), ("what is your name", "identity"),
            ("who am i", "identity"), ("do you know me", "identity"),
            ("what do you know about me", "identity"),
            ("tell me a fact", "knowledge"), ("tell me something", "knowledge"),
            ("history", "knowledge"), ("tell me about", "knowledge")
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
        
        # 1. Fuzzy Matching (High precision)
        best_match, highest = None, 0
        for kt, intent in self.data:
            score = SequenceMatcher(None, clean_text, kt).ratio()
            if score > highest: highest, best_match = score, intent
        
        if highest > 0.85: 
            SoulLogger.brain(f"Fuzzy Logic Match: '{best_match}' (Confidence: {highest:.2f})")
            return best_match
        
        # 2. ML Prediction (Generalization)
        try:
            if not hasattr(self.classifier, "classes_"): 
                SoulLogger.sys("Brain: ML Model not trained yet. Defaulting.")
                return "default"
            
            X = self.vectorizer.transform([clean_text])
            prediction = self.classifier.predict(X)[0]
            SoulLogger.brain(f"ML Model Prediction: '{prediction}'")
            return prediction
        except Exception as e: 
            SoulLogger.err(f"Brain Prediction Error: {e}")
            return "default"

    def train(self):
        try:
            unique_labels = set([item[1] for item in self.data])
            if len(unique_labels) < 2:
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
            SoulLogger.sys(f"Brain stabilized. Knowledge base size: {len(self.data)} nodes.")
        except Exception as e: 
            SoulLogger.err(f"Brain Training Failure: {e}")

    def load_model(self):
        if os.path.exists(config.BRAIN_MODEL_PATH):
            try:
                with open(config.BRAIN_MODEL_PATH, 'rb') as f:
                    v, c, d = pickle.load(f)
                    self.vectorizer, self.classifier, self.data = v, c, d
                
                existing_texts = [item[0] for item in self.data]
                merged = False
                for text, intent in self.base_data:
                    if self.nlp_clean(text) not in existing_texts:
                        self.data.append((self.nlp_clean(text), intent))
                        merged = True
                if merged: self.train()
                SoulLogger.sys("Brain model loaded successfully.")
            except:
                SoulLogger.err("Brain corruption detected. Resetting...")
                if os.path.exists(config.BRAIN_MODEL_PATH): os.remove(config.BRAIN_MODEL_PATH)
                self.train()
        else:
            self.train()

    def teach(self, text, intent):
        clean_p = self.nlp_clean(text)
        if (clean_p, intent) not in self.data:
            self.data.append((clean_p, intent))
            SoulLogger.sys(f"Learning: '{clean_p}' is now linked to '{intent}'.")
            self.train()