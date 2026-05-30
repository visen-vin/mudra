# backend/engine/position_monitor.py
from backend.database import Position, SessionLocal
from backend.engine.pnl_calculator import PnLCalculator
from typing import Callable, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PositionMonitor:
    """Monitors open positions for SL/TP triggers"""

    def __init__(self, on_exit_callback: Optional[Callable] = None):
        self.on_exit_callback = on_exit_callback  # called when position closes

    def check_exit(self, position: Position, current_price: float) -> Optional[dict]:
        """
        Check if position should exit based on SL/TP.
        Returns exit_event if triggered, else None.
        """
        if position.status != "OPEN":
            return None

        exit_event = None

        # Check SL
        if position.side == "long" and current_price <= position.sl:
            exit_event = {
                "position_id": position.id,
                "exit_price": current_price,
                "exit_reason": "SL",
                "status": "CLOSED"
            }
        elif position.side == "short" and current_price >= position.sl:
            exit_event = {
                "position_id": position.id,
                "exit_price": current_price,
                "exit_reason": "SL",
                "status": "CLOSED"
            }

        # Check TP
        if position.side == "long" and current_price >= position.tp:
            exit_event = {
                "position_id": position.id,
                "exit_price": current_price,
                "exit_reason": "TP",
                "status": "CLOSED"
            }
        elif position.side == "short" and current_price <= position.tp:
            exit_event = {
                "position_id": position.id,
                "exit_price": current_price,
                "exit_reason": "TP",
                "status": "CLOSED"
            }

        return exit_event

    async def execute_exit(self, position: Position, exit_event: dict):
        """Execute exit: update position in DB, calculate PnL"""
        db = SessionLocal()
        try:
            position.status = "CLOSED"
            position.closed_at = datetime.utcnow()
            position.exit_price = exit_event["exit_price"]
            position.exit_reason = exit_event["exit_reason"]

            pnl, pnl_pct = PnLCalculator.calculate(
                position.side,
                position.entry_price,
                position.exit_price,
                position.qty
            )
            position.pnl = pnl

            db.commit()
            logger.info(f"Position {position.id} closed: {exit_event['exit_reason']} @ {exit_event['exit_price']}, PnL: {pnl}")

            if self.on_exit_callback:
                await self.on_exit_callback(position)

        finally:
            db.close()
