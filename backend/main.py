from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from chatkit.server import StreamingResult

from app.server import MeetingSchedulerServer
from app.types import RequestContext
from app.store.app_store import init_db, seed_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await seed_db()
    yield
    # Shutdown

app = FastAPI(lifespan=lifespan)

# CORS is crucial for Next.js to talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

server = MeetingSchedulerServer()


@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    # Extract User ID from header set by Frontend
    user_id = request.headers.get("X-User-ID", "anonymous")
    context = RequestContext(user_id=user_id)

    body = await request.body()
    result = await server.process(body, context)

    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")

    return Response(content=result.json, media_type="application/json")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)