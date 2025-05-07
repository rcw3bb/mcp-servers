"""Main server module that handles MCP (Model Context Protocol) server implementation for Winget.

This module provides the server implementation for handling Winget package management operations
through the Model Context Protocol. It sets up the server, registers tools, and handles tool execution.

Author: Ron Webb
Since: 1.0.0
"""

import asyncio
from typing import Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource, ErrorData
from mcp.shared.exceptions import McpError
from mcp_server_winget.controller import get_controller_registry, execute_tool
from mcp_server_winget.util import setup_logger, get_project_info

logger = setup_logger(__name__)

app = Server("Winget Server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools in the Winget server.

    Returns:
        list[Tool]: List of available tools and their descriptions.
    """
    logger.info("Listing available tools")
    tools = [controller.tool() for controller in get_controller_registry()]
    logger.info("Found %d tools", len(tools))
    return tools

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
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
        result = execute_tool(name, arguments)
        logger.debug("Tool execution successful")
        return result
    except Exception as e:
        logger.error("Error executing tool %s: %s", name, str(e))
        raise McpError(ErrorData(message=f"An error occurred: {str(e)}", code=500)) from e

async def main():
    """Main entry point for the Winget server.

    This function initializes and runs the server, handling stdio communication
    and server lifecycle.

    Raises:
        Exception: If there is an error during server execution.
    """

    project_info = get_project_info()
    logger.info("Starting %s", project_info)
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
    asyncio.run(main())
