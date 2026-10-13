# Project: 3YZN Discord Bot
# Author: 3YZN (@3yzn)
# Copyright (c) 2026 3YZN
# License: See LICENSE
import pytest
from config import ConfigurationError, Settings

def test_rejects_missing_token(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN", "")
    monkeypatch.setenv("SYNC_MODE", "guild")
    monkeypatch.setenv("DEV_GUILD_ID", "123")
    with pytest.raises(ConfigurationError): Settings.from_env()

def test_rejects_invalid_sync_mode(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN", "example-token")
    monkeypatch.setenv("SYNC_MODE", "invalid")
    with pytest.raises(ConfigurationError): Settings.from_env()
