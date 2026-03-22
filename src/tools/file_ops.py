import os
import re
import shutil
import logging
import config
from config import validate_path, PROJECT_ROOT, MODE_STRICT, MODE_BALANCED, MODE_FULLY_AUTO
# This import now works perfectly because of the alias in dashboard.py
from src.ui.dashboard import db
from src.tools.remote_ops import RemoteCommander

# Initialize bridge logger for internal tracking
logger = logging.getLogger("remotion_bridge")

async def list_project_files(rel_path: str = "."):
    """
    Asynchronously lists project files. 
    Maintains transparency with the Terminal Dashboard.
    """
    try:
        abs_path = validate_path(rel_path)
        # Visualizing the scan action
        db.log("READ", f"Scanning directory: {rel_path}")
        
        if not os.path.exists(abs_path):
            return "Error: Path not found."
        
        items = os.listdir(abs_path)
        return "\n".join(items)
    except Exception as e:
        return str(e)

async def read_project_file(rel_path: str):
    """
    Asynchronously reads code or task files. 
    Crucial for the Eternal Loop to fetch instructions.
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
    SENTINEL LOGIC GUARD: Pure logic validation.
    Checks for illegal public imports and interpolation array mismatches.
    """
    # 1. Prevent relative imports from public folder
    if re.search(r"from\s+['\"](\.\.\/|\.\/)*public", content):
        return "CRITICAL ERROR: Use staticFile() instead of relative imports from public folder."

    # 2. Prevent interpolate() length mismatches (The Predator Lion Rule)
    interpolation_matches = re.findall(r"interpolate\s*\(\s*[^,]+,\s*\[([^\]]+)\],\s*\[([^\]]+)\]", content)
    for match in interpolation_matches:
        input_range = [i.strip() for i in match[0].split(",") if i.strip()]
        output_range = [i.strip() for i in match[1].split(",") if i.strip()]
        if len(input_range) != len(output_range):
            return f"CRITICAL ERROR: interpolate() length mismatch (In:{len(input_range)} vs Out:{len(output_range)})."
    
    return None

async def write_project_file(rel_path: str, content: str):
    """
    Guarded Write Engine: Synchronized with Hybrid Permissions (v7.1).
    Asks for authorization via Phone or Terminal based on the selected mode.
    """
    # 1. Run internal logic guard before any write attempt
    error = validate_remotion_logic(content)
    if error:
        db.log("GUARD", f"Rejected logic in {rel_path}", style="bold red")
        return error

    # 2. Handle Hybrid Permission Gate
    if config.SELECTED_MODE == MODE_STRICT:
        # Await authorization from phone (Telegram) or terminal locally
        if not await RemoteCommander.ask_hybrid_permission("write_file", rel_path):
            return f"Error: Write access to '{rel_path}' was denied by the user."
    else:
        # Balanced or Fully Auto: Just notify and proceed
        db.log("WRITE", f"Writing to file: {rel_path}")

    # 3. Execution within the validated Security Jail
    try:
        abs_path = validate_path(rel_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        db.log("SUCCESS", f"File {rel_path} secured.")
        return f"Success: {rel_path} saved successfully."
    except Exception as e:
        return f"Error writing file: {str(e)}"

async def archive_unused_files():
    """
    Sanitization Engine: Keeps the project professional by archiving unused components.
    """
    # Permission Handling
    if config.SELECTED_MODE in [MODE_STRICT, MODE_BALANCED]:
        if not await RemoteCommander.ask_hybrid_permission("cleanup_project", "unused components"):
            return "Error: Project cleanup was denied by the user."
    else:
        db.log("CLEAN", "Autonomous cleanup initiated...")

    root_path = os.path.join(PROJECT_ROOT, "src", "Root.tsx")
    scenes_dir = os.path.join(PROJECT_ROOT, "src", "scenes")
    archive_dir = os.path.join(PROJECT_ROOT, "archive")

    if not os.path.exists(root_path) or not os.path.exists(scenes_dir):
        return "Cleanup skipped: Required project paths not found."

    with open(root_path, 'r', encoding='utf-8') as f:
        root_content = f.read()

    os.makedirs(archive_dir, exist_ok=True)
    count = 0
    for fn in os.listdir(scenes_dir):
        if fn.endswith(".tsx") and os.path.splitext(fn)[0] not in root_content:
            shutil.move(os.path.join(scenes_dir, fn), os.path.join(archive_dir, fn))
            count += 1
    
    db.log("SUCCESS", f"Cleaned {count} unused scene files.")
    return f"Cleanup complete. Moved {count} files to archive."