# tests/test_models.py
import pytest
from backend.database import Position
from datetime import datetime

def test_position_calculate_pnl_long():
    pos = Position(
        id="1",
        symbol="BTCUSDT",
        market="crypto",
        side="long",
        qty=1.0,
        entry_price=50000,
        sl=49000,
        tp=51000,
        status="CLOSED",
        mode="paper",
        opened_at=datetime.utcnow()
    )
    pnl = pos.calculate_pnl(51000)  # exit at TP
    assert pnl == 1000  # (51000 - 50000) * 1.0

def test_position_calculate_pnl_short():
    pos = Position(
        id="2",
        symbol="BTCUSDT",
        market="crypto",
        side="short",
        qty=1.0,
        entry_price=50000,
        sl=51000,
        tp=49000,
        status="CLOSED",
        mode="paper",
        opened_at=datetime.utcnow()
    )
    pnl = pos.calculate_pnl(49000)  # exit at TP
    assert pnl == 1000  # (50000 - 49000) * 1.0

def test_position_calculate_pnl_long_loss():
    """Test PnL calculation for a losing long trade"""
    pos = Position(
        id="3",
        symbol="BTCUSDT",
        market="crypto",
        side="long",
        qty=1.0,
        entry_price=50000,
        sl=49000,
        tp=51000,
        status="CLOSED",
        mode="paper",
        opened_at=datetime.utcnow()
    )
    pnl = pos.calculate_pnl(49500)  # exit at loss
    assert pnl == -500  # (49500 - 50000) * 1.0

def test_position_calculate_pnl_short_loss():
    """Test PnL calculation for a losing short trade"""
    pos = Position(
        id="4",
        symbol="BTCUSDT",
        market="crypto",
        side="short",
        qty=1.0,
        entry_price=50000,
        sl=51000,
        tp=49000,
        status="CLOSED",
        mode="paper",
        opened_at=datetime.utcnow()
    )
    pnl = pos.calculate_pnl(50500)  # exit at loss
    assert pnl == -500  # (50000 - 50500) * 1.0

def test_position_calculate_pnl_invalid_side():
    """Test that calculate_pnl raises ValueError on invalid side"""
    pos = Position(
        id="5",
        symbol="BTCUSDT",
        market="crypto",
        side="invalid_side",  # bad value
        qty=1.0,
        entry_price=50000,
        sl=49000,
        tp=51000,
        status="CLOSED",
        mode="paper",
        opened_at=datetime.utcnow()
    )
    with pytest.raises(ValueError, match="Invalid side"):
        pos.calculate_pnl(51000)
