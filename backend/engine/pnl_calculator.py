# backend/engine/pnl_calculator.py
from typing import Tuple


class PnLCalculator:
    @staticmethod
    def calculate(
        side: str,
        entry_price: float,
        exit_price: float,
        qty: float
    ) -> Tuple[float, float]:
        """
        Calculate PnL and percentage return.
        Returns: (pnl_in_currency, pnl_percentage)
        """
        if side == "long":
            pnl = (exit_price - entry_price) * qty
        else:  # short
            pnl = (entry_price - exit_price) * qty

        pnl_pct = (pnl / (entry_price * qty)) * 100

        return pnl, pnl_pct
