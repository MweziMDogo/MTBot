"""Modal dialogs for user input."""

import discord
from discord import ui
import json
import logging
from typing import Optional, List, Dict, Any
from database.db import get_pet_by_name, get_listing_by_id, update_listing, create_listing, delete_listing
from utils.validators import parse_quantities, parse_pet_quantities
from config.settings import DB_PATH, MSG_LISTING_UPDATED, MSG_LISTING_DELETED

logger = logging.getLogger(__name__)


class QuantityPresetButtons(ui.View):
    """Quick quantity preset buttons to guide users."""
    
    def __init__(self) -> None:
        super().__init__()
    
    @ui.button(label="1", style=discord.ButtonStyle.gray)
    async def preset_1(self, interaction: discord.Interaction, button: ui.Button) -> None:  # type: ignore
        await interaction.response.send_message("Enter **1** in the Quantity field.", ephemeral=True)
    
    @ui.button(label="10", style=discord.ButtonStyle.gray)
    async def preset_10(self, interaction: discord.Interaction, button: ui.Button) -> None:  # type: ignore
        await interaction.response.send_message("Enter **10** in the Quantity field.", ephemeral=True)
    
    @ui.button(label="50", style=discord.ButtonStyle.gray)
    async def preset_50(self, interaction: discord.Interaction, button: ui.Button) -> None:  # type: ignore
        await interaction.response.send_message("Enter **50** in the Quantity field.", ephemeral=True)
    
    @ui.button(label="100", style=discord.ButtonStyle.gray)
    async def preset_100(self, interaction: discord.Interaction, button: ui.Button) -> None:  # type: ignore
        await interaction.response.send_message("Enter **100** in the Quantity field.", ephemeral=True)
    
    @ui.button(label="1000", style=discord.ButtonStyle.blurple)
    async def preset_1000(self, interaction: discord.Interaction, button: ui.Button) -> None:  # type: ignore
        await interaction.response.send_message("Enter **1000** in the Quantity field.", ephemeral=True)


class AddPetModal(ui.Modal, title="Add Pet to Listing"):  # type: ignore
    """Modal for adding pets with validation and dual-rarity support."""
    pet_name = ui.TextInput(
        label="Pet Name",
        placeholder="e.g., Delve, Bramble, Kragg... (use /pets to see all)",
        min_length=1,
        max_length=50,
        required=True
    )
    legendary_qty = ui.TextInput(
        label="Legendary Quantity",
        placeholder="Examples: 1, 10, 50, 100, 1000 | Leave blank for 0",
        min_length=0,
        max_length=5,
        required=False
    )
    mythic_qty = ui.TextInput(
        label="Mythic Quantity",
        placeholder="Examples: 1, 10, 50, 100, 1000 | Leave blank for 0",
        min_length=0,
        max_length=5,
        required=False
    )
    
    def __init__(
        self,
        section_name: str,
        user_id: int,
        have_pets: Optional[List[Dict[str, Any]]] = None,
        want_only: bool = False,
        listing_id: Optional[int] = None,
        edit_mode: bool = False,
        replace_mode: bool = False,
        listing_type_mode: Optional[str] = None
    ) -> None:  # type: ignore
        super().__init__()
        self.section_name = section_name
        self.user_id = user_id
        self.have_pets = have_pets or []
        self.replace_mode = replace_mode
        self.want_only = want_only
        self.listing_id = listing_id
        self.edit_mode = edit_mode
        self.listing_type_mode = listing_type_mode
    
    async def on_submit(self, interaction: discord.Interaction) -> None:  # type: ignore
        try:
            pet_name_input = self.pet_name.value.strip()
            legendary_input = self.legendary_qty.value.strip()
            mythic_input = self.mythic_qty.value.strip()
            
            # Build quantity string only with non-empty values
            qty_parts = []
            if legendary_input and legendary_input != '0':
                qty_parts.append(f"Legendary:{legendary_input}")
            if mythic_input and mythic_input != '0':
                qty_parts.append(f"Mythic:{mythic_input}")
            
            qty_string = ",".join(qty_parts) if qty_parts else ""
            
            # Parse quantities
            is_valid, quantities, error_msg = parse_quantities(qty_string)
            if not is_valid or not quantities:
                await interaction.response.send_message(
                    "❌ You must enter at least one quantity (Legendary or Mythic)",
                    ephemeral=True
                )
                return
            
            # Get pet from database
            pet_result = get_pet_by_name(pet_name_input)
            if not pet_result:
                from database.db import get_all_pets
                available = ', '.join([p[1] for p in get_all_pets()])
                await interaction.response.send_message(
                    f"❌ Pet '{pet_name_input}' not found in database.\nAvailable pets: {available}",
                    ephemeral=True
                )
                return
            
            pet_id, pet_name, pet_url = pet_result
            
            # Handle edit mode
            if self.edit_mode and self.listing_id:
                await self._handle_edit_mode(interaction, pet_name, quantities, pet_url)
                return
            
            # Handle creation mode (per-pet listings)
            if self.listing_type_mode:
                await self._handle_creation_mode(interaction, pet_name, quantities, pet_url)
                return
            
            # Handle legacy flow
            await interaction.response.send_message(
                "❌ Invalid mode",
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Error in AddPetModal.on_submit: {e}", exc_info=True)
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
    
    async def _handle_edit_mode(
        self,
        interaction: discord.Interaction,
        pet_name: str,
        quantities: Dict[str, int],
        pet_url: str
    ) -> None:
        """Handle editing an existing listing."""
        try:
            listing = get_listing_by_id(self.listing_id)
            if not listing or listing['user_id'] != self.user_id:
                await interaction.response.send_message(
                    f"❌ Listing #{self.listing_id} not found or doesn't belong to you.",
                    ephemeral=True
                )
                return
            
            haves = listing['haves'].copy() if listing['haves'] else {}
            wants = listing['wants'].copy() if listing['wants'] else {}
            
            # Get the section to update
            section_dict = haves if self.section_name == "Have" else wants
            
            if self.replace_mode:
                # Remove all entries for this pet
                section_dict = {k: v for k, v in section_dict.items() if k.lower() != pet_name.lower()}
            
            # Add/update the new quantities - merge with existing if same pet
            if pet_name in section_dict and not self.replace_mode:
                # Merge rarities for the same pet - ADD quantities together
                existing_qty = section_dict[pet_name].copy() if isinstance(section_dict[pet_name], dict) else {}
                for rarity, qty in quantities.items():
                    if rarity in existing_qty:
                        existing_qty[rarity] += qty  # Add to existing quantity
                    else:
                        existing_qty[rarity] = qty  # Add new rarity
                section_dict[pet_name] = existing_qty
            else:
                # Replace entirely for this pet
                section_dict[pet_name] = quantities
            
            # Update the listing
            if self.section_name == "Have":
                haves = section_dict
            else:
                wants = section_dict
            
            update_listing(self.listing_id, haves=haves if self.section_name == "Have" else None,
                          wants=wants if self.section_name == "Want" else None)
            
            from utils.validators import format_quantities
            section_text = f"{pet_name}: {format_quantities(quantities)}"
            full_section_text = ", ".join([f"{p}: {format_quantities(q)}" for p, q in section_dict.items()])
            action_text = "Replaced" if self.replace_mode else "Added to"
            
            await interaction.response.send_message(
                f"✅ {action_text} {self.section_name} section: {section_text}\n\n"
                f"**Updated {self.section_name}:** {full_section_text}\n"
                f"**Listing #{self.listing_id} has been updated!**",
                ephemeral=True
            )
            logger.info(f"User {self.user_id} edited listing {self.listing_id}")
        except Exception as e:
            logger.error(f"Error in _handle_edit_mode: {e}", exc_info=True)
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
    
    async def _handle_creation_mode(
        self,
        interaction: discord.Interaction,
        pet_name: str,
        quantities: Dict[str, int],
        pet_url: str
    ) -> None:
        """Handle creating new per-pet listings."""
        try:
            if self.listing_type_mode == "Both" and self.listing_id:
                # In BOTH mode with existing listing - update it
                listing = get_listing_by_id(self.listing_id)
                if listing and listing['user_id'] == self.user_id:
                    haves = listing['haves'].copy() if listing['haves'] else {}
                    wants = listing['wants'].copy() if listing['wants'] else {}
                    
                    if self.section_name == "Have":
                        haves[pet_name] = quantities
                    else:
                        wants[pet_name] = quantities
                    
                    update_listing(self.listing_id, haves=haves, wants=wants)
                    listing_id = self.listing_id
            else:
                # Create new listing
                if self.listing_type_mode == "Have":
                    listing_id = create_listing(self.user_id, {pet_name: quantities}, {})
                elif self.listing_type_mode == "Want":
                    listing_id = create_listing(self.user_id, {}, {pet_name: quantities})
                elif self.listing_type_mode == "Both":
                    listing_id = create_listing(self.user_id, {pet_name: quantities}, {pet_name: quantities})
                else:
                    listing_id = create_listing(self.user_id, {pet_name: quantities}, {})
            
            from utils.validators import format_quantities
            pet_text = f"{pet_name}: {format_quantities(quantities)}"
            
            from views.listing import PetListingView, BothListingTypeView
            
            # For BOTH mode, show the BOTH view instead of PetListingView
            if self.listing_type_mode == "Both":
                view = BothListingTypeView(self.user_id, listing_id)
            else:
                view = PetListingView(self.listing_type_mode or "Have", self.user_id)
            
            await interaction.response.send_message(
                f"✅ Added {pet_text}!\n\n**Add another pet or click Done**",
                view=view,
                ephemeral=True
            )
            logger.info(f"User {self.user_id} created listing for {pet_name}")
        except Exception as e:
            logger.error(f"Error in _handle_creation_mode: {e}", exc_info=True)
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)


class EditListingSelectModal(ui.Modal, title="Edit Listing"):  # type: ignore
    """Modal to select which listing to edit."""
    listing_id = ui.TextInput(
        label="Listing ID to edit",
        placeholder="Enter the listing ID number",
        min_length=1,
        max_length=10,
        required=True
    )
    
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
    
    async def on_submit(self, interaction: discord.Interaction):  # type: ignore
        try:
            listing_id = int(self.listing_id.value.strip())
            
            # Check if listing exists and belongs to user
            listing = get_listing_by_id(listing_id)
            if not listing or listing['user_id'] != self.user_id:
                await interaction.response.send_message(
                    f"❌ Listing #{listing_id} not found or doesn't belong to you.",
                    ephemeral=True
                )
                return
            
            # Show edit options
            from views.manage import EditListingOptionsView
            await interaction.response.send_message(
                f"**Editing Listing #{listing_id}**\n\nWhat would you like to edit?",
                view=EditListingOptionsView(listing_id, self.user_id),
                ephemeral=True
            )
        except ValueError:
            await interaction.response.send_message("❌ Please enter a valid listing ID number.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)


class DeleteListingModal(ui.Modal, title="Delete Listing"):  # type: ignore
    """Modal to delete a listing by ID."""
    listing_id = ui.TextInput(
        label="Listing ID to delete",
        placeholder="Enter the listing ID number",
        min_length=1,
        max_length=10,
        required=True
    )
    
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
    
    async def on_submit(self, interaction: discord.Interaction):  # type: ignore
        try:
            listing_id = int(self.listing_id.value.strip())
            
            # Check if listing exists and belongs to user
            listing = get_listing_by_id(listing_id)
            if not listing:
                await interaction.response.send_message(f"❌ Listing #{listing_id} not found.", ephemeral=True)
                return
            
            if listing['user_id'] != self.user_id:
                await interaction.response.send_message("❌ You can only delete your own listings.", ephemeral=True)
                return
            
            # Delete the listing
            delete_listing(listing_id)
            
            await interaction.response.send_message(f"✅ Listing #{listing_id} has been deleted.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Please enter a valid listing ID number.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)


class EditListingModal(ui.Modal, title="Edit Listing"):  # type: ignore
    """Modal for admins to edit any listing (simple format like /create_listing)."""
    
    def __init__(self, listing_id: int, listing_data: Dict[str, Any]):
        super().__init__()
        self.listing_id = listing_id
        self.listing_data = listing_data
    
    haves = ui.TextInput(
        label="Items They HAVE",
        placeholder='Pet Rarity Quantity\ne.g. "Bramble Legendary 15, Mythic 2"',
        min_length=0,
        max_length=1000,
        required=False,
        style=discord.TextStyle.paragraph
    )
    
    wants = ui.TextInput(
        label="Items They WANT",
        placeholder='Pet Rarity Quantity\ne.g. "Aurelia Legendary 25, Delve Mythic 5"',
        min_length=0,
        max_length=1000,
        required=False,
        style=discord.TextStyle.paragraph
    )
    
    description = ui.TextInput(
        label="Description (optional)",
        placeholder="Any notes about the trade...",
        min_length=0,
        max_length=500,
        required=False,
        style=discord.TextStyle.paragraph
    )
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        """Process the modal submission."""
        try:
            # Parse inputs using the new pet-rarity-quantity format
            new_haves = None
            new_wants = None
            
            if self.haves.value.strip():
                try:
                    new_haves = parse_pet_quantities(self.haves.value)
                    if not new_haves:
                        await interaction.response.send_message(
                            "❌ No valid items in 'Items They HAVE' field.\nFormat: `Pet Rarity Quantity` (comma-separated)",
                            ephemeral=True
                        )
                        return
                except ValueError as e:
                    await interaction.response.send_message(
                        f"❌ Error in 'Items They HAVE': {str(e)}",
                        ephemeral=True
                    )
                    return
            
            if self.wants.value.strip():
                try:
                    new_wants = parse_pet_quantities(self.wants.value)
                    if not new_wants:
                        await interaction.response.send_message(
                            "❌ No valid items in 'Items They WANT' field.\nFormat: `Pet Rarity Quantity` (comma-separated)",
                            ephemeral=True
                        )
                        return
                except ValueError as e:
                    await interaction.response.send_message(
                        f"❌ Error in 'Items They WANT': {str(e)}",
                        ephemeral=True
                    )
                    return
            
            # Update the listing
            update_listing(
                self.listing_id,
                haves=new_haves or self.listing_data.get('haves'),
                wants=new_wants or self.listing_data.get('wants'),
                description=self.description.value if self.description.value.strip() else self.listing_data.get('description')
            )
            
            embed = discord.Embed(
                title=f"✅ Listing #{self.listing_id} Updated",
                color=discord.Color.green(),
                description="The listing has been successfully updated!"
            )
            
            # Format the display
            if new_haves:
                haves_display = ", ".join([f"{pet} {', '.join([f'{r}:{q}' for r, q in rarities.items()])}" for pet, rarities in new_haves.items()])
                embed.add_field(name="New HAVE", value=haves_display, inline=False)
            
            if new_wants:
                wants_display = ", ".join([f"{pet} {', '.join([f'{r}:{q}' for r, q in rarities.items()])}" for pet, rarities in new_wants.items()])
                embed.add_field(name="New WANT", value=wants_display, inline=False)
            
            if self.description.value.strip():
                embed.add_field(name="New Description", value=self.description.value, inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logger.info(f"Admin edited listing {self.listing_id}")
            
        except Exception as e:
            logger.error(f"Error editing listing: {e}", exc_info=True)
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
