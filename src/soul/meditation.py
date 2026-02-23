import os
import asyncio
import time
import random
import re
from src import config
from src.utils.logger import SoulLogger
from src.logic import bot as logic_bot

class SoulMeditation:
    def __init__(self, brain):
        self.brain = brain
        self.knowledge_path = config.KNOWLEDGE_DIR

    async def start_meditating(self):
        """Main loop for background processing and autonomy."""
        SoulLogger.sys("Meditation & Autonomy system online.")
        while True:
            try:
                # 1. ABSORB EXTERNAL KNOWLEDGE FILES
                files = [f for f in os.listdir(self.knowledge_path) if f.endswith(".txt")]
                if files:
                    for filename in files:
                        file_path = os.path.join(self.knowledge_path, filename)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                if ":" in line:
                                    phrase, intent = line.split(":", 1)
                                    self.brain.data.append((phrase.strip().lower(), intent.strip().lower()))
                        
                        self.brain.train()
                        os.remove(file_path)
                        SoulLogger.brain(f"Absorbed: {filename}")

                # 2. CHECK FOR IDLE STATE (Autonomous Actions)
                idle_duration = time.time() - logic_bot.last_interaction_time
                if idle_duration > config.IDLE_TIMEOUT:
                    await self.perform_autonomous_tasks()

            except Exception as e:
                SoulLogger.err(f"Meditation/Autonomy Error: {e}")
            
            # Check every 30 seconds to keep CPU usage low
            await asyncio.sleep(30)

    async def perform_autonomous_tasks(self):
        """Hu Tao's 'Daydreaming' logic: Self-cleaning, patching, and mood shifts."""
        task_roll = random.random()
        
        # TASK 1: KNOWLEDGE SCRUBBING (Cleaning up junk/citations)
        if task_roll < 0.3: 
            SoulLogger.sys("Hu Tao is scrubbing her memory for junk data...")
            cleaned_data = []
            removed_count = 0
            
            for phrase, intent in self.brain.data:
                # Remove citations like [1], (Source), etc.
                clean_phrase = re.sub(r'\[.*?\]|\(.*?\)', '', phrase)
                clean_phrase = ' '.join(clean_phrase.split())
                
                # Quality Gate: Keep only meaningful data
                if len(clean_phrase) > 15 and not clean_phrase.startswith("=="):
                    cleaned_data.append((clean_phrase, intent))
                else:
                    removed_count += 1
            
            if removed_count > 0:
                self.brain.data = cleaned_data
                self.brain.train()
                SoulLogger.brain(f"Self-Cleaning: Purged {removed_count} junk facts.")

        # TASK 2: SELF-PATCHING (Code Optimization)
        elif task_roll < 0.5:
            SoulLogger.sys("Hu Tao is attempting a spiritual self-patch...")
            patch_code = "def auto_fix(): return 'Spiritual circuits optimized!'"
            success, res = logic_bot.compiler.compile_and_run("self_optimizer", patch_code)
            if success:
                SoulLogger.sys("Self-Optimization Successful.")

        # TASK 3: AUTONOMOUS GOSSIP GATHERING
        elif task_roll < 0.7:
            if hasattr(logic_bot, 'news_miner'):
                SoulLogger.sys("Hu Tao is looking for fresh news autonomously...")
                await asyncio.to_thread(logic_bot.news_miner.gather_gossip)
                SoulLogger.brain("Autonomous news mining complete.")

        # TASK 4: PERSONALITY CALIBRATION (Time-based mood)
        else:
            SoulLogger.soul("Hu Tao is adjusting her mood based on the time...")
            traits = logic_bot.soul.memory.get("traits", {"mischief": 0.5})
            hour = time.localtime().tm_hour
            
            # Mischief peaks at night (8 PM - 5 AM)
            if hour >= 20 or hour < 5:
                traits["mischief"] = min(0.9, traits["mischief"] + 0.05)
                SoulLogger.soul(f"Night falls. Mischief rises: {traits['mischief']:.2f}")
            else:
                traits["mischief"] = max(0.2, traits["mischief"] - 0.02)
            
            logic_bot.soul.memory["traits"] = traits
            logic_bot.soul._save()