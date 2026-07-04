"""Offline AQRL risk and portfolio rebalance example."""

from __future__ import annotations

import pandas as pd

from aqrl.portfolio import PortfolioConstraints, SimpleRebalancer
from aqrl.risk import calculate_returns, summarize_returns


def main() -> None:
    """Run deterministic risk analytics and a rebalance plan."""
    equity_curve = pd.Series([100_000.0, 101_200.0, 100_500.0, 103_400.0, 104_100.0])
    returns = calculate_returns(equity_curve)
    risk = summarize_returns(returns, equity_curve=equity_curve.iloc[1:])
    plan = SimpleRebalancer().rebalance(
        current_weights={"AAPL": 0.5, "MSFT": 0.5},
        desired_weights={"AAPL": 0.7, "MSFT": 0.3},
        constraints=PortfolioConstraints(max_weight=0.8),
    )

    print("cumulative_return:", round(risk.cumulative_return, 6))
    print("max_drawdown:", round(risk.max_drawdown, 6))
    print("var:", round(risk.value_at_risk, 6))
    print("target_weights:", dict(plan.target_weights))
    print("trades:", dict(plan.trades))
    print("turnover:", round(plan.turnover, 6))


if __name__ == "__main__":
    main()
