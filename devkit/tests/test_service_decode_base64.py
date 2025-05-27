"""
Unit tests for decode_base64 service method.

Author: Ron Webb
Since: 1.3.0
"""
import pytest
from mcp_server_devkit.service import decode_base64

class TestDecodeBase64:
    """Tests for the decode_base64 function in the service module."""

    def test_decode_base64_default_utf8(self):
        assert decode_base64("aGVsbG8=") == "hello"

    def test_decode_base64_with_encoding_utf8(self):
        assert decode_base64("Y2Fmw6k=", encoding="utf-8") == "café"

    def test_decode_base64_with_encoding_ascii(self):
        assert decode_base64("aGVsbG8=", encoding="ascii") == "hello"

    def test_decode_base64_empty(self):
        assert decode_base64("") == ""

    def test_decode_base64_invalid_encoding(self):
        with pytest.raises(LookupError):
            decode_base64("aGVsbG8=", encoding="invalid-enc")

    def test_decode_base64_invalid_base64(self):
        with pytest.raises(Exception):
            decode_base64("not_base64!!")
