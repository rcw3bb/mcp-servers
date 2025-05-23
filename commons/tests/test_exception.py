"""
Test module for mcp_commons.exception.

Author: Ron Webb
Since: 1.0.0
"""

import pytest
from mcp_commons.exception import McpCommonsError

def test_mcp_commons_error_message():
    """Test that McpCommonsError sets the message attribute."""
    err = McpCommonsError("test error")
    assert str(err) == "test error"
    assert err.message == "test error"
