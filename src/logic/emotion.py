current_emotion_vector = {
    "happy": 0.2, "sad": 0.1, "playful": 0.4, "serious": 0.3
}

def analyze_emotion_vector(text: str) -> dict:
    """
    Analyzes text and returns a dictionary of emotional scores.
    This is a more nuanced approach.
    """
    # This is a simplified example. You could use more advanced models here.
    from textblob import TextBlob
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity  # -1 (neg) to 1 (pos)
    subjectivity = analysis.sentiment.subjectivity # 0 (objective) to 1 (subjective)

    vector = {
        "happy": max(0, polarity),
        "sad": max(0, -polarity),
        "playful": subjectivity * 0.8, # Playfulness is often subjective
        "serious": (1 - subjectivity) * 0.8 # Seriousness is often objective
    }
    # Normalize to make sure they sum roughly to 1
    total = sum(vector.values())
    if total > 0:
        for key in vector:
            vector[key] /= total
    return vector

def update_current_emotion(new_vector: dict):
    """Updates the current emotion state by blending with the new one."""
    global current_emotion_vector
    # Blend the new emotion with the old one to create emotional inertia
    for key, value in new_vector.items():
        current_emotion_vector[key] = (current_emotion_vector.get(key, 0) * 0.7) + (value * 0.3)

def get_emotion_description() -> str:
    """Returns a text description of the current emotional state."""
    # Find the dominant emotions
    sorted_emotions = sorted(current_emotion_vector.items(), key=lambda item: item[1], reverse=True)
    # Describe the state in a way the LLM can understand
    return f"a mix of {sorted_emotions[0][0]} ({sorted_emotions[0][1]:.0%}) and {sorted_emotions[1][0]} ({sorted_emotions[1][1]:.0%})"