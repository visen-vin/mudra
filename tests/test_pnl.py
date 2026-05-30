# tests/test_pnl.py
import pytest
from backend.engine.pnl_calculator import PnLCalculator


def test_pnl_long_profit():
    """Test PnL calculation for a profitable long trade"""
    pnl, pnl_pct = PnLCalculator.calculate(
        side="long",
        entry_price=50000,
        exit_price=51000,
        qty=1.0
    )
    assert pnl == 1000
    assert abs(pnl_pct - 2.0) < 0.01


def test_pnl_long_loss():
    """Test PnL calculation for a losing long trade"""
    pnl, pnl_pct = PnLCalculator.calculate(
        side="long",
        entry_price=50000,
        exit_price=49000,
        qty=1.0
    )
    assert pnl == -1000
    assert abs(pnl_pct - (-2.0)) < 0.01


def test_pnl_short_profit():
    """Test PnL calculation for a profitable short trade"""
    pnl, pnl_pct = PnLCalculator.calculate(
        side="short",
        entry_price=50000,
        exit_price=49000,
        qty=1.0
    )
    assert pnl == 1000
    assert abs(pnl_pct - 2.0) < 0.01


def test_pnl_short_loss():
    """Test PnL calculation for a losing short trade"""
    pnl, pnl_pct = PnLCalculator.calculate(
        side="short",
        entry_price=50000,
        exit_price=51000,
        qty=1.0
    )
    assert pnl == -1000
    assert abs(pnl_pct - (-2.0)) < 0.01
