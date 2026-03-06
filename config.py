import os
from dotenv import load_dotenv

# Load local environment variables from a .env file (if it exists)
load_dotenv()

# =============================================================================
# UNIVERSAL CONFIGURATION & SECURITY PATH LOCKING
# =============================================================================

# Dynamic Project Root: 
# 1. Tries to get the path from .env (REMOTION_PROJECT_PATH)
# 2. Falls back to a relative path (../my-video) if .env is missing
PROJECT_ROOT = os.path.normpath(
    os.getenv("REMOTION_PROJECT_PATH", 
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "my-video")))
)

# Core project sub-directories based on the dynamic PROJECT_ROOT
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
PUBLIC_DIR = os.path.join(PROJECT_ROOT, "public")
SKILLS_DIR = os.path.join(PROJECT_ROOT, ".qwen", "skills", "remotion-best-practices")
MEMORY_FILE = os.path.join(PROJECT_ROOT, "memory.md")

def validate_path(relative_path: str) -> str:
    """
    Security Jail: Ensures the AI strictly stays inside the PROJECT_ROOT.
    Normalizes paths to prevent Directory Traversal attacks.
    """
    try:
        absolute_path = os.path.abspath(os.path.join(PROJECT_ROOT, relative_path))
        if os.path.commonpath([absolute_path, PROJECT_ROOT]) == PROJECT_ROOT:
            return absolute_path
        raise PermissionError(f"Security Violation: Access denied to {relative_path}")
    except Exception:
        raise PermissionError(f"Security Violation: Path validation failed.")

# Feedback for the Terminal Dashboard
if not os.path.exists(PROJECT_ROOT):
    print(f"[*] WARNING: Target project NOT FOUND at: {PROJECT_ROOT}")
else:
    print(f"[*] Security jail locked to: {PROJECT_ROOT}")