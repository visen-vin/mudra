# tests/test_api_routes.py
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import init_db

client = TestClient(app)

def setup_function():
    init_db()

def test_get_positions():
    response = client.get("/api/positions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_place_order():
    response = client.post("/api/place-order", json={
        "symbol": "BTCUSDT",
        "market": "crypto",
        "side": "long",
        "qty": 1.0,
        "entry_price": 50000,
        "sl": 49000,
        "tp": 51000,
        "mode": "paper"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "BTCUSDT"
    assert data["status"] == "OPEN"

def test_get_history():
    response = client.get("/api/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_settings():
    response = client.get("/api/settings")
    assert response.status_code == 200
    assert "mode" in response.json()
