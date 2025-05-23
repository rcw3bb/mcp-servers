"""
Merged tests for mcp_commons.util.

Author: Ron Webb
Since: 1.0.0
"""
import logging
import os
import pytest
from mcp_commons.util import setup_logger

def test_setup_logger_returns_logger():
    """Test that setup_logger returns a Logger instance."""
    commons_dir = os.path.dirname(os.path.dirname(__file__))
    ini_path = os.path.join(commons_dir, "logging.ini")
    if os.path.exists(ini_path):
        import shutil
        dst_path = os.path.join(os.getcwd(), "logging.ini")
        if os.path.abspath(ini_path) != os.path.abspath(dst_path):
            shutil.copy(ini_path, dst_path)
    logger = setup_logger("test_logger")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_logger"

def test_setup_logger_fallback(monkeypatch):
    """Test that setup_logger falls back to basicConfig if logging.ini is missing."""
    ini_path = os.path.join(os.getcwd(), "logging.ini")
    backup_path = ini_path + ".bak"
    if os.path.exists(ini_path):
        os.rename(ini_path, backup_path)
    try:
        logger = setup_logger("fallback_logger")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "fallback_logger"
    finally:
        if os.path.exists(backup_path):
            os.rename(backup_path, ini_path)
