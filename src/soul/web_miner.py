# src/soul/web_miner.py
import requests
from bs4 import BeautifulSoup
import os
import re
import random  # FIXED: Added missing import
from src import config
from src.utils.logger import SoulLogger

class SpiritSearcher:
    def __init__(self):
        self.output_folder = config.KNOWLEDGE_DIR
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

    def clean_html_to_knowledge(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript']):
            element.decompose()

        main_content = soup.find('main') or soup.find('article') or soup.body
        if not main_content: return []

        text = main_content.get_text(separator=' ')
        text = re.sub(r'\[\d+\]', '', text) 
        sentences = re.split(r'(?<=[.!?]) +', text)
        
        # Only keep sentences that look like useful facts
        return [s.strip() for s in sentences if 40 < len(s.strip()) < 300]

    def mine_url(self, url):
        SoulLogger.sys(f"Mining URL: {url}")
        try:
            if not url.startswith("http"): url = "https://" + url
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code != 200: return f"Error {response.status_code}"

            knowledge_lines = self.clean_html_to_knowledge(response.text)
            if not knowledge_lines: return "No readable knowledge found."

            safe_name = re.sub(r'\W+', '_', url[-15:])
            file_path = os.path.join(self.output_folder, f"mined_{safe_name}.txt")
            
            with open(file_path, "w", encoding="utf-8") as f:
                for line in knowledge_lines:
                    # Tags content as knowledge for the IntentBrain
                    f.write(f"{line}:knowledge\n")

            return f"Found {len(knowledge_lines)} facts. I'll meditate on them!"
        except Exception as e:
            SoulLogger.err(f"Miner Error: {e}")
            return f"Failed to mine: {str(e)}"

    def hunt_for_knowledge(self):
        """Autonomous mode: Hu Tao picks a site she's curious about."""
        targets = [
            "https://genshin-impact.fandom.com/wiki/Hu_Tao/Lore",
            "https://genshin-impact.fandom.com/wiki/Wangsheng_Funeral_Parlor",
            "https://en.wikipedia.org/wiki/Ghost"
        ]
        # FIXED: random is now defined
        url = random.choice(targets)
        return self.mine_url(url)