# Project: 3YZN Discord Bot
# Author: 3YZN (@3yzn)
# Copyright (c) 2026 3YZN
# License: See LICENSE
"""Central application-command error handling for 3YZN Discord Bot."""
import logging
import discord
from discord import app_commands
from discord.ext import commands
from utils.embeds import make_embed, ERROR

log = logging.getLogger("3yzn.errors")

async def _respond(interaction: discord.Interaction, message: str) -> None:
    embed = make_embed("Unable to complete command", message, ERROR)
    if interaction.response.is_done():
        await interaction.followup.send(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message(embed=embed, ephemeral=True)

def install_error_handlers(bot: commands.Bot) -> None:
    @bot.tree.error
    async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.MissingPermissions):
            message = "You do not have the required Discord permissions for this command."
        elif isinstance(error, app_commands.BotMissingPermissions):
            message = "The bot is missing a required Discord permission."
        elif isinstance(error, app_commands.CommandOnCooldown):
            message = f"Try again in {error.retry_after:.1f} seconds."
        elif isinstance(error, app_commands.CheckFailure):
            message = "You are not authorized to use this command here."
        else:
            log.error("Unhandled app command error for %s", interaction.command.name if interaction.command else "unknown", exc_info=(type(error), error, error.__traceback__))
            message = "An unexpected error occurred. The issue was logged for the bot maintainer."
        await _respond(interaction, message)
