# src/utils/sys_utils.py

import importlib
import subprocess
import sys
import tkinter as tk
import tkinter.ttk as ttk # ttk is needed for the progress bar
from tkinter import messagebox # messagebox is needed for showing messages


# --- Library Management ---

def get_required_libraries() -> list[str]:
    """Returns a list of libraries required by the application."""
    # This list should be kept updated based on the imports in your project
    return ['tkinter', 'PIL', 'asyncio', 'characterai', 'sqlite3', 'textblob']

def check_libraries() -> list[str]:
    """
    Checks if all required libraries are installed.

    Returns:
        A list of names of the missing libraries.
    """
    required_libraries = get_required_libraries()
    missing_libraries = []

    for lib in required_libraries:
        try:
            # Try importing the library
            importlib.import_module(lib)
        except ImportError:
            # If import fails, the library is missing
            missing_libraries.append(lib)

    return missing_libraries

def install_libraries(missing_libraries: list[str]) -> bool:
    """
    Attempts to install a list of missing libraries using pip.

    Args:
        missing_libraries: A list of library names to install.

    Returns:
        True if installation was successful, False otherwise.
    """
    if not missing_libraries:
        print("No libraries to install.")
        return True

    print(f"Attempting to install missing libraries: {', '.join(missing_libraries)}")
    try:
        # Run pip install as a subprocess
        # Use sys.executable to ensure pip from the current environment is used
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing_libraries])
        print("Libraries installed successfully!")
        return True  # Indicate successful installation
    except subprocess.CalledProcessError as e:
        print(f"Error installing libraries: {e}")
        return False # Installation failed


def create_loading_window(master: tk.Tk, Toplevel_widget: type):
    """
    Creates a simple loading window for displaying installation progress.

    Args:
        master: The parent Tkinter window (usually the root window).
        Toplevel_widget: The tk.Toplevel class from tkinter.

    Returns:
        The created Toplevel window instance.
    """
    # Create a Toplevel window as a child of the main window (even if main is hidden)
    loading_window = Toplevel_widget(master)
    loading_window.title("Installing Libraries...")
    loading_window.geometry("300x150")
    loading_window.transient(master) # Make the loading window appear on top of the master
    loading_window.grab_set() # Prevent interaction with the main window

    label = tk.Label(loading_window, text="Installing required libraries...", font=("Arial", 12))
    label.pack(pady=20)

    # Use a ttk Progressbar
    progressbar = ttk.Progressbar(loading_window, mode='indeterminate')
    progressbar.pack(pady=10, fill=tk.X, padx=20)
    progressbar.start()

    # Ensure the window is visible
    loading_window.update()

    return loading_window

def check_and_install_libraries(root_window: tk.Tk, messagebox_module, Toplevel_widget) -> bool:
    """
    Orchestrates the process of checking and installing libraries.
    Displays GUI feedback and prompts for restart if necessary.

    Args:
        root_window: The main Tkinter root window.
        messagebox_module: The tkinter.messagebox module.
        Toplevel_widget: The tkinter.Toplevel class.

    Returns:
        True if all libraries are installed and the application can proceed,
        False if libraries were installed and a restart is required, or if
        installation failed.
    """
    missing = check_libraries()

    if missing:
        print("Missing libraries detected.")
        print("Attempting to install...")

        # Create and show the loading window
        loading_window = create_loading_window(root_window, Toplevel_widget)

        # Attempt installation
        install_success = install_libraries(missing)

        # Close the loading window regardless of success
        loading_window.destroy()

        if not install_success:
            # Installation failed
            messagebox_module.showerror(
                "Error",
                "Failed to install required libraries.\n"
                "Please install them manually using pip (e.g., pip install characterai textblob) "
                "and re-run the application."
            )
            return False # Indicate failure

        else:
            # Installation succeeded
            messagebox_module.showinfo(
                "Info",
                "Required libraries installed successfully.\n"
                "Please re-run the application to load the new libraries."
            )
            # Since libraries might need to be loaded by the interpreter,
            # it's safer to ask the user to restart.
            return False # Indicate that a restart is required

    else:
        # No missing libraries
        print("All required libraries are installed.")
        return True # Indicate success, application can proceed