"""
Test for generate_guid in service module.
Author: Ron Webb
Since: 1.1.0
"""
import re
from mcp_server_devkit.service import generate_guid

class TestGenerateGuidService:
    """Test cases for generate_guid service method."""

    def test_generate_guid_default(self):
        guid = generate_guid(None)
        assert re.match(r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$", guid)

    def test_generate_guid_with_delimiter(self):
        delimiter = ":"
        guid = generate_guid(delimiter)
        assert delimiter in guid
        assert "-" not in guid
        assert len(guid.split(delimiter)) == 5
