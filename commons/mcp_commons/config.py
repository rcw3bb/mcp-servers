"""
Configuration module for MCP Commons.

This module defines any configuration class for application configuration.

Author: Ron Webb
Since: 1.0.0
"""

from pydantic import BaseModel, Field
from .controller import AbstractControllerRegistry, EmptyControllerRegistry


class McpConfig(BaseModel):
    """Configuration class for MCP Commons."""

    server_name: str = "MCP Server"
    server_version: str | None = None
    controller_registry: AbstractControllerRegistry = Field(
        default_factory=EmptyControllerRegistry, exclude=True
    )

    model_config = {"arbitrary_types_allowed": True}
