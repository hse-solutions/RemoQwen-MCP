import uvicorn
import logging
import sys
import os
import asyncio
import questionary
from contextlib import asynccontextmanager
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import Response
from mcp.server.sse import SseServerTransport

import config
from src.server import server
# Importing via the synchronized alias in dashboard.py
from src.ui.dashboard import db
from src.tools.remote_ops import RemoteCommander

# =============================================================================
# AUTO-ONBOARDING WIZARD (Synchronous & Safe)
# =============================================================================

def update_env_file(key: str, value: str):
    """Safely updates or appends configuration keys in the .env file."""
    env_path = ".env"
    lines = []
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
    
    found = False
    new_line = f"{key}={value}\n"
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = new_line
            found = True
            break
    if not found:
        lines.append(new_line)
        
    with open(env_path, "w") as f:
        f.writelines(lines)

def telegram_setup_wizard() -> bool:
    """Configures the Telegram Remote Gateway before entering the async loop."""
    if not config.TELEGRAM_TOKEN or not config.AUTHORIZED_CHAT_ID:
        setup_now = questionary.confirm("Telegram Remote Control is not configured. Setup now?", default=False).ask()
        
        if setup_now:
            token = questionary.text("Enter your Telegram Bot Token:").ask()
            chat_id = questionary.text("Enter your Authorized Chat ID:").ask()
            
            if token and chat_id:
                update_env_file("TELEGRAM_TOKEN", token)
                update_env_file("AUTHORIZED_CHAT_ID", chat_id)
                config.refresh_env() # Reload into system memory
                db.log("SUCCESS", "Remote credentials secured and activated.")
                return True
        return False
    else:
        return questionary.confirm("Enable Telegram Remote Commander for this session?", default=True).ask()

# =============================================================================
# CORE SERVER ENGINE (Lifespan & Heartbeat Architecture)
# =============================================================================

# Suppress internal noise logs
logging.getLogger("uvicorn.error").setLevel(logging.CRITICAL)
logging.getLogger("uvicorn.access").setLevel(logging.CRITICAL)

# Global SSE Transport instance
sse = SseServerTransport("/messages")

async def keep_alive_pulse():
    """
    THE HEARTBEAT ENGINE: Maintains the SSE connection during long AI idle periods.
    Sends a silent comment (:) every 15 seconds to prevent network timeouts.
    Essential for v8.0 Eternal Watcher stability.
    """
    while True:
        try:
            if hasattr(sse, "_stream") and sse._stream:
                await sse._stream.send(":\n\n")
            await asyncio.sleep(15)
        except asyncio.CancelledError:
            break
        except Exception:
            await asyncio.sleep(5)

@asynccontextmanager
async def server_lifespan(app: Starlette):
    """
    SERVER LIFECYCLE MANAGER: Synchronizes background tasks within the Uvicorn loop.
    Ensures that Telegram Bot and Heartbeat Pulse run concurrently without conflicts.
    """
    # 1. Start the Immortal Heartbeat
    pulse_task = asyncio.create_task(keep_alive_pulse())

    # 2. Start the Telegram Gateway if enabled
    if config.TELEGRAM_ENABLED:
        asyncio.create_task(RemoteCommander.start_bot())
    
    # Ready Signal
    db.status_board()
    db.log("SERVER", f"Engine v8.0 ({config.CODENAME}) is officially SHIELDED.")
    
    yield # Execution occurs while yielded
    
    # 3. Graceful Shutdown sequence
    pulse_task.cancel()
    db.log("SERVER", "Shield deactivated. System offline.")

async def sse_endpoint(request):
    """Handles persistent SSE connections for local AI clients (Qwen Desktop)."""
    try:
        async with sse.connect_sse(request.scope, request.receive, request._send) as (r, w):
            db.log("SUCCESS", "Local AI bridge connection established.")
            await server.run(r, w, server.create_initialization_options())
    except Exception:
        pass

async def messages_endpoint(request):
    """Handles JSON-RPC POST messages and returns a proper 202 status."""
    try:
        await sse.handle_post_message(request.scope, request.receive, request._send)
        return Response(status_code=202)
    except Exception:
        return Response(status_code=500)

# Initialize Starlette application with Lifespan support
app = Starlette(
    routes=[
        Route("/sse", sse_endpoint, methods=["GET"]),
        Route("/messages", messages_endpoint, methods=["POST"])
    ],
    lifespan=server_lifespan
)

if __name__ == "__main__":
    try:
        # 1. Boot up Interactive UI sequence (Pure Synchronous)
        db.header()
        config.TELEGRAM_ENABLED = telegram_setup_wizard()
        config.SELECTED_MODE = db.select_mode()
        config.refresh_env() # Lock in final pathing configuration
        
        # 2. Hand over event loop control to Uvicorn with High-Persistence parameters
        uvicorn.run(
            app, 
            host="127.0.0.1", 
            port=8000, 
            access_log=False, 
            log_level="critical",
            timeout_keep_alive=36000 # 10-Hour persistence layer
        )
        
    except KeyboardInterrupt:
        print("\n")
        db.log("SERVER", "Manual shutdown detected. Closing session safely. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Critical Startup Failure: {e}")