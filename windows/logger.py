"""
Logger configuration module for the MQTT to LINE messaging system.
"""
import logging
import os
import sys
from datetime import datetime

# Create logs directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(log_dir, exist_ok=True)

def setup_logger(name, log_level=logging.INFO, console_output=True, file_output=False):
    """
    Configure and return a logger with the specified name.
    
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
    
    # Add file handler if requested
    if file_output:
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(log_dir, f"{name}_{today}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger