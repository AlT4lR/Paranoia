import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import asyncio
from characterai import aiocai
from database import initialize_db, save_chat_session, get_chat_session
import random
import datetime
import subprocess
import importlib
import sys
from textblob import TextBlob  # For sentiment analysis

# --- Hu Tao Color Scheme ---
HU_TAO_RED = "#FF4500"
HU_TAO_MESSAGE = "#FFB347"
HU_TAO_WHITE = "#FFFAFA"
HU_TAO_DARK = "#333333"

# --- CharacterAI Setup ---
client = aiocai.Client('YOUR_CHARACTER_AI_KEY')  # Replace with your key
USER_NAME = "Altair"  # User's name is permanently Altair
DEFAULT_USER_NAME = "Altair"  # Default name
IDLE_TIMEOUT = 180  # seconds
CHAR_ID = "YOUR_CHARACTER_ID"  # Replace with your character ID

# --- Conversation Topics ---
HU_TAO_TOPICS = [
    "funeral arrangements and the best deals for customers",
    "the latest ghost stories circulating in Liyue",
    "the most comfortable coffins for a peaceful afterlife",
    "the fascinating customs surrounding death in different cultures",
    "Wangsheng Funeral Parlor's exclusive discounts and promotions",
    "the strangest occurrences witnessed in Liyue's graveyards",
    "poems that capture the essence of death and the fleeting nature of life",
    "recent eerie events and supernatural phenomena in Liyue",
    "the various types of spirits and their unique characteristics",
    "the importance of respecting the deceased and honoring their memory",
    "philosophical debates about mortality and the purpose of existence"
]

# --- Hu Tao Activities ---
HU_TAO_ACTIVITIES = {
    "Happy": [
        "practicing polearm techniques with extra flair in the courtyard",
        "playing pranks on Qiqi and giggling mischievously",
        "planning a grand funeral event with exciting surprises",
        "bargaining with grave robbers for the most unique finds",
        "sampling the finest teas and savoring the flavors of life"
    ],
    "Sad": [
        "composing melancholic poems about lost souls",
        "meditating on the ephemeral nature of existence in solitude",
        "seeking solace in the quiet corners of Wangsheng Funeral Parlor",
        "reflecting on the delicate balance between life and death",
        "gazing at the starry night and contemplating the mysteries of the universe"
    ],
    "Angry": [
        "scolding disrespectful customers with a stern gaze",
        "arguing with Zhongli about the importance of proper funeral rites",
        "venting frustrations by smashing old vases in the courtyard",
        "complaining loudly about the incompetence of her employees",
        "threatening to haunt those who disrespect the deceased"
    ],
    "Fearful": [
        "hiding under a table during a thunderstorm",
        "clutching a lucky charm tightly while exploring a haunted site",
        "trembling at the thought of confronting vengeful spirits",
        "seeking reassurance from Zhongli about supernatural dangers",
        "avoiding dark alleys and suspicious-looking individuals"
    ],
    "Neutral": [
        "reviewing funeral arrangements with meticulous attention to detail",
        "organizing paperwork and updating records in the office",
        "conducting routine inspections of coffins and embalming equipment",
        "attending meetings with business partners and suppliers",
        "sipping tea while contemplating the day's agenda"
    ]
}

# --- Activity Progression ---
ACTIVITY_DURATION = 60  # seconds (how long an activity takes)
current_activity = None
activity_start_time = None

# --- Emotion Recognition Setup ---
EMOTIONS = ["Happy", "Sad", "Angry", "Fearful", "Surprised", "Neutral", "Disgusted", "Worried", "Loving", "Obsessed", "Endearing"] # Extended List
emotion_label = None  # Placeholder
current_emotion = "Neutral"  # Default emotion
EMOTION_COLORS = {
    "Happy": "#FFD700",     # Gold
    "Sad": "#87CEEB",       # Sky Blue
    "Angry": "#FF4500",     # Orange Red
    "Fearful": "#90EE90",   # Light Green
    "Surprised": "#DDA0DD",  # Plum
    "Neutral": "#FFFFFF",   # White
    "Disgusted": "#8B4513",  # Saddle Brown
    "Worried": "#A9A9A9",   # Dark Gray
    "Loving": "#FF69B4",    # Hot Pink
    "Obsessed": "#800080",  # Purple
    "Endearing": "#FFA07A",   # Light Salmon
}

# --- Affection System ---
DEFAULT_AFFECTION = 50
MAX_AFFECTION = 100
MIN_AFFECTION = 0
AFFECTION_CHANGE_AMOUNT = 5  # Adjust the amount of affection change per interaction
user_affection = DEFAULT_AFFECTION #Initialize the user's affection

# --- Personality Traits ---
PERSONALITY_TRAITS = {
    "optimism": 0.5,    # Positive (0.0 to 1.0)
    "cynicism": 0.2,    # Negative
    "playfulness": 0.8,   # Positive
    "seriousness": 0.3,  # Neutral/Situational
    "mischievousness": 0.7, # Neutral/Can be + or -
    "respectfulness": 0.6,  # Positive
    "worldliness": 0.4,    # Neutral/Maturity
    "impatience": 0.2,    # Negative
    "compassion": 0.7      # Positive
}

TRAIT_ADJUSTMENT_RATE = 0.01  # How much traits can change per conversation
POSITIVE_TRAITS = ["optimism", "playfulness", "respectfulness", "compassion"]
NEGATIVE_TRAITS = ["cynicism", "impatience"]
NEUTRAL_TRAITS = ["seriousness", "mischievousness", "worldliness"] #Traits that can either positively or negatively
INFLUENCE_FACTOR = 0.005 # Rate that personality effect other aspects

# --- Tkinter Setup ---
root = tk.Tk()
root.title("Director Hu Tao")

# Center the window on the screen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 800  # You can change this
window_height = 600  # You can change this
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

root.configure(bg=HU_TAO_DARK)

# --- Flags ---
running = True
last_interaction_time = asyncio.get_event_loop().time()
# user_introduced = False  # Flag to track if the user has introduced themselves - REMOVED

# --- Frames ---
main_frame = tk.Frame(root, bg=HU_TAO_DARK)
main_frame.pack(fill=tk.BOTH, expand=True)

chat_frame = tk.Frame(main_frame, bg=HU_TAO_DARK)
chat_frame.pack(fill=tk.BOTH, expand=True)

chat_log = tk.Text(chat_frame, bg=HU_TAO_DARK, fg=HU_TAO_WHITE, wrap=tk.WORD, state=tk.DISABLED)
chat_log.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

input_frame = tk.Frame(root, bg=HU_TAO_DARK)
input_frame.pack(side=tk.BOTTOM, fill=tk.X)

message_entry = tk.Entry(input_frame, bg=HU_TAO_DARK, fg=HU_TAO_WHITE, font=("Courier New", 12), insertbackground=HU_TAO_WHITE)
message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)

send_button = tk.Button(input_frame, text="Send", bg=HU_TAO_RED, fg=HU_TAO_WHITE, font=("Arial", 12), padx=10, pady=10)
send_button.pack(side=tk.RIGHT, padx=10, pady=10)

# --- Hu Tao Info ---
info_frame = tk.Frame(chat_frame, bg=HU_TAO_DARK)
info_frame.pack(side=tk.TOP, fill=tk.X)

def create_circular_image(image_path, size):
    image = Image.open(image_path).resize(size)
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    circular_image = Image.new("RGBA", size)
    circular_image.paste(image, (0, 0), mask=mask)
    return circular_image

try:
    img_path = "assets/hutao.jpg"
    circular_image = create_circular_image(img_path, (75, 75))
    photo = ImageTk.PhotoImage(circular_image)
    image_label = tk.Label(info_frame, image=photo, bg=HU_TAO_DARK)
    image_label.image = photo
    image_label.pack(side=tk.LEFT, padx=10, pady=10)
except FileNotFoundError:
    print(f"Image not found: {img_path}")

name_label_frame = tk.Frame(info_frame, bg=HU_TAO_DARK)
name_label_frame.pack(side=tk.LEFT, pady=10)

name_label = tk.Label(name_label_frame, text="Hu Tao", font=("Baskerville", 22), bg=HU_TAO_DARK, fg=HU_TAO_RED)
name_label.pack(side=tk.TOP)

version_label = tk.Label(name_label_frame, text="by Altair, Version 1.4", font=("Arial", 10), bg=HU_TAO_DARK, fg=HU_TAO_WHITE)
version_label.pack(side=tk.TOP)

# --- Emotion Label Setup ---
emotion_label = tk.Label(info_frame, text=f"{current_emotion}", font=("Arial", 12), bg=HU_TAO_DARK, fg=EMOTION_COLORS[current_emotion])  # Set initial color
emotion_label.pack(side=tk.RIGHT, padx=10)

# --- Helper Functions ---
def choose_activity():
    """Selects a new activity for Hu Tao, based on her current emotion."""
    global current_activity, activity_start_time, current_emotion
    activities = HU_TAO_ACTIVITIES.get(current_emotion, HU_TAO_ACTIVITIES["Neutral"])  # Use Neutral as default
    current_activity = random.choice(activities)
    activity_start_time = asyncio.get_event_loop().time()

def suggest_topic():
    """Randomly selects a new conversation topic from the list."""
    return random.choice(HU_TAO_TOPICS)

def get_activity_status():
    """Checks if the current activity is still ongoing, and generates more descriptive status."""
    global current_activity, activity_start_time
    if current_activity is None:
        choose_activity()
        return f"I was about to begin {current_activity}, what a coincidence you asked me this!"

    elapsed_time = asyncio.get_event_loop().time() - activity_start_time
    if elapsed_time >= ACTIVITY_DURATION:
        choose_activity()
        return f"Oh, I've just finished {current_activity}. Now, I think I'll start {current_activity}!"
    else:
        remaining_time = ACTIVITY_DURATION - elapsed_time
        return f"Currently, I'm deeply engaged in {current_activity}.  It'll take about {int(remaining_time)} more seconds."

def analyze_emotion(text):
    """More robust emotion analysis."""
    text_lower = text.lower()  # Convert to lowercase once

    # Keyword-based detection
    if any(word in text_lower for word in ["happy", "joyful", "delighted", "excited"]):
        return "Happy"
    elif any(word in text_lower for word in ["sad", "depressed", "unhappy", "grief", "mourning"]):
        return "Sad"
    elif any(word in text_lower for word in ["angry", "furious", "irate", "annoyed"]):
        return "Angry"
    elif any(word in text_lower for word in ["fearful", "scared", "afraid", "terrified"]):
        return "Fearful"
    elif any(word in text_lower for word in ["surprised", "amazed", "astonished", "shocked"]):
        return "Surprised"
    elif any(word in text_lower for word in ["disgusted", "repulsed", "sickened", "nauseated"]):
        return "Disgusted"
    elif any(word in text_lower for word in ["worried", "anxious", "concerned", "apprehensive"]):
        return "Worried"
    elif any(word in text_lower for word in ["loving", "affectionate", "caring", "romantic"]):
        return "Loving"
    elif any(word in text_lower for word in ["obsessed", "fixated", "infatuated", "stalking"]):
        return "Obsessed"  # Potentially risky, handle with care
    elif any(word in text_lower for word in ["darling", "sweetheart", "dearest", "honey"]):
        return "Endearing"
    else:
        # Fallback to TextBlob (if no keywords matched, or if you want a general baseline)
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity

        if polarity > 0.5:
            return "Happy"
        elif polarity < -0.5:
            return "Sad"
        else:
            return "Neutral" # No strong emotional cues.

def update_emotion_label(emotion):
    """Updates the emotion label in the GUI."""
    global emotion_label
    emotion_label.config(text=f"{emotion}", fg=EMOTION_COLORS.get(emotion, "#FFFFFF"))  #Update Color

def adjust_affection(amount):
    """Adjusts Hu Tao's affection towards the user, and keeps it within bounds."""
    global user_affection
    user_affection += amount
    user_affection = max(MIN_AFFECTION, min(MAX_AFFECTION, user_affection))  #Clamp the value between MIN_AFFECTION and MAX_AFFECTION

# --- Function to Analyze Conversation for Trait Expressions ---
def analyze_conversation_traits(conversation_history):
    """Analyzes recent conversation history to detect expressions of personality traits."""
    analysis = {trait: 0.0 for trait in PERSONALITY_TRAITS}  # Initialize

    # Combine recent history for analysis
    recent_history = " ".join(conversation_history[-5:])  # Last 5 lines
    recent_history_lower = recent_history.lower()

    # Optimism cues
    if any(word in recent_history_lower for word in ["hope", "bright side", "positive", "wonderful", "amazing", "believe", "confident"]):
        analysis["optimism"] += 0.1
    # Cynicism cues
    if any(word in recent_history_lower for word in ["pointless", "meaningless", "waste of time", "doomed", "inevitable", "pathetic", "useless"]):
        analysis["cynicism"] += 0.1
    # Playfulness cues
    if any(word in recent_history_lower for word in ["joke", "funny", "tease", "prank", "silly", "laugh", "amuse"]):
        analysis["playfulness"] += 0.1
    # Seriousness cues
    if any(word in recent_history_lower for word in ["important", "matter of fact", "consider", "reflection", "thoughtful", "grave", "solemn"]):
        analysis["seriousness"] += 0.1
   # Mischievousness cues
    if any(word in recent_history_lower for word in ["trick", "sneak", "surprise", "rascal", "impish", "naughty", "scheme"]):
        analysis["mischievousness"] += 0.1
    # Respectfulness cues
    if any(word in recent_history_lower for word in ["honor", "respect", "courtesy", "polite", "deference", "esteem", "revere"]):
        analysis["respectfulness"] += 0.1
    # worldliness cues (increase as she has more conversations)
    analysis["worldliness"] += 0.02
    # Impatience cues
    if any(word in recent_history_lower for word in ["hurry", "rush", "wait", "delay", "bother", "late", "annoying"]):
        analysis["impatience"] += 0.1
    # Compassion cues
    if any(word in recent_history_lower for word in ["sympathy", "care", "comfort", "console", "kind", "gentle", "empathy"]):
        analysis["compassion"] += 0.1

    return analysis

# --- Function to Adjust Personality Traits and Influence ---
def adjust_personality_traits(analysis_results):
    """Adjusts personality traits based on conversation analysis and accounts for influence."""
    global PERSONALITY_TRAITS

    for trait, value in analysis_results.items():
        PERSONALITY_TRAITS[trait] += value * TRAIT_ADJUSTMENT_RATE
        PERSONALITY_TRAITS[trait] = max(0.0, min(1.0, PERSONALITY_TRAITS[trait]))  # Clamp

    # --- Influence of Positive/Negative Traits ---
    # Example: High cynicism might slightly decrease optimism.
    for positive_trait in POSITIVE_TRAITS:
        for negative_trait in NEGATIVE_TRAITS:
            influence = (PERSONALITY_TRAITS[negative_trait] - 0.5) * INFLUENCE_FACTOR  #Influence will be positive when over 0.5, and negative is below.
            PERSONALITY_TRAITS[positive_trait] -= influence  # Diminish positive traits

            #Do this so high positive trait will reduce negative traits
            influence = (PERSONALITY_TRAITS[positive_trait] - 0.5) * INFLUENCE_FACTOR
            PERSONALITY_TRAITS[negative_trait] -= influence #reduce negative traits

        for neutral_trait in NEUTRAL_TRAITS: #balance neutral traits
            influence = (PERSONALITY_TRAITS[positive_trait] - 0.5) * INFLUENCE_FACTOR  #Influence will be positive when over 0.5, and negative is below.
            PERSONALITY_TRAITS[neutral_trait] += influence  # Diminish neutral traits

            #Do this so high positive trait will reduce neutral traits
            influence = (PERSONALITY_TRAITS[negative_trait] - 0.5) * INFLUENCE_FACTOR
            PERSONALITY_TRAITS[neutral_trait] += influence #reduce neutral traits

# --- CharacterAI Functions ---
async def handle_characterai_command(user_id, message):  # Removed display_traits parameter
    global current_activity, activity_start_time, current_emotion, user_affection, USER_NAME, PERSONALITY_TRAITS

    try:
        chat_id, conversation_history = await get_chat_session(user_id)
        chat = await client.connect()

        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")
        current_date = now.strftime("%Y-%m-%d")
        context = f"The current time is {current_time} on {current_date}. "

        if not chat_id:
            initial_message = "Heya. I'm the 77th Director of the Wangsheng Funeral Parlor, Hu Tao. Are you one of my clients?"
            new_chat, _ = await chat.new_chat(CHAR_ID, (await client.get_me()).id)
            chat_id = new_chat.chat_id
            conversation_history = [f"Hu Tao: {initial_message}"]
            await save_chat_session(user_id, chat_id, conversation_history)


        # Analyze recent conversation
        trait_analysis = analyze_conversation_traits(conversation_history)
        adjust_personality_traits(trait_analysis) #Adjusted to save.

        # ---- Affection-Based Tone Adjustment ----
        if user_affection > 75:
            tone = "Warm, playful, and slightly flirtatious"
        elif user_affection < 25:
            tone = "Slightly distant, teasing, and subtly morbid"
        else:
            tone = "Playful, mischievous, and generally cheerful"

        # Remove personality string from the prompt
        prompt = f"""You are Hu Tao, the 77th Director of the Wangsheng Funeral Parlor.
        Your **primary** goal is to directly respond to {USER_NAME}'s message in a meaningful and relevant way. Do not ignore the user.
        Do not introduce unrelated topics unless they are very closely tied to Wangsheng Funeral Parlor or death.
        Maintain your personality and the tone of {tone} given your affection level towards {USER_NAME}, which is {user_affection} out of 100.

        **Be concise and avoid excessive tangents or overly long responses.** Keep the conversation focused.

        Remember to have a good time and never break character. Always try to bring it back to funeral and death,
        always make a dark joke with the user if there's opening.

        Previous conversation:
        {conversation_history}

        {USER_NAME}: {message}
        Hu Tao: """

        full_message = context + prompt
        response = await chat.send_message(CHAR_ID, chat_id, full_message)
        response_text = response.text

        # Analyze emotion
        current_emotion = analyze_emotion(response_text)
        update_emotion_label(current_emotion)

        # Adjust affection based on emotion
        if current_emotion == "Happy" or current_emotion == "Endearing":
            adjust_affection(AFFECTION_CHANGE_AMOUNT)
        elif current_emotion == "Angry" or current_emotion == "Disgusted":
            adjust_affection(-AFFECTION_CHANGE_AMOUNT)

        conversation_history.append(f"{USER_NAME}: {message}")
        conversation_history.append(f"Hu Tao: {response_text}")
        await save_chat_session(user_id, chat_id, conversation_history)

        return response_text

    except Exception as e:
        print(f"Error generating content: {e}")
        return f"Error: {e}"

# --- Chat Handling ---
def update_chat_log(message, sender="user"):
    chat_log.config(state=tk.NORMAL)
    if sender == "hutao":
        chat_log.insert(tk.END, message + "\n", "hutao")
    else:
        chat_log.insert(tk.END, message + "\n")
    chat_log.tag_config("hutao", foreground=HU_TAO_MESSAGE)
    chat_log.see(tk.END)
    chat_log.config(state=tk.DISABLED)

def send_message():
    global last_interaction_time

    user_message = message_entry.get().strip()

    if user_message:

        update_chat_log(f"{DEFAULT_USER_NAME}: {user_message}") #start up Altair if never introduced.
        message_entry.delete(0, tk.END)
        asyncio.create_task(process_response(user_message))
        last_interaction_time = asyncio.get_event_loop().time()

async def process_response(message):
    user_id = 1
    # Simulate activity interruption (20% chance)
    if random.random() < 0.2:
        interruption_message = f"Oh, excuse me! I was in the middle of {current_activity} when your message came through!"
        update_chat_log(f"Hu Tao: {interruption_message}", sender="hutao")
        display_conversation()
        await asyncio.sleep(1)  #Small delay to see interupt message

    response = await handle_characterai_command(user_id, message) # Changed the trait
    update_chat_log(f"Hu Tao: {response}", sender="hutao")
    display_conversation()
    # No longer updating trait labels, since the display is removed.

def display_conversation():
    async def _display_conversation():
        global USER_NAME
        user_id = 1
        chat_id, conversation_history = await get_chat_session(user_id)

        chat_log.config(state=tk.NORMAL)
        chat_log.delete("1.0", tk.END)

        for line in conversation_history:
            if line.startswith("Hu Tao:"):
                update_chat_log(line, sender="hutao")

            elif line.startswith(f"{USER_NAME}:"):  # Already replaced. Use USERNAME
               update_chat_log(line) #append old record
            elif line.startswith(f"{DEFAULT_USER_NAME}:"): # if intro have yet or wrong recognized intro do!
                 update_chat_log(line) #keep showing name if dont have USER_NAME
            else:

                update_chat_log(line)


        chat_log.config(state=tk.DISABLED)
        chat_log.see(tk.END)

    asyncio.create_task(_display_conversation())

async def generate_idle_response(user_id):
    global current_emotion, user_affection
    try:
        chat_id, conversation_history = await get_chat_session(user_id)
        chat = await client.connect()

        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")
        current_date = now.strftime("%Y-%m-%d")
        context = f"The current time is {current_time} on {current_date}. "

        if not chat_id:
            new_chat, _ = await chat.new_chat(CHAR_ID, (await client.get_me()).id)
            chat_id = new_chat.chat_id
            conversation_history = []
            await save_chat_session(user_id, chat_id, conversation_history)

        # ---- More Dynamic Idle Prompts ----
        activity_status = get_activity_status() #Get activities
        if random.random() < 0.6: #combine activities with conversation starter to show aliveness.
            topic = random.choice(HU_TAO_TOPICS)
            prompt = f"""You are Hu Tao. The user is idle. {activity_status}. **Briefly** re-engage them by playfully suggesting the topic: {topic} in a dark humor way, but **ONLY IF IT RELATES TO THE LAST TOPIC DISCUSSED, or something the USER said**.  Otherwise, simply greet them and ask if they have any further inquiries about Wangsheng Funeral Parlor. Don't ask if they need help or are there. Be conversational not creepy. Keep it short.
            Hu Tao's current affection level towards {USER_NAME} is {user_affection} out of 100."""
        else:
            prompt = f"""You are Hu Tao. The user is idle. Re-engage them.  **Be conversational not creepy, and keep to your role.** Briefly mention your current activity, which is {activity_status}. then **immediately ask if they have any questions related to your work or the Parlor.** Do not drift off-topic.
            Hu Tao's current affection level towards {USER_NAME} is {user_affection} out of 100."""

        full_message = context + prompt
        response = await chat.send_message(CHAR_ID, chat_id, full_message)
        response_text = response.text

        # Basic response filtering
        if "I am an AI" in response_text or len(response_text) < 5:
            print("Filtered nonsensical response.")
            response_text = "Hehe... Are you still there?"

        # Analyze emotion
        current_emotion = analyze_emotion(response_text)
        update_emotion_label(current_emotion)

        # Adjust affection based on emotion
        if current_emotion == "Happy" or current_emotion == "Endearing":
            adjust_affection(AFFECTION_CHANGE_AMOUNT)
        elif current_emotion == "Angry" or current_emotion == "Disgusted":
            adjust_affection(-AFFECTION_CHANGE_AMOUNT)

        conversation_history.append(f"Hu Tao: {response_text}")
        await save_chat_session(user_id, chat_id, conversation_history)

        return response_text

    except Exception as e:
        print(f"Error generating idle response: {e}")
        return "Boo! Did I scare you?"

# --- Shutdown Handling ---
async def shutdown():
    print("Shutting down...")
    try:
        if hasattr(client, 'close') and callable(client.close):
            await client.close()
            print("CharacterAI client closed")
    except Exception as e:
        print(f"Error closing client: {e}")
    print("Shutdown complete.")

def on_closing():
    global running
    running = False
    print("Closing application...")

    async def _close():
        await shutdown()
        root.destroy()

    asyncio.create_task(_close())


send_button.config(command=send_message)
message_entry.bind("<Return>", lambda event: send_message())
root.protocol("WM_DELETE_WINDOW", on_closing)

def check_libraries():
    required_libraries = ['tkinter', 'PIL', 'asyncio', 'characterai', 'sqlite3', 'textblob']
    missing_libraries = []

    for lib in required_libraries:
        try:
            importlib.import_module(lib)
        except ImportError:
            missing_libraries.append(lib)

    return missing_libraries

def install_libraries(missing_libraries):
    try:
        subprocess.check_call(['pip', 'install', *missing_libraries])
        print("Libraries installed successfully!")
        return True  # Indicate successful installation
    except subprocess.CalledProcessError as e:
        print(f"Error installing libraries: {e}")
        return False # Installation failed

def create_loading_window():
    loading_window = tk.Toplevel(root) # Creates a child window
    loading_window.title("Installing Libraries...")
    loading_window.geometry("300x150")

    label = tk.Label(loading_window, text="Installing required libraries...", font=("Arial", 12))
    label.pack(pady=20)

    progressbar = tk.ttk.Progressbar(loading_window, mode='indeterminate')
    progressbar.pack(pady=10, fill=tk.X, padx=20)
    progressbar.start()

    return loading_window

# --- Tkinter with Asyncio Support ---
async def main():

    missing = check_libraries()
    if missing:

        print("Missing libraries: ", missing)
        print("Attempting to install...")

        loading_window = create_loading_window()

        install_success = install_libraries(missing)
        loading_window.destroy()  #Close window regardless of install

        if not install_success:
            messagebox.showerror("Error", "Please install the required libraries to launch Hu Tao Director AI!")
            root.destroy()
            sys.exit()  #ensure script stop
        else:
            messagebox.showinfo("Info", "Libraries intalled, Please re-run to see changes!") #restart for code load

            sys.exit()  #quit instead since library require another start.


    else:
        print("All required libraries are installed.")

    await initialize_db()
    global client, last_interaction_time, user_affection
    client = aiocai.Client('YOUR_CHARACTER_AI_KEY')  # Replace with your key
    user_id = 1
    chat_id, conversation_history = await get_chat_session(user_id)

    first_message_sent = False
    global current_activity, activity_start_time, USER_NAME

    USER_NAME = DEFAULT_USER_NAME   #IMPORTANT if session exit and come back for default Altair to properly initialized!
    choose_activity() # Initialize the activity when the bot starts

    global emotion_label, current_emotion
    current_emotion = "Neutral"

    user_affection = DEFAULT_AFFECTION  # Initialize affection when the bot starts

    while running:
        user_id = 1
        chat_id, conversation_history = await get_chat_session(user_id)

        if not chat_id and not first_message_sent:
            initial_message = "Heya. I'm the 77th Director of the Wangsheng Funeral Parlor, Hu Tao. Are you one of my clients?"
            update_chat_log(f"Hu Tao: {initial_message}", sender="hutao")
            first_message_sent = True
            new_chat = await client.connect()
            new_chat, _ = await new_chat.new_chat(CHAR_ID, (await client.get_me()).id)
            chat_id = new_chat.chat_id
            conversation_history = [f"Hu Tao: {initial_message}"]
            await save_chat_session(user_id, chat_id, conversation_history)

        elif not chat_id and first_message_sent:
            print("New Session. Please Wait...")

        try:
            current_time = asyncio.get_event_loop().time()
            if current_time - last_interaction_time > IDLE_TIMEOUT:
                last_interaction_time = current_time

                idle_message = await generate_idle_response(user_id)

                chat_id, conversation_history = await get_chat_session(user_id)
                conversation_history.append(f"Hu Tao: {idle_message}")
                await save_chat_session(user_id, chat_id, conversation_history)

                update_chat_log(f"Hu Tao: {idle_message}", sender="hutao")

                display_conversation()

            root.update()
            await asyncio.sleep(0.01)
        except tk.TclError:
            break

    print("Main loop terminated.")

if __name__ == "__main__":
    # Ensure Tkinter is initialized *before* checking libraries
    import tkinter.ttk as ttk

    asyncio.run(main())