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
    Exposes the v7.0 toolset with highly detailed descriptions.
    Tuned for maximum AI reasoning and autonomous error correction.
    """
    db.log("SERVER", "AI Engineer is synchronizing v7.0 Remote toolset...")
    
    return [
        Tool(
            name="initialize_task",
            description=(
                "MANDATORY FIRST STEP: Loads memory, skills, and project state. "
                "Also checks for REMOTE MISSIONS sent from the user's phone via Telegram. "
                "ALWAYS call this before starting any task."
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
            description="Knowledge Acquisition: Reads content of any code or doc file.",
            inputSchema={"type": "object", "properties": {"rel_path": {"type": "string"}}, "required": ["rel_path"]}
        ),
        Tool(
            name="write_file",
            description=(
                "Action: Writes code with auto-validation for Remotion best practices. "
                "Requires explicit user authorization (Y/n) from phone or terminal."
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
            inputSchema={
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"]
            }
        ),
        Tool(
            name="verify_rendering",
            description="SENTINEL LION HUNT: Headless deep scan of the timeline to catch browser-only crashes.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="download_asset",
            description=(
                "Branding Gateway: Downloads images/logos to public/ folder. "
                "Requires explicit user authorization from phone or terminal."
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
            description="Sanitization: Archives unused scenes to keep the project professional.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="update_memory",
            description="Evolutionary Step: Saves mission findings to Top 20 memory rules.",
            inputSchema={"type": "object", "properties": {"lesson": {"type": "string"}}, "required": ["lesson"]}
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    """
    v7.0 Master Dispatcher: Orchestrates local and remote autonomous interactions.
    Now fully asynchronous to maintain the Immortal SSE connection.
    """
    try:
        if name == "initialize_task":
            db.log("CONTEXT", "Generating full autonomous context...")
            base_context = memory_ops.get_autonomous_context()
            
            # Atomic Remote Task Injection
            remote_instructions = ""
            if os.path.exists(config.REMOTE_TASK_FILE):
                try:
                    with open(config.REMOTE_TASK_FILE, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            remote_instructions = f"\n\n🚨 [REMOTE MISSION RECEIVED]:\n{content}\n\nACTION: Prioritize this phone request."
                            db.log("REMOTE", "Injected instructions from phone into AI brain.")
                            # Clear the file after read to prevent repeat tasks
                            with open(config.REMOTE_TASK_FILE, 'w', encoding='utf-8') as f_clear:
                                f_clear.write("")
                except Exception as e:
                    db.log("ERROR", f"Remote sync failed: {e}")

            res = base_context + remote_instructions
            db.log("SUCCESS", "Sentinel brain is synchronized.")

        elif name == "list_files":
            res = file_ops.list_project_files(arguments.get("rel_path", "."))

        elif name == "read_file":
            res = file_ops.read_project_file(arguments["rel_path"])

        elif name == "write_file":
            # FIXED: Now awaiting the async write process with hybrid authorization
            await remote_ops.RemoteCommander.send_notification(f"✍️ AI is attempting to write: {arguments['rel_path']}")
            res = await file_ops.write_project_file(arguments["rel_path"], arguments["content"])
            
            if "CRITICAL ERROR" in res:
                db.log("GUARD", "Validation failed. AI must fix code.", style="bold red")
            else:
                db.log("SUCCESS", f"File saved: {arguments['rel_path']}")

        elif name == "run_shell_command":
            db.log("EXEC", f"Terminal Strike: {arguments['command']}")
            res = await shell_ops.run_command_async(arguments["command"])

        elif name == "verify_rendering":
            # Execute the Predator hunt
            res = await shell_ops.verify_runtime_logic()
            status_msg = "✅ CLEAN" if "Success" in res else "❌ CRASHED"
            await remote_ops.RemoteCommander.send_notification(f"🦁 Hunt Result: {status_msg}")

        elif name == "download_asset":
            # FIXED: Now awaiting the async download with hybrid authorization
            await remote_ops.RemoteCommander.send_notification("📥 AI is requesting branding assets.")
            res = await asset_ops.download_asset(arguments["url"], arguments["filename"])

        elif name == "cleanup_project":
            # FIXED: Now awaiting async sanitization
            res = await file_ops.archive_unused_files()
            await remote_ops.RemoteCommander.send_notification("🧹 Project sanitized.")

        elif name == "update_memory":
            res = memory_ops.update_memory(arguments["lesson"])
            db.log("SUCCESS", "Mission findings committed to evolutionary memory.")
            await remote_ops.RemoteCommander.send_notification("💾 Mission Complete. Memory evolved.")

        else:
            res = f"Error: Tool '{name}' not found."

        return [TextContent(type="text", text=res)]

    except Exception as e:
        db.log("ERROR", f"Dispatcher failure: {str(e)}")
        return [TextContent(type="text", text=f"Critical Error: {str(e)}")]