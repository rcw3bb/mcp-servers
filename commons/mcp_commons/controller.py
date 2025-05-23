"""Controllers module for handling tool execution and controller management.

This module provides controller implementations for various tool operations. Each controller
implements a specific tool functionality and handles the execution of commands through the service layer.

Author: Ron Webb
Since: 1.0.0
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any
from pydantic import BaseModel
from mcp.types import Tool, TextContent
from mcp_commons.exception import McpCommonsError
from .util import setup_logger

logger = setup_logger(__name__)


class BaseController(BaseModel):
    """Base class for all controllers.

    Attributes:
        name (str): The name of tool.
        description (str): A brief description of the tool's functionality.
        input_schema (dict[str, Any]): The JSON schema for the input arguments.
    """

    name: str
    description: str
    input_schema: dict[str, Any]

    def tool(self) -> Tool:
        """Create a Tool object representing this controller.

        Returns:
            Tool: A Tool object with valid name, description, and input schema.
        """

        logger.debug("Creating tool for controller: %s", self.name)
        return Tool(
            name=self.name, description=self.description, inputSchema=self.input_schema
        )

    def can_execute(self, name: str) -> bool:
        """Check if this controller can execute a given tool name.

        Args:
            name (str): The name of the tool to check.

        Returns:
            bool: True if the controller can execute the tool, False otherwise.
        """
        can_exec = self.name == name
        logger.debug(
            "Checking if controller %s can execute %s: %s",
            self.name,
            name,
            can_exec,
        )
        return can_exec

    def execute(self, name: str, arguments: dict) -> Sequence[TextContent]:
        """Execute the tool with the given name and arguments.

        Args:
            name (str): The name of the tool to execute.
            arguments (dict): The arguments for the tool.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement execute method")


class AbstractControllerRegistry(ABC):
    """Abstract base class for controller registries.

    Any implementation must provide the get_registry() method.
    """

    @abstractmethod
    def get_registry(self) -> Sequence[BaseController]:
        """Return a tuple of all controller instances in the registry.

        Returns:
            tuple: A tuple containing all controller instances.
        """
        raise NotImplementedError("Subclasses must implement get_registry method.")

    def error_handler(
        self,
        exception: McpCommonsError,
        controller: BaseController,  # pylint: disable=unused-argument
        tool_name: str,  # pylint: disable=unused-argument
        arguments: dict,  # pylint: disable=unused-argument
    ) -> list[TextContent]:
        """Handle MCP Commons errors.

        Args:
            exception (McpCommonsError): The exception to handle.
            controller (BaseController): The controller that encountered the error.
            tool_name (str): The name of the tool that encountered the error.
            arguments (dict): The arguments that were passed to the tool.

        Returns:
            list[TextContent]: A list containing a TextContent object with the error message.
        """
        return [TextContent(type="text", text=str(exception))]


class EmptyControllerRegistry(AbstractControllerRegistry):
    """Default implementation of ControllerRegistry."""

    def get_registry(self) -> Sequence[BaseController]:
        """Return a tuple of all registered controllers.

        Returns:
            tuple: A tuple containing all registered controller instances.
        """
        return ()
