"""
Unit tests for the DecodeJWTController in the controller module.

Author: Ron Webb
Since: 1.0.0
"""

import pytest
from mcp_server_devkit.controller import DecodeJWTController

class DummyTextContent:
    def __init__(self, type, text):
        self.type = type
        self.text = text

def test_decode_jwt_controller_execute_valid(monkeypatch):
    """
    Test DecodeJWTController execute with valid token.
    """
    controller = DecodeJWTController()
    token = (
        "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0."
        "eyJ1c2VyIjoicm9uIn0."
    )
    # Patch TextContent to DummyTextContent for test
    monkeypatch.setattr("mcp_server_devkit.controller.TextContent", DummyTextContent)
    result = controller.execute("decode_jwt", {"token": token})
    assert isinstance(result, list)
    assert result[0].type == "text"
    assert '"user":"ron"' in result[0].text

def test_decode_jwt_controller_execute_missing_token():
    """
    Test DecodeJWTController execute with missing token argument.
    """
    controller = DecodeJWTController()
    with pytest.raises(ValueError):
        controller.execute("decode_jwt", {})
