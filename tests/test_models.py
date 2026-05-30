# tests/test_models.py
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
