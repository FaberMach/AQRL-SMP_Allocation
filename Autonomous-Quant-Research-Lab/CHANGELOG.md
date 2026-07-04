# Changelog

## [Unreleased]

### Added
- Backtest report artifact writer for summary JSON, CSV tables, Markdown, HTML, and manifests.
- Hardened AQRL client view with CLI arguments, health endpoints, equity chart, JSON download, and Windows launch script.
- Local dependency-free AQRL client view with browser UI and JSON model endpoint.
- Offline executable examples for data pipeline, strategy backtest, and risk/portfolio rebalance.
- Market feature engine for returns, rolling return, volatility, momentum, and drawdown.
- Simple market regime classifier for trend and volatility states.
- Portfolio constraints and deterministic rebalance plans.
- Return analytics and risk metrics for volatility, drawdown, VaR, CVaR, Sharpe, and Sortino.
- Deterministic strategy/backtest MVP with buy-and-hold and moving-average crossover baselines.
- Dataset registry, Parquet market-data persistence, DuckDB queries, and data-quality reports.
- Canonical Git workspace documentation, committed Poetry lock file, and CI-visible quality gates.
- Data layer primitives for loader abstraction, persistent cache, feature store, and Yahoo Finance loader.
- Shared core support primitives for constants, exceptions, type aliases, and reusable utilities.
- Canonical immutable MarketState model with prices, returns, volatility, and metadata.
- Simple in-process scheduler with task registration and execution.
- Plugin protocol and plugin manager for registration and initialization.
- Generic named registry with explicit duplicate and missing-entry errors.
- Synchronous event bus and immutable event model for core infrastructure.
- Structured AQRL logger factory with optional file output.
- Core configuration helpers with defaults, YAML loading, and environment overrides.

## [0.1.0] - 2026-06-29

### Added
- Initial AQRL repository bootstrap.
- Institutional project structure.
- README, roadmap, project bible, architecture specification, task backlog, and agent roles.
- Python packaging configuration with Poetry.
- Quality tooling baseline: ruff, black, mypy, pytest, pre-commit.
- GitHub Actions CI workflow.
