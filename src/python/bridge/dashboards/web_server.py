from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Any
import ujson as json
import asyncio
import os
import logging
import uvicorn
from multiprocessing import Process
from multiprocessing.managers import DictProxy, ListProxy

logger = logging.getLogger("AAT_WebDashboard")

def to_dict(obj):
    """Recursively convert multiprocessing proxies to real dicts."""
    if isinstance(obj, (DictProxy, dict)):
        return {k: to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, (ListProxy, list)):
        return [to_dict(v) for v in obj]
    else:
        return obj

class WebDashboard(Process):
    """10400: FastAPI Web Terminal for remote telemetry."""
    def __init__(self, ipc: Any = None, port: int = 8009):
        Process.__init__(self)
        self.ipc = ipc
        self.port = port

    def run(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - WebDash - %(levelname)s - %(message)s')
        app = FastAPI()

        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            logger.info("WebSocket connection established.")
            try:
                while True:
                    try:
                        all_state = self.ipc.get_all_state()
                        # 10408: Ensure all state is converted to real dicts before JSON serialization
                        safe_state = to_dict(all_state)
                        await websocket.send_text(json.dumps(safe_state))
                    except (WebSocketDisconnect, RuntimeError):
                        break
                    except Exception as e:
                        logger.error(f"WebSocket Serialization Error: {e}")
                        if "send" in str(e).lower(): break

                    await asyncio.sleep(1)
            except WebSocketDisconnect:
                logger.info("WebSocket client disconnected.")
            except Exception as e:
                logger.warning(f"WebSocket Loop Error: {e}")

        @app.get("/")
        async def get_index():
            path = os.path.join(os.path.dirname(__file__), "static/index.html")
            return FileResponse(path)

        @app.get("/health")
        async def health():
            return {"status": "ok", "m_id": 10403}

        logger.info(f"Starting Web Dashboard on port {self.port}")
        uvicorn.run(app, host="0.0.0.0", port=self.port, log_level="warning")
