import os
import asyncio
from src import config

class SoulMeditation:
    def __init__(self, brain):
        self.brain = brain
        self.knowledge_path = config.KNOWLEDGE_DIR
        os.makedirs(self.knowledge_path, exist_ok=True)

    async def start_meditating(self):
        """Hu Tao scans for new knowledge files and self-patches in the background."""
        print("Hu Tao's soul is now meditating in the background...")
        while True:
            try:
                files = [f for f in os.listdir(self.knowledge_path) if f.endswith(".txt")]
                
                if files:
                    for filename in files:
                        file_path = os.path.join(self.knowledge_path, filename)
                        absorbed_anything = False
                        
                        with open(file_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                line = line.strip()
                                if not line: continue

                                # --- 1. SELF-HEALING / CODE PATCHING ---
                                # Format: FIX:feature_name|def new_code(): ...
                                if line.startswith("FIX:"):
                                    try:
                                        content = line.replace("FIX:", "").strip()
                                        feature_to_fix, new_code = content.split("|", 1)
                                        
                                        # Use the compiler attached to the brain to apply the patch
                                        success, err = self.brain.compiler.compile_and_run(
                                            feature_to_fix.strip(), 
                                            new_code.strip()
                                        )
                                        
                                        if not success:
                                            print(f"Self-Healing Failed for {feature_to_fix}. Error: {err}")
                                        else:
                                            print(f"Hu Tao: 'Fixed a bug in my {feature_to_fix} circuits!'")
                                            absorbed_anything = True
                                    except ValueError:
                                        print(f"Skipping malformed FIX line in {filename}")

                                # --- 2. STANDARD KNOWLEDGE ABSORPTION ---
                                # Format: phrase:intent
                                elif ":" in line:
                                    phrase, intent = line.split(":", 1)
                                    self.brain.data.append((phrase.strip().lower(), intent.strip().lower()))
                                    absorbed_anything = True
                        
                        # Retrain the ML brain if new NLP data was added
                        if absorbed_anything:
                            self.brain.train()
                            print(f"Hu Tao: 'Aiya! I just absorbed the essence of {filename}!'")
                        
                        # Remove file so it isn't processed again
                        os.remove(file_path) 
                
            except Exception as e:
                print(f"Meditation Error: {e}")
            
            # Check for new knowledge every 30 seconds
            await asyncio.sleep(30)