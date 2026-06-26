# Version: V3.1.4-AUTONOMOUS (Hardened RESTRUCTURE)
import asyncio
import ujson as json
import logging
import time
from typing import Dict, Any, List, Optional, Callable
from shared.memory import SharedState, MessageQueue

logging.basicConfig(level=logging.INFO, format='%(asctime)s - AAT_Bridge - %(levelname)s - %(message)s')
logger = logging.getLogger("AAT_Bridge")

class InstitutionalBridge:
    """13000: High-speed Async IO Bridge for MT5 Integration."""
    def __init__(self, host: str, port: int, shared_state: SharedState, orchestrator_q: MessageQueue):
        self.host = host
        self.port = port
        self.shm = shared_state
        self.oq = orchestrator_q
        self.clients: Dict[str, asyncio.StreamWriter] = {}
        self.is_running = True

    async def start(self):
        server = await asyncio.start_server(self.handle_mt5_client, self.host, self.port)
        addr = server.sockets[0].getsockname()
        logger.info(f"Institutional Bridge active at {addr}")

        async with server:
            while self.is_running:
                await asyncio.sleep(1)

    async def handle_mt5_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info('peername')
        client_id = f"{addr[0]}:{addr[1]}"
        logger.info(f"MT5 Client connected: {client_id}")
        self.clients[client_id] = writer

        buffer = bytearray()
        try:
            while True:
                data = await reader.read(8192)
                if not data: break

                buffer.extend(data)
                while b'\n' in buffer:
                    pos = buffer.find(b'\n')
                    line = buffer[:pos]
                    del buffer[:pos+1]

                    if not line: continue

                    try:
                        msg = json.loads(line)
                        await self.process_mt5_message(client_id, msg)
                    except Exception as e:
                        logger.error(f"Message corruption from {client_id}: {e}")

        except Exception as e:
            logger.warning(f"Connection dropped for {client_id}: {e}")
        finally:
            self.clients.pop(client_id, None)
            writer.close()
            await writer.wait_closed()
            logger.info(f"Client offline: {client_id}")

    async def process_mt5_message(self, client_id: str, msg: Dict[str, Any]):
        """13001: Route data to Orchestrator and update Shared State."""
        m_type = msg.get("t")

        if m_type == "HB": # Heartbeat / Account Sync
            self.shm.update_key("account", {
                "equity": msg.get("e", 0),
                "drawdown": msg.get("d", 0),
                "last_update": time.time()
            })

        elif m_type == "DATA": # Market Data Push
            symbol = msg.get("s")
            if symbol:
                self.shm.update_key(f"market:{symbol}", {
                    "bid": msg.get("b"),
                    "ask": msg.get("a"),
                    "v": msg.get("v"),
                    "t": time.time()
                })

        # Always push to orchestrator queue for brain processing
        msg['cid'] = client_id
        self.oq.push(msg)

    async def broadcast(self, message: Dict[str, Any]):
        """13002: Send orders/telemetry back to all MT5 instances."""
        payload = (json.dumps(message) + "\n").encode('utf-8')
        for client_id, writer in self.clients.items():
            try:
                writer.write(payload)
                await writer.drain()
            except Exception as e:
                logger.debug(f"Broadcast fail to {client_id}: {e}")
