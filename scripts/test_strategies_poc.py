import sys
import os
from datetime import datetime, timedelta

# Add the project root to sys.path
sys.path.append("/Users/vin/Projects/mudra")

from backend.database import Candle
from backend.strategies.ma_crossover import MACrossoverStrategy
from backend.strategies.registry import get_active_strategies

def test_ma_crossover():
    print("Testing MA Crossover Strategy...")
    strategy = MACrossoverStrategy()
    
    # Create 30 candles with an upward trend to trigger a LONG signal
    candles = []
    base_price = 100.0
    for i in range(30):
        candle = Candle(
            symbol="TEST",
            market="crypto",
            timeframe="1m",
            open_time=datetime.now() - timedelta(minutes=30-i),
            close_time=datetime.now() - timedelta(minutes=29-i),
            open=base_price + i,
            high=base_price + i + 1,
            low=base_price + i - 1,
            close=base_price + i + 0.5,
            volume=1000.0
        )
        candles.append(candle)
    
    signal = strategy.analyze(candles)
    if signal:
        print(f"Signal generated: {signal}")
    else:
        print("No signal generated")

def test_registry():
    print("\nTesting Strategy Registry...")
    # Mocking environment variable to avoid DB issues in test
    os.environ["ENABLED_STRATEGIES"] = "MACrossoverStrategy"
    
    strategies = get_active_strategies()
    print(f"Active strategies: {[s.name for s in strategies]}")
    if any(isinstance(s, MACrossoverStrategy) for s in strategies):
        print("MACrossoverStrategy successfully loaded through registry")
    else:
        print("MACrossoverStrategy NOT found in active strategies")

if __name__ == "__main__":
    try:
        import pandas
        test_ma_crossover()
        test_registry()
    except ImportError as e:
        print(f"Skipping tests due to missing dependencies: {e}")
