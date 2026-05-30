import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from backend.services.data_ingestion import DataIngestionService
from backend.database import Candle

@pytest.fixture
def mock_zerodha():
    adapter = AsyncMock()
    return adapter

@pytest.fixture
def mock_redis():
    client = MagicMock()
    # Mock redis methods as async since we use redis.asyncio
    client.delete = AsyncMock()
    client.lpush = AsyncMock()
    client.ltrim = AsyncMock()
    return client

@pytest.mark.asyncio
async def test_fetch_and_store_candles(mock_zerodha, mock_redis):
    # Setup mock data
    symbol = "RELIANCE"
    mock_candles = [
        Candle(
            symbol=symbol,
            market="indian_equity",
            timeframe="1m",
            open_time=datetime.utcnow() - timedelta(minutes=i),
            close_time=datetime.utcnow() - timedelta(minutes=i-1),
            open=100.0 + i,
            high=105.0 + i,
            low=95.0 + i,
            close=101.0 + i,
            volume=1000 + i
        ) for i in range(5)
    ]
    mock_zerodha.get_candles.return_value = mock_candles

    service = DataIngestionService(zerodha_adapter=mock_zerodha, redis_client=mock_redis)
    await service.initialize_data(mock_zerodha, symbol)

    # Verify Zerodha was called
    mock_zerodha.get_candles.assert_called_with(symbol, "1m", limit=100)

    # Verify Redis was called
    assert mock_redis.delete.called
    assert mock_redis.lpush.call_count == 5
    assert mock_redis.ltrim.called

@pytest.mark.asyncio
async def test_error_handling_api_failure(mock_zerodha, mock_redis):
    symbol = "RELIANCE"
    mock_zerodha.get_candles.side_effect = Exception("API Down")

    service = DataIngestionService(zerodha_adapter=mock_zerodha, redis_client=mock_redis)
    # Should not raise exception
    await service.initialize_data(mock_zerodha, symbol)
    
    # Verify Redis was not updated (except maybe delete, but let's check lpush)
    assert mock_redis.lpush.call_count == 0

@pytest.mark.asyncio
async def test_fifo_limit(mock_zerodha, mock_redis):
    symbol = "RELIANCE"
    mock_candles = [
        Candle(
            symbol=symbol,
            market="indian_equity",
            timeframe="1m",
            open_time=datetime.utcnow(),
            close_time=datetime.utcnow(),
            open=100.0, high=105.0, low=95.0, close=101.0, volume=1000
        )
    ]
    mock_zerodha.get_candles.return_value = mock_candles

    service = DataIngestionService(zerodha_adapter=mock_zerodha, redis_client=mock_redis)
    await service.initialize_data(mock_zerodha, symbol)
    
    # Verify ltrim called to keep 100
    mock_redis.ltrim.assert_called_with(f"market_data:1m:{symbol}", 0, 99)
