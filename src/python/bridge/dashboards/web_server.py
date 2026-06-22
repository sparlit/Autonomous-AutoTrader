from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Any
import ujson as json
import asyncio
import os
import logging
import uvicorn
from multiprocessing import Process

class WebDashboard(Process):
    """10400: FastAPI Web Terminal for remote telemetry."""
    def __init__(self, ipc: Any = None, port: int = 8009):
        Process.__init__(self)
        self.ipc = ipc
        self.port = port

    def run(self):
        logging.basicConfig(level=logging.INFO)
        app = FastAPI()
        active_connections: List[WebSocket] = []

        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            active_connections.append(websocket)
            try:
                while True:
                    # Send regular updates
                    all_state = self.ipc.get_all_state()
                    await websocket.send_text(json.dumps(all_state))
                    await asyncio.sleep(1)
            except Exception as e:
                if websocket in active_connections:
                    active_connections.remove(websocket)

        @app.get("/")
        async def get_index():
            path = os.path.join(os.path.dirname(__file__), "static/index.html")
            return FileResponse(path)

        @app.get("/health")
        async def health():
            return {"status": "ok", "m_id": 10403}

        uvicorn.run(app, host="0.0.0.0", port=self.port, log_level="error")

