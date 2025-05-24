"""
Pydantic models for mcp_server_devkit.

Author: Ron Webb
Since: 1.0.0
"""

from typing import Any
from pydantic import BaseModel


class DecodedJWT(BaseModel):
    """
    Model representing a decoded JWT token.

    Attributes:
        headers (dict[str, Any]): JWT headers.
        data (dict[str, Any]): JWT payload.
        signature (str): JWT signature (base64url encoded).
        signature_verified (bool | None):
            True if signature is verified,
            False if verification failed,
            None if not checked.
    """

    headers: dict[str, Any]
    data: dict[str, Any]
    signature: str
    signature_verified: bool | None = None
