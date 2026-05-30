# backend/api/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db, Position, SessionLocal
from backend.schemas import PositionCreate, PositionRead, SignalRead, SignalCreate
from backend.engine.trade_engine import TradeEngine
from backend.feeds.binance import BinanceAdapter
from backend.services.signal_service import SignalService
from typing import List

router = APIRouter(prefix="/api", tags=["trading"])
engine = TradeEngine()

# Initialize and register adapters
binance = BinanceAdapter()
engine.register_adapter("crypto", binance)

@router.get("/signals", response_model=List[SignalRead])
def get_signals(strategy: str = None, limit: int = 100, offset: int = 0):
    """Get recent trading signals"""
    if strategy:
        signals = SignalService.get_signals_by_strategy(strategy, limit)
    else:
        signals = SignalService.get_signals(limit, offset)
    return signals

@router.post("/signals", response_model=SignalRead)
def create_signal(signal: SignalCreate):
    """Create new signal (from strategy)"""
    new_signal = SignalService.create_signal(
        strategy=signal.strategy,
        symbol=signal.symbol,
        side=signal.side,
        confidence=signal.confidence,
        candle_close_time=signal.candle_close_time
    )
    return new_signal

@router.get("/positions", response_model=List[PositionRead])
def get_positions(db: Session = Depends(get_db)):
    """Get all open positions"""
    return db.query(Position).filter(Position.status == "OPEN").all()

@router.get("/history", response_model=List[PositionRead])
def get_history(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    """Get closed trades (history)"""
    return db.query(Position).filter(Position.status == "CLOSED") \
        .order_by(Position.closed_at.desc()) \
        .offset(offset).limit(limit).all()

@router.post("/place-order", response_model=PositionRead)
async def place_order(order: PositionCreate, db: Session = Depends(get_db)):
    """Place manual trade"""
    try:
        position = await engine.open_position(
            symbol=order.symbol,
            market=order.market,
            side=order.side,
            qty=order.qty,
            entry_price=order.entry_price,
            sl=order.sl,
            tp=order.tp,
            mode=order.mode
        )
        return position
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/close-position/{position_id}", response_model=PositionRead)
async def close_position(position_id: str, exit_price: float, db: Session = Depends(get_db)):
    """Manually close a position"""
    position = await engine.close_position_manual(position_id, exit_price)
    return position

@router.get("/prices")
def get_prices(symbols: str):
    """Get current prices (mock for now)"""
    # Will be connected to feed service in Phase 2
    symbols_list = symbols.split(",")
    return {
        symbol: 0  # TODO: fetch from feed service
        for symbol in symbols_list
    }

@router.get("/settings")
def get_settings():
    """Get trading settings (paper/live mode)"""
    from backend.config import Config
    return {"mode": Config.DEFAULT_MODE}

@router.post("/settings")
def update_settings(mode: str):
    """Toggle paper/live mode"""
    # TODO: Persist settings to DB or config
    return {"mode": mode, "status": "updated"}
