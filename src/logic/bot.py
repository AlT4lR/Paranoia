# src/logic/bot.py

import asyncio
import random
import datetime

# Import modules from your src package
from src import config
from src.database import get_chat_session, save_chat_session # Need DB interaction
# Need to import the API functions from the character_ai package
from src.character_ai import api as cai_api
# Need logic modules for state management
from src.logic import emotion as logic_emotion
from src.logic import personality as logic_personality
from src.logic import activity as logic_activity # For potential activity interruption

# --- Bot Processing Function ---

async def process_user_message(user_message: str, user_id: int, client, gui_updater):
    """
    Processes a user's message, interacts with the CharacterAI API,
    updates character state, saves the session, and updates the GUI.

    Args:
        user_message: The message received from the user.
        user_id: The ID of the user sending the message.
        client: The initialized CharacterAI client instance.
        gui_updater: An object or module containing GUI update functions
                     (e.g., src.gui.app). Needs methods like update_chat_log,
                     display_conversation, update_emotion_label.
    """
    print(f"Processing message from user {user_id}: {user_message}")

    try:
        # 1. Get current chat session
        chat_id, conversation_history = await get_chat_session(user_id)
        print(f"Loaded session: chat_id={chat_id}, history_length={len(conversation_history)}")

        # If no session exists, this is the first message.
        # The initial welcome message was shown by main.py/app.py.
        # The CAI chat session will be created in cai_api.send_message if chat_id is None.


        # 2. Simulate activity interruption
        # Only show interruption if an activity is actually set
        if random.random() < 0.2 and logic_activity.current_activity is not None:
            # Use the stored activity name directly
            interruption_message = f"Oh, excuse me! I was in the middle of {logic_activity.current_activity} when your message came through!"
            gui_updater.update_chat_log(f"Hu Tao: {interruption_message}", sender="hutao")
            # Adding a small visual delay might be good, but await asyncio.sleep() inside GUI handler is tricky
            # gui_updater might need an async update method, or main loop handles updates based on state changes.
            # For now, just display the message. The actual AI response follows.


        # 3. Analyze conversation for personality traits *before* generating response
        # This helps the bot's response be influenced by recent interactions
        # Use DEFAULT_USER_NAME for history representation passed to personality analysis
        trait_analysis = logic_personality.analyze_conversation_traits(conversation_history + [f"{config.DEFAULT_USER_NAME}: {user_message}"])
        logic_personality.adjust_personality_traits(trait_analysis) # Adjust traits based on analysis


        # 4. Generate response from CharacterAI API
        # The cai_api module handles the actual API call and chat session creation if needed
        print("Calling CharacterAI API...")
        # --- CORRECTED API CALL ARGUMENTS ---
        # Ensure arguments match the signature of cai_api.send_message
        api_response_text, new_chat_id = await cai_api.send_message(
            client=client,
            char_id=config.CHAR_ID,
            user_id=user_id,
            chat_id=chat_id, # Correct positional/keyword argument
            user_message=user_message,
            conversation_history=conversation_history, # Correct positional/keyword argument
            user_name=config.USER_NAME, # Passed as keyword, used in prompt
            default_user_name=config.DEFAULT_USER_NAME, # Passed as keyword, used in prompt context
            user_affection=logic_personality.get_user_affection(), # Get current affection
            activity_status=logic_activity.get_activity_status(), # Get current activity status
            # Note: Sending personality traits in the prompt can influence the AI,
            # but might make the prompt very long. The original code removed this.
            # If you want to include them, pass logic_personality.get_personality_traits()
        )
        print(f"Received API response. New chat_id: {new_chat_id}")

        # Update chat_id if a new session was created by the API call
        if chat_id is None and new_chat_id is not None:
            chat_id = new_chat_id


        # 5. Analyze the API response for emotion and update state
        print("Analyzing emotion from response...")
        response_emotion = logic_emotion.analyze_emotion(api_response_text)
        logic_emotion.set_current_emotion(response_emotion) # Update the module-level state
        gui_updater.update_emotion_label(logic_emotion.get_current_emotion()) # Update GUI

        # 6. Adjust affection based on the response emotion
        logic_personality.adjust_affection_based_on_emotion(response_emotion, config.AFFECTION_CHANGE_AMOUNT)
        print(f"Affection adjusted based on emotion. New affection: {logic_personality.get_user_affection()}")


        # 7. Update conversation history with the API response and save
        print("Updating history and saving session...")
        # Use DEFAULT_USER_NAME for the user message in history storage for consistency
        updated_history = conversation_history + [f"{config.DEFAULT_USER_NAME}: {user_message}", f"Hu Tao: {api_response_text}"]
        await save_chat_session(user_id, chat_id, updated_history)
        print("Session saved.")

        # 8. Update GUI with the Hu Tao response
        gui_updater.update_chat_log(f"Hu Tao: {api_response_text}", sender="hutao")
        # Re-displaying the whole conversation might be necessary if history state is complex,
        # but update_chat_log is usually sufficient for just adding the last message.
        # gui_updater.display_conversation(updated_history, config.USER_NAME, config.DEFAULT_USER_NAME)


    except Exception as e:
        print(f"Error processing message: {e}")
        # Display an error message in the chat log
        gui_updater.update_chat_log(f"Error: {e}", sender="hutao")
        # Potentially show a messagebox for critical errors
        # gui_updater.show_error_message("Bot Error", f"An error occurred while processing your message: {e}")


# --- Function for Handling Idle Responses ---
# This logic was in main.py in the original script's idle loop.
# It's better to place the *generation* logic here, called by main.py's loop.

async def generate_idle_response(user_id: int, client, gui_updater):
    """
    Generates and processes an idle response from the CharacterAI API.

    Args:
        user_id: The ID of the user.
        client: The initialized CharacterAI client instance.
        gui_updater: An object or module containing GUI update functions.
    """
    print(f"Generating idle response for user {user_id}")
    try:
        chat_id, conversation_history = await get_chat_session(user_id)

        # Get relevant state for the prompt
        activity_status = logic_activity.get_activity_status()
        user_affection = logic_personality.get_user_affection()

        # Generate the idle response using the API module
        # The arguments here already match the signature of cai_api.generate_idle_message
        idle_message_text, new_chat_id = await cai_api.generate_idle_message(
            client,
            config.CHAR_ID,
            user_id, # Pass user_id for session handling in API module
            chat_id, # Pass current chat_id (can be None)
            conversation_history, # Pass history for context
            user_name=config.USER_NAME, # Used in prompt
            activity_status=activity_status,
            user_affection=user_affection,
            hu_tao_topics=config.HU_TAO_TOPICS # Pass topics for suggestion
        )

        # Update chat_id if a new session was created
        if chat_id is None and new_chat_id is not None:
             chat_id = new_chat_id

        # Analyze emotion from the idle response
        idle_emotion = logic_emotion.analyze_emotion(idle_message_text)
        logic_emotion.set_current_emotion(idle_emotion) # Update state
        gui_updater.update_emotion_label(logic_emotion.get_current_emotion()) # Update GUI

        # Adjust affection based on idle response emotion
        logic_personality.adjust_affection_based_on_emotion(idle_emotion, config.AFFECTION_CHANGE_AMOUNT)
        print(f"Affection adjusted based on idle response. New affection: {logic_personality.get_user_affection()}")


        # Update history and save
        updated_history = conversation_history + [f"Hu Tao: {idle_message_text}"]
        await save_chat_session(user_id, chat_id, updated_history)
        print("Idle session saved.")

        # Update GUI with the idle response
        gui_updater.update_chat_log(f"Hu Tao: {idle_message_text}", sender="hutao")
        # gui_updater.display_conversation(updated_history, config.USER_NAME, config.DEFAULT_USER_NAME)


    except Exception as e:
        print(f"Error generating idle response: {e}")
        # Display an error message in the chat log
        gui_updater.update_chat_log(f"Error generating idle response: {e}", sender="hutao")
        # Potentially show a messagebox for critical errors
        # gui_updater.show_error_message("Bot Error", f"An error occurred during idle response: {e}")


# --- Functions for managing character state if needed ---
# You might add functions here or keep them in their respective modules.
# For now, let's call into the separate modules.