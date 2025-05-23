"""Utility module providing shared functionality.

This module contains utility functions that are used by other modules in the package,
primarily focused on logging setup and configuration to ensure consistent logging
behavior throughout the application.

Author: Ron Webb
Since: 1.0.0
"""

import logging
import logging.config
import os
import sys


def setup_logger(name: str) -> logging.Logger:
    """
    Set up and return a logger with consistent configuration.

    Args:
        name: The name of the logger to create

    Returns:
        A configured logger instance
    """

    def find_logging_ini(start_dir: str) -> str | None:
        current = start_dir
        while True:
            candidate = os.path.join(current, "logging.ini")
            if os.path.exists(candidate):
                return candidate
            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent
        return None

    main_script = os.path.abspath(sys.argv[0])
    search_dir = os.path.dirname(main_script)
    config_path = find_logging_ini(search_dir)
    if config_path is not None and os.path.exists(config_path):
        logging.config.fileConfig(config_path, disable_existing_loggers=False)
    else:
        # Fallback: basic config for test/dev environments
        logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(name)
    return logger
