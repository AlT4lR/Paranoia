# src/soul/meditation.py
import os, asyncio, time, random, re
from src.utils import state 
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
        """Main idle loop for background evolution."""
        SoulLogger.sys("Meditation System Active. I'm... I'm reflecting on my studies.")
        
        while state.is_running:
            if not logic_bot.processing_lock.locked():
                try:
                    # 1. KNOWLEDGE ABSORPTION
                    if os.path.exists(config.KNOWLEDGE_DIR):
                        files = [fn for fn in os.listdir(config.KNOWLEDGE_DIR) if fn.endswith(".txt")]
                        if files:
                            for fn in files:
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
                             await self.perform_mining() # Now guaranteed to exist!
                             
                        self.last_task_time = time.time()
                    
                except Exception as e:
                    SoulLogger.err(f"Meditation Logic Error: {e}")
            
            await asyncio.sleep(30)
        
        SoulLogger.sys("Meditation loop terminated gracefully.")

    def absorb_file(self, fn):
        """Autonomously decides if new data should be a 'fact' or a 'new intent'."""
        path = os.path.join(config.KNOWLEDGE_DIR, fn)
        if not os.path.exists(path): return

        new_intent_label = fn.replace("mined_", "").replace(".txt", "").lower()
        count = 0
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if ":" in line:
                        pattern, intent = line.split(":", 1)
                        clean_pattern = re.sub(r'\[\s*\d+\s*\]', '', pattern).strip()
                        final_intent = intent.strip().lower()
                        
                        if final_intent == "knowledge" and "mined_" in fn:
                            final_intent = new_intent_label
                        
                        if len(clean_pattern) > 5:
                            self.brain.data.append((clean_pattern.lower(), final_intent))
                            count += 1
            
            if count > 0:
                SoulLogger.sys(f"Evolution: Discovered new intent category: '{new_intent_label}'")
                self.brain.train()
                if os.path.exists(path):
                    os.remove(path)
                    SoulLogger.sys(f"Meditation: Successfully absorbed {count} nodes into '{new_intent_label}'.")
        except Exception as e:
            SoulLogger.err(f"Meditation: Error in autonomous learning -> {e}")

    async def perform_scrubbing(self):
        """Tidies up the knowledge base."""
        SoulLogger.sys("Evolution: I am tidying up my messy memories...")
        await asyncio.to_thread(self.brain.scrub_knowledge)

    async def perform_mining(self):
        """Hunts for news or wiki knowledge in the background."""
        task = random.choice(["gossip", "hunt"])
        # Offload network task to thread
        res = await asyncio.to_thread(
            logic_bot.news_miner.gather_gossip if task == "gossip" else logic_bot.searcher.hunt_for_knowledge
        )
        SoulLogger.soul(f"Meditation Mining: {res}")

    async def perform_synthesis(self):
        """Attempts to write code to solve failures or spontaneously invent features."""
        # A. Personality & Memory Audit
        user_facts = await logic_bot.get_all_facts(user_id=1)
        logic_bot.soul._adjust_personality(user_facts)
        
        # Prune old persona ghosts
        await asyncio.to_thread(self.brain.audit_soul_memory)

        # B. Re-indexing
        SoulLogger.sys("Evolution: I am sorting my notes and upgrading my speech...")
        reindexed = await asyncio.to_thread(self.brain.reindex_mass_data)
        if reindexed:
            await asyncio.to_thread(self.synthesizer.audit_and_upgrade_intents, self.brain.data)

        # C. Spontaneous Invention Logic
        is_feeling_inventive = random.random() > 0.7 
        
        if not logic_bot.intent_failures and not is_feeling_inventive:
            SoulLogger.sys("Meditation: I feel content with my current skills.")
            self.brain.train()
            return

        # D. Source Code Synthesis (DNA-Based)
        reason = "spontaneous invention" if not logic_bot.intent_failures else "failure correction"
        target_failure = logic_bot.intent_failures[-1] if logic_bot.intent_failures else "academic_tool"
        
        SoulLogger.sys(f"Synthesis: I'm trying to code a solution for '{target_failure}'...")
        
        # FIXED: Pass two arguments to match the synthesizer signature (existing_code, request_intent)
        name, code = self.synthesizer.evolve_source_code("", target_failure)
        
        if name and code:
            success, message = dynamic.rewrite_or_add_capability(name, code, logic_bot.compiler)
            if success:
                self.brain.teach(name, "dynamic_feature")
                logic_bot.intent_failures = [] 
                SoulLogger.soul(f"Synthesis Success: I taught myself '{name}'! It felt... rewarding.")
                return

        # E. Evolutionary Journaling
        if logic_bot.intent_failures:
            target_intent = self.brain.predict(logic_bot.intent_failures[-1])
            if target_intent != "default":
                self.synthesizer.reflect_and_evolve(
                    target_intent, 
                    logic_bot.intent_failures[-1], 
                    logic_bot.soul.memory["traits"]
                )

        self.brain.train()