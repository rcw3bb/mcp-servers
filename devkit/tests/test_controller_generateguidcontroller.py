"""
Test for GenerateGuidController in controller module.
Author: Ron Webb
Since: 1.1.0
"""
import re
import pytest
from mcp_server_devkit.controller import GenerateGuidController

class TestGenerateGuidController:
    """Test cases for GenerateGuidController."""

    def test_execute_default(self):
        controller = GenerateGuidController()
        result = controller.execute("generate_guid", {})
        guid = result[0].text
        # UUID4 pattern: 8-4-4-4-12 hex digits
        assert re.match(r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$", guid)

    def test_execute_with_delimiter(self):
        controller = GenerateGuidController()
        delimiter = ":"
        result = controller.execute("generate_guid", {"delimiter": delimiter})
        guid = result[0].text
        # Should not contain dashes, should contain delimiter
        assert delimiter in guid
        assert "-" not in guid
        # Should have 5 segments
        assert len(guid.split(delimiter)) == 5
