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

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
# Mapping for numeric levels (used in dashboard.py)
LOG_LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40}
CURRENT_LOG_LEVEL = LOG_LEVELS.get(LOG_LEVEL, 20)

# =============================================================================
# PERMISSION TIMEOUT (seconds)
# =============================================================================
PERMISSION_TIMEOUT = int(os.getenv("PERMISSION_TIMEOUT", "60"))

# =============================================================================
# DYNAMIC PATHS - Managed by refresh_env()
# =============================================================================
PROJECT_ROOT = ""
SRC_DIR = ""
PUBLIC_DIR = ""
OUT_DIR = ""               # <-- NEW: for rendered videos
SKILLS_DIR = ""
MEMORY_FILE = ""
REMOTE_TASK_FILE = ""

def sanitize_filename(filename: str) -> str:
    """Cleans filenames for Remotion project compatibility."""
    base_name = os.path.basename(filename)
    clean = re.sub(r'[^a-zA-Z0-9.\-_]', '', base_name.replace(' ', '-'))
    return clean if clean else "asset"  # fallback if empty

def refresh_env():
    """
    DYNAMIC RELOADER: Synchronizes all project paths with the .env file.
    Ensures the remote task bridge is mapped correctly to the current project.
    """
    global TELEGRAM_TOKEN, AUTHORIZED_CHAT_ID, PROJECT_ROOT, SRC_DIR, \
           PUBLIC_DIR, OUT_DIR, SKILLS_DIR, MEMORY_FILE, REMOTE_TASK_FILE
    
    load_dotenv(override=True)
    
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    AUTHORIZED_CHAT_ID = os.getenv("AUTHORIZED_CHAT_ID")
    
    # Path Resolution from .env – ensure absolute path
    base_path = os.getenv("REMOTION_PROJECT_PATH",
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "my-video")))
    PROJECT_ROOT = os.path.abspath(os.path.normpath(base_path))
    
    SRC_DIR = os.path.join(PROJECT_ROOT, "src")
    PUBLIC_DIR = os.path.join(PROJECT_ROOT, "public")
    OUT_DIR = os.path.join(PROJECT_ROOT, "out")                # <-- NEW
    SKILLS_DIR = os.path.join(PROJECT_ROOT, ".qwen", "skills", "remotion-best-practices")
    MEMORY_FILE = os.path.join(PROJECT_ROOT, "memory.md")
    REMOTE_TASK_FILE = os.path.join(SRC_DIR, "remote_task.md")

# Initialize and lock paths on startup
refresh_env()

# =============================================================================
# SHELL SECURITY & SENTINEL LION GUARD
# =============================================================================
ALLOWED_COMMANDS = {"npm", "npx", "node", "remotion"}  # changed to set for O(1) lookup
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
        # Ensure the path is within PROJECT_ROOT (commonpath works for both files and dirs)
        if os.path.commonpath([absolute_path, PROJECT_ROOT]) == PROJECT_ROOT:
            return absolute_path
        raise PermissionError(f"Access Denied: {relative_path} is outside boundary.")
    except (OSError, ValueError) as e:
        raise PermissionError(f"Path validation failed: {e}")

# We no longer need PROJECT_EXISTS as a static variable; use a function if needed
# def project_exists(): return os.path.isdir(PROJECT_ROOT)