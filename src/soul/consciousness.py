import random, json, os, re
from datetime import datetime
from textblob import TextBlob
from src import config
from src.utils.logger import SoulLogger
from src.database import save_fact 

class HuTaoSoul:
    def __init__(self):
        self.path = config.SOUL_MEMORY_PATH
        self.memory = self._load_memory()

    def _load_memory(self):
        """Loads persistent soul data like affection and personality traits."""
        default = {"affection": 50, "traits": {"mischief": 0.7}}
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r') as f: return json.load(f)
            except Exception as e:
                SoulLogger.err(f"Failed to load soul memory: {e}")
        return default

    def _save(self):
        """Saves current state to the soul JSON file."""
        with open(self.path, 'w') as f: 
            json.dump(self.memory, f, indent=4)

    def generate_idle_thought(self, user_facts):
        """
        Generates a variety of proactive messages.
        Uses randomized pools and merges user-specific knowledge.
        """
        user_name = user_facts.get("name", "Traveler")
        hobby = user_facts.get("hobby", "wandering the hills")
        
        # Diversity pool for proactive engagement
        idle_pool = [
            (f"Aiya, {user_name}! The sun is high, but the spirits are restless... wanna go for a stroll?", "happy"),
            (f"Hee-hee! I was just thinking about how you enjoy {hobby}... shall we find an adventure related to that?", "mischief"),
            (f"Business is slow at the parlor today. Maybe I should go hand out some coupons? Want one, {user_name}?", "happy"),
            (f"I found a particularly interesting butterfly today. It reminded me of you!~", "happy"),
            (f"Oh! {user_name}! Are you awake? I've got a new poem I'm working on!", "surprised"),
            (f"Zhongli is off sipping tea again... leaving me all alone! Come entertain the Director!~", "mischief"),
            (f"The border between life and death is thin today... perfect for an adventure, don't you think?", "mischief")
        ]
        
        return random.choice(idle_pool)

    def get_time_response(self):
        """Returns a randomized, personality-driven time response."""
        now = datetime.now()
        current_time = now.strftime('%I:%M %p')
        
        time_variants = [
            f"It's {current_time}! Perfect for a mid-day prank, don't you think?",
            f"The clock says {current_time}. Time flies when you're having fun... or when you're a ghost!~",
            f"It's exactly {current_time}. The spirits are most active right about now...",
            f"Aiya, is it {current_time} already? The day is slipping away like a butterfly!",
            f"It's {current_time}. Should we grab some tea, or maybe go for a walk?"
        ]
        return random.choice(time_variants), "happy"

    def find_relevant_fact(self, user_input, brain_data):
        """Matches user input to the most relevant knowledge node."""
        from difflib import SequenceMatcher
        best_fact, highest = None, 0
        input_clean = user_input.lower().strip()
        
        for text, intent in brain_data:
            if intent == "knowledge":
                score = SequenceMatcher(None, input_clean, text).ratio()
                if score > highest:
                    highest, best_fact = score, text
        
        return best_fact if highest > 0.4 else None

    async def extract_and_save_facts(self, user_id, text):
        """Autonomous memory: learns about the user during conversation."""
        patterns = {
            "name": [r"my name is (\w+)", r"i'm (\w+)", r"call me (\w+)"],
            "hobby": [r"i like (\w+)", r"i enjoy (\w+)", r"my hobby is (\w+)"],
            "fear": [r"i'm scared of (\w+)", r"i hate (\w+)", r"(\w+) is scary"]
        }
        for key, regexes in patterns.items():
            for reg in regexes:
                match = re.search(reg, text.lower())
                if match:
                    fact_val = match.group(1)
                    await save_fact(user_id, key, fact_val)
                    SoulLogger.soul(f"Memory Logged: {key} -> {fact_val}")

    def generate_thought(self, intent, brain_data, user_facts, user_input):
        """Primary engine for choosing what to say based on intent."""
        user_name = user_facts.get("name", "Traveler")

        # 1. SPECIAL INTENT HANDLING
        if intent == "time":
            return self.get_time_response()

        if intent == "greet":
            greetings = [
                f"Good evening, {user_name}! Business is quiet tonight...",
                f"Aiya! Hello {user_name}!",
                "Hee-hee, you called?",
                f"Oh, it's you! Ready to help the Director with some... funeral marketing?~",
                "Silly {user_name}, you look like you've seen a ghost! Oh wait, that's just me!~"
            ]
            return random.choice(greetings), "happy"

        if intent == "identity":
            if "who am i" in user_input.lower():
                # If she knows facts about the user, she uses them dynamically
                known_facts = [f"{k} is {v}" for k, v in user_facts.items() if k != "name"]
                if known_facts:
                    detail = random.choice(known_facts)
                    return f"You're {user_name}! And I haven't forgotten that your {detail}. I'm a funeral director, I have to have a good memory!~", "mischief"
                return f"You're {user_name}, of course! Did you trip over a coffin and lose your memory?", "mischief"
            return f"I'm Hu Tao! 77th Director of the Wangsheng Funeral Parlor. But you can just call me 'Boss'!~", "mischief"

        if intent == "knowledge":
            fact = self.find_relevant_fact(user_input, brain_data)
            if fact:
                responses = [
                    f"Oh! I know something about that: {fact}",
                    f"Aha! The spirits told me this: {fact}",
                    f"I read about that in a dusty old scroll! It said: {fact}"
                ]
                return random.choice(responses), "happy"
            
            # Fallback for when she doesn't know the specific fact
            return random.choice([
                "I've heard of that, but my memory is a bit fuzzy. Want to teach me?",
                "Hmm, I'll have to ask Zhongli or the spirits about that one later!",
                f"I'm not sure about that, {user_name}, but it sounds like a mystery worth solving!"
            ]), "surprised"

        # 2. DEFAULT/SOCIAL FALLBACK (The "Idle Chatter" layer)
        self._save()
        responses = [
            "Aiya... I was daydreaming about new poem verses again. What were we saying?",
            "The spirits are whispering something... but I'd rather listen to you!~",
            f"That's interesting, {user_name}! Tell me more? Or should we go for a walk?",
            "Hee-hee! You're quite the chatterbox today! I like that in a client.~",
            "Is it just me, or is the air getting colder? Perfect for a ghost story!"
        ]
        return random.choice(responses), "happy"