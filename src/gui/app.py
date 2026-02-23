# src/gui/app.py
import tkinter as tk
from PIL import Image, ImageTk
import os
from src import config
from src.utils import image_utils

# Global references for the GUI elements
image_label = None
root = None

def setup_gui(master: tk.Tk, image_path: str):
    global root, image_label, chat_log, message_entry, send_button, emotion_label
    root = master
    root.title("Director Hu Tao")
    root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
    root.configure(bg=config.HU_TAO_DARK)

    # --- UI Layout ---
    info_frame = tk.Frame(root, bg=config.HU_TAO_DARK)
    info_frame.pack(side=tk.TOP, fill=tk.X)

    # Avatar Image
    try:
        circular_img = image_utils.create_circular_image(image_path, (80, 80))
        photo = ImageTk.PhotoImage(circular_img)
        image_label = tk.Label(info_frame, image=photo, bg=config.HU_TAO_DARK)
        image_label.image = photo # Keep reference
        image_label.pack(side=tk.LEFT, padx=15, pady=10)
    except: pass

    # Name and Version
    text_frame = tk.Frame(info_frame, bg=config.HU_TAO_DARK)
    text_frame.pack(side=tk.LEFT)
    tk.Label(text_frame, text="Hu Tao", font=("Baskerville", 22, "bold"), fg=config.HU_TAO_RED, bg=config.HU_TAO_DARK).pack(anchor="w")
    tk.Label(text_frame, text=f"v1.5.2 Resilience", font=("Arial", 10), fg="gray", bg=config.HU_TAO_DARK).pack(anchor="w")

    emotion_label = tk.Label(info_frame, text="Playful", font=("Arial", 12), fg=config.HU_TAO_MESSAGE, bg=config.HU_TAO_DARK)
    emotion_label.pack(side=tk.RIGHT, padx=20)

    # Chat Log
    chat_frame = tk.Frame(root, bg=config.HU_TAO_DARK)
    chat_frame.pack(fill=tk.BOTH, expand=True, padx=10)
    chat_log = tk.Text(chat_frame, bg="#1e1e1e", fg="white", font=("Courier New", 11), state=tk.DISABLED, wrap=tk.WORD)
    chat_log.pack(fill=tk.BOTH, expand=True)

    # Input
    input_frame = tk.Frame(root, bg=config.HU_TAO_DARK)
    input_frame.pack(fill=tk.X, side=tk.BOTTOM)
    message_entry = tk.Entry(input_frame, bg="#2d2d2d", fg="white", font=("Courier New", 12), insertbackground="white")
    message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
    send_button = tk.Button(input_frame, text="Send", bg=config.HU_TAO_RED, fg="white", width=10)
    send_button.pack(side=tk.RIGHT, padx=10)

def update_avatar(emotion):
    """Swaps Hu Tao's face based on her mood."""
    global image_label
    if not image_label: return

    # Map emotions to file names
    img_map = {
        "happy": "happy.jpg",
        "mischief": "mischief.jpg",
        "sad": "sad.jpg",
        "surprised": "surprised.jpg",
        "default": "hutao.jpg"
    }
    
    img_name = img_map.get(emotion, "hutao.jpg")
    img_path = os.path.join(config.ASSETS_DIR, img_name)

    # If the emotional image doesn't exist, stay with the default
    if not os.path.exists(img_path):
        img_path = os.path.join(config.ASSETS_DIR, "hutao.jpg")

    try:
        circular_img = image_utils.create_circular_image(img_path, (80, 80))
        photo = ImageTk.PhotoImage(circular_img)
        image_label.config(image=photo)
        image_label.image = photo
        
        # Also update the text label
        color_map = {"happy": "#FFD700", "sad": "#87CEEB", "mischief": "#FF4500"}
        emotion_label.config(text=emotion.capitalize(), fg=color_map.get(emotion, config.HU_TAO_MESSAGE))
    except: pass

def update_chat_log(message, sender="user"):
    chat_log.config(state=tk.NORMAL)
    tag = "hutao" if sender == "hutao" else "user"
    chat_log.insert(tk.END, message + "\n", tag)
    chat_log.tag_config("hutao", foreground=config.HU_TAO_MESSAGE)
    chat_log.see(tk.END)
    chat_log.config(state=tk.DISABLED)

def get_message_entry_text(): return message_entry.get()
def clear_message_entry(): message_entry.delete(0, tk.END)
def bind_send_button(cmd): send_button.config(command=cmd)
def bind_message_entry_return(cmd): message_entry.bind("<Return>", cmd)