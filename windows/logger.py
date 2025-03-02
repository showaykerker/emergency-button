"""
Logger configuration module for the MQTT to LINE messaging system.
Uses TimedRotatingFileHandler for automatic log rotation with reliable cleanup.
"""
import logging
import os
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

import config

# Create logs directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(log_dir, exist_ok=True)

class SafeTimedRotatingFileHandler(TimedRotatingFileHandler):
    """
    A custom TimedRotatingFileHandler that ensures proper file cleanup
    while still allowing for custom formatters.
    """
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)

def setup_logger(name, log_level=logging.INFO, console_output=True, file_output=True):
    """
    Configure and return a logger with the specified name.
    Uses TimedRotatingFileHandler to automatically rotate logs by time.

    Args:
        name (str): The name of the logger
        log_level (int): The logging level (default: logging.INFO)
        console_output (bool): Whether to output logs to console
        file_output (bool): Whether to output logs to file

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Add console handler if requested
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Add timed rotating file handler if requested
    if file_output:
        log_file = os.path.join(log_dir, f"{name}.log")

        # Create a timed rotating file handler
        file_handler = TimedRotatingFileHandler(
            filename=log_file,
            when=config.LOG_ROTATE_WHEN,
            interval=config.LOG_ROTATE_INTERVAL,
            backupCount=config.LOG_ROTATE_BACKUPCOUNT,
            encoding='utf-8',
            delay=True  # Only open file when first record is emitted
        )

        # Apply the formatter to the file handler
        file_handler.setFormatter(formatter)

        # Standard log rotation suffix - this is important for proper cleanup
        # Don't modify this unless you also modify the namer and rotator functions
        # file_handler.suffix = "%Y-%m-%d-%H-%M-%S"

        logger.addHandler(file_handler)

    return logger