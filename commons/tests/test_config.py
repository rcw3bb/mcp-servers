"""
Test module for mcp_commons.config.

Author: Ron Webb
Since: 1.0.0
"""

from mcp_commons.config import McpConfig
from mcp_commons.controller import AbstractControllerRegistry

def test_mcp_config_defaults():
    """Test default values of McpConfig."""
    config = McpConfig()
    assert config.server_name == "MCP Server"
    assert config.server_version is None
    assert isinstance(config.controller_registry, AbstractControllerRegistry)

def test_mcp_config_custom_values():
    """Test custom initialization of McpConfig."""
    class DummyRegistry(AbstractControllerRegistry):
        def get_registry(self):
            return []
    config = McpConfig(server_name="Custom", server_version="2.0", controller_registry=DummyRegistry())
    assert config.server_name == "Custom"
    assert config.server_version == "2.0"
    assert isinstance(config.controller_registry, AbstractControllerRegistry)
