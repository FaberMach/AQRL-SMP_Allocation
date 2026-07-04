from pathlib import Path

import pandas as pd
import pytest

from aqrl.core.exceptions import AQRLDataError
from aqrl.data.dataset_registry import DatasetAlreadyExistsError
from aqrl.data.market_data_store import MarketDataStore


def test_market_data_store_writes_reads_and_queries_parquet(tmp_path: Path) -> None:
    store = MarketDataStore(tmp_path / "market_data")
    frame = _market_frame([100.0, 101.5])

    dataset = store.write(
        "daily_prices",
        "v1",
        frame,
        source="unit-test",
        metadata={"asset_class": "equity"},
    )

    assert dataset.dataset_id == "daily_prices:v1"
    assert dataset.source == "unit-test"
    assert dataset.metadata["rows"] == 2
    assert dataset.metadata["partition_by"] == ["symbol"]
    assert dataset.metadata["asset_class"] == "equity"
    assert "timestamp" in dataset.schema

    loaded = store.read("daily_prices", "v1").sort_values("timestamp").reset_index(drop=True)
    assert loaded["symbol"].astype(str).tolist() == ["AAPL", "AAPL"]
    assert loaded["close"].tolist() == [100.0, 101.5]

    queried = store.query(
        "daily_prices",
        "v1",
        "SELECT symbol, COUNT(*) AS rows, AVG(close) AS avg_close "
        "FROM market_data GROUP BY symbol",
    )
    assert queried.loc[0, "symbol"] == "AAPL"
    assert queried.loc[0, "rows"] == 2
    assert queried.loc[0, "avg_close"] == pytest.approx(100.75)


def test_market_data_store_overwrite_and_missing_paths(tmp_path: Path) -> None:
    store = MarketDataStore(tmp_path / "market_data")
    store.write("daily_prices", "v1", _market_frame([100.0, 101.5]))

    with pytest.raises(DatasetAlreadyExistsError):
        store.write("daily_prices", "v1", _market_frame([200.0, 201.5]))

    store.write("daily_prices", "v1", _market_frame([200.0, 201.5]), overwrite=True)
    loaded = store.read("daily_prices", "v1").sort_values("timestamp").reset_index(drop=True)

    assert loaded["close"].tolist() == [200.0, 201.5]

    with pytest.raises(AQRLDataError):
        store.read("missing", "v1")


def _market_frame(close_values: list[float]) -> pd.DataFrame:
    """Build a deterministic market-data frame for store tests."""
    return pd.DataFrame(
        {
            "symbol": ["AAPL", "AAPL"],
            "open": [99.0, 100.5],
            "high": [101.0, 102.0],
            "low": [98.5, 100.0],
            "close": close_values,
            "volume": [1_000, 1_100],
        },
        index=pd.date_range("2024-01-01", periods=2, tz="UTC", name="timestamp"),
    )
