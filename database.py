# Project: 3YZN Discord Bot
# Author: 3YZN (@3yzn)
# Copyright (c) 2026 3YZN
# License: See LICENSE
"""Async SQLite persistence layer for 3YZN Discord Bot."""
from pathlib import Path
import aiosqlite

SCHEMA_VERSION = 1

class Database:
    def __init__(self, path: str) -> None:
        self.path = path
        self._connection: aiosqlite.Connection | None = None

    async def initialize(self) -> None:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._connection = await aiosqlite.connect(self.path)
        self._connection.row_factory = aiosqlite.Row
        await self._connection.execute("PRAGMA foreign_keys = ON")
        await self._connection.execute("PRAGMA journal_mode = WAL")
        await self._connection.executescript("""
        CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS separator_settings (guild_id INTEGER PRIMARY KEY, trigger TEXT NOT NULL, image_url TEXT NOT NULL, matching_mode TEXT NOT NULL DEFAULT 'substring');
        CREATE TABLE IF NOT EXISTS separator_exempt_channels (guild_id INTEGER NOT NULL, channel_id INTEGER NOT NULL, PRIMARY KEY (guild_id, channel_id), FOREIGN KEY(guild_id) REFERENCES separator_settings(guild_id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS autoresponses (id INTEGER PRIMARY KEY AUTOINCREMENT, guild_id INTEGER NOT NULL, trigger TEXT NOT NULL, response TEXT NOT NULL, case_sensitive INTEGER NOT NULL DEFAULT 0, created_by INTEGER NOT NULL, UNIQUE(guild_id, trigger));
        CREATE TABLE IF NOT EXISTS guild_settings (guild_id INTEGER PRIMARY KEY, mute_role_id INTEGER);
        """)
        await self._connection.execute("INSERT OR REPLACE INTO metadata(key, value) VALUES('schema_version', ?)", (str(SCHEMA_VERSION),))
        await self._connection.commit()

    async def close(self) -> None:
        if self._connection is not None:
            await self._connection.close()
            self._connection = None

    @property
    def connection(self) -> aiosqlite.Connection:
        if self._connection is None:
            raise RuntimeError("Database has not been initialized")
        return self._connection

    async def execute(self, query: str, parameters: tuple = ()) -> int:
        cursor = await self.connection.execute(query, parameters)
        await self.connection.commit()
        return cursor.lastrowid or 0

    async def fetchone(self, query: str, parameters: tuple = ()):
        cursor = await self.connection.execute(query, parameters)
        return await cursor.fetchone()

    async def fetchall(self, query: str, parameters: tuple = ()) -> list:
        cursor = await self.connection.execute(query, parameters)
        return await cursor.fetchall()
