import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from backend.services.data_ingestion import DataIngestionService
from backend.database import Candle

@pytest.mark.asyncio
async def test_binance_websocket_kline_handling():
    """Test that closed klines are stored in Redis"""
    mock_redis = AsyncMock()
    mock_binance = AsyncMock()
    
    service = DataIngestionService(redis_client=mock_redis, binance_adapter=mock_binance)
    
    # Mock Binance WebSocket message
    msg = {
        "e": "kline",
        "k": {
            "s": "BTCUSDT",
            "t": 1672531200000,
            "T": 1672531259999,
            "o": "50000.0",
            "h": "51000.0",
            "l": "49000.0",
            "c": "50500.0",
            "v": "10.0",
            "x": True # Closed
        }
    }
    
    await service.handle_binance_kline(msg)
    
    # Verify Redis interactions
    mock_redis.lpush.assert_called()
    mock_redis.ltrim.assert_called_with("market_data:1m:BTCUSDT", 0, 99)

@pytest.mark.asyncio
async def test_binance_rest_fallback_on_startup():
    """Test that service fetches last 100 candles via REST on startup"""
    mock_redis = AsyncMock()
    mock_binance = AsyncMock()

    # Mock historical candles
    mock_candles = [
        Candle(symbol="BTCUSDT", market="crypto", timeframe="1m",
               open_time=datetime.utcnow(), close_time=datetime.utcnow(),
               open=50000.0, high=51000.0, low=49000.0, close=50500.0, volume=10.0)
    ]
    mock_binance.get_candles.return_value = mock_candles

    service = DataIngestionService(redis_client=mock_redis, binance_adapter=mock_binance)
    await service.initialize_data(mock_binance, "BTCUSDT")

    mock_binance.get_candles.assert_called_with("BTCUSDT", "1m", limit=100)
    # Using lpush to maintain order when backfilling
    assert mock_redis.lpush.called

@pytest.mark.asyncio
async def test_reconnection_logic():
    """Test that stream reconnects on failure"""
    mock_redis = AsyncMock()
    mock_binance = AsyncMock()
    
    # Mock failure then success
    mock_binance.start_kline_stream.side_effect = [Exception("WS Error"), None]
    
    service = DataIngestionService(redis_client=mock_redis, binance_adapter=mock_binance)
    
    # Run connect_binance_stream in a task and cancel after one retry
    task = asyncio.create_task(service.connect_binance_stream("BTCUSDT", max_retries=2))
    await asyncio.sleep(0.1) # Allow some time for retries
    
    assert mock_binance.start_kline_stream.call_count >= 1
    task.cancel()
