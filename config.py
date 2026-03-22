import os
import re
from dotenv import load_dotenv

# Load local environment variables from .env
load_dotenv()

# =============================================================================
# BRANDING & VERSION METADATA (v8.0 STABLE)
# =============================================================================
APP_NAME = "RemoQwen-MCP"
VERSION = "v8.0"
CODENAME = "ETERNAL WATCHER (STABLE)"
THEME_COLOR = "magenta"

# =============================================================================
# OPERATION MODES DEFINITION (CRITICAL: Fixed Missing Constants)
# =============================================================================
MODE_FULLY_AUTO = "Fully Autonomous (Speedster)"
MODE_BALANCED = "Guarded Network (Professional)"
MODE_STRICT = "Strict Manual (Architect)"

# Global state for current session mode (Defaults to Balanced)
SELECTED_MODE = MODE_BALANCED 

# =============================================================================
# REACTIVE POLLING CONFIGURATION (v8.0 Persistence)
# =============================================================================
# The signal string sent to AI to indicate 'No new task yet, keep waiting'.
IDLE_SIGNAL = "STATUS_IDLE_NO_TASK"

# Recommended wait time for AI between polls in seconds
AI_POLL_DELAY = 5 

# =============================================================================
# TELEGRAM GATEWAY SETTINGS
# =============================================================================
TELEGRAM_ENABLED = False
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
AUTHORIZED_CHAT_ID = os.getenv("AUTHORIZED_CHAT_ID")

# Dynamic Paths - Managed by refresh_env()
PROJECT_ROOT = ""
SRC_DIR = ""
PUBLIC_DIR = ""
SKILLS_DIR = ""
MEMORY_FILE = ""
REMOTE_TASK_FILE = ""

def sanitize_filename(filename: str) -> str:
    """Cleans filenames for Remotion project compatibility."""
    base_name = os.path.basename(filename)
    return re.sub(r'[^a-zA-Z0-9.\-_]', '', base_name.replace(' ', '-'))

def refresh_env():
    """
    DYNAMIC RELOADER: Synchronizes all project paths with the .env file.
    Ensures the remote task bridge is mapped correctly to the current project.
    """
    global TELEGRAM_TOKEN, AUTHORIZED_CHAT_ID, PROJECT_ROOT, SRC_DIR, \
           PUBLIC_DIR, SKILLS_DIR, MEMORY_FILE, REMOTE_TASK_FILE
    
    load_dotenv(override=True)
    
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    AUTHORIZED_CHAT_ID = os.getenv("AUTHORIZED_CHAT_ID")
    
    # Path Resolution from .env
    PROJECT_ROOT = os.path.normpath(
        os.getenv("REMOTION_PROJECT_PATH", 
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "my-video")))
    )
    
    SRC_DIR = os.path.join(PROJECT_ROOT, "src")
    PUBLIC_DIR = os.path.join(PROJECT_ROOT, "public")
    SKILLS_DIR = os.path.join(PROJECT_ROOT, ".qwen", "skills", "remotion-best-practices")
    MEMORY_FILE = os.path.join(PROJECT_ROOT, "memory.md")
    REMOTE_TASK_FILE = os.path.join(SRC_DIR, "remote_task.md")

# Initialize and lock paths on startup
refresh_env()

# =============================================================================
# SHELL SECURITY & SENTINEL LION GUARD
# =============================================================================
ALLOWED_COMMANDS = ["npm", "npx", "node", "remotion"]
COMMAND_TIMEOUT = 600 # 10 Minutes
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
    """Strict security jail to keep the AI within the PROJECT_ROOT."""
    try:
        absolute_path = os.path.abspath(os.path.join(PROJECT_ROOT, relative_path))
        if os.path.commonpath([absolute_path, PROJECT_ROOT]) == PROJECT_ROOT:
            return absolute_path
        raise PermissionError(f"Access Denied: {relative_path} is outside boundary.")
    except Exception:
        raise PermissionError("Path validation failed. Access Denied.")

PROJECT_EXISTS = os.path.exists(PROJECT_ROOT)