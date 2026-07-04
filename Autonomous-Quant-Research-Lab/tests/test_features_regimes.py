import pandas as pd
import pytest

from aqrl.features import (
    FeatureConfig,
    RegimeConfig,
    build_market_features,
    classify_market_regimes,
)


def test_build_market_features_emits_deterministic_columns() -> None:
    market_data = _market_data([100.0, 110.0, 99.0, 108.9])

    features = build_market_features(
        market_data,
        config=FeatureConfig(return_window=2, volatility_window=2, momentum_window=2),
    )

    assert list(features.columns) == [
        "price",
        "simple_return",
        "log_return",
        "rolling_return",
        "rolling_volatility",
        "momentum",
        "rolling_drawdown",
    ]
    assert features["simple_return"].tolist() == pytest.approx([0.0, 0.1, -0.1, 0.1])
    assert features["rolling_return"].tolist() == pytest.approx([0.0, 0.0, -0.01, -0.01])
    assert features["momentum"].tolist() == pytest.approx([0.0, 0.0, -0.01, -0.01])
    assert features["rolling_drawdown"].iloc[2] == pytest.approx(-0.1)


def test_classify_market_regimes_labels_trend_and_volatility() -> None:
    features = pd.DataFrame(
        {
            "momentum": [-0.02, 0.0, 0.03],
            "rolling_volatility": [0.1, 0.2, 0.3],
        },
        index=pd.date_range("2026-01-01", periods=3, tz="UTC"),
    )

    regimes = classify_market_regimes(
        features,
        config=RegimeConfig(momentum_threshold=0.01, volatility_threshold=0.2),
    )

    assert regimes["trend_regime"].tolist() == ["bear", "neutral", "bull"]
    assert regimes["volatility_regime"].tolist() == [
        "low_volatility",
        "low_volatility",
        "high_volatility",
    ]
    assert regimes["regime"].iloc[-1] == "bull/high_volatility"


def test_feature_and_regime_validation_errors() -> None:
    with pytest.raises(ValueError):
        build_market_features(_market_data([100.0, 0.0]))

    with pytest.raises(ValueError):
        classify_market_regimes(pd.DataFrame({"momentum": [0.01]}))


def _market_data(close_values: list[float]) -> pd.DataFrame:
    """Build a deterministic market-data frame."""
    return pd.DataFrame(
        {"close": close_values},
        index=pd.date_range("2026-01-01", periods=len(close_values), tz="UTC"),
    )
