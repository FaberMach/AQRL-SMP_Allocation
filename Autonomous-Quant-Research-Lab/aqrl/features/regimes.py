"""Simple market regime classification for AQRL."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd

from aqrl.core.utils import normalize_name

TrendRegime = Literal["bull", "bear", "neutral"]
VolatilityRegime = Literal["high_volatility", "low_volatility"]


@dataclass(frozen=True, slots=True)
class RegimeConfig:
    """Configuration for simple threshold-based regime classification."""

    momentum_column: str = "momentum"
    volatility_column: str = "rolling_volatility"
    momentum_threshold: float = 0.0
    volatility_threshold: float | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "momentum_column",
            normalize_name(self.momentum_column, "momentum_column"),
        )
        object.__setattr__(
            self,
            "volatility_column",
            normalize_name(self.volatility_column, "volatility_column"),
        )
        if not isinstance(self.momentum_threshold, int | float):
            raise TypeError("momentum_threshold must be numeric.")
        if self.momentum_threshold < 0:
            raise ValueError("momentum_threshold must be non-negative.")
        object.__setattr__(self, "momentum_threshold", float(self.momentum_threshold))
        if self.volatility_threshold is not None:
            if not isinstance(self.volatility_threshold, int | float):
                raise TypeError("volatility_threshold must be numeric when present.")
            if self.volatility_threshold < 0:
                raise ValueError("volatility_threshold must be non-negative.")
            object.__setattr__(self, "volatility_threshold", float(self.volatility_threshold))


def classify_market_regimes(
    features: pd.DataFrame,
    *,
    config: RegimeConfig | None = None,
) -> pd.DataFrame:
    """Classify simple trend and volatility regimes from feature columns."""
    active_config = RegimeConfig() if config is None else config
    momentum = _feature_series(features, active_config.momentum_column)
    volatility = _feature_series(features, active_config.volatility_column)
    volatility_threshold = (
        float(volatility.median())
        if active_config.volatility_threshold is None
        else active_config.volatility_threshold
    )

    trend_regime = momentum.map(
        lambda value: _trend_regime(value, active_config.momentum_threshold)
    )
    volatility_regime = volatility.map(
        lambda value: _volatility_regime(value, volatility_threshold)
    )
    combined_regime = trend_regime.astype(str) + "/" + volatility_regime.astype(str)

    return pd.DataFrame(
        {
            "trend_regime": trend_regime,
            "volatility_regime": volatility_regime,
            "regime": combined_regime,
        },
        index=features.index.copy(),
    )


def _trend_regime(value: float, threshold: float) -> TrendRegime:
    """Classify a momentum value into bull, bear, or neutral."""
    if value > threshold:
        return "bull"
    if value < -threshold:
        return "bear"
    return "neutral"


def _volatility_regime(value: float, threshold: float) -> VolatilityRegime:
    """Classify a volatility value into high/low volatility."""
    if value > threshold:
        return "high_volatility"
    return "low_volatility"


def _feature_series(features: pd.DataFrame, column: str) -> pd.Series:
    """Return a validated numeric feature series."""
    if not isinstance(features, pd.DataFrame):
        raise TypeError("features must be a pandas DataFrame.")
    if features.empty:
        raise ValueError("features must contain at least one row.")
    if column not in features.columns:
        raise ValueError(f"feature column missing: {column}")
    series = pd.to_numeric(features[column], errors="coerce")
    if series.isna().any():
        raise ValueError(f"feature column contains missing or non-numeric values: {column}")
    return series.astype(float)


__all__ = [
    "RegimeConfig",
    "TrendRegime",
    "VolatilityRegime",
    "classify_market_regimes",
]
