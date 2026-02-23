# src/logic/bot.py
import asyncio, os, re, time
from src.soul.brain import IntentBrain
from src.soul.consciousness import HuTaoSoul
from src.soul.web_miner import SpiritSearcher
from src.soul.news_miner import NewsMiner
from src.utils.compiler import SoulCompiler
from src.database import save_chat_session, get_chat_session, get_all_facts
from src.utils.logger import SoulLogger
from src import config

brain = IntentBrain()
soul = HuTaoSoul()
searcher = SpiritSearcher()
compiler = SoulCompiler()
news_miner = NewsMiner(api_key="YOUR_KEY") 
last_interaction_time = time.time()
processing_lock = asyncio.Lock()

async def process_user_message(user_message, user_id, gui_updater):
    global last_interaction_time
    async with processing_lock:
        last_interaction_time = time.time()
        msg_clean = str(user_message).strip()
        msg_lower = msg_clean.lower()
        SoulLogger.sys(f"Request: {msg_clean}")

        try:
            # 1. SPECIAL COMMANDS
            if msg_lower == "!reset brain":
                if os.path.exists(config.BRAIN_MODEL_PATH): os.remove(config.BRAIN_MODEL_PATH)
                # Ensure we reset with AT LEAST 2 classes
                brain.data = list(brain.base_data)
                brain.train()
                gui_updater.update_chat_log("Hu Tao: I've cleared my head! Fresh as a daisy!", sender="hutao")
                return

            if msg_lower.startswith("!teach "):
                raw = msg_clean[7:].strip()
                new_intent = raw.split(":")[-1].strip()
                brain.teach(last_user_message, new_intent)
                gui_updater.update_chat_log(f"Hu Tao: Learned that '{last_user_message}' is '{new_intent}'!", sender="hutao")
                return

            if msg_lower.startswith("!mine "):
                url = msg_clean[6:].strip()
                res = await asyncio.to_thread(searcher.mine_url, url)
                gui_updater.update_chat_log(f"Hu Tao: {res}", sender="hutao")
                return

            if msg_lower.startswith("!news"):
                res = await asyncio.to_thread(news_miner.gather_gossip)
                gui_updater.update_chat_log(f"Hu Tao: {res}", sender="hutao")
                return

            # 2. DYNAMIC FEATURES
            intent = brain.predict(msg_clean)
            if intent == "dynamic_feature":
                for f_key in compiler.registry.keys():
                    if f_key.split("_")[0] in msg_lower:
                        res = compiler.execute_feature(f_key)
                        gui_updater.update_chat_log(f"Hu Tao: {res}", sender="hutao")
                        return

            # 3. NORMAL CONVERSATION
            last_user_message = msg_clean
            user_facts = await get_all_facts(user_id)
            response = soul.generate_thought(intent, brain.data, user_facts, msg_clean)
            gui_updater.update_chat_log(f"Hu Tao: {response}", sender="hutao")

            _, hist = await get_chat_session(user_id)
            await save_chat_session(user_id, "soul_chat", hist + [f"U: {msg_clean}", f"H: {response}"])

        except Exception as e:
            SoulLogger.err(f"Logic Error: {e}")