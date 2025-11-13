# src/utils/sys_utils.py

import importlib
import subprocess
import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox

def get_required_libraries() -> dict[str, str]:
    """
    Returns a dictionary of required libraries.
    Key: package name to install with pip.
    Value: module name to import.
    """
    # MODIFIED: Updated list to include the new ML libraries.
    return {
        'Pillow': 'PIL',
        'textblob': 'textblob',
        'torch': 'torch',
        'transformers': 'transformers',
        'accelerate': 'accelerate',
        'bitsandbytes': 'bitsandbytes'
    }

def check_libraries() -> list[str]:
    """Checks if all required libraries are installed."""
    required_libraries = get_required_libraries()
    missing_packages = []

    for package_name, module_name in required_libraries.items():
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing_packages.append(package_name)

    return missing_packages

def install_libraries(missing_packages: list[str], loading_window: tk.Toplevel) -> bool:
    """Attempts to install a list of missing libraries using pip."""
    if not missing_packages:
        return True
    
    print(f"Attempting to install missing libraries: {', '.join(missing_packages)}")
    try:
        # Provide real-time feedback to the user in the loading window
        label = loading_window.winfo_children()[0] # Get the label widget
        for package in missing_packages:
            label.config(text=f"Installing {package}...")
            loading_window.update()
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        
        print("Libraries installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing libraries: {e}")
        return False

def create_loading_window(master: tk.Tk, Toplevel_widget: type):
    """Creates a simple loading window for displaying installation progress."""
    loading_window = Toplevel_widget(master)
    loading_window.title("Initializing...")
    loading_window.geometry("350x150")
    loading_window.transient(master)
    loading_window.grab_set()
    loading_window.update_idletasks()
    
    # Center the loading window
    x = master.winfo_x() + (master.winfo_width() // 2) - (loading_window.winfo_width() // 2)
    y = master.winfo_y() + (master.winfo_height() // 2) - (loading_window.winfo_height() // 2)
    loading_window.geometry(f"+{x}+{y}")

    label = tk.Label(loading_window, text="Installing required libraries...", font=("Arial", 12))
    label.pack(pady=20)

    progressbar = ttk.Progressbar(loading_window, mode='indeterminate')
    progressbar.pack(pady=10, fill=tk.X, padx=20)
    progressbar.start(10)

    loading_window.update()
    return loading_window

def check_and_install_libraries(root_window: tk.Tk, messagebox_module, Toplevel_widget) -> bool:
    """Orchestrates checking and installing libraries with GUI feedback."""
    missing = check_libraries()

    if missing:
        loading_window = create_loading_window(root_window, Toplevel_widget)
        install_success = install_libraries(missing, loading_window)
        loading_window.destroy()

        if not install_success:
            messagebox_module.showerror(
                "Installation Error",
                "Failed to install required libraries.\nPlease install them manually and restart."
            )
            return False
        else:
            messagebox_module.showinfo(
                "Restart Required",
                "Libraries installed successfully.\nPlease restart the application."
            )
            return False
    return True