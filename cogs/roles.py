# Project: 3YZN Discord Bot
# Author: 3YZN (@3yzn)
# Copyright (c) 2026 3YZN
# License: See LICENSE
"""Role assignment commands for 3YZN Discord Bot."""
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from utils.permissions import can_manage_role, can_moderate

class Roles(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None: self.bot = bot

    async def role_action(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role, add: bool) -> bool:
        ok, message = can_manage_role(interaction.guild, role, interaction.guild.me)
        if not ok: await interaction.response.send_message(message, ephemeral=True); return False
        actor = interaction.user
        if isinstance(actor, discord.Member) and member.id != actor.id and member.id != interaction.guild.owner_id and member.top_role >= actor.top_role and actor.id != interaction.guild.owner_id:
            await interaction.response.send_message("Your highest role must be above the target member's highest role.", ephemeral=True); return False
        if add: await member.add_roles(role, reason=f"Role assigned by {interaction.user}")
        else: await member.remove_roles(role, reason=f"Role removed by {interaction.user}")
        return True

    @app_commands.command(name="role-add", description="Assign a role to one member.")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.guild_only()
    async def role_add(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role) -> None:
        if await self.role_action(interaction, member, role, True): await interaction.response.send_message(f"Assigned {role.mention} to {member.mention}.", ephemeral=True)

    @app_commands.command(name="role-remove", description="Remove a role from one member.")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.guild_only()
    async def role_remove(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role) -> None:
        if await self.role_action(interaction, member, role, False): await interaction.response.send_message(f"Removed {role.mention} from {member.mention}.", ephemeral=True)

    async def bulk(self, interaction: discord.Interaction, members: str, role: discord.Role, add: bool) -> None:
        ids=[]
        for part in members.replace(',', ' ').split():
            token=part.strip('<@!>')
            if token.isdigit(): ids.append(int(token))
        ids=list(dict.fromkeys(ids))
        limit=self.bot.settings.bulk_role_limit
        if not ids or len(ids)>limit:
            await interaction.response.send_message(f"Provide 1 to {limit} unique member IDs or mentions.", ephemeral=True); return
        ok, message=can_manage_role(interaction.guild, role, interaction.guild.me)
        if not ok: await interaction.response.send_message(message, ephemeral=True); return
        await interaction.response.defer(ephemeral=True, thinking=True)
        success=0; failures=[]
        for uid in ids:
            member=interaction.guild.get_member(uid)
            if member is None: failures.append(f"{uid}: not found in this server"); continue
            actor=interaction.user
            if isinstance(actor, discord.Member) and actor.id != interaction.guild.owner_id and member.id != actor.id and member.top_role >= actor.top_role:
                failures.append(f"{member}: member role hierarchy prevents action"); continue
            try:
                if add: await member.add_roles(role, reason=f"Bulk role action by {interaction.user}")
                else: await member.remove_roles(role, reason=f"Bulk role action by {interaction.user}")
                success+=1
            except (discord.Forbidden, discord.HTTPException) as exc: failures.append(f"{member}: {type(exc).__name__}")
            await asyncio.sleep(0.15)
        details=f"Completed: {success}/{len(ids)}."
        if failures: details += "\nFailures:\n" + "\n".join(failures[:10])
        await interaction.followup.send(details, ephemeral=True)

    @app_commands.command(name="role-add-bulk", description="Assign a role to multiple members using IDs or mentions.")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.guild_only()
    async def role_add_bulk(self, interaction: discord.Interaction, members: app_commands.Range[str, 1, 1800], role: discord.Role) -> None: await self.bulk(interaction, members, role, True)

    @app_commands.command(name="role-remove-bulk", description="Remove a role from multiple members using IDs or mentions.")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.guild_only()
    async def role_remove_bulk(self, interaction: discord.Interaction, members: app_commands.Range[str, 1, 1800], role: discord.Role) -> None: await self.bulk(interaction, members, role, False)

async def setup(bot: commands.Bot) -> None: await bot.add_cog(Roles(bot))
