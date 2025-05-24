"""
Unit tests for the models module.

Author: Ron Webb
Since: 1.0.0
"""

import pytest
from mcp_server_devkit.models import DecodedJWT


def test_decoded_jwt_model_fields():
    """
    Test DecodedJWT model field assignment and defaults.
    """
    headers = {"alg": "HS256"}
    data = {"user": "ron"}
    signature = "abc123"
    model = DecodedJWT(headers=headers, data=data, signature=signature)
    assert model.headers == headers
    assert model.data == data
    assert model.signature == signature
    assert model.signature_verified is None


def test_decoded_jwt_signature_verified_values():
    """
    Test DecodedJWT signature_verified field with all possible values.
    """
    model_true = DecodedJWT(headers={}, data={}, signature="sig", signature_verified=True)
    model_false = DecodedJWT(headers={}, data={}, signature="sig", signature_verified=False)
    model_none = DecodedJWT(headers={}, data={}, signature="sig")
    assert model_true.signature_verified is True
    assert model_false.signature_verified is False
    assert model_none.signature_verified is None


def test_decoded_jwt_model_dump():
    """
    Test DecodedJWT model_dump_json method.
    """
    model = DecodedJWT(headers={"alg": "HS256"}, data={"user": "ron"}, signature="sig", signature_verified=True)
    json_str = model.model_dump_json()
    assert '"alg":"HS256"' in json_str
    assert '"user":"ron"' in json_str
    assert '"signature_verified":true' in json_str
