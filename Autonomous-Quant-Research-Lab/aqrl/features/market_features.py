"""Market feature engineering primitives for AQRL."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from aqrl.core.utils import normalize_name
from aqrl.risk import TRADING_DAYS_PER_YEAR


@dataclass(frozen=True, slots=True)
class FeatureConfig:
    """Configuration for deterministic market feature generation."""

    price_column: str = "close"
    return_window: int = 1
    volatility_window: int = 5
    momentum_window: int = 5
    drawdown_window: int = 20
    periods_per_year: int = TRADING_DAYS_PER_YEAR

    def __post_init__(self) -> None:
        object.__setattr__(self, "price_column", normalize_name(self.price_column, "price_column"))
        for field_name in (
            "return_window",
            "volatility_window",
            "momentum_window",
            "drawdown_window",
            "periods_per_year",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, int):
                raise TypeError(f"{field_name} must be an integer.")
            if value <= 0:
                raise ValueError(f"{field_name} must be positive.")


def build_market_features(
    market_data: pd.DataFrame,
    *,
    config: FeatureConfig | None = None,
) -> pd.DataFrame:
    """Build deterministic rolling market features from a price frame."""
    active_config = FeatureConfig() if config is None else config
    prices = _price_series(market_data, active_config.price_column)
    simple_return = prices.pct_change().fillna(0.0)
    log_return = pd.Series(
        np.log(prices / prices.shift(1)),
        index=prices.index,
        name="log_return",
    ).fillna(0.0)
    rolling_return = prices.pct_change(active_config.return_window).fillna(0.0)
    rolling_volatility = (
        simple_return.rolling(active_config.volatility_window, min_periods=1).std(ddof=0)
        * np.sqrt(active_config.periods_per_year)
    ).fillna(0.0)
    momentum = (prices / prices.shift(active_config.momentum_window) - 1.0).fillna(0.0)
    rolling_peak = prices.rolling(active_config.drawdown_window, min_periods=1).max()
    rolling_drawdown = (prices / rolling_peak - 1.0).fillna(0.0)

    return pd.DataFrame(
        {
            "price": prices,
            "simple_return": simple_return,
            "log_return": log_return,
            "rolling_return": rolling_return,
            "rolling_volatility": rolling_volatility,
            "momentum": momentum,
            "rolling_drawdown": rolling_drawdown,
        },
        index=market_data.index.copy(),
    )


def _price_series(market_data: pd.DataFrame, price_column: str) -> pd.Series:
    """Return a validated positive price series."""
    if not isinstance(market_data, pd.DataFrame):
        raise TypeError("market_data must be a pandas DataFrame.")
    if market_data.empty:
        raise ValueError("market_data must contain at least one row.")
    if price_column not in market_data.columns:
        raise ValueError(f"price column missing from market data: {price_column}")
    prices = pd.to_numeric(market_data[price_column], errors="coerce")
    if prices.isna().any():
        raise ValueError(f"price column contains missing or non-numeric values: {price_column}")
    if (prices <= 0.0).any():
        raise ValueError(f"price column contains non-positive values: {price_column}")
    return prices.astype(float).rename(price_column)


__all__ = ["FeatureConfig", "build_market_features"]
