"""
Entrypoint for running the Winget MCP server.

Author: Ron Webb
Since: 2.0.0
"""

import asyncio
from mcp_commons.server import main
from . import mcp_config

if __name__ == "__main__":
    asyncio.run(main(mcp_config))
