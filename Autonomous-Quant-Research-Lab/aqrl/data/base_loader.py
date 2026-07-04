"""Base loader abstractions for AQRL data sources."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date, datetime
from hashlib import sha256
from typing import Any

from aqrl.core.utils import ensure_mapping, json_safe, normalize_name

type TimePoint = date | datetime | str


@dataclass(frozen=True, slots=True)
class LoadRequest:
    """Immutable request describing a data-loading operation."""

    symbol: str
    start: TimePoint | None = None
    end: TimePoint | None = None
    interval: str = "1d"
    adjusted: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "symbol", normalize_name(self.symbol, "symbol"))
        object.__setattr__(self, "interval", normalize_name(self.interval, "interval").lower())
        object.__setattr__(self, "metadata", ensure_mapping(self.metadata, "metadata"))

        if not isinstance(self.adjusted, bool):
            raise TypeError("adjusted must be a boolean.")
        self._validate_timepoint(self.start, "start")
        self._validate_timepoint(self.end, "end")

    @staticmethod
    def _validate_timepoint(value: TimePoint | None, field_name: str) -> None:
        """Validate a load time boundary."""
        if value is None:
            return
        if isinstance(value, str):
            if not value.strip():
                raise ValueError(f"{field_name} must not be empty.")
            return
        if isinstance(value, datetime):
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError(f"{field_name} datetime values must be timezone-aware.")
            return
        if isinstance(value, date):
            return
        raise TypeError(f"{field_name} must be a date, datetime, string, or None.")


class BaseLoader(ABC):
    """Shared behavior for concrete AQRL data loaders."""

    def load(
        self,
        symbol: str,
        *,
        start: TimePoint | None = None,
        end: TimePoint | None = None,
        interval: str = "1d",
        adjusted: bool = True,
        metadata: Mapping[str, Any] | None = None,
    ) -> Any:
        """Build a request and delegate to the concrete loader implementation."""
        request = LoadRequest(
            symbol=symbol,
            start=start,
            end=end,
            interval=interval,
            adjusted=adjusted,
            metadata={} if metadata is None else metadata,
        )
        return self._load(request)

    @abstractmethod
    def _load(self, request: LoadRequest) -> Any:
        """Load a resource for the given request."""

    @staticmethod
    def _cache_key(namespace: str, request: LoadRequest) -> str:
        """Build a stable cache key for a request."""
        normalized_namespace = normalize_name(namespace, "namespace")
        payload = {
            "adjusted": request.adjusted,
            "end": BaseLoader._serialize_timepoint(request.end),
            "interval": request.interval,
            "metadata": json_safe(request.metadata),
            "namespace": normalized_namespace,
            "start": BaseLoader._serialize_timepoint(request.start),
            "symbol": request.symbol,
        }
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        digest = sha256(encoded.encode("utf-8")).hexdigest()
        return f"{normalized_namespace}:{digest}"

    @staticmethod
    def _serialize_timepoint(value: TimePoint | None) -> str | None:
        """Serialize a time boundary into a stable textual representation."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, str):
            return value.strip()
        return repr(value)


__all__ = ["BaseLoader", "LoadRequest", "TimePoint"]
