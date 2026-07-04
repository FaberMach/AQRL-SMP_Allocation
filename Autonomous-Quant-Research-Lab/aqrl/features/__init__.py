"""Feature engineering and regime primitives for AQRL."""

from .market_features import FeatureConfig, build_market_features
from .regimes import (
    RegimeConfig,
    TrendRegime,
    VolatilityRegime,
    classify_market_regimes,
)

__all__ = [
    "FeatureConfig",
    "RegimeConfig",
    "TrendRegime",
    "VolatilityRegime",
    "build_market_features",
    "classify_market_regimes",
]
