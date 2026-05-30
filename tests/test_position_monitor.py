# tests/test_position_monitor.py
import pytest
from backend.database import Position
from backend.engine.position_monitor import PositionMonitor
from datetime import datetime


def test_position_monitor_sl_hit_long():
    """Test SL hit for a long position"""
    position = Position(
        id="test_1",
        symbol="BTCUSDT",
        market="crypto",
        side="long",
        qty=1.0,
        entry_price=50000,
        sl=49000,
        tp=51000,
        status="OPEN",
        mode="paper",
        opened_at=datetime.utcnow()
    )

    monitor = PositionMonitor()
    exit_event = monitor.check_exit(position, 48900)  # Below SL

    assert exit_event is not None
    assert exit_event["exit_reason"] == "SL"
    assert exit_event["exit_price"] == 48900
    assert exit_event["status"] == "CLOSED"


def test_position_monitor_tp_hit_long():
    """Test TP hit for a long position"""
    position = Position(
        id="test_2",
        symbol="BTCUSDT",
        market="crypto",
        side="long",
        qty=1.0,
        entry_price=50000,
        sl=49000,
        tp=51000,
        status="OPEN",
        mode="paper",
        opened_at=datetime.utcnow()
    )

    monitor = PositionMonitor()
    exit_event = monitor.check_exit(position, 51100)  # Above TP

    assert exit_event is not None
    assert exit_event["exit_reason"] == "TP"
    assert exit_event["exit_price"] == 51100
    assert exit_event["status"] == "CLOSED"


def test_position_monitor_sl_hit_short():
    """Test SL hit for a short position"""
    position = Position(
        id="test_3",
        symbol="BTCUSDT",
        market="crypto",
        side="short",
        qty=1.0,
        entry_price=50000,
        sl=51000,
        tp=49000,
        status="OPEN",
        mode="paper",
        opened_at=datetime.utcnow()
    )

    monitor = PositionMonitor()
    exit_event = monitor.check_exit(position, 51100)  # Above SL

    assert exit_event is not None
    assert exit_event["exit_reason"] == "SL"
    assert exit_event["exit_price"] == 51100
    assert exit_event["status"] == "CLOSED"


def test_position_monitor_no_exit():
    """Test no exit when price is between SL and TP"""
    position = Position(
        id="test_4",
        symbol="BTCUSDT",
        market="crypto",
        side="long",
        qty=1.0,
        entry_price=50000,
        sl=49000,
        tp=51000,
        status="OPEN",
        mode="paper",
        opened_at=datetime.utcnow()
    )

    monitor = PositionMonitor()
    exit_event = monitor.check_exit(position, 50500)  # Between SL and TP

    assert exit_event is None
