# src/logic/activity.py

import random
import asyncio # Needed for time tracking

# Import configuration constants
from src import config

# --- Global/Module-level variables for Activity State ---
# These variables hold the current state of the character's activity.
# In a more complex application, this state might be part of a larger
# character state object or class, but for now, global module variables
# are sufficient to match the original script's structure.
current_activity = None
activity_start_time = None

def choose_activity(current_emotion: str = "Neutral"):
    """
    Selects a new random activity for Hu Tao based on her current emotion.
    Initializes or updates the current activity and its start time.

    Args:
        current_emotion: The character's current emotional state (string).
                         Defaults to "Neutral" if not provided or emotion is unknown.

    Returns:
        A tuple containing the chosen activity string and its start time (timestamp).
    """
    global current_activity, activity_start_time

    # Get activities based on the emotion from the configuration
    # Use Neutral as a fallback if the emotion doesn't have specific activities defined
    activities = config.HU_TAO_ACTIVITIES.get(current_emotion, config.HU_TAO_ACTIVITIES["Neutral"])

    # Choose a random activity from the list
    current_activity = random.choice(activities)

    # Record the time the activity started
    activity_start_time = asyncio.get_event_loop().time()

    print(f"Activity chosen: {current_activity}")
    return current_activity, activity_start_time

def get_activity_status():
    """
    Checks if the current activity is still ongoing and generates a descriptive status string.

    Returns:
        A string describing the current activity status.
        Returns a default message if no activity has been chosen yet.
    """
    global current_activity, activity_start_time

    # Check if an activity has been initialized
    if current_activity is None or activity_start_time is None:
        # If no activity is set, choose one and report starting it
        # Pass a default emotion, or get the current emotion from the emotion module if needed
        # For simplicity, let's assume choose_activity might be called elsewhere first.
        # If called here, it needs an emotion. Let's default to Neutral if status is checked before any activity is set.
        # A better approach: ensure activity is chosen during application startup.
        # If this function is called when current_activity is None, it implies an issue or initial check.
        # Let's return a neutral status in this specific case.
         return "Hmm? I wasn't really doing anything at the moment."


    elapsed_time = asyncio.get_event_loop().time() - activity_start_time
    duration = config.ACTIVITY_DURATION

    # Check if the activity is finished
    if elapsed_time >= duration:
        # Note: This function only *reports* that the activity is finished.
        # A separate call to `choose_activity` is needed elsewhere (e.g., in the idle loop
        # or message processing) to actually select a *new* activity.
        return f"Oh, I've just finished {current_activity}."
    else:
        # Activity is still ongoing
        remaining_time = duration - elapsed_time
        return f"Currently, I'm deeply engaged in {current_activity}. It'll take about {int(remaining_time)} more seconds."

# You might add other functions here later, like:
# - Loading/saving activity state from the database
# - Explicitly setting the activity state
# - Interrupting an activity