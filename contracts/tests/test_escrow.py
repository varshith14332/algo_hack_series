"""Basic tests for escrow contract logic (unit level, no chain needed)."""
import pytest


def test_platform_share_calculation():
    """Verify basis point split logic."""
    total = 5000  # microALGO
    platform_bps = 7000  # 70%

    platform_amt = (total * platform_bps) // 10000
    requester_amt = total - platform_amt

    assert platform_amt == 3500
    assert requester_amt == 1500
    assert platform_amt + requester_amt == total


def test_requester_share_remainder():
    """Remainder always goes to requester."""
    total = 1000
    platform_bps = 7000
    platform_amt = (total * platform_bps) // 10000
    requester_amt = total - platform_amt
    assert requester_amt > 0
    assert requester_amt + platform_amt == total
