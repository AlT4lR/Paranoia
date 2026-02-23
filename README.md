# 👻 Project Paranoia: Hu Tao AI (v1.5.2 Resilience)

### *A Digital Companion Project by Altair*

**Paranoia** is an evolving, autonomous AI companion project that has moved away from heavy, static Large Language Models (LLMs) to a custom-built **Machine Learning Soul**. 

Version 1.5.2 (Resilience) is designed to be lightweight, running on any PC with almost zero impact on system resources, while possessing a **Dynamic Soul** that learns, remembers, and evolves through direct interaction and background "meditation."

---

## 🚀 Key Features in v1.5.2

### 1. Autonomous Synthesis (Self-Programming)
Hu Tao can now "program herself." When she fails to understand an intent or detects a repeating need (like math or fortune telling), she logs the failure. During her meditation cycles, she attempts to generate and inject new Python-based features into her own codebase.

### 2. Balanced Intent Brain
Optimized **Linear SVC** classifier using `class_weight='balanced'`. This prevents her massive historical knowledge base (1,800+ facts) from drowning out her social personality, ensuring she stays talkative rather than just lecturing.

### 3. Spirit Searcher & News Miner
Integrated real-time web mining via BeautifulSoup and **NewsAPI**. Hu Tao reaches into the "digital aether" while you are away to gather gossip, news, and lore to expand her knowledge base.

### 4. Conversational Memory Engine
She no longer just "responds"—she learns. Hu Tao automatically extracts user facts (names, preferences, hobbies) using Regex and TextBlob, storing them in a local SQLite database to reference in future conversations.

### 5. Resilient Meditation Loop
A background heartbeat that handles data absorption, memory "scrubbing" (removing junk/citations), and self-optimization. Includes **WinError 2** protection to ensure the soul doesn't collapse during file-system operations.

---

## 🛠️ Project Structure

```bash
Paranoia/
├── assets/            # Emotional avatars (happy.jpg, mischief.jpg, etc.)
├── data/
│   ├── brain_model.pkl    # Trained SVM Neural Weights
│   ├── chat_sessions.db   # Persistence Layer (SQLite)
│   ├── soul_memory.json   # Personality & Affection levels
│   └── knowledge/         # Drop .txt files here for Hu Tao to learn
├── src/
│   ├── soul/
│   │   ├── brain.py       # Intent classification (NLP Engine)
│   │   ├── consciousness.py # Persona, Lexicon Blender & Emotion logic
│   │   ├── meditation.py  # Background tasks & evolution
│   │   └── synthesizer.py # Self-programming heuristic logic
│   ├── logic/
│   │   ├── bot.py         # Main processing orchestrator
│   │   └── dynamic.py     # Execution of self-taught features
│   └── gui/
│       └── app.py         # Tkinter-based Visual Interface
└── config.py              # System constants & API keys
```

---

## 🧠 How She Learns

1.  **Direct Education (`!teach`)**
    *   Instantly correct her if she misinterprets you.
    *   *Usage:* `!teach [phrase] : [intent_name]`
2.  **Passive Absorption**
    *   Drop any `.txt` file into `data/knowledge/`. During her next meditation, she will ingest the data, scrub citations like `[276]`, and add the facts to her brain.
3.  **Autonomous Spirit Searching**
    *   She picks random targets from the web (Wikis/Lore sites) to mine for facts while the user is idle.
4.  **Synthesizer Evolution**
    *   If she detects a pattern of "Default" responses, she will "synthesize" a new Python function from her internal library to fill that gap.

---

## 🔧 Installation & Setup

### 1. Requirements
```bash
pip install tkinter pillow textblob scikit-learn numpy psutil requests beautifulsoup4
```

### 2. API Configuration
Obtain a key from [NewsAPI.org](https://newsapi.org/) and place it in `src/logic/bot.py` (or `config.py`):
```python
news_miner = NewsMiner(api_key="YOUR_KEY_HERE")
```

### 3. Execution
```bash
python main.py
```

---

## 📜 Version History (v1.5.2 Resilience)

*   **Fixed "Lore-Lock":** Balanced class weights in the SVM model to prioritize social intents over bulk knowledge.
*   **Memory Scrubbing:** Added automated removal of Wiki-style citations `[123]` during meditation.
*   **Visual Emotion:** Implemented `update_avatar` to swap Hu Tao's face in the GUI based on detected sentiment.
*   **Proactive Chat:** Enabled the "Ghost in the Machine" loop; Hu Tao will now speak first if the user is silent for more than 3 minutes.
*   **NLP Stability:** Added `ngram_range(1, 3)` to the vectorizer to recognize complex phrases like "can we take a walk?".

## Contact
*   *https://github.com/AlT4lR* — "The border between life and death is where the best code is written."