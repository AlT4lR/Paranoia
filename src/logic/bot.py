import asyncio
import time  # For tracking idle states
import os
import re
from src.soul.brain import IntentBrain
from src.soul.consciousness import HuTaoSoul
from src.soul.web_miner import SpiritSearcher
from src.soul.news_miner import NewsMiner 
from src.utils.compiler import SoulCompiler
from src.database import save_chat_session, get_chat_session, save_fact, get_all_facts
from src.utils.logger import SoulLogger
from src import config

# Initialize components
brain = IntentBrain()
soul = HuTaoSoul()
searcher = SpiritSearcher()
compiler = SoulCompiler()
# REPLACE WITH YOUR ACTUAL KEY
news_miner = NewsMiner(api_key="YOUR_NEWS_API_KEY") 

last_user_message = ""
last_interaction_time = time.time() # Tracks idle state for meditation logic

async def process_user_message(user_message, user_id, gui_updater):
    global last_user_message, last_interaction_time
    
    # Reset idle timer as soon as a message is received
    last_interaction_time = time.time() 
    
    msg_clean = user_message.strip()
    msg_lower = msg_clean.lower()
    
    SoulLogger.sys(f"Processing Request: '{msg_clean}'")

    # --- 1. COMMAND: NEWS (Highest Priority) ---
    if msg_lower.startswith("!news"):
        SoulLogger.sys("Command Detected: !news")
        gui_updater.update_chat_log("Hu Tao: Let me listen to the whispers of the world for a second...", sender="hutao")
        
        result = await asyncio.to_thread(news_miner.gather_gossip)
        gui_updater.update_chat_log(f"Hu Tao: {result}", sender="hutao")
        return

    # --- 2. COMMAND: DEEP MINE ---
    if msg_lower.startswith("!mine "):
        url = msg_clean[6:].strip() 
        SoulLogger.sys(f"Command Detected: !mine | Target: {url}")
        gui_updater.update_chat_log(f"Hu Tao: Oho? A new source of info? Looking at {url}...", sender="hutao")
        
        result = await asyncio.to_thread(searcher.mine_url, url)
        gui_updater.update_chat_log(f"Hu Tao: {result}", sender="hutao")
        return 

    # --- 3. COMMAND: WEB SEARCH ---
    if "!search" in msg_lower or "go search the internet" in msg_lower:
        SoulLogger.sys("Command Detected: !search")
        gui_updater.update_chat_log("Hu Tao: Shh... I'm listening to the whispers of the world...", sender="hutao")
        
        result = await asyncio.to_thread(searcher.hunt_for_knowledge) 
        gui_updater.update_chat_log(f"Hu Tao: {result}", sender="hutao")
        return 

    # --- 4. COMMAND: TEACH ---
    if msg_lower.startswith("!teach "):
        if not last_user_message:
            gui_updater.update_chat_log("Hu Tao: I need to hear you say something first before I can learn!", sender="hutao")
            return
        new_intent = msg_clean[7:].strip()
        brain.teach(last_user_message, new_intent) 
        SoulLogger.brain(f"Manual Lesson: '{last_user_message}' -> '{new_intent}'")
        gui_updater.update_chat_log("Hu Tao: Aiya! My brain just got a little bigger~", sender="hutao")
        return 

    # --- 5. NORMAL BRAIN PROCESSING ---
    last_user_message = msg_clean
    intent = brain.predict(msg_clean)
    SoulLogger.brain(f"Brain Prediction: '{msg_clean}' -> Intent: '{intent}'")
    
    # Fetch user-specific facts (name, preferences, etc.)
    try:
        user_facts = await get_all_facts(user_id)
    except Exception as e:
        SoulLogger.err(f"Fact Retrieval Error: {e}")
        user_facts = {}

    # UPDATED: Generate response using intent, brain data, user facts, AND raw message context
    response = soul.generate_thought(intent, brain.data, user_facts, msg_clean)
    SoulLogger.soul(f"Thought generated via Intent: {intent}")
    
    gui_updater.update_chat_log(f"Hu Tao: {response}", sender="hutao")

    # --- 6. DATABASE PERSISTENCE ---
    try:
        _, conversation_history = await get_chat_session(user_id)
        history = conversation_history if conversation_history else []
        updated_history = history + [f"User: {msg_clean}", f"Hu Tao: {response}"]
        await save_chat_session(user_id, "soul_chat", updated_history)
    except Exception as e:
        SoulLogger.err(f"Database Error: {e}")