"""
Discord slash commands for managing log messages.
"""

import discord
from discord.ext import commands
from datetime import datetime, timedelta


def register_commands(bot, channel_id):
    """
    Register all slash commands for the bot.
    
    Args:
        bot: The Discord bot instance
        channel_id: The ID of the channel where logs are sent
    """
    
    @bot.tree.command(name="delete_logs", description="Delete the last N messages in the channel")
    async def delete_logs(interaction: discord.Interaction, count: int = 5, all_users: bool = True):
        """Delete the last N messages in the channel"""
        if count <= 0 or count > 100:  # Discord API limit is 100 messages at once
            await interaction.response.send_message("Please specify a number between 1 and 100.", ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=True)
        
        channel = bot.get_channel(channel_id)
        if not channel:
            await interaction.followup.send("Channel not found.", ephemeral=True)
            return
            
        deleted = 0
        try:
            # Get messages to delete
            messages = []
            async for message in channel.history(limit=count):
                # If all_users is False, only delete messages from this bot
                if all_users or message.author.id == bot.user.id:
                    messages.append(message)
            
            # Delete the messages
            if messages:
                if len(messages) == 1:
                    await messages[0].delete()
                    deleted = 1
                else:
                    # Bulk delete only works for messages less than 14 days old
                    try:
                        await channel.delete_messages(messages)
                        deleted = len(messages)
                    except discord.errors.HTTPException:
                        # Fall back to individual deletion if bulk deletion fails
                        for msg in messages:
                            try:
                                await msg.delete()
                                deleted += 1
                            except Exception:
                                pass
        except Exception as e:
            print(f"Error deleting messages: {e}")
            await interaction.followup.send(f"Error occurred: {str(e)}", ephemeral=True)
            return
        
        await interaction.followup.send(f"Deleted {deleted} messages.", ephemeral=True)
    
    @bot.tree.command(name="delete_time_range", description="Delete messages within a specified time range")
    async def delete_time_range(
        interaction: discord.Interaction, 
        hours_ago: int = 0, 
        minutes_ago: int = 0,
        all_users: bool = True
    ):
        """Delete messages within a certain time range"""
        if hours_ago < 0 or minutes_ago < 0:
            await interaction.response.send_message("Please specify a positive time range.", ephemeral=True)
            return
            
        if hours_ago == 0 and minutes_ago == 0:
            await interaction.response.send_message("Please specify a non-zero time range.", ephemeral=True)
            return
            
        # Calculate the cutoff time
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_ago, minutes=minutes_ago)
        
        await interaction.response.defer(ephemeral=True)
        
        channel = bot.get_channel(channel_id)
        if not channel:
            await interaction.followup.send("Channel not found.", ephemeral=True)
            return
            
        deleted = 0
        bulk_eligible = []
        
        try:
            # Get messages within the time range, up to Discord's limit
            async for message in channel.history(limit=1000, after=cutoff_time):
                # If all_users is False, only delete messages from this bot
                if all_users or message.author.id == bot.user.id:
                    # Messages older than 14 days can't be bulk deleted
                    # Ensure we're comparing timezone-aware with timezone-aware
                    # Discord message timestamps are timezone-aware
                    two_weeks_ago = datetime.utcnow().replace(tzinfo=message.created_at.tzinfo) - timedelta(days=14)
                    
                    if message.created_at > two_weeks_ago:
                        bulk_eligible.append(message)
                        
                        # Bulk delete in chunks of 100 (Discord API limit)
                        if len(bulk_eligible) >= 100:
                            try:
                                await channel.delete_messages(bulk_eligible)
                                deleted += len(bulk_eligible)
                                bulk_eligible = []
                            except Exception as e:
                                print(f"Error bulk deleting: {e}")
                    else:
                        # Delete individually if older than 14 days
                        try:
                            await message.delete()
                            deleted += 1
                        except Exception:
                            pass
            
            # Delete any remaining messages
            if bulk_eligible:
                if len(bulk_eligible) == 1:
                    await bulk_eligible[0].delete()
                    deleted += 1
                else:
                    await channel.delete_messages(bulk_eligible)
                    deleted += len(bulk_eligible)
                    
        except Exception as e:
            print(f"Error deleting messages: {e}")
            await interaction.followup.send(f"Error occurred: {str(e)}", ephemeral=True)
            return
        
        await interaction.followup.send(f"Deleted {deleted} messages from the last {hours_ago}h {minutes_ago}m.", ephemeral=True)