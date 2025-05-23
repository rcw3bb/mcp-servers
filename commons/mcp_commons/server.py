"""Main server module that handles MCP (Model Context Protocol) server implementation.

This module provides the server implementation for handling operations through the Model Context Protocol.
It sets up the server, registers tools, and handles tool execution.

Author: Ron Webb
Since: 1.0.0
"""

import asyncio

from collections.abc import Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource, ErrorData
from mcp.shared.exceptions import McpError

from mcp_commons.config import McpConfig
from . import __version__
from .executor import execute_tool
from .util import setup_logger


async def main(config: McpConfig) -> None:
    """Main entry point for the MCP server.

    This function initializes and runs the server, handling stdio communication
    and server lifecycle.

    Args:
        config: The MCP server configuration instance.

    Raises:
        Exception: If there is an error during server execution.
    """
    logger = setup_logger(__name__)

    app = Server(config.server_name)

    @app.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools in the MCP server.

        Returns:
            list[Tool]: List of available tools and their descriptions.
        """
        logger.info("Listing available tools")
        tools = [
            controller.tool()
            for controller in config.controller_registry.get_registry()
        ]
        logger.info("Found %d tools", len(tools))
        return tools

    @app.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Execute a tool with the given name and arguments.

        Args:
            name: The name of the tool to execute.
            arguments: Dictionary of arguments to pass to the tool.

        Returns:
            Sequence[TextContent | ImageContent | EmbeddedResource]: Tool execution results.

        Raises:
            McpError: If tool execution fails.
        """
        try:
            logger.info("Executing tool: %s", name)
            logger.debug("Tool arguments: %s", arguments)
            result = execute_tool(name, arguments, config)
            logger.debug("Tool execution successful")
            return result
        except Exception as e:
            logger.error("Error executing tool %s: %s", name, str(e))
            raise McpError(
                ErrorData(message=f"An error occurred: {str(e)}", code=500)
            ) from e

    logger.info(
        "Starting %s v%s (MCP Commons v%s)",
        config.server_name,
        config.server_version,
        __version__,
    )
    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Server initialized, starting main loop")
            await app.run(
                read_stream, write_stream, app.create_initialization_options()
            )
    except Exception as e:
        logger.error("Server error: %s", str(e))
        raise
    finally:
        logger.info("Server shutting down")


if __name__ == "__main__":
    asyncio.run(main(McpConfig()))
