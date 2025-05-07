"""Utility module providing shared functionality across the mcp_server_choco package.

This module contains utility functions that are used by other modules in the package,
primarily focused on logging setup and configuration to ensure consistent logging
behavior throughout the application.

Author: Ron Webb
Since: 1.0.0
"""

import logging
import tomllib
from pathlib import Path

def setup_logger(name: str) -> logging.Logger:
    """
    Set up and return a logger with consistent configuration.

    Args:
        name: The name of the logger to create

    Returns:
        A configured logger instance
    """
    log_level = logging.INFO

    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler('mcp_server_choco.log')

    console_handler.setLevel(log_level)
    file_handler.setLevel(log_level)

    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(log_format)
    file_handler.setFormatter(log_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

def get_project_info() -> str:
    """
    Read project information from pyproject.toml file.
    
    Returns:
        The name and version of the project as a string.
    """
    logger = setup_logger(__name__)
    name = "unknown"
    version = "unknown"

    try:
        project_root = Path(__file__).parent.parent
        pyproject_path = project_root / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)

        project_section = pyproject_data.get("project", {})
        name = project_section.get("name", "unknown")
        version = project_section.get("version", "unknown")
    except FileNotFoundError as e:
        logger.warning("pyproject.toml file not found: %s", str(e))
    except PermissionError as e:
        logger.warning("Permission error accessing pyproject.toml: %s", str(e))
    except tomllib.TOMLDecodeError as e:
        logger.warning("Failed to parse pyproject.toml: %s", str(e))
    except (KeyError, ValueError) as e:
        logger.warning("Error extracting project info from pyproject.toml: %s", str(e))

    return f"{name} v{version}"
