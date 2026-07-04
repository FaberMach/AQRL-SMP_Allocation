"""Research layer primitives for AQRL."""

from .backtest import BacktestConfig, BacktestEngine, BacktestResult
from .reporting import BacktestArtifacts, BacktestReportWriter
from .strategies import (
    SIGNAL_COLUMN,
    BuyAndHoldStrategy,
    MovingAverageCrossoverStrategy,
    Strategy,
)

__all__ = [
    "SIGNAL_COLUMN",
    "BacktestConfig",
    "BacktestEngine",
    "BacktestResult",
    "BacktestArtifacts",
    "BacktestReportWriter",
    "BuyAndHoldStrategy",
    "MovingAverageCrossoverStrategy",
    "Strategy",
]
