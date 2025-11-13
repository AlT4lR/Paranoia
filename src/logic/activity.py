# src/logic/activity.py

import random
import asyncio
from src import config
from src.database import save_character_state # Import the new database function

# Module-level variables holding the current activity state.
current_activity = None
activity_start_time = None
USER_ID = 1 # Hardcoded for single-user application

def load_activity_state(state_data: dict):
    """
    Loads the activity state from a dictionary (retrieved from the database).
    This is called once on application startup.
    """
    global current_activity, activity_start_time
    current_activity = state_data.get("current_activity")
    start_time_str = state_data.get("activity_start_time")
    if start_time_str:
        activity_start_time = float(start_time_str)
    print(f"Loaded activity state: {current_activity} (started at {activity_start_time})")

async def _save_activity_state():
    """A helper function to save the current activity state to the database."""
    if current_activity is not None and activity_start_time is not None:
        state_to_save = {
            "current_activity": current_activity,
            "activity_start_time": activity_start_time
        }
        await save_character_state(USER_ID, state_to_save)

async def set_activity(new_activity: str):
    """
    Explicitly sets the character's activity, resets the timer, and saves to the database.
    """
    global current_activity, activity_start_time
    current_activity = new_activity
    activity_start_time = asyncio.get_event_loop().time()
    print(f"Activity explicitly set to: {current_activity}")
    await _save_activity_state()

async def choose_activity(current_emotion: str = "Neutral"):
    """Selects a new random activity based on emotion and saves it."""
    activities = config.HU_TAO_ACTIVITIES.get(current_emotion, config.HU_TAO_ACTIVITIES["Neutral"])
    await set_activity(random.choice(activities))

async def interrupt_activity():
    """
    Interrupts the current activity when the user interacts.
    Sets the activity to a special "chatting" state.
    """
    print(f"Activity '{current_activity}' interrupted.")
    await set_activity("Responding to you!")

def get_activity_status() -> str:
    """Checks the status of the current activity."""
    if current_activity is None or activity_start_time is None:
         return "I wasn't really doing anything at the moment."

    elapsed_time = asyncio.get_event_loop().time() - activity_start_time
    duration = config.ACTIVITY_DURATION

    if elapsed_time >= duration and "Responding" not in current_activity:
        return f"Oh, I've just finished {current_activity}."
    else:
        return f"I'm currently engaged in {current_activity}."