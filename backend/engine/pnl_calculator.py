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

        Raises ValueError if entry_price or qty are not positive.
        """
        if entry_price <= 0 or qty <= 0:
            raise ValueError(
                f"entry_price and qty must be > 0, got entry_price={entry_price}, qty={qty}"
            )

        if side == "long":
            pnl = (exit_price - entry_price) * qty
        else:  # short
            pnl = (entry_price - exit_price) * qty

        pnl_pct = (pnl / (entry_price * qty)) * 100

        return pnl, pnl_pct
