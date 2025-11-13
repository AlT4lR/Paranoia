# main.py 
import asyncio
import tkinter as tk
import tkinter.ttk as ttk
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """

    if getattr(sys, 'frozen', False):

        base_path = sys._MEIPASS
    else:

        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

from src import config
from src.database import initialize_db, get_chat_session, load_character_state
from src.gui import app as gui_app
from src.local_llm import engine as llm_engine
from src.logic import activity as logic_activity
from src.logic import bot as logic_bot
from src.utils import sys_utils

running = True
last_interaction_time = 0
root = None

async def main():
    global last_interaction_time, running, root
    last_interaction_time = asyncio.get_event_loop().time()
    
    if not sys_utils.check_and_install_libraries(root, tk.messagebox, tk.Toplevel):
        sys.exit("Application exit due to library requirements.")
    root.deiconify()

    await initialize_db()

    try:
        model_folder_path = resource_path("local_model")
        llm_engine.initialize_model(model_folder_path)
    except Exception as e:
        tk.messagebox.showerror("Model Initialization Error", f"Failed to load LLM: {e}")
        sys.exit(f"Critical Error: LLM failed to load: {e}")

    user_id = 1
    character_state = await load_character_state(user_id)
    logic_activity.load_activity_state(character_state)
    _, conversation_history = await get_chat_session(user_id)
    
    gui_app.setup_gui(root, image_path=resource_path(os.path.join("assets", "hutao.jpg")))
    gui_app.bind_send_button(lambda: asyncio.create_task(handle_user_input(user_id, gui_app)))
    gui_app.bind_message_entry_return(lambda event: asyncio.create_task(handle_user_input(user_id, gui_app)))

    if logic_activity.current_activity is None:
        await logic_activity.choose_activity()
    
    if not conversation_history:
        gui_app.update_chat_log("Hu Tao: Heya. I'm the 77th Director of the Wangsheng Funeral Parlor, Hu Tao.", sender="hutao")
    else:
        gui_app.display_conversation(conversation_history, config.USER_NAME, config.DEFAULT_USER_NAME)

    print("Application ready. Starting main loop.")
    while running:
        current_time = asyncio.get_event_loop().time()
        if current_time - last_interaction_time > config.IDLE_TIMEOUT:
            last_interaction_time = current_time
            asyncio.create_task(logic_bot.generate_idle_response(user_id, gui_app))
        try:
            root.update()
        except tk.TclError:
            running = False
            break
        await asyncio.sleep(0.01)

async def handle_user_input(user_id: int, gui_updater):
    global last_interaction_time
    user_message = gui_updater.get_message_entry_text()
    if not user_message: return
    gui_updater.update_chat_log(f"{config.DEFAULT_USER_NAME}: {user_message}")
    gui_updater.clear_message_entry()
    last_interaction_time = asyncio.get_event_loop().time()
    await logic_bot.process_user_message(user_message, user_id=user_id, gui_updater=gui_updater)

def on_closing():
    """
    Signals the main loop to terminate gracefully.
    We do NOT destroy the window here; we let the main loop exit naturally.
    """
    global running
    print("Window closed by user. Shutting down...")
    running = False

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    try:
        icon_path = resource_path(os.path.join("assets", "main_img.png"))
        photo_icon = tk.PhotoImage(file=icon_path)
        root.iconphoto(True, photo_icon)
    except Exception as e:
        print(f"Could not load window icon: {e}")
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    try:
        asyncio.run(main())
    except RuntimeError as e:

        if "Event loop is closed" not in str(e) and "Event loop stopped" not in str(e):
            raise
    finally:

        if root and root.winfo_exists():
            root.destroy()