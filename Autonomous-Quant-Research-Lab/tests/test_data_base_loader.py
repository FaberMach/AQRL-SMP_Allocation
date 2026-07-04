from datetime import UTC, datetime

import pytest

from aqrl.data.base_loader import BaseLoader, LoadRequest


class DummyLoader(BaseLoader):
    def _load(self, request: LoadRequest) -> LoadRequest:
        return request


def test_load_request_normalizes_fields() -> None:
    request = LoadRequest(
        symbol="  aapl  ",
        start="2024-01-01",
        end=datetime(2024, 1, 2, tzinfo=UTC),
        interval="1D",
        adjusted=True,
        metadata={"source": "test"},
    )

    assert request.symbol == "aapl"
    assert request.interval == "1d"
    assert request.metadata == {"source": "test"}


def test_load_request_rejects_invalid_timepoint() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        LoadRequest(
            symbol="AAPL",
            start=datetime(2024, 1, 1),
        )


def test_base_loader_builds_requests() -> None:
    loader = DummyLoader()

    request = loader.load("MSFT", interval="5D", metadata={"batch": 1})

    assert request.symbol == "MSFT"
    assert request.interval == "5d"
    assert request.metadata == {"batch": 1}
