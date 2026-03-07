import uvicorn
import logging
import sys
import anyio
import config
from starlette.applications import Starlette
from starlette.routing import Route
from mcp.server.sse import SseServerTransport
from src.server import server
from src.ui.dashboard import Dashboard as db

# =============================================================================
# PRODUCTION ENGINE CONFIGURATION
# =============================================================================

# Fully silence background noise for a clean Dashboard experience
logging.getLogger("uvicorn.error").setLevel(logging.CRITICAL)
logging.getLogger("uvicorn.access").setLevel(logging.CRITICAL)

# Initialize SSE Transport for MCP
sse = SseServerTransport("/messages")

async def sse_endpoint(request):
    """Handles the persistent SSE connection with anti-spam protection."""
    try:
        async with sse.connect_sse(request.scope, request.receive, request._send) as (r, w):
            db.log("SUCCESS", "Autonomous Bridge connection established.")
            # Run the server with standardized initialization
            await server.run(r, w, server.create_initialization_options())
    except Exception as e:
        # Silently refresh connections without terminal noise
        if "TaskGroup" in str(e) or "IncompleteRead" in str(e):
            pass 
        else:
            db.log("SERVER", "Connection lifecycle refreshed.")

async def messages_endpoint(request):
    """Handle JSON-RPC messages from AI client."""
    try:
        await sse.handle_post_message(request.scope, request.receive, request._send)
    except Exception:
        pass 

# Define Starlette application
app = Starlette(routes=[
    Route("/sse", sse_endpoint, methods=["GET"]),
    Route("/messages", messages_endpoint, methods=["POST"])
])

if __name__ == "__main__":
    try:
        # 1. Display Branding Header
        db.header()
        
        # 2. INTERACTIVE MODE SELECTION (Arrow Key Menu)
        selected_mode = db.select_mode()
        
        # 3. Update Global State
        config.SELECTED_MODE = selected_mode
        
        # 4. Show Status Board with Selected Mode & URL
        db.status_board(config.SELECTED_MODE, "http://127.0.0.1:8000/sse")
        
        db.log("SERVER", "Engine Stabilized. Monitoring AI operations...")
        
        # 5. Start the production server
        uvicorn.run(
            app, 
            host="127.0.0.1", 
            port=8000, 
            access_log=False, 
            log_level="critical"
        )
        
    except KeyboardInterrupt:
        print("\n")
        db.log("SERVER", "Ctrl+C detected. Shutting down Bridge safely. Goodbye!")
        sys.exit(0)
    except Exception as e:
        # Basic error handling for unexpected startup issues
        print(f"Startup Error: {e}")