"""
Merged tests for mcp_commons.controller and related logic.

Author: Ron Webb
Since: 1.0.0
"""
import pytest
from mcp_commons.controller import BaseController, AbstractControllerRegistry, EmptyControllerRegistry
from mcp_commons.exception import McpCommonsError
from mcp.types import TextContent

def test_controller_import():
    """Test that controller module can be imported."""
    import mcp_commons.controller

class DummyController(BaseController):
    name: str = "dummy"
    description: str = "Dummy controller"
    input_schema: dict = {}
    def execute(self, name: str, arguments: dict) -> list[TextContent]:
        return [TextContent(type="text", text="executed")]

def test_tool_method():
    ctrl = DummyController()
    tool = ctrl.tool()
    assert tool.name == "dummy"
    assert tool.description == "Dummy controller"
    assert tool.inputSchema == {}

def test_can_execute():
    ctrl = DummyController()
    assert ctrl.can_execute("dummy")
    assert not ctrl.can_execute("other")

def test_execute_raises():
    base = BaseController(name="base", description="desc", input_schema={})
    with pytest.raises(NotImplementedError):
        base.execute("base", {})

def test_abstract_registry_not_implemented():
    # Instantiating an abstract class without implementing abstract methods raises TypeError
    with pytest.raises(TypeError):
        class DummyRegistry(AbstractControllerRegistry):
            pass
        DummyRegistry()

def test_error_handler():
    reg = EmptyControllerRegistry()
    ctrl = DummyController()
    err = McpCommonsError("fail")
    result = reg.error_handler(err, ctrl, "dummy", {})
    assert isinstance(result, list)
    assert isinstance(result[0], TextContent)
