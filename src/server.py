import logging
from mcp.server import Server
from mcp.types import Tool, TextContent

# Importing the v6.0 Predator-class modular tools
import src.tools.file_ops as file_ops
import src.tools.memory_ops as memory_ops
import src.tools.asset_ops as asset_ops
import src.tools.shell_ops as shell_ops 
from src.ui.dashboard import Dashboard as db

# Initialize the MCP Server (RemoQwen-MCP v6.0: Sentinel Lion)
server = Server("RemoQwen-MCP-Sentinel-Lion")

@server.list_tools()
async def handle_list_tools():
    """
    Exposes the ultimate autonomous toolset to the AI.
    Features the v6.0 Sentinel Lion 'Hunting' capabilities.
    """
    db.log("SERVER", "AI Engineer is initializing the v6.0 SENTINEL LION toolset...")
    
    return [
        Tool(
            name="initialize_task",
            description="MANDATORY FIRST STEP: Loads your evolutionary memory, Remotion skills, and project state. Do NOT start without this.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="list_files",
            description="Explore the project structure to find components and assets.",
            inputSchema={"type": "object", "properties": {"rel_path": {"type": "string"}}}
        ),
        Tool(
            name="read_file",
            description="Read existing code or skills to understand logic and prevent repeats.",
            inputSchema={"type": "object", "properties": {"rel_path": {"type": "string"}}, "required": ["rel_path"]}
        ),
        Tool(
            name="write_file",
            description="Write/Update code. Auto-validates syntax, interpolation, and staticFile rules locally.",
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
            description="Execute terminal commands (npm, npx, remotion) with live log monitoring.",
            inputSchema={
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"]
            }
        ),
        Tool(
            name="verify_rendering",
            description="SENTINEL LION MODE: Probes 5 points in the timeline to hunt down browser-level crashes (e.g., inputRange mismatches). Use after every code write.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="download_asset",
            description="Securely download branding assets (SVG/PNG) from the web into the public folder.",
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
            description="Archive unused components to keep the codebase professional and zero-noise.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="update_memory",
            description="FINAL STEP: Commit the lesson learned from this hunt to your Top 20 evolutionary rules.",
            inputSchema={"type": "object", "properties": {"lesson": {"type": "string"}}, "required": ["lesson"]}
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    """
    The Command Center that routes AI requests to the Sentinel Lion Predator Engine.
    """
    try:
        if name == "initialize_task":
            db.log("CONTEXT", "Injecting autonomous intelligence and memory...")
            res = memory_ops.get_autonomous_context()
            db.log("SUCCESS", "Sentinel Brain is now fully synchronized.")

        elif name == "list_files":
            res = file_ops.list_project_files(arguments.get("rel_path", "."))

        elif name == "read_file":
            res = file_ops.read_project_file(arguments["rel_path"])

        elif name == "write_file":
            res = file_ops.write_project_file(arguments["rel_path"], arguments["content"])
            if "CRITICAL ERROR" in res:
                db.log("GUARD", "Local validation failed. Correcting logic...", style="bold red")
            else:
                db.log("SUCCESS", f"File updated: {arguments['rel_path']}")

        elif name == "run_shell_command":
            db.log("EXEC", f"Terminal Execution: {arguments['command']}")
            res = shell_ops.run_command(arguments["command"])

        elif name == "verify_rendering":
            # This triggers the 5-point Predator Deep Scan
            res = shell_ops.verify_runtime_logic()
            if "SENTINEL LION STRIKE" in res:
                db.log("STRIKE", "Browser-level crash caught! AI is forced to debug.", style="bold bright_red")
            else:
                db.log("SUCCESS", "Video timeline is clean. No errors found.")

        elif name == "download_asset":
            res = asset_ops.download_asset(arguments["url"], arguments["filename"])

        elif name == "cleanup_project":
            db.log("PREDATOR", "Cleaning unused prey from project structure...")
            res = file_ops.archive_unused_files()

        elif name == "update_memory":
            db.log("MEMORY", "Evolving knowledge based on this hunt...")
            res = memory_ops.update_memory(arguments["lesson"])
            db.log("SUCCESS", "Evolution complete. Rules 1-20 updated.")

        else:
            res = f"Error: Tool '{name}' not found."

        return [TextContent(type="text", text=res)]

    except Exception as e:
        db.log("ERROR", f"Sentinel system failure: {str(e)}")
        return [TextContent(type="text", text=f"Critical Error: {str(e)}")]