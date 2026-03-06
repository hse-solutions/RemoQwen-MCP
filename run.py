import uvicorn
import logging
import sys
import anyio
from starlette.applications import Starlette
from starlette.routing import Route
from mcp.server.sse import SseServerTransport
from src.server import server
from src.ui.dashboard import Dashboard as db

# Fully silence background noise
logging.getLogger("uvicorn.error").setLevel(logging.CRITICAL)
logging.getLogger("uvicorn.access").setLevel(logging.CRITICAL)

sse = SseServerTransport("/messages")

async def sse_endpoint(request):
    """Handles the SSE connection with anti-spam protection."""
    try:
        async with sse.connect_sse(request.scope, request.receive, request._send) as (r, w):
            db.log("SUCCESS", "Autonomous Bridge: ONLINE")
            # Using initialization options instead of initial options
            await server.run(r, w, server.create_initialization_options())
    except Exception as e:
        # Catch the "TaskGroup" and other connection-reset errors silently
        # This prevents the "Parade" of error messages in the terminal
        if "TaskGroup" in str(e) or "IncompleteRead" in str(e):
            pass 
        else:
            db.log("SERVER", "Connection cycle refreshed.")

async def messages_endpoint(request):
    """Handle POST messages from AI client."""
    try:
        await sse.handle_post_message(request.scope, request.receive, request._send)
    except Exception:
        pass # Silently ignore post-message failures during disconnects

app = Starlette(routes=[
    Route("/sse", sse_endpoint, methods=["GET"]),
    Route("/messages", messages_endpoint, methods=["POST"])
])

if __name__ == "__main__":
    try:
        db.header()
        db.log("SERVER", "Engine Stabilized. Monitoring AI for activity...")
        uvicorn.run(app, host="127.0.0.1", port=8000, access_log=False, log_level="critical")
    except KeyboardInterrupt:
        print("\n")
        db.log("SERVER", "Bridge shutting down safely. Goodbye!")
        sys.exit(0)
    except Exception as e:
        # Prevent the server from exploding on startup errors
        pass