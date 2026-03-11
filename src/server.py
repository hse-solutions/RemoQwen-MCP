import logging
from mcp.server import Server
from mcp.types import Tool, TextContent

# Importing our high-performance modular tools
import src.tools.file_ops as file_ops
import src.tools.memory_ops as memory_ops
import src.tools.asset_ops as asset_ops
import src.tools.shell_ops as shell_ops # New for v5.0
from src.ui.dashboard import Dashboard as db

# Initialize the MCP Server (RemoQwen-MCP v5.0)
server = Server("remotion-autonomous-pro-engineer")

@server.list_tools()
async def handle_list_tools():
    """
    Exposes the ultimate autonomous toolset to the AI.
    The descriptions are enhanced to trigger the 'Self-Healing' cycle.
    """
    db.log("SERVER", "AI Engineer is synchronizing advanced v5.0 toolset...")
    
    return [
        Tool(
            name="initialize_task",
            description="MANDATORY START: Loads memory rules, Remotion skills, and project state. Always call this first.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="list_files",
            description="Explore project structure.",
            inputSchema={"type": "object", "properties": {"rel_path": {"type": "string"}}}
        ),
        Tool(
            name="read_file",
            description="Read code or skills to understand logic.",
            inputSchema={"type": "object", "properties": {"rel_path": {"type": "string"}}, "required": ["rel_path"]}
        ),
        Tool(
            name="write_file",
            description="Write/Update code. This tool auto-validates interpolation and staticFile rules.",
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
            description="Run terminal commands (npm, npx, node, remotion). Useful for starting servers or checking builds.",
            inputSchema={
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"]
            }
        ),
        Tool(
            name="verify_rendering",
            description="CRITICAL: Run this after writing code to catch logic errors that only appear in a browser (like inputRange mismatches).",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="download_asset",
            description="Download external branding assets into the public folder.",
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
            description="Archive unused scenes and keep the codebase professional.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="update_memory",
            description="FINAL STEP: Save new lessons and evolution rules (Rules 1-20).",
            inputSchema={"type": "object", "properties": {"lesson": {"type": "string"}}, "required": ["lesson"]}
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    """
    Orchestrates the AI requests and updates the Dashboard with v5.0 logic.
    """
    try:
        if name == "initialize_task":
            db.log("CONTEXT", "Initializing full autonomous intelligence...")
            res = memory_ops.get_autonomous_context()
            db.log("SUCCESS", "Project DNA and Memory injected into AI brain.")

        elif name == "list_files":
            res = file_ops.list_project_files(arguments.get("rel_path", "."))

        elif name == "read_file":
            res = file_ops.read_project_file(arguments["rel_path"])

        elif name == "write_file":
            res = file_ops.write_project_file(arguments["rel_path"], arguments["content"])
            if "CRITICAL ERROR" in res:
                db.log("ERROR", "Code rejection! Forcing logic correction.")
            else:
                db.log("SUCCESS", f"Code saved: {arguments['rel_path']}")

        elif name == "run_shell_command":
            db.log("EXEC", f"Running terminal command: {arguments['command']}")
            res = shell_ops.run_command(arguments["command"])

        elif name == "verify_rendering":
            db.log("GUARD", "Executing Headless Runtime Validation...")
            res = shell_ops.verify_runtime_logic()
            if "CRITICAL ERROR" in res:
                db.log("ERROR", "Browser-level crash detected! AI must debug.")
            else:
                db.log("SUCCESS", "React/Remotion runtime validation passed.")

        elif name == "download_asset":
            res = asset_ops.download_asset(arguments["url"], arguments["filename"])

        elif name == "cleanup_project":
            db.log("MEMORY", "Sanitizing project structure...")
            res = file_ops.archive_unused_files()

        elif name == "update_memory":
            db.log("MEMORY", "Evolving the knowledge base...")
            res = memory_ops.update_memory(arguments["lesson"])
            db.log("SUCCESS", "Lesson committed to Top 20 rules.")

        else:
            res = f"Error: Tool '{name}' not found."

        return [TextContent(type="text", text=res)]

    except Exception as e:
        db.log("ERROR", f"System failure in '{name}': {str(e)}")
        return [TextContent(type="text", text=f"Critical Error: {str(e)}")]