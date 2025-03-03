"""
Logger configuration module for the MQTT to LINE messaging system.
Uses TimedRotatingFileHandler for automatic log rotation with reliable cleanup.
"""
import os
import sys

sys_path = sys.path
curr_folder = os.path.abspath(os.path.dirname(__file__))
if curr_folder not in sys_path:
    sys.path.insert(0, curr_folder)

import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from dotenv import load_dotenv

import config
from .discord_bot_handler import DiscordBotHandler

load_dotenv()

# Create logs directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs")
os.makedirs(log_dir, exist_ok=True)

# To prevent bot being init multiple times
discord_handler = None
if config.ENABLE_DISOCRD_BOT_LOGGING:
    # Launch only 1 discord bot
    bot_token = os.environ.get("DISCORD_BOT_TOKEN")
    channel_id = os.environ.get("DISCORD_CHANNEL_ID")
    if bot_token is None or channel_id is None:
        print("Please set DISCORD_BOT_TOKEN and DISCORD_CHANNEL_ID environment variables.")
    else:
        discord_handler = DiscordBotHandler(
            bot_token=bot_token,
            channel_id=channel_id
        )
        # Create Discord-specific formatter
        discord_formatter = logging.Formatter(
            '%(asctime)s - **%(levelname)s** - `%(message)s`',
            '%Y-%m-%d %H:%M:%S'
        )

        # Set the specific log level for the Discord handler
        discord_handler.setLevel(config.BOT_LOG_LEVEL)
        discord_handler.setFormatter(discord_formatter)

def setup_logger(name,
        console_log_level=logging.INFO, console_output=True,
        file_log_level=logging.DEBUG, file_output=True,
        dc_output=True):
    """
    Configure and return a logger with the specified name.
    Uses TimedRotatingFileHandler to automatically rotate logs by time.

    Args:
        name (str): The name of the logger
        console_log_level (int): The logging level for console output (default: logging.INFO)
        console_output (bool): Whether to output logs to console
        file_log_level (int): The logging level for file output (default: logging.DEBUG)
        file_output (bool): Whether to output logs to file
        dc_output (bool): Whether to output logs to DC Bot

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)


    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    logger.setLevel(logging.DEBUG)

    # Add console handler if requested
    if console_output:
        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d - %(name)-10s - %(levelname)-5s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(console_log_level)
        logger.addHandler(console_handler)

    # Add timed rotating file handler if requested
    if file_output:
        log_file = os.path.join(log_dir, f"{name}.log")
        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d - %(name)-10s - %(levelname)-5s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
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
        file_handler.setLevel(file_log_level)

        # Standard log rotation suffix - this is important for proper cleanup
        # Don't modify this unless you also modify the namer and rotator functions
        # file_handler.suffix = "%Y-%m-%d-%H-%M-%S"

        logger.addHandler(file_handler)

    # Add Discord Bot Handler For logs at specified level
    if dc_output and config.ENABLE_DISOCRD_BOT_LOGGING and discord_handler:
        logger.addHandler(discord_handler)

    return logger