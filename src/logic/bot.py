import asyncio
import os
import re
from src.soul.brain import IntentBrain
from src.soul.consciousness import HuTaoSoul
from src.soul.web_miner import SpiritSearcher
from src.utils.compiler import SoulCompiler  # New Import
from src.database import save_chat_session, get_chat_session, save_fact
from src import config

# Initialize global brain, soul, searcher, and compiler objects
brain = IntentBrain()
soul = HuTaoSoul()
searcher = SpiritSearcher()
compiler = SoulCompiler() # New Instance

# Keep track of the last message received for the "!teach" command
last_user_message = ""

async def process_user_message(user_message, user_id, gui_updater):
    global last_user_message
    
    # --- 1. TEACHER COMMAND HANDLING ---
    if user_message.startswith("!teach "):
        if not last_user_message:
            gui_updater.update_chat_log("Hu Tao: Aiya! I don't have anything to learn yet.", sender="hutao")
            return

        new_intent = user_message.replace("!teach ", "").strip()
        brain.teach(last_user_message, new_intent) 
        gui_updater.update_chat_log(f"Hu Tao: Ooh, so '{last_user_message}' means {new_intent}? I've written that into my soul memory~", sender="hutao")
        return

    # --- 2. SELF-UPGRADE / COMPILER LOGIC ---
    if "integrate" in user_message.lower() or "add feature" in user_message.lower():
        gui_updater.update_chat_log("Hu Tao: Aiya! Time for a soul-upgrade. Let me compile this...", sender="hutao")
        
        # Internal Logic: Feature Definition
        feature_name = "math_expert"
        code = """
def calculate(a, b):
    return f'The result of your spirit-math is {a + b}!'
"""
        # Attempt to compile the new soul-feature
        success, result = compiler.compile_and_run(feature_name, code)
        
        if success:
            gui_updater.update_chat_log(f"Hu Tao: {result}", sender="hutao")
            # Test run the newly integrated feature
            output = compiler.execute_feature("math_expert_calculate", 10, 20)
            gui_updater.update_chat_log(f"Hu Tao: Test run successful! {output}", sender="hutao")
        else:
            gui_updater.update_chat_log(f"Hu Tao: Aiya, a bug in the spiritual circuits! Let me fix that...", sender="hutao")
        return

    # --- 3. AUTO NAME MEMORY (Regex) ---
    name_match = re.search(r"(?:i am|my name is|call me)\s+([a-zA-Z]+)", user_message.lower())
    if name_match:
        user_name = name_match.group(1).capitalize()
        await save_fact(user_id, "user_name", user_name)
        gui_updater.update_chat_log(f"Hu Tao: Aiya! So your name is {user_name}? I've carved it into my memory!", sender="hutao")
        last_user_message = user_message
        return

    # --- 4. WEB MINING / SEARCH LOGIC ---
    if "!search" in user_message.lower() or "go search the internet" in user_message.lower():
        gui_updater.update_chat_log("Hu Tao: Give me a moment... the spirits are far away...", sender="hutao")
        result = await asyncio.to_thread(searcher.hunt_for_knowledge) 
        gui_updater.update_chat_log(f"Hu Tao: {result}", sender="hutao")
        return

    # --- 5. NORMAL PROCESSING ---
    last_user_message = user_message
    intent = brain.predict(user_message)
    response = soul.generate_thought(intent)
    
    gui_updater.update_chat_log(f"Hu Tao: {response}", sender="hutao")

    # --- 6. DATABASE PERSISTENCE ---
    try:
        _, conversation_history = await get_chat_session(user_id)
        updated_history = conversation_history + [
            f"{config.DEFAULT_USER_NAME}: {user_message}", 
            f"Hu Tao: {response}"
        ]
        await save_chat_session(user_id, "soul_chat", updated_history)
    except Exception as e:
        print(f"Database error: {e}")

async def generate_idle_response(user_id, gui_updater):
    """Generates a proactive message if the user is silent for too long."""
    response = "Aiya... are you daydreaming about coffins again? Or did a ghost steal your tongue?"
    gui_updater.update_chat_log(f"Hu Tao: {response}", sender="hutao")
    
    try:
        _, history = await get_chat_session(user_id)
        await save_chat_session(user_id, "soul_chat", history + [f"Hu Tao: {response}"])
    except Exception as e:
        print(f"Idle log error: {e}")