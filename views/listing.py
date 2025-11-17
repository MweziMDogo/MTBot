"""UI views and buttons for listing management."""

import discord
from discord import ui
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class QuantityPresetView(ui.View):  # type: ignore
    """Quick quantity preset buttons to help users."""
    
    @ui.button(label="💡 1", style=discord.ButtonStyle.gray)
    async def preset_1(self, interaction: discord.Interaction, button: ui.Button) -> None:  # type: ignore
        await interaction.response.send_message("📝 **Quick tip:** Enter **1** in the quantity field.", ephemeral=True)
    
    @ui.button(label="💡 10", style=discord.ButtonStyle.gray)
    async def preset_10(self, interaction: discord.Interaction, button: ui.Button) -> None:  # type: ignore
        await interaction.response.send_message("📝 **Quick tip:** Enter **10** in the quantity field.", ephemeral=True)
    
    @ui.button(label="💡 50", style=discord.ButtonStyle.gray)
    async def preset_50(self, interaction: discord.Interaction, button: ui.Button) -> None:  # type: ignore
        await interaction.response.send_message("📝 **Quick tip:** Enter **50** in the quantity field.", ephemeral=True)
    
    @ui.button(label="💡 100", style=discord.ButtonStyle.gray)
    async def preset_100(self, interaction: discord.Interaction, button: ui.Button) -> None:  # type: ignore
        await interaction.response.send_message("📝 **Quick tip:** Enter **100** in the quantity field.", ephemeral=True)
    
    @ui.button(label="💡 1000", style=discord.ButtonStyle.blurple)
    async def preset_1000(self, interaction: discord.Interaction, button: ui.Button) -> None:  # type: ignore
        await interaction.response.send_message("📝 **Quick tip:** Enter **1000** in the quantity field.", ephemeral=True)


class BothListingTypeView(ui.View):  # type: ignore
    """Choose to add HAVE or WANT items when in BOTH mode."""
    
    def __init__(self, user_id: int, listing_id: int = None):  # type: ignore
        super().__init__(timeout=600)
        self.user_id = user_id
        self.listing_id = listing_id
    
    @ui.button(label="📦 Add HAVE (What I have)", style=discord.ButtonStyle.primary)
    async def add_have(self, interaction: discord.Interaction, button: ui.Button):  # type: ignore
        from modals.add_pet import AddPetModal
        await interaction.response.send_modal(AddPetModal(
            section_name="Have", 
            user_id=self.user_id, 
            listing_type_mode="Both",
            listing_id=self.listing_id
        ))
    
    @ui.button(label="🔍 Add WANT (What I need)", style=discord.ButtonStyle.primary)
    async def add_want(self, interaction: discord.Interaction, button: ui.Button):  # type: ignore
        from modals.add_pet import AddPetModal
        await interaction.response.send_modal(AddPetModal(
            section_name="Want", 
            user_id=self.user_id, 
            listing_type_mode="Both",
            listing_id=self.listing_id
        ))
    
    @ui.button(label="✅ Done", style=discord.ButtonStyle.success)
    async def done(self, interaction: discord.Interaction, button: ui.Button):  # type: ignore
        await interaction.response.send_message(
            "✅ All done! Your listings have been created. Use `/my_listings` to view them.",
            ephemeral=True
        )


class ListingTypeView(ui.View):  # type: ignore
    """Choose whether to create HAVE, WANT, or both."""
    
    @ui.button(label="📦 HAVE (What I have)", style=discord.ButtonStyle.primary)
    async def have_only(self, interaction: discord.Interaction, button: ui.Button):  # type: ignore
        from modals.add_pet import AddPetModal
        await interaction.response.send_modal(AddPetModal(section_name="Have", user_id=interaction.user.id, listing_type_mode="Have"))
    
    @ui.button(label="🔍 WANT (What I need)", style=discord.ButtonStyle.primary)
    async def want_only(self, interaction: discord.Interaction, button: ui.Button):  # type: ignore
        from modals.add_pet import AddPetModal
        await interaction.response.send_modal(AddPetModal(section_name="Want", user_id=interaction.user.id, listing_type_mode="Want"))
    
    @ui.button(label="↔️ BOTH (Have + Want)", style=discord.ButtonStyle.success)
    async def both(self, interaction: discord.Interaction, button: ui.Button):  # type: ignore
        from database.db import create_listing
        # Create an empty listing that will be populated
        listing_id = create_listing(interaction.user.id, {}, {})
        await interaction.response.send_message(
            "📋 **Add items to your BOTH listing:**\n\nClick a button below to add pets to either the HAVE or WANT section. You can add as many as you want!",
            view=BothListingTypeView(interaction.user.id, listing_id),
            ephemeral=True
        )


class PetListingView(ui.View):  # type: ignore
    """View for managing pet listings - creates one listing per pet."""
    def __init__(self, listing_type: str, user_id: int):  # type: ignore
        super().__init__(timeout=600)
        self.listing_type = listing_type  # "Have", "Want", or "Both"
        self.user_id = user_id
    
    @ui.button(label="➕ Add Another Pet", style=discord.ButtonStyle.primary)
    async def add_pet(self, interaction: discord.Interaction, button: ui.Button):  # type: ignore
        from modals.add_pet import AddPetModal
        await interaction.response.send_modal(AddPetModal(self.listing_type, self.user_id, listing_type_mode=self.listing_type))
    
    @ui.button(label="✅ Done", style=discord.ButtonStyle.success)
    async def done(self, interaction: discord.Interaction, button: ui.Button):  # type: ignore
        await interaction.response.send_message(
            "✅ All done! Your listings have been created. Use `/my_listings` to view them.",
            ephemeral=True
        )


class ListingView(ui.View):
    def __init__(self, listing_id: int, user_id: int, client: discord.Client):
        super().__init__(timeout=None)  # Persistent view
        self.listing_id = listing_id
        self.user_id = user_id
        self.client = client

    @ui.button(label='Contact User', style=discord.ButtonStyle.primary)
    async def contact(self, interaction: discord.Interaction, button: ui.Button):
        try:
            user = await self.client.fetch_user(self.user_id)
            await interaction.response.send_message(f"DM {user.mention} to discuss the trade!", ephemeral=True)
        except discord.NotFound:
            await interaction.response.send_message("User not found.", ephemeral=True)

    @ui.button(label='Delete Listing', style=discord.ButtonStyle.danger)
    async def delete(self, interaction: discord.Interaction, button: ui.Button):
        from database.db import get_listing_by_id, delete_listing
        listing = get_listing_by_id(self.listing_id)
        if not listing or listing['user_id'] != interaction.user.id:
            await interaction.response.send_message("You can only delete your own listings.", ephemeral=True)
            return

        delete_listing(self.listing_id)
        await interaction.response.send_message(f"Listing {self.listing_id} deleted.", ephemeral=True)

