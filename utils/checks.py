# Project: 3YZN Discord Bot
# Author: 3YZN (@3yzn)
# Copyright (c) 2026 3YZN
# License: See LICENSE
"""Reusable app-command checks for 3YZN Discord Bot."""
from discord import app_commands

def admin_only():
    return app_commands.checks.has_permissions(administrator=True)

def moderator_only():
    return app_commands.checks.has_permissions(moderate_members=True)
