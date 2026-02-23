# main.py
import asyncio
import tkinter as tk
import sys
import os
import traceback

# Import local modules
from src import config
from src.database import initialize_db
from src.gui import app as gui_app
from src.logic import bot as logic_bot
from src.soul.meditation import SoulMeditation
from src.utils.logger import SoulLogger

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

async def handle_input():
    try:
        msg = gui_app.get_message_entry_text()
        if not msg: return
        gui_app.update_chat_log(f"{config.DEFAULT_USER_NAME}: {msg}")
        gui_app.clear_message_entry()
        try:
            await logic_bot.process_user_message(msg, 1, gui_app)
        except Exception as e:
            SoulLogger.err(f"Logic Processing Error: {e}")
            gui_app.update_chat_log("Hu Tao: Aiya! My spiritual circuits are tangled...", sender="hutao")
    except Exception as e:
        SoulLogger.err(f"Input Handling Error: {e}")

async def ensure_linguistics():
    """Ensures TextBlob/NLTK dependencies are ready."""
    try:
        import nltk
        # Vital components for Hu Tao's NLP
        required_data = ['punkt', 'punkt_tab', 'brown', 'wordnet', 'averaged_perceptron_tagger']
        for data in required_data:
            nltk.download(data, quiet=True)
        SoulLogger.sys("Linguistic data verified.")
    except Exception as e:
        SoulLogger.err(f"Linguistic Init Error: {e}. (Ignore if offline)")

async def main():
    SoulLogger.sys("--- RESILIENCE MODE ACTIVE ---")
    
    # 1. Initialize Database
    try:
        await initialize_db()
        SoulLogger.sys("Database connection verified.")
    except Exception as e:
        SoulLogger.err(f"Database Failure: {e}")

    # 2. Setup GUI (Show window early to avoid 'hanging' feel)
    try:
        root.deiconify()
        gui_app.setup_gui(root, image_path=resource_path(config.HUTAO_IMAGE_PATH))
        gui_app.bind_send_button(lambda: asyncio.create_task(handle_input()))
        gui_app.bind_message_entry_return(lambda e: asyncio.create_task(handle_input()))
        gui_app.update_chat_log("Hu Tao: Lighting the incense... give me a moment.", sender="hutao")
        SoulLogger.sys("GUI Interface active.")
    except Exception as e:
        SoulLogger.err(f"GUI Error: {e}")

    # 3. Background: Verify Linguistics (NLTK)
    asyncio.create_task(ensure_linguistics())

    # 4. Background: Start Meditation
    try:
        meditator = SoulMeditation(logic_bot.brain)
        asyncio.create_task(meditator.start_meditating())
        SoulLogger.sys("Meditation task launched.")
    except Exception as e:
        SoulLogger.err(f"Meditation system failed: {e}")

    gui_app.update_chat_log("Hu Tao: I'm here! Ready for business?~", sender="hutao")

    # 5. Main Loop
    while True:
        try:
            root.update()
            await asyncio.sleep(0.01)
        except tk.TclError:
            break
        except Exception as e:
            SoulLogger.err(f"Main Loop Error: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw() # Hide until GUI is ready
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        SoulLogger.sys("Shutting down gracefully...")
    except Exception as fatal_e:
        with open("crash_log.txt", "w") as f:
            f.write(traceback.format_exc())