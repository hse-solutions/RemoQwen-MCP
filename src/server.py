import logging
import os
import asyncio
import hashlib
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

server = Server(config.APP_NAME)

@server.list_tools()
async def handle_list_tools():
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
                f"If it returns '{config.IDLE_SIGNAL}', you MUST wait exactly {config.AI_POLL_DELAY} seconds and call it again. "
                "This ensures you are always responsive to other tools like read/write."
            ),
            inputSchema={"type": "object", "properties": {}}
        ),
        # NEW: Render video tool for remote rendering
        Tool(
            name="render_video",
            description="Renders the Remotion video to MP4. Saves to out/ folder.",
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
    global LAST_TASK_HASH
    
    try:
        # ---- argument validation for tools that require it ----
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
            if os.path.exists(config.REMOTE_TASK_FILE):
                try:
                    with open(config.REMOTE_TASK_FILE, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            if content.upper() == "STOP_WORK":
                                db.log("SERVER", "Manual exit signal received.")
                                return [TextContent(type="text", text="TERMINATE: User ended session.")]
                            
                            new_hash = hashlib.md5(content.encode()).hexdigest()
                            if new_hash != LAST_TASK_HASH:
                                LAST_TASK_HASH = new_hash
                                db.log("REMOTE", "New instruction caught! Waking up AI.")
                                return [TextContent(type="text", text=f"NEW MISSION DETECTED:\n{content}")]
                except Exception:
                    pass  # silent failure, just return idle

            return [TextContent(type="text", text=config.IDLE_SIGNAL)]

        elif name == "list_files":
            res = await file_ops.list_project_files(arguments.get("rel_path", "."))
        elif name == "read_file":
            res = await file_ops.read_project_file(arguments["rel_path"])
        elif name == "write_file":
            # Send notification (async)
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
            res = memory_ops.update_memory(arguments["lesson"])  # sync, no await needed
        elif name == "render_video":
            comp_id = arguments.get("composition_id", "VideoComposition")
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