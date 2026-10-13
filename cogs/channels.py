# Project: 3YZN Discord Bot
# Author: 3YZN (@3yzn)
# Copyright (c) 2026 3YZN
# License: See LICENSE
"""Channel visibility commands for 3YZN Discord Bot."""
import discord
from discord import app_commands
from discord.ext import commands

class Channels(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None: self.bot = bot

    async def visibility(self, interaction: discord.Interaction, channel: discord.TextChannel, hidden: bool) -> None:
        if not interaction.guild.me.guild_permissions.manage_channels:
            await interaction.response.send_message("I need Manage Channels permission.", ephemeral=True); return
        everyone = interaction.guild.default_role
        overwrite = channel.overwrites_for(everyone)
        overwrite.view_channel = not hidden
        await channel.set_permissions(everyone, overwrite=overwrite, reason=f"Visibility changed by {interaction.user}")
        state = "hidden from" if hidden else "visible to"
        await interaction.response.send_message(f"{channel.mention} is now {state} @everyone. Other role overrides are preserved.", ephemeral=True)

    @app_commands.command(name="hide-channel", description="Hide a text channel from @everyone.")
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.guild_only()
    async def hide_channel(self, interaction: discord.Interaction, channel: discord.TextChannel) -> None: await self.visibility(interaction, channel, True)

    @app_commands.command(name="unhide-channel", description="Make a text channel visible to @everyone.")
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.guild_only()
    async def unhide_channel(self, interaction: discord.Interaction, channel: discord.TextChannel) -> None: await self.visibility(interaction, channel, False)

async def setup(bot: commands.Bot) -> None: await bot.add_cog(Channels(bot))
