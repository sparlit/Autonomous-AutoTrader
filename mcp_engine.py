import sys
import os
import asyncio
import logging

# Ensure root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.python.bridge.mcp_server import mcp, initialize_coordinator

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filename="mcp_server.log"
    )

    # Run the initialization in the background before starting the MCP server
    loop = asyncio.get_event_loop()
    loop.run_until_complete(initialize_coordinator())

    # Start the MCP server
    mcp.run()
