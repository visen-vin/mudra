# tests/test_signal_service.py
from backend.services.signal_service import SignalService
from backend.database import init_db
from datetime import datetime

def setup_function():
    init_db()

def test_create_signal():
    signal = SignalService.create_signal(
        strategy="MA_CROSSOVER",
        symbol="BTCUSDT",
        side="long",
        confidence=0.75,
        candle_close_time=datetime.utcnow()
    )
    
    assert signal.signal_id is not None
    assert signal.strategy == "MA_CROSSOVER"
    assert signal.symbol == "BTCUSDT"

def test_get_signals():
    SignalService.create_signal(
        strategy="MA_CROSSOVER",
        symbol="ETHUSDT",
        side="short",
        confidence=0.65,
        candle_close_time=datetime.utcnow()
    )
    
    signals = SignalService.get_signals(limit=10)
    assert len(signals) >= 1
