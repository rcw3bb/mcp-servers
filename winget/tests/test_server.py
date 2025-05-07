import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp_server_winget.server import list_tools, call_tool, main

@pytest.mark.asyncio
class TestServer:
    @patch("mcp_server_winget.server.get_controller_registry")
    async def test_list_tools(self, mock_registry):
        mock_controller = MagicMock()
        mock_tool = Tool(name="test", description="test tool", inputSchema={})
        mock_controller.tool.return_value = mock_tool
        mock_registry.return_value = (mock_controller,)
        
        result = await list_tools()
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Tool)
        assert result[0].name == "test"
        assert result[0].description == "test tool"

    @patch("mcp_server_winget.server.execute_tool")
    async def test_call_tool_success(self, mock_execute):
        mock_execute.return_value = [TextContent(type="text", text="success")]
        result = await call_tool("test-tool", {"arg": "value"})
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].text == "success"
        mock_execute.assert_called_with("test-tool", {"arg": "value"})

    @patch("mcp_server_winget.server.execute_tool")
    async def test_call_tool_error(self, mock_execute):
        mock_execute.side_effect = Exception("test error")
        with pytest.raises(Exception):
            await call_tool("test-tool", {})

    @patch("mcp_server_winget.server.stdio_server")
    @patch("mcp_server_winget.server.app")
    async def test_main_success(self, mock_app, mock_stdio):
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = (AsyncMock(), AsyncMock())
        mock_stdio.return_value = mock_context
        mock_app.run = AsyncMock()
        mock_app.create_initialization_options.return_value = {}
        
        await main()
        mock_app.run.assert_called_once()

    @patch("mcp_server_winget.server.stdio_server")
    @patch("mcp_server_winget.server.app")
    async def test_main_error(self, mock_app, mock_stdio):
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = (AsyncMock(), AsyncMock())
        mock_stdio.return_value = mock_context
        mock_app.run.side_effect = Exception("test error")
        
        with pytest.raises(Exception):
            await main()