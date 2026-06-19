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
        self.throttle_threshold = 0.05 # 50ms processing limit

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info('peername')
        client_id = f"{addr[0]}:{addr[1]}"
        logger.info(f"Ultra-Bridge: New connection from {client_id}")
        self.clients[client_id] = writer

        buffer = bytearray()
        try:
            while True:
                data = await reader.read(16384) # 16KB buffer for heavy MTF/warmup pushes
                if not data: break

                buffer.extend(data)
                while b'\n' in buffer:
                    pos = buffer.find(b'\n')
                    line = buffer[:pos]
                    del buffer[:pos + 1]

                    if not line: continue

                    try:
                        start_time = time.perf_counter()
                        message = json.loads(line)
                        self.stats["msgs_rx"] += 1

                        # High-Speed Multi-Symbol Processing
                        response = await self.on_message_cb(client_id, message)

                        if response:
                            payload = json.dumps(response).encode() + b'\n'
                            writer.write(payload)
                            await writer.drain()
                            self.stats["msgs_tx"] += 1
                            self.stats["last_latency"] = (time.perf_counter() - start_time)
                    except json.JSONDecodeError:
                        logger.error(f"Corruption in stream from {client_id}")
                    except Exception as e:
                        logger.error(f"Bridge Execution Error: {e}")

        except Exception as e:
            logger.error(f"Link Dropped: {client_id} ({e})")
        finally:
            self.clients.pop(client_id, None)
            writer.close()
            try: await writer.wait_closed()
            except: pass

    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        async with server:
            logger.info(f"Ultra-Parallel Bridge active at {self.host}:{self.port}")
            await server.serve_forever()
