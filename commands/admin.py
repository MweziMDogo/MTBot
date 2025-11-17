"""Admin commands for moderating listings."""

from typing import Optional
import discord
from discord import app_commands
import logging
import json
import sqlite3
from database.db import get_listing_by_id, delete_listing, update_listing

logger = logging.getLogger(__name__)

# Admin user IDs (stored in memory - can be added via /admin_add command)
ADMIN_IDS = [
    184858845221224448,  # Your user ID - add more if needed
]


def is_admin(user_id: int) -> bool:
    """Check if user is an admin."""
    return user_id in ADMIN_IDS


def add_admin(user_id: int) -> bool:
    """Add a user to the admin list. Returns True if added, False if already exists."""
    if user_id not in ADMIN_IDS:
        ADMIN_IDS.append(user_id)
        return True
    return False


def remove_admin(user_id: int) -> bool:
    """Remove a user from the admin list. Returns True if removed, False if not found."""
    if user_id in ADMIN_IDS:
        ADMIN_IDS.remove(user_id)
        return True
    return False


def get_admin_list() -> list[int]:
    """Get current list of admin IDs."""
    return ADMIN_IDS.copy()


async def setup_admin_commands(tree: app_commands.CommandTree, client: discord.Client) -> None:
    """Register admin commands."""

    @tree.command(name='admin_listings', description='View all listings (Admin only)')
    async def admin_listings(interaction: discord.Interaction):
        """Show all listings in the server."""
        if not is_admin(interaction.user.id):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
            return

        try:
            conn = sqlite3.connect('database/auction_house.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id, user_id, haves, wants, description FROM listings ORDER BY id DESC')
            listings = cursor.fetchall()
            conn.close()
            
            if not listings:
                await interaction.response.send_message(
                    "📋 No listings in the database.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title=f"📋 All Listings ({len(listings)} total)",
                color=discord.Color.gold(),
                description="Admin view - showing all user listings"
            )
            
            for listing_id, user_id, haves, wants, desc in listings[:25]:  # Discord limit 25 fields
                embed.add_field(
                    name=f"ID #{listing_id} | User {user_id}",
                    value=f"**Have:** {haves or 'None'}\n**Want:** {wants or 'None'}\n**Desc:** {desc or 'N/A'}",
                    inline=False
                )
            
            if len(listings) > 25:
                embed.set_footer(text=f"Showing first 25 of {len(listings)} listings")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in admin_listings: {e}", exc_info=True)
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

    @tree.command(name='admin_delete_listing', description='Delete any listing by ID (Admin only)')
    @app_commands.describe(listing_id='The listing ID to delete')
    async def admin_delete_listing(interaction: discord.Interaction, listing_id: int):
        """Delete any listing."""
        if not is_admin(interaction.user.id):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
            return

        try:
            listing = get_listing_by_id(listing_id)
            
            if not listing:
                await interaction.response.send_message(
                    f"❌ Listing #{listing_id} not found.",
                    ephemeral=True
                )
                return
            
            # Create confirmation view
            class ConfirmDeleteView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=30)
                
                @discord.ui.button(label="Yes, Delete", style=discord.ButtonStyle.danger)
                async def confirm(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
                    try:
                        delete_listing(listing_id)
                        await btn_interaction.response.send_message(
                            f"✅ Listing #{listing_id} deleted!",
                            ephemeral=True
                        )
                        logger.info(f"Admin {interaction.user.id} deleted listing {listing_id}")
                    except Exception as e:
                        await btn_interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
                
                @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
                async def cancel(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
                    await btn_interaction.response.send_message("❌ Cancelled.", ephemeral=True)
            
            embed = discord.Embed(
                title=f"⚠️ Delete Listing #{listing_id}",
                color=discord.Color.red(),
                description=f"User: {listing['user_id']}\n**Have:** {listing['haves']}\n**Want:** {listing['wants']}"
            )
            
            await interaction.response.send_message(
                embed=embed,
                view=ConfirmDeleteView(),
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Error in admin_delete_listing: {e}", exc_info=True)
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

    @tree.command(name='admin_clear_user_listings', description='Delete all listings from a user (Admin only)')
    @app_commands.describe(user_id='The Discord user ID to clear listings for')
    async def admin_clear_user_listings(interaction: discord.Interaction, user_id: int):
        """Delete all listings from a specific user."""
        if not is_admin(interaction.user.id):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
            return

        try:
            conn = sqlite3.connect('database/auction_house.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM listings WHERE user_id = ?', (user_id,))
            count = cursor.fetchone()[0]
            
            if count == 0:
                await interaction.response.send_message(
                    f"❌ No listings found for user {user_id}.",
                    ephemeral=True
                )
                conn.close()
                return
            
            # Create confirmation view
            class ConfirmClearView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=30)
                
                @discord.ui.button(label="Yes, Delete All", style=discord.ButtonStyle.danger)
                async def confirm(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
                    try:
                        conn2 = sqlite3.connect('database/auction_house.db')
                        cursor2 = conn2.cursor()
                        cursor2.execute('DELETE FROM listings WHERE user_id = ?', (user_id,))
                        conn2.commit()
                        conn2.close()
                        
                        await btn_interaction.response.send_message(
                            f"✅ Deleted {count} listing(s) from user {user_id}!",
                            ephemeral=True
                        )
                        logger.info(f"Admin {interaction.user.id} deleted {count} listings from user {user_id}")
                    except Exception as e:
                        await btn_interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
                
                @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
                async def cancel(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
                    await btn_interaction.response.send_message("❌ Cancelled.", ephemeral=True)
            
            embed = discord.Embed(
                title=f"⚠️ Delete All Listings for User {user_id}",
                color=discord.Color.red(),
                description=f"This will delete **{count}** listing(s).\n\nThis action cannot be undone!"
            )
            
            await interaction.response.send_message(
                embed=embed,
                view=ConfirmClearView(),
                ephemeral=True
            )
            conn.close()
            
        except Exception as e:
            logger.error(f"Error in admin_clear_user_listings: {e}", exc_info=True)
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

    @tree.command(name='admin_edit_listing', description='Edit any listing by ID (Admin only)')
    @app_commands.describe(listing_id='The listing ID to edit', haves='New HAVE section (JSON format)', wants='New WANT section (JSON format)')
    async def admin_edit_listing(interaction: discord.Interaction, listing_id: int, haves: Optional[str] = None, wants: Optional[str] = None):
        """Edit any listing directly."""
        if not is_admin(interaction.user.id):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
            return

        try:
            listing = get_listing_by_id(listing_id)
            
            if not listing:
                await interaction.response.send_message(
                    f"❌ Listing #{listing_id} not found.",
                    ephemeral=True
                )
                return
            
            # Parse JSON inputs
            new_haves = json.loads(haves) if haves else listing['haves']
            new_wants = json.loads(wants) if wants else listing['wants']
            
            # Update listing
            update_listing(listing_id, haves=new_haves, wants=new_wants)
            
            await interaction.response.send_message(
                f"✅ Listing #{listing_id} updated!\n\n**Have:** {new_haves}\n**Want:** {new_wants}",
                ephemeral=True
            )
            logger.info(f"Admin {interaction.user.id} edited listing {listing_id}")
            
        except json.JSONDecodeError:
            await interaction.response.send_message(
                "❌ Invalid JSON format. Use: `{\"PetName\": {\"Rarity\": quantity}}`",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error in admin_edit_listing: {e}", exc_info=True)
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

    @tree.command(name='admin_add', description='Add a new admin user (Admin only)')
    @app_commands.describe(user_id='The Discord user ID to make an admin')
    async def admin_add(interaction: discord.Interaction, user_id: int):
        """Add a new admin user."""
        if not is_admin(interaction.user.id):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
            return

        try:
            if add_admin(user_id):
                await interaction.response.send_message(
                    f"✅ User {user_id} has been added as an admin!",
                    ephemeral=True
                )
                logger.info(f"Admin {interaction.user.id} added user {user_id} as admin")
            else:
                await interaction.response.send_message(
                    f"⚠️ User {user_id} is already an admin.",
                    ephemeral=True
                )
        except Exception as e:
            logger.error(f"Error in admin_add: {e}", exc_info=True)
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

    @tree.command(name='admin_remove', description='Remove an admin user (Admin only)')
    @app_commands.describe(user_id='The Discord user ID to remove from admin')
    async def admin_remove(interaction: discord.Interaction, user_id: int):
        """Remove an admin user."""
        if not is_admin(interaction.user.id):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
            return

        try:
            if remove_admin(user_id):
                await interaction.response.send_message(
                    f"✅ User {user_id} has been removed from admin!",
                    ephemeral=True
                )
                logger.info(f"Admin {interaction.user.id} removed user {user_id} from admin")
            else:
                await interaction.response.send_message(
                    f"⚠️ User {user_id} is not an admin.",
                    ephemeral=True
                )
        except Exception as e:
            logger.error(f"Error in admin_remove: {e}", exc_info=True)
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

    @tree.command(name='admin_list', description='Show all current admins (Admin only)')
    async def admin_list(interaction: discord.Interaction):
        """Show list of all admins."""
        if not is_admin(interaction.user.id):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
            return

        try:
            admins = get_admin_list()
            if not admins:
                await interaction.response.send_message(
                    "📋 No admins found.",
                    ephemeral=True
                )
                return
            
            admin_list_str = '\n'.join([f"• {admin_id}" for admin_id in admins])
            
            embed = discord.Embed(
                title="👨‍💼 Current Admins",
                color=discord.Color.gold(),
                description=f"Total: **{len(admins)}** admin(s)\n\n{admin_list_str}"
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in admin_list: {e}", exc_info=True)
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
