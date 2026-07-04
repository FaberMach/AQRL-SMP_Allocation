"""Canonical market state model for AQRL."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from numbers import Real
from types import MappingProxyType
from typing import Any


@dataclass(frozen=True, slots=True)
class MarketState:
    """Immutable market snapshot used by downstream data and research layers."""

    prices: Mapping[str, float] = field(default_factory=dict)
    returns: Mapping[str, float] = field(default_factory=dict)
    volatility: Mapping[str, float] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "prices", _coerce_numeric_mapping(self.prices, "prices"))
        object.__setattr__(self, "returns", _coerce_numeric_mapping(self.returns, "returns"))
        object.__setattr__(
            self, "volatility", _coerce_numeric_mapping(self.volatility, "volatility")
        )
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata, "metadata"))


def _freeze_mapping(value: Mapping[str, Any], field_name: str) -> Mapping[str, Any]:
    """Validate and freeze a generic mapping."""
    if not isinstance(value, Mapping):
        raise TypeError(f"{field_name} must be a mapping.")
    return MappingProxyType({_normalize_key(key, field_name): item for key, item in value.items()})


def _coerce_numeric_mapping(value: Mapping[str, Any], field_name: str) -> Mapping[str, float]:
    """Validate and freeze a numeric mapping."""
    if not isinstance(value, Mapping):
        raise TypeError(f"{field_name} must be a mapping.")
    frozen: dict[str, float] = {}
    for key, item in value.items():
        normalized_key = _normalize_key(key, field_name)
        frozen[normalized_key] = _coerce_number(item, field_name)
    return MappingProxyType(frozen)


def _normalize_key(key: Any, field_name: str) -> str:
    """Normalize mapping keys used by the market state."""
    if not isinstance(key, str):
        raise TypeError(f"{field_name} keys must be strings.")
    normalized_key = key.strip()
    if not normalized_key:
        raise ValueError(f"{field_name} keys must not be empty.")
    return normalized_key


def _coerce_number(value: Any, field_name: str) -> float:
    """Validate and convert numeric values to floats."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{field_name} values must be numeric.")
    return float(value)


__all__ = ["MarketState"]
