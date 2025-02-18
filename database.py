import sqlite3

DATABASE_NAME = "hutao_chat.db"

async def initialize_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            user_id INTEGER PRIMARY KEY,
            chat_id TEXT,
            conversation_history TEXT
        )
    """)
    conn.commit()
    conn.close()


async def save_chat_session(user_id, chat_id, conversation_history):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    # Convert conversation history to a string representation
    history_string = "\n".join(conversation_history)
    cursor.execute("REPLACE INTO chat_sessions (user_id, chat_id, conversation_history) VALUES (?, ?, ?)",
                   (user_id, chat_id, history_string))
    conn.commit()
    conn.close()


async def get_chat_session(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id, conversation_history FROM chat_sessions WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        chat_id, history_string = result
        # Split the history string back into a list
        conversation_history = history_string.split("\n")
        return chat_id, conversation_history
    else:
        return None, []