# Project: 3YZN Discord Bot
# Author: 3YZN (@3yzn)
# Copyright (c) 2026 3YZN
# License: See LICENSE
"""Moderation slash commands for 3YZN Discord Bot."""
from datetime import timedelta
import discord
from discord import app_commands
from discord.ext import commands
from utils.embeds import make_embed, SUCCESS, ERROR
from utils.permissions import can_moderate, can_manage_role

def reason_text(reason: str | None) -> str: return (reason or "No reason provided")[:450]

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None: self.bot = bot

    async def check_target(self, interaction: discord.Interaction, target: discord.Member) -> bool:
        actor = interaction.user; bot_member = interaction.guild.me
        if not isinstance(actor, discord.Member) or bot_member is None: return False
        ok, message = can_moderate(actor, target, bot_member)
        if not ok: await interaction.response.send_message(message, ephemeral=True); return False
        return True

    @app_commands.command(name="kick", description="Kick a member from this server.")
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.guild_only()
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str | None = None) -> None:
        if not await self.check_target(interaction, member): return
        await member.kick(reason=reason_text(reason)); await interaction.response.send_message(embed=make_embed("Member kicked", f"{member} was kicked. Reason: {reason_text(reason)}", SUCCESS), ephemeral=True)

    @app_commands.command(name="ban", description="Ban a member from this server.")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.guild_only()
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str | None = None, delete_message_days: app_commands.Range[int, 0, 7] = 0) -> None:
        if not await self.check_target(interaction, member): return
        await interaction.guild.ban(member, reason=reason_text(reason), delete_message_seconds=delete_message_days*86400)
        await interaction.response.send_message(embed=make_embed("Member banned", f"{member} was banned. Reason: {reason_text(reason)}", SUCCESS), ephemeral=True)

    @app_commands.command(name="unban", description="Unban a user by Discord user ID.")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.guild_only()
    async def unban(self, interaction: discord.Interaction, user_id: str, reason: str | None = None) -> None:
        try: uid = int(user_id)
        except ValueError:
            await interaction.response.send_message("User ID must be a numeric Discord ID.", ephemeral=True); return
        try:
            user = await self.bot.fetch_user(uid); await interaction.guild.unban(user, reason=reason_text(reason))
        except discord.NotFound:
            await interaction.response.send_message("That user is not banned here, or the ID does not exist.", ephemeral=True); return
        await interaction.response.send_message(embed=make_embed("User unbanned", f"{user} was unbanned.", SUCCESS), ephemeral=True)

    @app_commands.command(name="timeout", description="Apply Discord's native member timeout.")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.guild_only()
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, minutes: app_commands.Range[int, 1, 40320], reason: str | None = None) -> None:
        if not await self.check_target(interaction, member): return
        await member.timeout(timedelta(minutes=minutes), reason=reason_text(reason))
        await interaction.response.send_message(embed=make_embed("Timeout applied", f"{member} timed out for {minutes} minute(s).", SUCCESS), ephemeral=True)

    @app_commands.command(name="untimeout", description="Remove a member's native timeout.")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.guild_only()
    async def untimeout(self, interaction: discord.Interaction, member: discord.Member, reason: str | None = None) -> None:
        if not await self.check_target(interaction, member): return
        await member.timeout(None, reason=reason_text(reason)); await interaction.response.send_message(f"Timeout removed for {member}.", ephemeral=True)

    @app_commands.command(name="mute", description="Assign the configured mute role to a member.")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.guild_only()
    async def mute(self, interaction: discord.Interaction, member: discord.Member, reason: str | None = None) -> None:
        if not await self.check_target(interaction, member): return
        row = await self.bot.db.fetchone("SELECT mute_role_id FROM guild_settings WHERE guild_id=?", (interaction.guild_id,))
        role = interaction.guild.get_role(row["mute_role_id"]) if row and row["mute_role_id"] else None
        if role is None:
            await interaction.response.send_message("Configure a mute role first with `/settings-mute-role`.", ephemeral=True); return
        ok, message = can_manage_role(interaction.guild, role, interaction.guild.me)
        if not ok: await interaction.response.send_message(message, ephemeral=True); return
        await member.add_roles(role, reason=reason_text(reason)); await interaction.response.send_message(f"Mute role {role.mention} assigned to {member}.", ephemeral=True)

    @app_commands.command(name="unmute", description="Remove the configured mute role from a member.")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.guild_only()
    async def unmute(self, interaction: discord.Interaction, member: discord.Member, reason: str | None = None) -> None:
        row = await self.bot.db.fetchone("SELECT mute_role_id FROM guild_settings WHERE guild_id=?", (interaction.guild_id,))
        role = interaction.guild.get_role(row["mute_role_id"]) if row and row["mute_role_id"] else None
        if role is None or role not in member.roles:
            await interaction.response.send_message("The configured mute role is missing or not assigned to that member.", ephemeral=True); return
        await member.remove_roles(role, reason=reason_text(reason)); await interaction.response.send_message(f"Mute role removed from {member}.", ephemeral=True)

    @app_commands.command(name="clear", description="Delete recent messages in this channel.")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.guild_only()
    async def clear(self, interaction: discord.Interaction, amount: app_commands.Range[int, 1, 100]) -> None:
        if not isinstance(interaction.channel, discord.TextChannel):
            await interaction.response.send_message("Use this in a text channel.", ephemeral=True); return
        await interaction.response.defer(ephemeral=True, thinking=True)
        try: deleted = await interaction.channel.purge(limit=amount, bulk=True, reason=f"Requested by {interaction.user}")
        except discord.Forbidden:
            await interaction.followup.send("I lack permission to manage messages in this channel.", ephemeral=True); return
        await interaction.followup.send(f"Deleted {len(deleted)} message(s). Discord does not bulk-delete messages older than 14 days; those may remain.", ephemeral=True)

    @app_commands.command(name="slowmode", description="Set this text channel's slowmode in seconds.")
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.guild_only()
    async def slowmode(self, interaction: discord.Interaction, seconds: app_commands.Range[int, 0, 21600]) -> None:
        if not isinstance(interaction.channel, discord.TextChannel): await interaction.response.send_message("Use this in a text channel.", ephemeral=True); return
        await interaction.channel.edit(slowmode_delay=seconds, reason=f"Changed by {interaction.user}")
        await interaction.response.send_message(f"Slowmode set to {seconds} second(s).", ephemeral=True)

    @app_commands.command(name="nickname", description="Change a member's server nickname.")
    @app_commands.checks.has_permissions(manage_nicknames=True)
    @app_commands.guild_only()
    async def nickname(self, interaction: discord.Interaction, member: discord.Member, nickname: app_commands.Range[str, 1, 32], reason: str | None = None) -> None:
        if not await self.check_target(interaction, member): return
        await member.edit(nick=nickname, reason=reason_text(reason)); await interaction.response.send_message(f"Nickname updated for {member}.", ephemeral=True)

    @app_commands.command(name="unnickname", description="Remove a member's server nickname.")
    @app_commands.checks.has_permissions(manage_nicknames=True)
    @app_commands.guild_only()
    async def unnickname(self, interaction: discord.Interaction, member: discord.Member, reason: str | None = None) -> None:
        if not await self.check_target(interaction, member): return
        await member.edit(nick=None, reason=reason_text(reason)); await interaction.response.send_message(f"Nickname reset for {member}.", ephemeral=True)

async def setup(bot: commands.Bot) -> None: await bot.add_cog(Moderation(bot))
