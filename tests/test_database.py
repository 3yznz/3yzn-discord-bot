# Project: 3YZN Discord Bot
# Author: 3YZN (@3yzn)
# Copyright (c) 2026 3YZN
# License: See LICENSE
import pytest
import aiosqlite
from database import Database

@pytest.mark.asyncio
async def test_database_initializes_and_persists(tmp_path):
    db=Database(str(tmp_path / "test.sqlite3"))
    await db.initialize()
    await db.execute("INSERT INTO separator_settings(guild_id,trigger,image_url,matching_mode) VALUES(?,?,?,?)", (123,"hello","https://example.com/image.png","substring"))
    row=await db.fetchone("SELECT trigger FROM separator_settings WHERE guild_id=?", (123,))
    assert row["trigger"] == "hello"
    await db.close()
