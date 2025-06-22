# --- Hu Tao Color Scheme ---
HU_TAO_RED = "#FF4500"
HU_TAO_MESSAGE = "#FFB347"
HU_TAO_WHITE = "#FFFAFA"
HU_TAO_DARK = "#333333"

# --- CharacterAI Setup ---
# IMPORTANT: Replace 'YOUR_CHARACTER_AI_KEY' with your actual key
CAI_API_KEY = 'U3dJdreV9rrvUiAnILMauI-oNH838a8E_kEYfOFPalE' # Your CharacterAI API Key
USER_NAME = "Altair"  # User's name in the conversation
DEFAULT_USER_NAME = "Altair"  # Default display name for the user
IDLE_TIMEOUT = 180  # seconds before triggering an idle response
# IMPORTANT: Replace 'YOUR_CHARACTER_ID' with the ID of your Hu Tao character
CHAR_ID = "kBjZiwTQ"  # Hutao Character ID

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
ACTIVITY_DURATION = 60  # seconds (how long an activity takes)

# --- Emotion Recognition Setup ---
EMOTIONS = ["Happy", "Sad", "Angry", "Fearful", "Surprised", "Neutral", "Disgusted", "Worried", "Loving", "Obsessed", "Endearing"] # Extended List
EMOTION_COLORS = {
    "Happy": "#FFD700",     # Gold
    "Sad": "#87CEEB",       # Sky Blue
    "Angry": "#FF4500",     # Orange Red
    "Fearful": "#90EE90",   # Light Green
    "Surprised": "#DDA0DD",  # Plum
    "Neutral": "#FFFFFF",   # White
    "Disgusted": "#8B4513",  # Saddle Brown
    "Worried": "#A9A9A9",   # Dark Gray
    "Loving": "#FF69B4",    # Hot Pink
    "Obsessed": "#800080",  # Purple
    "Endearing": "#FFA07A",   # Light Salmon
}

# --- Affection System ---
DEFAULT_AFFECTION = 50
MAX_AFFECTION = 100
MIN_AFFECTION = 0
AFFECTION_CHANGE_AMOUNT = 5  # Adjust the amount of affection change per interaction

# --- Personality Traits ---
PERSONALITY_TRAITS = {
    "optimism": 0.5,    # Positive (0.0 to 1.0)
    "cynicism": 0.2,    # Negative
    "playfulness": 0.8,   # Positive
    "seriousness": 0.3,  # Neutral/Situational
    "mischievousness": 0.7, # Neutral/Can be + or -
    "respectfulness": 0.6,  # Positive
    "worldliness": 0.4,    # Neutral/Maturity
    "impatience": 0.2,    # Negative
    "compassion": 0.7      # Positive
}

TRAIT_ADJUSTMENT_RATE = 0.01  # How much traits can change per conversation
POSITIVE_TRAITS = ["optimism", "playfulness", "respectfulness", "compassion"]
NEGATIVE_TRAITS = ["cynicism", "impatience"]
NEUTRAL_TRAITS = ["seriousness", "mischievousness", "worldliness"] #Traits that can either positively or negatively
INFLUENCE_FACTOR = 0.005 # Rate that personality effect other aspects

# --- Database Configuration ---
DATABASE_NAME = "chat_sessions.db" # Name for your SQLite database file

# --- Asset Paths ---
# Use os.path.join and potentially relative paths if assets are inside src
# from src import __file__ as src_path
# BASE_DIR = os.path.dirname(os.path.abspath(src_path))
# ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
# HUTAO_IMAGE_PATH = os.path.join(ASSETS_DIR, 'hutao.jpg')

# Or, if assets are at the root level:
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Go up two levels from config.py
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
HUTAO_IMAGE_PATH = os.path.join(ASSETS_DIR, 'hutao.jpg')


# --- Other Settings ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600