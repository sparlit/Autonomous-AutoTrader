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

logger = logging.getLogger("AAT_WebDashboard")

class WebDashboard(Process):
    """10400: FastAPI Web Terminal for remote telemetry."""
    def __init__(self, ipc: Any = None, port: int = 8009):
        Process.__init__(self)
        self.ipc = ipc
        self.port = port

    def run(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - WebDash - %(levelname)s - %(message)s')
        app = FastAPI()
        active_connections: List[WebSocket] = []

        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            active_connections.append(websocket)
            logger.info("WebSocket connection established.")
            try:
                while True:
                    # 10401: Robust serialization for IPC state
                    try:
                        all_state = self.ipc.get_all_state()
                        # Convert any non-serializable objects to strings/lists
                        safe_state = {}
                        for k, v in all_state.items():
                            if isinstance(v, (dict, list, str, int, float, bool)) or v is None:
                                safe_state[k] = v
                            else:
                                safe_state[k] = str(v)

                        await websocket.send_text(json.dumps(safe_state))
                    except Exception as e:
                        logger.error(f"WebSocket Loop Serialization Error: {e}")

                    await asyncio.sleep(1)
            except Exception as e:
                logger.warning(f"WebSocket connection closed: {e}")
                if websocket in active_connections:
                    active_connections.remove(websocket)

        @app.get("/")
        async def get_index():
            path = os.path.join(os.path.dirname(__file__), "static/index.html")
            return FileResponse(path)

        @app.get("/health")
        async def health():
            return {"status": "ok", "m_id": 10403}

        logger.info(f"Starting Web Dashboard on port {self.port}")
        uvicorn.run(app, host="0.0.0.0", port=self.port, log_level="warning")
