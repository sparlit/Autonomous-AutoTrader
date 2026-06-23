import asyncio
import ujson as json
import logging
import time
import socket
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
        try:
            # 13009: Set Keep-Alive to prevent silent drops
            sock = writer.get_extra_info('socket')
            if sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

            addr = writer.get_extra_info('peername')
            if not addr:
                writer.close()
                return
            client_id = f"{addr[0]}:{addr[1]}"
        except Exception:
            writer.close()
            return

        logger.info(f"Ultra-Bridge: New connection from {client_id}")
        self.clients[client_id] = writer

        buffer = bytearray()
        try:
            while True:
                try:
                    data = await reader.read(16384) # 16KB buffer for heavy MTF/warmup pushes
                    if not data: break
                except (ConnectionResetError, BrokenPipeError):
                    break

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

                        response = await self.on_message_cb(client_id, message)

                        if response:
                            payload = json.dumps(response).encode() + b'\n'
                            writer.write(payload)
                            await writer.drain()
                            self.stats["msgs_tx"] += 1
                            self.stats["last_latency"] = (time.perf_counter() - start_time)
                    except json.JSONDecodeError:
                        logger.error(f"Corruption in stream from {client_id}")
                    except (ConnectionResetError, BrokenPipeError):
                        logger.info(f"Connection Reset by {client_id} during write")
                        return
                    except Exception as e:
                        logger.error(f"Bridge Execution Error: {e}")

        except Exception as e:
            logger.error(f"Link Dropped: {client_id} ({e})")
        finally:
            self.clients.pop(client_id, None)
            logger.info(f"Client offline: {client_id}")
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                logger.debug("Silent cleanup completed for closed writer")

    async def broadcast(self, message: Dict[str, Any]):
        """13006: Broadcast message to all connected clients."""
        payload = json.dumps(message).encode() + b"\n"
        dead_clients = []
        for client_id, writer in self.clients.items():
            try:
                writer.write(payload)
                await writer.drain()
                self.stats["msgs_tx"] += 1
            except (ConnectionResetError, BrokenPipeError, socket.error):
                dead_clients.append(client_id)
            except Exception as e:
                logger.debug(f"Broadcast failed to {client_id}: {e}")

        for cid in dead_clients:
            self.clients.pop(cid, None)
            logger.info(f"Pruned dead client: {cid}")

    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        async with server:
            logger.info(f"Ultra-Parallel Bridge active at {self.host}:{self.port}")
            await server.serve_forever()
