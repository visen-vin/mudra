# backend/engine/trade_engine.py
from backend.database import Position, SessionLocal
from backend.engine.position_monitor import PositionMonitor
from backend.engine.pnl_calculator import PnLCalculator
from typing import Optional, Dict
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


class TradeEngine:
    """Manages trade entry and position lifecycle"""

    def __init__(self):
        self.monitor = PositionMonitor()
        self.open_positions: Dict[str, Position] = {}

    def open_position(
        self,
        symbol: str,
        market: str,
        side: str,
        qty: float,
        entry_price: float,
        sl: float,
        tp: float,
        mode: str = "paper",
        signal_id: Optional[str] = None
    ) -> Position:
        """Create and persist a new position"""
        db = SessionLocal()
        try:
            position = Position(
                id=str(uuid.uuid4()),
                signal_id=signal_id,
                symbol=symbol,
                market=market,
                side=side,
                qty=qty,
                entry_price=entry_price,
                sl=sl,
                tp=tp,
                status="OPEN",
                mode=mode,
                opened_at=datetime.utcnow()
            )

            db.add(position)
            db.commit()
            db.refresh(position)

            self.open_positions[position.id] = position
            logger.info(f"Position opened: {position.id} {symbol} {side} @ {entry_price}")

            return position
        finally:
            db.close()

    def get_position(self, position_id: str) -> Optional[Position]:
        """Get position by ID"""
        db = SessionLocal()
        try:
            return db.query(Position).filter(Position.id == position_id).first()
        finally:
            db.close()

    def get_open_positions(self) -> list[Position]:
        """Get all open positions"""
        db = SessionLocal()
        try:
            return db.query(Position).filter(Position.status == "OPEN").all()
        finally:
            db.close()

    def close_position_manual(self, position_id: str, exit_price: float) -> Position:
        """Manually close a position"""
        db = SessionLocal()
        try:
            position = db.query(Position).filter(Position.id == position_id).first()
            if not position:
                raise ValueError(f"Position {position_id} not found")

            position.status = "CLOSED"
            position.closed_at = datetime.utcnow()
            position.exit_price = exit_price
            position.exit_reason = "manual"

            # Calculate PnL
            pnl, pnl_pct = PnLCalculator.calculate(
                position.side,
                position.entry_price,
                position.exit_price,
                position.qty
            )
            position.pnl = pnl

            db.commit()
            db.refresh(position)

            logger.info(f"Position {position_id} closed manually, PnL: {pnl}")

            return position
        finally:
            db.close()
