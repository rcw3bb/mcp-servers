"""
Unit tests for DecodeBase64Controller.

Author: Ron Webb
Since: 1.3.0
"""
import pytest
from mcp_server_devkit.controller import DecodeBase64Controller
from mcp.types import TextContent

class TestDecodeBase64Controller:
    """Tests for the DecodeBase64Controller class."""

    def setup_method(self):
        self.controller = DecodeBase64Controller()

    def test_decode_base64_default_utf8(self):
        args = {"b64_string": "aGVsbG8="}
        result = self.controller.execute("decode_base64", args)
        assert isinstance(result, list)
        assert result[0].text == "hello"

    def test_decode_base64_with_encoding_utf8(self):
        args = {"b64_string": "Y2Fmw6k=", "encoding": "utf-8"}
        result = self.controller.execute("decode_base64", args)
        assert result[0].text == "café"

    def test_decode_base64_with_encoding_ascii(self):
        args = {"b64_string": "aGVsbG8=", "encoding": "ascii"}
        result = self.controller.execute("decode_base64", args)
        assert result[0].text == "hello"

    def test_decode_base64_empty(self):
        args = {"b64_string": ""}
        result = self.controller.execute("decode_base64", args)
        assert result[0].text == ""

    def test_decode_base64_invalid_encoding(self):
        args = {"b64_string": "aGVsbG8=", "encoding": "invalid-enc"}
        with pytest.raises(LookupError):
            self.controller.execute("decode_base64", args)

    def test_decode_base64_invalid_base64(self):
        args = {"b64_string": "not_base64!!"}
        with pytest.raises(Exception):
            self.controller.execute("decode_base64", args)

    def test_decode_base64_missing_b64_string(self):
        args = {}
        with pytest.raises(ValueError):
            self.controller.execute("decode_base64", args)
