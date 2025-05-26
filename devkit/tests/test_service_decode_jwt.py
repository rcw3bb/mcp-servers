"""
Unit tests for the service module.

Author: Ron Webb
Since: 1.0.0
"""

import pytest
from mcp_server_devkit import service
import base64
import json


def create_jwt(payload: dict) -> str:
    """
    Helper to create a fake JWT token with the given payload (no signature).
    """
    header = base64.urlsafe_b64encode(json.dumps({"alg": "none", "typ": "JWT"}).encode()).rstrip(b'=').decode()
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()
    return f"{header}.{payload_b64}."


def test_decode_jwt_valid():
    payload = {"user": "ron", "role": "admin"}
    token = create_jwt(payload)
    decoded = service.decode_jwt(token)
    assert decoded.headers["alg"] == "none"
    assert decoded.headers["typ"] == "JWT"
    assert decoded.data == payload
    assert decoded.signature == ""


def test_decode_jwt_invalid_format():
    with pytest.raises(ValueError):
        service.decode_jwt("invalidtoken")


def test_decode_jwt_invalid_payload():
    # Invalid base64 in payload
    token = "aW52YWxpZA==.!!!."
    with pytest.raises(ValueError):
        service.decode_jwt(token)

def test_decode_jwt_with_certificate(monkeypatch):
    """
    Test decode_jwt with a PEM certificate (mocked extraction and verification).
    """
    token = (
        "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJ1c2VyIjoicm9uIn0."
        "c2lnbmF0dXJl"
    )
    cert = "-----BEGIN CERTIFICATE-----\nFAKECERTDATA\n-----END CERTIFICATE-----"
    # Patch _extract_public_key_from_certificate and _verify_jwt_signature
    monkeypatch.setattr(service, "_extract_public_key_from_certificate", lambda c: "FAKEPUBKEY")
    monkeypatch.setattr(service, "_verify_jwt_signature", lambda p, h, s, k: True)
    decoded = service.decode_jwt(token, certificate=cert)
    assert decoded.signature_verified is True

def test_decode_jwt_with_public_key(monkeypatch):
    """
    Test decode_jwt with a PEM public key (mocked verification).
    """
    token = (
        "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJ1c2VyIjoicm9uIn0."
        "c2lnbmF0dXJl"
    )
    pubkey = "-----BEGIN PUBLIC KEY-----\nFAKEPUBKEYDATA\n-----END PUBLIC KEY-----"
    monkeypatch.setattr(service, "_verify_jwt_signature", lambda p, h, s, k: True)
    decoded = service.decode_jwt(token, public_key=pubkey)
    assert decoded.signature_verified is True

def test_decode_jwt_signature_verification_fail(monkeypatch):
    """
    Test decode_jwt when signature verification fails (mocked).
    """
    token = (
        "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJ1c2VyIjoicm9uIn0."
        "c2lnbmF0dXJl"
    )
    pubkey = "-----BEGIN PUBLIC KEY-----\nFAKEPUBKEYDATA\n-----END PUBLIC KEY-----"
    def fail_verify(*args, **kwargs):
        raise Exception("Invalid signature")
    monkeypatch.setattr(service, "_verify_jwt_signature", fail_verify)
    decoded = service.decode_jwt(token, public_key=pubkey)
    assert decoded.signature_verified is False

def test_decode_jwt_invalid_parts():
    """
    Test decode_jwt with a token that does not have 3 parts.
    """
    with pytest.raises(ValueError, match="Invalid JWT token format"):
        service.decode_jwt("header.payload")

def test_decode_jwt_invalid_json_in_header():
    """
    Test decode_jwt with invalid JSON in header segment.
    """
    # 'aW52YWxpZA' is base64 for 'invalid', which is not JSON
    token = "aW52YWxpZA.."
    with pytest.raises(ValueError):
        service.decode_jwt(token)

def test_decode_jwt_invalid_json_in_payload():
    """
    Test decode_jwt with invalid JSON in payload segment.
    """
    import base64, json
    header = base64.urlsafe_b64encode(json.dumps({"alg": "none"}).encode()).rstrip(b'=').decode()
    token = f"{header}.aW52YWxpZA."
    with pytest.raises(ValueError):
        service.decode_jwt(token)

def test_decode_jwt_certificate_formatting(monkeypatch):
    """
    Test decode_jwt auto-wraps certificate with PEM headers.
    """
    token = (
        "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJ1c2VyIjoicm9uIn0."
        "c2lnbmF0dXJl"
    )
    # Patch extraction and verification
    monkeypatch.setattr(service, "_extract_public_key_from_certificate", lambda c: "FAKEPUBKEY")
    monkeypatch.setattr(service, "_verify_jwt_signature", lambda p, h, s, k: True)
    # Pass a cert string without PEM headers
    cert = "FAKECERTDATA"
    decoded = service.decode_jwt(token, certificate=cert)
    assert decoded.signature_verified is True

def test_decode_jwt_public_key_formatting(monkeypatch):
    """
    Test decode_jwt auto-wraps public key with PEM headers.
    """
    token = (
        "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJ1c2VyIjoicm9uIn0."
        "c2lnbmF0dXJl"
    )
    monkeypatch.setattr(service, "_verify_jwt_signature", lambda p, h, s, k: True)
    pubkey = "FAKEPUBKEYDATA"
    decoded = service.decode_jwt(token, public_key=pubkey)
    assert decoded.signature_verified is True

def test_extract_public_key_from_certificate_error():
    """
    Test _extract_public_key_from_certificate raises ValueError on error.
    """
    with pytest.raises(ValueError):
        service._extract_public_key_from_certificate("not a cert")

def test_verify_jwt_signature_unsupported_alg():
    """
    Test _verify_jwt_signature raises ValueError for unsupported algorithm.
    """
    import base64
    valid_sig = base64.urlsafe_b64encode(b"sig").rstrip(b'=').decode()
    parts = ["a", "b", valid_sig]
    headers = {"alg": "XYZ"}
    with pytest.raises(ValueError, match="Unsupported or insecure JWT algorithm"):
        service._verify_jwt_signature(parts, headers, valid_sig, "key")

def test_verify_jwt_signature_hmac_invalid():
    """
    Test _verify_jwt_signature with HMAC and invalid signature.
    """
    import base64, json
    import hashlib
    import hmac
    parts = [
        base64.urlsafe_b64encode(json.dumps({"alg": "HS256"}).encode()).rstrip(b'=').decode(),
        base64.urlsafe_b64encode(json.dumps({"foo": "bar"}).encode()).rstrip(b'=').decode(),
        base64.urlsafe_b64encode(b"bad_signature").rstrip(b'=').decode(),
    ]
    headers = {"alg": "HS256"}
    signature = parts[2]
    # Use wrong key so signature won't match
    with pytest.raises(ValueError, match="Invalid JWT signature"):
        service._verify_jwt_signature(parts, headers, signature, "wrongkey")

def test_verify_jwt_signature_rsa_unsupported(monkeypatch):
    """
    Test _verify_jwt_signature with unsupported RSA algorithm.
    """
    import base64
    valid_sig = base64.urlsafe_b64encode(b"sig").rstrip(b'=').decode()
    parts = ["a", "b", valid_sig]
    headers = {"alg": "RS999"}
    with pytest.raises(ValueError, match="Unsupported RSA/PS algorithm"):
        service._verify_jwt_signature(parts, headers, valid_sig, "key")

def test_verify_jwt_signature_ps(monkeypatch):
    """
    Test _verify_jwt_signature with PS algorithm and verification error.
    """
    import base64, json
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import hashes
    # Generate a test key
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pubkey = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    header = base64.urlsafe_b64encode(json.dumps({"alg": "PS256"}).encode()).rstrip(b'=').decode()
    payload = base64.urlsafe_b64encode(json.dumps({"foo": "bar"}).encode()).rstrip(b'=').decode()
    signature = base64.urlsafe_b64encode(b"bad_signature").rstrip(b'=').decode()
    parts = [header, payload, signature]
    headers = {"alg": "PS256"}
    # Should raise ValueError due to invalid signature
    with pytest.raises(ValueError, match="Invalid JWT signature"):
        service._verify_jwt_signature(parts, headers, signature, pubkey)
