import os
import re
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# BRANDING & VERSION METADATA (v8.0 STABLE)
# =============================================================================
APP_NAME = "RemoQwen-MCP"
VERSION = "v8.0"
CODENAME = "ETERNAL WATCHER (STABLE)"
THEME_COLOR = "magenta"

# =============================================================================
# OPERATION MODES DEFINITION
# =============================================================================
MODE_FULLY_AUTO = "Fully Autonomous (Speedster)"
MODE_BALANCED = "Guarded Network (Professional)"
MODE_STRICT = "Strict Manual (Architect)"

SELECTED_MODE = MODE_BALANCED 

# =============================================================================
# REACTIVE POLLING CONFIGURATION
# =============================================================================
IDLE_SIGNAL = "STATUS_IDLE_NO_TASK"
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
LOG_LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40}
CURRENT_LOG_LEVEL = LOG_LEVELS.get(LOG_LEVEL, 20)

# =============================================================================
# PERMISSION TIMEOUT (seconds)
# =============================================================================
PERMISSION_TIMEOUT = int(os.getenv("PERMISSION_TIMEOUT", "60"))

# =============================================================================
# VERIFICATION TIMEOUT (seconds) - for verify_rendering total execution
# =============================================================================
VERIFY_RENDERING_TIMEOUT = 45  # Must be less than MCP tool timeout

# =============================================================================
# DYNAMIC PATHS - Managed by refresh_env()
# =============================================================================
PROJECT_ROOT = ""
SRC_DIR = ""
PUBLIC_DIR = ""
OUT_DIR = ""
SKILLS_DIR = ""
MEMORY_FILE = ""
REMOTE_TASK_FILE = ""

def sanitize_filename(filename: str) -> str:
    base_name = os.path.basename(filename)
    clean = re.sub(r'[^a-zA-Z0-9.\-_]', '', base_name.replace(' ', '-'))
    return clean if clean else "asset"

def refresh_env():
    global TELEGRAM_TOKEN, AUTHORIZED_CHAT_ID, PROJECT_ROOT, SRC_DIR, \
           PUBLIC_DIR, OUT_DIR, SKILLS_DIR, MEMORY_FILE, REMOTE_TASK_FILE
    
    load_dotenv(override=True)
    
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    AUTHORIZED_CHAT_ID = os.getenv("AUTHORIZED_CHAT_ID")
    
    base_path = os.getenv("REMOTION_PROJECT_PATH",
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "my-video")))
    PROJECT_ROOT = os.path.abspath(os.path.normpath(base_path))
    
    SRC_DIR = os.path.join(PROJECT_ROOT, "src")
    PUBLIC_DIR = os.path.join(PROJECT_ROOT, "public")
    OUT_DIR = os.path.join(PROJECT_ROOT, "out")
    SKILLS_DIR = os.path.join(PROJECT_ROOT, ".agents")  # Changed to .agents folder
    MEMORY_FILE = os.path.join(PROJECT_ROOT, "memory.md")
    REMOTE_TASK_FILE = os.path.join(SRC_DIR, "remote_task.md")

refresh_env()

# =============================================================================
# SHELL SECURITY & SENTINEL LION GUARD
# =============================================================================
ALLOWED_COMMANDS = {"npm", "npx", "node", "remotion"}
COMMAND_TIMEOUT = 600
PREVIEW_SCAN_DURATION = 15 

# Sentinel Lion Hunting Parameters
DEEP_SCAN_POINTS = 3  # Reduced from 5 to avoid timeout
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
    try:
        absolute_path = os.path.abspath(os.path.join(PROJECT_ROOT, relative_path))
        if os.path.commonpath([absolute_path, PROJECT_ROOT]) == PROJECT_ROOT:
            return absolute_path
        raise PermissionError(f"Access Denied: {relative_path} is outside boundary.")
    except (OSError, ValueError) as e:
        raise PermissionError(f"Path validation failed: {e}")