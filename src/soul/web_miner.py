# src/soul/web_miner.py
import requests
from bs4 import BeautifulSoup
import os
from src import config

class SpiritSearcher:
    def __init__(self):
        self.target_url = "https://genshin-impact.fandom.com/wiki/Hu_Tao/Voice-Overs"
        self.output_folder = config.KNOWLEDGE_DIR

    def hunt_for_knowledge(self):
        """Scrapes the wiki for Hu Tao's dialogue and turns it into knowledge."""
        print("Hu Tao: 'Shh... I'm listening to the whispers of the world...'")
        try:
            response = requests.get(self.target_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Find all dialogue lines
                quotes = soup.find_all('td', style="width: 75%;")
                
                learned_count = 0
                with open(os.path.join(self.output_folder, "wiki_knowledge.txt"), "w", encoding="utf-8") as f:
                    for quote in quotes:
                        text = quote.get_text().strip()
                        if text:
                            # Map general dialogue to 'fun' or 'greet' automatically
                            f.write(f"{text}:fun\n")
                            learned_count += 1
                
                return f"I just found {learned_count} new things to say!"
            return "The internet spirits are being quiet today..."
        except Exception as e:
            return f"I tried to reach out, but: {e}"