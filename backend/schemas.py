# backend/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PositionCreate(BaseModel):
    symbol: str
    market: str  # "crypto", "indian_equity"
    side: str  # "long", "short"
    qty: float
    entry_price: float
    sl: float
    tp: float
    mode: str = "paper"  # "paper", "live"

class PositionRead(BaseModel):
    id: str
    signal_id: Optional[str]
    market: str
    symbol: str
    side: str
    qty: float
    entry_price: float
    sl: float
    tp: float
    status: str
    mode: str
    opened_at: datetime
    closed_at: Optional[datetime]
    exit_price: Optional[float]
    exit_reason: Optional[str]
    pnl: Optional[float]

    class Config:
        from_attributes = True

class SignalCreate(BaseModel):
    strategy: str
    symbol: str
    side: str
    confidence: float
    candle_close_time: datetime

class SignalRead(BaseModel):
    signal_id: str
    strategy: str
    symbol: str
    side: str
    confidence: float
    candle_close_time: datetime
    emitted_at: datetime

    class Config:
        from_attributes = True
