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
from .service import decode_jwt, generate_guid, url_encode, encode_base64, decode_base64


class EncodeBase64Controller(BaseController):
    """
    Controller for encoding a string to base64.

    Since: 1.3.0
    """

    name: str = "encode_base64"
    description: str = "Encodes a text string to base64."
    input_schema: Dict[str, Any] = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {"type": "string", "description": "The text to encode to base64."},
            "encoding": {
                "type": "string",
                "description": "The encoding to use (default: utf-8).",
                "nullable": True,
            },
        },
    }

    def execute(self, name: str, arguments: dict) -> Sequence[TextContent]:
        """
        Execute the encode_base64 tool.

        Args:
            name (str): The name of the tool to execute.
            arguments (dict): The arguments for the tool, must include 'text'.

        Returns:
            Sequence[TextContent]: A sequence of TextContent objects with the base64-encoded string.
        """
        text = arguments.get("text")
        encoding = arguments.get("encoding", "utf-8")
        if text is None:
            logger.error("Text is required but not provided")
            raise ValueError("Text is required.")
        try:
            encoded = encode_base64(text, encoding=encoding)
            logger.info("Base64-encoded value: %s", encoded)
            return [TextContent(type="text", text=encoded)]
        except Exception as exc:
            logger.error("Failed to encode base64: %s", exc)
            raise


class DecodeBase64Controller(BaseController):
    """
    Controller for decoding a base64-encoded string.

    Since: 1.3.0
    """

    name: str = "decode_base64"
    description: str = "Decodes a base64-encoded string to text."
    input_schema: Dict[str, Any] = {
        "type": "object",
        "required": ["b64_string"],
        "properties": {
            "b64_string": {
                "type": "string",
                "description": "The base64-encoded string to decode.",
            },
            "encoding": {
                "type": "string",
                "description": "The encoding to use for the output string (default: utf-8).",
                "nullable": True,
            },
        },
    }

    def execute(self, name: str, arguments: dict) -> Sequence[TextContent]:
        """
        Execute the decode_base64 tool.

        Args:
            name (str): The name of the tool to execute.
            arguments (dict): The arguments for the tool, must include 'b64_string'.

        Returns:
            Sequence[TextContent]: A sequence of TextContent objects with the decoded string.
        """
        b64_string = arguments.get("b64_string")
        encoding = arguments.get("encoding", "utf-8")
        if b64_string is None:
            logger.error("b64_string is required but not provided")
            raise ValueError("b64_string is required.")
        try:
            decoded = decode_base64(b64_string, encoding=encoding)
            logger.info("Base64-decoded value: %s", decoded)
            return [TextContent(type="text", text=decoded)]
        except Exception as exc:
            logger.error("Failed to decode base64: %s", exc)
            raise


class UrlEncodeController(BaseController):
    """
    Controller for URL encoding a string.

    Since: 1.2.0
    """

    name: str = "url_encode"
    description: str = "URL-encodes a string using percent-encoding."
    input_schema: Dict[str, Any] = {
        "type": "object",
        "required": ["value"],
        "properties": {
            "value": {"type": "string", "description": "The string to URL encode."}
        },
    }

    def execute(self, name: str, arguments: dict) -> Sequence[TextContent]:
        """
        Execute the url_encode tool.

        Args:
            name (str): The name of the tool to execute.
            arguments (dict): The arguments for the tool, must include 'value'.

        Returns:
            Sequence[TextContent]: A sequence of TextContent objects with the URL-encoded string.
        """
        value = arguments.get("value")
        if value is None:
            logger.error("Value is required but not provided")
            raise ValueError("Value is required.")
        encoded = url_encode(value)
        logger.info("URL-encoded value: %s", encoded)
        return [TextContent(type="text", text=encoded)]


logger = setup_logger(__name__)


class GenerateGuidController(BaseController):
    """
    Controller for generating GUIDs (UUID4) with an optional delimiter.

    Since: 1.1.0
    """

    name: str = "generate_guid"
    description: str = "Generates a random GUID (UUID4) with an optional delimiter."
    input_schema: Dict[str, Any] = {
        "type": "object",
        "required": [],
        "properties": {
            "delimiter": {
                "type": "string",
                "description": "Delimiter to use between UUID segments (optional).",
                "nullable": True,
            }
        },
    }

    def execute(self, name: str, arguments: dict) -> Sequence[TextContent]:
        """
        Execute the generate_guid tool.

        Args:
            name (str): The name of the tool to execute.
            arguments (dict): The arguments for the tool, may include 'delimiter'.

        Returns:
            Sequence[TextContent]: A sequence of TextContent objects with the generated GUID.
        """
        delimiter = arguments.get("delimiter")
        guid = generate_guid(delimiter=delimiter)
        logger.info("Generated GUID: %s", guid)
        return [TextContent(type="text", text=guid)]


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
        return (
            DecodeJWTController(),
            GenerateGuidController(),
            UrlEncodeController(),
            EncodeBase64Controller(),
            DecodeBase64Controller(),
        )

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
