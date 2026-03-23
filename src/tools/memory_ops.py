import os
import config  # full config for dynamic access
from src.ui.dashboard import db

def recall_memory():
    if not os.path.exists(config.MEMORY_FILE):
        return "Fresh start. No learned rules yet."
    with open(config.MEMORY_FILE, 'r', encoding='utf-8') as f:
        return f.read().strip() or "Memory is empty."

def update_memory(new_lesson: str):
    rules = []
    if os.path.exists(config.MEMORY_FILE):
        with open(config.MEMORY_FILE, 'r', encoding='utf-8') as f:
            rules = [l.strip() for l in f.readlines() if l.strip().startswith("- ")]
    rules.append(f"- {new_lesson}")
    if len(rules) > 20:
        rules = rules[-20:]
    with open(config.MEMORY_FILE, 'w', encoding='utf-8') as f:
        f.write("# AI EVOLUTIONARY MEMORY (TOP 20)\n\n" + "\n".join(rules))
    
    # Log to dashboard
    db.log("MEMORY", f"Learned: {new_lesson[:50]}... (total rules: {len(rules)})")
    return f"Memory evolved. Total rules: {len(rules)}"

def get_autonomous_context():
    memory = recall_memory()
    skills = ""
    skill_path = os.path.join(config.SKILLS_DIR, "animations.md")
    if os.path.exists(skill_path):
        with open(skill_path, 'r', encoding='utf-8') as f:
            skills = f.read()
    return f"### CONTEXT ###\nRULES:\n{memory}\n\nSKILLS:\n{skills}"