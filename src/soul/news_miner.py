# src/soul/news_miner.py
import requests
import os
from src import config
from src.utils.logger import SoulLogger

class NewsMiner:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/top-headlines"
        self.output_folder = config.KNOWLEDGE_DIR

    def gather_gossip(self, category="general"):
        """Fetches world news and saves it as knowledge."""
        if not self.api_key or self.api_key == "YOUR_API_KEY":
            return "I need a 'News API Key' to listen to the world's gossip!"

        params = {
            "apiKey": self.api_key,
            "country": "us",
            "category": category,
            "pageSize": 5
        }

        try:
            SoulLogger.sys(f"Hu Tao is tuning into the world's frequency ({category})...")
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()

            if data.get("status") == "ok":
                articles = data.get("articles", [])
                filename = os.path.join(self.output_folder, f"news_{category}.txt")
                
                with open(filename, "w", encoding="utf-8") as f:
                    for art in articles:
                        title = art.get("title")
                        desc = art.get("description")
                        if title:
                            # Save as knowledge so she can 'retrive' it in conversation
                            content = f"Did you hear? {title}. {desc if desc else ''}"
                            f.write(f"{content}:knowledge\n")
                
                return f"I just heard {len(articles)} new rumors from the aether! Give me a second to process them."
            return "The news spirits are being cryptic. I couldn't understand them."
        except Exception as e:
            SoulLogger.err(f"News Miner Error: {e}")
            return "The connection to the world news was severed!"