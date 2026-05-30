# tests/test_trade_engine.py
import pytest
from backend.engine.trade_engine import TradeEngine
from backend.database import SessionLocal


@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_db")
async def test_open_position():
    """Test opening a new position"""
    engine = TradeEngine()

    position = await engine.open_position(
        symbol="BTCUSDT",
        market="crypto",
        side="long",
        qty=1.0,
        entry_price=50000,
        sl=49000,
        tp=51000,
        mode="paper"
    )

    assert position is not None
    assert position.id is not None
    assert position.symbol == "BTCUSDT"
    assert position.side == "long"
    assert position.status == "OPEN"
    assert position.entry_price == 50000
    assert position.sl == 49000
    assert position.tp == 51000


@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_db")
async def test_get_open_positions():
    """Test retrieving all open positions"""
    engine = TradeEngine()

    # Open two positions
    pos1 = await engine.open_position(
        symbol="BTCUSDT",
        market="crypto",
        side="long",
        qty=1.0,
        entry_price=50000,
        sl=49000,
        tp=51000
    )

    pos2 = await engine.open_position(
        symbol="ETHUSDT",
        market="crypto",
        side="short",
        qty=10.0,
        entry_price=3000,
        sl=3100,
        tp=2900
    )

    open_positions = engine.get_open_positions()

    assert len(open_positions) == 2
    assert any(p.id == pos1.id for p in open_positions)
    assert any(p.id == pos2.id for p in open_positions)


@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_db")
async def test_close_position_manual():
    """Test manually closing a position"""
    engine = TradeEngine()

    # Open a position
    position = await engine.open_position(
        symbol="BTCUSDT",
        market="crypto",
        side="long",
        qty=1.0,
        entry_price=50000,
        sl=49000,
        tp=51000
    )

    # Close it manually
    closed_position = await engine.close_position_manual(position.id, exit_price=51000)

    assert closed_position.status == "CLOSED"
    assert closed_position.exit_price == 51000
    assert closed_position.exit_reason == "manual"
    assert closed_position.pnl == 1000  # (51000 - 50000) * 1.0
