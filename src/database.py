# src/database.py
import sqlite3
import asyncio
import json
from src import config

def _connect_db():
    return sqlite3.connect(config.DATABASE_NAME)

def _initialize_db_sync():
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
        # Table for persistent user facts (Memory)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                user_id INTEGER,
                fact_key TEXT,
                fact_value TEXT,
                PRIMARY KEY (user_id, fact_key)
            )
        """)
        # Table for character state (Emotions/Activities)
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
        print(f"Error initializing database: {e}")
    finally:
        if conn: conn.close()

async def initialize_db():
    await asyncio.to_thread(_initialize_db_sync)

async def save_fact(user_id: int, fact_key: str, fact_value: str):
    def _sync(u_id, f_key, f_val):
        conn = _connect_db()
        try:
            cursor = conn.cursor()
            cursor.execute("REPLACE INTO facts (user_id, fact_key, fact_value) VALUES (?, ?, ?)",
                           (u_id, f_key.lower(), f_val))
            conn.commit()
        finally:
            conn.close()
    await asyncio.to_thread(_sync, user_id, fact_key, fact_value)

async def get_all_facts(user_id: int) -> dict:
    def _sync(u_id):
        conn = _connect_db()
        facts = {}
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT fact_key, fact_value FROM facts WHERE user_id = ?", (u_id,))
            for row in cursor.fetchall():
                facts[row[0]] = row[1]
            return facts
        finally:
            conn.close()
    return await asyncio.to_thread(_sync, user_id)

async def save_character_state(user_id: int, state_data: dict):
    def _sync(u_id, s_data):
        conn = _connect_db()
        try:
            cursor = conn.cursor()
            for key, value in s_data.items():
                cursor.execute("REPLACE INTO character_state (user_id, state_key, state_value) VALUES (?, ?, ?)",
                               (u_id, key, str(value)))
            conn.commit()
        finally:
            conn.close()
    await asyncio.to_thread(_sync, user_id, state_data)

async def load_character_state(user_id: int) -> dict:
    def _sync(u_id):
        conn = _connect_db()
        state = {}
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT state_key, state_value FROM character_state WHERE user_id = ?", (u_id,))
            for row in cursor.fetchall():
                state[row[0]] = row[1]
            return state
        finally:
            conn.close()
    return await asyncio.to_thread(_sync, user_id)

async def save_chat_session(user_id, chat_id, history):
    def _sync(u_id, c_id, hist):
        conn = _connect_db()
        try:
            cursor = conn.cursor()
            cursor.execute("REPLACE INTO chat_sessions (user_id, chat_id, conversation_history) VALUES (?, ?, ?)",
                           (u_id, c_id, json.dumps(hist)))
            conn.commit()
        finally:
            conn.close()
    await asyncio.to_thread(_sync, user_id, chat_id, history)

async def get_chat_session(user_id):
    def _sync(u_id):
        conn = _connect_db()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT chat_id, conversation_history FROM chat_sessions WHERE user_id = ?", (u_id,))
            return cursor.fetchone()
        finally:
            conn.close()
    res = await asyncio.to_thread(_sync, user_id)
    return (res[0], json.loads(res[1])) if res else (None, [])