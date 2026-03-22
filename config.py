import os
import re
from dotenv import load_dotenv

# Load local environment variables
load_dotenv()

# =============================================================================
# BRANDING & VERSION METADATA (v7.1 Update)
# =============================================================================
APP_NAME = "RemoQwen-MCP"
VERSION = "v7.1"
CODENAME = "ASSET COMMANDER"
THEME_COLOR = "magenta"

# =============================================================================
# OPERATIONAL MODES
# =============================================================================
MODE_FULLY_AUTO = "Fully Autonomous (Speedster)"
MODE_BALANCED = "Guarded Network (Professional)"
MODE_STRICT = "Strict Manual (Architect)"

SELECTED_MODE = MODE_BALANCED 

# =============================================================================
# TELEGRAM GATEWAY SETTINGS
# =============================================================================
TELEGRAM_ENABLED = False
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
AUTHORIZED_CHAT_ID = os.getenv("AUTHORIZED_CHAT_ID")

# Dynamic Paths
PROJECT_ROOT = ""
SRC_DIR = ""
PUBLIC_DIR = ""
SKILLS_DIR = ""
MEMORY_FILE = ""
REMOTE_TASK_FILE = ""

def sanitize_filename(filename: str) -> str:
    """
    Cleans the user-provided filename from Telegram captions.
    Removes illegal characters and spaces to ensure Remotion compatibility.
    """
    # Remove any path traversal attempts and keep only name + extension
    base_name = os.path.basename(filename)
    # Replace spaces with hyphens and remove non-alphanumeric chars (except . and -)
    clean_name = re.sub(r'[^a-zA-Z0-9.\-_]', '', base_name.replace(' ', '-'))
    return clean_name

def refresh_env():
    """Synchronizes environment variables and project sub-directories."""
    global TELEGRAM_TOKEN, AUTHORIZED_CHAT_ID, PROJECT_ROOT, SRC_DIR, \
           PUBLIC_DIR, SKILLS_DIR, MEMORY_FILE, REMOTE_TASK_FILE
    
    load_dotenv(override=True)
    
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    AUTHORIZED_CHAT_ID = os.getenv("AUTHORIZED_CHAT_ID")
    
    PROJECT_ROOT = os.path.normpath(
        os.getenv("REMOTION_PROJECT_PATH", 
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "my-video")))
    )
    
    SRC_DIR = os.path.join(PROJECT_ROOT, "src")
    PUBLIC_DIR = os.path.join(PROJECT_ROOT, "public")
    SKILLS_DIR = os.path.join(PROJECT_ROOT, ".qwen", "skills", "remotion-best-practices")
    MEMORY_FILE = os.path.join(PROJECT_ROOT, "memory.md")
    REMOTE_TASK_FILE = os.path.join(SRC_DIR, "remote_task.md")

# Run immediate sync
refresh_env()

# =============================================================================
# SHELL & COMMAND SECURITY
# =============================================================================
ALLOWED_COMMANDS = ["npm", "npx", "node", "remotion"]
COMMAND_TIMEOUT = 600 
PREVIEW_SCAN_DURATION = 15 

# Sentinel Lion Hunting Parameters
DEEP_SCAN_POINTS = 5
REMOTION_LOG_LEVEL = "--log=verbose"
ERROR_KEYWORDS = [
    "ERROR", "Failed to compile", "SyntaxError", "Module not found", 
    "mismatch", "TypeError", "ReferenceError", "Invariant Violation",
    "must have the same length"
]

# =============================================================================
# SECURITY JAIL & VALIDATION
# =============================================================================
def validate_path(relative_path: str) -> str:
    """Strictly ensures the AI stays inside the user's PROJECT_ROOT."""
    try:
        absolute_path = os.path.abspath(os.path.join(PROJECT_ROOT, relative_path))
        if os.path.commonpath([absolute_path, PROJECT_ROOT]) == PROJECT_ROOT:
            return absolute_path
        raise PermissionError(f"Security Violation: Access denied to {relative_path}")
    except Exception:
        raise PermissionError("Path validation failed. Access denied.")

PROJECT_EXISTS = os.path.exists(PROJECT_ROOT)