"""Shared utility helpers for AQRL core infrastructure."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .types import PathLikeValue


def normalize_name(value: str, field_name: str = "name") -> str:
    """Validate and normalize a textual identifier."""
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string.")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty.")
    return normalized


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(tz=UTC)


def coerce_bool(value: Any, field_name: str = "value") -> bool:
    """Coerce common boolean-like inputs into ``bool``."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and not isinstance(value, bool) and value in {0, 1}:
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
    raise TypeError(f"{field_name} must be a boolean-like value.")


def coerce_path(value: PathLikeValue, field_name: str = "path") -> Path:
    """Coerce a string or ``Path`` into a ``Path`` instance."""
    if isinstance(value, Path):
        return value
    if isinstance(value, str):
        return Path(value)
    raise TypeError(f"{field_name} must be a path-like string or Path instance.")


def ensure_mapping(value: Any, field_name: str) -> dict[str, Any]:
    """Validate a mapping and convert it into a plain dictionary."""
    if not isinstance(value, Mapping):
        raise TypeError(f"{field_name} must be a mapping.")
    return dict(value)


def json_safe(value: Any) -> Any:
    """Convert common Python values into JSON-serializable data."""
    if value is None or isinstance(value, bool | int | float | str):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, set):
        return [json_safe(item) for item in value]
    return repr(value)


__all__ = [
    "coerce_bool",
    "coerce_path",
    "ensure_mapping",
    "json_safe",
    "normalize_name",
    "utc_now",
]
