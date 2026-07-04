"""Feature store helpers for AQRL."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from aqrl.core.utils import ensure_mapping, normalize_name, utc_now

from .cache import DataCache


@dataclass(frozen=True, slots=True)
class FeatureSet:
    """Immutable snapshot of a named feature frame."""

    name: str
    frame: pd.DataFrame
    metadata: Mapping[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", normalize_name(self.name, "name"))

        if not isinstance(self.frame, pd.DataFrame):
            raise TypeError("frame must be a pandas DataFrame.")
        object.__setattr__(self, "frame", self.frame.copy(deep=True))

        object.__setattr__(self, "metadata", ensure_mapping(self.metadata, "metadata"))

        if not isinstance(self.created_at, datetime):
            raise TypeError("created_at must be a datetime instance.")
        if self.created_at.tzinfo is None or self.created_at.utcoffset() is None:
            raise ValueError("created_at must be timezone-aware.")


class FeatureStore:
    """Persist named pandas feature frames on disk."""

    def __init__(
        self,
        root: Path | str = Path(".cache/features"),
        *,
        cache: DataCache | None = None,
    ) -> None:
        self._cache = DataCache(root) if cache is None else cache

    def put(
        self,
        name: str,
        frame: pd.DataFrame,
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> FeatureSet:
        """Store a feature frame and return the persisted snapshot."""
        record = FeatureSet(
            name=name,
            frame=frame,
            metadata={} if metadata is None else metadata,
        )
        self._cache.set(record.name, record)
        return record

    def get(self, name: str) -> FeatureSet:
        """Return a stored feature snapshot."""
        record = self._cache.get(normalize_name(name, "name"))
        if record is None:
            raise KeyError(name)
        if not isinstance(record, FeatureSet):
            raise TypeError("Stored feature payload is not a FeatureSet.")
        return record

    def load_frame(self, name: str) -> pd.DataFrame:
        """Return the stored DataFrame for a feature name."""
        return self.get(name).frame.copy(deep=True)

    def exists(self, name: str) -> bool:
        """Return whether the store contains a feature name."""
        return self._cache.exists(normalize_name(name, "name"))

    def remove(self, name: str) -> FeatureSet:
        """Remove a stored feature snapshot and return it."""
        record = self.get(name)
        self._cache.delete(record.name)
        return record

    def list(self) -> tuple[str, ...]:
        """Return stored feature names in insertion order."""
        return self._cache.keys()


__all__ = ["FeatureSet", "FeatureStore"]
