import logging
import os
import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent

# Importing modular tools
import src.tools.file_ops as file_ops
import src.tools.memory_ops as memory_ops
import src.tools.asset_ops as asset_ops
import src.tools.shell_ops as shell_ops 
import src.tools.remote_ops as remote_ops 
from src.ui.dashboard import Dashboard as db
import config

# Initialize the MCP Server (v7.0: Remote Commander Edition)
server = Server(config.APP_NAME)

@server.list_tools()
async def handle_list_tools():
    """
    Exposes the v7.0 toolset with high-detail descriptions to guide the AI brain.
    """
    db.log("SERVER", "AI Engineer is synchronizing elite v7.0 toolset...")
    
    return [
        Tool(
            name="initialize_task",
            description="MANDATORY FIRST STEP: Synchronizes memory, skills, and checks for REMOTE MISSIONS from Telegram.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="list_files",
            description="Exploration: Lists all files in a directory to understand project structure.",
            inputSchema={"type": "object", "properties": {"rel_path": {"type": "string"}}}
        ),
        Tool(
            name="read_file",
            description="Knowledge Acquisition: Reads the full text content of any code or doc file.",
            inputSchema={"type": "object", "properties": {"rel_path": {"type": "string"}}, "required": ["rel_path"]}
        ),
        Tool(
            name="write_file",
            description="Action Engine: Creates/Updates files. Auto-validates Remotion rules. Requires User Authorization.",
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
            description="Terminal Strike: Executes npm/npx/remotion commands with real-time log monitoring.",
            inputSchema={
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"]
            }
        ),
        Tool(
            name="verify_rendering",
            description="SENTINEL LION HUNT: Headless deep-scan of 5 timeline points to catch browser-level crashes.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="download_asset",
            description="Branding Gateway: Downloads images/logos to public/ folder. Requires User Authorization.",
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
            description="Sanitization: Archives unused scene files to keep codebase professional.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="update_memory",
            description="Evolution: Saves mission findings to Top 20 evolutionary rules.",
            inputSchema={"type": "object", "properties": {"lesson": {"type": "string"}}, "required": ["lesson"]}
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    """
    v7.0 Master Dispatcher: Synchronizes local and remote operations via the Async Pipeline.
    """
    try:
        if name == "initialize_task":
            db.log("CONTEXT", "Generating full autonomous context...")
            base_context = memory_ops.get_autonomous_context()
            
            # Atomic Remote Task Injection logic
            remote_instructions = ""
            if os.path.exists(config.REMOTE_TASK_FILE):
                try:
                    with open(config.REMOTE_TASK_FILE, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            remote_instructions = f"\n\n🚨 [REMOTE MISSION RECEIVED]:\n{content}\n\nACTION: Prioritize this phone request."
                            db.log("REMOTE", "Injected instructions from phone into AI brain.")
                            # Clear task file after successful sync
                            with open(config.REMOTE_TASK_FILE, 'w', encoding='utf-8') as f_clear:
                                f_clear.write("")
                except Exception as e:
                    db.log("ERROR", f"Remote sync failed: {e}")

            res = str(base_context) + str(remote_instructions)
            db.log("SUCCESS", "Sentinel brain is synchronized.")

        elif name == "list_files":
            # FIXED: Added await to prevent Coroutine crash
            res = await file_ops.list_project_files(arguments.get("rel_path", "."))

        elif name == "read_file":
            # FIXED: Added await to ensure string return
            res = await file_ops.read_project_file(arguments["rel_path"])

        elif name == "write_file":
            await remote_ops.RemoteCommander.send_notification(f"✍️ [ACTION]: AI is writing {arguments['rel_path']}")
            res = await file_ops.write_project_file(arguments["rel_path"], arguments["content"])
            
            if "CRITICAL ERROR" in res:
                db.log("GUARD", "Local validation failed. AI must fix logic.", style="bold red")
            else:
                db.log("SUCCESS", f"File saved: {arguments['rel_path']}")

        elif name == "run_shell_command":
            db.log("EXEC", f"Terminal Strike: {arguments['command']}")
            res = await shell_ops.run_command_async(arguments["command"])

        elif name == "verify_rendering":
            res = await shell_ops.verify_runtime_logic()
            status_msg = "✅ CLEAN" if "Success" in res else "❌ CRASHED"
            await remote_ops.RemoteCommander.send_notification(f"🦁 [SENTINEL]: Hunt complete. Result: {status_msg}")

        elif name == "download_asset":
            await remote_ops.RemoteCommander.send_notification("📥 [FETCH]: AI is requesting branding assets.")
            res = await asset_ops.download_asset(arguments["url"], arguments["filename"])

        elif name == "cleanup_project":
            db.log("PREDATOR", "Cleaning unused scene components...")
            res = await file_ops.archive_unused_files()
            await remote_ops.RemoteCommander.send_notification("🧹 [CLEANUP]: Project sanitized.")

        elif name == "update_memory":
            res = memory_ops.update_memory(arguments["lesson"])
            db.log("SUCCESS", "Knowledge base evolved.")
            await remote_ops.RemoteCommander.send_notification("💾 [MEMORY]: Lesson committed. Mission successful.")

        else:
            res = f"Error: Tool '{name}' not found."

        # Safety Check: Ensure the final result is always a string for TextContent
        return [TextContent(type="text", text=str(res))]

    except Exception as e:
        db.log("ERROR", f"Dispatcher critical crash: {str(e)}")
        return [TextContent(type="text", text=f"Critical Error: {str(e)}")]