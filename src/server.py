import logging
import os
import asyncio
import hashlib
from mcp.server import Server
from mcp.types import Tool, TextContent

# Importing the v8.0 High-Performance Modular Tools
import src.tools.file_ops as file_ops
import src.tools.memory_ops as memory_ops
import src.tools.asset_ops as asset_ops
import src.tools.shell_ops as shell_ops 
import src.tools.remote_ops as remote_ops 

# Global dashboard and config sync
from src.ui.dashboard import db
import config

# Global state to prevent duplicate mission execution
LAST_TASK_HASH = ""

# Initialize the MCP Server (v8.0: Eternal Watcher Stable)
server = Server(config.APP_NAME)

@server.list_tools()
async def handle_list_tools():
    """
    Exposes the v8.0 toolset.
    Optimized for Reactive Polling to prevent dispatcher blocking.
    """
    db.log("SERVER", "AI Engineer is synchronizing v8.0 Stable toolset...")
    
    return [
        Tool(
            name="initialize_task",
            description=(
                "MANDATORY START: Loads evolutionary memory, documentation skills, "
                "and synchronizes with the Remote Task engine. NEVER skip this."
            ),
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="list_files",
            description="Exploration: Lists project files to understand structure.",
            inputSchema={"type": "object", "properties": {"rel_path": {"type": "string"}}}
        ),
        Tool(
            name="read_file",
            description="Knowledge Acquisition: Reads any code or documentation file.",
            inputSchema={"type": "object", "properties": {"rel_path": {"type": "string"}}, "required": ["rel_path"]}
        ),
        Tool(
            name="write_file",
            description="Action: Writes code with auto-validation. Requires Authorization.",
            inputSchema={"type": "object", "properties": {"rel_path": {"type": "string"}, "content": {"type": "string"}}, "required": ["rel_path", "content"]}
        ),
        Tool(
            name="run_shell_command",
            description="Terminal Strike: Runs npm/npx commands with real-time monitoring.",
            inputSchema={"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}
        ),
        Tool(
            name="verify_rendering",
            description="SENTINEL LION HUNT: Headless deep-scan for browser-level crashes.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="download_asset",
            description="Asset Commander: Downloads images/logos. Requires Authorization.",
            inputSchema={"type": "object", "properties": {"url": {"type": "string"}, "filename": {"type": "string"}}, "required": ["url", "filename"]}
        ),
        Tool(
            name="cleanup_project",
            description="Sanitization: Archives unused scenes to keep project clean.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="update_memory",
            description="Evolution: Commits findings to the Top 20 rules.",
            inputSchema={"type": "object", "properties": {"lesson": {"type": "string"}}, "required": ["lesson"]}
        ),
        Tool(
            name="wait_for_next_task",
            description=(
                "REACTIVE WATCHER: Call this to check for new phone instructions. "
                "If it returns 'STATUS_IDLE_NO_TASK', you MUST wait exactly 5 seconds and call it again. "
                "This ensures you are always responsive to other tools like read/write."
            ),
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    """
    v8.0 Master Dispatcher: Implements Instant-Response Polling.
    This prevents dispatcher-level timeouts and tool-unresponsiveness.
    """
    global LAST_TASK_HASH
    
    try:
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
                            db.log("REMOTE", "Initial mission synchronized.")
                except Exception as e:
                    db.log("ERROR", f"Initial sync failed: {e}")

            res = str(base_context) + str(remote_instructions)
            
            # v8.0 STABLE RECURSIVE PROTOCOL
            res += (
                f"\n\n### v8.0 STABLE OPERATIONAL PROTOCOL ###\n"
                f"1. You are a Reactive Agent. NEVER block the dispatcher loop.\n"
                f"2. After each task, call wait_for_next_task.\n"
                f"3. If wait_for_next_task returns '{config.IDLE_SIGNAL}', you MUST:\n"
                f"   - State: 'No new mission yet. Sleeping for {config.AI_POLL_DELAY}s...'\n"
                f"   - WAIT for exactly {config.AI_POLL_DELAY} seconds.\n"
                f"   - CALL wait_for_next_task again.\n"
                f"4. This protocol prevents timeouts and keeps you 100% responsive."
            )
            return [TextContent(type="text", text=res)]

        elif name == "wait_for_next_task":
            # INSTANT RESPONSE LOGIC: Check once and return immediately.
            # This keeps the server thread free for other tool calls (read/write).
            if os.path.exists(config.REMOTE_TASK_FILE):
                try:
                    with open(config.REMOTE_TASK_FILE, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            # 1. Check for Termination Signal
                            if content.upper() == "STOP_WORK":
                                db.log("SERVER", "Manual exit signal received.")
                                return [TextContent(type="text", text="TERMINATE: User ended session.")]
                            
                            # 2. Check if a NEW task is available
                            new_hash = hashlib.md5(content.encode()).hexdigest()
                            if new_hash != LAST_TASK_HASH:
                                LAST_TASK_HASH = new_hash
                                db.log("REMOTE", "New instruction caught! Waking up AI.")
                                return [TextContent(type="text", text=f"NEW MISSION DETECTED:\n{content}")]
                except: pass

            # 3. No new task? Return IDLE immediately (Non-blocking)
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
            res = await shell_ops.verify_runtime_logic()
        elif name == "download_asset":
            res = await asset_ops.download_asset(arguments["url"], arguments["filename"])
        elif name == "cleanup_project":
            res = await file_ops.archive_unused_files()
        elif name == "update_memory":
            res = memory_ops.update_memory(arguments["lesson"])
        else:
            res = f"Error: Tool '{name}' not found."

        return [TextContent(type="text", text=str(res))]

    except Exception as e:
        db.log("ERROR", f"Dispatcher failure: {str(e)}")
        return [TextContent(type="text", text=f"Critical Dispatcher Error: {str(e)}")]