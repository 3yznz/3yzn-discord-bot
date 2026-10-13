# Project: 3YZN Discord Bot
# Author: 3YZN (@3yzn)
# Copyright (c) 2026 3YZN
# License: See LICENSE
"""Persistent per-server settings for 3YZN Discord Bot."""
import discord
from discord import app_commands
from discord.ext import commands
from utils.checks import admin_only

class SettingsCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None: self.bot=bot

    @app_commands.command(name="settings-mute-role", description="Set the role used by /mute and /unmute.")
    @admin_only()
    @app_commands.guild_only()
    async def mute_role(self, interaction: discord.Interaction, role: discord.Role) -> None:
        if role.is_default() or role.managed or role >= interaction.guild.me.top_role:
            await interaction.response.send_message("Choose a normal role below the bot's highest role.", ephemeral=True); return
        await self.bot.db.execute("INSERT INTO guild_settings(guild_id,mute_role_id) VALUES(?,?) ON CONFLICT(guild_id) DO UPDATE SET mute_role_id=excluded.mute_role_id", (interaction.guild_id,role.id))
        await interaction.response.send_message(f"Mute role configured as {role.mention}. Ensure its channel permissions deny the abilities you intend to mute.", ephemeral=True)

async def setup(bot: commands.Bot) -> None: await bot.add_cog(SettingsCog(bot))
