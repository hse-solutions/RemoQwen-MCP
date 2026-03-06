import os
import requests
import logging
from config import validate_path
from src.ui.dashboard import Dashboard as db

logger = logging.getLogger("remotion_bridge")

def download_asset(url, filename):
    """
    Guarded tool to download external assets.
    Requires human permission (Y/n) before starting the download.
    """
    # 1. Ask for human permission before hitting the network
    # We show the URL as the target so the user knows where the file is coming from
    if not db.ask_permission("download_asset", url):
        return f"Error: Download of '{filename}' was denied by the user."

    # 2. Proceed with the download if granted
    rel_path = os.path.join("public", filename)
    abs_path = validate_path(rel_path)
    
    # Browser-like headers to prevent 403 Forbidden errors
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, stream=True, timeout=20, headers=headers)
        response.raise_for_status()
        
        # Ensure the public directory exists
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        
        with open(abs_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        return f"Success: Asset '{filename}' downloaded and saved to public folder."
        
    except Exception as e:
        logger.error(f"Download failed for {url}: {str(e)}")
        return f"Error: Failed to download asset. {str(e)}"