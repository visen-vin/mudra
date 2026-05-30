# tests/test_zerodha_feed.py
import pytest
from backend.feeds.zerodha import ZerodhaAdapter

@pytest.mark.asyncio
async def test_zerodha_requires_token():
    """Test that Zerodha requires OAuth token"""
    adapter = ZerodhaAdapter()
    
    with pytest.raises(ValueError, match="requires access_token"):
        await adapter.connect()

@pytest.mark.asyncio
async def test_zerodha_get_price_no_token():
    """Test get_price returns None without token"""
    adapter = ZerodhaAdapter()
    price = await adapter.get_price("SBIN")
    
    assert price is None

@pytest.mark.asyncio
async def test_zerodha_place_order_not_implemented():
    """Test place_order raises NotImplementedError"""
    adapter = ZerodhaAdapter(access_token="mock_token")
    
    from backend.schemas import Order
    order = Order(symbol="SBIN", side="long", qty=1.0, price=500)
    
    with pytest.raises(NotImplementedError):
        await adapter.place_order(order)

def test_zerodha_connect_with_token():
    """Test Zerodha adapter initializes with token"""
    adapter = ZerodhaAdapter(access_token="test_token_xyz")
    assert adapter.access_token == "test_token_xyz"
