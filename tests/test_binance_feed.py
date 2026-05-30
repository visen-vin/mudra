# tests/test_binance_feed.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.feeds.binance import BinanceAdapter
from backend.schemas import Order, OrderResponse
from backend.database import Candle
from datetime import datetime

@pytest.mark.asyncio
async def test_binance_get_price_from_cache():
    """Test retrieving price from cache"""
    adapter = BinanceAdapter()
    adapter.session = MagicMock()  # session must be set; cache hit avoids any actual call
    adapter.prices["BTCUSDT"] = 50000.0

    price = await adapter.get_price("BTCUSDT")
    assert price == 50000.0

@pytest.mark.asyncio
async def test_binance_get_candles():
    """Test fetching historical candles"""
    adapter = BinanceAdapter()
    adapter.session = MagicMock()

    # Mock response data (Binance klines format)
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=[
        [1000, "50000", "51000", "49000", "50500", 0, 1100000, 100, 0, 0, 0, 0]
    ])

    ctx = AsyncMock()
    ctx.__aenter__ = AsyncMock(return_value=mock_response)
    ctx.__aexit__ = AsyncMock(return_value=False)
    adapter.session.get.return_value = ctx

    candles = await adapter.get_candles("BTCUSDT", "15m", 1)

    assert len(candles) == 1
    assert candles[0].symbol == "BTCUSDT"
    assert candles[0].close == 50500.0

@pytest.mark.asyncio
async def test_binance_on_price_update():
    """Test price update callback registration"""
    adapter = BinanceAdapter()

    callback = AsyncMock()
    await adapter.on_price_update(callback)

    # Callback should be registered (implementation stores it for later invocation)
    # This test verifies the signature accepts a callback function

@pytest.mark.asyncio
async def test_binance_connect_disconnect():
    """Test connection lifecycle"""
    adapter = BinanceAdapter()

    # Mock aiohttp.ClientSession
    with patch('aiohttp.ClientSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value = mock_session

        await adapter.connect()
        assert adapter.session is not None

        await adapter.disconnect()
        mock_session.close.assert_called_once()

@pytest.mark.asyncio
async def test_binance_get_candles_http_error():
    """Test error handling when API returns error status"""
    adapter = BinanceAdapter()
    adapter.session = MagicMock()

    mock_response = AsyncMock()
    mock_response.status = 400  # Bad request

    ctx = AsyncMock()
    ctx.__aenter__ = AsyncMock(return_value=mock_response)
    ctx.__aexit__ = AsyncMock(return_value=False)
    adapter.session.get.return_value = ctx

    candles = await adapter.get_candles("INVALID", "15m", 1)

    assert candles == []  # Returns empty list on error

@pytest.mark.asyncio
async def test_binance_get_candles_parse_error():
    """Test error handling when candle data is malformed"""
    adapter = BinanceAdapter()
    adapter.session = MagicMock()

    # Malformed candle (missing fields)
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=[
        [1000, "50000"]  # Only 2 fields instead of 12
    ])

    ctx = AsyncMock()
    ctx.__aenter__ = AsyncMock(return_value=mock_response)
    ctx.__aexit__ = AsyncMock(return_value=False)
    adapter.session.get.return_value = ctx

    candles = await adapter.get_candles("BTCUSDT", "15m", 1)

    assert candles == []  # Returns empty list on parse error

@pytest.mark.asyncio
async def test_binance_get_price_rest_fallback():
    """Test that get_price falls back to REST when not in cache"""
    adapter = BinanceAdapter()
    adapter.session = MagicMock()

    # Mock successful REST response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"price": "52000"})

    ctx = AsyncMock()
    ctx.__aenter__ = AsyncMock(return_value=mock_response)
    ctx.__aexit__ = AsyncMock(return_value=False)
    adapter.session.get.return_value = ctx

    price = await adapter.get_price("BTCUSDT")

    assert price == 52000.0
    assert adapter.prices["BTCUSDT"] == 52000.0  # cached

@pytest.mark.asyncio
async def test_binance_get_price_before_connect_returns_none():
    """Test that get_price returns None if connect() not called"""
    adapter = BinanceAdapter()  # session is None

    price = await adapter.get_price("BTCUSDT")

    assert price is None

@pytest.mark.asyncio
async def test_binance_get_candles_before_connect_returns_empty():
    """Test that get_candles returns empty list if connect() not called"""
    adapter = BinanceAdapter()  # session is None

    candles = await adapter.get_candles("BTCUSDT", "15m")

    assert candles == []
