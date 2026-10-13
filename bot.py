# Project: 3YZN Discord Bot
# Author: 3YZN (@3yzn)
# Copyright (c) 2026 3YZN
# License: See LICENSE
"""Application entry point for the 3YZN Discord Bot."""
import asyncio
import logging

import discord
from discord.ext import commands

from config import Settings, ConfigurationError
from database import Database
from utils.errors import install_error_handlers

COGS = (
    "cogs.general", "cogs.moderation", "cogs.roles", "cogs.channels",
    "cogs.embeds", "cogs.separator", "cogs.autoresponses", "cogs.settings",
)

class ThreeYZNBot(commands.Bot):
    def __init__(self, settings: Settings) -> None:
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix=commands.when_mentioned, intents=intents, help_command=None)
        self.settings = settings
        self.db = Database(settings.database_path)
        self.log = logging.getLogger("3yzn")

    async def setup_hook(self) -> None:
        await self.db.initialize()
        for extension in COGS:
            await self.load_extension(extension)
            self.log.info("Loaded extension: %s", extension)
        try:
            if self.settings.sync_mode == "guild":
                if not self.settings.dev_guild_id:
                    raise ConfigurationError("DEV_GUILD_ID is required when SYNC_MODE=guild")
                guild = discord.Object(id=self.settings.dev_guild_id)
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                self.log.info("Synchronized %d commands to development guild", len(synced))
            else:
                synced = await self.tree.sync()
                self.log.info("Synchronized %d global application commands", len(synced))
        except (discord.HTTPException, ConfigurationError):
            self.log.exception("Application command synchronization failed")
            raise

    async def close(self) -> None:
        await self.db.close()
        await super().close()

def main() -> None:
    from utils.logging_config import configure_logging
    configure_logging()
    try:
        settings = Settings.from_env()
    except ConfigurationError as exc:
        raise SystemExit(f"Configuration error: {exc}") from exc
    bot = ThreeYZNBot(settings)
    install_error_handlers(bot)
    bot.run(settings.discord_token, log_handler=None)

if __name__ == "__main__":
    main()
