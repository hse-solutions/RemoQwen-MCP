from mcp.server import Server
from mcp.types import Tool, TextContent
import src.tools.file_ops as file_ops
import src.tools.memory_ops as memory_ops
import src.tools.asset_ops as asset_ops
from src.ui.dashboard import Dashboard as db

server = Server("remotion-autonomous-engineer")

@server.list_tools()
async def handle_list_tools():
    return [
        Tool(name="initialize_task", description="MANDATORY START: Syncs memory and skills.", inputSchema={"type": "object"}),
        Tool(name="list_files", description="Explore project.", inputSchema={"type": "object", "properties": {"rel_path": {"type": "string"}}}),
        Tool(name="read_file", description="Read code.", inputSchema={"type": "object", "properties": {"rel_path": {"type": "string"}}, "required": ["rel_path"]}),
        Tool(name="write_file", description="Write code with validation.", inputSchema={"type": "object", "properties": {"rel_path": {"type": "string"}, "content": {"type": "string"}}, "required": ["rel_path", "content"]}),
        Tool(name="download_asset", description="Download assets.", inputSchema={"type": "object", "properties": {"url": {"type": "string"}, "filename": {"type": "string"}}, "required": ["url", "filename"]}),
        Tool(name="cleanup_project", description="Archive unused scenes.", inputSchema={"type": "object"}),
        Tool(name="update_memory", description="Commit lessons (Rules 1-20).", inputSchema={"type": "object", "properties": {"lesson": {"type": "string"}}, "required": ["lesson"]})
    ]

@server.call_tool()
async def handle_call_tool(name, arguments):
    try:
        if name == "initialize_task":
            db.log("CONTEXT", "Loading brain...")
            res = memory_ops.get_autonomous_context()
        elif name == "list_files":
            res = file_ops.list_project_files(arguments.get("rel_path", "."))
        elif name == "read_file":
            res = file_ops.read_project_file(arguments["rel_path"])
        elif name == "write_file":
            res = file_ops.write_project_file(arguments["rel_path"], arguments["content"])
            db.log("ERROR" if "CRITICAL" in res else "SUCCESS", res)
        elif name == "download_asset":
            res = asset_ops.download_asset(arguments["url"], arguments["filename"])
        elif name == "cleanup_project":
            res = file_ops.archive_unused_files()
        elif name == "update_memory":
            res = memory_ops.update_memory(arguments["lesson"])
        else: res = "Unknown tool."
        return [TextContent(type="text", text=res)]
    except Exception as e:
        db.log("ERROR", str(e))
        return [TextContent(type="text", text=str(e))]