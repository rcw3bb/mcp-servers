"""
Entrypoint for running the Chocolatey MCP server.

Author: Ron Webb
Since: 1.0.0
"""

import asyncio
from mcp_commons.server import main
from . import mcp_config

if __name__ == "__main__":
    asyncio.run(main(mcp_config))
