import os
from dotenv import load_dotenv

# Load local environment variables from a .env file
load_dotenv()

# =============================================================================
# OPERATION MODES DEFINITION
# =============================================================================
# Mode 1: No permissions asked. Total freedom.
MODE_FULLY_AUTO = "Fully Autonomous (Speedster)"
# Mode 2: Only ask for Downloads & Commands. File edits are automatic.
MODE_BALANCED = "Guarded Network (Professional)"
# Mode 3: Ask for everything (Reads, Writes, Downloads, Cleanup).
MODE_STRICT = "Strict Manual (Architect)"

# This will hold the user's choice at runtime
SELECTED_MODE = MODE_BALANCED 

# =============================================================================
# UNIVERSAL CONFIGURATION & SECURITY PATH LOCKING
# =============================================================================

# Dynamic Project Root logic remains unchanged for reliability
PROJECT_ROOT = os.path.normpath(
    os.getenv("REMOTION_PROJECT_PATH", 
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "my-video")))
)

# Core project sub-directories
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
PUBLIC_DIR = os.path.join(PROJECT_ROOT, "public")
SKILLS_DIR = os.path.join(PROJECT_ROOT, ".qwen", "skills", "remotion-best-practices")
MEMORY_FILE = os.path.join(PROJECT_ROOT, "memory.md")

def validate_path(relative_path: str) -> str:
    """
    Security Jail: Strictly ensures the AI stays inside the PROJECT_ROOT.
    Prevents directory traversal attacks.
    """
    try:
        absolute_path = os.path.abspath(os.path.join(PROJECT_ROOT, relative_path))
        if os.path.commonpath([absolute_path, PROJECT_ROOT]) == PROJECT_ROOT:
            return absolute_path
        raise PermissionError(f"Security Violation: Access denied to {relative_path}")
    except Exception:
        raise PermissionError(f"Security Violation: Path validation failed.")

# Check if project exists (Visual feedback is now handled by the Dashboard)
PROJECT_EXISTS = os.path.exists(PROJECT_ROOT)