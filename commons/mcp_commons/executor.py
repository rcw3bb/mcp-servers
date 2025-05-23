"""Executor module for tool execution logic.

This module provides the execute_tool function, which is responsible for dispatching tool execution
to the appropriate controller.

Author: Ron Webb
Since: 1.0.0
"""

from collections.abc import Sequence
from mcp import (
    McpError,
)
from mcp.types import (
    TextContent,
    ErrorData,
)
from mcp_commons.config import McpConfig
from mcp_commons.exception import McpCommonsError
from .util import setup_logger


def execute_tool(
    name: str,
    arguments: dict,
    config: McpConfig,
) -> Sequence[TextContent]:
    """Execute a tool by its name with the provided arguments.

    Args:
        name (str): The name of the tool to execute.
        arguments (dict): A dictionary of arguments to pass to the tool.
        config (McpConfig): The MCP server configuration instance.

    Returns:
        Sequence[TextContent]: The result of the tool execution as a sequence of TextContent objects.

    Raises:
        McpError: If the tool is not found or an error occurs during execution.
    """

    logger = setup_logger(__name__)

    controller_registry = config.controller_registry

    logger.debug("Looking for controller to execute tool: %s", name)
    for controller in controller_registry.get_registry():
        if controller.can_execute(name):
            logger.info("Found controller %s for tool %s", controller.name, name)
            try:
                return controller.execute(name, arguments)
            except McpCommonsError as e:
                return controller_registry.error_handler(e, controller, name, arguments)
            except Exception as e:
                logger.error("Error executing tool %s: %s", name, str(e))
                raise McpError(ErrorData(message=str(e), code=500)) from e
    logger.error("No controller found for tool: %s", name)
    raise McpError(ErrorData(message="Unknown tool.", code=404))
