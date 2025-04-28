"""Utility module providing shared functionality across the mcp_server_choco package.

This module contains utility functions that are used by other modules in the package,
primarily focused on logging setup and configuration to ensure consistent logging
behavior throughout the application.

Author: Ron Webb
Since: 1.0.0
"""

import logging

def setup_logger(name: str) -> logging.Logger:
    """
    Set up and return a logger with consistent configuration.

    Args:
        name: The name of the logger to create

    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler('mcp_server_choco.log')

    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(log_format)
    file_handler.setFormatter(log_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
