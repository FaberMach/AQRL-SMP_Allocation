"""Structured data-quality checks for AQRL datasets."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import Any, Literal

import pandas as pd

from aqrl.core.utils import ensure_mapping, json_safe, normalize_name, utc_now

Severity = Literal["warning", "error"]
DEFAULT_PRICE_COLUMNS = ("open", "high", "low", "close", "adj_close")


@dataclass(frozen=True, slots=True)
class DataQualityIssue:
    """Machine-readable data-quality finding."""

    check: str
    severity: Severity
    message: str
    column: str | None = None
    row_count: int = 0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "check", normalize_name(self.check, "check"))
        if self.severity not in {"warning", "error"}:
            raise ValueError("severity must be 'warning' or 'error'.")
        object.__setattr__(self, "message", normalize_name(self.message, "message"))
        if self.column is not None:
            object.__setattr__(self, "column", normalize_name(self.column, "column"))
        if not isinstance(self.row_count, int):
            raise TypeError("row_count must be an integer.")
        if self.row_count < 0:
            raise ValueError("row_count must be non-negative.")
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(ensure_mapping(self.metadata, "metadata")),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the issue to a JSON-compatible dictionary."""
        return {
            "check": self.check,
            "severity": self.severity,
            "message": self.message,
            "column": self.column,
            "row_count": self.row_count,
            "metadata": json_safe(dict(self.metadata)),
        }


@dataclass(frozen=True, slots=True)
class DataQualityReport:
    """Structured result from data-quality validation."""

    row_count: int
    issues: tuple[DataQualityIssue, ...] = ()
    dataset_name: str | None = None
    generated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not isinstance(self.row_count, int):
            raise TypeError("row_count must be an integer.")
        if self.row_count < 0:
            raise ValueError("row_count must be non-negative.")
        object.__setattr__(self, "issues", tuple(self.issues))
        if self.dataset_name is not None:
            object.__setattr__(
                self,
                "dataset_name",
                normalize_name(self.dataset_name, "dataset_name"),
            )
        if not isinstance(self.generated_at, datetime):
            raise TypeError("generated_at must be a datetime instance.")
        if self.generated_at.tzinfo is None or self.generated_at.utcoffset() is None:
            raise ValueError("generated_at must be timezone-aware.")

    @property
    def passed(self) -> bool:
        """Return whether the report has no error-severity issues."""
        return not self.failures

    @property
    def failures(self) -> tuple[DataQualityIssue, ...]:
        """Return error-severity issues."""
        return tuple(issue for issue in self.issues if issue.severity == "error")

    def to_dict(self) -> dict[str, Any]:
        """Serialize the report to a JSON-compatible dictionary."""
        return {
            "dataset_name": self.dataset_name,
            "row_count": self.row_count,
            "passed": self.passed,
            "generated_at": self.generated_at.isoformat(),
            "issues": [issue.to_dict() for issue in self.issues],
        }


def validate_market_data(
    frame: pd.DataFrame,
    *,
    dataset_name: str | None = None,
    timestamp_column: str | None = None,
    price_columns: Sequence[str] = DEFAULT_PRICE_COLUMNS,
) -> DataQualityReport:
    """Validate common market-data invariants."""
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("frame must be a pandas DataFrame.")

    issues: list[DataQualityIssue] = []
    row_count = len(frame)
    if row_count == 0:
        issues.append(
            DataQualityIssue(
                check="empty_dataset",
                severity="error",
                message="Dataset has no rows.",
            )
        )
        return DataQualityReport(
            row_count=row_count,
            issues=tuple(issues),
            dataset_name=dataset_name,
        )

    issues.extend(_missing_value_issues(frame))
    timestamp_values = _timestamp_values(frame, timestamp_column, issues)
    if timestamp_values is not None:
        issues.extend(_timestamp_issues(timestamp_values))
    issues.extend(_price_issues(frame, price_columns))

    return DataQualityReport(
        row_count=row_count,
        issues=tuple(issues),
        dataset_name=dataset_name,
    )


def _missing_value_issues(frame: pd.DataFrame) -> tuple[DataQualityIssue, ...]:
    """Return missing-value issues by column."""
    issues: list[DataQualityIssue] = []
    missing_counts = frame.isna().sum()
    for column, count in missing_counts.items():
        missing_count = int(count)
        if missing_count:
            issues.append(
                DataQualityIssue(
                    check="missing_values",
                    severity="error",
                    message=f"Column '{column}' contains missing values.",
                    column=str(column),
                    row_count=missing_count,
                )
            )
    return tuple(issues)


def _timestamp_values(
    frame: pd.DataFrame,
    timestamp_column: str | None,
    issues: list[DataQualityIssue],
) -> pd.Series[Any] | None:
    """Return timestamp values from a column, timestamp column, or DateTimeIndex."""
    if timestamp_column is not None:
        normalized_column = normalize_name(timestamp_column, "timestamp_column")
        if normalized_column not in frame.columns:
            issues.append(
                DataQualityIssue(
                    check="missing_timestamp_column",
                    severity="error",
                    message=f"Timestamp column '{normalized_column}' is missing.",
                    column=normalized_column,
                )
            )
            return None
        return frame[normalized_column]

    if "timestamp" in frame.columns:
        return frame["timestamp"]
    if isinstance(frame.index, pd.DatetimeIndex):
        return pd.Series(frame.index, index=frame.index, name="timestamp")

    issues.append(
        DataQualityIssue(
            check="missing_timestamp",
            severity="error",
            message="Dataset must provide a timestamp column or DateTimeIndex.",
        )
    )
    return None


def _timestamp_issues(timestamps: pd.Series[Any]) -> tuple[DataQualityIssue, ...]:
    """Return duplicate and monotonicity timestamp issues."""
    issues: list[DataQualityIssue] = []
    duplicate_count = int(timestamps.duplicated().sum())
    if duplicate_count:
        issues.append(
            DataQualityIssue(
                check="duplicate_timestamps",
                severity="error",
                message="Dataset contains duplicate timestamps.",
                column=str(timestamps.name or "timestamp"),
                row_count=duplicate_count,
            )
        )
    if not bool(timestamps.is_monotonic_increasing):
        issues.append(
            DataQualityIssue(
                check="non_monotonic_timestamp",
                severity="error",
                message="Timestamps must be monotonic increasing.",
                column=str(timestamps.name or "timestamp"),
            )
        )
    return tuple(issues)


def _price_issues(
    frame: pd.DataFrame,
    price_columns: Sequence[str],
) -> tuple[DataQualityIssue, ...]:
    """Return common OHLC price sanity issues."""
    issues: list[DataQualityIssue] = []
    normalized_columns = tuple(normalize_name(column, "price column") for column in price_columns)
    available = tuple(column for column in normalized_columns if column in frame.columns)
    if not available:
        return (
            DataQualityIssue(
                check="missing_price_columns",
                severity="warning",
                message="Dataset has no recognized price columns.",
                metadata={"expected_columns": normalized_columns},
            ),
        )

    numeric_prices: dict[str, pd.Series[Any]] = {}
    for column in available:
        numeric = pd.to_numeric(frame[column], errors="coerce")
        numeric_prices[column] = numeric
        non_numeric = numeric.isna() & frame[column].notna()
        non_numeric_count = int(non_numeric.sum())
        if non_numeric_count:
            issues.append(
                DataQualityIssue(
                    check="non_numeric_prices",
                    severity="error",
                    message=f"Column '{column}' contains non-numeric prices.",
                    column=column,
                    row_count=non_numeric_count,
                )
            )
        non_positive_count = int((numeric <= 0).sum())
        if non_positive_count:
            issues.append(
                DataQualityIssue(
                    check="non_positive_prices",
                    severity="error",
                    message=f"Column '{column}' contains non-positive prices.",
                    column=column,
                    row_count=non_positive_count,
                )
            )

    if "high" in numeric_prices and "low" in numeric_prices:
        invalid_high_low = numeric_prices["high"] < numeric_prices["low"]
        invalid_count = int(invalid_high_low.sum())
        if invalid_count:
            issues.append(
                DataQualityIssue(
                    check="high_below_low",
                    severity="error",
                    message="High price is below low price.",
                    row_count=invalid_count,
                )
            )

    if {"close", "high", "low"}.issubset(numeric_prices):
        close = numeric_prices["close"]
        invalid_close = (close > numeric_prices["high"]) | (close < numeric_prices["low"])
        invalid_count = int(invalid_close.sum())
        if invalid_count:
            issues.append(
                DataQualityIssue(
                    check="close_outside_high_low",
                    severity="error",
                    message="Close price is outside the high/low range.",
                    column="close",
                    row_count=invalid_count,
                )
            )
    return tuple(issues)


__all__ = [
    "DEFAULT_PRICE_COLUMNS",
    "DataQualityIssue",
    "DataQualityReport",
    "Severity",
    "validate_market_data",
]
