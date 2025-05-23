"""Exception module for the MCP server implementation.

This module provides custom exception classes used throughout the MCP server
for handling different types of errors in a structured way.

Author: Ron Webb
Since: 1.0.0
"""


class McpCommonsError(Exception):
    """Base exception for all MCP Commons errors.

    This is the base class for all exceptions that can be raised by the MCP Commons package.
    It provides a consistent way to handle errors throughout the package.

    Attributes:
        message (str): Explanation of the error.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
