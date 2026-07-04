from pathlib import Path

import pytest

from aqrl.data.dataset_registry import (
    DatasetAlreadyExistsError,
    DatasetMetadata,
    DatasetNotFoundError,
    DatasetRegistry,
)


def test_dataset_registry_adds_lists_persists_and_deprecates(tmp_path: Path) -> None:
    registry_path = tmp_path / "datasets.json"
    registry = DatasetRegistry(registry_path)
    metadata = DatasetMetadata(
        name="daily_prices",
        version="v1",
        source="unit-test",
        schema={"timestamp": "datetime64[ns, UTC]", "close": "float64"},
        storage_uri=(tmp_path / "daily_prices").resolve().as_uri(),
        metadata={"rows": 2},
    )

    registry.add(metadata)

    assert registry.get("daily_prices", "v1").dataset_id == "daily_prices:v1"
    assert registry.list() == (metadata,)

    reloaded = DatasetRegistry(registry_path)
    assert reloaded.get("daily_prices", "v1").metadata == {"rows": 2}

    deprecated = reloaded.deprecate("daily_prices", "v1", reason="superseded")
    assert deprecated.deprecated is True
    assert deprecated.deprecation_reason == "superseded"
    assert reloaded.list(include_deprecated=False) == ()


def test_dataset_registry_rejects_duplicate_and_missing_dataset(tmp_path: Path) -> None:
    registry = DatasetRegistry(tmp_path / "datasets.json")
    dataset = DatasetMetadata(
        name="daily_prices",
        version="v1",
        source="unit-test",
        schema={"close": "float64"},
        storage_uri=(tmp_path / "daily_prices").resolve().as_uri(),
    )

    registry.add(dataset)

    with pytest.raises(DatasetAlreadyExistsError):
        registry.add(dataset)

    with pytest.raises(DatasetNotFoundError):
        registry.get("daily_prices", "v2")
