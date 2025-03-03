"""
Discord Bot Handler for logging.

This module provides a logging.Handler implementation that sends
log messages to a Discord channel using a bot.
"""

import os
import sys

sys_path = sys.path
curr_folder = os.path.abspath(os.path.dirname(__file__))
if curr_folder not in sys_path:
    sys.path.insert(0, curr_folder)

import logging
import asyncio
import threading
import discord
from discord.ext import commands, tasks

from commands import register_commands

class DiscordBotHandler(logging.Handler):
    """
    A logging handler that sends log messages to a Discord channel.
    
    This handler starts a Discord bot in a separate thread and uses it to
    send log messages to a specified channel.
    """
    
    def __init__(self, bot_token, channel_id, level=logging.NOTSET):
        """
        Initialize the handler with bot token and channel ID.
        
        Args:
            bot_token (str): The Discord bot token
            channel_id (str or int): The Discord channel ID
            level (int, optional): The logging level. Defaults to logging.NOTSET.
        """
        super().__init__(level)
        self.bot_token = bot_token
        self.channel_id = int(channel_id)  # Channel IDs must be integers
        self.bot = None
        self.queue = asyncio.Queue()
        self.ready = asyncio.Event()
        self.commands_synced = False
        
        # Start the bot in a separate thread
        self.loop = asyncio.new_event_loop()
        self.thread = None
        self._start_bot_thread()
    
    def _start_bot_thread(self):
        """Starts the bot in a separate thread with its own event loop"""
        def run_bot():
            asyncio.set_event_loop(self.loop)
            intents = discord.Intents.default()
            intents.message_content = True
            self.bot = commands.Bot(command_prefix='!', intents=intents)
            
            # Register the commands
            register_commands(self.bot, self.channel_id)
            
            @self.bot.event
            async def on_ready():
                print(f'Bot connected as {self.bot.user}')
                print("Bot ready and accepting logs")
                
                self.ready.set()
                self.process_queue.start()
                
                # Start background command sync
                asyncio.create_task(self.sync_commands_background())
            
            @tasks.loop(seconds=1)
            async def process_queue():
                if not self.queue.empty():
                    try:
                        while not self.queue.empty():
                            message = self.queue.get_nowait()
                            channel = self.bot.get_channel(self.channel_id)
                            if channel:
                                await channel.send(message)
                                print(f"Sent message to Discord: {message}")
                            else:
                                print(f"Channel {self.channel_id} not found")
                    except Exception as e:
                        print(f"Error sending to Discord: {e}")
            
            self.process_queue = process_queue
            self.loop.run_until_complete(self.bot.start(self.bot_token))
        
        self.thread = threading.Thread(target=run_bot, daemon=True)
        self.thread.start()
    
    async def sync_commands_background(self):
        """Sync commands in the background after bot is connected"""
        if self.commands_synced:  # Prevent multiple syncs
            return
            
        try:
            print("Starting background command sync...")
            await asyncio.sleep(2)  # Short delay to ensure bot is fully initialized
            
            # Sync the commands
            await self.bot.tree.sync()
            self.commands_synced = True
            
            print("Slash commands synced successfully")
            
            # Send a message to the channel to confirm
            channel = self.bot.get_channel(self.channel_id)
            if channel:
                await channel.send("✅ Bot initialization complete - slash commands are now ready to use")
        except Exception as e:
            error_msg = f"Error syncing commands: {str(e)}"
            print(error_msg)
            # Try to notify in the channel
            channel = self.bot.get_channel(self.channel_id)
            if channel:
                await channel.send(f"⚠️ Error syncing commands: {str(e)}")

    def emit(self, record):
        """
        Process a log record by putting it in the queue.
        
        Args:
            record: The log record to process
        """
        try:
            msg = self.format(record)
            # Add the formatted message to the queue
            asyncio.run_coroutine_threadsafe(self.queue.put(msg), self.loop)
        except Exception as e:
            print(f"Error in emit: {e}")
    
    def close(self):
        """Shut down the handler cleanly"""
        if self.bot and self.bot.is_ready():
            asyncio.run_coroutine_threadsafe(self.bot.close(), self.loop)
        super().close()


if __name__ == '__main__':
    import os
    import time
    from dotenv import load_dotenv

    """Run an example that sends log messages to Discord."""
    # Load environment variables
    load_dotenv()

    bot_token = os.environ.get("DISCORD_BOT_TOKEN")
    channel_id = os.environ.get("DISCORD_CHANNEL_ID")
    
    if not bot_token or not channel_id:
        print("Please set DISCORD_BOT_TOKEN and DISCORD_CHANNEL_ID environment variables.")
        print("Example:")
        print("export DISCORD_BOT_TOKEN='your-bot-token'")
        print("export DISCORD_CHANNEL_ID='123456789012345678'")
        exit(1)
    
    # Configure logging
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.DEBUG)
    
    # Add a console handler for comparison
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter('CONSOLE: %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Add the Discord handler
    discord_handler = DiscordBotHandler(
        bot_token=bot_token,
        channel_id=channel_id
    )
    discord_formatter = logging.Formatter('**%(levelname)s** (%(asctime)s): %(message)s', '%Y-%m-%d %H:%M:%S')
    discord_handler.setFormatter(discord_formatter)
    logger.addHandler(discord_handler)
    
    # Wait for the bot to be ready before sending logs
    print("Waiting for Discord bot to connect...")
    while not discord_handler.ready.is_set():
        time.sleep(0.1)
    
    # Send test log messages
    print("Sending test log messages...")
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    logger.critical("This is a CRITICAL message")
    
    # Keep the script running to allow messages to be sent
    print("Messages queued. Waiting for them to be sent...")
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("Exiting...")
    print("Test complete.")
