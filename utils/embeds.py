# Project: 3YZN Discord Bot
# Author: 3YZN (@3yzn)
# Copyright (c) 2026 3YZN
# License: See LICENSE
"""Shared embed styling for 3YZN Discord Bot."""
import discord

BRAND = "3YZN • Discord Bot"
COLOR = discord.Color.from_rgb(47, 111, 168)
SUCCESS = discord.Color.from_rgb(46, 160, 98)
WARNING = discord.Color.from_rgb(204, 146, 35)
ERROR = discord.Color.from_rgb(190, 62, 62)

def make_embed(title: str, description: str | None = None, color: discord.Color = COLOR) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text=BRAND)
    return embed
