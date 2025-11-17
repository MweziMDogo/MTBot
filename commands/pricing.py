"""Commands for trade tracking and price charts."""

import discord
from discord import app_commands
import logging
from database.db import record_trade, get_average_prices, get_all_pets
from modals.trade_modal import RecordTradeModal

logger = logging.getLogger(__name__)


async def setup_pricing_commands(tree: app_commands.CommandTree, client: discord.Client) -> None:
    """Register pricing and trade tracking commands."""

    @tree.command(name='record_trade', description='Record a completed trade for price tracking')
    async def record_trade_command(interaction: discord.Interaction):
        """Open modal to record a trade."""
        await interaction.response.send_modal(RecordTradeModal(interaction.user.id))

    @tree.command(name='price_chart', description='View average trade prices for a pet')
    @app_commands.describe(pet='Pet name to check prices for', days='Days to look back (default 30)')
    async def price_chart(interaction: discord.Interaction, pet: str, days: int = 30):
        """Show average prices for a pet over time."""
        if days < 1 or days > 365:
            await interaction.response.send_message(
                "❌ Days must be between 1 and 365",
                ephemeral=True
            )
            return

        try:
            prices = get_average_prices(pet, days)
            
            if prices['total_trades'] == 0:
                await interaction.response.send_message(
                    f"📊 No trades recorded for **{pet}** in the last {days} days.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title=f"💹 Price Chart - {pet}",
                color=discord.Color.gold(),
                description=f"Average trade prices over the last {days} days\n**Total Trades: {prices['total_trades']}**"
            )
            
            for rarity, price_data in prices['by_rarity'].items():
                embed.add_field(
                    name=f"{rarity} Rarity",
                    value=(
                        f"**Average Price:** {price_data['avg_price']}\n"
                        f"**Trades:** {price_data['trade_count']}"
                    ),
                    inline=False
                )
            
            embed.set_footer(text="Based on recorded trades - submit your trades with /record_trade!")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in price_chart: {e}", exc_info=True)
            await interaction.response.send_message(
                f"❌ Error: {str(e)}",
                ephemeral=True
            )

    @tree.command(name='market_overview', description='View market trends for all pets')
    @app_commands.describe(days='Days to look back (default 30)')
    async def market_overview(interaction: discord.Interaction, days: int = 30):
        """Show market overview for all pets."""
        if days < 1 or days > 365:
            await interaction.response.send_message(
                "❌ Days must be between 1 and 365",
                ephemeral=True
            )
            return

        try:
            pets = get_all_pets()
            
            embed = discord.Embed(
                title="📈 Market Overview",
                color=discord.Color.blurple(),
                description=f"Trade activity overview for the last {days} days"
            )
            
            market_data = []
            
            for pet_id, pet_name, pet_url in pets:
                prices = get_average_prices(pet_name, days)
                if prices['total_trades'] > 0:
                    market_data.append((pet_name, prices['total_trades']))
            
            if not market_data:
                embed.description = f"No trades recorded in the last {days} days. Start recording trades with `/record_trade`!"
            else:
                # Sort by trade count (most active first)
                market_data.sort(key=lambda x: x[1], reverse=True)
                
                # Show top 10
                for i, (pet_name, trade_count) in enumerate(market_data[:10], 1):
                    embed.add_field(
                        name=f"{i}. {pet_name}",
                        value=f"**{trade_count}** trades",
                        inline=True
                    )
            
            embed.set_footer(text="Most traded pets appear first")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in market_overview: {e}", exc_info=True)
            await interaction.response.send_message(
                f"❌ Error: {str(e)}",
                ephemeral=True
            )
