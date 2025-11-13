# Import configuration constants
from src import config

# --- Module-level variables for Character State ---
# These global variables hold the character's personality, affection, and relationship status.

# Initialize affection from configuration
user_affection = config.DEFAULT_AFFECTION

# Initialize personality traits from configuration
personality_traits = config.PERSONALITY_TRAITS.copy()

# Add new relationship metrics
relationship_status = {
    "trust": 50,       # (0-100) Does the user seem trustworthy/supportive?
    "familiarity": 10, # (0-100) How much personal info has been shared?
    "tension": 0       # (0-100) Is there conflict in the recent conversation?
}


# --- Affection Management ---

def adjust_affection(amount: int):
    """
    Adjusts the character's affection towards the user by a specified amount.
    Clamps the affection value between MIN_AFFECTION and MAX_AFFECTION.

    Args:
        amount: The integer amount to add to the current affection level.
    """
    global user_affection
    user_affection += amount
    # Clamp the value between the defined min and max
    user_affection = max(config.MIN_AFFECTION, min(config.MAX_AFFECTION, user_affection))
    print(f"Affection adjusted by {amount}. New affection: {user_affection}")

def adjust_affection_based_on_emotion(emotion: str, change_amount: int):
    """
    Adjusts affection based on the character's detected emotion.

    Args:
        emotion: The current emotional state of the character.
        change_amount: The base amount to change affection by.
    """
    # Positive emotions increase affection, negative decrease it
    if emotion in ["Happy", "Endearing", "Loving"]:
        adjust_affection(change_amount)
    elif emotion in ["Angry", "Disgusted", "Fearful"]:
        adjust_affection(-change_amount)


# --- Relationship Status Management (New Section) ---

def adjust_relationship_status(metric: str, amount: int):
    """
    Adjusts a specific relationship status metric.
    Clamps the value between 0 and 100.

    Args:
        metric: The relationship metric to adjust ("trust", "familiarity", "tension").
        amount: The integer amount to add to the current metric value.
    """
    global relationship_status
    if metric in relationship_status:
        relationship_status[metric] += amount
        # Clamp the value between 0 and 100
        relationship_status[metric] = max(0, min(100, relationship_status[metric]))
        print(f"Relationship status '{metric}' adjusted by {amount}. New value: {relationship_status[metric]}")
    else:
        print(f"Warning: Attempted to adjust unknown relationship metric: {metric}")

def get_relationship_status() -> dict:
    """Returns a copy of the current relationship status dictionary."""
    global relationship_status
    return relationship_status.copy()


# --- Personality Trait Analysis and Adjustment ---

def analyze_conversation_traits(conversation_history: list) -> dict:
    """
    Analyzes recent conversation history to detect expressions of personality traits.
    This is a simplified keyword-based analysis.

    Args:
        conversation_history: A list of strings representing the recent conversation turns.

    Returns:
        A dictionary where keys are trait names and values are floats representing
        the detected intensity of that trait in the recent history.
    """
    analysis = {trait: 0.0 for trait in personality_traits}

    # Analyze the last 5 lines to focus on recent interaction style
    recent_history = " ".join(conversation_history[-5:])
    recent_history_lower = recent_history.lower()

    # --- Keyword-based trait detection ---
    if any(word in recent_history_lower for word in ["hope", "bright side", "positive", "wonderful", "amazing", "believe", "confident"]):
        analysis["optimism"] += 0.1
    if any(word in recent_history_lower for word in ["pointless", "meaningless", "waste of time", "doomed", "inevitable", "pathetic", "useless", "sigh", "fatalistic"]):
        analysis["cynicism"] += 0.1
    if any(word in recent_history_lower for word in ["joke", "funny", "tease", "prank", "silly", "laugh", "amuse", "heehee", "kidding"]):
        analysis["playfulness"] += 0.1
    if any(word in recent_history_lower for word in ["important", "matter of fact", "consider", "reflection", "thoughtful", "grave", "solemn", "serious"]):
        analysis["seriousness"] += 0.1
    if any(word in recent_history_lower for word in ["trick", "sneak", "surprise", "rascal", "impish", "naughty", "scheme", "secret", "plan"]):
        analysis["mischievousness"] += 0.1
    if any(word in recent_history_lower for word in ["honor", "respect", "courtesy", "polite", "deference", "esteem", "revere", "sir", "madam"]):
        analysis["respectfulness"] += 0.1
    if any(word in recent_history_lower for word in ["hurry", "rush", "wait", "delay", "bother", "late", "annoying", "impatient", "come on"]):
        analysis["impatience"] += 0.1
    if any(word in recent_history_lower for word in ["sympathy", "care", "comfort", "console", "kind", "gentle", "empathy", "poor thing", "there there"]):
        analysis["compassion"] += 0.1

    return analysis

def adjust_personality_traits(analysis_results: dict):
    """
    Adjusts personality traits based on recent conversation analysis results
    and accounts for inter-trait influence.

    Args:
        analysis_results: A dictionary of detected trait intensities.
    """
    global personality_traits

    # --- Apply Direct Influence from Conversation ---
    for trait, value in analysis_results.items():
        personality_traits[trait] += value * config.TRAIT_ADJUSTMENT_RATE
        # Clamp value between 0.0 and 1.0
        personality_traits[trait] = max(0.0, min(1.0, personality_traits[trait]))

    # --- Apply Inter-Trait Influence ---
    trait_influences = {trait: 0.0 for trait in personality_traits}

    for positive_trait in config.POSITIVE_TRAITS:
        for negative_trait in config.NEGATIVE_TRAITS:
            # Negative traits diminish positive traits
            influence_neg_on_pos = (personality_traits[negative_trait] - 0.5) * config.INFLUENCE_FACTOR
            trait_influences[positive_trait] -= influence_neg_on_pos

            # High positive traits reduce negative traits
            influence_pos_on_neg = (personality_traits[positive_trait] - 0.5) * config.INFLUENCE_FACTOR
            trait_influences[negative_trait] -= influence_pos_on_neg

        for neutral_trait in config.NEUTRAL_TRAITS:
            # Positive traits influence neutral traits
            influence_pos_on_neut = (personality_traits[positive_trait] - 0.5) * config.INFLUENCE_FACTOR
            trait_influences[neutral_trait] += influence_pos_on_neut

            # Negative traits influence neutral traits
            influence_neg_on_neut = (personality_traits[negative_trait] - 0.5) * config.INFLUENCE_FACTOR
            trait_influences[neutral_trait] -= influence_neg_on_neut


    # Apply calculated influences simultaneously
    for trait, influence in trait_influences.items():
        personality_traits[trait] += influence
        # Re-clamp after influence application
        personality_traits[trait] = max(0.0, min(1.0, personality_traits[trait]))

    # Worldliness increases over time with interactions
    personality_traits["worldliness"] += 0.002
    personality_traits["worldliness"] = max(0.0, min(1.0, personality_traits["worldliness"]))

    print("Personality traits adjusted:", {k: round(v, 3) for k, v in personality_traits.items()})


# --- Accessor Functions ---

def get_user_affection() -> int:
    """Returns the current user affection level."""
    global user_affection
    return user_affection

def get_personality_traits() -> dict:
    """Returns a copy of the current personality traits dictionary."""
    global personality_traits
    return personality_traits.copy()