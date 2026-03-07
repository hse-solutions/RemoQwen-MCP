import os
import requests
import logging
import config
from config import validate_path, MODE_STRICT, MODE_BALANCED, MODE_FULLY_AUTO
from src.ui.dashboard import Dashboard as db

logger = logging.getLogger("remotion_bridge")

def download_asset(url: str, filename: str):
    """
    Downloads an external asset with Mode-Aware Permission Handling.
    
    Mode Logic:
    - MODE_STRICT & MODE_BALANCED: Requires human permission (Y/n).
    - MODE_FULLY_AUTO: Automatic download with high visibility log.
    """
    # 1. Permission Gate based on Operational Mode
    if config.SELECTED_MODE in [MODE_STRICT, MODE_BALANCED]:
        # Always ask for permission before hitting the network in Guarded/Strict modes
        if not db.ask_permission("download_asset", url):
            return f"Error: Download of '{filename}' from '{url}' was denied by the user."
    else:
        # Fully Autonomous Mode: Proceed but show the FETCH icon for transparency
        db.log("FETCH", f"Requesting asset from: {url}")

    # 2. Execution Logic (Path Security Jail)
    try:
        rel_path = os.path.join("public", filename)
        abs_path = validate_path(rel_path)
        
        # Browser-like headers to avoid 403 Forbidden errors
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        # Request the asset with a 20-second timeout
        response = requests.get(url, stream=True, timeout=20, headers=headers)
        response.raise_for_status()
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        
        # Write the binary content to the public folder
        with open(abs_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        db.log("SUCCESS", f"Asset '{filename}' fetched and saved to public folder.")
        return f"Success: Asset '{filename}' is ready."

    except Exception as e:
        db.log("ERROR", f"Download failed for {url}: {str(e)}")
        return f"Error: Failed to fetch asset. {str(e)}"