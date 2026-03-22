import os
from dotenv import load_dotenv

# Load local environment variables from .env
load_dotenv()

# =============================================================================
# BRANDING & VERSION METADATA
# =============================================================================
APP_NAME = "RemoQwen-MCP"
VERSION = "v7.0"
CODENAME = "REMOTE COMMANDER"
THEME_COLOR = "magenta" # Standard color for high compatibility

# =============================================================================
# OPERATIONAL MODES
# =============================================================================
MODE_FULLY_AUTO = "Fully Autonomous (Speedster)"
MODE_BALANCED = "Guarded Network (Professional)"
MODE_STRICT = "Strict Manual (Architect)"

SELECTED_MODE = MODE_BALANCED 

# =============================================================================
# TELEGRAM REMOTE GATEWAY SETTINGS
# =============================================================================
TELEGRAM_ENABLED = False
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
AUTHORIZED_CHAT_ID = os.getenv("AUTHORIZED_CHAT_ID")

# Core Paths - Initialized as empty, populated by refresh_env()
PROJECT_ROOT = ""
SRC_DIR = ""
PUBLIC_DIR = ""
SKILLS_DIR = ""
MEMORY_FILE = ""
REMOTE_TASK_FILE = ""

def refresh_env():
    """
    DYNAMIC RELOADER: Synchronizes all project paths with the .env file.
    Ensures that file operations and asset ingestion always hit the 
    correct directories even if settings change mid-session.
    """
    global TELEGRAM_TOKEN, AUTHORIZED_CHAT_ID, PROJECT_ROOT, SRC_DIR, \
           PUBLIC_DIR, SKILLS_DIR, MEMORY_FILE, REMOTE_TASK_FILE
    
    load_dotenv(override=True)
    
    # Reload Credentials
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    AUTHORIZED_CHAT_ID = os.getenv("AUTHORIZED_CHAT_ID")
    
    # Resolve the absolute path to the Remotion Project
    PROJECT_ROOT = os.path.normpath(
        os.getenv("REMOTION_PROJECT_PATH", 
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "my-video")))
    )
    
    # Synchronize sub-directories
    SRC_DIR = os.path.join(PROJECT_ROOT, "src")
    PUBLIC_DIR = os.path.join(PROJECT_ROOT, "public")
    SKILLS_DIR = os.path.join(PROJECT_ROOT, ".qwen", "skills", "remotion-best-practices")
    MEMORY_FILE = os.path.join(PROJECT_ROOT, "memory.md")
    
    # Task bridge file for Telegram->AI communication
    REMOTE_TASK_FILE = os.path.join(SRC_DIR, "remote_task.md")

# Run an immediate sync on startup
refresh_env()

# =============================================================================
# SHELL SECURITY & LOGIC GUARD
# =============================================================================
ALLOWED_COMMANDS = ["npm", "npx", "node", "remotion"]
COMMAND_TIMEOUT = 600  # 10 Minutes for heavy video rendering tasks
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
    """
    Path Guard: Strictly ensures the AI cannot access files outside PROJECT_ROOT.
    Essential for secure autonomous operation.
    """
    try:
        absolute_path = os.path.abspath(os.path.join(PROJECT_ROOT, relative_path))
        if os.path.commonpath([absolute_path, PROJECT_ROOT]) == PROJECT_ROOT:
            return absolute_path
        raise PermissionError(f"Security Violation: Access denied to {relative_path}")
    except Exception:
        raise PermissionError("Path validation failed. Access denied.")

# Environmental readiness check
PROJECT_EXISTS = os.path.exists(PROJECT_ROOT)