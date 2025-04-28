import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
from mcp.types import Tool, TextContent, ErrorData
from mcp import McpError
from mcp_server_choco.server import list_tools, call_tool, main
from mcp_server_choco.controller import ListSourcesController

class TestServer(unittest.TestCase):
    @patch('mcp_server_choco.server.get_controller_registry')
    async def test_list_tools(self, mock_registry):
        # Setup mock
        controller = ListSourcesController()
        mock_registry.return_value = [controller]
        
        # Execute
        tools = await list_tools()
        
        # Assert
        self.assertEqual(len(tools), 1)
        self.assertIsInstance(tools[0], Tool)
        self.assertEqual(tools[0].name, "list_sources")

    @patch('mcp_server_choco.server.execute_tool')
    async def test_call_tool_success(self, mock_execute):
        # Setup mock
        mock_execute.return_value = [TextContent(type="text", text="test output")]
        
        # Execute
        result = await call_tool("test_tool", {"arg": "value"})
        
        # Assert
        mock_execute.assert_called_once_with("test_tool", {"arg": "value"})
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], TextContent)
        self.assertEqual(result[0].text, "test output")

    @patch('mcp_server_choco.server.execute_tool')
    async def test_call_tool_error(self, mock_execute):
        # Setup mock to raise an error
        mock_execute.side_effect = Exception("Tool execution failed")
        
        # Assert error is raised
        with self.assertRaises(McpError) as context:
            await call_tool("test_tool", {})
        self.assertEqual(context.exception.error, ErrorData(message="An error occurred: Tool execution failed", code=500))

    @patch('mcp_server_choco.server.stdio_server')
    @patch('mcp_server_choco.server.app')
    async def test_main_success(self, mock_app, mock_stdio):
        # Setup mocks
        mock_read_stream = AsyncMock()
        mock_write_stream = AsyncMock()
        mock_stdio.return_value.__aenter__.return_value = (mock_read_stream, mock_write_stream)
        mock_app.create_initialization_options.return_value = {}
        mock_app.run = AsyncMock()
        
        # Execute
        await main()
        
        # Assert
        mock_app.run.assert_awaited_once_with(
            mock_read_stream,
            mock_write_stream,
            {}
        )

    @patch('mcp_server_choco.server.stdio_server')
    @patch('mcp_server_choco.server.app')
    async def test_main_error(self, mock_app, mock_stdio):
        # Setup mock to raise an error
        mock_app.run = AsyncMock(side_effect=Exception("Server error"))
        mock_read_stream = AsyncMock()
        mock_write_stream = AsyncMock()
        mock_stdio.return_value.__aenter__.return_value = (mock_read_stream, mock_write_stream)
        
        # Assert error is raised
        with self.assertRaises(Exception) as context:
            await main()
        self.assertEqual(str(context.exception), "Server error")

def async_test(coro):
    def wrapper(*args, **kwargs):
        return asyncio.run(coro(*args, **kwargs))
    return wrapper

# Apply async_test decorator to async test methods
TestServer.test_list_tools = async_test(TestServer.test_list_tools)
TestServer.test_call_tool_success = async_test(TestServer.test_call_tool_success)
TestServer.test_call_tool_error = async_test(TestServer.test_call_tool_error)
TestServer.test_main_success = async_test(TestServer.test_main_success)
TestServer.test_main_error = async_test(TestServer.test_main_error)

if __name__ == '__main__':
    unittest.main()