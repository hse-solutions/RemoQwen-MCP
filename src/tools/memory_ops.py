import os
import config
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
    
    db.log("MEMORY", f"Learned: {new_lesson[:50]}... (total rules: {len(rules)})")
    return f"Memory evolved. Total rules: {len(rules)}"

def get_autonomous_context():
    memory = recall_memory()
    skills = ""
    
    # Load all .md files from .agents folder recursively
    if os.path.exists(config.SKILLS_DIR):
        for root, dirs, files in os.walk(config.SKILLS_DIR):
            for f in files:
                if f.endswith('.md'):
                    file_path = os.path.join(root, f)
                    rel_path = os.path.relpath(file_path, config.SKILLS_DIR)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as sf:
                            skills += f"\n### {rel_path} ###\n{sf.read()}\n"
                    except Exception as e:
                        db.log("ERROR", f"Failed to read skill file {rel_path}: {e}")
    
    return f"### CONTEXT ###\nRULES:\n{memory}\n\nSKILLS:\n{skills}"