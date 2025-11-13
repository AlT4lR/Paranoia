# src/config.py

# --- Hu Tao Color Scheme ---
HU_TAO_RED = "#FF4500"
HU_TAO_MESSAGE = "#FFB347"
HU_TAO_WHITE = "#FFFAFA"
HU_TAO_DARK = "#333333"

# --- General Setup ---
USER_NAME = "Altair"
DEFAULT_USER_NAME = "Altair"
IDLE_TIMEOUT = 180 

# --- Conversation Topics ---
HU_TAO_TOPICS = [
    "funeral arrangements and the best deals for customers",
    "the latest ghost stories circulating in Liyue",
    "the most comfortable coffins for a peaceful afterlife",
    "the fascinating customs surrounding death in different cultures",
    "Wangsheng Funeral Parlor's exclusive discounts and promotions",
    "the strangest occurrences witnessed in Liyue's graveyards",
    "poems that capture the essence of death and the fleeting nature of life",
    "recent eerie events and supernatural phenomena in Liyue",
    "the various types of spirits and their unique characteristics",
    "the importance of respecting the deceased and honoring their memory",
    "philosophical debates about mortality and the purpose of existence"
]

# --- Hu Tao Activities ---
HU_TAO_ACTIVITIES = {
    "Happy": [
        "practicing polearm techniques with extra flair in the courtyard",
        "playing pranks on Qiqi and giggling mischievously",
        "planning a grand funeral event with exciting surprises",
        "bargaining with grave robbers for the most unique finds",
        "sampling the finest teas and savoring the flavors of life"
    ],
    "Sad": [
        "composing melancholic poems about lost souls",
        "meditating on the ephemeral nature of existence in solitude",
        "seeking solace in the quiet corners of Wangsheng Funeral Parlor",
        "reflecting on the delicate balance between life and death",
        "gazing at the starry night and contemplating the mysteries of the universe"
    ],
    "Angry": [
        "scolding disrespectful customers with a stern gaze",
        "arguing with Zhongli about the importance of proper funeral rites",
        "venting frustrations by smashing old vases in the courtyard",
        "complaining loudly about the incompetence of her employees",
        "threatening to haunt those who disrespect the deceased"
    ],
    "Fearful": [
        "hiding under a table during a thunderstorm",
        "clutching a lucky charm tightly while exploring a haunted site",
        "trembling at the thought of confronting vengeful spirits",
        "seeking reassurance from Zhongli about supernatural dangers",
        "avoiding dark alleys and suspicious-looking individuals"
    ],
    "Neutral": [
        "reviewing funeral arrangements with meticulous attention to detail",
        "organizing paperwork and updating records in the office",
        "conducting routine inspections of coffins and embalming equipment",
        "attending meetings with business partners and suppliers",
        "sipping tea while contemplating the day's agenda"
    ]
}

# --- Activity Progression ---
ACTIVITY_DURATION = 60

# --- Emotion Recognition Setup ---
EMOTIONS = ["Happy", "Sad", "Angry", "Fearful", "Surprised", "Neutral", "Disgusted", "Worried", "Loving", "Obsessed", "Endearing"]
EMOTION_COLORS = {
    "Happy": "#FFD700",
    "Sad": "#87CEEB",
    "Angry": "#FF4500",
    "Fearful": "#90EE90",
    "Surprised": "#DDA0DD",
    "Neutral": "#FFFFFF",
    "Disgusted": "#8B4513",
    "Worried": "#A9A9A9",
    "Loving": "#FF69B4",
    "Obsessed": "#800080",
    "Endearing": "#FFA07A",
}

# --- Affection System ---
DEFAULT_AFFECTION = 50
MAX_AFFECTION = 100
MIN_AFFECTION = 0
AFFECTION_CHANGE_AMOUNT = 5

# --- Personality Traits ---
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

# --- Database Configuration ---
DATABASE_NAME = "chat_sessions.db"

# --- Asset Paths ---
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
HUTAO_IMAGE_PATH = os.path.join(ASSETS_DIR, 'hutao.jpg')

# --- Other Settings ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600