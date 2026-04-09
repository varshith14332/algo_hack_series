"""Tests for marketplace contract box storage logic (unit level)."""
import pytest


def test_box_value_format():
    """Box value concatenation format matches contract."""
    merkle_root = "abc123"
    requester = "ABCDE12345"
    price = 5000

    box_value = f"{merkle_root}|{requester}|".encode() + price.to_bytes(8, "big")
    assert b"|" in box_value
    assert merkle_root.encode() in box_value


def test_box_value_parse():
    """Parsing box value returns correct fields."""
    merkle_root = "deadbeef"
    requester = "TESTADDR"
    price = 1000

    raw = f"{merkle_root}|{requester}|".encode() + price.to_bytes(8, "big")
    text_part = raw[: raw.rfind(b"|") + 1].decode()
    parts = text_part.split("|")
    assert parts[0] == merkle_root
    assert parts[1] == requester
