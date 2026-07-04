import pytest

from aqrl.portfolio import (
    PortfolioConstraintError,
    PortfolioConstraints,
    SimpleRebalancer,
    normalize_weights,
)


def test_normalize_weights_and_constraints_validate_exposure() -> None:
    weights = normalize_weights({"AAPL": 2.0, "MSFT": 1.0})
    constraints = PortfolioConstraints(max_weight=0.6)

    assert weights["AAPL"] == pytest.approx(2.0 / 3.0)
    assert weights["MSFT"] == pytest.approx(1.0 / 3.0)
    assert constraints.validate(weights)[0].check == "max_weight"

    with pytest.raises(PortfolioConstraintError):
        constraints.assert_valid(weights)


def test_simple_rebalancer_generates_trades_and_turnover() -> None:
    plan = SimpleRebalancer().rebalance(
        {"AAPL": 0.5, "MSFT": 0.5},
        {"AAPL": 3.0, "MSFT": 1.0},
    )

    assert plan.target_weights["AAPL"] == pytest.approx(0.75)
    assert plan.target_weights["MSFT"] == pytest.approx(0.25)
    assert plan.trades["AAPL"] == pytest.approx(0.25)
    assert plan.trades["MSFT"] == pytest.approx(-0.25)
    assert plan.turnover == pytest.approx(0.5)
    assert plan.traded_assets == ("AAPL", "MSFT")


def test_simple_rebalancer_handles_empty_current_and_trade_tolerance() -> None:
    opening_plan = SimpleRebalancer().rebalance(None, {"AAPL": 0.6, "MSFT": 0.4})

    assert opening_plan.turnover == pytest.approx(1.0)
    assert opening_plan.trades == {"AAPL": 0.6, "MSFT": 0.4}

    tolerance_plan = SimpleRebalancer().rebalance(
        {"AAPL": 0.50001, "MSFT": 0.49999},
        {"AAPL": 0.5, "MSFT": 0.5},
        tolerance=0.001,
    )

    assert tolerance_plan.trades == {}
    assert tolerance_plan.turnover == 0.0


def test_portfolio_helpers_reject_empty_inputs() -> None:
    with pytest.raises(ValueError):
        normalize_weights({})

    with pytest.raises(ValueError):
        SimpleRebalancer().rebalance({}, {})
