# src/logic/emotion.py

from textblob import TextBlob  # For sentiment analysis

# Import configuration constants
from src import config

# --- Module-level variable for Emotion State ---
# This variable holds the character's current emotional state.
# It is initialized to the default.
current_emotion = "Neutral" # Initialize with a default emotion


def analyze_emotion(text: str) -> str:
    """
    Analyzes the emotional tone of the input text using keyword matching
    and TextBlob sentiment analysis.

    Args:
        text: The input string to analyze.

    Returns:
        A string representing the detected emotion (e.g., "Happy", "Sad", "Neutral").
    """
    text_lower = text.lower()  # Convert to lowercase once for efficiency

    # --- Keyword-based detection (More direct control) ---
    # This prioritizes specific words that strongly indicate an emotion
    if any(word in text_lower for word in ["happy", "joyful", "delighted", "excited", "cheerful", "yay", "hehe"]):
        return "Happy"
    elif any(word in text_lower for word in ["sad", "depressed", "unhappy", "grief", "mourning", "tear", "sob"]):
        return "Sad"
    elif any(word in text_lower for word in ["angry", "furious", "irate", "annoyed", "grr", "hmpf", "tsk"]):
        return "Angry"
    elif any(word in text_lower for word in ["fearful", "scared", "afraid", "terrified", "spooked", "eek", "gulp"]):
        return "Fearful"
    elif any(word in text_lower for word in ["surprised", "amazed", "astonished", "shocked", "wow", "oh my"]):
        return "Surprised"
    elif any(word in text_lower for word in ["disgusted", "repulsed", "sickened", "nauseated", "eww", "ugh", "gross"]):
        return "Disgusted"
    elif any(word in text_lower for word in ["worried", "anxious", "concerned", "apprehensive", "nervous", "fret"]):
        return "Worried"
    elif any(word in text_lower for word in ["loving", "affectionate", "caring", "romantic", "love", "dear", "sweetheart", "honey"]):
        return "Loving"
    # Note: "Obsessed" and "Endearing" might need careful handling depending on context
    elif any(word in text_lower for word in ["obsessed", "fixated", "infatuated", "stalking", "can't stop thinking"]):
         return "Obsessed" # Potentially risky, handle with care
    elif any(word in text_lower for word in ["darling", "sweetheart", "dearest", "honey", "cutie", "my dear"]):
        return "Endearing"
    elif any(word in text_lower for word in ["neutral", "okay", "alright", "fine"]):
         return "Neutral" # Explicit neutral keywords


    # --- Fallback to TextBlob Sentiment (if no strong keywords matched) ---
    # This provides a general positive/negative/neutral baseline
    try:
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity # -1.0 (negative) to 1.0 (positive)
        # subjectivity = analysis.sentiment.subjectivity # 0.0 (objective) to 1.0 (subjective)

        if polarity > 0.4: # Threshold for positive sentiment
            return "Happy" # Or perhaps a less intense positive like "Content" if you had it
        elif polarity < -0.4: # Threshold for negative sentiment
            return "Sad" # Or perhaps "Unhappy" or "Irritated" depending on intensity needed
        # Add checks for more specific negative emotions if needed based on polarity range

        # If polarity is close to 0, consider it Neutral
        return "Neutral"

    except Exception as e:
        print(f"Error during TextBlob analysis: {e}")
        return "Neutral" # Default to Neutral on error


# --- Functions to Get and Set Emotion State ---

def get_current_emotion() -> str:
    """Returns the character's current emotional state."""
    global current_emotion
    return current_emotion

def set_current_emotion(emotion: str):
    """
    Sets the character's current emotional state.
    Validates the input emotion against the defined list (optional but good practice).
    """
    global current_emotion
    # Optional: Add validation to ensure the emotion is in the EMOTIONS list
    # if emotion in config.EMOTIONS:
    current_emotion = emotion
    # else:
    #     print(f"Warning: Attempted to set invalid emotion: {emotion}")
    #     current_emotion = "Neutral" # Default to neutral if invalid