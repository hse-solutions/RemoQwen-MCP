import logging
import os
import asyncio
import hashlib
from mcp.server import Server
from mcp.types import Tool, TextContent

# Importing the v7.1 Asynchronous Modular Tools
import src.tools.file_ops as file_ops
import src.tools.memory_ops as memory_ops
import src.tools.asset_ops as asset_ops
import src.tools.shell_ops as shell_ops 
import src.tools.remote_ops as remote_ops 

# Importing the synced dashboard instance
from src.ui.dashboard import db
import config

# Global state to prevent duplicate task execution in the loop
LAST_TASK_HASH = ""

# Initialize the MCP Server (v7.1 Asset Commander)
server = Server(config.APP_NAME)

@server.list_tools()
async def handle_list_tools():
    """
    Exposes the ultimate v7.1 toolset to the AI.
    Detailed descriptions ensure the AI follows the autonomous loop protocol.
    """
    db.log("SERVER", "AI Engineer is synchronizing v7.1 High-Detail toolset...")
    
    return [
        Tool(
            name="initialize_task",
            description=(
                "MANDATORY FIRST STEP: Loads evolutionary memory, documentation skills, "
                "and checks for initial REMOTE MISSIONS from the user's phone. "
                "ALWAYS call this before starting any logic."
            ),
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="list_files",
            description="Exploration: Lists files to understand project structure.",
            inputSchema={"type": "object", "properties": {"rel_path": {"type": "string"}}}
        ),
        Tool(
            name="read_file",
            description="Knowledge Acquisition: Reads the content of any code or doc file.",
            inputSchema={"type": "object", "properties": {"rel_path": {"type": "string"}}, "required": ["rel_path"]}
        ),
        Tool(
            name="write_file",
            description=(
                "Action Engine: Creates or updates files. Auto-validates Remotion logic. "
                "Requires user authorization (Y/n) from phone or terminal."
            ),
            inputSchema={
                "type": "object", 
                "properties": {
                    "rel_path": {"type": "string"},
                    "content": {"type": "string"}
                }, 
                "required": ["rel_path", "content"]
            }
        ),
        Tool(
            name="run_shell_command",
            description="Terminal Strike: Runs npm/npx commands with real-time log monitoring.",
            inputSchema={"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}
        ),
        Tool(
            name="verify_rendering",
            description="SENTINEL LION HUNT: Headless scan of the timeline to catch browser-level crashes.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="download_asset",
            description=(
                "Asset Commander: Downloads images/logos to public/ folder. "
                "Requires user authorization from phone or terminal."
            ),
            inputSchema={
                "type": "object", 
                "properties": {
                    "url": {"type": "string"},
                    "filename": {"type": "string"}
                }, 
                "required": ["url", "filename"]
            }
        ),
        Tool(
            name="cleanup_project",
            description="Sanitization: Archives unused scenes to keep the codebase clean.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="update_memory",
            description="Evolution: Commits mission findings to the Top 20 evolutionary rules.",
            inputSchema={"type": "object", "properties": {"lesson": {"type": "string"}}, "required": ["lesson"]}
        ),
        Tool(
            name="wait_for_next_task",
            description=(
                "ETERNAL WATCHER: Call this AFTER finishing a task. "
                "Puts you in a listening state until a NEW instruction arrives via Telegram. "
                "Returns 'TERMINATE' if the user stops the session."
            ),
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    """
    Orchestration Hub: Routes AI missions to specialized engineering tools.
    Fully asynchronous to maintain the Immortal Heartbeat and avoid loop crashes.
    """
    global LAST_TASK_HASH
    
    try:
        if name == "initialize_task":
            db.log("CONTEXT", "Initializing autonomous brain context...")
            
            # 1. Fetch Local Brain state
            base_context = memory_ops.get_autonomous_context()
            
            # 2. Check for Remote Instructions injected via Telegram
            remote_instructions = ""
            if os.path.exists(config.REMOTE_TASK_FILE):
                try:
                    with open(config.REMOTE_TASK_FILE, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            remote_instructions = f"\n\n🚨 [REMOTE MISSION RECEIVED]:\n{content}\n\nACTION: Prioritize this mission."
                            # Set initial hash to prevent immediate re-trigger in watcher
                            LAST_TASK_HASH = hashlib.md5(content.encode()).hexdigest()
                            db.log("REMOTE", "Telegram instruction synchronized.")
                except Exception as e:
                    db.log("ERROR", f"Failed to sync remote task: {e}")

            # 3. Inject Autonomous Loop Protocol
            res = str(base_context) + str(remote_instructions)
            res += (
                "\n\n### v7.1 OPERATIONAL PROTOCOL ###\n"
                "1. Read documentation and existing code logic.\n"
                "2. Execute the mission (Use staticFile for assets).\n"
                "3. Call verify_rendering to hunt for browser crashes.\n"
                "4. Call update_memory to evolve.\n"
                "5. MANDATORY: Call wait_for_next_task to await your next phone instruction."
            )
            return [TextContent(type="text", text=res)]

        elif name == "wait_for_next_task":
            db.log("THINKING", "AI is entering 'Watcher Mode'. Waiting for new phone instructions...")
            
            while True:
                if os.path.exists(config.REMOTE_TASK_FILE):
                    try:
                        with open(config.REMOTE_TASK_FILE, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                            if content:
                                # Check for Kill Switch
                                if content.upper() == "STOP_WORK":
                                    db.log("SERVER", "Manual termination received. Powering down AI.")
                                    return [TextContent(type="text", text="TERMINATE: The user has ended the session.")]
                                
                                # Check if the task content has changed
                                new_hash = hashlib.md5(content.encode()).hexdigest()
                                if new_hash != LAST_TASK_HASH:
                                    LAST_TASK_HASH = new_hash
                                    db.log("REMOTE", "New instruction detected! Waking up AI brain.")
                                    return [TextContent(type="text", text=f"NEW MISSION:\n{content}")]
                    except: pass
                
                # Non-blocking wait to keep the SSE socket and Heartbeat alive
                await asyncio.sleep(2)

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

        # Safety cast to string to ensure TextContent validation passes
        return [TextContent(type="text", text=str(res))]

    except Exception as e:
        db.log("ERROR", f"Critical Dispatcher Failure: {str(e)}")
        return [TextContent(type="text", text=f"Dispatcher Critical Error: {str(e)}")]