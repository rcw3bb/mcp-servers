"""
Unit tests for url_encode service method.

Author: Ron Webb
Since: 1.2.0
"""
from mcp_server_devkit.service import url_encode

class TestUrlEncode:
    """Tests for the url_encode function in the service module."""

    def test_url_encode_simple(self):
        assert url_encode("hello world") == "hello%20world"

    def test_url_encode_reserved_chars(self):
        assert url_encode("a/b?c=d&e=f") == "a%2Fb%3Fc%3Dd%26e%3Df"

    def test_url_encode_unicode(self):
        assert url_encode("café") == "caf%C3%A9"

    def test_url_encode_empty(self):
        assert url_encode("") == ""
