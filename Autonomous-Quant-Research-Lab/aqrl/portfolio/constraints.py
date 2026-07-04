"""Portfolio constraint primitives for AQRL."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from math import isfinite
from types import MappingProxyType

from aqrl.core.exceptions import AQRLValidationError
from aqrl.core.utils import normalize_name

type WeightMap = Mapping[str, float]


class PortfolioConstraintError(AQRLValidationError):
    """Raised when portfolio weights violate configured constraints."""


@dataclass(frozen=True, slots=True)
class PortfolioConstraintViolation:
    """Machine-readable portfolio constraint violation."""

    check: str
    message: str
    asset: str | None = None
    value: float | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "check", normalize_name(self.check, "check"))
        object.__setattr__(self, "message", normalize_name(self.message, "message"))
        if self.asset is not None:
            object.__setattr__(self, "asset", normalize_name(self.asset, "asset"))
        if self.value is not None:
            if not isinstance(self.value, int | float):
                raise TypeError("value must be numeric when present.")
            if not isfinite(float(self.value)):
                raise ValueError("value must be finite when present.")
            object.__setattr__(self, "value", float(self.value))


@dataclass(frozen=True, slots=True)
class PortfolioConstraints:
    """Simple long/short portfolio constraints."""

    min_weight: float = 0.0
    max_weight: float = 1.0
    net_exposure: float = 1.0
    tolerance: float = 1e-8
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for field_name in ("min_weight", "max_weight", "net_exposure", "tolerance"):
            value = getattr(self, field_name)
            if not isinstance(value, int | float):
                raise TypeError(f"{field_name} must be numeric.")
            if not isfinite(float(value)):
                raise ValueError(f"{field_name} must be finite.")
            object.__setattr__(self, field_name, float(value))

        if self.min_weight > self.max_weight:
            raise ValueError("min_weight must be less than or equal to max_weight.")
        if self.tolerance < 0:
            raise ValueError("tolerance must be non-negative.")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping.")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def validate(self, weights: WeightMap) -> tuple[PortfolioConstraintViolation, ...]:
        """Return all violations for a weight map."""
        normalized = coerce_weights(weights)
        violations: list[PortfolioConstraintViolation] = []
        total_weight = sum(normalized.values())

        if abs(total_weight - self.net_exposure) > self.tolerance:
            violations.append(
                PortfolioConstraintViolation(
                    check="net_exposure",
                    message="Portfolio weights do not match target net exposure.",
                    value=total_weight,
                )
            )

        for asset, weight in normalized.items():
            if weight < self.min_weight - self.tolerance:
                violations.append(
                    PortfolioConstraintViolation(
                        check="min_weight",
                        message="Asset weight is below the minimum.",
                        asset=asset,
                        value=weight,
                    )
                )
            if weight > self.max_weight + self.tolerance:
                violations.append(
                    PortfolioConstraintViolation(
                        check="max_weight",
                        message="Asset weight is above the maximum.",
                        asset=asset,
                        value=weight,
                    )
                )
        return tuple(violations)

    def assert_valid(self, weights: WeightMap) -> None:
        """Raise when a weight map violates constraints."""
        violations = self.validate(weights)
        if violations:
            joined = "; ".join(violation.message for violation in violations)
            raise PortfolioConstraintError(joined)


def coerce_weights(weights: WeightMap) -> dict[str, float]:
    """Validate and normalize a weight mapping into a plain dictionary."""
    if not isinstance(weights, Mapping):
        raise TypeError("weights must be a mapping.")
    if not weights:
        raise ValueError("weights must contain at least one asset.")

    normalized: dict[str, float] = {}
    for asset, weight in weights.items():
        normalized_asset = normalize_name(asset, "asset")
        if normalized_asset in normalized:
            raise ValueError(f"duplicate normalized asset name: {normalized_asset}")
        if not isinstance(weight, int | float):
            raise TypeError(f"weight for {normalized_asset} must be numeric.")
        numeric_weight = float(weight)
        if not isfinite(numeric_weight):
            raise ValueError(f"weight for {normalized_asset} must be finite.")
        normalized[normalized_asset] = numeric_weight
    return normalized


def normalize_weights(
    weights: WeightMap,
    *,
    net_exposure: float = 1.0,
) -> dict[str, float]:
    """Scale weights so they sum to the requested net exposure."""
    normalized = coerce_weights(weights)
    if not isinstance(net_exposure, int | float):
        raise TypeError("net_exposure must be numeric.")
    target_exposure = float(net_exposure)
    if not isfinite(target_exposure):
        raise ValueError("net_exposure must be finite.")

    total_weight = sum(normalized.values())
    if total_weight == 0.0:
        raise ValueError("weights must not sum to zero.")
    scale = target_exposure / total_weight
    return {asset: weight * scale for asset, weight in normalized.items()}


__all__ = [
    "PortfolioConstraintError",
    "PortfolioConstraintViolation",
    "PortfolioConstraints",
    "WeightMap",
    "coerce_weights",
    "normalize_weights",
]
