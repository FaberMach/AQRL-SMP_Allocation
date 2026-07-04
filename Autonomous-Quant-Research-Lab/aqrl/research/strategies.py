"""Baseline strategy contracts and implementations for AQRL research."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Self

import pandas as pd

from aqrl.core.utils import normalize_name

SIGNAL_COLUMN = "signal"


class Strategy(Protocol):
    """Strategy contract for fitting and generating aligned trading signals."""

    name: str

    def fit(self, market_data: pd.DataFrame) -> Self:
        """Fit strategy state from market data."""

    def generate_signals(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """Generate a signal frame aligned to ``market_data``."""


@dataclass(frozen=True, slots=True)
class BuyAndHoldStrategy:
    """Baseline strategy that stays fully invested."""

    name: str = "buy_and_hold"

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", normalize_name(self.name, "name"))

    def fit(self, market_data: pd.DataFrame) -> Self:
        """Buy-and-hold has no trainable state."""
        _validate_market_data(market_data)
        return self

    def generate_signals(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """Return a long-only signal aligned to the input index."""
        _validate_market_data(market_data)
        return pd.DataFrame({SIGNAL_COLUMN: 1.0}, index=market_data.index.copy())


@dataclass(frozen=True, slots=True)
class MovingAverageCrossoverStrategy:
    """Long-only moving-average crossover baseline strategy."""

    short_window: int = 20
    long_window: int = 50
    price_column: str = "close"
    name: str = "moving_average_crossover"

    def __post_init__(self) -> None:
        if not isinstance(self.short_window, int) or not isinstance(self.long_window, int):
            raise TypeError("window values must be integers.")
        if self.short_window <= 0 or self.long_window <= 0:
            raise ValueError("window values must be positive.")
        if self.short_window >= self.long_window:
            raise ValueError("short_window must be smaller than long_window.")
        object.__setattr__(self, "price_column", normalize_name(self.price_column, "price_column"))
        object.__setattr__(self, "name", normalize_name(self.name, "name"))

    def fit(self, market_data: pd.DataFrame) -> Self:
        """Moving-average crossover has no trainable state."""
        self._price_series(market_data)
        return self

    def generate_signals(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """Generate long/flat signals from moving-average crossovers."""
        prices = self._price_series(market_data)
        short_average = prices.rolling(self.short_window, min_periods=self.short_window).mean()
        long_average = prices.rolling(self.long_window, min_periods=self.long_window).mean()
        signal = (short_average > long_average).astype(float).fillna(0.0)

        return pd.DataFrame(
            {
                SIGNAL_COLUMN: signal,
                "short_average": short_average,
                "long_average": long_average,
            },
            index=market_data.index.copy(),
        )

    def _price_series(self, market_data: pd.DataFrame) -> pd.Series:
        """Return a validated numeric price series."""
        _validate_market_data(market_data)
        if self.price_column not in market_data.columns:
            raise ValueError(f"price column missing from market data: {self.price_column}")
        prices = pd.to_numeric(market_data[self.price_column], errors="coerce")
        if prices.isna().any():
            raise ValueError(f"price column contains non-numeric values: {self.price_column}")
        return prices


def _validate_market_data(market_data: pd.DataFrame) -> None:
    """Validate a strategy market-data frame."""
    if not isinstance(market_data, pd.DataFrame):
        raise TypeError("market_data must be a pandas DataFrame.")
    if market_data.empty:
        raise ValueError("market_data must contain at least one row.")


__all__ = [
    "SIGNAL_COLUMN",
    "BuyAndHoldStrategy",
    "MovingAverageCrossoverStrategy",
    "Strategy",
]
