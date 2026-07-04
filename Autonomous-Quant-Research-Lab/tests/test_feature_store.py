from pathlib import Path

import pandas as pd
import pandas.testing as pdt

from aqrl.data.feature_store import FeatureSet, FeatureStore


def test_feature_store_persists_feature_frames(tmp_path: Path) -> None:
    store = FeatureStore(tmp_path / "features")
    frame = pd.DataFrame(
        {
            "close": [100.0, 101.5],
            "volume": [10, 12],
        },
        index=pd.date_range("2024-01-01", periods=2, tz="UTC"),
    )

    record = store.put("prices", frame, metadata={"source": "unit-test"})
    frame.iloc[0, 0] = 999.0

    assert isinstance(record, FeatureSet)
    assert record.name == "prices"
    assert record.metadata == {"source": "unit-test"}
    assert record.frame.iloc[0, 0] == 100.0
    assert store.exists("prices") is True
    assert store.list() == ("prices",)

    loaded = store.get("prices")
    pdt.assert_frame_equal(loaded.frame, record.frame)
    pdt.assert_frame_equal(store.load_frame("prices"), record.frame)

    removed = store.remove("prices")
    assert removed.name == "prices"
    assert store.exists("prices") is False
