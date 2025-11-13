# src/database.py

import sqlite3
import asyncio
import json
from src import config

def _connect_db():
    """Synchronous function to establish a database connection."""
    return sqlite3.connect(config.DATABASE_NAME)

def _initialize_db_sync():
    """Synchronous function to create all required tables."""
    conn = None
    try:
        conn = _connect_db()
        cursor = conn.cursor()
        # Table for conversation history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                user_id INTEGER PRIMARY KEY,
                chat_id TEXT,
                conversation_history TEXT
            )
        """)
        # Table for persistent user facts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                user_id INTEGER,
                fact_key TEXT,
                fact_value TEXT,
                PRIMARY KEY (user_id, fact_key)
            )
        """)
        # ## NEW ##: Table for storing the character's own state
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS character_state (
                user_id INTEGER,
                state_key TEXT,
                state_value TEXT,
                PRIMARY KEY (user_id, state_key)
            )
        """)
        conn.commit()
    except Exception as e:
        print(f"Error initializing database synchronously: {e}")
    finally:
        if conn:
            conn.close()

async def initialize_db():
    """Initializes the database tables asynchronously."""
    await asyncio.to_thread(_initialize_db_sync)

# --- Conversation History Functions ---
async def save_chat_session(user_id: int, chat_id: str, conversation_history: list):
    # ... (This function remains the same as before)
    def _sync(user_id, chat_id, conversation_history):
        conn = _connect_db()
        try:
            cursor = conn.cursor()
            history_string = json.dumps(conversation_history)
            cursor.execute("REPLACE INTO chat_sessions (user_id, chat_id, conversation_history) VALUES (?, ?, ?)",
                           (user_id, chat_id, history_string))
            conn.commit()
        finally:
            conn.close()
    await asyncio.to_thread(_sync, user_id, chat_id, conversation_history)

async def get_chat_session(user_id: int) -> tuple[str | None, list]:
    # ... (This function remains the same as before)
    def _sync(user_id):
        conn = _connect_db()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT chat_id, conversation_history FROM chat_sessions WHERE user_id = ?", (user_id,))
            return cursor.fetchone()
        finally:
            conn.close()
    result = await asyncio.to_thread(_sync, user_id)
    if result:
        chat_id, history_string = result
        try:
            return chat_id, json.loads(history_string)
        except (json.JSONDecodeError, TypeError):
            return chat_id, []
    return None, []

# --- User Fact Functions ---
async def save_fact(user_id: int, fact_key: str, fact_value: str):
    # ... (This function remains the same as before)
    def _sync(user_id, fact_key, fact_value):
        conn = _connect_db()
        try:
            cursor = conn.cursor()
            cursor.execute("REPLACE INTO facts (user_id, fact_key, fact_value) VALUES (?, ?, ?)",
                           (user_id, fact_key, fact_value))
            conn.commit()
            print(f"Memory saved: User {user_id} -> {fact_key} = {fact_value}")
        finally:
            conn.close()
    await asyncio.to_thread(_sync, user_id, fact_key, fact_value)

async def get_all_facts(user_id: int) -> dict:
    # ... (This function remains the same as before)
    def _sync(user_id):
        conn = _connect_db()
        facts = {}
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT fact_key, fact_value FROM facts WHERE user_id = ?", (user_id,))
            for row in cursor.fetchall():
                facts[row[0]] = row[1]
            return facts
        finally:
            conn.close()
    return await asyncio.to_thread(_sync, user_id)

# --- ## NEW ##: Character State Functions ---
async def save_character_state(user_id: int, state_data: dict):
    """Asynchronously saves key-value pairs of the character's state."""
    def _sync(user_id, state_data):
        conn = _connect_db()
        try:
            cursor = conn.cursor()
            for key, value in state_data.items():
                cursor.execute("REPLACE INTO character_state (user_id, state_key, state_value) VALUES (?, ?, ?)",
                               (user_id, key, str(value)))
            conn.commit()
            print(f"Character state saved for user {user_id}: {state_data}")
        finally:
            conn.close()
    await asyncio.to_thread(_sync, user_id, state_data)

async def load_character_state(user_id: int) -> dict:
    """Asynchronously loads all character state for a user."""
    def _sync(user_id):
        conn = _connect_db()
        state = {}
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT state_key, state_value FROM character_state WHERE user_id = ?", (user_id,))
            for row in cursor.fetchall():
                state[row[0]] = row[1]
            return state
        finally:
            conn.close()
    return await asyncio.to_thread(_sync, user_id)