# src/soul/meditation.py
import os
import asyncio
from src import config

class SoulMeditation:
    def __init__(self, brain):
        self.brain = brain
        self.knowledge_path = config.KNOWLEDGE_DIR
        os.makedirs(self.knowledge_path, exist_ok=True)

    async def start_meditating(self):
        """Hu Tao scans for new knowledge files in the background."""
        print("Hu Tao's soul is now meditating in the background...")
        while True:
            try:
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
                        os.remove(file_path) # Knowledge absorbed!
                        print(f"Hu Tao: 'Aiya! I just learned everything inside {filename}!'")
                
            except Exception as e:
                print(f"Meditation Error: {e}")
            
            await asyncio.sleep(30) # Check for new knowledge every 30 seconds