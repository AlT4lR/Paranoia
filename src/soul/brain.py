import pickle, os, shutil, re
from textblob import TextBlob
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from src import config
from src.utils.logger import SoulLogger

class IntentBrain:
    def __init__(self, soul=None):
        # Increased ngram range (1, 3) to better capture phrases like "take a walk"
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 3))
        # Added class_weight='balanced' to prevent the large knowledge base from drowning out social cues
        self.classifier = LinearSVC(class_weight='balanced', max_iter=2000)
        
        # Expanded base data for better context separation and social balance
        self.base_data = [
            ("hello", "greet"), ("hi", "greet"), ("hey", "greet"), ("good evening", "greet"),
            ("bye", "exit"), ("goodbye", "exit"), ("see ya", "exit"),
            ("yes", "agree"), ("no", "negative"), ("sure", "agree"), ("okay", "agree"),
            ("what time is it", "time"), ("tell me the time", "time"),
            ("what day is it", "date"), ("today's date", "date"),
            ("who are you", "identity"), ("what is your name", "identity"),
            ("who am i", "identity"), ("do you know me", "identity"),
            ("take a walk", "fun"), ("go for a stroll", "fun"), ("let's go out", "fun"),
            ("search the web", "mine"), ("look up", "mine"), ("go search", "mine"),
            ("tell me a fact", "knowledge"), ("history", "knowledge"), ("tell me about", "knowledge"),
            ("fortune telling", "dynamic_feature"), ("calculate", "dynamic_feature")
        ]
        self.data = list(self.base_data)
        self.load_model()

    def nlp_clean(self, text):
        """Standardizes text by lowercasing and lemmatizing."""
        try:
            blob = TextBlob(str(text).lower().strip())
            return " ".join([w.lemmatize() for w in blob.words])
        except:
            return str(text).lower().strip()

    def scrub_knowledge(self):
        """Cleans citations [123] and whitespace from the knowledge base."""
        cleaned_count = 0
        new_data = []
        for phrase, intent in self.data:
            if intent == "knowledge":
                clean_phrase = re.sub(r'\[\s*\d+\s*\]', '', phrase)
                clean_phrase = " ".join(clean_phrase.split()).strip()
                
                if clean_phrase != phrase:
                    cleaned_count += 1
                
                if len(clean_phrase) > 20:
                    new_data.append((clean_phrase, intent))
            else:
                new_data.append((phrase, intent))
        
        self.data = new_data
        if cleaned_count > 0:
            SoulLogger.brain(f"Scrubbed {cleaned_count} citations from memory.")
            self.train()

    def predict(self, text):
        """Predicts intent using Direct Commands, then Fuzzy Match, then SVM."""
        clean_text = self.nlp_clean(text)
        low_text = text.lower()

        # 1. Direct Command Detection (Overrides ML to fix the "Lore Drop" issue)
        if any(w in low_text for w in ["search the web", "mine", "search for"]):
            return "mine"
        if any(w in low_text for w in ["walk", "stroll", "play", "fun", "hang out"]):
            return "fun"

        # 2. Fuzzy Matching (High precision)
        best_match, highest = None, 0
        for kt, intent in self.data:
            score = SequenceMatcher(None, clean_text, kt).ratio()
            if score > highest: highest, best_match = score, intent
        
        if highest > 0.85: 
            SoulLogger.brain(f"Fuzzy Match: '{best_match}' (Confidence: {highest:.2f})")
            return best_match
        
        # 3. ML Prediction (Generalization with balanced weights)
        try:
            if not hasattr(self.classifier, "classes_"): 
                return "default"
            
            X = self.vectorizer.transform([clean_text])
            prediction = self.classifier.predict(X)[0]
            SoulLogger.brain(f"ML Model Prediction: '{prediction}'")
            return prediction
        except Exception as e: 
            SoulLogger.err(f"Brain Prediction Error: {e}")
            return "default"

    def train(self):
        """Vectorizes data and fits the SVM classifier with re-balancing logic."""
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
            
            SoulLogger.sys(f"Brain Balanced. Social/Knowledge ratio optimized ({len(self.data)} nodes).")
        except Exception as e: 
            SoulLogger.err(f"Training Failure: {e}")

    def load_model(self):
        """Loads model from disk with corruption recovery and data merging."""
        if os.path.exists(config.BRAIN_MODEL_PATH):
            try:
                with open(config.BRAIN_MODEL_PATH, 'rb') as f:
                    v, c, d = pickle.load(f)
                    self.vectorizer, self.classifier, self.data = v, c, d
                
                # Ensure base data is always present after a load
                existing_texts = [item[0] for item in self.data]
                merged = False
                for text, intent in self.base_data:
                    if self.nlp_clean(text) not in existing_texts:
                        self.data.append((self.nlp_clean(text), intent))
                        merged = True
                if merged: self.train()
                SoulLogger.sys("Brain model loaded.")
            except:
                SoulLogger.err("Brain corruption detected. Resetting...")
                if os.path.exists(config.BRAIN_MODEL_PATH): os.remove(config.BRAIN_MODEL_PATH)
                self.train()
        else:
            self.train()

    def teach(self, text, intent):
        """Adds a new text-intent pair to the memory and retrains."""
        clean_p = self.nlp_clean(text)
        if (clean_p, intent) not in self.data:
            self.data.append((clean_p, intent))
            SoulLogger.sys(f"Learning: '{clean_p}' -> '{intent}'.")
            self.train()