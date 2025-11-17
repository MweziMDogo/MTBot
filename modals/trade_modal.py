"""Modal for recording completed trades."""

import discord
from discord import ui
import logging
from database.db import record_trade, get_pet_by_name
from config.settings import VALID_RARITIES

logger = logging.getLogger(__name__)


class RecordTradeModal(ui.Modal, title="Record Completed Trade"):  # type: ignore
    """Modal for recording a completed trade."""
    
    gave_pet = ui.TextInput(
        label="Pet You Gave (Name Rarity Qty)",
        placeholder="e.g., Aurelia Legendary 10",
        min_length=1,
        max_length=50,
        required=True
    )
    received_pet = ui.TextInput(
        label="Pet You Received (Name Rarity Qty)",
        placeholder="e.g., Bramble Mythic 5",
        min_length=1,
        max_length=50,
        required=True
    )
    
    def __init__(self, user_id: int) -> None:  # type: ignore
        super().__init__()
        self.user_id = user_id
    
    async def on_submit(self, interaction: discord.Interaction) -> None:  # type: ignore
        try:
            # Parse "Pet Rarity Qty" format
            gave_input = self.gave_pet.value.strip().split()
            received_input = self.received_pet.value.strip().split()
            
            if len(gave_input) < 3:
                await interaction.response.send_message(
                    "❌ Invalid format for gave pet. Use: **Pet Rarity Quantity** (e.g., Aurelia Legendary 10)",
                    ephemeral=True
                )
                return
            
            if len(received_input) < 3:
                await interaction.response.send_message(
                    "❌ Invalid format for received pet. Use: **Pet Rarity Quantity** (e.g., Bramble Mythic 5)",
                    ephemeral=True
                )
                return
            
            # Extract data
            gave_pet_name = gave_input[0]
            gave_rarity = gave_input[1]
            received_pet_name = received_input[0]
            received_rarity = received_input[1]
            
            # Validate pet names
            if not get_pet_by_name(gave_pet_name):
                await interaction.response.send_message(
                    f"❌ Pet '{gave_pet_name}' not found in database. Use `/pets` to see available pets.",
                    ephemeral=True
                )
                return
            
            if not get_pet_by_name(received_pet_name):
                await interaction.response.send_message(
                    f"❌ Pet '{received_pet_name}' not found in database. Use `/pets` to see available pets.",
                    ephemeral=True
                )
                return
            
            # Validate rarities
            if gave_rarity not in VALID_RARITIES:
                await interaction.response.send_message(
                    f"❌ '{gave_rarity}' is not a valid rarity. Valid options: {', '.join(VALID_RARITIES)}",
                    ephemeral=True
                )
                return
            
            if received_rarity not in VALID_RARITIES:
                await interaction.response.send_message(
                    f"❌ '{received_rarity}' is not a valid rarity. Valid options: {', '.join(VALID_RARITIES)}",
                    ephemeral=True
                )
                return
            
            # Validate quantities
            try:
                gave_qty = int(gave_input[2])
                received_qty = int(received_input[2])
                
                if gave_qty < 1 or received_qty < 1:
                    raise ValueError("Quantities must be at least 1")
            except (ValueError, IndexError) as e:
                await interaction.response.send_message(
                    f"❌ Invalid quantity: {str(e)}",
                    ephemeral=True
                )
                return
            
            # Record the trade
            trade_id = record_trade(
                self.user_id,
                gave_pet_name,
                gave_qty,
                gave_rarity,
                received_pet_name,
                received_qty,
                received_rarity
            )
            
            await interaction.response.send_message(
                f"✅ Trade recorded! (ID: {trade_id})\n\n"
                f"**You gave:** {gave_qty}x {gave_pet_name} ({gave_rarity})\n"
                f"**You received:** {received_qty}x {received_pet_name} ({received_rarity})\n\n"
                f"Use `/price_chart` to view average prices!",
                ephemeral=True
            )
            
            logger.info(f"Trade recorded: User {self.user_id}, Trade ID {trade_id}")
            
        except Exception as e:
            logger.error(f"Error in RecordTradeModal.on_submit: {e}", exc_info=True)
            await interaction.response.send_message(
                f"❌ Error recording trade: {str(e)}",
                ephemeral=True
            )
