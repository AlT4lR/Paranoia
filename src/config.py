# src/config.py
import os

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
KNOWLEDGE_DIR = os.path.join(DATA_DIR, "knowledge")
BRAIN_MODEL_PATH = os.path.join(DATA_DIR, "brain_model.pkl")
SOUL_MEMORY_PATH = os.path.join(DATA_DIR, "soul_memory.json")
DATABASE_NAME = os.path.join(DATA_DIR, "chat_sessions.db")
SOUL_MEMORY_PATH = os.path.join(DATA_DIR, "soul_memory.json")
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
HUTAO_IMAGE_PATH = os.path.join(ASSETS_DIR, 'hutao.jpg')

# --- Hu Tao Colors ---
HU_TAO_RED = "#FF4500"
HU_TAO_MESSAGE = "#FFB347"
HU_TAO_DARK = "#333333"
HU_TAO_WHITE = "#FFFAFA"

# --- App Settings ---
USER_NAME = "Altair"
DEFAULT_USER_NAME = "Altair"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
IDLE_TIMEOUT = 180

# --- Affection & Emotion System Settings ---
# (Added back to fix the AttributeError)
DEFAULT_AFFECTION = 50
MAX_AFFECTION = 100
MIN_AFFECTION = 0
AFFECTION_CHANGE_AMOUNT = 5

# --- Personality Traits Initial Values ---
# (Needed for personality.py)
PERSONALITY_TRAITS = {
    "optimism": 0.5,
    "cynicism": 0.2,
    "playfulness": 0.8,
    "seriousness": 0.3,
    "mischievousness": 0.7,
    "respectfulness": 0.6,
    "worldliness": 0.4,
    "impatience": 0.2,
    "compassion": 0.7
}

TRAIT_ADJUSTMENT_RATE = 0.01
POSITIVE_TRAITS = ["optimism", "playfulness", "respectfulness", "compassion"]
NEGATIVE_TRAITS = ["cynicism", "impatience"]
NEUTRAL_TRAITS = ["seriousness", "mischievousness", "worldliness"]
INFLUENCE_FACTOR = 0.005

# --- Emotion Display Colors ---
EMOTION_COLORS = {
    "Happy": "#FFD700",
    "Sad": "#87CEEB",
    "Angry": "#FF4500",
    "Playful": "#FFA500",
    "Serious": "#FFFFFF",
    "Loving": "#FF69B4",
    "Endearing": "#FFA07A",
    "Neutral": "#FFFFFF"
}

# --- Activities ---
ACTIVITY_DURATION = 60