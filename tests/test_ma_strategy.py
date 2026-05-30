from backend.strategies.ma_crossover import MACrossoverStrategy
from backend.database import Candle
from datetime import datetime, timedelta

def test_ma_bullish_crossover():
    """Test MA20 crossing above MA50"""
    strategy = MACrossoverStrategy()
    
    # Create 100 candles. 
    # Use 100 for first 99 candles, then 110 for the last one.
    # This will ensure MA20 crosses above MA50 on the last candle.
    candles = []
    base_time = datetime.utcnow() - timedelta(days=5)
    for i in range(100):
        close = 100.0
        if i == 99:
            close = 110.0
            
        candles.append(Candle(
            id=i,
            symbol="BTCUSDT",
            market="crypto",
            timeframe="1h",
            open_time=base_time + timedelta(hours=i),
            close_time=base_time + timedelta(hours=i, minutes=59),
            open=close,
            high=close + 1,
            low=close - 1,
            close=close,
            volume=1000
        ))
    
    signal = strategy.analyze(candles)
    
    assert signal is not None
    assert signal["side"] == "long"
    assert signal["confidence"] == 0.7

def test_ma_bearish_crossover():
    """Test MA20 crossing below MA50"""
    strategy = MACrossoverStrategy()
    
    # Create 100 candles.
    # Use 100 for first 99 candles, then 90 for the last one.
    # This will ensure MA20 crosses below MA50 on the last candle.
    candles = []
    base_time = datetime.utcnow() - timedelta(days=5)
    for i in range(100):
        close = 100.0
        if i == 99:
            close = 90.0
            
        candles.append(Candle(
            id=i,
            symbol="ETHUSDT",
            market="crypto",
            timeframe="1h",
            open_time=base_time + timedelta(hours=i),
            close_time=base_time + timedelta(hours=i, minutes=59),
            open=close,
            high=close + 1,
            low=close - 1,
            close=close,
            volume=1000
        ))
    
    signal = strategy.analyze(candles)
    
    assert signal is not None
    assert signal["side"] == "short"
    assert signal["confidence"] == 0.7

def test_ma_no_signal():
    """Test no signal when MAs haven't crossed"""
    strategy = MACrossoverStrategy()
    
    # Create flat candles (no crossover)
    candles = []
    for i in range(70):
        candles.append(Candle(
            id=i,
            symbol="BTCUSDT",
            market="crypto",
            timeframe="1h",
            open_time=datetime.utcnow(),
            close_time=datetime.utcnow(),
            open=100,
            high=101,
            low=99,
            close=100,
            volume=1000
        ))
    
    signal = strategy.analyze(candles)
    
    assert signal is None
