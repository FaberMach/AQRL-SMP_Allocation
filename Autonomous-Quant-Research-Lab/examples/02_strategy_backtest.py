"""Offline AQRL strategy and backtest example."""

from __future__ import annotations

import pandas as pd

from aqrl.research import BacktestEngine, MovingAverageCrossoverStrategy


def main() -> None:
    """Run a deterministic moving-average strategy backtest."""
    market_data = pd.DataFrame(
        {"close": [100.0, 101.0, 102.0, 99.0, 103.0, 105.0, 104.0, 108.0, 110.0]},
        index=pd.date_range("2026-01-01", periods=9, tz="UTC", name="timestamp"),
    )
    strategy = MovingAverageCrossoverStrategy(short_window=2, long_window=4)
    signals = strategy.fit(market_data).generate_signals(market_data)
    result = BacktestEngine().run(
        market_data,
        signals,
        initial_capital=100_000,
        transaction_cost=0.001,
    )

    print("strategy:", strategy.name)
    print("final_equity:", round(result.summary["final_equity"], 2))
    print("total_return:", round(result.summary["total_return"], 6))
    print("sharpe:", round(result.summary["sharpe"], 6))
    print("trades:", len(result.trades))


if __name__ == "__main__":
    main()
