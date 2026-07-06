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
        self.client_seqs: Dict[str, int] = {}
        self.stats = {"msgs_rx": 0, "msgs_tx": 0, "last_latency": 0.0}
        self.throttle_threshold = 0.05 # 50ms processing limit
        self._server = None

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
        self.client_seqs[client_id] = 0

        buffer = bytearray()
        try:
            while True:
                try:
                    data = await reader.read(16384) # 16KB buffer for heavy MTF/warmup pushes
                    if not data: break
                except (ConnectionResetError, BrokenPipeError, asyncio.CancelledError):
                    break

                buffer.extend(data)
                while b'\n' in buffer:
                    pos = buffer.find(b'\n')
                    line = buffer[:pos]
                    del buffer[:pos + 1]

                    if not line: continue

                    try:
                        start_time = time.perf_counter()
                        # 13010: Strip null bytes and whitespace to prevent decoding errors
                        clean_line = line.replace(b'\x00', b'').strip()
                        if not clean_line: continue

                        message = json.loads(clean_line)
                        self.stats["msgs_rx"] += 1

                        response = await self.on_message_cb(client_id, message)

                        if response:
                            self.client_seqs[client_id] += 1
                            response["seq"] = self.client_seqs[client_id]
                            payload = json.dumps(response).encode() + b'\n'
                            writer.write(payload)
                            await writer.drain()
                            self.stats["msgs_tx"] += 1
                            self.stats["last_latency"] = (time.perf_counter() - start_time)
                    except json.JSONDecodeError as e:
                        logger.error(f"Corruption in stream from {client_id}: {e} (Raw: {line[:50]!r})")
                    except (ConnectionResetError, BrokenPipeError):
                        logger.info(f"Connection Reset by {client_id} during write")
                        return
                    except Exception as e:
                        logger.error(f"Bridge Execution Error: {e}")

        except Exception as e:
            logger.error(f"Link Dropped: {client_id} ({e})")
        finally:
            self.clients.pop(client_id, None)
            self.client_seqs.pop(client_id, None)
            logger.info(f"Client offline: {client_id}")
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                logger.debug("Silent cleanup completed for closed writer")

    async def broadcast(self, message: Dict[str, Any]):
        """13006: Broadcast message to all connected clients."""
        # 13007: Use list(items()) to prevent "dictionary changed size during iteration"
        dead_clients = []
        for client_id, writer in list(self.clients.items()):
            try:
                # Per-client sequence for broadcast too
                self.client_seqs[client_id] += 1
                msg_copy = message.copy()
                msg_copy["seq"] = self.client_seqs[client_id]

                payload = json.dumps(msg_copy).encode() + b"\n"
                writer.write(payload)
                await writer.drain()
                self.stats["msgs_tx"] += 1
            except (ConnectionResetError, BrokenPipeError, socket.error):
                dead_clients.append(client_id)
            except Exception as e:
                logger.debug(f"Broadcast failed to {client_id}: {e}")

        for cid in dead_clients:
            self.clients.pop(cid, None)
            self.client_seqs.pop(cid, None)
            logger.info(f"Pruned dead client: {cid}")

    async def start(self):
        """
        Start the TCP server and listen indefinitely for client connections.
        """
        try:
            self._server = await asyncio.start_server(self.handle_client, self.host, self.port, reuse_address=True)
        except OSError as e:
            logger.error(f"Failed to bind to {self.host}:{self.port} - Port may be in use: {e}")
            raise e

        async with self._server:
            logger.info(f"Ultra-Parallel Bridge active at {self.host}:{self.port}")
            try:
                await self._server.serve_forever()
            except asyncio.CancelledError:
                logger.info("Bridge server task cancelled.")

    async def stop(self):
        """Stop the bridge server and close all client connections."""
        logger.info("Stopping Bridge Server...")
        if self._server:
            self._server.close()
            await self._server.wait_closed()

        # 13008: Use list(items()) to prevent "dictionary changed size during iteration"
        for client_id, writer in list(self.clients.items()):
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass
        self.clients.clear()
        logger.info("Bridge Server stopped.")
