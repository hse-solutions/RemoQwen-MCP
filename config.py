import os
from dotenv import load_dotenv

# Initial load of environment variables from .env
load_dotenv()

# =============================================================================
# BRANDING & VERSION METADATA
# =============================================================================
APP_NAME = "RemoQwen-MCP"
VERSION = "v7.0"
CODENAME = "REMOTE COMMANDER"
THEME_COLOR = "magenta" # Fixed: Standard color for maximum library compatibility

# =============================================================================
# OPERATION MODES DEFINITION
# =============================================================================
MODE_FULLY_AUTO = "Fully Autonomous (Speedster)"
MODE_BALANCED = "Guarded Network (Professional)"
MODE_STRICT = "Strict Manual (Architect)"

SELECTED_MODE = MODE_BALANCED 

# =============================================================================
# TELEGRAM REMOTE ORCHESTRATION (Dynamic State)
# =============================================================================
TELEGRAM_ENABLED = False
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
AUTHORIZED_CHAT_ID = os.getenv("AUTHORIZED_CHAT_ID")

# These will be initialized properly in the refresh_env() call below
PROJECT_ROOT = ""
SRC_DIR = ""
PUBLIC_DIR = ""
SKILLS_DIR = ""
MEMORY_FILE = ""
REMOTE_TASK_FILE = ""

def refresh_env():
    """
    DYNAMIC RELOADER: Re-reads .env and synchronizes all project paths.
    Ensures that REMOTE_TASK_FILE always points to the correct 'src' folder 
    defined in the user's REMOTION_PROJECT_PATH.
    """
    global TELEGRAM_TOKEN, AUTHORIZED_CHAT_ID, PROJECT_ROOT, SRC_DIR, \
           PUBLIC_DIR, SKILLS_DIR, MEMORY_FILE, REMOTE_TASK_FILE
    
    load_dotenv(override=True)
    
    # Update Credentials
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    AUTHORIZED_CHAT_ID = os.getenv("AUTHORIZED_CHAT_ID")
    
    # 🛡️ THE PATH FIX: Get the absolute root from .env correctly
    PROJECT_ROOT = os.path.normpath(
        os.getenv("REMOTION_PROJECT_PATH", 
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "my-video")))
    )
    
    # Initialize all sub-paths relative to the validated PROJECT_ROOT
    SRC_DIR = os.path.join(PROJECT_ROOT, "src")
    PUBLIC_DIR = os.path.join(PROJECT_ROOT, "public")
    SKILLS_DIR = os.path.join(PROJECT_ROOT, ".qwen", "skills", "remotion-best-practices")
    MEMORY_FILE = os.path.join(PROJECT_ROOT, "memory.md")
    
    # Ensure remote tasks are written into the actual project's src folder
    REMOTE_TASK_FILE = os.path.join(SRC_DIR, "remote_task.md")

# Run an immediate refresh to lock paths on startup
refresh_env()

# =============================================================================
# SHELL & COMMAND SECURITY CONFIGURATION
# =============================================================================
ALLOWED_COMMANDS = ["npm", "npx", "node", "remotion"]
COMMAND_TIMEOUT = 300 
PREVIEW_SCAN_DURATION = 15 

# =============================================================================
# SENTINEL LION: ERROR HUNTING SETTINGS (v6.0 Predator Logic)
# =============================================================================
DEEP_SCAN_POINTS = 5
REMOTION_LOG_LEVEL = "--log=verbose"
ERROR_KEYWORDS = [
    "ERROR", "Failed to compile", "SyntaxError", "Module not found", 
    "mismatch", "TypeError", "ReferenceError", "Invariant Violation",
    "must have the same length"
]

# =============================================================================
# SECURITY JAIL & PATH VALIDATION
# =============================================================================
def validate_path(relative_path: str) -> str:
    """Strictly ensures the AI stays inside the user's PROJECT_ROOT."""
    try:
        absolute_path = os.path.abspath(os.path.join(PROJECT_ROOT, relative_path))
        if os.path.commonpath([absolute_path, PROJECT_ROOT]) == PROJECT_ROOT:
            return absolute_path
        raise PermissionError(f"Security Violation: Access denied to {relative_path}")
    except Exception:
        raise PermissionError(f"Security Violation: Path validation failed.")

# Check if environment is ready
PROJECT_EXISTS = os.path.exists(PROJECT_ROOT)