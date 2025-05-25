"""
Service module for mcp_server_devkit.

Author: Ron Webb
Since: 1.0.0
"""

import base64
import json
import hashlib
import hmac
import uuid
from typing import Any
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    load_pem_public_key,
)
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from .models import DecodedJWT


def generate_guid(delimiter: str | None) -> str:
    """
    Generates a random GUID (UUID4) as a string, with an optional delimiter between segments.

    Args:
        delimiter (str, optional): The delimiter to use between UUID segments. Defaults to no delimiter.

    Returns:
        str: The generated GUID as a string, with the specified delimiter.

    Since: 1.1.0
    """
    guid = str(uuid.uuid4())
    if delimiter:
        return delimiter.join(guid.split("-"))
    return guid


def decode_jwt(
    token: str, public_key: str = None, certificate: str = None
) -> DecodedJWT:
    """
    Decodes a JWT token. If public_key or certificate is provided, verifies the signature.

    Args:
        token (str): The JWT token to decode.
        public_key (str, optional): The PEM public key to verify the JWT signature.
        certificate (str, optional): The PEM certificate to extract the public key for verification.

    Returns:
        DecodedJWT: A Pydantic model with 'headers', 'data', and 'signature'.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid JWT token format.")

        def decode_segment(segment: str) -> Any:
            pad = "=" * (-len(segment) % 4)
            segment += pad
            return json.loads(base64.urlsafe_b64decode(segment).decode("utf-8"))

        headers = decode_segment(parts[0])
        data = decode_segment(parts[1])
        signature = parts[2]

        signature_verified = None
        pem_key = None
        if certificate is not None:
            cert = certificate.strip()
            if not cert.startswith("-----BEGIN CERTIFICATE-----"):
                cert = f"-----BEGIN CERTIFICATE-----\n{cert}\n-----END CERTIFICATE-----"
            pem_key = _extract_public_key_from_certificate(cert)
        elif public_key is not None:
            pem = public_key.strip()
            if not pem.startswith("-----BEGIN PUBLIC KEY-----"):
                pem = f"-----BEGIN PUBLIC KEY-----\n{pem}\n-----END PUBLIC KEY-----"
            pem_key = pem
        if pem_key:
            try:
                _verify_jwt_signature(parts, headers, signature, pem_key)
                signature_verified = True
            except Exception:  # pylint: disable=broad-except
                signature_verified = False
        return DecodedJWT(
            headers=headers,
            data=data,
            signature=signature,
            signature_verified=signature_verified,
        )
    except Exception as exc:
        raise ValueError(f"Failed to decode JWT: {exc}") from exc


def _extract_public_key_from_certificate(certificate: str) -> str:
    """
    Extracts the PEM public key from a PEM certificate.
    Args:
        certificate (str): The PEM certificate string.
    Returns:
        str: The PEM public key string.
    Raises:
        ValueError: If extraction fails.
    """
    try:
        cert = load_pem_x509_certificate(certificate.encode(), default_backend())
        pubkey_obj = cert.public_key()
        return pubkey_obj.public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
        ).decode()
    except Exception as exc:
        raise ValueError(
            f"Failed to extract public key from certificate: {exc}"
        ) from exc


def _verify_jwt_signature(
    parts: list[str], headers: dict, signature: str, public_key: str
) -> None:
    """
    Verifies the signature of a JWT token.

    Args:
        parts (list[str]): The JWT token split into header, payload, and signature.
        headers (dict): Decoded JWT headers.
        signature (str): The JWT signature (base64url encoded).
        public_key (str): The public key or secret for verification.

    Raises:
        ValueError: If the signature is invalid or the algorithm is unsupported.
        ImportError: If cryptography is required but not installed.
    """
    alg = headers.get("alg", "")
    signing_input = f"{parts[0]}.{parts[1]}".encode("utf-8")
    signature_bytes = base64.urlsafe_b64decode(signature + "=" * (-len(signature) % 4))

    if alg.startswith("HS"):
        # HMAC algorithms (HS256, HS384, HS512)
        hash_alg = {
            "HS256": hashlib.sha256,
            "HS384": hashlib.sha384,
            "HS512": hashlib.sha512,
        }.get(alg)
        if not hash_alg:
            raise ValueError(f"Unsupported HMAC algorithm: {alg}")
        expected_sig = hmac.new(public_key.encode(), signing_input, hash_alg).digest()
        if not hmac.compare_digest(expected_sig, signature_bytes):
            raise ValueError("Invalid JWT signature.")
    elif alg.startswith("RS") or alg.startswith("PS"):
        # RSA/PS algorithms (RS256, RS384, RS512, PS256, PS384, PS512)
        hash_alg = {
            "RS256": hashes.SHA256(),
            "RS384": hashes.SHA384(),
            "RS512": hashes.SHA512(),
            "PS256": hashes.SHA256(),
            "PS384": hashes.SHA384(),
            "PS512": hashes.SHA512(),
        }.get(alg)

        if not hash_alg:
            raise ValueError(f"Unsupported RSA/PS algorithm: {alg}")

        pubkey = load_pem_public_key(public_key.encode())
        try:
            if alg.startswith("RS"):
                pubkey.verify(
                    signature_bytes,
                    signing_input,
                    padding.PKCS1v15(),
                    hash_alg,
                )
            else:  # PS*
                pubkey.verify(
                    signature_bytes,
                    signing_input,
                    padding.PSS(
                        mgf=padding.MGF1(hash_alg),
                        salt_length=padding.PSS.MAX_LENGTH,
                    ),
                    hash_alg,
                )
        except Exception as exc:
            raise ValueError("Invalid JWT signature.") from exc
    else:
        raise ValueError(f"Unsupported or insecure JWT algorithm: {alg}")
