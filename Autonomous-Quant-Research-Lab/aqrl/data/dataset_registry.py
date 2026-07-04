"""Dataset catalog primitives for AQRL."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from types import MappingProxyType
from typing import Any, Self

from aqrl.core.exceptions import AQRLDataError
from aqrl.core.utils import ensure_mapping, json_safe, normalize_name, utc_now

type DatasetKey = tuple[str, str]


class DatasetRegistryError(AQRLDataError):
    """Base error for dataset registry operations."""


class DatasetAlreadyExistsError(DatasetRegistryError):
    """Raised when a dataset version is already registered."""


class DatasetNotFoundError(DatasetRegistryError):
    """Raised when a dataset version cannot be found."""


@dataclass(frozen=True, slots=True)
class DatasetMetadata:
    """Versioned metadata describing a persisted dataset."""

    name: str
    version: str
    source: str
    schema: Mapping[str, str]
    storage_uri: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utc_now)
    deprecated: bool = False
    deprecated_at: datetime | None = None
    deprecation_reason: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", normalize_name(self.name, "name"))
        object.__setattr__(self, "version", normalize_name(self.version, "version"))
        object.__setattr__(self, "source", normalize_name(self.source, "source"))
        object.__setattr__(self, "storage_uri", normalize_name(self.storage_uri, "storage_uri"))
        object.__setattr__(self, "schema", _freeze_schema(self.schema))
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(ensure_mapping(self.metadata, "metadata")),
        )

        _validate_timezone_aware(self.created_at, "created_at")
        if not isinstance(self.deprecated, bool):
            raise TypeError("deprecated must be a boolean.")
        if self.deprecated_at is not None:
            _validate_timezone_aware(self.deprecated_at, "deprecated_at")
        if self.deprecation_reason is not None:
            object.__setattr__(
                self,
                "deprecation_reason",
                normalize_name(self.deprecation_reason, "deprecation_reason"),
            )
        if self.deprecated and self.deprecated_at is None:
            object.__setattr__(self, "deprecated_at", utc_now())
        if not self.deprecated and self.deprecated_at is not None:
            raise ValueError("deprecated_at requires deprecated=True.")

    @property
    def dataset_id(self) -> str:
        """Return the stable name/version identifier."""
        return f"{self.name}:{self.version}"

    def deprecate(self, reason: str | None = None) -> DatasetMetadata:
        """Return a deprecated copy of this metadata."""
        normalized_reason = None if reason is None else normalize_name(reason, "reason")
        return replace(
            self,
            deprecated=True,
            deprecated_at=utc_now(),
            deprecation_reason=normalized_reason,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize metadata to a JSON-compatible dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "source": self.source,
            "schema": dict(self.schema),
            "storage_uri": self.storage_uri,
            "metadata": json_safe(dict(self.metadata)),
            "created_at": self.created_at.isoformat(),
            "deprecated": self.deprecated,
            "deprecated_at": None if self.deprecated_at is None else self.deprecated_at.isoformat(),
            "deprecation_reason": self.deprecation_reason,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> Self:
        """Deserialize metadata from a JSON-compatible mapping."""
        created_at = _parse_datetime(payload.get("created_at"), "created_at")
        deprecated_at_raw = payload.get("deprecated_at")
        deprecated_at = (
            None
            if deprecated_at_raw is None
            else _parse_datetime(deprecated_at_raw, "deprecated_at")
        )
        return cls(
            name=_expect_str(payload, "name"),
            version=_expect_str(payload, "version"),
            source=_expect_str(payload, "source"),
            schema=_expect_mapping(payload, "schema"),
            storage_uri=_expect_str(payload, "storage_uri"),
            metadata=_expect_mapping(payload, "metadata", default={}),
            created_at=created_at,
            deprecated=bool(payload.get("deprecated", False)),
            deprecated_at=deprecated_at,
            deprecation_reason=_expect_optional_str(payload, "deprecation_reason"),
        )


class DatasetRegistry:
    """In-memory dataset catalog with optional JSON persistence."""

    def __init__(self, path: Path | str | None = None) -> None:
        self.path = None if path is None else Path(path).expanduser()
        self._datasets: dict[DatasetKey, DatasetMetadata] = self._load()

    def add(self, dataset: DatasetMetadata, *, overwrite: bool = False) -> DatasetMetadata:
        """Register dataset metadata."""
        key = self._key(dataset.name, dataset.version)
        if key in self._datasets and not overwrite:
            raise DatasetAlreadyExistsError(f"Dataset already registered: {dataset.dataset_id}")
        self._datasets[key] = dataset
        self._write()
        return dataset

    def register(
        self,
        name: str,
        *,
        version: str,
        source: str,
        schema: Mapping[str, str],
        storage_uri: str,
        metadata: Mapping[str, Any] | None = None,
        overwrite: bool = False,
    ) -> DatasetMetadata:
        """Create and register dataset metadata."""
        dataset = DatasetMetadata(
            name=name,
            version=version,
            source=source,
            schema=schema,
            storage_uri=storage_uri,
            metadata={} if metadata is None else metadata,
        )
        return self.add(dataset, overwrite=overwrite)

    def get(self, name: str, version: str) -> DatasetMetadata:
        """Return metadata for a dataset name/version pair."""
        key = self._key(name, version)
        try:
            return self._datasets[key]
        except KeyError as exc:
            raise DatasetNotFoundError(f"Dataset not found: {key[0]}:{key[1]}") from exc

    def list(self, *, include_deprecated: bool = True) -> tuple[DatasetMetadata, ...]:
        """Return registered datasets in insertion order."""
        datasets = tuple(self._datasets.values())
        if include_deprecated:
            return datasets
        return tuple(dataset for dataset in datasets if not dataset.deprecated)

    def deprecate(
        self,
        name: str,
        version: str,
        *,
        reason: str | None = None,
    ) -> DatasetMetadata:
        """Mark a dataset version as deprecated."""
        dataset = self.get(name, version).deprecate(reason)
        self._datasets[self._key(name, version)] = dataset
        self._write()
        return dataset

    @staticmethod
    def _key(name: str, version: str) -> DatasetKey:
        """Normalize a dataset registry key."""
        return (normalize_name(name, "name"), normalize_name(version, "version"))

    def _load(self) -> dict[DatasetKey, DatasetMetadata]:
        """Load registry records from disk when persistence is enabled."""
        if self.path is None or not self.path.exists():
            return {}
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise DatasetRegistryError("Failed to load dataset registry.") from exc
        if not isinstance(raw, list):
            raise DatasetRegistryError("Dataset registry must contain a list of records.")

        datasets: dict[DatasetKey, DatasetMetadata] = {}
        for item in raw:
            if not isinstance(item, Mapping):
                raise DatasetRegistryError("Dataset registry records must be mappings.")
            dataset = DatasetMetadata.from_dict(item)
            datasets[self._key(dataset.name, dataset.version)] = dataset
        return datasets

    def _write(self) -> None:
        """Persist registry records when persistence is enabled."""
        if self.path is None:
            return
        payload = [dataset.to_dict() for dataset in self._datasets.values()]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(
            delete=False,
            dir=self.path.parent,
            suffix=".tmp",
            mode="w",
            encoding="utf-8",
        ) as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            temp_path = Path(handle.name)
        temp_path.replace(self.path)


def _freeze_schema(schema: Mapping[str, str]) -> Mapping[str, str]:
    """Validate and freeze a dataset schema mapping."""
    if not isinstance(schema, Mapping):
        raise TypeError("schema must be a mapping.")
    frozen: dict[str, str] = {}
    for column, dtype in schema.items():
        if not isinstance(column, str):
            raise TypeError("schema column names must be strings.")
        if not isinstance(dtype, str):
            raise TypeError("schema dtype values must be strings.")
        frozen[normalize_name(column, "schema column")] = normalize_name(dtype, "schema dtype")
    if not frozen:
        raise ValueError("schema must contain at least one column.")
    return MappingProxyType(frozen)


def _validate_timezone_aware(value: datetime, field_name: str) -> None:
    """Validate timezone-aware datetimes."""
    if not isinstance(value, datetime):
        raise TypeError(f"{field_name} must be a datetime instance.")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware.")


def _parse_datetime(value: Any, field_name: str) -> datetime:
    """Parse an ISO timestamp from registry JSON."""
    if not isinstance(value, str):
        raise DatasetRegistryError(f"{field_name} must be an ISO datetime string.")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise DatasetRegistryError(f"{field_name} must be an ISO datetime string.") from exc
    _validate_timezone_aware(parsed, field_name)
    return parsed


def _expect_str(payload: Mapping[str, Any], key: str) -> str:
    """Return a required string from a payload."""
    value = payload.get(key)
    if not isinstance(value, str):
        raise DatasetRegistryError(f"{key} must be a string.")
    return value


def _expect_optional_str(payload: Mapping[str, Any], key: str) -> str | None:
    """Return an optional string from a payload."""
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise DatasetRegistryError(f"{key} must be a string when present.")
    return value


def _expect_mapping(
    payload: Mapping[str, Any],
    key: str,
    *,
    default: Mapping[str, Any] | None = None,
) -> Mapping[str, Any]:
    """Return a mapping from a payload."""
    value = payload.get(key, default)
    if not isinstance(value, Mapping):
        raise DatasetRegistryError(f"{key} must be a mapping.")
    return value


__all__ = [
    "DatasetAlreadyExistsError",
    "DatasetKey",
    "DatasetMetadata",
    "DatasetNotFoundError",
    "DatasetRegistry",
    "DatasetRegistryError",
]
