import os
from dotenv import load_dotenv

# Load local environment variables from a .env file
load_dotenv()

# =============================================================================
# OPERATION MODES DEFINITION (Preserved)
# =============================================================================
MODE_FULLY_AUTO = "Fully Autonomous (Speedster)"
MODE_BALANCED = "Guarded Network (Professional)"
MODE_STRICT = "Strict Manual (Architect)"

# Global state for current session mode
SELECTED_MODE = MODE_BALANCED 

# =============================================================================
# SHELL & COMMAND SECURITY CONFIGURATION
# =============================================================================
# Strictly allow only these base commands for security
ALLOWED_COMMANDS = ["npm", "npx", "node", "remotion"]

# Timeouts and Scan Durations
COMMAND_TIMEOUT = 120  # Increased for deep rendering tasks
PREVIEW_SCAN_DURATION = 15  # Monitoring window for dev server logs

# =============================================================================
# SENTINEL LION: ERROR HUNTING SETTINGS (New for v6.0)
# =============================================================================
# Number of strategic points in the timeline to probe (e.g., Start, 25%, 50%, 75%, End)
DEEP_SCAN_POINTS = 5

# Remotion verbosity flag to force browser errors into the terminal
REMOTION_LOG_LEVEL = "--log=verbose"

# Enhanced error keywords to catch React/Remotion internal crashes
ERROR_KEYWORDS = [
    "ERROR", "Failed to compile", "SyntaxError", "Module not found", 
    "mismatch", "TypeError", "ReferenceError", "Invariant Violation",
    "must have the same length"
]

# =============================================================================
# UNIVERSAL CONFIGURATION & SECURITY PATH LOCKING
# =============================================================================
PROJECT_ROOT = os.path.normpath(
    os.getenv("REMOTION_PROJECT_PATH", 
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "my-video")))
)

SRC_DIR = os.path.join(PROJECT_ROOT, "src")
PUBLIC_DIR = os.path.join(PROJECT_ROOT, "public")
SKILLS_DIR = os.path.join(PROJECT_ROOT, ".qwen", "skills", "remotion-best-practices")
MEMORY_FILE = os.path.join(PROJECT_ROOT, "memory.md")

def validate_path(relative_path: str) -> str:
    """
    Security Jail: Strictly ensures the AI stays inside the PROJECT_ROOT.
    Logic preserved to guarantee 100% security during autonomous file operations.
    """
    try:
        absolute_path = os.path.abspath(os.path.join(PROJECT_ROOT, relative_path))
        if os.path.commonpath([absolute_path, PROJECT_ROOT]) == PROJECT_ROOT:
            return absolute_path
        raise PermissionError(f"Security Violation: Access denied to {relative_path}")
    except Exception:
        raise PermissionError(f"Security Violation: Path validation failed.")

# Check if environment is ready
PROJECT_EXISTS = os.path.exists(PROJECT_ROOT)