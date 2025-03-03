# Discord Logging Handler

A Python logging module that sends log messages to a Discord channel using a bot.

## Features

- Send log messages to a Discord channel in real-time
- Configure multiple loggers with different settings
- Automatic log rotation with TimedRotatingFileHandler
- Discord slash commands for managing logs:
  - `/delete_logs`: Delete the last N messages in the channel
  - `/delete_time_range`: Delete messages within a specified time range

## Installation

1. Install the required dependencies:

```bash
pip install discord python-dotenv
```

2. Set up your environment variables in a `.env` file:

```
DISCORD_BOT_TOKEN=your_bot_token_here
DISCORD_CHANNEL_ID=your_channel_id_here
```

## Usage

### Basic Usage

```python
from logger_module import setup_logger

# Create a logger
logger = setup_logger('my_application')

# Send logs
logger.debug("This is a DEBUG message")
logger.info("This is an INFO message")
logger.warning("This is a WARNING message")
logger.error("This is an ERROR message")
logger.critical("This is a CRITICAL message")
```

### Configuration Options

You can customize the logger behavior using the `setup_logger` function:

```python
logger = setup_logger(
    name='my_application',               # Logger name
    console_log_level=logging.INFO,      # Console logging level
    console_output=True,                 # Enable console output
    file_log_level=logging.DEBUG,        # File logging level
    file_output=True,                    # Enable file output
    dc_output=True                       # Enable Discord output, logging level configured in [config.py](../config.py).
)
```

### Configuration File

You can modify the behavior of the logger by editing the [config.py](../config.py) file:

```python
# Example config.py
ENABLE_DISOCRD_BOT_LOGGING = True       # Enable Discord bot logging
BOT_LOG_LEVEL = logging.WARNING         # Only send WARNING or higher to Discord

# Log rotation settings
LOG_ROTATE_WHEN = 'midnight'            # Rotate logs at midnight
LOG_ROTATE_INTERVAL = 1                 # Rotate every 1 day
LOG_ROTATE_BACKUPCOUNT = 7              # Keep 7 days of logs
```

## Discord Bot Setup

1. Create a Discord bot on the [Discord Developer Portal](https://discord.com/developers/applications)
2. Enable the "Message Content Intent" in the Bot section
3. Generate a Bot Token and add it to your environment variables
4. Invite the bot to your server with appropriate permissions:
   - Send Messages
   - Manage Messages (for the delete commands)
5. Create a channel for logs and copy the Channel ID

## Discord Slash Commands

The module provides two slash commands for managing log messages:

### `/delete_logs`

Delete the last N messages in the channel.

Parameters:
- `count`: Number of messages to delete (default: 5, max: 100)
- `all_users`: Whether to delete messages from all users or just the bot (default: True)

### `/delete_time_range`

Delete messages within a specified time range.

Parameters:
- `hours_ago`: Hours to look back (default: 0)
- `minutes_ago`: Minutes to look back (default: 0)
- `all_users`: Whether to delete messages from all users or just the bot (default: True)

## Module Structure

- `setup_logger.py`: Main module for configuring loggers
- `discord_bot_handler.py`: Discord bot handler implementation
- `commands.py`: Discord slash commands implementation
