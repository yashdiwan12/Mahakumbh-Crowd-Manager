import asyncio
from fastapi import FastAPI
from app.api.routes import router as api_router
from app.api.websocket import router as ws_router
from app.api.websocket import broadcast_state_loop
from app.core.state import state

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Mahakumbh Crowd Routing Control Room")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
app.include_router(ws_router, prefix="/api/v1")

async def background_state_flusher():
    while True:
        await asyncio.sleep(30)
        await state.flush_to_db()

@app.on_event('startup')
async def on_start():
    # create db tables in dev
    from app.db import init_db
    init_db()
    
    # load initial state into memory
    state.load_from_db()
    
    # start background flush task
    asyncio.create_task(background_state_flusher())
    # start websocket broadcast loop
    asyncio.create_task(broadcast_state_loop())

@app.get("/")
async def root():
    return {"status": "ok", "service": "backend control room"}
