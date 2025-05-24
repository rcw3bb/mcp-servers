"""
Unit tests for the ControllerRegistry in the controller module.

Author: Ron Webb
Since: 1.0.0
"""

import pytest
from mcp_server_devkit.controller import DecodeJWTController, ControllerRegistry

def test_controller_registry_get_registry():
    """
    Test ControllerRegistry get_registry returns controllers.
    """
    registry = ControllerRegistry()
    controllers = registry.get_registry()
    assert isinstance(controllers, tuple)
    assert any(isinstance(c, DecodeJWTController) for c in controllers)

def test_controller_registry_error_handler_raises():
    """
    Test ControllerRegistry error_handler raises the exception.
    """
    registry = ControllerRegistry()
    class DummyException(Exception):
        pass
    with pytest.raises(DummyException):
        registry.error_handler(DummyException(), DecodeJWTController(), "decode_jwt", {})
