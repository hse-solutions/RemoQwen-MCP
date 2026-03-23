import logging
import os
import asyncio
import hashlib
import uuid
from mcp.server import Server
from mcp.types import Tool, TextContent

import src.tools.file_ops as file_ops
import src.tools.memory_ops as memory_ops
import src.tools.asset_ops as asset_ops
import src.tools.shell_ops as shell_ops 
import src.tools.remote_ops as remote_ops 

from src.ui.dashboard import db
import config

LAST_TASK_HASH = ""
LAST_TASK_CONTENT = ""

# Background verification tasks storage
_verification_tasks = {}   # task_id -> {"status": "pending/running/completed/failed", "result": None or str, "error": None or str}

server = Server(config.APP_NAME)

async def _run_verification(task_id: str):
    """Background task that runs the actual verification."""
    try:
        _verification_tasks[task_id]["status"] = "running"
        result = await shell_ops.verify_runtime_logic()
        _verification_tasks[task_id]["status"] = "completed"
        _verification_tasks[task_id]["result"] = result
        db.log("SUCCESS", f"Background verification {task_id} completed.")
    except Exception as e:
        _verification_tasks[task_id]["status"] = "failed"
        _verification_tasks[task_id]["error"] = str(e)
        db.log("ERROR", f"Background verification {task_id} failed: {e}")

@server.list_tools()
async def handle_list_tools():
    db.log("SERVER", "AI Engineer is synchronizing v8.0 Stable toolset...")
    
    return [
        Tool(
            name="initialize_task",
            description=(
                "MANDATORY STARTUP TOOL. Call this ONCE at the very beginning.\n"
                "Loads the evolutionary memory (top 20 rules), loads all skills from .agents folder,\n"
                "and synchronizes with the remote task engine (remote_task.md).\n"
                "Returns the full context (memory + skills + any initial mission).\n"
                "After receiving the context, you MUST follow the infinite loop described in the protocol."
            ),
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="list_files",
            description=(
                "Exploration tool. Lists all files and folders inside the given relative path.\n"
                "Useful to understand the project structure before reading or writing files.\n"
                "Path must be inside the project root (security enforced)."
            ),
            inputSchema={"type": "object", "properties": {"rel_path": {"type": "string", "default": "."}}}
        ),
        Tool(
            name="read_file",
            description=(
                "Knowledge acquisition tool. Reads the content of a file.\n"
                "Use this to inspect existing code, configuration, or task files.\n"
                "Path must be relative to project root (security enforced).\n"
                "Cannot read directories – will return an error."
            ),
            inputSchema={"type": "object", "properties": {"rel_path": {"type": "string"}}, "required": ["rel_path"]}
        ),
        Tool(
            name="write_file",
            description=(
                "Action tool. Writes content to a file (overwrites if exists).\n"
                "Automatically validates Remotion logic before writing:\n"
                " - Prevents relative imports from public folder (use staticFile).\n"
                " - Checks interpolate() length mismatches.\n"
                "In Strict or Balanced modes, requires user authorization via Telegram or local terminal.\n"
                "In Fully Autonomous mode, executes automatically.\n"
                "Creates parent directories if needed."
            ),
            inputSchema={"type": "object", "properties": {"rel_path": {"type": "string"}, "content": {"type": "string"}}, "required": ["rel_path", "content"]}
        ),
        Tool(
            name="run_shell_command",
            description=(
                "Terminal execution tool. Runs allowed commands only: npm, npx, node, remotion.\n"
                "Executes inside the project root directory.\n"
                "Real-time log monitoring: if error keywords are found, returns the last 15 lines of output.\n"
                "In Strict or Balanced modes, requires user authorization (Telegram or local terminal).\n"
                "In Fully Autonomous mode, executes automatically.\n"
                "Commands that hang will be terminated after 600 seconds (configurable)."
            ),
            inputSchema={"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}
        ),
        Tool(
            name="verify_rendering",
            description=(
                "**DEPRECATED – Use verify_rendering_start + verify_rendering_status instead.**\n"
                "Legacy synchronous verification. May cause MCP timeout. Do not use."
            ),
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="verify_rendering_start",
            description=(
                "Start a background verification of the entire video timeline.\n"
                "This tool returns immediately with a unique task_id.\n"
                "The actual verification (multi‑frame rendering check) runs in the background and may take several seconds to minutes.\n"
                "**How to use:**\n"
                "1. Call this tool to get a task_id.\n"
                "2. Then repeatedly call verify_rendering_status with that task_id (e.g., every 5 seconds).\n"
                "3. When status becomes 'completed', the result is ready.\n"
                "4. If status becomes 'failed', check the error message.\n"
                "This pattern avoids MCP timeouts and allows you to do other work while verification runs."
            ),
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="verify_rendering_status",
            description=(
                "Check the status of a previously started verification task.\n"
                "Provide the task_id returned by verify_rendering_start.\n"
                "Returns one of: pending, running, completed, failed.\n"
                "If completed, returns the full verification output.\n"
                "If failed, returns an error description.\n"
                "You should poll this in a loop (e.g., with 5‑second delays) until the status is completed or failed."
            ),
            inputSchema={"type": "object", "properties": {"task_id": {"type": "string"}}, "required": ["task_id"]}
        ),
        Tool(
            name="download_asset",
            description=(
                "Download an image or file from a URL and save it to the public/ folder.\n"
                "The filename is sanitized to avoid special characters.\n"
                "In Strict or Balanced modes, requires user authorization (Telegram or local terminal).\n"
                "In Fully Autonomous mode, executes automatically.\n"
                "After download, the asset is ready to be used in Remotion via staticFile()."
            ),
            inputSchema={"type": "object", "properties": {"url": {"type": "string"}, "filename": {"type": "string"}}, "required": ["url", "filename"]}
        ),
        Tool(
            name="cleanup_project",
            description=(
                "Sanitization tool. Archives unused scene files to the /archive folder.\n"
                "It scans src/Root.tsx to find which scenes are used, and moves unused .tsx files from src/scenes to archive.\n"
                "In Strict or Balanced modes, requires user authorization.\n"
                "In Fully Autonomous mode, executes automatically."
            ),
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="update_memory",
            description=(
                "Evolution tool. Adds a new lesson to the AI's long‑term memory (top 20 rules).\n"
                "Use this when you learn something important about the project or Remotion.\n"
                "The memory is persistent and will be loaded in future sessions.\n"
                "Old rules are automatically trimmed when exceeding 20."
            ),
            inputSchema={"type": "object", "properties": {"lesson": {"type": "string"}}, "required": ["lesson"]}
        ),
        Tool(
            name="wait_for_next_task",
            description=(
                "REACTIVE WATCHER – the heart of the infinite loop.\n"
                "Call this tool AFTER completing any work.\n"
                "It checks the remote_task.md file for new instructions from Telegram.\n"
                "Returns:\n"
                f"  - '{config.IDLE_SIGNAL}' → no new task. You MUST wait exactly {config.AI_POLL_DELAY} seconds and call again.\n"
                "  - 'NEW MISSION DETECTED: ...' → a new mission has arrived. Process it immediately.\n"
                "  - 'TERMINATE: User ended session.' → stop all work and exit the loop.\n"
                "You are not allowed to exit the loop unless you receive TERMINATE.\n"
                "This ensures the system remains responsive to remote commands forever."
            ),
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="render_video",
            description=(
                "Render the Remotion video to MP4. The output is saved in the out/ folder.\n"
                "By default renders the composition named 'VideoComposition' – you can specify another composition_id.\n"
                "**Important:** This tool requires user authorization in Strict or Balanced modes.\n"
                "Only use it when the user explicitly requests a render via Telegram /render command.\n"
                "Do not call it autonomously without explicit permission.\n"
                "This tool runs synchronously and may take time; you will receive the output when finished."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "composition_id": {"type": "string", "description": "Composition ID to render (default: VideoComposition)"}
                }
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    global LAST_TASK_HASH, LAST_TASK_CONTENT
    
    try:
        # ---- argument validation ----
        if name == "read_file" and "rel_path" not in arguments:
            return [TextContent(type="text", text="Error: missing 'rel_path' argument")]
        if name == "write_file":
            if "rel_path" not in arguments:
                return [TextContent(type="text", text="Error: missing 'rel_path' argument")]
            if "content" not in arguments:
                return [TextContent(type="text", text="Error: missing 'content' argument")]
        if name == "run_shell_command" and "command" not in arguments:
            return [TextContent(type="text", text="Error: missing 'command' argument")]
        if name == "download_asset":
            if "url" not in arguments:
                return [TextContent(type="text", text="Error: missing 'url' argument")]
            if "filename" not in arguments:
                return [TextContent(type="text", text="Error: missing 'filename' argument")]
        if name == "update_memory" and "lesson" not in arguments:
            return [TextContent(type="text", text="Error: missing 'lesson' argument")]
        if name == "verify_rendering_status" and "task_id" not in arguments:
            return [TextContent(type="text", text="Error: missing 'task_id' argument")]

        if name == "initialize_task":
            db.log("CONTEXT", "Generating v8.0 autonomous brain context...")
            base_context = memory_ops.get_autonomous_context()
            remote_instructions = ""
            
            if os.path.exists(config.REMOTE_TASK_FILE):
                try:
                    with open(config.REMOTE_TASK_FILE, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            remote_instructions = f"\n\n🚨 [REMOTE MISSION]:\n{content}"
                            LAST_TASK_HASH = hashlib.md5(content.encode()).hexdigest()
                            LAST_TASK_CONTENT = content
                            db.log("REMOTE", "Initial mission synchronized.")
                except Exception as e:
                    db.log("ERROR", f"Initial sync failed: {e}")

            res = str(base_context) + str(remote_instructions)
            res += (
                "\n\n### 🧠 v8.0 ENHANCED OPERATIONAL PROTOCOL ###\n\n"
                "1. **STARTUP**: You are the autonomous Remotion engineer. "
                "Read the memory and skills above. "
                "If a remote mission exists (in remote_task.md), execute it first.\n\n"
                "2. **CORE LOOP (NEVER BREAK)**: After completing any work, you MUST call `wait_for_next_task`.\n"
                "   - If it returns `STATUS_IDLE_NO_TASK`, wait exactly 5 seconds and call it again.\n"
                "   - If it returns `NEW MISSION DETECTED`, process that mission immediately.\n"
                "   - If it returns `TERMINATE: User ended session`, stop all work and exit.\n"
                "   - NEVER exit the loop unless you receive `TERMINATE`.\n\n"
                "3. **AVAILABLE TOOLS** (use as needed):\n"
                "   - `list_files`, `read_file`, `write_file`\n"
                "   - `run_shell_command` (requires permission in Strict/Balanced modes)\n"
                "   - `verify_rendering_start` – start background verification (returns task_id). Then poll `verify_rendering_status` until 'completed' or 'failed'.\n"
                "   - `download_asset` – downloads assets to public folder\n"
                "   - `cleanup_project` – archives unused scenes\n"
                "   - `update_memory` – save important lessons (max 20 rules)\n"
                "   - `render_video` – render final video to MP4 (requires permission in Strict/Balanced modes)\n"
                "   - `wait_for_next_task` – ALWAYS call this at the end\n\n"
                "4. **MISSION PROCESSING**:\n"
                "   - Read `src/remote_task.md` to get the user's mission.\n"
                "   - Write code, run tests, fix errors.\n"
                "   - **VERIFICATION**: Use `verify_rendering_start` to start timeline verification. Then in a loop: `verify_rendering_status` with the task_id. Wait a few seconds between polls. When status is 'completed', read the result. If 'failed', handle error. This avoids timeout issues.\n"
                "   - When rendering, use `render_video` with composition ID.\n\n"
                "5. **PERMISSIONS**:\n"
                "   - In Strict/Balanced modes, sensitive actions require user approval.\n"
                "   - The system handles permission requests; you just await the result.\n"
                "   - In Fully Autonomous mode, all actions execute automatically.\n\n"
                "6. **REMOTE CONTROL**:\n"
                "   - User can send tasks via Telegram at any time.\n"
                "   - Commands: `/show_public`, `/show_out`, `/assets`, `/delete`, `/render`.\n\n"
                "7. **CRITICAL**: Never block the dispatcher. Always return immediately from tool calls.\n"
                "   - Your loop: `call wait_for_next_task` → process if mission → repeat.\n"
                "   - DO NOT exit without user's explicit `STOP` command.\n\n"
                "8. **GOOD LUCK**. You are the Eternal Watcher. Keep the mission going forever."
            )
            return [TextContent(type="text", text=res)]

        elif name == "wait_for_next_task":
            if os.path.exists(config.REMOTE_TASK_FILE):
                try:
                    with open(config.REMOTE_TASK_FILE, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            if content.upper() == "STOP_WORK":
                                db.log("SERVER", "Manual exit signal received.")
                                if LAST_TASK_CONTENT:
                                    summary = f"Session ended by user. Last mission: {LAST_TASK_CONTENT[:150]}"
                                    memory_ops.update_memory(summary)
                                else:
                                    memory_ops.update_memory("Session terminated by user. (STOP command received)")
                                return [TextContent(type="text", text="TERMINATE: User ended session.")]
                            
                            new_hash = hashlib.md5(content.encode()).hexdigest()
                            if new_hash != LAST_TASK_HASH:
                                LAST_TASK_HASH = new_hash
                                LAST_TASK_CONTENT = content
                                db.log("REMOTE", "New instruction caught! Waking up AI.")
                                return [TextContent(type="text", text=f"NEW MISSION DETECTED:\n{content}")]
                except Exception:
                    pass

            return [TextContent(type="text", text=config.IDLE_SIGNAL)]

        elif name == "list_files":
            res = await file_ops.list_project_files(arguments.get("rel_path", "."))
        elif name == "read_file":
            res = await file_ops.read_project_file(arguments["rel_path"])
        elif name == "write_file":
            await remote_ops.RemoteCommander.send_notification(f"✍️ AI is writing: {arguments['rel_path']}")
            res = await file_ops.write_project_file(arguments["rel_path"], arguments["content"])
        elif name == "run_shell_command":
            res = await shell_ops.run_command_async(arguments["command"])
        elif name == "verify_rendering":
            db.log("SERVER", "Legacy verify_rendering called (synchronous). Use verify_rendering_start instead.")
            res = await shell_ops.verify_runtime_logic()
        elif name == "verify_rendering_start":
            task_id = uuid.uuid4().hex
            _verification_tasks[task_id] = {"status": "pending", "result": None, "error": None}
            asyncio.create_task(_run_verification(task_id))
            db.log("SERVER", f"Background verification started with task_id: {task_id}")
            return [TextContent(type="text", text=f"Verification started. Task ID: {task_id}")]
        elif name == "verify_rendering_status":
            task_id = arguments["task_id"]
            if task_id not in _verification_tasks:
                return [TextContent(type="text", text=f"Error: Task ID {task_id} not found.")]
            task = _verification_tasks[task_id]
            if task["status"] == "completed":
                return [TextContent(type="text", text=f"Status: completed\nResult: {task['result']}")]
            elif task["status"] == "failed":
                return [TextContent(type="text", text=f"Status: failed\nError: {task['error']}")]
            else:
                return [TextContent(type="text", text=f"Status: {task['status']}")]
        elif name == "download_asset":
            res = await asset_ops.download_asset(arguments["url"], arguments["filename"])
        elif name == "cleanup_project":
            res = await file_ops.archive_unused_files()
        elif name == "update_memory":
            res = memory_ops.update_memory(arguments["lesson"])
        elif name == "render_video":
            comp_id = arguments.get("composition_id", "VideoComposition")
            if config.SELECTED_MODE in (config.MODE_STRICT, config.MODE_BALANCED):
                if not await remote_ops.RemoteCommander.ask_hybrid_permission("render_video", comp_id):
                    return [TextContent(type="text", text="Error: Render was denied by the user.")]
            else:
                db.log("EXEC", f"Autonomous render requested for composition: {comp_id}")
            db.log("EXEC", f"Starting video render for composition: {comp_id}")
            render_cmd = f"npx remotion render src/index.ts {comp_id}"
            result = await shell_ops.run_command_async(render_cmd)
            if "CRITICAL ERROR" in result or "Error" in result:
                await remote_ops.RemoteCommander.send_notification(f"❌ Render failed: {result[:200]}")
                res = f"Render failed: {result}"
            else:
                await remote_ops.RemoteCommander.send_notification(f"✅ Render complete! Video saved to out/ folder.")
                res = f"Render complete. Video saved to out/ folder.\n\nOutput:\n{result}"
        else:
            res = f"Error: Tool '{name}' not found."

        return [TextContent(type="text", text=str(res))]

    except Exception as e:
        db.log("ERROR", f"Dispatcher failure: {str(e)}")
        return [TextContent(type="text", text=f"Critical Dispatcher Error: {str(e)}")]