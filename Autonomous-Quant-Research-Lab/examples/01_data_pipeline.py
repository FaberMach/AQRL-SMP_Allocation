"""Offline AQRL data pipeline example."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd

from aqrl.data import MarketDataStore, validate_market_data
from aqrl.features import (
    FeatureConfig,
    RegimeConfig,
    build_market_features,
    classify_market_regimes,
)


def main() -> None:
    """Run a deterministic data-quality, persistence, feature, and regime flow."""
    market_data = pd.DataFrame(
        {
            "symbol": ["AAPL"] * 8,
            "open": [100.0, 101.0, 102.0, 101.5, 103.0, 104.0, 105.0, 106.0],
            "high": [101.0, 102.0, 103.0, 103.0, 104.0, 105.0, 106.0, 107.0],
            "low": [99.0, 100.0, 101.0, 100.5, 102.0, 103.0, 104.0, 105.0],
            "close": [100.5, 101.5, 102.2, 102.8, 103.5, 104.4, 105.2, 106.5],
            "volume": [1000, 1100, 1050, 1200, 1250, 1300, 1280, 1400],
        },
        index=pd.date_range("2026-01-01", periods=8, tz="UTC", name="timestamp"),
    )

    quality = validate_market_data(market_data)
    features = build_market_features(market_data, config=FeatureConfig(momentum_window=3))
    regimes = classify_market_regimes(features, config=RegimeConfig(momentum_threshold=0.005))

    with tempfile.TemporaryDirectory() as temp_dir:
        store = MarketDataStore(Path(temp_dir) / "market_data")
        dataset = store.write("example_prices", "v1", market_data)
        queried = store.query(
            "example_prices",
            "v1",
            "SELECT symbol, COUNT(*) AS rows, AVG(close) AS avg_close "
            "FROM market_data GROUP BY symbol",
        )

    print("quality_passed:", quality.passed)
    print("dataset:", dataset.dataset_id)
    print("features:", list(features.columns))
    print("latest_regime:", regimes["regime"].iloc[-1])
    print("duckdb_rows:", int(queried["rows"].iloc[0]))


if __name__ == "__main__":
    main()
