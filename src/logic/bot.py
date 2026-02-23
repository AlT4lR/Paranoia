import asyncio, os, time
from src.soul.brain import IntentBrain
from src.soul.consciousness import HuTaoSoul
from src.soul.web_miner import SpiritSearcher
from src.soul.news_miner import NewsMiner
from src.utils.compiler import SoulCompiler
from src.database import save_chat_session, get_chat_session, get_all_facts
from src.utils.logger import SoulLogger
from src import config
from src.logic import dynamic 

# Single instances for global state
brain = IntentBrain()
soul = HuTaoSoul()
searcher = SpiritSearcher()
compiler = SoulCompiler()

# MERGED: Using the specific active API Key provided
news_miner = NewsMiner(api_key="1f3284f3c5cd4781ba75a20e6e421c73") 

# --- State Tracking ---
intent_failures = []  # Tracks messages for future meditation/synthesis
last_interaction_time = time.time()
processing_lock = asyncio.Lock()
last_user_message = ""

async def get_proactive_message(user_id):
    """
    NEW: Generates a message for when Hu Tao gets bored and talks first.
    Integrates the idle thought generation logic.
    """
    user_facts = await get_all_facts(user_id)
    msg, emotion = soul.generate_idle_thought(user_facts)
    return msg, emotion

async def process_user_message(user_message, user_id, gui_updater):
    global last_interaction_time, last_user_message, intent_failures
    
    async with processing_lock:
        last_interaction_time = time.time() # Reset idle timer
        msg_clean = str(user_message).strip()
        msg_lower = msg_clean.lower()
        
        SoulLogger.sys(f"Processing Request: '{msg_clean}'")

        try:
            # 1. SPECIAL COMMANDS (e.g., Web Mining)
            if msg_lower.startswith("!mine "):
                res = await asyncio.to_thread(searcher.mine_url, msg_clean[6:].strip())
                gui_updater.update_avatar("happy")
                gui_updater.update_chat_log(f"Hu Tao: {res}", sender="hutao")
                return

            # 2. AUTONOMOUS MEMORY ENGINE
            # Scans input to see if user shared a personal fact
            await soul.extract_and_save_facts(user_id, msg_clean)

            # 3. INTENT PREDICTION
            intent = brain.predict(msg_clean)
            
            # --- Synthesis Tracking ---
            if intent == "default":
                intent_failures.append(msg_clean)
                if len(intent_failures) > 10: 
                    intent_failures.pop(0)

            # 4. DYNAMIC FEATURE EXECUTION (Power Synthesis)
            if intent == "dynamic_feature":
                for f_key in compiler.registry.keys():
                    trigger = f_key.split("_")[0]
                    if trigger in msg_lower:
                        SoulLogger.sys(f"Running Dynamic Power: {f_key}")
                        res = compiler.execute_feature(f_key)
                        gui_updater.update_avatar("happy")
                        gui_updater.update_chat_log(f"Hu Tao: {res}", sender="hutao")
                        return

            # 5. NORMAL CONVERSATION & THOUGHT GENERATION
            last_user_message = msg_clean
            user_facts = await get_all_facts(user_id)
            
            # generate_thought returns (response, emotion)
            response, emotion = soul.generate_thought(intent, brain.data, user_facts, msg_clean)
            
            # --- THE FIX FOR THE SCREENSHOT/KNOWLEDGE BUG ---
            # If soul returns None, it fails to find a fact; log for meditation
            if response is None:
                intent_failures.append(msg_clean)
                response = "Aiya... I'm not sure about that. Teach me, or let me meditate on it!~"
                emotion = "surprised"

            # 6. GUI UPDATE & HISTORY PERSISTENCE
            gui_updater.update_avatar(emotion)
            gui_updater.update_chat_log(f"Hu Tao: {response}", sender="hutao")
            
            # Save to database history
            _, hist = await get_chat_session(user_id)
            new_history = hist + [f"U: {msg_clean}", f"H: {response}"]
            await save_chat_session(user_id, "soul_chat", new_history)

        except Exception as e:
            SoulLogger.err(f"Bot Logic Error: {e}")
            gui_updater.update_avatar("sad")