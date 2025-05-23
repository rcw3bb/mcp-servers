"""
Merged tests for mcp_commons.server including entry, logic, list_tools, and call_tool endpoints.

Author: Ron Webb
Since: 1.0.0
"""
import pytest
import asyncio
from mcp_commons import server
from mcp_commons.server import main
from mcp_commons.config import McpConfig
from mcp_commons.controller import BaseController, AbstractControllerRegistry
from mcp.types import Tool, TextContent

# Dummy controller and registry for all tests
class DummyController(BaseController):
    name: str = "dummy"
    description: str = "Dummy controller"
    input_schema: dict = {}
    def tool(self):
        return Tool(name=self.name, description=self.description, inputSchema=self.input_schema)
    def can_execute(self, name: str) -> bool:
        return name == self.name
    def execute(self, name: str, arguments: dict):
        if arguments.get("fail"): raise Exception("fail")
        return [TextContent(type="text", text="ok")]

class DummyRegistry(AbstractControllerRegistry):
    def get_registry(self):
        return [DummyController()]

def test_server_import():
    """Test that server module can be imported."""
    assert hasattr(server, "main")

def test_server_importable():
    import mcp_commons.server

def test_main_runs(monkeypatch):
    """Test that main() runs and completes the server lifecycle."""
    config = McpConfig(controller_registry=DummyRegistry())
    called = {}
    class DummyApp:
        def __init__(self, *a, **kw): pass
        def list_tools(self):
            def decorator(fn):
                called['list_tools'] = fn
                return fn
            return decorator
        def call_tool(self):
            def decorator(fn):
                called['call_tool'] = fn
                return fn
            return decorator
        def create_initialization_options(self):
            return {}
        async def run(self, *a, **kw):
            called['ran'] = True
    class DummyStream:
        async def __aenter__(self):
            return (None, None)
        async def __aexit__(self, exc_type, exc, tb):
            return False
    monkeypatch.setattr("mcp_commons.server.Server", DummyApp)
    monkeypatch.setattr("mcp_commons.server.stdio_server", lambda: DummyStream())
    monkeypatch.setattr("mcp_commons.server.execute_tool", lambda n, a, c: [TextContent(type="text", text="ok")])
    asyncio.run(server.main(config))
    assert 'list_tools' in called
    assert 'call_tool' in called
    assert 'ran' in called

def test_main_server_error(monkeypatch):
    """Test that main() logs and raises on server error."""
    config = McpConfig(controller_registry=DummyRegistry())
    class DummyApp:
        def __init__(self, *a, **kw): pass
        def list_tools(self):
            def decorator(fn): return fn
            return decorator
        def call_tool(self):
            def decorator(fn): return fn
            return decorator
        def create_initialization_options(self):
            return {}
        async def run(self, *a, **kw):
            raise RuntimeError("fail")
    class DummyStream:
        async def __aenter__(self):
            return (None, None)
        async def __aexit__(self, exc_type, exc, tb):
            return False
    monkeypatch.setattr("mcp_commons.server.Server", DummyApp)
    monkeypatch.setattr("mcp_commons.server.stdio_server", lambda: DummyStream())
    monkeypatch.setattr("mcp_commons.server.execute_tool", lambda n, a, c: [TextContent(type="text", text="ok")])
    with pytest.raises(RuntimeError):
        asyncio.run(server.main(config))

def test_main_list_tools(monkeypatch):
    """Test that main() registers and lists tools."""
    config = McpConfig(controller_registry=DummyRegistry())
    called = {}
    class DummyApp:
        def __init__(self, *a, **kw): pass
        def list_tools(self):
            def decorator(fn):
                called['list_tools'] = fn
                return fn
            return decorator
        def call_tool(self):
            def decorator(fn):
                called['call_tool'] = fn
                return fn
            return decorator
        def create_initialization_options(self):
            return {}
        async def run(self, *a, **kw):
            called['ran'] = True
    class DummyStream:
        async def __aenter__(self):
            return (None, None)
        async def __aexit__(self, exc_type, exc, tb):
            return False
    monkeypatch.setattr("mcp_commons.server.Server", DummyApp)
    monkeypatch.setattr("mcp_commons.server.stdio_server", lambda: DummyStream())
    monkeypatch.setattr("mcp_commons.server.execute_tool", lambda n, a, c: [])
    asyncio.run(main(config))
    assert 'list_tools' in called
    assert 'call_tool' in called
    assert 'ran' in called

def test_list_tools_logic(monkeypatch):
    """Test that list_tools endpoint returns the correct tool list."""
    config = McpConfig(controller_registry=DummyRegistry())
    tool_list = {}
    class DummyApp:
        def __init__(self, *a, **kw): pass
        def list_tools(self):
            def decorator(fn):
                tool_list['list_tools'] = fn
                return fn
            return decorator
        def call_tool(self):
            def decorator(fn): return fn
            return decorator
        def create_initialization_options(self):
            return {}
        async def run(self, *a, **kw):
            pass
    class DummyStream:
        async def __aenter__(self):
            return (None, None)
        async def __aexit__(self, exc_type, exc, tb):
            return False
    monkeypatch.setattr("mcp_commons.server.Server", DummyApp)
    monkeypatch.setattr("mcp_commons.server.stdio_server", lambda: DummyStream())
    monkeypatch.setattr("mcp_commons.server.execute_tool", lambda n, a, c: [])
    asyncio.run(main(config))
    list_tools_fn = tool_list.get('list_tools')
    assert list_tools_fn is not None
    result = asyncio.run(list_tools_fn())
    assert len(result) == 1
    assert result[0].name == "dummy"

def test_call_tool_logic(monkeypatch):
    """Test that call_tool endpoint executes the tool and returns the result."""
    config = McpConfig(controller_registry=DummyRegistry())
    call_result = {}
    class DummyApp:
        def __init__(self, *a, **kw): pass
        def list_tools(self):
            def decorator(fn): return fn
            return decorator
        def call_tool(self):
            def decorator(fn):
                async def wrapper(name, arguments):
                    result = await fn(name, arguments)
                    call_result['result'] = result
                    return result
                call_result['call_tool'] = wrapper
                return wrapper
            return decorator
        def create_initialization_options(self):
            return {}
        async def run(self, *a, **kw):
            pass
    class DummyStream:
        async def __aenter__(self):
            return (None, None)
        async def __aexit__(self, exc_type, exc, tb):
            return False
    monkeypatch.setattr("mcp_commons.server.Server", DummyApp)
    monkeypatch.setattr("mcp_commons.server.stdio_server", lambda: DummyStream())
    monkeypatch.setattr("mcp_commons.server.execute_tool", lambda n, a, c: [TextContent(type="text", text="ok")])
    asyncio.run(main(config))
    call_tool_fn = call_result.get('call_tool')
    assert call_tool_fn is not None
    result = asyncio.run(call_tool_fn("dummy", {}))
    assert isinstance(result, list)
    assert result[0].text == "ok"
