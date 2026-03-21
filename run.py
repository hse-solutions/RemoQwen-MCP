import uvicorn
import logging
import sys
import os
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
# AUTO-ONBOARDING WIZARD (Synchronous & Safe)
# =============================================================================

def update_env_file(key: str, value: str):
    """Writes or updates configuration in the local .env file."""
    env_path = ".env"
    lines =[]
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
    """CLI wizard to configure Telegram. Runs BEFORE the async loop starts."""
    if not config.TELEGRAM_TOKEN or not config.AUTHORIZED_CHAT_ID:
        # Using synchronous .ask() to avoid loop conflicts
        setup_now = questionary.confirm("Telegram Remote Control is not configured. Setup now?", default=False).ask()
        
        if setup_now:
            token = questionary.text("Enter your Telegram Bot Token:").ask()
            chat_id = questionary.text("Enter your Authorized Chat ID (Numbers only):").ask()
            
            if token and chat_id:
                update_env_file("TELEGRAM_TOKEN", token)
                update_env_file("AUTHORIZED_CHAT_ID", chat_id)
                config.refresh_env()
                db.log("SUCCESS", "Remote credentials saved and activated.")
                return True
        return False
    else:
        return questionary.confirm("Enable Telegram Remote Commander for this session?", default=True).ask()

# =============================================================================
# CORE SERVER ENGINE (The Lifespan Architecture)
# =============================================================================

logging.getLogger("uvicorn.error").setLevel(logging.CRITICAL)
logging.getLogger("uvicorn.access").setLevel(logging.CRITICAL)

sse = SseServerTransport("/messages")

@asynccontextmanager
async def server_lifespan(app: Starlette):
    """
    THE MAGIC FIX: This runs exactly when Uvicorn takes over the event loop.
    It guarantees the Telegram Bot starts in the SAME loop without conflicts.
    """
    if config.TELEGRAM_ENABLED:
        import asyncio
        # Start Telegram Bot as a background task in the Uvicorn loop
        asyncio.create_task(RemoteCommander.start_bot())
    
    # Display the final status board once the server is fully ready
    db.status_board()
    db.log("SERVER", f"Engine v7.0 ({config.CODENAME}) is officially online.")
    
    yield # The Server runs here
    
    # Shutdown logic
    db.log("SERVER", "Shutting down Bridge components...")

async def sse_endpoint(request):
    """Handles persistent SSE connections."""
    try:
        async with sse.connect_sse(request.scope, request.receive, request._send) as (r, w):
            db.log("SUCCESS", "Local AI bridge connection established.")
            await server.run(r, w, server.create_initialization_options())
    except Exception:
        pass

async def messages_endpoint(request):
    """Handles JSON-RPC POST messages safely."""
    await sse.handle_post_message(request.scope, request.receive, request._send)
    return Response(status_code=202)

# Apply the lifespan manager to the Starlette app
app = Starlette(
    routes=[
        Route("/sse", sse_endpoint, methods=["GET"]),
        Route("/messages", messages_endpoint, methods=["POST"])
    ],
    lifespan=server_lifespan
)

if __name__ == "__main__":
    try:
        # 1. Run the interactive UI (100% Synchronous, no loop conflicts)
        db.header()
        config.TELEGRAM_ENABLED = telegram_setup_wizard()
        config.SELECTED_MODE = db.select_mode()
        config.refresh_env()
        
        # 2. Hand over control to Uvicorn (It creates its own perfect loop)
        uvicorn.run(
            app, 
            host="127.0.0.1", 
            port=8000, 
            access_log=False, 
            log_level="critical",
            timeout_keep_alive=36000 # 10-Hour persistence
        )
        
    except KeyboardInterrupt:
        print("\n")
        db.log("SERVER", "Manual override detected. Bridge offline. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Critical Startup Failure: {e}")