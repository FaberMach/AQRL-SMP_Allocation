import pandas as pd
import pandas.testing as pdt
import pytest

from aqrl.research.strategies import (
    SIGNAL_COLUMN,
    BuyAndHoldStrategy,
    MovingAverageCrossoverStrategy,
)


def test_buy_and_hold_strategy_generates_aligned_long_signal() -> None:
    market_data = _market_data([100.0, 101.0, 102.0])
    strategy = BuyAndHoldStrategy()

    fitted = strategy.fit(market_data)
    signals = fitted.generate_signals(market_data)

    assert signals.index.equals(market_data.index)
    assert signals[SIGNAL_COLUMN].tolist() == [1.0, 1.0, 1.0]


def test_moving_average_crossover_is_aligned_and_reproducible() -> None:
    market_data = _market_data([10.0, 11.0, 12.0, 9.0, 14.0])
    strategy = MovingAverageCrossoverStrategy(short_window=2, long_window=3)

    first = strategy.fit(market_data).generate_signals(market_data)
    second = strategy.generate_signals(market_data)

    assert first.index.equals(market_data.index)
    assert first[SIGNAL_COLUMN].tolist() == [0.0, 0.0, 1.0, 0.0, 0.0]
    pdt.assert_frame_equal(first, second)


def test_moving_average_crossover_validates_windows() -> None:
    with pytest.raises(ValueError):
        MovingAverageCrossoverStrategy(short_window=5, long_window=5)


def _market_data(close_values: list[float]) -> pd.DataFrame:
    """Build a deterministic close-price frame."""
    return pd.DataFrame(
        {"close": close_values},
        index=pd.date_range("2024-01-01", periods=len(close_values), tz="UTC"),
    )
