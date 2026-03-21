import os
import re
import shutil
import logging
import config
from config import validate_path, PROJECT_ROOT, MODE_STRICT, MODE_BALANCED, MODE_FULLY_AUTO
from src.ui.dashboard import Dashboard as db
from src.tools.remote_ops import RemoteCommander # NEW: For v7.0 Hybrid Permissions

logger = logging.getLogger("remotion_bridge")

async def list_project_files(rel_path: str = "."):
    """
    Lists files in the project. 
    Converted to async for dispatcher consistency.
    """
    try:
        abs_path = validate_path(rel_path)
        db.log("READ", f"Scanning directory: {rel_path}")
        
        if not os.path.exists(abs_path):
            return "Error: Path not found."
        return "\n".join(os.listdir(abs_path))
    except Exception as e:
        return str(e)

async def read_project_file(rel_path: str):
    """
    Reads file content. 
    Converted to async to prevent 'str object can't be used in await' error.
    """
    try:
        abs_path = validate_path(rel_path)
        db.log("READ", f"Reading content of: {rel_path}")
        
        with open(abs_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def validate_remotion_logic(content: str):
    """
    Synchronous validation logic for Remotion best practices.
    Kept sync as it only performs regex checks on strings.
    """
    if re.search(r"from\s+['\"](\.\.\/|\.\/)*public", content):
        return "CRITICAL ERROR: Use staticFile() instead of relative imports from public folder."

    interpolation_matches = re.findall(r"interpolate\s*\(\s*[^,]+,\s*\[([^\]]+)\],\s*\[([^\]]+)\]", content)
    for match in interpolation_matches:
        input_range = [i.strip() for i in match[0].split(",") if i.strip()]
        output_range = [i.strip() for i in match[1].split(",") if i.strip()]
        if len(input_range) != len(output_range):
            return f"CRITICAL ERROR: interpolate() length mismatch (In:{len(input_range)} vs Out:{len(output_range)})."
    return None

async def write_project_file(rel_path: str, content: str):
    """
    v7.0 Guarded Async Write Engine.
    Uses the Hybrid Permission Gate to ask for authorization via Phone or Terminal.
    """
    # 1. Internal Logic Validation
    error = validate_remotion_logic(content)
    if error:
        db.log("GUARD", f"Rejected logic in {rel_path}", style="bold red")
        return error

    # 2. Hybrid Permission Handling
    # MODE_STRICT asks for every write.
    # MODE_BALANCED/FULLY_AUTO can be customized. Currently, Balanced allows auto-writes for speed.
    if config.SELECTED_MODE == MODE_STRICT:
        # Await the signal from Telegram or Terminal
        if not await RemoteCommander.ask_hybrid_permission("write_file", rel_path):
            return f"Error: Write access to '{rel_path}' was denied by the user."
    else:
        # Autonomous/Balanced: Just log the action
        db.log("WRITE", f"Writing to file: {rel_path}")

    # 3. Safe Execution within the Security Jail
    try:
        abs_path = validate_path(rel_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)
        db.log("SUCCESS", f"File {rel_path} saved safely.")
        return f"Success: {rel_path} saved successfully."
    except Exception as e:
        return f"Error: {str(e)}"

async def archive_unused_files():
    """
    v7.0 Guarded Async Cleanup Engine.
    Requires user permission in Strict and Balanced modes.
    """
    # Permission Handling
    if config.SELECTED_MODE in [MODE_STRICT, MODE_BALANCED]:
        # Await hybrid approval before touching files
        if not await RemoteCommander.ask_hybrid_permission("cleanup_project", "unused components"):
            return "Error: Project cleanup was denied by the user."
    else:
        db.log("CLEAN", "Automatically cleaning unused assets...")

    root_path = os.path.join(PROJECT_ROOT, "src", "Root.tsx")
    scenes_dir = os.path.join(PROJECT_ROOT, "src", "scenes")
    archive_dir = os.path.join(PROJECT_ROOT, "archive")

    if not os.path.exists(root_path) or not os.path.exists(scenes_dir):
        return "Cleanup skipped: Essential paths missing."

    with open(root_path, 'r', encoding='utf-8') as f:
        root_content = f.read()

    os.makedirs(archive_dir, exist_ok=True)
    count = 0
    for fn in os.listdir(scenes_dir):
        if fn.endswith(".tsx") and os.path.splitext(fn)[0] not in root_content:
            shutil.move(os.path.join(scenes_dir, fn), os.path.join(archive_dir, fn))
            count += 1
    
    db.log("SUCCESS", f"Archived {count} files.")
    return f"Cleanup complete. Moved {count} files to archive."