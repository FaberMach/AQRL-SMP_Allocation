"""Parquet and DuckDB persistence for market data datasets."""

from __future__ import annotations

import shutil
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

from aqrl.core.exceptions import AQRLDataError
from aqrl.core.utils import json_safe, normalize_name

from .dataset_registry import (
    DatasetAlreadyExistsError,
    DatasetMetadata,
    DatasetRegistry,
)

DEFAULT_PARTITION_COLUMNS = ("symbol",)


class MarketDataStore:
    """Persist versioned market data frames as Parquet datasets."""

    def __init__(
        self,
        root: Path | str = Path("artifacts/market_data"),
        *,
        registry: DatasetRegistry | None = None,
    ) -> None:
        self.root = Path(root).expanduser()
        self.root.mkdir(parents=True, exist_ok=True)
        self.registry = (
            DatasetRegistry(self.root / "datasets.json") if registry is None else registry
        )

    def write(
        self,
        name: str,
        version: str,
        frame: pd.DataFrame,
        *,
        source: str = "market-data",
        partition_by: Sequence[str] = DEFAULT_PARTITION_COLUMNS,
        overwrite: bool = False,
        metadata: Mapping[str, Any] | None = None,
    ) -> DatasetMetadata:
        """Write market data to Parquet and register its metadata."""
        dataset_path = self._dataset_path(name, version)
        if dataset_path.exists():
            if not overwrite:
                raise DatasetAlreadyExistsError(f"Dataset storage already exists: {name}:{version}")
            self._remove_dataset_path(dataset_path)

        prepared = self._prepare_frame(frame)
        partition_columns = self._validate_partition_columns(prepared, partition_by)
        if partition_columns:
            prepared.to_parquet(dataset_path, partition_cols=list(partition_columns), index=False)
        else:
            dataset_path.mkdir(parents=True, exist_ok=True)
            prepared.to_parquet(dataset_path / "data.parquet", index=False)

        dataset_metadata = {
            "rows": len(prepared),
            "partition_by": list(partition_columns),
            **({} if metadata is None else json_safe(dict(metadata))),
        }
        dataset = DatasetMetadata(
            name=name,
            version=version,
            source=source,
            schema=self._schema_for(prepared),
            storage_uri=dataset_path.resolve().as_uri(),
            metadata=dataset_metadata,
        )
        return self.registry.add(dataset, overwrite=overwrite)

    def read(
        self,
        name: str,
        version: str,
        *,
        columns: Sequence[str] | None = None,
    ) -> pd.DataFrame:
        """Read a persisted Parquet dataset into a DataFrame."""
        dataset_path = self._existing_dataset_path(name, version)
        selected_columns = None if columns is None else list(columns)
        try:
            frame = pd.read_parquet(dataset_path, columns=selected_columns)
        except FileNotFoundError as exc:
            raise AQRLDataError(f"No Parquet files found for dataset: {name}:{version}") from exc
        return frame

    def query(
        self,
        name: str,
        version: str,
        sql: str = "SELECT * FROM market_data",
    ) -> pd.DataFrame:
        """Query a persisted dataset through DuckDB.

        The query can reference a view named ``market_data``.
        """
        dataset_path = self._existing_dataset_path(name, version)
        parquet_files = tuple(dataset_path.rglob("*.parquet"))
        if not parquet_files:
            raise AQRLDataError(f"No Parquet files found for dataset: {name}:{version}")

        pattern = (dataset_path / "**" / "*.parquet").as_posix().replace("'", "''")
        connection = duckdb.connect(database=":memory:")
        try:
            connection.execute(
                "CREATE VIEW market_data AS "
                f"SELECT * FROM read_parquet('{pattern}', hive_partitioning = true)"
            )
            return connection.execute(sql).fetchdf()
        finally:
            connection.close()

    def _dataset_path(self, name: str, version: str) -> Path:
        """Return the storage path for a dataset name/version."""
        return self.root / self._safe_segment(name, "name") / self._safe_segment(version, "version")

    def _existing_dataset_path(self, name: str, version: str) -> Path:
        """Return an existing storage path or raise a data error."""
        dataset_path = self._dataset_path(name, version)
        if not dataset_path.exists():
            raise AQRLDataError(f"Dataset storage not found: {name}:{version}")
        return dataset_path

    def _remove_dataset_path(self, dataset_path: Path) -> None:
        """Remove a dataset path after confirming it is under the store root."""
        root = self.root.resolve()
        resolved = dataset_path.resolve()
        if not str(resolved).lower().startswith(str(root).lower()):
            raise AQRLDataError(f"Refusing to remove outside market-data root: {resolved}")
        shutil.rmtree(resolved)

    @staticmethod
    def _prepare_frame(frame: pd.DataFrame) -> pd.DataFrame:
        """Validate and normalize a DataFrame before Parquet persistence."""
        if not isinstance(frame, pd.DataFrame):
            raise TypeError("frame must be a pandas DataFrame.")
        if frame.empty:
            raise ValueError("frame must contain at least one row.")
        if isinstance(frame.index, pd.MultiIndex):
            raise ValueError("MultiIndex frames must be flattened before persistence.")

        prepared = frame.copy(deep=True)
        if not isinstance(prepared.index, pd.RangeIndex):
            index_name = "timestamp" if prepared.index.name is None else str(prepared.index.name)
            if index_name in prepared.columns:
                raise ValueError(f"index name conflicts with an existing column: {index_name}")
            prepared = prepared.rename_axis(index_name).reset_index()
        return prepared

    @staticmethod
    def _validate_partition_columns(
        frame: pd.DataFrame,
        partition_by: Sequence[str],
    ) -> tuple[str, ...]:
        """Validate partition columns and return them as a tuple."""
        partition_columns = tuple(
            normalize_name(column, "partition column") for column in partition_by
        )
        missing = tuple(column for column in partition_columns if column not in frame.columns)
        if missing:
            raise ValueError(f"partition columns missing from frame: {', '.join(missing)}")
        return partition_columns

    @staticmethod
    def _schema_for(frame: pd.DataFrame) -> dict[str, str]:
        """Infer a stable schema mapping from a DataFrame."""
        return {str(column): str(dtype) for column, dtype in frame.dtypes.items()}

    @staticmethod
    def _safe_segment(value: str, field_name: str) -> str:
        """Return a path-safe dataset segment."""
        normalized = normalize_name(value, field_name)
        if normalized in {".", ".."} or "/" in normalized or "\\" in normalized:
            raise ValueError(f"{field_name} must be a single path segment.")
        return normalized


__all__ = ["DEFAULT_PARTITION_COLUMNS", "MarketDataStore"]
