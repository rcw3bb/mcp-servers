"""
MCP Server Winget package initialization.

Author: Ron Webb
Since: 2.0.0
"""

import os
import tomllib
from mcp_commons.config import McpConfig
from mcp_server_winget.controller import ControllerRegistry

with open(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "pyproject.toml"), "rb"
) as f:
    pyproject = tomllib.load(f)
    app_name = pyproject["project"]["name"]
    version = pyproject["project"]["version"]

mcp_config = McpConfig()
mcp_config.server_name = "Winget MCP Server"
mcp_config.server_version = version
mcp_config.controller_registry = ControllerRegistry()
