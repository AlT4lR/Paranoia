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

# Single instances for global state management
brain = IntentBrain()
soul = HuTaoSoul()
searcher = SpiritSearcher()
compiler = SoulCompiler()

# NEWS_MINER integrated with the provided active API key
news_miner = NewsMiner(api_key="1f3284f3c5cd4781ba75a20e6e421c73") 

# --- State Tracking ---
intent_failures = []       # Tracks messages that Hu Tao couldn't answer for future synthesis
last_interaction_time = time.time()
processing_lock = asyncio.Lock()
last_user_message = ""

async def get_proactive_message(user_id):
    """Safely attempts to generate an idle thought for when the bot speaks first."""
    try:
        user_facts = await get_all_facts(user_id)
        if hasattr(soul, 'generate_idle_thought'):
            return soul.generate_idle_thought(user_facts)
        else:
            return "Aiya! I forgot what I was going to say...", "surprised"
    except Exception as e:
        SoulLogger.err(f"Proactive Generation Error: {e}")
        return "The spirits are being quiet today...", "default"

async def process_user_message(user_message, user_id, gui_updater):
    """
    The main pipeline that moves from User Input -> Intent -> Soul -> GUI.
    """
    global last_interaction_time, last_user_message, intent_failures
    
    async with processing_lock:
        last_interaction_time = time.time() 
        msg_clean = str(user_message).strip()
        msg_lower = msg_clean.lower()
        
        SoulLogger.sys(f"Processing Request: '{msg_clean}'")

        try:
            # 1. SPECIAL COMMANDS (e.g., !mine URL)
            if msg_lower.startswith("!mine "):
                target_url = msg_clean[6:].strip()
                gui_updater.update_chat_log("Hu Tao: Let me check the spiritual records for that... one moment!~", sender="hutao")
                res = await asyncio.to_thread(searcher.mine_url, target_url)
                emotion = "happy" if "Success" in res else "surprised"
                gui_updater.update_avatar(emotion)
                gui_updater.update_chat_log(f"Hu Tao: {res}", sender="hutao")
                return

            # 2. AUTONOMOUS MEMORY ENGINE
            await soul.extract_and_save_facts(user_id, msg_clean)

            # 3. INTENT PREDICTION
            intent = brain.predict(msg_clean)
            
            # Record failures for later "Meditation" (Synthesis)
            if intent == "default":
                intent_failures.append(msg_clean)
                if len(intent_failures) > 10: intent_failures.pop(0)

            # 4. DYNAMIC FEATURE EXECUTION
            if intent == "dynamic_feature":
                for f_key in compiler.registry.keys():
                    trigger = f_key.split("_")[0]
                    if trigger in msg_lower:
                        SoulLogger.sys(f"Running Dynamic Power: {f_key}")
                        res = compiler.execute_feature(f_key)
                        gui_updater.update_avatar("happy")
                        gui_updater.update_chat_log(f"Hu Tao: {res}", sender="hutao")
                        return

            # --- 4.5 GOSSIP / NEWS TRIGGER ---
            # Triggers if the brain predicts "gossip" OR keywords are found
            if intent == "gossip" or "gossip" in msg_lower or "news" in msg_lower:
                gui_updater.update_chat_log("Hu Tao: One second... let me check the headlines...", sender="hutao")
                
                # Call the miner in a thread to prevent GUI freezing
                report, raw_articles = await asyncio.to_thread(news_miner.gather_gossip)
                
                # Double-persist the news as knowledge for long-term memory
                if raw_articles:
                    filename = os.path.join(config.KNOWLEDGE_DIR, "live_news.txt")
                    with open(filename, "a", encoding="utf-8") as f:
                        for art in raw_articles:
                            # Added newline for cleaner file structure
                            f.write(f"I heard that {art}:knowledge\n")

                gui_updater.update_avatar("happy")
                gui_updater.update_chat_log(f"Hu Tao: {report}", sender="hutao")
                return

            # 5. NORMAL CONVERSATION & THOUGHT GENERATION
            last_user_message = msg_clean
            user_facts = await get_all_facts(user_id)
            
            response, emotion = soul.generate_thought(intent, brain.data, user_facts, msg_clean)
            
            # Knowledge fallback
            if response is None:
                intent_failures.append(msg_clean)
                response = "Aiya... I'm not sure about that. Teach me, or let me meditate on it!~"
                emotion = "surprised"

            # 6. GUI UPDATE & HISTORY PERSISTENCE
            gui_updater.update_avatar(emotion)
            gui_updater.update_chat_log(f"Hu Tao: {response}", sender="hutao")
            
            # Persist to DB
            _, hist = await get_chat_session(user_id)
            new_history = hist + [f"U: {msg_clean}", f"H: {response}"]
            await save_chat_session(user_id, "soul_chat", new_history)

        except Exception as e:
            SoulLogger.err(f"Bot Logic Error: {e}")
            gui_updater.update_avatar("sad")
            gui_updater.update_chat_log("Aiya! My head hurts... even spirits get headaches sometimes!", sender="hutao")