import asyncio
import ujson as json
import logging
from typing import Callable, Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AAT_Bridge")

class BridgeServer:
    def __init__(self, host: str, port: int, on_message_cb: Callable[[str, Dict[str, Any]], Any]):
        self.host = host
        self.port = port
        self.on_message_cb = on_message_cb
        self.clients: Dict[str, asyncio.StreamWriter] = {}

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info('peername')
        client_id = f"{addr[0]}:{addr[1]}"
        logger.info(f"New connection from {client_id}")
        self.clients[client_id] = writer

        try:
            while True:
                data = await reader.readuntil(b'\n')
                if not data:
                    break

                message_str = data.decode().strip()
                if not message_str:
                    continue

                try:
                    message = json.loads(message_str)
                    response = await self.on_message_cb(client_id, message)
                    if response:
                        writer.write(json.dumps(response).encode() + b'\n')
                        await writer.drain()
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from {client_id}: {message_str}")
                except Exception as e:
                    logger.error(f"Error processing message from {client_id}: {e}")

        except asyncio.IncompleteReadError:
            logger.info(f"Client {client_id} disconnected")
        except Exception as e:
            logger.error(f"Connection error with {client_id}: {e}")
        finally:
            self.clients.pop(client_id, None)
            writer.close()
            await writer.wait_closed()

    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        addr = server.sockets[0].getsockname()
        logger.info(f'Serving on {addr}')
        async with server:
            await server.serve_forever()

    async def broadcast(self, message: Dict[str, Any]):
        data = json.dumps(message).encode() + b'\n'
        for client_id, writer in self.clients.items():
            try:
                writer.write(data)
                await writer.drain()
            except Exception as e:
                logger.error(f"Failed to broadcast to {client_id}: {e}")
