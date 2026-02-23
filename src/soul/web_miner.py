# src/soul/web_miner.py
import requests
from bs4 import BeautifulSoup
import os
import re
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
        text = re.sub(r'\[\d+\]', '', text) # Remove citations
        sentences = re.split(r'(?<=[.!?]) +', text)
        
        return [s.strip() for s in sentences if 30 < len(s.strip()) < 300]

    def mine_url(self, url):
        SoulLogger.sys(f"Attempting to mine: {url}")
        try:
            if not url.startswith("http"):
                url = "https://" + url
                
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code != 200:
                return f"I couldn't get into that site. It said: Error {response.status_code}"

            knowledge_lines = self.clean_html_to_knowledge(response.text)
            
            if not knowledge_lines:
                return "I looked, but I couldn't find any readable text there!"

            # Create a safe filename
            safe_name = re.sub(r'\W+', '_', url[-20:])
            file_path = os.path.join(self.output_folder, f"mined_{safe_name}.txt")
            
            with open(file_path, "w", encoding="utf-8") as f:
                for line in knowledge_lines:
                    # Save as 'phrase:identity'
                    f.write(f"{line}:knowledge\n")

            SoulLogger.brain(f"Mine success! Generated {len(knowledge_lines)} facts in {file_path}")
            return f"Success! I read the page and found {len(knowledge_lines)} facts. I'll meditate on them now!"

        except Exception as e:
            SoulLogger.err(f"Miner Error: {e}")
            return f"The spirits blocked my path to that URL: {str(e)}"

    def hunt_for_knowledge(self):
        """Legacy search command for the wiki"""
        return self.mine_url("https://genshin-impact.fandom.com/wiki/Hu_Tao/Voice-Overs")