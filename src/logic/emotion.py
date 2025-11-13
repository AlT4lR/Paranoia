# src/logic/emotion.py (Corrected Version)

from textblob import TextBlob

# Module-level variable holding the current emotion state.
current_emotion_vector = {
    "Happy": 0.2, 
    "Sad": 0.1, 
    "Playful": 0.4, 
    "Serious": 0.3,
    "Angry": 0.0,
    "Loving": 0.1,
    "Endearing": 0.1
}

def _analyze_emotion_vector(text: str) -> dict:
    """
    Analyzes text and returns a dictionary of emotional scores.
    (Internal helper function)
    """
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity  # -1 (neg) to 1 (pos)
    subjectivity = analysis.sentiment.subjectivity # 0 (objective) to 1 (subjective)

    vector = {
        "Happy": max(0, polarity * subjectivity),
        "Sad": max(0, -polarity),
        "Playful": subjectivity * 0.8,
        "Serious": (1 - subjectivity) * 0.8,
        "Angry": max(0, -polarity * (1 - subjectivity)), # Anger is often negative and objective
        "Loving": max(0, polarity * 0.5),
        "Endearing": max(0, polarity * 0.7)
    }
    
    # Normalize to prevent runaway values
    total = sum(vector.values())
    if total > 0:
        for key in vector:
            vector[key] /= total
            
    return vector

def _update_current_emotion_vector(new_vector: dict):
    """
    Updates the current emotion state by blending with the new one for emotional inertia.
    (Internal helper function)
    """
    global current_emotion_vector
    for key, value in new_vector.items():
        # Blend the new emotion with the old one
        current_emotion_vector[key] = (current_emotion_vector.get(key, 0) * 0.7) + (value * 0.3)

# --- Public API Functions ---

def analyze_and_update_emotion_from_text(text: str):
    """
    Analyzes a piece of text and updates the character's internal emotional state.
    This is the main function for processing emotion from new text.
    """
    new_vector = _analyze_emotion_vector(text)
    _update_current_emotion_vector(new_vector)

def get_emotion_description_for_prompt() -> str:
    """
    Returns a detailed text description of the current emotional state for the LLM's system prompt.
    """
    global current_emotion_vector
    # Find the two most dominant emotions
    sorted_emotions = sorted(current_emotion_vector.items(), key=lambda item: item[1], reverse=True)
    # Describe the state in a way the LLM can understand
    return f"a mix of {sorted_emotions[0][0]} ({sorted_emotions[0][1]:.0%}) and {sorted_emotions[1][0]} ({sorted_emotions[1][1]:.0%})"

def get_dominant_emotion() -> str:
    """
    Returns the single most dominant emotion as a capitalized string (e.g., "Playful").
    This is used for the GUI display and for simplified logic checks.
    """
    global current_emotion_vector
    if not current_emotion_vector:
        return "Neutral"
    # Find the emotion with the highest score
    dominant_emotion = max(current_emotion_vector, key=current_emotion_vector.get)
    return dominant_emotion