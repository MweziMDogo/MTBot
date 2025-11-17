"""Miner Tycon Auction House Bot - Modular Version"""

import discord
from discord import app_commands
import os
import logging
from dotenv import load_dotenv
from database.db import init_database
from commands.listings import setup_commands
from commands.pricing import setup_pricing_commands
from commands.admin import setup_admin_commands

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Create a bot instance
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready() -> None:
    """Called when the bot has finished logging in."""
    try:
        await tree.sync()
        logger.info(f'Logged in as {client.user.name}#{client.user.discriminator} (ID: {client.user.id})')
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")


async def setup_bot():
    """Initialize bot and setup commands."""
    init_database()
    logger.info("Database initialized")
    
    await setup_commands(tree, client)
    logger.info("Commands registered")
    
    await setup_pricing_commands(tree, client)
    logger.info("Pricing commands registered")
    
    await setup_admin_commands(tree, client)
    logger.info("Admin commands registered")


# Run setup before starting bot
@client.event
async def on_connect():
    """Called when the bot establishes a connection to Discord."""
    # Only run setup once
    if not hasattr(client, '_setup_done'):
        await setup_bot()
        client._setup_done = True


# Load bot token from environment variable
token = os.getenv('DISCORD_BOT_TOKEN')
if not token:
    raise ValueError('DISCORD_BOT_TOKEN environment variable not set')

client.run(token)
