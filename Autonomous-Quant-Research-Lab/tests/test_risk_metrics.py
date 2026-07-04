import math

import pandas as pd
import pytest

from aqrl.risk import (
    annualized_return,
    annualized_volatility,
    calculate_returns,
    conditional_value_at_risk,
    cumulative_return,
    max_drawdown,
    sharpe_ratio,
    sortino_ratio,
    summarize_returns,
    value_at_risk,
)


def test_risk_metrics_are_deterministic_for_known_returns() -> None:
    prices = pd.Series([100.0, 110.0, 99.0])
    returns = calculate_returns(prices)

    assert returns.tolist() == pytest.approx([0.1, -0.1])
    assert calculate_returns(prices, method="log").tolist() == pytest.approx(
        [math.log(1.1), math.log(0.9)]
    )
    assert cumulative_return(returns) == pytest.approx(-0.01)
    assert annualized_return(returns, periods_per_year=2) == pytest.approx(-0.01)
    assert annualized_volatility(returns, periods_per_year=2) == pytest.approx(math.sqrt(2) * 0.1)
    assert max_drawdown(prices) == pytest.approx(-0.1)
    assert value_at_risk(returns, confidence=0.75) == pytest.approx(-0.05)
    assert conditional_value_at_risk(returns, confidence=0.75) == pytest.approx(-0.1)
    assert sharpe_ratio(returns, periods_per_year=2) == pytest.approx(0.0)
    assert sortino_ratio(returns, periods_per_year=2) == pytest.approx(0.0)


def test_summarize_returns_emits_canonical_metrics() -> None:
    returns = pd.Series([0.1, -0.1])
    equity = pd.Series([110.0, 99.0])

    summary = summarize_returns(
        returns,
        equity_curve=equity,
        confidence=0.75,
        periods_per_year=2,
    )

    assert summary.observation_count == 2
    assert summary.cumulative_return == pytest.approx(-0.01)
    assert summary.max_drawdown == pytest.approx(-0.1)
    assert summary.value_at_risk == pytest.approx(-0.05)
    assert summary.conditional_value_at_risk == pytest.approx(-0.1)
    assert summary.to_dict()["observation_count"] == 2.0


def test_risk_metrics_validate_inputs() -> None:
    with pytest.raises(ValueError):
        calculate_returns(pd.Series([100.0, 0.0]))

    with pytest.raises(ValueError):
        value_at_risk(pd.Series([0.01]), confidence=1.0)

    with pytest.raises(ValueError):
        cumulative_return(pd.Series([-1.0]))
