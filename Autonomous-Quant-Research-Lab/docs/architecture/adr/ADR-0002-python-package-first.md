# ADR-0002: Package-first Development

## Status
Accepted

## Context
Quant research often begins in notebooks, but production-quality platforms require reusable modules.

## Decision
AQRL will place all core logic in the `aqrl/` Python package. Notebooks and dashboards will import from the package.

## Consequences
- Better testing and maintainability.
- Easier transition from research to production.
- Reduced notebook-driven technical debt.
