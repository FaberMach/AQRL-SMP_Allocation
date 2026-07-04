from pathlib import Path
from typing import Any

import pandas.testing as pdt
from pytest import MonkeyPatch

from aqrl.data.base_loader import LoadRequest
from aqrl.data.cache import DataCache
from aqrl.data.yahoo_loader import YahooFinanceLoader


def test_yahoo_loader_builds_chart_url() -> None:
    loader = YahooFinanceLoader()

    url = loader.build_url(
        "AAPL",
        start="2024-01-01",
        end="2024-01-02",
        interval="1D",
    )

    assert url.startswith("https://query1.finance.yahoo.com/v8/finance/chart/AAPL?")
    assert "interval=1d" in url
    assert "period1=" in url
    assert "period2=" in url
    assert "events=div%2Csplits" in url


def test_yahoo_loader_parses_and_caches_chart_payload(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    cache = DataCache(tmp_path / "cache")
    loader = YahooFinanceLoader(cache=cache)
    calls = {"count": 0}

    sample_payload = {
        "chart": {
            "result": [
                {
                    "timestamp": [1704067200, 1704153600],
                    "indicators": {
                        "quote": [
                            {
                                "open": [10.0, 11.0],
                                "high": [10.5, 11.5],
                                "low": [9.5, 10.5],
                                "close": [10.25, 11.25],
                                "volume": [100, 110],
                            }
                        ],
                        "adjclose": [{"adjclose": [10.1, 11.1]}],
                    },
                    "meta": {"symbol": "AAPL"},
                }
            ],
            "error": None,
        }
    }

    def fake_fetch(request: LoadRequest) -> dict[str, Any]:
        calls["count"] += 1
        return sample_payload

    monkeypatch.setattr(loader, "_fetch_chart_payload", fake_fetch)

    frame = loader.load(
        "AAPL",
        start="2024-01-01",
        end="2024-01-02",
        interval="1d",
    )
    cached = loader.load(
        "AAPL",
        start="2024-01-01",
        end="2024-01-02",
        interval="1d",
    )

    assert calls["count"] == 1
    assert list(frame.columns) == [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "adj_close",
        "raw_close",
    ]
    assert frame.index.name == "timestamp"
    assert str(frame.index.tz) == "UTC"
    assert frame.attrs["symbol"] == "AAPL"
    assert frame.attrs["adjusted"] is True
    pdt.assert_frame_equal(frame, cached)
    assert frame["close"].tolist() == [10.1, 11.1]
    assert frame["raw_close"].tolist() == [10.25, 11.25]
