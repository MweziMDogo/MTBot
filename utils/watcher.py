"""Watch for git commits and auto-restart the bot."""

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

class GitCommitHandler(FileSystemEventHandler):
    """Handle git commits and trigger bot restart."""
    
    def __init__(self, bot=None):
        self.bot = bot
        self.last_commit_time = time.time()
        self.cooldown = 3  # Prevent multiple restarts in quick succession
        self.git_dir = Path('.git')
        
    def on_modified(self, event):
        """Called when a file is modified."""
        if event.is_directory:
            return
        
        # Only watch git index and HEAD files (these change on commits)
        event_path = Path(event.src_path)
        
        # Trigger on git index changes (happens during git operations)
        if event_path.name in ['index', 'HEAD', 'COMMIT_EDITMSG']:
            # Check if this is actually a commit (index file modification)
            current_time = time.time()
            if current_time - self.last_commit_time < self.cooldown:
                return
            
            self.last_commit_time = current_time
            
            logger.warning("[GIT] Commit detected")
            logger.warning("[GIT] Bot will restart in 3 seconds...")
            
            # Restart in a separate thread to avoid event loop issues
            import threading
            restart_thread = threading.Thread(target=self._restart_bot_sync)
            restart_thread.daemon = True
            restart_thread.start()
    
    def _restart_bot_sync(self):
        """Synchronously restart the bot (called from separate thread)."""
        try:
            # Wait before restarting
            time.sleep(2)
            
            # Try to send notification if bot is available
            if self.bot:
                try:
                    import asyncio
                    # Try to schedule notification in bot's event loop if available
                    for guild in self.bot.guilds:
                        for channel in guild.text_channels:
                            try:
                                # Create task in bot's event loop
                                future = asyncio.run_coroutine_threadsafe(
                                    channel.send(embed=discord.Embed(
                                        title="⚙️ Bot Restarting",
                                        description="Updating bot code... I'll be back in a moment!",
                                        color=discord.Color.blue()
                                    )),
                                    self.bot.loop
                                )
                                future.result(timeout=1)
                                break  # Send to first available channel per guild
                            except Exception as e:
                                logger.debug(f"Could not send notification: {e}")
                                continue
                except Exception as e:
                    logger.debug(f"Skipping notification: {e}")
        except Exception as e:
            logger.error(f"Error during restart: {e}")
        finally:
            # Restart the bot process
            logger.info("Restarting bot...")
            os.execl(sys.executable, sys.executable, "bot.py")


def start_file_watcher(bot=None):
    """Start watching for git commits."""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        
        # Check if .git directory exists
        if not Path('.git').exists():
            logger.warning("Git repository not found - auto-restart disabled")
            return None
        
        event_handler = GitCommitHandler(bot)
        observer = Observer()
        
        # Watch only the .git directory for commits
        observer.schedule(event_handler, path='.git', recursive=True)
        observer.start()
        
        logger.info("[GIT] Watcher started - bot will auto-restart on git commits")
        return observer
    except ImportError:
        logger.warning("watchdog not installed - auto-restart disabled")
        logger.warning("Install it with: pip install watchdog")
        return None
