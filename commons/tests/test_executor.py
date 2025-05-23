"""
Merged tests for mcp_commons.executor logic and importability.

Author: Ron Webb
Since: 1.0.0
"""
import pytest
from mcp_commons.executor import execute_tool
from mcp_commons.config import McpConfig
from mcp_commons.controller import BaseController, AbstractControllerRegistry
from mcp_commons.exception import McpCommonsError
from mcp import McpError
from mcp.types import TextContent, ErrorData

def test_executor_import():
    """Test that executor module can be imported."""
    import mcp_commons.executor

def test_executor_importable():
    import mcp_commons.executor

class DummyController(BaseController):
    name: str = "dummy"
    description: str = "Dummy controller"
    input_schema: dict = {}
    def execute(self, name: str, arguments: dict) -> list[TextContent]:
        if arguments.get("fail"):
            raise McpCommonsError("fail")
        if arguments.get("error"):
            raise Exception("boom")
        return [TextContent(type="text", text="ok")]

class DummyRegistry(AbstractControllerRegistry):
    def get_registry(self):
        return [DummyController()]

def make_config():
    return McpConfig(controller_registry=DummyRegistry())

def test_execute_tool_success():
    config = make_config()
    result = execute_tool("dummy", {}, config)
    assert isinstance(result, list)
    assert result[0].text == "ok"

def test_execute_tool_mcp_commons_error():
    config = make_config()
    result = execute_tool("dummy", {"fail": True}, config)
    assert isinstance(result, list)
    assert "fail" in result[0].text

def test_execute_tool_general_error():
    config = make_config()
    with pytest.raises(McpError) as exc:
        execute_tool("dummy", {"error": True}, config)
    assert exc.value.error.message == "boom"
    assert exc.value.error.code == 500

def test_execute_tool_unknown():
    config = make_config()
    with pytest.raises(McpError) as exc:
        execute_tool("notfound", {}, config)
    assert exc.value.error.message == "Unknown tool."
    assert exc.value.error.code == 404
