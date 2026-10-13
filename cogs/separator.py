# Project: 3YZN Discord Bot
# Author: 3YZN (@3yzn)
# Copyright (c) 2026 3YZN
# License: See LICENSE
"""Persistent separator-image automation for 3YZN Discord Bot."""
import discord
from discord import app_commands
from discord.ext import commands
from utils.checks import admin_only
from utils.validators import valid_http_url, safe_text
from utils.embeds import make_embed

class Separator(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None: self.bot=bot

    @app_commands.command(name="separator-set", description="Configure the separator trigger and image URL.")
    @admin_only()
    @app_commands.guild_only()
    async def separator_set(self, interaction: discord.Interaction, trigger: app_commands.Range[str, 3, 80], image_url: str, matching_mode: str = "substring") -> None:
        trigger=trigger.strip()
        if len(trigger)<3: await interaction.response.send_message("Trigger must contain at least 3 characters.", ephemeral=True); return
        if not valid_http_url(image_url): await interaction.response.send_message("Image URL must be a valid HTTP or HTTPS URL.", ephemeral=True); return
        if matching_mode not in {"substring", "exact"}: await interaction.response.send_message("Matching mode must be `substring` or `exact`.", ephemeral=True); return
        await self.bot.db.execute("INSERT INTO separator_settings(guild_id,trigger,image_url,matching_mode) VALUES(?,?,?,?) ON CONFLICT(guild_id) DO UPDATE SET trigger=excluded.trigger,image_url=excluded.image_url,matching_mode=excluded.matching_mode", (interaction.guild_id,trigger,image_url,matching_mode))
        await interaction.response.send_message("Separator automation settings saved.", ephemeral=True)

    @app_commands.command(name="separator-remove", description="Disable separator-image automation in this server.")
    @admin_only()
    @app_commands.guild_only()
    async def separator_remove(self, interaction: discord.Interaction) -> None:
        await self.bot.db.execute("DELETE FROM separator_settings WHERE guild_id=?", (interaction.guild_id,))
        await interaction.response.send_message("Separator automation disabled and its exempt-channel list removed.", ephemeral=True)

    @app_commands.command(name="separator-exempt-channel-add", description="Add a channel where the original message is preserved.")
    @admin_only()
    @app_commands.guild_only()
    async def separator_exempt_add(self, interaction: discord.Interaction, channel: discord.TextChannel) -> None:
        exists=await self.bot.db.fetchone("SELECT guild_id FROM separator_settings WHERE guild_id=?", (interaction.guild_id,))
        if not exists: await interaction.response.send_message("Configure the trigger first using `/separator-set`.", ephemeral=True); return
        await self.bot.db.execute("INSERT OR IGNORE INTO separator_exempt_channels(guild_id,channel_id) VALUES(?,?)", (interaction.guild_id,channel.id))
        await interaction.response.send_message(f"{channel.mention} is now exempt from message deletion.", ephemeral=True)

    @app_commands.command(name="separator-exempt-channel-remove", description="Remove a channel from the separator exemption list.")
    @admin_only()
    @app_commands.guild_only()
    async def separator_exempt_remove(self, interaction: discord.Interaction, channel: discord.TextChannel) -> None:
        await self.bot.db.execute("DELETE FROM separator_exempt_channels WHERE guild_id=? AND channel_id=?", (interaction.guild_id,channel.id))
        await interaction.response.send_message(f"{channel.mention} removed from the exemption list.", ephemeral=True)

    @app_commands.command(name="separator-settings", description="View separator automation settings.")
    @admin_only()
    @app_commands.guild_only()
    async def separator_settings(self, interaction: discord.Interaction) -> None:
        row=await self.bot.db.fetchone("SELECT trigger,image_url,matching_mode FROM separator_settings WHERE guild_id=?", (interaction.guild_id,))
        if not row: await interaction.response.send_message("Separator automation is not configured.", ephemeral=True); return
        exempt=await self.bot.db.fetchall("SELECT channel_id FROM separator_exempt_channels WHERE guild_id=? ORDER BY channel_id", (interaction.guild_id,))
        channels=[f"<#{item['channel_id']}>" for item in exempt]
        embed=make_embed("Separator settings", f"**Trigger:** {row['trigger']}\n**Mode:** {row['matching_mode']}\n**Image:** {row['image_url']}\n**Exempt channels:** {', '.join(channels) if channels else 'None'}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.guild is None or message.author.bot or message.webhook_id is not None or not message.content: return
        row=await self.bot.db.fetchone("SELECT trigger,image_url,matching_mode FROM separator_settings WHERE guild_id=?", (message.guild.id,))
        if not row: return
        trigger=row['trigger']; content=message.content
        matches=(trigger.casefold() in content.casefold()) if row['matching_mode']=='substring' else (content.strip().casefold()==trigger.casefold())
        if not matches: return
        if len(trigger)<3: return
        exempt=await self.bot.db.fetchone("SELECT 1 FROM separator_exempt_channels WHERE guild_id=? AND channel_id=?", (message.guild.id,message.channel.id))
        try:
            if not exempt:
                if not message.channel.permissions_for(message.guild.me).manage_messages: return
                await message.delete()
            if not message.channel.permissions_for(message.guild.me).send_messages: return
            image_embed=discord.Embed(color=discord.Color.from_rgb(47, 111, 168))
            image_embed.set_image(url=row['image_url'])
            image_embed.set_footer(text="3YZN • Discord Bot")
            await message.channel.send(embed=image_embed, allowed_mentions=discord.AllowedMentions.none())
        except discord.NotFound: return
        except discord.Forbidden: self.bot.log.warning("Separator action blocked by permissions in guild %s", message.guild.id)
        except discord.HTTPException: self.bot.log.exception("Separator action failed in guild %s", message.guild.id)

async def setup(bot: commands.Bot) -> None: await bot.add_cog(Separator(bot))
