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
from src.ui.dashboard import Dashboard as db
from src.tools.remote_ops import RemoteCommander

# =============================================================================
# AUTO-ONBOARDING WIZARD (Synchronous Logic)
# =============================================================================

def update_env_file(key: str, value: str):
    """Writes or updates configuration in the local .env file."""
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
    """Configures Telegram Remote Gateway before the async loop starts."""
    if not config.TELEGRAM_TOKEN or not config.AUTHORIZED_CHAT_ID:
        setup_now = questionary.confirm("Telegram Remote Control is not configured. Setup now?", default=False).ask()
        
        if setup_now:
            token = questionary.text("Enter your Telegram Bot Token:").ask()
            chat_id = questionary.text("Enter your Authorized Chat ID (Numbers only):").ask()
            
            if token and chat_id:
                update_env_file("TELEGRAM_TOKEN", token)
                update_env_file("AUTHORIZED_CHAT_ID", chat_id)
                config.refresh_env()
                db.log("SUCCESS", "Remote credentials secured and activated.")
                return True
        return False
    else:
        return questionary.confirm("Enable Telegram Remote Commander for this session?", default=True).ask()

# =============================================================================
# CORE SERVER ENGINE (The Pulse & Eternal Loop Architecture)
# =============================================================================

# Silence uvicorn background noise
logging.getLogger("uvicorn.error").setLevel(logging.CRITICAL)
logging.getLogger("uvicorn.access").setLevel(logging.CRITICAL)

# Global SSE Transport instance
sse = SseServerTransport("/messages")

async def keep_alive_pulse():
    """
    THE HEARTBEAT ENGINE: Sends SSE comments every 15 seconds.
    Ensures the 'Eternal Watcher' loop in server.py stays connected to Qwen Desktop
    without timing out during long periods of AI inactivity.
    """
    while True:
        try:
            # Send an SSE comment (:) to keep the TCP socket active
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
    MISSION LIFECYCLE: Manages background tasks for Telegram and Heartbeat.
    Guarantees all components run in the same event loop to prevent crashes.
    """
    # 1. Start the Heartbeat Pulse
    pulse_task = asyncio.create_task(keep_alive_pulse())

    # 2. Start Telegram Remote Commander
    if config.TELEGRAM_ENABLED:
        asyncio.create_task(RemoteCommander.start_bot())
    
    # Ready confirmation
    db.status_board()
    db.log("SERVER", f"Engine v7.1 ({config.CODENAME}) is officially SHIELDED.")
    
    yield # App execution happens here
    
    # 3. Graceful Shutdown
    pulse_task.cancel()
    db.log("SERVER", "Shield deactivated. Bridge offline.")

async def sse_endpoint(request):
    """Handles persistent SSE connections for AI handshakes."""
    try:
        async with sse.connect_sse(request.scope, request.receive, request._send) as (r, w):
            db.log("SUCCESS", "Local AI bridge established.")
            await server.run(r, w, server.create_initialization_options())
    except Exception:
        pass

async def messages_endpoint(request):
    """Handles RPC messages and ensures 202 status for the client."""
    await sse.handle_post_message(request.scope, request.receive, request._send)
    return Response(status_code=202)

# Create the Starlette App with Lifespan support
app = Starlette(
    routes=[
        Route("/sse", sse_endpoint, methods=["GET"]),
        Route("/messages", messages_endpoint, methods=["POST"])
    ],
    lifespan=server_lifespan
)

if __name__ == "__main__":
    try:
        # 1. Interactive CLI (Synchronous sequence)
        db.header()
        config.TELEGRAM_ENABLED = telegram_setup_wizard()
        config.SELECTED_MODE = db.select_mode()
        config.refresh_env()
        
        # 2. Hand over to Uvicorn for Loop Management
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
        db.log("SERVER", "Manual override detected. Closing connection...")
        sys.exit(0)
    except Exception as e:
        print(f"Critical Startup Failure: {e}")