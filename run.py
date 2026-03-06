import uvicorn
import logging
import sys
import anyio
from starlette.applications import Starlette
from starlette.routing import Route
from mcp.server.sse import SseServerTransport
from src.server import server
from src.ui.dashboard import Dashboard as db

# =============================================================================
# PRODUCTION SERVER CONFIGURATION
# =============================================================================

# Fully silence background noise to keep the Dashboard clean
logging.getLogger("uvicorn.error").setLevel(logging.CRITICAL)
logging.getLogger("uvicorn.access").setLevel(logging.CRITICAL)

# Initialize SSE Transport
sse = SseServerTransport("/messages")

async def sse_endpoint(request):
    """Handles the SSE connection with anti-spam and task-group protection."""
    try:
        async with sse.connect_sse(request.scope, request.receive, request._send) as (r, w):
            db.log("SUCCESS", "Autonomous Bridge: ONLINE")
            # Run the server with standardized initialization options
            await server.run(r, w, server.create_initialization_options())
    except Exception as e:
        # Silently handle connection drops to prevent terminal spamming
        if "TaskGroup" in str(e) or "IncompleteRead" in str(e):
            pass 
        else:
            db.log("SERVER", "Connection lifecycle refreshed.")

async def messages_endpoint(request):
    """Handle POST messages from AI client without response conflicts."""
    try:
        await sse.handle_post_message(request.scope, request.receive, request._send)
    except Exception:
        pass # Ignore post-message failures during rapid disconnects

# Define stable application routes
app = Starlette(routes=[
    Route("/sse", sse_endpoint, methods=["GET"]),
    Route("/messages", messages_endpoint, methods=["POST"])
])

if __name__ == "__main__":
    try:
        # Display the professional UI Header
        db.header()
        
        # DISPLAY THE SSE URL CLEARLY (AS REQUESTED)
        db.connection_info("http://127.0.0.1:8000/sse")
        
        db.log("SERVER", "Engine Stabilized. Monitoring AI for activity...")
        
        # Start the production server
        uvicorn.run(
            app, 
            host="127.0.0.1", 
            port=8000, 
            access_log=False, 
            log_level="critical"
        )
    except KeyboardInterrupt:
        print("\n")
        db.log("SERVER", "Bridge shutting down safely. Goodbye!")
        sys.exit(0)
    except Exception:
        # Prevent server explosion on startup
        pass