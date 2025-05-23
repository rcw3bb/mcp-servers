"""mcp_commons package initialization.

Author: Ron Webb
Since: 1.0.0
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("mcp_commons")
except PackageNotFoundError:
    __version__ = "unknown"

__author__ = "Ron Webb"
