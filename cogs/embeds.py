# Project: 3YZN Discord Bot
# Author: 3YZN (@3yzn)
# Copyright (c) 2026 3YZN
# License: See LICENSE
"""Custom embed builder for 3YZN Discord Bot."""
import discord
from discord import app_commands
from discord.ext import commands
from utils.embeds import make_embed
from utils.validators import valid_http_url, parse_color

class Embeds(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None: self.bot = bot

    @app_commands.command(name="embed", description="Create and send a custom embed.")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.guild_only()
    @app_commands.describe(title="Embed title", description="Main text", color="Hex color, e.g. #2F6FA8", footer="Footer text", author_name="Author label", author_icon_url="Author icon URL", thumbnail_url="Thumbnail URL", image_url="Main image URL", channel="Destination text channel", field1_name="Optional field 1 title", field1_value="Optional field 1 text", field2_name="Optional field 2 title", field2_value="Optional field 2 text")
    async def embed_command(self, interaction: discord.Interaction, title: app_commands.Range[str, 1, 256], description: app_commands.Range[str, 1, 4000], color: str = "2F6FA8", footer: str | None = None, author_name: str | None = None, author_icon_url: str | None = None, thumbnail_url: str | None = None, image_url: str | None = None, channel: discord.TextChannel | None = None, field1_name: str | None = None, field1_value: str | None = None, field2_name: str | None = None, field2_value: str | None = None) -> None:
        numeric_color=parse_color(color)
        if numeric_color is None: await interaction.response.send_message("Color must be six hexadecimal digits, optionally prefixed by #.", ephemeral=True); return
        urls=[("Author icon", author_icon_url), ("Thumbnail", thumbnail_url), ("Image", image_url)]
        for label, url in urls:
            if url and not valid_http_url(url): await interaction.response.send_message(f"{label} URL must be a valid HTTP or HTTPS URL.", ephemeral=True); return
        if bool(field1_name) != bool(field1_value) or bool(field2_name) != bool(field2_value):
            await interaction.response.send_message("Each optional field requires both a title and a value.", ephemeral=True); return
        target=channel or interaction.channel
        if not isinstance(target, discord.TextChannel) or not target.permissions_for(interaction.guild.me).send_messages or not target.permissions_for(interaction.guild.me).embed_links:
            await interaction.response.send_message("I need Send Messages and Embed Links permissions in the destination channel.", ephemeral=True); return
        embed=make_embed(title, description, discord.Color(numeric_color))
        if footer: embed.set_footer(text=footer[:2048])
        if author_name:
            if author_icon_url: embed.set_author(name=author_name[:256], icon_url=author_icon_url)
            else: embed.set_author(name=author_name[:256])
        elif author_icon_url:
            await interaction.response.send_message("Provide an author name when using an author icon URL.", ephemeral=True); return
        if thumbnail_url: embed.set_thumbnail(url=thumbnail_url)
        if image_url: embed.set_image(url=image_url)
        for name, value in ((field1_name, field1_value),(field2_name, field2_value)):
            if name and value: embed.add_field(name=name[:256], value=value[:1024], inline=False)
        await target.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())
        await interaction.response.send_message(f"Embed sent to {target.mention}.", ephemeral=True)

async def setup(bot: commands.Bot) -> None: await bot.add_cog(Embeds(bot))
