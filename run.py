import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import Response
from mcp.server.sse import SseServerTransport
from src.server import server
from src.ui.dashboard import Dashboard as db

sse = SseServerTransport("/messages")

async def sse_endpoint(request):
    db.log("SERVER", "AI Connecting...")
    async with sse.connect_sse(request.scope, request.receive, request._send) as (r, w):
        db.log("SUCCESS", "Autonomous Mode: ONLINE")
        await server.run(r, w, server.create_initialization_options())

async def messages_endpoint(request):
    await sse.handle_post_message(request.scope, request.receive, request._send)
    return Response(status_code=202)

app = Starlette(routes=[Route("/sse", sse_endpoint), Route("/messages", messages_endpoint, methods=["POST"])])

if __name__ == "__main__":
    db.header()
    uvicorn.run(app, host="127.0.0.1", port=8000, access_log=False)