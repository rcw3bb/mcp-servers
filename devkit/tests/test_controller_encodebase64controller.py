"""
Unit tests for EncodeBase64Controller.

Author: Ron Webb
Since: 1.3.0
"""
import pytest
from mcp_server_devkit.controller import EncodeBase64Controller
from mcp.types import TextContent

class TestEncodeBase64Controller:
    """Tests for the EncodeBase64Controller class."""

    def setup_method(self):
        self.controller = EncodeBase64Controller()

    def test_encode_base64_default_utf8(self):
        args = {"text": "hello"}
        result = self.controller.execute("encode_base64", args)
        assert isinstance(result, list)
        assert result[0].text == "aGVsbG8="

    def test_encode_base64_with_encoding_utf8(self):
        args = {"text": "café", "encoding": "utf-8"}
        result = self.controller.execute("encode_base64", args)
        assert result[0].text == "Y2Fmw6k="

    def test_encode_base64_with_encoding_ascii(self):
        args = {"text": "hello", "encoding": "ascii"}
        result = self.controller.execute("encode_base64", args)
        assert result[0].text == "aGVsbG8="

    def test_encode_base64_empty(self):
        args = {"text": ""}
        result = self.controller.execute("encode_base64", args)
        assert result[0].text == ""

    def test_encode_base64_invalid_encoding(self):
        args = {"text": "hello", "encoding": "invalid-enc"}
        with pytest.raises(LookupError):
            self.controller.execute("encode_base64", args)

    def test_encode_base64_missing_text(self):
        args = {}
        with pytest.raises(ValueError):
            self.controller.execute("encode_base64", args)
