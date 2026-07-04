import pandas as pd
import pytest

from aqrl.research.backtest import BacktestConfig, BacktestEngine, BacktestResult
from aqrl.research.strategies import BuyAndHoldStrategy


def test_backtest_engine_returns_equity_positions_trades_and_summary() -> None:
    market_data = _market_data([100.0, 110.0, 121.0])
    signals = BuyAndHoldStrategy().generate_signals(market_data)

    result = BacktestEngine().run(
        market_data,
        signals,
        initial_capital=1_000.0,
    )

    assert isinstance(result, BacktestResult)
    assert result.equity_curve["equity"].tolist() == pytest.approx([1_000.0, 1_100.0, 1_210.0])
    assert result.positions["target_position"].tolist() == [1.0, 1.0, 1.0]
    assert len(result.trades) == 1
    assert result.summary["final_equity"] == pytest.approx(1_210.0)
    assert result.summary["total_return"] == pytest.approx(0.21)
    assert "value_at_risk" in result.summary
    assert "conditional_value_at_risk" in result.summary
    assert "sortino" in result.summary


def test_backtest_engine_applies_transaction_costs() -> None:
    market_data = _market_data([100.0, 102.0, 104.0, 106.0])
    signals = pd.DataFrame(
        {"signal": [1.0, 0.0, 1.0, 0.0]},
        index=market_data.index.copy(),
    )
    engine = BacktestEngine()

    without_costs = engine.run(market_data, signals, initial_capital=1_000.0)
    with_costs = engine.run(
        market_data,
        signals,
        initial_capital=1_000.0,
        transaction_cost=0.01,
    )

    assert with_costs.summary["final_equity"] < without_costs.summary["final_equity"]
    assert with_costs.summary["transaction_cost_paid"] > 0
    assert with_costs.summary["trade_count"] == 4.0


def test_backtest_config_validates_inputs() -> None:
    with pytest.raises(ValueError):
        BacktestConfig(initial_capital=0)

    with pytest.raises(ValueError):
        BacktestConfig(transaction_cost=-0.01)


def _market_data(close_values: list[float]) -> pd.DataFrame:
    """Build a deterministic market-data frame."""
    return pd.DataFrame(
        {"close": close_values},
        index=pd.date_range("2024-01-01", periods=len(close_values), tz="UTC"),
    )
