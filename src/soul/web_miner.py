# src/soul/web_miner.py
import requests
from bs4 import BeautifulSoup
import os
import re
import random 
import time
from src import config
from src.utils.logger import SoulLogger

class SpiritSearcher:
    def __init__(self):
        self.output_folder = config.KNOWLEDGE_DIR
        self.session = requests.Session()
        # HEAVILY IMPROVED HEADERS: These simulate a modern Chrome browser to bypass anti-bot wards
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

    def clean_html_to_knowledge(self, html_content):
        """Intelligently scrapes text while bypassing structural noise and nested tags."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # --- Multi-Site Content Targeting ---
        # Prioritize the actual article body over the sidebar noise
        content_selectors = [
            'div.mw-parser-output', # Fandom/MediaWiki/Wikipedia
            'div#mw-content-text',  # Wikipedia fallback
            'article',               # News/Blogs
            'main'                   # Standard HTML5
        ]
        
        target = None
        for selector in content_selectors:
            target = soup.select_one(selector)
            if target: break
        
        if not target:
            target = soup.body

        # Remove the noise that clogs up historical articles
        for element in target(['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript', 'table', 'figure', 'label', 'form', 'div.toc']):
            element.decompose()

        extracted_facts = []
        
        # Specifically target paragraphs (p) first, as they contain the narrative lore
        for node in target.find_all(['p', 'li']):
            text = node.get_text().strip()
            
            # Scrub Wiki citations [1], [edit], [citation needed], [2a]
            text = re.sub(r'\[\s*[\d\w\s]+\s*\]', '', text)
            text = re.sub(r'\[\s*edit\s*\]', '', text, flags=re.IGNORECASE)
            
            # Basic whitespace cleanup
            text = " ".join(text.split())

            # Split into sentences
            sentences = re.split(r'(?<=[.!?]) +', text)
            for s in sentences:
                clean_s = s.strip()
                # EXPANDED LIMITS: 25 to 800 characters to capture complex history and code
                if 25 < len(clean_s) < 800:
                    # Filter out purely structural or web-specific phrases
                    if not any(x in clean_s.lower() for x in [
                        "read more", "click here", "cookie policy", 
                        "terms of service", "sign up", "privacy policy",
                        "may also like", "related articles"
                    ]):
                        if clean_s not in extracted_facts:
                            extracted_facts.append(clean_s)

        return extracted_facts

    def mine_url(self, url):
        """Attempts to fetch and extract knowledge from a specific URL with stealth."""
        # Clean up the URL in case underscores were messed up
        url = url.replace("__", "_")
        
        SoulLogger.sys(f"Attempting Stealth Mine: {url}")
        try:
            if not url.startswith("http"): url = "https://" + url
            
            # Simulated human "thinking" time
            time.sleep(random.uniform(1.2, 2.8))
            
            response = self.session.get(url, headers=self.headers, timeout=15, allow_redirects=True)
            
            if response.status_code == 403:
                return "The library guardians blocked me! Aiya! (403 Forbidden)"
            
            if response.status_code != 200:
                return f"The library door is locked. Error code: {response.status_code}"

            knowledge_lines = self.clean_html_to_knowledge(response.text)
            
            if not knowledge_lines: 
                return "I successfully slipped inside, but I couldn't find any scrolls worth reading. (No valid facts found)"

            # Create a safe filename
            topic = url.split('/')[-1] if '/' in url else "unknown"
            safe_name = re.sub(r'\W+', '_', topic)
            file_path = os.path.join(self.output_folder, f"mined_{safe_name}.txt")
            
            with open(file_path, "w", encoding="utf-8") as f:
                for line in knowledge_lines:
                    f.write(f"{line}:knowledge\n")

            SoulLogger.brain(f"Mine Success! {len(knowledge_lines)} facts gathered about {safe_name}")
            return f"Success! I sneaked into the archives and found {len(knowledge_lines)} facts about {safe_name}. I'll learn them now!~"
            
        except Exception as e:
            SoulLogger.err(f"Miner Fatal Error: {e}")
            return f"The spiritual link snapped: {str(e)}"

    def hunt_for_knowledge(self):
        """Autonomous mode targets."""
        targets = [
              # --- The Digital Incantations (Coding & Tech) ---
            "https://en.wikipedia.org/wiki/Python_(programming_language)",
            "https://en.wikipedia.org/wiki/Machine_learning",
            "https://en.wikipedia.org/wiki/Natural_language_processing",
            "https://en.wikipedia.org/wiki/Marketing",
            "https://en.wikipedia.org/wiki/Digital_marketing",
            
        ]
        url = random.choice(targets)
        return self.mine_url(url)