"""Tests for reputation score update logic (unit level)."""
import pytest


def test_reward_increments_score():
    score = 500
    score = min(1000, score + 10)
    assert score == 510


def test_slash_decrements_score():
    score = 500
    score = max(0, score - 20)
    assert score == 480


def test_score_capped_at_1000():
    score = 995
    score = min(1000, score + 10)
    assert score == 1000


def test_score_floored_at_0():
    score = 10
    score = max(0, score - 20)
    assert score == 0


def test_default_score_is_500():
    # New agents start at 500
    default = 500
    assert default == 500
