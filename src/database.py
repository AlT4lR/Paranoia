# src/database.py

import sqlite3
import asyncio
import json # Use json for robust history storage instead of newline joins

# Import database name from config
from src import config

# Database connection function (synchronous)
# This function will be run in a separate thread
def _connect_db():
    """Synchronous function to establish a database connection."""
    return sqlite3.connect(config.DATABASE_NAME)

# Initialize database table (synchronous)
# This function will be run in a separate thread
def _initialize_db_sync():
    """Synchronous function to create the chat_sessions table."""
    conn = None
    try:
        conn = _connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                user_id INTEGER PRIMARY KEY,
                chat_id TEXT,
                conversation_history TEXT -- Storing history as a JSON string
            )
        """)
        conn.commit()
    except Exception as e:
        print(f"Error initializing database synchronously: {e}")
        # Depending on severity, you might want to reraise or handle differently
    finally:
        if conn:
            conn.close()


# Asynchronous wrapper for database initialization
async def initialize_db():
    """
    Initializes the database table asynchronously by running the synchronous
    initialization in a separate thread.
    """
    print(f"Initializing database: {config.DATABASE_NAME}")
    await asyncio.to_thread(_initialize_db_sync)
    print("Database initialization complete.")


# Save chat session (synchronous part)
def _save_chat_session_sync(user_id: int, chat_id: str, conversation_history: list):
    """Synchronous function to save a chat session."""
    conn = None
    try:
        conn = _connect_db()
        cursor = conn.cursor()
        # Convert conversation history list to a JSON string
        # Using json is more robust than joining with newline, especially if messages contain newlines
        history_string = json.dumps(conversation_history)

        cursor.execute("REPLACE INTO chat_sessions (user_id, chat_id, conversation_history) VALUES (?, ?, ?)",
                       (user_id, chat_id, history_string))
        conn.commit()
    except Exception as e:
        print(f"Error saving chat session synchronously: {e}")
    finally:
        if conn:
            conn.close()


# Asynchronous wrapper for saving chat session
async def save_chat_session(user_id: int, chat_id: str, conversation_history: list):
    """
    Saves the chat session asynchronously by running the synchronous save
    in a separate thread.

    Args:
        user_id: The ID of the user.
        chat_id: The CharacterAI chat ID for this session.
        conversation_history: A list of strings representing the conversation history.
    """
    print(f"Saving session for user {user_id}, chat {chat_id}")
    await asyncio.to_thread(_save_chat_session_sync, user_id, chat_id, conversation_history)
    print(f"Session saved for user {user_id}.")


# Get chat session (synchronous part)
def _get_chat_session_sync(user_id: int):
    """Synchronous function to retrieve a chat session."""
    conn = None
    result = None
    try:
        conn = _connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id, conversation_history FROM chat_sessions WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
    except Exception as e:
         print(f"Error getting chat session synchronously: {e}")
    finally:
        if conn:
            conn.close()

    return result


# Asynchronous wrapper for getting chat session
async def get_chat_session(user_id: int) -> tuple[str | None, list]:
    """
    Retrieves the chat session for a user asynchronously by running the
    synchronous retrieval in a separate thread.

    Args:
        user_id: The ID of the user.

    Returns:
        A tuple containing the chat_id (str or None) and the conversation_history (list of strings).
        Returns (None, []) if no session is found for the user_id.
    """
    print(f"Getting session for user {user_id}")
    result = await asyncio.to_thread(_get_chat_session_sync, user_id)

    if result:
        chat_id, history_string = result
        try:
            # Convert the JSON string back into a list
            conversation_history = json.loads(history_string)
            print(f"Session found for user {user_id}. History length: {len(conversation_history)}")
        except (json.JSONDecodeError, TypeError):
             print(f"Warning: Could not decode conversation history for user {user_id}. Starting fresh.")
             conversation_history = [] # Start fresh if history is corrupted or not JSON

        return chat_id, conversation_history
    else:
        print(f"No session found for user {user_id}.")
        return None, [] # Return None for chat_id and an empty list for history if no session