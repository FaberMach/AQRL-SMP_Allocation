"""Portfolio rebalancing helpers for AQRL."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from math import isfinite
from types import MappingProxyType

from .constraints import (
    PortfolioConstraints,
    PortfolioConstraintViolation,
    WeightMap,
    coerce_weights,
    normalize_weights,
)


@dataclass(frozen=True, slots=True)
class RebalancePlan:
    """Immutable output from a portfolio rebalance calculation."""

    current_weights: Mapping[str, float]
    target_weights: Mapping[str, float]
    trades: Mapping[str, float]
    turnover: float
    violations: tuple[PortfolioConstraintViolation, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(self, "current_weights", MappingProxyType(dict(self.current_weights)))
        object.__setattr__(self, "target_weights", MappingProxyType(dict(self.target_weights)))
        object.__setattr__(self, "trades", MappingProxyType(dict(self.trades)))
        if not isinstance(self.turnover, int | float):
            raise TypeError("turnover must be numeric.")
        if not isfinite(float(self.turnover)):
            raise ValueError("turnover must be finite.")
        if self.turnover < 0:
            raise ValueError("turnover must be non-negative.")
        object.__setattr__(self, "turnover", float(self.turnover))
        object.__setattr__(self, "violations", tuple(self.violations))

    @property
    def traded_assets(self) -> tuple[str, ...]:
        """Return assets with non-zero trades."""
        return tuple(asset for asset, trade in self.trades.items() if trade != 0.0)


class SimpleRebalancer:
    """Generate deterministic target-weight rebalance plans."""

    def rebalance(
        self,
        current_weights: WeightMap | None,
        desired_weights: WeightMap,
        *,
        constraints: PortfolioConstraints | None = None,
        tolerance: float = 0.0,
    ) -> RebalancePlan:
        """Normalize desired weights, validate constraints, and compute trades."""
        active_constraints = PortfolioConstraints() if constraints is None else constraints
        trade_tolerance = _validate_tolerance(tolerance)
        current = _coerce_optional_weights(current_weights)
        target = normalize_weights(
            desired_weights,
            net_exposure=active_constraints.net_exposure,
        )
        active_constraints.assert_valid(target)

        all_assets = tuple(sorted(set(current) | set(target)))
        complete_current = {asset: current.get(asset, 0.0) for asset in all_assets}
        complete_target = {asset: target.get(asset, 0.0) for asset in all_assets}
        trades = {
            asset: _apply_tolerance(
                complete_target[asset] - complete_current[asset],
                trade_tolerance,
            )
            for asset in all_assets
        }
        non_zero_trades = {asset: trade for asset, trade in trades.items() if trade != 0.0}
        turnover = sum(abs(trade) for trade in non_zero_trades.values())

        return RebalancePlan(
            current_weights=complete_current,
            target_weights=complete_target,
            trades=non_zero_trades,
            turnover=turnover,
        )


def _coerce_optional_weights(weights: WeightMap | None) -> dict[str, float]:
    """Coerce current weights while allowing an empty starting portfolio."""
    if weights is None:
        return {}
    if not weights:
        return {}
    return coerce_weights(weights)


def _validate_tolerance(tolerance: float) -> float:
    """Validate trade tolerance."""
    if not isinstance(tolerance, int | float):
        raise TypeError("tolerance must be numeric.")
    numeric_tolerance = float(tolerance)
    if not isfinite(numeric_tolerance):
        raise ValueError("tolerance must be finite.")
    if numeric_tolerance < 0:
        raise ValueError("tolerance must be non-negative.")
    return numeric_tolerance


def _apply_tolerance(value: float, tolerance: float) -> float:
    """Return zero for trades inside tolerance."""
    return 0.0 if abs(value) <= tolerance else float(value)


__all__ = ["RebalancePlan", "SimpleRebalancer"]
