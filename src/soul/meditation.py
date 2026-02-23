# src/soul/meditation.py
import os, asyncio, time, random, re
from src import config 
from src.utils.logger import SoulLogger
from src.logic import bot as logic_bot
from src.soul.synthesizer import SoulSynthesizer
from src.logic import dynamic

class SoulMeditation:
    def __init__(self, brain):
        self.brain = brain
        self.synthesizer = SoulSynthesizer()
        self.last_task_time = 0
        self.task_cooldown = 150 # Seconds between autonomous actions

    async def start_meditating(self):
        """The main idle loop for background evolution and memory cleanup."""
        SoulLogger.sys("Meditation System Active. Hu Tao is evolving and cleaning...")
        
        while True:
            # Only run background tasks if the bot isn't busy responding to a user
            if not logic_bot.processing_lock.locked():
                try:
                    # 1. KNOWLEDGE ABSORPTION
                    if os.path.exists(config.KNOWLEDGE_DIR):
                        files = [fn for fn in os.listdir(config.KNOWLEDGE_DIR) if fn.endswith(".txt")]
                        if files:
                            for fn in files:
                                # Run as thread to avoid blocking the event loop
                                await asyncio.to_thread(self.absorb_file, fn)

                    # 2. AUTONOMOUS IDLE TASKS
                    idle_duration = time.time() - logic_bot.last_interaction_time
                    
                    if idle_duration > 180 and (time.time() - self.last_task_time) > self.task_cooldown:
                        decision = random.choice(["scrub", "mine", "synthesize"])
                        
                        if decision == "synthesize" or idle_duration > 600:
                             await self.perform_synthesis()
                        elif decision == "scrub":
                             await self.perform_scrubbing()
                        else:
                             await self.perform_mining()
                             
                        self.last_task_time = time.time()
                    
                except Exception as e:
                    SoulLogger.err(f"Meditation Logic Error: {e}")
            
            await asyncio.sleep(30)

    async def perform_scrubbing(self):
        """Tidies up the knowledge base and balances intent weights."""
        SoulLogger.sys("Autonomous: Hu Tao is tidying up her messy memory...")
        await asyncio.to_thread(self.brain.scrub_knowledge)

    async def perform_mining(self):
        """Hunts for news or wiki knowledge in the background."""
        task = random.choice(["gossip", "hunt"])
        if task == "gossip":
            res = await asyncio.to_thread(logic_bot.news_miner.gather_gossip)
        else:
            res = await asyncio.to_thread(logic_bot.searcher.hunt_for_knowledge)
        SoulLogger.soul(f"Meditation Mining: {res}")

    async def perform_synthesis(self):
        """Attempts to write code to solve past interaction failures."""
        if not logic_bot.intent_failures:
            self.brain.train()
            return

        SoulLogger.sys("Synthesis: Hu Tao is attempting to program herself...")
        
        name, code = self.synthesizer.generate_new_feature(
            logic_bot.intent_failures, 
            logic_bot.compiler.registry
        )
        
        if name and code:
            success, message = dynamic.save_new_capability(name, code, logic_bot.compiler)
            if success:
                self.brain.teach(name, "dynamic_feature")
                logic_bot.intent_failures = []
                SoulLogger.soul(f"Synthesis Success: I taught myself '{name}'!")
        else:
            SoulLogger.sys("Synthesis: Re-organizing existing thoughts.")
            self.brain.train()

    def absorb_file(self, fn):
        """
        Reads a file, filters junk, trains the brain, and safely removes file.
        Includes safety checks to prevent WinError 2.
        """
        path = os.path.join(config.KNOWLEDGE_DIR, fn)
        
        # Guard 1: Check if file still exists (Prevents error if deleted by user/another process)
        if not os.path.exists(path):
            return

        count = 0
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if ":" in line:
                        p, i = line.split(":", 1)
                        # Remove citations like [1] or [ 22 ]
                        clean_p = re.sub(r'\[\s*\d+\s*\]', '', p).strip()
                        if len(clean_p) > 5:
                            self.brain.data.append((clean_p.lower(), i.strip().lower()))
                            count += 1
            
            # Retrain brain with new balanced nodes
            if count > 0:
                self.brain.train()
            
            # Guard 2: Final existence check before deletion
            if os.path.exists(path):
                os.remove(path)
                SoulLogger.sys(f"Meditation: Successfully absorbed {count} facts from '{fn}'.")
                
        except Exception as e:
            SoulLogger.err(f"Meditation: Error processing {fn} -> {e}")