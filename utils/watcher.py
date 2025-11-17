"""Watch for code changes and auto-restart the bot."""

import os
import sys
import time
import subprocess
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

class CodeChangeHandler(FileSystemEventHandler):
    """Handle file system changes and trigger bot restart."""
    
    def __init__(self, bot=None):
        self.bot = bot
        self.last_modified = time.time()
        self.cooldown = 2  # Prevent multiple restarts in quick succession
        
    def on_modified(self, event):
        """Called when a file is modified."""
        if event.is_directory:
            return
        
        # Only watch Python files
        if not event.src_path.endswith('.py'):
            return
        
        # Ignore __pycache__ and logs
        if '__pycache__' in event.src_path or 'logs' in event.src_path:
            return
        
        # Check cooldown
        current_time = time.time()
        if current_time - self.last_modified < self.cooldown:
            return
        
        self.last_modified = current_time
        
        logger.warning(f"Code change detected: {event.src_path}")
        logger.warning("Bot will restart in 3 seconds...")
        
        if self.bot:
            # Schedule restart
            import asyncio
            asyncio.create_task(self.restart_bot_with_notification())
    
    async def restart_bot_with_notification(self):
        """Notify users and restart the bot."""
        try:
            # Send notification to all connected guilds
            if self.bot and hasattr(self.bot, 'guilds'):
                for guild in self.bot.guilds:
                    for channel in guild.text_channels:
                        try:
                            embed = discord.Embed(
                                title="⚙️ Bot Update",
                                description="Updating bot code... I'll be back in a few seconds!",
                                color=discord.Color.blue()
                            )
                            await channel.send(embed=embed)
                            break  # Send to first available channel per guild
                        except Exception as e:
                            logger.debug(f"Could not send notification: {e}")
                            continue
        except Exception as e:
            logger.error(f"Error sending update notification: {e}")
        
        # Wait a bit then restart
        await asyncio.sleep(2)
        logger.info("Restarting bot...")
        os.execl(sys.executable, sys.executable, "bot.py")


def start_file_watcher(bot=None):
    """Start watching for file changes."""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        
        event_handler = CodeChangeHandler(bot)
        observer = Observer()
        
        # Watch current directory and subdirectories
        observer.schedule(event_handler, path='.', recursive=True)
        observer.start()
        
        logger.info("File watcher started - bot will auto-restart on code changes")
        return observer
    except ImportError:
        logger.warning("watchdog not installed - auto-restart disabled")
        logger.warning("Install it with: pip install watchdog")
        return None
