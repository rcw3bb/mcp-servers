"""
MCP Server Choco package initialization.

Author: Ron Webb
Since: 1.0.0
"""

import logging
import os
import tomli
from mcp_commons.config import McpConfig
from mcp_server_choco.controller import ControllerRegistry

with open(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "pyproject.toml"), "rb"
) as f:
    pyproject = tomli.load(f)
    app_name = pyproject["project"]["name"]
    version = pyproject["project"]["version"]

mcp_config = McpConfig()
mcp_config.server_name = "Chocolatey MCP Server"
mcp_config.server_version = version
mcp_config.controller_registry = ControllerRegistry()
