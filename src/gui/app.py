# src/gui/app.py

import tkinter as tk
from tkinter import messagebox  # messagebox might be used here for GUI errors
from PIL import Image, ImageTk  # PIL is used for image processing
import asyncio  # Needed for creating async tasks from GUI events

# Import modules from your src package
from src import config  # Get configuration constants (from src/config.py)
from src.utils import image_utils  # Utility for image processing
# Need to import bot logic for handling user input
from src.logic import bot as logic_bot
# Need emotion logic to update the emotion label color based on state
from src.logic import emotion as logic_emotion
# Import __version__ directly from the src package (src/__init__.py)
from src import __version__ # <-- Re-add this import!
# Need personality logic to get initial affection if needed, although emotion affects it
# from src.logic import personality as logic_personality # Not directly needed in GUI setup

# --- Global/Module-level variables for GUI elements ---
# These will be set up in the setup_gui function
root = None # The main Tkinter root window
chat_log = None # The Text widget displaying the chat history
message_entry = None # The Entry widget for user input
send_button = None # The Button to send messages
image_label = None  # The Label displaying the Hu Tao image
name_label = None # The Label for the character's name
version_label = None # The Label for the application version
emotion_label = None  # The Label displaying the current emotion


def setup_gui(master: tk.Tk):
    """
    Sets up the main Tkinter GUI window and all its widgets.
    This function should be called once during application startup in main.py.

    Args:
        master: The root Tkinter window instance.
    """
    global root, chat_log, message_entry, send_button, image_label, name_label, version_label, emotion_label

    root = master  # Store the master window reference

    root.title("Director Hu Tao")

    # Center the window on the screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - config.WINDOW_WIDTH) // 2
    y = (screen_height - config.WINDOW_HEIGHT) // 2
    root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}+{x}+{y}")

    root.configure(bg=config.HU_TAO_DARK)

    # --- Frames ---
    main_frame = tk.Frame(root, bg=config.HU_TAO_DARK)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Frame for the Hu Tao info section (image, name, version, emotion)
    info_frame = tk.Frame(main_frame, bg=config.HU_TAO_DARK)
    info_frame.pack(side=tk.TOP, fill=tk.X)

    # Frame for the chat log
    chat_frame = tk.Frame(main_frame, bg=config.HU_TAO_DARK)
    chat_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)  # Fill remaining space

    # Frame for the input area
    input_frame = tk.Frame(root, bg=config.HU_TAO_DARK)  # Attach to root, not main_frame
    input_frame.pack(side=tk.BOTTOM, fill=tk.X)

    # --- Widgets within Frames ---

    # Hu Tao Info Frame (info_frame) - Image, Name, Version, Emotion
    # The try...except block for the image should be inside setup_gui
    try:
        # Use the utility function to create the circular image
        # This call uses the path from config.py
        print(f"Attempting to load image from: {config.HUTAO_IMAGE_PATH}") # Debug print
        circular_image = image_utils.create_circular_image(config.HUTAO_IMAGE_PATH, (75, 75))
        photo = ImageTk.PhotoImage(circular_image) # Create Tkinter compatible image
        image_label = tk.Label(info_frame, image=photo, bg=config.HU_TAO_DARK)
        image_label.image = photo  # Keep a reference to prevent garbage collection!
        image_label.pack(side=tk.LEFT, padx=10, pady=10)
        print("Image loaded successfully.")
    except FileNotFoundError:
        # Handle the case where the image file is not found
        print(f"Error: Image file not found at {config.HUTAO_IMAGE_PATH}")
        # Optionally display a placeholder or error message in the GUI where the image would be
        # e.g., image_label = tk.Label(info_frame, text="Image N/A", bg=config.HU_TAO_DARK, fg="red")
        # image_label.pack(side=tk.LEFT, padx=10, pady=10)
        image_label = None # Ensure image_label is None if loading fails
    except Exception as e:
        # Catch other potential errors during image loading or processing (e.g., invalid image file)
        print(f"Error loading or processing image at {config.HUTAO_IMAGE_PATH}: {e}")
        # Optionally display an error indicator in the GUI
        # e.g., image_label = tk.Label(info_frame, text="Image Error", bg=config.HU_TAO_DARK, fg="red")
        # image_label.pack(side=tk.LEFT, padx=10, pady=10)
        image_label = None # Ensure image_label is None if loading fails


    name_label_frame = tk.Frame(info_frame, bg=config.HU_TAO_DARK)
    name_label_frame.pack(side=tk.LEFT, pady=10)

    name_label = tk.Label(name_label_frame, text="Hu Tao", font=("Baskerville", 22), bg=config.HU_TAO_DARK,
                          fg=config.HU_TAO_RED)
    name_label.pack(side=tk.TOP, anchor=tk.W)  # Anchor name to the west

    # Version Label - Use the directly imported __version__ variable
    version_label = tk.Label(name_label_frame, text=f"by Altair, Version {__version__}", font=("Arial", 10), bg=config.HU_TAO_DARK, # <-- Use __version__ directly
                             fg=config.HU_TAO_WHITE)
    version_label.pack(side=tk.TOP, anchor=tk.W)  # Anchor version to the west

    # Emotion Label
    # Initial text and color based on the default emotion state from logic.emotion
    # Ensure logic_emotion module is initialized before this call in main.py if necessary
    initial_emotion = logic_emotion.get_current_emotion()
    emotion_label = tk.Label(info_frame, text=f"{initial_emotion}",
                             font=("Arial", 12), bg=config.HU_TAO_DARK,
                             fg=config.EMOTION_COLORS.get(initial_emotion, config.HU_TAO_WHITE))
    emotion_label.pack(side=tk.RIGHT, padx=10, pady=10)  # Pad it a bit

    # Chat Frame (chat_frame) - Text widget for chat log
    chat_log = tk.Text(chat_frame, bg=config.HU_TAO_DARK, fg=config.HU_TAO_WHITE, wrap=tk.WORD, state=tk.DISABLED,
                       font=("Courier New", 11))
    chat_log.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)  # Add some padding

    # Input Frame (input_frame) - Message entry and Send button
    message_entry = tk.Entry(input_frame, bg=config.HU_TAO_DARK, fg=config.HU_TAO_WHITE, font=("Courier New", 12),
                             insertbackground=config.HU_TAO_WHITE)
    message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)

    send_button = tk.Button(input_frame, text="Send", bg=config.HU_TAO_RED, fg=config.HU_TAO_WHITE, font=("Arial", 12),
                            padx=10, pady=10, relief=tk.FLAT)  # Use FLAT relief for a cleaner look
    send_button.pack(side=tk.RIGHT, padx=10, pady=10)

    # Configure chat log tags for coloring Hu Tao's messages
    chat_log.tag_config("hutao", foreground=config.HU_TAO_MESSAGE)


# --- GUI Update Functions ---
# These functions are called by other modules (like bot.py) to update the GUI.

def update_chat_log(message: str, sender: str = "user"):
    """
    Appends a message to the chat log Text widget.

    Args:
        message: The string message to append.
        sender: The sender of the message ("user" or "hutao").
    """
    # Check if the widget has been created before trying to use it
    if chat_log:
        chat_log.config(state=tk.NORMAL)  # Enable editing temporarily
        if sender == "hutao":
            # Insert Hu Tao's message with the 'hutao' tag for coloring
            chat_log.insert(tk.END, message + "\n", "hutao")
        else:
            # Insert user's message with default styling
            chat_log.insert(tk.END, message + "\n")
        chat_log.see(tk.END)  # Auto-scroll to the bottom
        chat_log.config(state=tk.DISABLED)  # Disable editing


def display_conversation(conversation_history: list[str], user_name: str, default_user_name: str):
    """
    Clears the chat log Text widget and displays the provided conversation history.
    Assumes history lines are formatted like "Sender: message".

    Args:
        conversation_history: A list of strings, each representing a line of conversation.
        user_name: The user's actual name prefix used in history (e.g., "Altair").
        default_user_name: The default display name for the user if the actual name isn't used.
    """
    # Check if the widget has been created before trying to use it
    if chat_log:
        chat_log.config(state=tk.NORMAL)  # Enable editing
        chat_log.delete("1.0", tk.END)  # Clear existing content

        for line in conversation_history:
            # Determine sender based on line prefix (adjust if your history format differs)
            if line.startswith("Hu Tao:"):
                update_chat_log(line, sender="hutao")
            elif line.startswith(f"{user_name}:"):
                # Use the user's actual name prefix
                update_chat_log(line, sender="user")  # Assuming 'user' sender uses default style
            elif line.startswith(f"{default_user_name}:"):
                # Also handle the default name prefix if it appears in history
                update_chat_log(line, sender="user")
            else:
                # For any other lines (e.g., system messages, potentially), just display them
                update_chat_log(line, sender="user")  # Default styling

        chat_log.config(state=tk.DISABLED)  # Disable editing
        chat_log.see(tk.END)  # Auto-scroll to the bottom


def update_emotion_label(emotion: str):
    """
    Updates the emotion label text and color based on the current emotion state.

    Args:
        emotion: The string representing the character's current emotion.
    """
    global emotion_label
    # Check if the widget has been created before trying to use it
    if emotion_label:
        # Get the color from config, fallback to white if emotion color not found
        color = config.EMOTION_COLORS.get(emotion, config.HU_TAO_WHITE)
        emotion_label.config(text=f"{emotion}", fg=color)

# You might add a function to show a messagebox if needed, although main.py also does this.
# def show_error_message(title: str, message: str):
#     messagebox.showerror(title, message)


# --- GUI Event Handlers (trigger async tasks) ---
# These functions are called directly by Tkinter events in the main thread.
# They should be lightweight and immediately schedule the actual work
# using asyncio.create_task().
# The actual processing (talking to CAI, updating state, saving) is delegated
# to the bot logic module and must be awaited, so it needs to be an async task.

# The handle_user_input function here will be called by the lambda in main.py
# That lambda in main.py *must* pass the necessary arguments (user_id, client, gui_updater)
# Let's adjust the signature here to accept them.

async def handle_user_input(user_id: int, client, gui_updater):
    """
    Handles user input from the GUI. Gets the message, updates the GUI immediately,
    and delegates the complex processing to the bot logic module as an async task.

    This function is called by the async tasks scheduled in main.py's event bindings.

    Args:
        user_id: The ID of the current user.
        client: The initialized CharacterAI client instance.
        gui_updater: This module itself (src.gui.app), passed for callbacks.
                     (e.g., gui_updater=app)
    """
    # Note: The idle timer update (last_interaction_time) is handled in main.py
    # where the async task for handle_user_input is created.

    user_message = get_message_entry_text()
    if not user_message:
        return  # Do nothing if message is empty

    # --- Immediate GUI Updates ---
    # Update chat log to show the user's message right away for responsiveness
    update_chat_log(f"{config.DEFAULT_USER_NAME}: {user_message}")
    # Clear the input field immediately
    clear_message_entry()

    # --- Delegate to Bot Logic (as an awaitable call) ---
    # Call the core bot processing function. This function is awaited here.
    # The bot function will handle CAI interaction, state updates, saving,
    # and calling back to GUI update functions (like update_chat_log, update_emotion_label)
    # when the CAI response is ready.
    try:
        print("Calling bot.process_user_message...")
        await logic_bot.process_user_message(
            user_message,
            user_id=user_id,  # Pass user ID
            client=client,  # Pass the CharacterAI client instance
            gui_updater=gui_updater,  # Pass this app module for callbacks (e.g., update_chat_log)
            # Pass references to other state/logic modules if bot.py needs them directly,
            # although bot.py should import them itself.
        )
        print("Bot processing complete.")
    except Exception as e:
         # Handle errors from the bot processing (e.g., CAI API errors, DB errors)
         print(f"Error during bot message processing: {e}")
         # Display an error message in the chat log
         update_chat_log(f"Error processing message: {e}", sender="hutao")
         # You might also want a messagebox for critical errors
         # messagebox.showerror("Processing Error", f"Failed to process message: {e}")


# --- Accessor Functions ---
# These functions allow other modules to interact with GUI widgets safely.

def get_message_entry_text() -> str:
    """Gets the current text from the message entry field."""
    # Check if the widget has been created
    if message_entry:
        return message_entry.get().strip()
    return ""


def clear_message_entry():
    """Clears the text from the message entry field."""
    # Check if the widget has been created
    if message_entry:
        message_entry.delete(0, tk.END)


# --- Functions for Binding Events (called by main.py) ---
# These functions are called by main.py during setup to link GUI events
# to the asynchronous handler defined above.

def bind_send_button(command):
    """
    Binds a command (typically an async function wrapped in asyncio.create_task)
    to the Send button click event.

    Args:
        command: The function to be called when the button is clicked.
                 This function should handle scheduling the async task.
    """
    # Check if the widget has been created
    if send_button:
        send_button.config(command=command)


def bind_message_entry_return(command):
    """
    Binds a command (typically an async function wrapped in asyncio.create_task)
    to the Return key press event in the message entry field.

    Args:
        command: The function to be called when Return is pressed.
                 This function should handle scheduling the async task.
    """
    # Check if the widget has been created
    if message_entry:
        message_entry.bind("<Return>", command)

# Note: The window closing protocol (WM_DELETE_WINDOW) is typically handled
# in main.py or the top-level application logic, as it needs to stop the
# asyncio loop and destroy the root window. This module focuses on GUI elements.

# The main application loop (root.update() calls) runs in main.py.