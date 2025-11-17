"""Watch for git commits and auto-restart the bot."""

import os
import sys
import time
import subprocess
import logging
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

class GitCommitPoller(threading.Thread):
    """Poll git for new commits and trigger restart."""
    
    def __init__(self, bot=None):
        super().__init__(daemon=True)
        self.bot = bot
        self.running = True
        self.cooldown_until = 0
        # Fetch initially to sync with remote
        self._fetch_remote()
        # Store the initial state
        self.last_checked_remote = self._get_remote_commit()
        logger.debug(f"[GIT] Initial remote commit: {self.last_checked_remote[:8]}")
        
    def _fetch_remote(self) -> None:
        """Fetch from remote to get latest commits."""
        try:
            subprocess.run(
                ['git', 'fetch', 'origin'],
                capture_output=True,
                timeout=10,
                cwd='.'
            )
        except Exception as e:
            logger.debug(f"[GIT] Could not fetch from remote: {e}")
    
    def _get_remote_commit(self) -> str:
        """Get the remote commit hash (origin/main)."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'origin/main'],
                capture_output=True,
                text=True,
                timeout=5,
                cwd='.'
            )
            if result.returncode == 0:
                commit = result.stdout.strip()
                return commit if commit else ""
        except Exception as e:
            logger.debug(f"[GIT] Could not get remote commit: {e}")
        return ""
    
    def run(self):
        """Poll for git changes every 5 seconds."""
        logger.info("[GIT] Polling for commits every 5 seconds...")
        
        while self.running:
            try:
                time.sleep(5)
                
                # Check cooldown
                if time.time() < self.cooldown_until:
                    continue
                
                # Fetch latest from remote
                self._fetch_remote()
                
                # Check if remote has changed
                current_remote = self._get_remote_commit()
                
                if not current_remote:
                    continue
                
                # If remote changed from our last check, trigger restart
                if current_remote != self.last_checked_remote and self.last_checked_remote != "":
                    logger.warning(f"[GIT] New commits detected on remote!")
                    logger.warning(f"[GIT] Old: {self.last_checked_remote[:8]}, New: {current_remote[:8]}")
                    logger.warning("[GIT] Bot will restart in 3 seconds...")
                    
                    self.cooldown_until = time.time() + 15  # 15 second cooldown
                    
                    # Restart in separate thread
                    restart_thread = threading.Thread(target=self._restart_bot_sync)
                    restart_thread.daemon = True
                    restart_thread.start()
                    return  # Exit polling after restart initiated
                
                # Update the last checked remote
                self.last_checked_remote = current_remote
                    
            except Exception as e:
                logger.debug(f"[GIT] Polling error: {e}")
    
    def _restart_bot_sync(self):
        """Synchronously restart the bot (called from separate thread)."""
        try:
            # Wait before restarting
            time.sleep(2)
            
            # Try to send notification if bot is available
            if self.bot and self.bot.guilds:
                try:
                    import asyncio
                    sent_count = 0
                    # Try to schedule notification in bot's event loop if available
                    for guild in self.bot.guilds:
                        if sent_count >= 1:  # Only send to first guild to avoid spam
                            break
                        for channel in guild.text_channels:
                            try:
                                # Check if bot has permission to send messages
                                if not channel.permissions_for(guild.me).send_messages:
                                    continue
                                
                                # Create task in bot's event loop
                                future = asyncio.run_coroutine_threadsafe(
                                    channel.send(embed=discord.Embed(
                                        title="[UPDATE] Bot Restarting",
                                        description="Detected new code update... I'll be back in a moment!",
                                        color=discord.Color.blue()
                                    )),
                                    self.bot.loop
                                )
                                future.result(timeout=2)
                                logger.info(f"[GIT] Sent restart notification to {channel.name}")
                                sent_count += 1
                                break  # Send to first available channel per guild
                            except Exception as e:
                                logger.debug(f"Could not send to {channel.name}: {e}")
                                continue
                except Exception as e:
                    logger.debug(f"[GIT] Skipping notification: {e}")
            else:
                logger.info("[GIT] No guilds connected - skipping notification")
        except Exception as e:
            logger.error(f"[GIT] Error during restart: {e}")
        finally:
            # Restart the bot process
            logger.info("[GIT] Restarting bot...")
            os.execl(sys.executable, sys.executable, "bot.py")


def start_file_watcher(bot=None):
    """Start polling for git commits."""
    try:
        # Check if .git directory exists
        if not Path('.git').exists():
            logger.warning("Git repository not found - auto-restart disabled")
            return None
        
        poller = GitCommitPoller(bot)
        poller.start()
        
        logger.info("[GIT] Watcher started - bot will auto-restart on git commits")
        return poller
    except Exception as e:
        logger.error(f"[GIT] Error starting watcher: {e}")
        return None
