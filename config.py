import os
from dotenv import load_dotenv

# Load local environment variables from a .env file
load_dotenv()

# =============================================================================
# OPERATION MODES DEFINITION (Preserved from v4.0)
# =============================================================================
MODE_FULLY_AUTO = "Fully Autonomous (Speedster)"
MODE_BALANCED = "Guarded Network (Professional)"
MODE_STRICT = "Strict Manual (Architect)"

# Global state for current session mode
SELECTED_MODE = MODE_BALANCED 

# =============================================================================
# SHELL & COMMAND SECURITY CONFIGURATION (New for v5.0)
# =============================================================================
# Strictly allow only these commands to prevent system-level damage
ALLOWED_COMMANDS = ["npm", "npx", "node", "remotion"]

# Timeouts to prevent the bridge from hanging on stuck processes
COMMAND_TIMEOUT = 60  # seconds
PREVIEW_SCAN_DURATION = 15  # seconds to monitor logs for errors

# Keywords that trigger the autonomous self-healing loop
ERROR_KEYWORDS = ["ERROR", "Failed to compile", "SyntaxError", "Module not found", "mismatch"]

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
    Logic preserved to guarantee 100% security during file operations.
    """
    try:
        absolute_path = os.path.abspath(os.path.join(PROJECT_ROOT, relative_path))
        if os.path.commonpath([absolute_path, PROJECT_ROOT]) == PROJECT_ROOT:
            return absolute_path
        raise PermissionError(f"Security Violation: Access denied to {relative_path}")
    except Exception:
        raise PermissionError(f"Security Violation: Path validation failed.")

# Global check for environment readiness
PROJECT_EXISTS = os.path.exists(PROJECT_ROOT)