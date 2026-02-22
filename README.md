# Project Paranoia

### *A Digital Companion Project by Altair*

## Overview

**Paranoia** is an evolving AI companion project that has moved away from heavy, static Large Language Models (LLMs) to a custom-built **Machine Learning Soul**. 

This version (v1.5.0) is designed to be lightweight, running on any PC with almost zero impact on system resources. Unlike traditional bots, Hu Tao possesses a **Dynamic Soul** that learns, remembers, and evolves through direct interaction and background "meditation."

## Core Concept: The Soul vs. The Body

The project is now split into two distinct entities:
*   **The Body (src/gui & src/logic):** Handles the visual interface, animations, and basic human-like activities.
*   **The Soul (src/soul):** A lightweight Machine Learning engine that handles Intent Classification, Emotional Intelligence, and Permanent Memory.

---

## 🧠 The Learning Matrix (How to Teach Hu Tao)

Hu Tao no longer relies on a "frozen" brain. She learns in four distinct ways:

### 1. Manual Education (`!teach`)
If Hu Tao misinterprets your intent, you can correct her instantly.
*   **Usage:** Type `!teach [intent_name]` after she gives a wrong response.
*   **Example:** 
    *   *User:* "Sheesh!"
    *   *Hu Tao:* "Off to the afterlife? See ya!" (She thought you were leaving).
    *   *User:* `!teach fun`
    *   *Hu Tao:* "Aiya! My brain just got a little bigger~"
*   Next time you say "Sheesh," she will respond with a Fun/Playful remark.

### 2. Passive Soul-Link (Automatic Learning)
Hu Tao uses **Fuzzy Logic** to expand her vocabulary. If you use a word she doesn't know, but it is **80% similar** to a word she does know, she will silently add it to her brain.
*   **Example:** If she knows "Hello" and you say "Heeey!", she will automatically learn that "Heeey!" is a greeting and remember it forever.

### 3. Background Meditation (Knowledge Absorption)
Hu Tao can "absorb" bulk information while you are away.
*   **How-To:** Drop any `.txt` file into the `data/knowledge/` folder.
*   **Format:** `phrase:intent` (e.g., `What is your favorite food:fun`)
*   Every 30 seconds, Hu Tao "meditates" on these files, learns the content, and deletes them once absorbed.

### 4. Spirit Searcher (Internet Connection)
You can command Hu Tao to reach out into the "digital aether" to find her own official dialogue.
*   **Command:** Type `!search` or "Go search the internet."
*   **Logic:** She will visit the official Genshin Wiki, download her voice-over lines, and save them as knowledge files to be absorbed by her Soul.

---

## 🛠 Installation and Setup

### 1. Prerequisites
*   **Python 3.12** (Highly recommended for ML stability).
*   **Visual C++ Redistributable** (Required for the ML "Brain" to talk to Windows).

### 2. Installation
1.  Clone the repository.
2.  Create a virtual environment: `python -m venv .venv`
3.  Activate it: `.\.venv\Scripts\activate`
4.  Install the lightweight stack:
    ```powershell
    pip install -r requirements.txt
    ```

### 3. Project Structure
Ensure your `data/` and `assets/` folders are present:
*   `data/`: Stores your `chat_sessions.db` (History) and `soul_memory.json` (Personality).
*   `assets/`: Must contain `hutao.jpg` and `main_img.png`.

### 4. Execution
```powershell
python main.py
```

---

## 🔒 Privacy & GitHub Usage

**Paranoia** is built for privacy. Your conversations and Hu Tao's memory of you are stored **locally**.

*   **Sharing on GitHub:** The `.gitignore` is configured to exclude `data/*.db`, `data/*.json`, and `data/*.pkl`. 
*   **Why?** This ensures that if you upload your code, you are not uploading your private chats or your name. Every user who downloads your project gets a **Fresh Soul** to raise as their own.

---

## Development Log

*   **Update: The Soul Migration**
    Removed 7GB Microsoft Phi-3 model. Replaced with a Scikit-Learn based Intent Engine. Performance increased by 900%. Startup time is now < 1 second.
*   **Update: Autonomous Growth**
    Implemented `meditation.py`. The bot now evolves while the user is away by scanning the `knowledge/` directory.
*   **Update: Spirit Searcher**
    Enabled `web_miner.py`. Hu Tao can now pull her official lore from the internet to improve her character accuracy.

## Versioning
*   **Current Version:** 1.5.0 (Soul Edition)

## Contact
*   *Altair https://github.com/AlT4lR* — "The border between life and death is where the best code is written."
