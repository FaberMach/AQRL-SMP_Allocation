from pathlib import Path
from typing import Any, cast

import pytest

from aqrl.data.market_state import MarketState


def test_market_state_normalizes_and_copies_mappings() -> None:
    prices = {"AAPL": 101, "MSFT": 250.5}
    returns = {"AAPL": 0.01}
    volatility = {"AAPL": 0.2}
    metadata = {"source": "yahoo", "path": Path("cache/prices.csv")}

    state = MarketState(
        prices=prices,
        returns=returns,
        volatility=volatility,
        metadata=metadata,
    )

    prices["AAPL"] = 999

    assert state.prices == {"AAPL": 101.0, "MSFT": 250.5}
    assert state.returns == {"AAPL": 0.01}
    assert state.volatility == {"AAPL": 0.2}
    assert state.metadata == metadata
    assert state.prices is not prices


def test_market_state_rejects_non_numeric_values() -> None:
    prices = cast(dict[str, Any], {"AAPL": "invalid"})

    with pytest.raises(TypeError, match="prices"):
        MarketState(prices=prices)
