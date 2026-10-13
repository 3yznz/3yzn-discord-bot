# Project: 3YZN Discord Bot
# Author: 3YZN (@3yzn)
# Copyright (c) 2026 3YZN
# License: See LICENSE
"""Permission and hierarchy checks for 3YZN Discord Bot."""
import discord

def can_manage_role(guild: discord.Guild, role: discord.Role, bot_member: discord.Member) -> tuple[bool, str]:
    if role.is_default():
        return False, "The @everyone role cannot be managed."
    if role.managed:
        return False, "Integration-managed roles cannot be managed manually."
    if role >= bot_member.top_role:
        return False, "That role is equal to or higher than the bot's highest role."
    return True, ""

def can_moderate(actor: discord.Member, target: discord.Member, bot_member: discord.Member) -> tuple[bool, str]:
    if target.id == actor.id:
        return False, "You cannot use this action on yourself."
    if target.id == target.guild.owner_id:
        return False, "The server owner cannot be targeted."
    if target.top_role >= actor.top_role and actor.id != target.guild.owner_id:
        return False, "Your highest role must be above the target's highest role."
    if target.top_role >= bot_member.top_role:
        return False, "The target's highest role must be below the bot's highest role."
    return True, ""
