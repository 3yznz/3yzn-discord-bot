# Project: 3YZN Discord Bot
# Author: 3YZN (@3yzn)
# Copyright (c) 2026 3YZN
# License: See LICENSE
"""Input validation helpers for 3YZN Discord Bot."""
from urllib.parse import urlparse
import re

def valid_http_url(value: str) -> bool:
    try:
        parsed = urlparse(value.strip())
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc) and not any(c.isspace() for c in value)
    except (ValueError, AttributeError):
        return False

def parse_color(value: str) -> int | None:
    normalized = value.strip().removeprefix("#").removeprefix("0x")
    if not re.fullmatch(r"[0-9a-fA-F]{6}", normalized):
        return None
    return int(normalized, 16)

def safe_text(value: str, limit: int, field: str) -> str:
    value = value.strip()
    if not value or len(value) > limit:
        raise ValueError(f"{field} must contain 1 to {limit} characters.")
    return value
