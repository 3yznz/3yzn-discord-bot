# Project: 3YZN Discord Bot
# Author: 3YZN (@3yzn)
# Copyright (c) 2026 3YZN
# License: See LICENSE
"""General information and utility slash commands for 3YZN Discord Bot."""
import discord
from discord import app_commands
from discord.ext import commands
from utils.embeds import make_embed

class General(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None: self.bot = bot

    @app_commands.command(name="say", description="Send a message as the bot.")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.describe(message="Message to send", channel="Where to send it (defaults to this channel)")
    async def say(self, interaction: discord.Interaction, message: app_commands.Range[str, 1, 1800], channel: discord.TextChannel | None = None) -> None:
        target = channel or interaction.channel
        if not isinstance(target, discord.TextChannel):
            await interaction.response.send_message("This command requires a text channel.", ephemeral=True); return
        if not target.permissions_for(interaction.guild.me).send_messages:
            await interaction.response.send_message("I cannot send messages in that channel.", ephemeral=True); return
        await target.send(message, allowed_mentions=discord.AllowedMentions.none())
        await interaction.response.send_message(f"Message sent to {target.mention}.", ephemeral=True)

    @app_commands.command(name="help", description="Show the command guide.")
    async def help_command(self, interaction: discord.Interaction) -> None:
        embed = make_embed("3YZN Discord Bot — Help", "All user-facing commands are slash commands. Administrative commands require the permissions described in the documentation.")
        embed.add_field(name="General", value="`/say` `/avatar` `/banner` `/user` `/server` `/come` `/help`", inline=False)
        embed.add_field(name="Moderation", value="`/kick` `/ban` `/unban` `/timeout` `/untimeout` `/mute` `/unmute` `/clear` `/slowmode` `/nickname` `/unnickname`", inline=False)
        embed.add_field(name="Roles and channels", value="`/role-add` `/role-remove` `/role-add-bulk` `/role-remove-bulk` `/hide-channel` `/unhide-channel`", inline=False)
        embed.add_field(name="Embeds and automation", value="`/embed` `/separator-set` `/separator-remove` `/separator-exempt-channel-add` `/separator-exempt-channel-remove` `/separator-settings` `/autoresponse-add` `/autoresponse-edit` `/autoresponse-remove` `/autoresponse-list` `/settings-mute-role`", inline=False)
        embed.add_field(name="Note", value="Discord has no reversible `/unkick` action. A kicked member may rejoin using a valid invite if server settings allow it.", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="avatar", description="Show a user's avatar.")
    async def avatar(self, interaction: discord.Interaction, user: discord.User | None = None) -> None:
        target = user or interaction.user
        embed = make_embed(f"{target.display_name}'s avatar")
        embed.set_image(url=target.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="banner", description="Show a user's profile banner if available.")
    async def banner(self, interaction: discord.Interaction, user: discord.User | None = None) -> None:
        target = user or interaction.user
        try: target = await self.bot.fetch_user(target.id)
        except discord.HTTPException:
            await interaction.response.send_message("I could not retrieve that user's profile right now.", ephemeral=True); return
        if not target.banner:
            await interaction.response.send_message("That user has no accessible profile banner.", ephemeral=True); return
        embed = make_embed(f"{target.display_name}'s banner"); embed.set_image(url=target.banner.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="user", description="Show account and server information about a user.")
    async def user_info(self, interaction: discord.Interaction, user: discord.Member | None = None) -> None:
        target = user or interaction.user
        embed = make_embed(f"User information: {target}")
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="User ID", value=str(target.id), inline=True)
        embed.add_field(name="Account created", value=discord.utils.format_dt(target.created_at, style="D"), inline=True)
        embed.add_field(name="Joined server", value=discord.utils.format_dt(target.joined_at, style="D") if target.joined_at else "Unknown", inline=True)
        embed.add_field(name="Top role", value=target.top_role.mention, inline=True)
        embed.add_field(name="Roles", value=str(max(0, len(target.roles)-1)), inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="server", description="Show information about this server.")
    @app_commands.guild_only()
    async def server_info(self, interaction: discord.Interaction) -> None:
        guild = interaction.guild
        embed = make_embed(f"Server information: {guild.name}")
        if guild.icon: embed.set_thumbnail(url=guild.icon.url)
        owner = guild.owner or await self.bot.fetch_user(guild.owner_id)
        embed.add_field(name="Owner", value=str(owner), inline=True)
        embed.add_field(name="Members", value=str(guild.member_count or "Unavailable"), inline=True)
        embed.add_field(name="Created", value=discord.utils.format_dt(guild.created_at, style="D"), inline=True)
        embed.add_field(name="Server ID", value=str(guild.id), inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="come", description="Invite a user to a selected channel.")
    @app_commands.describe(user="User to invite", channel="Destination channel", message="Invitation text")
    async def come(self, interaction: discord.Interaction, user: discord.Member, channel: discord.TextChannel, message: app_commands.Range[str, 1, 500] = "You have been invited to join this channel.") -> None:
        if not channel.permissions_for(interaction.guild.me).view_channel or not channel.permissions_for(interaction.guild.me).send_messages:
            await interaction.response.send_message("I cannot access or send messages in that channel.", ephemeral=True); return
        embed = make_embed("Channel invitation", f"{user.mention}, {message}\nDestination: {channel.mention}")
        await interaction.response.send_message(embed=embed, allowed_mentions=discord.AllowedMentions(users=True), ephemeral=False)

async def setup(bot: commands.Bot) -> None: await bot.add_cog(General(bot))
