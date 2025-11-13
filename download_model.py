# download_model.py (v2 - Robust Version)

import os
from huggingface_hub import snapshot_download, HfFolder
from huggingface_hub.utils import HfHubHTTPError

# --- Configuration ---
# The model repository ID on Hugging Face
MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"

# The local directory where we will save the model
# This creates the 'local_model' folder in the same directory as the script
LOCAL_MODEL_DIR = os.path.join(os.path.dirname(__file__), "local_model")

# --- Main Download Logic ---
def download_model_robustly():
    """
    Downloads the model files using the official Hugging Face library,
    which is more robust for large files and network interruptions.
    """
    print("--- Starting Robust Model Download ---")
    print(f"Model: {MODEL_ID}")
    print(f"Target directory: {LOCAL_MODEL_DIR}")
    print("\nThis process may take a long time depending on your internet speed.")
    print("Please be patient and do not interrupt the script.")

    try:
        # snapshot_download is the official, recommended way to download a full model repo.
        # It handles large files, shows progress bars, and is resumable.
        snapshot_download(
            repo_id=MODEL_ID,
            local_dir=LOCAL_MODEL_DIR,
            local_dir_use_symlinks=False,  # Set to False to copy files directly
            resume_download=True,        # If interrupted, it will try to resume
            
            # We can ignore files we don't need for inference to save space.
            # The .md and other non-essential files will be skipped.
            ignore_patterns=[
                "*.md",
                ".gitattributes",
                "*.pyc",
                "__pycache__/*",
                "sample_finetune.py"
            ]
        )
        print("\n--- Download Complete! ---")
        print("All necessary model files have been successfully downloaded.")
        print("You can now run the main application.")

    except HfHubHTTPError as e:
        print("\n--- Download Failed! ---")
        print("A network error occurred. This can happen with unstable connections.")
        print(f"Error details: {e}")
        print("\nPlease check your internet connection and try running the script again.")
        print("The download will attempt to resume from where it left off.")

    except Exception as e:
        print(f"\n--- An Unexpected Error Occurred! ---")
        print(f"Error details: {e}")

if __name__ == "__main__":
    download_model_robustly()