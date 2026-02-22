import asyncio
import tkinter as tk
import sys
import os
from src import config
from src.database import initialize_db
from src.gui import app as gui_app
from src.logic import bot as logic_bot
from src.soul.meditation import SoulMeditation

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

async def handle_input():
    msg = gui_app.get_message_entry_text()
    if not msg: 
        return
    gui_app.update_chat_log(f"{config.DEFAULT_USER_NAME}: {msg}")
    gui_app.clear_message_entry()
    await logic_bot.process_user_message(msg, 1, gui_app)

async def main():
    # 1. Initialize DB and GUI
    root.deiconify()
    await initialize_db()
    
    # 2. Setup the "Soul" / Meditation background task
    # We pass the bot's brain and start it as a non-blocking task
    meditator = SoulMeditation(logic_bot.brain)
    asyncio.create_task(meditator.start_meditating())
    
    # 3. Setup GUI components
    gui_app.setup_gui(root, image_path=resource_path(config.HUTAO_IMAGE_PATH))
    gui_app.bind_send_button(lambda: asyncio.create_task(handle_input()))
    gui_app.bind_message_entry_return(lambda e: asyncio.create_task(handle_input()))

    gui_app.update_chat_log("Hu Tao: I'm here! Ready to liven things up?", sender="hutao")

    # 4. The Bridge: Running Tkinter inside the Async loop
    while True:
        try:
            root.update()
            await asyncio.sleep(0.01)
        except tk.TclError:
            # This catches the error when the window is closed
            break

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw() # Hide until database/setup is ready
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass