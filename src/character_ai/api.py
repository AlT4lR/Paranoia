# src/character_ai/api.py

import asyncio
from characterai import aiocai
import datetime # Needed for context in prompt
import random # Needed for idle prompt logic

# Import configuration constants
from src import config

# --- CharacterAI Client Management ---

async def initialize_client(api_key: str):
    """
    Initializes and connects the CharacterAI client.

    Args:
        api_key: Your CharacterAI API key.

    Returns:
        The connected aiocai.Client instance.

    Raises:
        Exception: If client initialization or connection fails.
    """
    print("Connecting to CharacterAI client...")
    try:
        # Using the async context manager pattern if the library supports it is cleaner
        # async with aiocai.Client(api_key) as client: ...
        # But for a long-running app, initializing once and passing the client is common.
        client = aiocai.Client(api_key)
        # Getting self might be a good initial connection test
        # await client.get_me() # This can raise exceptions on failure if connection fails
        print("CharacterAI client initialized.")
        return client
    except Exception as e:
        print(f"Error initializing CharacterAI client: {e}")
        raise # Re-raise the exception so main.py can handle the failure

async def shutdown_client(client):
    """
    Shuts down the CharacterAI client connection.

    Args:
        client: The aiocai.Client instance to shut down.
    """
    # Check if client is not None and has a close method before trying
    if client and hasattr(client, 'close') and callable(client.close):
        print("Closing CharacterAI client connection...")
        try:
            await client.close()
            print("CharacterAI client closed successfully.")
        except Exception as e:
            print(f"Error closing CharacterAI client: {e}")
    else:
        print("CharacterAI client not initialized or already closed.")


# --- Message Sending and Prompt Construction ---

async def send_message(client: aiocai.Client, char_id: str, user_id: int, chat_id: str | None, user_message: str, conversation_history: list[str], user_name: str, default_user_name: str, user_affection: int, activity_status: str) -> tuple[str, str]:
    """
    Sends a message to the CharacterAI character and gets the response.
    Handles getting or creating the chat session using the CharacterAI client object.

    Args:
        client: The connected CharacterAI client instance.
        char_id: The ID of the character to interact with.
        user_id: The ID of the user (for session management, though CAI uses its own).
        chat_id: The existing chat ID (from database) or None if starting new.
        user_message: The message from the user.
        conversation_history: The list of previous conversation turns. <-- Pass this!
        user_name: The user's preferred name in the conversation.
        default_user_name: The default name for the user.
        user_affection: The current affection level (for tone).
        activity_status: The character's current background activity status.

    Returns:
        A tuple containing:
        - The response text from the character (str).
        - The chat_id of the conversation session (str - the ID used/created).

    Raises:
        Exception: If the API call fails.
    """
    print(f"Attempting to send message to character {char_id} for user {user_id}, chat {chat_id}")
    try:
        # --- AWAIT client.get_char() ---
        char = await client.get_char(char_id) # Added await here!

        if chat_id:
            chat = await char.fetch_chat(chat_id)
            print(f"Fetched existing chat session: {chat_id}")
        else:
            chat = await char.create_chat()
            print(f"Created new chat session: {chat.chat_id}")
            chat_id = chat.chat_id # Update chat_id for saving later if needed


        # --- Prompt Construction ---
        now = datetime.datetime.now()
        current_time_str = now.strftime("%H:%M")
        current_date_str = now.strftime("%Y-%m-%d")
        context = f"The current time is {current_time_str} on {current_date_str}. "

        if user_affection > 75:
            tone = "Warm, playful, and slightly flirtatious"
        elif user_affection < 25:
            tone = "Slightly distant, teasing, and subtly morbid"
        else:
            tone = "Playful, mischievous, and generally cheerful"

        full_prompt_text = f"""You are Hu Tao, the 77th Director of the Wangsheng Funeral Parlor.
        Your **primary** goal is to directly respond to {user_name}'s message in a meaningful and relevant way. Do not ignore the user.
        Do not introduce unrelated topics unless they are very closely tied to Wangsheng Funeral Parlor or death.
        Maintain your personality and the tone of {tone} given your affection level towards {user_name}, which is {user_affection} out of 100.

        **Be concise and avoid excessive tangents or overly long responses.** Keep the conversation focused.

        Remember to have a good time and never break character. Always try to bring it back to funeral and death,
        always make a dark joke with the user if there's opening.

        {activity_status}

        Previous conversation:
        {"\n".join(conversation_history)} # Still include history in the prompt text

        {user_name}: {user_message}
        Hu Tao: """

        print("Sending prompt text to CAI API...")
        # --- Corrected API Call ---
        # Pass the prompt text AND the conversation history list as positional arguments.
        response_obj = await chat.send_message(full_prompt_text, conversation_history)


        response_text = response_obj.text
        final_chat_id = chat.chat_id

        print(f"Received response from CAI (chat {final_chat_id}): {response_text[:100]}...")
        return response_text, final_chat_id

    except Exception as e:
        print(f"Error sending message to CharacterAI: {e}")
        raise


async def generate_idle_message(client: aiocai.Client, char_id: str, user_id: int, chat_id: str | None, conversation_history: list[str], user_name: str, activity_status: str, user_affection: int, hu_tao_topics: list[str]) -> tuple[str, str]:
    """
    Generates an idle response from the CharacterAI character.
    Handles getting or creating the chat session.

    Args:
        client: The connected CharacterAI client instance.
        char_id: The ID of the character.
        user_id: The ID of the user.
        chat_id: The current chat_id (str or None).
        conversation_history: The list of previous conversation turns. <-- Pass this!
        user_name: The user's name.
        activity_status: The character's current background activity status.
        user_affection: The current affection level.
        hu_tao_topics: The list of possible conversation topics from config.

    Returns:
        A tuple containing:
        - The generated idle response text (str).
        - The chat_id of the conversation session (str - the ID used/created).

    Raises:
        Exception: If the API call fails.
    """
    print(f"Attempting to generate idle message for user {user_id}, chat {chat_id}")
    try:
        # --- AWAIT client.get_char() ---
        char = await client.get_char(char_id) # Added await here!

        if chat_id:
            chat = await char.fetch_chat(chat_id)
            print(f"Fetched existing chat session for idle: {chat_id}")
        else:
            chat = await char.create_chat()
            print(f"Created new chat session for idle: {chat.chat_id}")
            chat_id = chat.chat_id


        if user_affection > 75:
            tone = "Warm, playful, and slightly flirtatious"
        elif user_affection < 25:
            tone = "Slightly distant, teasing, and subtly morbid"
        else:
            tone = "Playful, mischievous, and generally cheerful"

        now = datetime.datetime.now()
        current_time_str = now.strftime("%H:%M")
        current_date_str = now.strftime("%Y-%m-%d")
        context = f"The current time is {current_time_str} on {current_date_str}. "

        # Prompt logic from your original code
        if random.random() < 0.6:
            topic = random.choice(hu_tao_topics)
            idle_prompt_text = f"""{context}You are Hu Tao. The user is idle. {activity_status}. **Briefly** re-engage them by playfully suggesting the topic: {topic} in a dark humor way, but **ONLY IF IT RELATES TO THE LAST TOPIC DISCUSSED, or something the USER said**.  Otherwise, simply greet them and ask if they have any further inquiries about Wangsheng Funeral Parlor. Don't ask if they need help or are there. Be conversational not creepy. Keep it short.
            Hu Tao's current affection level towards {user_name} is {user_affection} out of 100.
            Previous conversation:
            {"\n".join(conversation_history[-5:])}
            Hu Tao: """

        else:
            idle_prompt_text = f"""{context}You are Hu Tao. The user is idle. Re-engage them.  **Be conversational not creepy, and keep to your role.** Briefly mention your current activity, which is {activity_status}. then **immediately ask if they have any questions related to your work or the Parlor.** Do not drift off-topic.
            Hu Tao's current affection level towards {user_name} is {user_affection} out of 100.
            Previous conversation:
            {"\n".join(conversation_history[-5:])}
            Hu Tao: """

        print("Sending idle prompt text to CAI API...")
        # --- Corrected API Call ---
        # Pass the prompt text AND the conversation history list as positional arguments.
        response_obj = await chat.send_message(idle_prompt_text, conversation_history)


        response_text = response_obj.text
        final_chat_id = chat.chat_id

        print(f"Generated idle response (chat {final_chat_id}): {response_text[:100]}...")
        return response_text, final_chat_id

    except Exception as e:
        print(f"Error generating idle response from CharacterAI: {e}")
        raise