import os

# ABSOLUTE PATH LOCKING
PROJECT_ROOT = os.path.normpath("D:/test/REMOTION TEST/my-video")
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
PUBLIC_DIR = os.path.join(PROJECT_ROOT, "public")
SKILLS_DIR = os.path.join(PROJECT_ROOT, ".qwen", "skills", "remotion-best-practices")
MEMORY_FILE = os.path.join(PROJECT_ROOT, "memory.md")

def validate_path(relative_path: str) -> str:
    """Ensures AI stays inside the project root."""
    absolute_path = os.path.abspath(os.path.join(PROJECT_ROOT, relative_path))
    if os.path.commonpath([absolute_path, PROJECT_ROOT]) == PROJECT_ROOT:
        return absolute_path
    raise PermissionError(f"Security Violation: Access denied to {relative_path}")