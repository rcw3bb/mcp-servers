"""
Unit tests for UrlEncodeController.

Author: Ron Webb
Since: 1.2.0
"""
import pytest
from mcp_server_devkit.controller import UrlEncodeController
from mcp.types import TextContent

class TestUrlEncodeController:
    """Tests for the UrlEncodeController class."""

    def setup_method(self):
        self.controller = UrlEncodeController()

    def test_execute_url_encode_simple(self):
        result = self.controller.execute("url_encode", {"value": "hello world"})
        assert isinstance(result, list)
        assert isinstance(result[0], TextContent)
        assert result[0].text == "hello%20world"

    def test_execute_url_encode_reserved(self):
        result = self.controller.execute("url_encode", {"value": "a/b?c=d&e=f"})
        assert result[0].text == "a%2Fb%3Fc%3Dd%26e%3Df"

    def test_execute_url_encode_unicode(self):
        result = self.controller.execute("url_encode", {"value": "café"})
        assert result[0].text == "caf%C3%A9"

    def test_execute_url_encode_empty(self):
        result = self.controller.execute("url_encode", {"value": ""})
        assert result[0].text == ""

    def test_execute_url_encode_missing_value(self):
        with pytest.raises(ValueError):
            self.controller.execute("url_encode", {})
