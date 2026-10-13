# Project: 3YZN Discord Bot
# Author: 3YZN (@3yzn)
# Copyright (c) 2026 3YZN
# License: See LICENSE
from utils.validators import valid_http_url, parse_color, safe_text
import pytest

def test_url_validation():
    assert valid_http_url("https://example.com/image.png")
    assert not valid_http_url("javascript:alert(1)")
    assert not valid_http_url("not a url")

def test_color_parser():
    assert parse_color("#2F6FA8") == 0x2F6FA8
    assert parse_color("bad") is None

def test_safe_text_limits():
    assert safe_text(" hi ", 5, "value") == "hi"
    with pytest.raises(ValueError): safe_text("", 5, "value")
