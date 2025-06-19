# main.py

import asyncio
import tkinter as tk
import tkinter.ttk as ttk  # Needed here for the initial library check window
import sys
import os # Keep for potential path joining if assets are at root


from src import config # Central configuration
from src.database import initialize_db, get_chat_session, save_chat_session # Database interactions
from src.gui import app as gui_app # Alias for the GUI application module
from src.character_ai import api as cai_api # CharacterAI API layer
from src.logic import activity as logic_activity # Logic for character activities
from src.logic import bot as logic_bot # Core bot processing logic
# No need to import emotion or personality directly in main, bot.py handles calls to them.
from src.utils import sys_utils # System utilities like library checks

# --- Flags and Core State ---
running = True # Flag to control the main application loop
last_interaction_time = asyncio.get_event_loop().time() # Track last user interaction timestamp

# CharacterAI client instance - managed here in main as it's a core resource
client = None

# Global reference to the Tkinter root window - necessary for the main loop and dialogs
root = None


async def main():
    """
    Main asynchronous function that initializes the application,
    sets up the GUI, connects to services, and runs the primary event loop.
    """
    global client, last_interaction_time, running, root # Declare globals used

    # --- Step 1: Initialize Tkinter and Check/Install Libraries ---
    # The root window is created in the __main__ block before calling asyncio.run
    # sys_utils uses this root for dialogs.

    # Check and install required libraries. This utility handles showing
    # the loading window and user prompts. It returns False if a restart is needed
    # or if installation failed critically.
    print("Checking required libraries...")
    # Pass the root window and messagebox/Toplevel references from Tkinter
    can_proceed = sys_utils.check_and_install_libraries(root, tk.messagebox, tk.Toplevel)

    if not can_proceed:
         # sys_utils has already informed the user and the application should exit.
         print("Library check/installation requires application termination or restart.")
         # The on_closing function is bound, but ensuring exit is good practice.
         # If root is still alive, destroy it before exiting.
         if root and root.winfo_exists():
              root.destroy()
         sys.exit("Application exit due to library requirements.")


    print("Libraries are ready. Proceeding with application initialization.")
    # Show the root window now that libraries are confirmed
    root.deiconify() # Make the main window visible


    # --- Step 2: Initialize Database ---
    print("Initializing database...")
    await initialize_db() # This function should be in src/database.py
    print("Database initialized.")

    # --- Step 3: Initialize the CharacterAI Client ---
    print("Connecting to CharacterAI...")
    try:
        # The cai_api module handles the actual client initialization and connection
        client = await cai_api.initialize_client(config.CAI_API_KEY)
        print("CharacterAI client connected successfully.")
    except Exception as e:
        print(f"Failed to initialize CharacterAI client: {e}")
        # Show a user-friendly error message via the GUI
        tk.messagebox.showerror(
            "CharacterAI Connection Error",
            f"Failed to connect to CharacterAI: {e}\n"
            "Please check your API key, character ID, and internet connection."
        )
        # Clean up and exit if a critical service like the AI is unavailable
        if root and root.winfo_exists():
             root.destroy()
        sys.exit(f"Critical Error: CharacterAI connection failed: {e}")


    # --- Step 4: Load Chat Session ---
    user_id = 1 # Hardcoded user ID for now. Could be loaded from config or user login later.
    print(f"Loading chat session for user {user_id}...")
    # get_chat_session is in src/database.py
    chat_id, conversation_history = await get_chat_session(user_id)
    print(f"Chat session loaded: chat_id={chat_id}, history_length={len(conversation_history)}")


    # --- Step 5: Setup GUI and Bind Events ---
    print("Setting up GUI elements...")
    # gui_app.setup_gui creates all the Tkinter widgets in the root window
    gui_app.setup_gui(root) # Pass the root window instance

    # Bind GUI events (like button clicks, Enter key) to async handlers
    # These handlers will schedule tasks on the asyncio loop.
    # gui_app provides methods to bind the events to our async functions.
    gui_app.bind_send_button(lambda: asyncio.create_task(handle_user_input(user_id, client, gui_app)))
    gui_app.bind_message_entry_return(lambda event: asyncio.create_task(handle_user_input(user_id, client, gui_app)))


    # --- Step 6: Initialize Character's Internal State ---
    # Initialize character state managers (Activity, Emotion, Affection).
    # These modules should handle their own internal state or load from DB.
    print("Initializing character state managers...")
    # Initialize the first activity (state is managed within logic_activity)
    logic_activity.choose_activity()
    # Emotion and Affection states are initialized to defaults in their modules
    # or should be loaded from the database if you implement state saving for them.
    # If loaded, set them using respective functions in personality and emotion modules.

    # --- Step 7: Display Initial Content ---
    # Display loaded conversation history or an initial welcome message
    if not chat_id:
         # If no session loaded, this is the first run for this user ID.
         # Display a simulated initial message from Hu Tao.
         initial_message_text = "Heya. I'm the 77th Director of the Wangsheng Funeral Parlor, Hu Tao. Are you one of my clients?"
         gui_app.update_chat_log(f"Hu Tao: {initial_message_text}", sender="hutao")
         # The actual CAI chat session creation on CAI will occur on the *first user message*
         # handled by logic_bot.process_user_message, which will get a chat_id.
    else:
         # Display the loaded history using the GUI module
         gui_app.display_conversation(conversation_history, config.USER_NAME, config.DEFAULT_USER_NAME)

    # --- Step 8: Start the Main Application Loop ---
    # Reset interaction timer on startup
    last_interaction_time = asyncio.get_event_loop().time()

    print("Application ready. Starting main loop.")

    # The main loop manages the Tkinter GUI updates and the idle timer check
    while running:
        # --- Check for Idle Timeout ---
        current_time = asyncio.get_event_loop().time()
        if current_time - last_interaction_time > config.IDLE_TIMEOUT:
            print(f"Idle timeout ({config.IDLE_TIMEOUT}s) reached. Generating idle response.")
            last_interaction_time = current_time # Reset timer immediately

            # Schedule the generation and processing of an idle response as an async task
            # logic_bot.generate_idle_response handles the API call, state updates, and GUI updates
            asyncio.create_task(logic_bot.generate_idle_response(user_id, client, gui_app))


        # --- Update Tkinter GUI ---
        # This allows Tkinter to process its event queue.
        try:
            root.update()
        except tk.TclError:
             # This exception typically occurs if the Tkinter window is closed by the user.
             running = False # Signal the main loop to stop
             print("Tkinter window closed via TclError. Stopping main loop.")
             break # Exit the loop


        # --- Small Sleep ---
        # This short sleep is crucial. It prevents the while loop from consuming 100% CPU,
        # and more importantly, it allows the asyncio event loop to switch context
        # and run other scheduled async tasks (like the CAI calls, database ops).
        await asyncio.sleep(0.01)

    print("Main loop terminated.")

    # --- Step 9: Application Shutdown ---
    print("Initiating shutdown procedures.")
    # Shut down the CharacterAI client connection
    if client: # Ensure client was successfully initialized
        await cai_api.shutdown_client(client) # cai_api module handles closing
        print("CharacterAI client closed.")

    # Any other cleanup (e.g., ensuring database connections are closed if not handled
    # by context managers elsewhere).

    print("Shutdown complete.")
    # The root.destroy() is handled by the on_closing function or the finally block below


# --- Async Handler for User Input ---
# This function is triggered by GUI events (Send button, Enter key)
# It is scheduled as an asyncio task by the GUI event bindings in setup_gui.
async def handle_user_input(user_id: int, client, gui_updater):
    """
    Handles user input from the GUI. Gets the message, updates the GUI,
    resets the idle timer, and delegates processing to the bot logic.

    Args:
        user_id: The ID of the current user.
        client: The initialized CharacterAI client instance.
        gui_updater: The object or module providing GUI update methods (src.gui.app).
    """
    global last_interaction_time # Access the global timer

    user_message = gui_updater.get_message_entry_text() # Get text from GUI entry
    if not user_message:
        return # Do nothing if message is empty

    # Update GUI immediately to show the user's message
    gui_updater.update_chat_log(f"{config.DEFAULT_USER_NAME}: {user_message}")
    gui_updater.clear_message_entry() # Clear the input field

    # Reset the idle timer since there was user interaction
    last_interaction_time = asyncio.get_event_loop().time()

    # Delegate the complex message processing to the bot logic module
    # The bot module will handle the CAI interaction, state updates, and saving.
    await logic_bot.process_user_message(
        user_message,
        user_id=user_id, # Pass user ID
        client=client, # Pass the CharacterAI client instance
        gui_updater=gui_updater, # Pass the GUI update functions/object
        # bot.py will import and use logic_activity, logic_emotion, logic_personality directly
    )
    # Note: logic_bot.process_user_message should handle updating the chat_id and
    # conversation_history and saving the session internally.


# --- Shutdown Handling ---
# This function is called by Tkinter when the window is closed.
def on_closing():
    """
    Handles the Tkinter window closing event. Signals the main loop to stop
    and schedules the stopping of the asyncio event loop.
    """
    global running, root # Access globals
    print("Closing application requested from GUI (WM_DELETE_WINDOW event).")
    running = False # Signal the main async loop to terminate

    # It's crucial to stop the asyncio loop thread-safely from the Tkinter thread.
    try:
        # Get the running event loop
        loop = asyncio.get_event_loop()
        # Schedule the loop.stop() coroutine to run in the loop's thread
        # call_soon_threadsafe is used because we are calling from a different thread (Tkinter's)
        loop.call_soon_threadsafe(loop.stop)
    except Exception as e:
        print(f"Error stopping asyncio loop threadsafe: {e}")
        # Fallback: if getting/stopping the loop fails, try to force destroy the window
        # This might be necessary if the loop isn't running yet or in some edge cases.
        if root and root.winfo_exists():
             root.destroy()
        print("Attempted fallback root.destroy() during closing.")


# --- Application Entry Point ---
# This block runs when the script is executed directly.
if __name__ == "__main__":
    # --- Step 1: Initial Tkinter Setup ---
    # Create the main Tkinter root window. It must be created in the main thread.
    # We withdraw it initially so it doesn't appear until we are ready (after library check).
    root = tk.Tk()
    root.withdraw() # Hide the initial blank window

    # Bind the window closing protocol to our handler
    # This must be done before the main loop starts.
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # --- Step 2: Run the Main Asynchronous Function ---
    # asyncio.run() is the entry point for running the top-level async function 'main'.
    # It handles creating and managing the asyncio event loop.
    try:
        print("Starting asyncio application...")
        asyncio.run(main())
    except RuntimeError as e:
        # This can happen if asyncio.run is called again or if the loop is already closed
        # during shutdown. It's often safe to ignore if it happens during planned shutdown.
        if "Event loop is closed" in str(e):
             print("Asyncio event loop was already closed during normal shutdown.")
        else:
             print(f"Runtime error during asyncio.run: {e}")
             sys.exit(f"Application exited with runtime error: {e}")
    except Exception as e:
        # Catch any unhandled exceptions during the execution of the 'main' coroutine.
        print(f"An unhandled exception occurred during asyncio.run: {e}")
        # Show an error message box to the user
        tk.messagebox.showerror("Application Error", f"An unexpected error occurred:\n{e}")
        sys.exit(f"Application exited due to unhandled error: {e}")
    finally:
         # --- Step 3: Final Cleanup ---
         # This block ensures the Tkinter root window is destroyed when the program finishes,
         # regardless of whether an exception occurred or the loop completed normally.
         if root and root.winfo_exists():
             print("Ensuring Tkinter root window is destroyed.")
             root.destroy()
         print("Application process finished.")