# Project: 3YZN Discord Bot
# Author: 3YZN (@3yzn)
# Copyright (c) 2026 3YZN
# License: See LICENSE
"""Persistent custom auto-responses for 3YZN Discord Bot."""
import discord
import time
from discord import app_commands
from discord.ext import commands
from utils.checks import admin_only
from utils.embeds import make_embed

class AutoResponses(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None: self.bot=bot; self._last_response: dict[tuple[int,int], float]={}

    @app_commands.command(name="autoresponse-add", description="Add an automatic response rule.")
    @admin_only()
    @app_commands.guild_only()
    async def add(self, interaction: discord.Interaction, trigger: app_commands.Range[str, 2, 80], response: app_commands.Range[str, 1, 1500], case_sensitive: bool = False) -> None:
        trigger=trigger.strip()
        if len(trigger)<2: await interaction.response.send_message("Trigger must contain at least 2 characters.", ephemeral=True); return
        try:
            await self.bot.db.execute("INSERT INTO autoresponses(guild_id,trigger,response,case_sensitive,created_by) VALUES(?,?,?,?,?)", (interaction.guild_id,trigger,response,int(case_sensitive),interaction.user.id))
        except Exception as exc:
            import sqlite3
            if isinstance(exc, sqlite3.IntegrityError): await interaction.response.send_message("A rule with that trigger already exists in this server.", ephemeral=True); return
            raise
        await interaction.response.send_message("Automatic response rule added.", ephemeral=True)

    @app_commands.command(name="autoresponse-edit", description="Edit the response or matching mode for a rule.")
    @admin_only()
    @app_commands.guild_only()
    async def edit(self, interaction: discord.Interaction, trigger: str, response: app_commands.Range[str, 1, 1500], case_sensitive: bool = False) -> None:
        cursor=await self.bot.db.fetchone("SELECT id FROM autoresponses WHERE guild_id=? AND trigger=?", (interaction.guild_id,trigger))
        if not cursor: await interaction.response.send_message("No rule found with that exact trigger.", ephemeral=True); return
        await self.bot.db.execute("UPDATE autoresponses SET response=?,case_sensitive=? WHERE id=?", (response,int(case_sensitive),cursor['id']))
        await interaction.response.send_message("Automatic response rule updated.", ephemeral=True)

    @app_commands.command(name="autoresponse-remove", description="Remove an automatic response rule.")
    @admin_only()
    @app_commands.guild_only()
    async def remove(self, interaction: discord.Interaction, trigger: str) -> None:
        await self.bot.db.execute("DELETE FROM autoresponses WHERE guild_id=? AND trigger=?", (interaction.guild_id,trigger))
        await interaction.response.send_message("Rule removed if an exact trigger match existed.", ephemeral=True)

    @app_commands.command(name="autoresponse-list", description="List configured auto-response rules.")
    @admin_only()
    @app_commands.guild_only()
    async def list_rules(self, interaction: discord.Interaction, page: app_commands.Range[int, 1, 100] = 1) -> None:
        rows=await self.bot.db.fetchall("SELECT trigger,response,case_sensitive FROM autoresponses WHERE guild_id=? ORDER BY id LIMIT 10 OFFSET ?", (interaction.guild_id,(page-1)*10))
        if not rows: await interaction.response.send_message("No rules on this page.", ephemeral=True); return
        embed=make_embed(f"Auto-responses — page {page}")
        for row in rows: embed.add_field(name=f"Trigger: {row['trigger']}", value=f"Response: {row['response'][:700]}\nCase-sensitive: {'Yes' if row['case_sensitive'] else 'No'}", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.guild is None or message.author.bot or message.webhook_id is not None or not message.content: return
        rows=await self.bot.db.fetchall("SELECT trigger,response,case_sensitive FROM autoresponses WHERE guild_id=? ORDER BY id", (message.guild.id,))
        content=message.content
        cooldown_key=(message.guild.id, message.channel.id)
        now=time.monotonic()
        if now-self._last_response.get(cooldown_key, 0.0) < 2.0:
            return
        for row in rows:
            trigger=row['trigger']
            matches=trigger in content if row['case_sensitive'] else trigger.casefold() in content.casefold()
            if not matches: continue
            if len(trigger)<2: continue
            try:
                await message.channel.send(row['response'][:1900], allowed_mentions=discord.AllowedMentions.none())
                self._last_response[cooldown_key]=now
            except discord.Forbidden: self.bot.log.warning("Auto-response blocked by permissions in guild %s", message.guild.id)
            except discord.HTTPException: self.bot.log.exception("Auto-response failed in guild %s", message.guild.id)
            break

async def setup(bot: commands.Bot) -> None: await bot.add_cog(AutoResponses(bot))
