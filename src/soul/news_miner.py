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
        """Fetches world news, saves it as knowledge, and returns a live summary."""
        if not self.api_key or self.api_key == "YOUR_API_KEY":
            return "I need a 'News API Key' to listen to the world's gossip!", []

        # Fetch up to 5 articles for broader coverage
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
                news_list = []
                
                # File path for saving knowledge
                filename = os.path.join(self.output_folder, f"news_{category}.txt")
                
                with open(filename, "w", encoding="utf-8") as f:
                    for art in articles:
                        title = art.get("title")
                        desc = art.get("description")
                        
                        if title:
                            news_list.append(title)
                            # Format for the knowledge base retrieval
                            content = f"Did you hear? {title}. {desc if desc else ''}"
                            f.write(f"{content}:knowledge\n")
                
                if news_list:
                    summary = "Um, I checked the news... " + " | ".join(news_list[:3]) # Limit summary length
                    return summary, news_list
                
                return "The news feed is empty... maybe the world is quiet today?", []
            
            return "The news spirits are being cryptic. I couldn't understand them.", []
            
        except Exception as e:
            SoulLogger.err(f"News Miner Error: {e}")
            return f"The spiritual connection to the news failed: {e}", []