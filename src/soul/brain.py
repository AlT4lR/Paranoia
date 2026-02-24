# src/soul/brain.py
import pickle, os, shutil, re, threading
from textblob import TextBlob
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from src import config
from src.utils.logger import SoulLogger

class IntentBrain:
    def __init__(self, soul=None):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 3))
        # dual='auto' for performance on large datasets
        self.classifier = LinearSVC(class_weight='balanced', max_iter=2000, dual='auto')
        self.lock = threading.Lock() # Spiritual stability lock
        
        # FIXED: Base data is now neutral/student focused
        self.base_data = [
            ("hello", "greet"), ("hi", "greet"), ("hey", "greet"),
            ("bye", "exit"), ("goodbye", "exit"),
            ("yes", "agree"), ("no", "negative"),
            ("what time is it", "time"),
            ("who are you", "identity"),
            ("search the web", "mine"),
            ("tell me a fact", "knowledge"),
            ("what is the news", "gossip"),
            ("any gossip", "gossip")
        ]
        self.data = list(self.base_data)
        self.load_model()

    def nlp_clean(self, text):
        """Standardizes text for the ML model."""
        try:
            blob = TextBlob(str(text).lower().strip())
            return " ".join([w.lemmatize() for w in blob.words])
        except:
            return str(text).lower().strip()

    def audit_soul_memory(self):
        """
        THE PURGE: Scans internal memory and prunes all 
        Genshin/Hu Tao related data points.
        """
        with self.lock:
            # The list of 'Old Life' echoes to be silenced
            forbidden_echoes = [
                "funeral", "mora", "director", "cremation", "wangsheng", 
                "coffin", "zhongli", "qiqi", "liyue", "homa", "parlor", 
                "aiya", "hee-hee", "hilichurl", "hilitune", "baizhu", 
                "wangshu", "adeptus", "archon", "tevat", "teyvat", "vision"
            ]
            
            initial_count = len(self.data)
            
            # Prune logic: remove if ANY forbidden word is in the fact
            self.data = [
                (phrase, intent) for phrase, intent in self.data 
                if not any(echo in phrase.lower() for echo in forbidden_echoes)
            ]
            
            removed_count = initial_count - len(self.data)
            if removed_count > 0:
                SoulLogger.brain(f"Soul Audit: Pruned {removed_count} echoes of the past persona.")
                self._train_internal()
                return True
        return False

    def reindex_mass_data(self):
        """Categorizes 'knowledge' nodes into Student-Persona intents."""
        with self.lock:
            topic_map = {
                "literature": ["poem", "book", "author", "writing", "literature", "novel", "prose", "essay"],
                "academy_life": ["student", "academy", "school", "dorm", "class", "exam", "grades", "university", "professor"],
                "introversion": ["quiet", "shy", "alone", "nervous", "library", "crowd", "hide", "social", "anxiety"],
                "piano_studies": ["piano", "music", "composition", "notes", "melody", "keys", "classical", "sonata"]
            }
            
            reindexed_count = 0
            new_data = []
            
            for phrase, intent in self.data:
                if intent == "knowledge":
                    found_new_intent = False
                    for category, keywords in topic_map.items():
                        if any(kw in phrase.lower() for kw in keywords):
                            new_data.append((phrase, category))
                            reindexed_count += 1
                            found_new_intent = True
                            break
                    if not found_new_intent:
                        new_data.append((phrase, intent))
                else:
                    new_data.append((phrase, intent))
            
            if reindexed_count > 0:
                self.data = new_data
                SoulLogger.brain(f"Re-Indexing: Moved {reindexed_count} nodes into specific personality categories.")
                self._train_internal()
                return True
        return False

    def scrub_knowledge(self):
        """Cleans citations and junk text."""
        with self.lock:
            cleaned_count = 0
            new_data = []
            for phrase, intent in self.data:
                if intent in ["knowledge", "literature", "academy_life", "introversion"]:
                    # Clean Wiki citations [1], [edit]
                    clean_phrase = re.sub(r'\[\s*[\d\w\s]+\s*\]', '', phrase)
                    clean_phrase = " ".join(clean_phrase.split()).strip()
                    if clean_phrase != phrase:
                        cleaned_count += 1
                    if len(clean_phrase) > 20:
                        new_data.append((clean_phrase, intent))
                else:
                    new_data.append((phrase, intent))
            
            self.data = new_data
            if cleaned_count > 0:
                SoulLogger.brain(f"Scrubbed {cleaned_count} citations.")
                self._train_internal()

    def predict(self, text):
        """Predicts intent with threading protection."""
        with self.lock:
            clean_text = self.nlp_clean(text)
            low_text = text.lower()

            # Direct overrides
            if any(w in low_text for w in ["search the web", "mine", "search for"]):
                return "mine"

            # Fuzzy Match
            best_match, highest = None, 0
            for kt, intent in self.data:
                score = SequenceMatcher(None, clean_text, kt).ratio()
                if score > highest: highest, best_match = score, intent
            
            if highest > 0.85: 
                return best_match
            
            # ML Model
            try:
                if not hasattr(self.classifier, "classes_"): 
                    return "default"
                X = self.vectorizer.transform([clean_text])
                prediction = self.classifier.predict(X)[0]
                return prediction
            except Exception as e: 
                SoulLogger.err(f"Brain Prediction Error: {e}")
                return "default"

    def train(self):
        with self.lock:
            self._train_internal()

    def _train_internal(self):
        """Fits the SVM model to the current dataset."""
        try:
            SoulLogger.brain("I'm reorganizing my thoughts... this might take a moment.")
            unique_labels = set([item[1] for item in self.data])
            if len(unique_labels) < 2:
                for item in self.base_data:
                    if item not in self.data: self.data.append(item)
            
            texts, labels = zip(*[(self.nlp_clean(t), l) for t, l in self.data])
            X = self.vectorizer.fit_transform(texts)
            self.classifier.fit(X, labels)
            
            os.makedirs(os.path.dirname(config.BRAIN_MODEL_PATH), exist_ok=True)
            with open(config.BRAIN_MODEL_PATH, 'wb') as f:
                pickle.dump((self.vectorizer, self.classifier, self.data), f)
            
            SoulLogger.sys(f"Brain Balanced ({len(self.data)} nodes). Ready to talk again.")
        except Exception as e: 
            SoulLogger.err(f"Training Failure: {e}")

    def load_model(self):
        if os.path.exists(config.BRAIN_MODEL_PATH):
            try:
                with open(config.BRAIN_MODEL_PATH, 'rb') as f:
                    v, c, d = pickle.load(f)
                    self.vectorizer, self.classifier, self.data = v, c, d
                SoulLogger.sys("Brain model loaded.")
            except:
                self._train_internal()
        else:
            self._train_internal()

    def teach(self, text, intent):
        with self.lock:
            clean_p = self.nlp_clean(text)
            if (clean_p, intent) not in self.data:
                self.data.append((clean_p, intent))
                self._train_internal()