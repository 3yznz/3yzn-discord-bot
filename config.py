# Project: 3YZN Discord Bot
# Author: 3YZN (@3yzn)
# Copyright (c) 2026 3YZN
# License: See LICENSE
"""Validated environment-backed configuration for 3YZN Discord Bot."""
from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv

class ConfigurationError(ValueError):
    """Raised when required configuration is missing or invalid."""

@dataclass(frozen=True, slots=True)
class Settings:
    discord_token: str
    bot_owner_id: int | None
    dev_guild_id: int | None
    sync_mode: str
    database_path: str
    log_level: str
    bulk_role_limit: int = 20

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        token = os.getenv("DISCORD_TOKEN", "").strip()
        if not token or token == "YOUR_DISCORD_BOT_TOKEN":
            raise ConfigurationError("Set DISCORD_TOKEN in your local .env file.")
        def optional_id(name: str) -> int | None:
            value = os.getenv(name, "").strip()
            if not value:
                return None
            try:
                result = int(value)
                if result <= 0:
                    raise ValueError
                return result
            except ValueError as exc:
                raise ConfigurationError(f"{name} must be a positive integer.") from exc
        mode = os.getenv("SYNC_MODE", "guild").strip().lower()
        if mode not in {"guild", "global"}:
            raise ConfigurationError("SYNC_MODE must be 'guild' or 'global'.")
        guild_id = optional_id("DEV_GUILD_ID")
        if mode == "guild" and guild_id is None:
            raise ConfigurationError("DEV_GUILD_ID is required for guild sync.")
        level = os.getenv("LOG_LEVEL", "INFO").upper()
        if level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ConfigurationError("LOG_LEVEL is not a valid logging level.")
        try:
            limit = int(os.getenv("BULK_ROLE_LIMIT", "20"))
        except ValueError as exc:
            raise ConfigurationError("BULK_ROLE_LIMIT must be an integer.") from exc
        if not 1 <= limit <= 100:
            raise ConfigurationError("BULK_ROLE_LIMIT must be between 1 and 100.")
        db_path = os.getenv("DATABASE_PATH", "data/3yzn.sqlite3").strip()
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        return cls(token, optional_id("BOT_OWNER_ID"), guild_id, mode, db_path, level, limit)
