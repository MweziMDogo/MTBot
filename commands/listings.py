"""Bot slash commands."""

import discord
from discord import app_commands, ui
import json
import logging
from database.db import get_all_pets, search_listings, get_user_listings_filtered
from utils.validators import format_quantities, get_quantity_presets
from views.listing import ListingTypeView, ListingView
from views.manage import MyListingsView

logger = logging.getLogger(__name__)


async def setup_commands(tree: app_commands.CommandTree, client: discord.Client) -> None:
    """Register all slash commands."""

    @tree.command(name='help', description='Get help and learn how to use the bot')
    async def help_command(interaction: discord.Interaction):
        """Show comprehensive help guide."""
        embed = discord.Embed(
            title="📖 Miner Tycon Auction House Bot - Help Guide",
            color=discord.Color.blue(),
            description="Learn how to trade pets effectively!"
        )
        
        embed.add_field(
            name="🎯 Quick Start",
            value=(
                "1. `/create_listing` - Create what you have or want\n"
                "2. `/search <pet>` - Find other traders\n"
                "3. `/my_listings` - Manage your listings\n"
                "4. `/help` - You are here!\n"
                "5. `/pets` - See all available pets"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📦 Creating Listings",
            value=(
                "Use `/create_listing` to start:\n"
                "• **HAVE** - Pets you want to trade away\n"
                "• **WANT** - Pets you're looking for\n"
                "• **BOTH** - List same pet in both sections\n\n"
                "Enter quantities like: `Legendary:5, Mythic:3`"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🔍 Searching",
            value=(
                "Use `/search <pet>` to find listings:\n"
                "• `search_type: all` - See offers and requests\n"
                "• `search_type: offers` - Who's selling\n"
                "• `search_type: requests` - Who's buying\n\n"
                "Contact traders through the 'Contact User' button"
            ),
            inline=False
        )
        
        embed.add_field(
            name="✏️ Managing Listings",
            value=(
                "Use `/my_listings` to:\n"
                "• **Edit** - Change quantities or add pets\n"
                "• **Delete** - Remove listings\n"
                "• **Preview** - See what's currently listed"
            ),
            inline=False
        )
        
        embed.add_field(
            name="💡 Tips",
            value=(
                "• Use `/pets` to see available pets\n"
                "• Add descriptions to help traders\n"
                "• Create separate listings for each pet type\n"
                "• Check recent listings for active traders"
            ),
            inline=False
        )
        
        embed.add_field(
            name="❓ Need More Help?",
            value="Use `/how-to-trade` for step-by-step examples",
            inline=False
        )
        
        embed.set_footer(text="Happy trading! 🚀")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @tree.command(name='how-to-trade', description='Step-by-step trading guide')
    async def how_to_trade(interaction: discord.Interaction):
        """Show detailed trading examples."""
        embed = discord.Embed(
            title="🤝 How to Trade - Step by Step",
            color=discord.Color.green(),
            description="Complete guide with examples"
        )
        
        embed.add_field(
            name="Step 1: Create Your First Listing",
            value=(
                "1. Type `/create_listing`\n"
                "2. Choose: HAVE, WANT, or BOTH\n"
                "3. Enter pet name (e.g., 'Delve')\n"
                "4. Enter quantities (e.g., `Legendary:5, Mythic:2`)\n"
                "5. Click 'Add Another Pet' or 'Done'"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Step 2: Search for Traders",
            value=(
                "1. Type `/search Delve`\n"
                "2. See who's offering Delve\n"
                "3. See who's looking for Delve\n"
                "4. Click 'Contact User' to DM them"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Step 3: Make a Deal",
            value=(
                "1. DM the trader directly\n"
                "2. Negotiate quantities and rarities\n"
                "3. Agree on trade terms\n"
                "4. Complete trade in-game\n"
                "5. Update your listings"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Step 4: Update Listings",
            value=(
                "1. Type `/my_listings`\n"
                "2. Click 'Edit Listing'\n"
                "3. Select listing ID\n"
                "4. Choose HAVE or WANT section\n"
                "5. Replace or add quantities\n"
                "6. Done!"
            ),
            inline=False
        )
        
        embed.add_field(
            name="💡 Pro Tips",
            value=(
                "✓ Use `/pets` to verify pet names\n"
                "✓ Keep listings updated after trades\n"
                "✓ Create one listing per pet type\n"
                "✓ Respond quickly to inquiries\n"
                "✓ Use descriptions to stand out"
            ),
            inline=False
        )
        
        embed.set_footer(text="Good luck trading! 🎉")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @tree.command(name='pets', description='View all available pets')
    async def pets_command(interaction: discord.Interaction):
        """Display all available pets with images."""
        try:
            pets = get_all_pets()
            
            if not pets:
                await interaction.response.send_message(
                    "❌ No pets found in database.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title=f"🐾 Available Pets ({len(pets)})",
                color=discord.Color.purple(),
                description="Use these names in `/create_listing`"
            )
            
            # Create pet list
            pet_list = "\n".join([f"• **{pet[1]}**" for pet in pets])
            embed.add_field(name="Pet Names", value=pet_list, inline=False)
            
            # Show first pet as thumbnail
            if pets:
                embed.set_thumbnail(url=pets[0][2])
            
            embed.add_field(
                name="How to Use",
                value=(
                    "1. Use `/create_listing`\n"
                    "2. Type any pet name from above\n"
                    "3. Enter quantities\n"
                    "4. Done!"
                ),
                inline=False
            )
            
            embed.set_footer(text="Tip: Use exact spelling from above")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in pets_command: {e}", exc_info=True)
            await interaction.response.send_message(
                f"❌ Error: {str(e)}",
                ephemeral=True
            )

    @tree.command(name='create_listing', description='Create a new auction listing')
    async def create_listing(interaction: discord.Interaction):
        """Start the listing creation process."""
        await interaction.response.send_message(
            "**What would you like to create?**",
            view=ListingTypeView(),
            ephemeral=True
        )

    @tree.command(name='search', description='Search for listings by item')
    @app_commands.describe(item='The item to search for', search_type='Type: all, offers, or requests')
    async def search(interaction: discord.Interaction, item: str, search_type: str = 'all'):
        """Search listings by pet name with pagination support."""
        if search_type not in ['all', 'offers', 'requests']:
            await interaction.response.send_message("Invalid search type. Use 'all', 'offers', or 'requests'.", ephemeral=True)
            return

        try:
            results = search_listings(pet_name=item)

            offers = []
            requests = []

            for listing in results:
                listing_id = listing['id']
                user_id = listing['user_id']
                haves = listing['haves']
                wants = listing['wants']
                desc = listing['description']

                have_items = list(haves.keys())
                want_items = list(wants.keys())

                have_str = ', '.join([
                    f"{pet} ({format_quantities(quantities)})" 
                    for pet, quantities in haves.items()
                ]) if haves else "None"
                
                want_str = ', '.join([
                    f"{pet} ({format_quantities(quantities)})" 
                    for pet, quantities in wants.items()
                ]) if wants else "None"
                
                # Get first item image if available for thumbnail
                first_image = None
                if haves:
                    first_pet = next(iter(haves.keys()))
                    pet_data = next((p for p in get_all_pets() if p[1] == first_pet), None)
                    if pet_data:
                        first_image = pet_data[2]
                if not first_image and wants:
                    first_pet = next(iter(wants.keys()))
                    pet_data = next((p for p in get_all_pets() if p[1] == first_pet), None)
                    if pet_data:
                        first_image = pet_data[2]
                
                try:
                    user = await client.fetch_user(user_id)
                    user_display = user.mention
                except discord.NotFound:
                    user_display = f"<@{user_id}>"
                
                listing_text = f"**ID {listing_id} by {user_display}**: Offers: {have_str} | Wants: {want_str}"
                if desc:
                    listing_text += f" | Note: {desc}"

                if any(item.lower() == pet.lower() for pet in have_items):
                    offers.append((listing_text, listing_id, user_id, first_image))
                if any(item.lower() == pet.lower() for pet in want_items):
                    requests.append((listing_text, listing_id, user_id, first_image))

            embed = discord.Embed(title=f"Search Results for '{item}'", color=discord.Color.blue())

            if search_type in ['all', 'offers'] and offers:
                offer_text = "\n".join([t[0] for t in offers[:5]])  # Show first 5
                if len(offers) > 5:
                    offer_text += f"\n... and {len(offers) - 5} more"
                embed.add_field(name=f"📦 Offers ({len(offers)})", value=offer_text, inline=False)
                if offers[0][3]:
                    embed.set_thumbnail(url=offers[0][3])
            
            if search_type in ['all', 'requests'] and requests:
                request_text = "\n".join([t[0] for t in requests[:5]])  # Show first 5
                if len(requests) > 5:
                    request_text += f"\n... and {len(requests) - 5} more"
                embed.add_field(name=f"🔍 Requests ({len(requests)})", value=request_text, inline=False)
                if requests[0][3] and not (search_type in ['all', 'offers'] and offers):
                    embed.set_thumbnail(url=requests[0][3])

            if not embed.fields:
                embed.description = f"No listings found for '{item}'"
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            # Attach view to first listing
            view = None
            if offers:
                view = ListingView(listing_id=offers[0][1], user_id=offers[0][2], client=client)
            elif requests:
                view = ListingView(listing_id=requests[0][1], user_id=requests[0][2], client=client)
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in search: {e}", exc_info=True)
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

    @tree.command(name='my_listings', description='View your own listings')
    @app_commands.describe(
        filter_by='Filter: all, have, want, or both',
        sort_by='Sort: newest, oldest, most, or least'
    )
    async def my_listings(
        interaction: discord.Interaction,
        filter_by: str = 'all',
        sort_by: str = 'newest'
    ):
        """Show all listings created by the user with optional filtering and sorting."""
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Validate filter and sort parameters
            if filter_by not in ['all', 'have', 'want', 'both']:
                filter_by = 'all'
            if sort_by not in ['newest', 'oldest', 'most', 'least']:
                sort_by = 'newest'
            
            from database.db import get_user_listings_filtered
            listings = get_user_listings_filtered(interaction.user.id, filter_by, sort_by)
            
            if not listings:
                filter_text = f" with filter '{filter_by}'" if filter_by != 'all' else ""
                await interaction.followup.send(
                    f"You don't have any listings{filter_text}. Use `/create_listing` to create one!",
                    ephemeral=True
                )
                return
            
            # Create summary line
            filter_name = {
                'all': 'All listings',
                'have': 'HAVE only',
                'want': 'WANT only',
                'both': 'BOTH only'
            }.get(filter_by, 'All listings')
            
            sort_name = {
                'newest': 'Newest first',
                'oldest': 'Oldest first',
                'most': 'Most items first',
                'least': 'Least items first'
            }.get(sort_by, 'Newest first')
            
            embed = discord.Embed(
                title="📋 Your Listings",
                color=discord.Color.green(),
                description=f"Showing {len(listings)} listing(s) | Filter: {filter_name} | Sort: {sort_name}"
            )
            
            for listing in listings:
                listing_id = listing['id']
                haves = listing['haves']
                wants = listing['wants']
                desc = listing['description']
                
                have_str = ', '.join([
                    f"{pet} ({format_quantities(quantities)})" 
                    for pet, quantities in haves.items()
                ]) if haves else "None"
                
                want_str = ', '.join([
                    f"{pet} ({format_quantities(quantities)})" 
                    for pet, quantities in wants.items()
                ]) if wants else "None"
                
                embed.add_field(
                    name=f"📌 Listing #{listing_id}",
                    value=f"**Have:** {have_str}\n**Want:** {want_str}\n**Desc:** {desc or 'N/A'}",
                    inline=False
                )
            
            view = MyListingsView(interaction.user.id)
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in my_listings: {e}", exc_info=True)
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)

    @tree.command(name='clear_all_listings', description='Clear all listings from the database (Admin/Demo only)')
    async def clear_all_listings(interaction: discord.Interaction):
        """Clear all listings - useful for fresh demos."""
        try:
            from database.db import conn_context
            import sqlite3
            
            # Create confirmation view
            class ConfirmClearView(ui.View):
                def __init__(self):
                    super().__init__(timeout=30)
                    self.confirmed = False
                
                @ui.button(label="Yes, Clear All", style=discord.ButtonStyle.danger)
                async def confirm(self, btn_interaction: discord.Interaction, button: ui.Button):
                    try:
                        conn = sqlite3.connect('database/auction_house.db')
                        cursor = conn.cursor()
                        cursor.execute('DELETE FROM listings')
                        cursor.execute('DELETE FROM trades')
                        conn.commit()
                        conn.close()
                        
                        await btn_interaction.response.send_message(
                            "✅ **All listings and trades cleared!**\n\n"
                            "The database is now ready for a fresh demo.",
                            ephemeral=True
                        )
                        logger.info(f"User {btn_interaction.user.id} cleared all listings and trades")
                    except Exception as e:
                        await btn_interaction.response.send_message(
                            f"❌ Error clearing listings: {str(e)}",
                            ephemeral=True
                        )
                
                @ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
                async def cancel(self, btn_interaction: discord.Interaction, button: ui.Button):
                    await btn_interaction.response.send_message(
                        "❌ Cancelled. Listings remain unchanged.",
                        ephemeral=True
                    )
            
            embed = discord.Embed(
                title="⚠️ Clear All Listings & Trades",
                color=discord.Color.red(),
                description="This will permanently delete **ALL listings and trades** from the database.\n\nThis action cannot be undone!"
            )
            embed.add_field(
                name="What will be deleted:",
                value="• All user listings\n• All recorded trades\n• All pricing history",
                inline=False
            )
            
            await interaction.response.send_message(
                embed=embed,
                view=ConfirmClearView(),
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Error in clear_all_listings: {e}", exc_info=True)
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)


