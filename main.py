import asyncio
import tkinter as tk
import sys, os, time, traceback

# Import local modules
from src import config
from src.database import initialize_db
from src.gui import app as gui_app
from src.logic import bot as logic_bot
from src.soul.meditation import SoulMeditation
from src.utils.logger import SoulLogger
from src.utils import state  # Ensure this exists if you use state.is_running elsewhere

# --- CONFIGURATION ---
PROACTIVE_TIMEOUT = 180  # 3 Minutes of silence
last_proactive_time = time.time()
is_running = True  # Global flag for thread safety

def resource_path(relative_path):
    """ Handles asset paths for both dev and PyInstaller (compiled) environments. """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

async def handle_input():
    """ Processes text from the GUI and passes it to the bot logic. """
    if not is_running: return
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
    """ Ensures NLTK dependencies are ready for NLP tasks. """
    try:
        import nltk
        required_data = ['punkt', 'punkt_tab', 'brown', 'wordnet', 'averaged_perceptron_tagger']
        for data in required_data:
            nltk.download(data, quiet=True)
        SoulLogger.sys("Linguistic data verified.")
    except Exception as e:
        SoulLogger.err(f"Linguistic Init Error: {e}. (Ignore if offline)")

async def proactive_chat_monitor():
    """ Background task: Hu Tao reaches out if the user is silent for too long. """
    global last_proactive_time, is_running
    while is_running:
        await asyncio.sleep(10) 
        if not is_running: break
        
        idle_time = time.time() - logic_bot.last_interaction_time
        time_since_last_proactive = time.time() - last_proactive_time
        
        if idle_time > PROACTIVE_TIMEOUT and time_since_last_proactive > PROACTIVE_TIMEOUT:
            if not logic_bot.processing_lock.locked():
                try:
                    msg, emotion = await logic_bot.get_proactive_message(user_id=1)
                    gui_app.update_avatar(emotion)
                    gui_app.update_chat_log(f"Hu Tao: {msg}", sender="hutao")
                    SoulLogger.soul("Proactive Chat triggered.")
                    last_proactive_time = time.time()
                except Exception as e:
                    SoulLogger.err(f"Proactive Error: {e}")

async def main():
    global is_running
    SoulLogger.sys("--- RESILIENCE v1.5.3: SOUL EDITION ACTIVE ---")
    
    # 1. Initialize Database
    try:
        await initialize_db()
        SoulLogger.sys("Database connection verified.")
    except Exception as e:
        SoulLogger.err(f"Database Failure: {e}")

    # 2. Setup GUI
    try:
        root.deiconify()
        gui_app.setup_gui(root, image_path=resource_path(config.HUTAO_IMAGE_PATH))
        gui_app.bind_send_button(lambda: asyncio.create_task(handle_input()))
        gui_app.bind_message_entry_return(lambda e: asyncio.create_task(handle_input()))
        gui_app.update_chat_log("Hu Tao: Lighting the incense... give me a moment.", sender="hutao")
    except Exception as e:
        SoulLogger.err(f"GUI Error: {e}")

    # 3. Launch Background Souls
    # This is where your SoulMeditation is integrated
    meditation = SoulMeditation(logic_bot.brain)
    
    asyncio.create_task(ensure_linguistics())
    asyncio.create_task(meditation.start_meditating())
    asyncio.create_task(proactive_chat_monitor())
    
    SoulLogger.sys("All spiritual systems launched.")
    gui_app.update_chat_log("Hu Tao: I'm here! Ready for business?~", sender="hutao")

    # 4. Main Event Loop (Bridging Tkinter and Asyncio)
    while is_running:
        try:
            root.update()
            await asyncio.sleep(0.01)
        except (tk.TclError, Exception) as e:
            if isinstance(e, tk.TclError):
                SoulLogger.sys("GUI closed. Breaking spiritual link...")
            else:
                SoulLogger.err(f"Main Loop Error: {e}")
            is_running = False
            # Update the global state if your other modules rely on it
            state.is_running = False 
            break

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw() 
    
    # Define closing behavior
    def on_closing():
        global is_running
        is_running = False
        state.is_running = False
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        is_running = False
        state.is_running = False
        SoulLogger.sys("Shutting down gracefully...")
    except Exception as fatal_e:
        with open("crash_log.txt", "w") as f:
            f.write(traceback.format_exc())
        print(f"FATAL ERROR: See crash_log.txt")
        sys.exit(1)