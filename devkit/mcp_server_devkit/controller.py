"""
Controllers module for handling JWT operations.

This module provides controller implementations for JWT decoding.

Author: Ron Webb
Since: 1.0.0
"""

from collections.abc import Sequence
from typing import Any, Dict
from mcp_commons.util import setup_logger
from mcp_commons.controller import BaseController, AbstractControllerRegistry
from mcp_commons.exception import McpCommonsError
from mcp.types import TextContent
from .service import decode_jwt

logger = setup_logger(__name__)


class DecodeJWTController(BaseController):
    """
    Controller for decoding JWT tokens.
    """

    name: str = "decode_jwt"
    description: str = "Decodes a JWT token and returns its components."
    input_schema: Dict[str, Any] = {
        "type": "object",
        "required": ["token"],
        "properties": {
            "token": {"type": "string", "description": "The JWT token to decode."},
            "public_key": {
                "type": "string",
                "description": "The PEM public key to verify the JWT signature.",
                "nullable": True,
            },
            "certificate": {
                "type": "string",
                "description": "The PEM certificate to extract the public key for verification.",
                "nullable": True,
            },
        },
    }

    def execute(self, name: str, arguments: dict) -> Sequence[TextContent]:
        """
        Execute the decode_jwt tool.

        Args:
            name (str): The name of the tool to execute.
            arguments (dict): The arguments for the tool, must include 'token'.

        Returns:
            Sequence[TextContent]: A sequence of TextContent objects with the decoded JWT.
        """
        token = arguments.get("token")
        public_key = arguments.get("public_key")
        certificate = arguments.get("certificate")
        if not token:
            logger.error("Token is required but not provided")
            raise ValueError("Token is required.")
        logger.info("Decoding JWT token")
        try:
            decoded = decode_jwt(token, public_key=public_key, certificate=certificate)
            logger.debug(
                "Decoded JWT: headers=%s, data=%s, signature_verified=%s",
                decoded.headers,
                decoded.data,
                decoded.signature_verified,
            )
            return [TextContent(type="text", text=decoded.model_dump_json())]
        except Exception as exc:
            logger.error("Failed to decode JWT: %s", exc)
            raise


class ControllerRegistry(AbstractControllerRegistry):
    """
    Registry for managing controllers.
    """

    def get_registry(self) -> Sequence[BaseController]:
        """
        Get all registered controllers.

        Returns:
            Sequence[BaseController]: A sequence containing all available controller instances.
        """
        return (DecodeJWTController(),)

    def error_handler(
        self,
        exception: McpCommonsError,
        controller: BaseController,
        tool_name: str,
        arguments: dict,
    ) -> list[TextContent]:
        """
        Handle controller errors.

        Args:
            exception (McpCommonsError): The exception to handle.

        Returns:
            list[TextContent]: A list of TextContent objects describing the error.
        """
        raise exception
