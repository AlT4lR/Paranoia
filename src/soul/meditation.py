# src/soul/meditation.py
import os, asyncio, time, random
from src.utils.logger import SoulLogger
from src.logic import bot as logic_bot

class SoulMeditation:
    def __init__(self, brain):
        self.brain = brain

    async def start_meditating(self):
        SoulLogger.sys("Meditation System Active. Monitoring for knowledge files...")
        while True:
            if not logic_bot.processing_lock.locked():
                try:
                    # 1. KNOWLEDGE ABSORPTION
                    files = [fn for fn in os.listdir(logic_bot.config.KNOWLEDGE_DIR) if fn.endswith(".txt")]
                    if files:
                        for fn in files:
                            SoulLogger.sys(f"Meditation: Found new scroll '{fn}'. Reading...")
                            count = 0
                            with open(os.path.join(logic_bot.config.KNOWLEDGE_DIR, fn), 'r', encoding='utf-8') as f:
                                for line in f:
                                    if ":" in line:
                                        p, i = line.split(":", 1)
                                        self.brain.data.append((p.strip().lower(), i.strip().lower()))
                                        count += 1
                            
                            self.brain.train()
                            os.remove(os.path.join(logic_bot.config.KNOWLEDGE_DIR, fn))
                            SoulLogger.sys(f"Meditation: Successfully absorbed {count} facts from '{fn}'.")

                    # 2. IDLE CHECK
                    idle_duration = time.time() - logic_bot.last_interaction_time
                    if idle_duration > 180:
                        SoulLogger.sys(f"Idle for {int(idle_duration)}s. Director is wandering...")
                        # await self.perform_tasks()

                except Exception as e:
                    SoulLogger.err(f"Meditation Logic Error: {e}")
            
            await asyncio.sleep(30)