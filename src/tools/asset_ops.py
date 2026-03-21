import os
import httpx # NEW: Using Async HTTP client for v7.0 stability
import logging
import config
from config import validate_path, MODE_STRICT, MODE_BALANCED, MODE_FULLY_AUTO
from src.ui.dashboard import Dashboard as db
from src.tools.remote_ops import RemoteCommander # NEW: For v7.0 Hybrid Permissions

logger = logging.getLogger("remotion_bridge")

async def download_asset(url: str, filename: str):
    """
    v7.0 Guarded Async Asset Downloader.
    Features: Mode-Aware Hybrid Permissions and Non-blocking Downloads.
    """
    # 1. Hybrid Permission Gate
    # Balanced and Strict modes require authorization via Phone or Terminal
    if config.SELECTED_MODE in [MODE_STRICT, MODE_BALANCED]:
        # Await the signal from the user (Hybrid: Telegram + Local)
        if not await RemoteCommander.ask_hybrid_permission("download_asset", url):
            return f"Error: Download of '{filename}' from '{url}' was denied by the user."
    else:
        # Fully Autonomous Mode: Transparent logging
        db.log("FETCH", f"Automatically requesting asset from: {url}")

    # 2. Path Security and Execution
    try:
        rel_path = os.path.join("public", filename)
        abs_path = validate_path(rel_path)
        
        # Browser-mimicking headers to bypass security filters (e.g. Wikipedia)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        # 3. Non-blocking Async Download using httpx
        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
            db.log("SERVER", f"Downloading stream initiated for {filename}...")
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            
            # Ensure the public directory exists before writing
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            
            # Save the binary content
            with open(abs_path, 'wb') as f:
                f.write(response.content)
        
        db.log("SUCCESS", f"Asset '{filename}' successfully saved to public folder.")
        return f"Success: Asset '{filename}' is ready for use."

    except httpx.HTTPStatusError as e:
        db.log("ERROR", f"Web rejection (HTTP {e.response.status_code}) for {url}")
        return f"Error: The website blocked the download. Try a different URL."
    except Exception as e:
        db.log("ERROR", f"Download failed: {str(e)}")
        return f"Error: Failed to fetch asset. {str(e)}"