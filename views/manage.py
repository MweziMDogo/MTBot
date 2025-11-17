"""Listing management views."""

import discord
from discord import ui
import logging

logger = logging.getLogger(__name__)


class MyListingsView(ui.View):  # type: ignore
    """View for managing your own listings."""
    def __init__(self, user_id: int):
        super().__init__(timeout=None)  # Persistent view
        self.user_id = user_id
    
    @ui.button(label="✏️ Edit Listing", style=discord.ButtonStyle.primary)
    async def edit_listing(self, interaction: discord.Interaction, button: ui.Button):  # type: ignore
        try:
            from modals.add_pet import EditListingSelectModal
            modal = EditListingSelectModal(self.user_id)
            await interaction.response.send_modal(modal)
        except discord.errors.NotFound:
            pass  # Interaction already expired, ignore
        except Exception as e:
            try:
                await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
            except:
                pass
    
    @ui.button(label="🗑️ Delete Listing", style=discord.ButtonStyle.danger)
    async def delete_listing(self, interaction: discord.Interaction, button: ui.Button):  # type: ignore
        try:
            from modals.add_pet import DeleteListingModal
            modal = DeleteListingModal(self.user_id)
            await interaction.response.send_modal(modal)
        except discord.errors.NotFound:
            pass  # Interaction already expired, ignore
        except Exception as e:
            try:
                await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
            except:
                pass


class EditListingOptionsView(ui.View):  # type: ignore
    """Choose what to edit in a listing."""
    def __init__(self, listing_id: int, user_id: int):
        super().__init__(timeout=600)
        self.listing_id = listing_id
        self.user_id = user_id
    
    @ui.button(label="📦 Edit HAVE", style=discord.ButtonStyle.primary)
    async def edit_have(self, interaction: discord.Interaction, button: ui.Button):  # type: ignore
        await interaction.response.send_message(
            f"**Editing HAVE section for Listing #{self.listing_id}**\n\nChoose an option:",
            view=EditModeChoiceView(self.listing_id, self.user_id, "Have"),
            ephemeral=True,
            delete_after=300
        )
    
    @ui.button(label="🔍 Edit WANT", style=discord.ButtonStyle.primary)
    async def edit_want(self, interaction: discord.Interaction, button: ui.Button):  # type: ignore
        await interaction.response.send_message(
            f"**Editing WANT section for Listing #{self.listing_id}**\n\nChoose an option:",
            view=EditModeChoiceView(self.listing_id, self.user_id, "Want"),
            ephemeral=True,
            delete_after=300
        )


class EditModeChoiceView(ui.View):  # type: ignore
    """Choose between replace or add mode."""
    def __init__(self, listing_id: int, user_id: int, section: str):
        super().__init__(timeout=600)
        self.listing_id = listing_id
        self.user_id = user_id
        self.section = section
    
    @ui.button(label="🔄 Replace Pet", style=discord.ButtonStyle.primary)
    async def replace_mode(self, interaction: discord.Interaction, button: ui.Button):  # type: ignore
        from modals.add_pet import AddPetModal
        await interaction.response.send_modal(AddPetModal(section_name=self.section, user_id=self.user_id, listing_id=self.listing_id, edit_mode=True, replace_mode=True))
    
    @ui.button(label="➕ Add to List", style=discord.ButtonStyle.success)
    async def add_mode(self, interaction: discord.Interaction, button: ui.Button):  # type: ignore
        from modals.add_pet import AddPetModal
        await interaction.response.send_modal(AddPetModal(section_name=self.section, user_id=self.user_id, listing_id=self.listing_id, edit_mode=True, replace_mode=False))
