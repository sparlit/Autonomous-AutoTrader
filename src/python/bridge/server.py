import asyncio
import ujson as json
import logging
import time
from typing import Callable, Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AAT_Bridge")

class BridgeServer:
    def __init__(self, host: str, port: int, on_message_cb: Callable[[str, Dict[str, Any]], Any]):
        self.host = host
        self.port = port
        self.on_message_cb = on_message_cb
        self.clients: Dict[str, asyncio.StreamWriter] = {}
        self.stats = {"msgs_rx": 0, "msgs_tx": 0, "last_latency": 0.0}

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info('peername')
        client_id = f"{addr[0]}:{addr[1]}"
        logger.info(f"Hybrid Engine: New connection from {client_id}")
        self.clients[client_id] = writer

        buffer = b""
        try:
            while True:
                data = await reader.read(8192) # Increased buffer for MTF pushes
                if not data: break

                buffer += data
                while b'\n' in buffer:
                    line, buffer = buffer.split(b'\n', 1)
                    message_str = line.decode().strip()
                    if not message_str: continue

                    try:
                        start_time = time.perf_counter()
                        message = json.loads(message_str)
                        self.stats["msgs_rx"] += 1

                        # Process using the hybrid brain
                        response = await self.on_message_cb(client_id, message)

                        if response:
                            writer.write(json.dumps(response).encode() + b'\n')
                            await writer.drain()
                            self.stats["msgs_tx"] += 1
                            self.stats["last_latency"] = (time.perf_counter() - start_time) * 1000
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON from {client_id}")
                    except Exception as e:
                        logger.error(f"Bridge Error: {e}")

        except Exception as e:
            logger.error(f"Client Disconnected: {client_id} ({e})")
        finally:
            self.clients.pop(client_id, None)
            writer.close()
            await writer.wait_closed()

    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        async with server:
            logger.info(f"Hybrid Bridge serving on {self.host}:{self.port}")
            await server.serve_forever()
