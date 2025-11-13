# src/gui/app.py (Complete Corrected Version)

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import asyncio

from src import config
from src.utils import image_utils
from src.logic import emotion as logic_emotion
from src import __version__

root = None
chat_log = None
message_entry = None
send_button = None
image_label = None
name_label = None
version_label = None
emotion_label = None

def setup_gui(master: tk.Tk, image_path: str):
    """ Sets up the main Tkinter GUI window and all its widgets. """
    global root, chat_log, message_entry, send_button, image_label, name_label, version_label, emotion_label

    root = master
    root.title("Director Hu Tao")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - config.WINDOW_WIDTH) // 2
    y = (screen_height - config.WINDOW_HEIGHT) // 2
    root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}+{x}+{y}")
    root.configure(bg=config.HU_TAO_DARK)

    main_frame = tk.Frame(root, bg=config.HU_TAO_DARK)
    main_frame.pack(fill=tk.BOTH, expand=True)
    info_frame = tk.Frame(main_frame, bg=config.HU_TAO_DARK)
    info_frame.pack(side=tk.TOP, fill=tk.X)
    chat_frame = tk.Frame(main_frame, bg=config.HU_TAO_DARK)
    chat_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    input_frame = tk.Frame(root, bg=config.HU_TAO_DARK)
    input_frame.pack(side=tk.BOTTOM, fill=tk.X)

    try:
        print(f"Attempting to load image from: {image_path}")
        circular_image = image_utils.create_circular_image(image_path, (75, 75))
        photo = ImageTk.PhotoImage(circular_image)
        image_label = tk.Label(info_frame, image=photo, bg=config.HU_TAO_DARK)
        image_label.image = photo
        image_label.pack(side=tk.LEFT, padx=10, pady=10)
    except Exception as e:
        print(f"Error loading avatar image: {e}")

    name_label_frame = tk.Frame(info_frame, bg=config.HU_TAO_DARK)
    name_label_frame.pack(side=tk.LEFT, pady=10)
    name_label = tk.Label(name_label_frame, text="Hu Tao", font=("Baskerville", 22), bg=config.HU_TAO_DARK, fg=config.HU_TAO_RED)
    name_label.pack(side=tk.TOP, anchor=tk.W)
    version_label = tk.Label(name_label_frame, text=f"by Altair, Version {__version__}", font=("Arial", 10), bg=config.HU_TAO_DARK, fg=config.HU_TAO_WHITE)
    version_label.pack(side=tk.TOP, anchor=tk.W)

    initial_emotion_desc = logic_emotion.get_emotion_description()
    try:
        dominant_emotion = initial_emotion_desc.split(" ")[2].replace('(', '').replace(')', '')
        initial_color = config.EMOTION_COLORS.get(dominant_emotion, config.HU_TAO_WHITE)
    except:
        initial_color = config.HU_TAO_WHITE
    emotion_label = tk.Label(info_frame, text=f"{initial_emotion_desc}", font=("Arial", 12), bg=config.HU_TAO_DARK, fg=initial_color)
    emotion_label.pack(side=tk.RIGHT, padx=10, pady=10)

    chat_log = tk.Text(chat_frame, bg=config.HU_TAO_DARK, fg=config.HU_TAO_WHITE, wrap=tk.WORD, state=tk.DISABLED, font=("Courier New", 11))
    chat_log.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)
    message_entry = tk.Entry(input_frame, bg=config.HU_TAO_DARK, fg=config.HU_TAO_WHITE, font=("Courier New", 12), insertbackground=config.HU_TAO_WHITE)
    message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
    send_button = tk.Button(input_frame, text="Send", bg=config.HU_TAO_RED, fg=config.HU_TAO_WHITE, font=("Arial", 12), padx=10, pady=10, relief=tk.FLAT)
    send_button.pack(side=tk.RIGHT, padx=10, pady=10)
    chat_log.tag_config("hutao", foreground=config.HU_TAO_MESSAGE)

def update_chat_log(message: str, sender: str = "user"):
    if chat_log:
        chat_log.config(state=tk.NORMAL)
        chat_log.insert(tk.END, message + "\n", "hutao" if sender == "hutao" else None)
        chat_log.see(tk.END)
        chat_log.config(state=tk.DISABLED)

def display_conversation(conversation_history: list[str], user_name: str, default_user_name: str):
    if chat_log:
        chat_log.config(state=tk.NORMAL)
        chat_log.delete("1.0", tk.END)
        for line in conversation_history:
            update_chat_log(line, sender="hutao" if line.startswith("Hu Tao:") else "user")
        chat_log.config(state=tk.DISABLED)
        chat_log.see(tk.END)

def update_emotion_label(emotion_description: str):
    global emotion_label
    if emotion_label:
        try:
            dominant_emotion = emotion_description.split(" ")[2].replace('(', '').replace(')', '')
            color = config.EMOTION_COLORS.get(dominant_emotion, config.HU_TAO_WHITE)
        except:
            color = config.HU_TAO_WHITE
        emotion_label.config(text=f"{emotion_description}", fg=color)

def get_message_entry_text() -> str:
    return message_entry.get().strip() if message_entry else ""

def clear_message_entry():
    if message_entry: message_entry.delete(0, tk.END)

def bind_send_button(command):
    if send_button: send_button.config(command=command)

def bind_message_entry_return(command):
    if message_entry: message_entry.bind("<Return>", command)