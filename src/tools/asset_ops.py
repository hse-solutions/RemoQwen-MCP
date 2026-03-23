import os
import httpx
import logging
import config  # Full config for dynamic access
from src.ui.dashboard import Dashboard as db
from src.tools.remote_ops import RemoteCommander

logger = logging.getLogger("remotion_bridge")

async def download_asset(url: str, filename: str):
    """
    v8.0 Guarded Async Asset Downloader.
    Features: Mode-Aware Hybrid Permissions, Non-blocking Downloads, Filename Sanitization.
    """
    # 1. Sanitize filename first
    filename = config.sanitize_filename(filename)
    if not filename:
        filename = "asset"  # fallback

    # 2. Hybrid Permission Gate
    if config.SELECTED_MODE in (config.MODE_STRICT, config.MODE_BALANCED):
        if not await RemoteCommander.ask_hybrid_permission("download_asset", url):
            return f"Error: Download of '{filename}' from '{url}' was denied by the user."
    else:
        db.log("FETCH", f"Automatically requesting asset from: {url}")

    # 3. Path Security and Execution
    try:
        # Build relative path inside public folder
        rel_path = os.path.join("public", filename)  # relative to PROJECT_ROOT
        abs_path = config.validate_path(rel_path)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
            db.log("FETCH", f"Downloading stream initiated for {filename}...")
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()

            # Ensure the public directory exists
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)

            # Save binary content
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