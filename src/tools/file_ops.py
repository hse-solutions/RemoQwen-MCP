import os
import re
import shutil
import logging
from config import validate_path, PROJECT_ROOT
from src.ui.dashboard import Dashboard as db

logger = logging.getLogger("remotion_bridge")

def list_project_files(rel_path="."):
    """Read-only tool to explore the project structure. No permission needed."""
    abs_path = validate_path(rel_path)
    return "\n".join(os.listdir(abs_path)) if os.path.exists(abs_path) else "Path not found."

def read_project_file(rel_path):
    """Read-only tool to understand code context. No permission needed."""
    abs_path = validate_path(rel_path)
    with open(abs_path, 'r', encoding='utf-8') as f:
        return f.read()

def validate_remotion_logic(content):
    """Checks for core Remotion best-practice violations before writing."""
    if re.search(r"from\s+['\"](\.\.\/|\.\/)*public", content):
        return "CRITICAL ERROR: Use staticFile() instead of relative imports from public."
    
    # Check for interpolate() array length mismatch
    matches = re.findall(r"interpolate\s*\(\s*[^,]+,\s*\[([^\]]+)\],\s*\[([^\]]+)\]", content)
    for m in matches:
        if len(m[0].split(",")) != len(m[1].split(",")):
            return "CRITICAL ERROR: interpolate() array length mismatch."
    return None

def write_project_file(rel_path, content):
    """
    Guarded tool to write files. 
    Requires human permission (Y/n) before saving the file.
    """
    # 1. First, check if the code logic is correct
    error = validate_remotion_logic(content)
    if error:
        return error

    # 2. Ask for user permission (The Claude Code experience)
    if not db.ask_permission("write_file", rel_path):
        return f"Error: Write access to '{rel_path}' was denied by the user."

    # 3. If allowed, perform the write
    abs_path = validate_path(rel_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return f"Success: {rel_path} saved successfully."

def archive_unused_files():
    """
    Guarded tool to cleanup the project.
    Requires human permission before moving files to archive.
    """
    root_path = os.path.join(PROJECT_ROOT, "src", "Root.tsx")
    scenes_dir = os.path.join(PROJECT_ROOT, "src", "scenes")
    archive_dir = os.path.join(PROJECT_ROOT, "archive")
    
    if not os.path.exists(root_path) or not os.path.exists(scenes_dir):
        return "Skip cleanup: Required paths not found."

    # Ask for permission before starting cleanup logic
    if not db.ask_permission("cleanup_project", "unused scene files"):
        return "Error: Project cleanup was denied by the user."

    with open(root_path, 'r', encoding='utf-8') as f:
        root_content = f.read()

    os.makedirs(archive_dir, exist_ok=True)
    count = 0
    for fn in os.listdir(scenes_dir):
        if fn.endswith(".tsx") and os.path.splitext(fn)[0] not in root_content:
            shutil.move(os.path.join(scenes_dir, fn), os.path.join(archive_dir, fn))
            count += 1
            
    return f"Cleanup complete. Archived {count} unused files."