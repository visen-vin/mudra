# tests/test_live_orders.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.feeds.binance import BinanceAdapter
from backend.engine.trade_engine import TradeEngine
from backend.schemas import Order, OrderResponse
import hmac
import hashlib
from urllib.parse import urlencode

@pytest.mark.asyncio
async def test_binance_place_order_signing():
    """Test that BinanceAdapter.place_order correctly signs requests"""
    adapter = BinanceAdapter()
    adapter.session = MagicMock()
    
    # Mock Config
    with patch("backend.feeds.binance.Config") as mock_config:
        mock_config.BINANCE_API_KEY = "test_key"
        mock_config.BINANCE_API_SECRET = "test_secret"
        
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"orderId": 12345, "status": "FILLED"})
        
        ctx = AsyncMock()
        ctx.__aenter__ = AsyncMock(return_value=mock_response)
        ctx.__aexit__ = AsyncMock(return_value=False)
        adapter.session.post.return_value = ctx
        
        order = Order(symbol="BTCUSDT", side="long", qty=1.0)
        resp = await adapter.place_order(order)
        
        assert resp.order_id == "12345"
        assert resp.status == "FILLED"
        
        # Check call arguments
        args, kwargs = adapter.session.post.call_args
        params = kwargs.get("params")
        headers = kwargs.get("headers")
        
        assert headers["X-MBX-APIKEY"] == "test_key"
        assert params["symbol"] == "BTCUSDT"
        assert params["side"] == "BUY"
        assert params["type"] == "MARKET"
        assert "signature" in params
        
        # Verify signature
        signature = params.pop("signature")
        query_string = urlencode(params)
        expected_signature = hmac.new(
            "test_secret".encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        assert signature == expected_signature

@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_db")
async def test_trade_engine_live_order_routing():
    """Test that TradeEngine routes live orders to the correct adapter"""
    engine = TradeEngine()
    mock_adapter = AsyncMock()
    mock_adapter.place_order.return_value = OrderResponse(order_id="live_123", status="NEW")
    
    engine.register_adapter("crypto", mock_adapter)
    
    position = await engine.open_position(
        symbol="BTCUSDT",
        market="crypto",
        side="long",
        qty=1.0,
        entry_price=50000,
        sl=49000,
        tp=51000,
        mode="live"
    )
    
    assert position.mode == "live"
    mock_adapter.place_order.assert_called_once()
    order_arg = mock_adapter.place_order.call_args[0][0]
    assert order_arg.symbol == "BTCUSDT"
    assert order_arg.qty == 1.0

@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_db")
async def test_trade_engine_live_order_failure():
    """Test that TradeEngine handles live order failures"""
    engine = TradeEngine()
    mock_adapter = AsyncMock()
    mock_adapter.place_order.return_value = OrderResponse(order_id="", status="FAILED: Insufficient balance")
    
    engine.register_adapter("crypto", mock_adapter)
    
    with pytest.raises(RuntimeError, match="Live order failed"):
        await engine.open_position(
            symbol="BTCUSDT",
            market="crypto",
            side="long",
            qty=1.0,
            entry_price=50000,
            sl=49000,
            tp=51000,
            mode="live"
        )
