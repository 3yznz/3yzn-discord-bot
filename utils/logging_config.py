# Project: 3YZN Discord Bot
# Author: 3YZN (@3yzn)
# Copyright (c) 2026 3YZN
# License: See LICENSE
"""Logging configuration for 3YZN Discord Bot."""
import logging
import os

def configure_logging() -> None:
    level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
    logging.basicConfig(level=level, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
