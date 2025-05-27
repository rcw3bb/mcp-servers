"""
Unit tests for encode_base64 service method.

Author: Ron Webb
Since: 1.3.0
"""
import pytest
from mcp_server_devkit.service import encode_base64

class TestEncodeBase64:
    """Tests for the encode_base64 function in the service module."""

    def test_encode_base64_default_utf8(self):
        assert encode_base64("hello") == "aGVsbG8="

    def test_encode_base64_with_encoding_utf8(self):
        assert encode_base64("café", encoding="utf-8") == "Y2Fmw6k="

    def test_encode_base64_with_encoding_ascii(self):
        assert encode_base64("hello", encoding="ascii") == "aGVsbG8="

    def test_encode_base64_empty(self):
        assert encode_base64("") == ""

    def test_encode_base64_invalid_encoding(self):
        with pytest.raises(LookupError):
            encode_base64("hello", encoding="invalid-enc")
