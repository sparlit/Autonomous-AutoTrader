from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
import ujson as json
import asyncio
import os
import logging

app = FastAPI()
active_connections: List[WebSocket] = []

# Magic: 10401
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception as e:
        logging.debug(f"Websocket disconnect: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)

# Magic: 10402
async def broadcast_telemetry(data: dict):
    for connection in active_connections:
        try:
            await connection.send_text(json.dumps(data))
        except Exception as e:
            logging.debug(f"Broadcast fail: {e}")

# Magic: 10403
@app.get("/")
async def get_index():
    path = os.path.join(os.path.dirname(__file__), "static/index.html")
    return FileResponse(path)

@app.get("/health")
async def health():
    return {"status": "ok", "m_id": 10403}
