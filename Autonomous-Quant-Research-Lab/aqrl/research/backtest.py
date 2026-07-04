"""Backtest engine MVP for AQRL research workflows."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

import pandas as pd

from aqrl.core.utils import ensure_mapping, normalize_name
from aqrl.risk import TRADING_DAYS_PER_YEAR, summarize_returns

from .strategies import SIGNAL_COLUMN


@dataclass(frozen=True, slots=True)
class BacktestConfig:
    """Configuration for a single-asset vectorized backtest."""

    initial_capital: float = 100_000.0
    transaction_cost: float = 0.0
    price_column: str = "close"
    signal_column: str = SIGNAL_COLUMN

    def __post_init__(self) -> None:
        if not isinstance(self.initial_capital, int | float):
            raise TypeError("initial_capital must be numeric.")
        if self.initial_capital <= 0:
            raise ValueError("initial_capital must be positive.")
        if not isinstance(self.transaction_cost, int | float):
            raise TypeError("transaction_cost must be numeric.")
        if self.transaction_cost < 0:
            raise ValueError("transaction_cost must be non-negative.")
        object.__setattr__(self, "initial_capital", float(self.initial_capital))
        object.__setattr__(self, "transaction_cost", float(self.transaction_cost))
        object.__setattr__(self, "price_column", normalize_name(self.price_column, "price_column"))
        object.__setattr__(
            self,
            "signal_column",
            normalize_name(self.signal_column, "signal_column"),
        )


@dataclass(frozen=True, slots=True)
class BacktestResult:
    """Result bundle returned by the backtest engine."""

    equity_curve: pd.DataFrame
    positions: pd.DataFrame
    trades: pd.DataFrame
    summary: Mapping[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.equity_curve, pd.DataFrame):
            raise TypeError("equity_curve must be a pandas DataFrame.")
        if not isinstance(self.positions, pd.DataFrame):
            raise TypeError("positions must be a pandas DataFrame.")
        if not isinstance(self.trades, pd.DataFrame):
            raise TypeError("trades must be a pandas DataFrame.")
        object.__setattr__(self, "equity_curve", self.equity_curve.copy(deep=True))
        object.__setattr__(self, "positions", self.positions.copy(deep=True))
        object.__setattr__(self, "trades", self.trades.copy(deep=True))
        object.__setattr__(
            self,
            "summary",
            MappingProxyType(ensure_mapping(self.summary, "summary")),
        )


class BacktestEngine:
    """Vectorized long/flat/short backtest engine."""

    def run(
        self,
        market_data: pd.DataFrame,
        signals: pd.DataFrame,
        *,
        initial_capital: float = 100_000.0,
        transaction_cost: float = 0.0,
        price_column: str = "close",
        signal_column: str = SIGNAL_COLUMN,
    ) -> BacktestResult:
        """Run a deterministic backtest from market data and strategy signals."""
        config = BacktestConfig(
            initial_capital=initial_capital,
            transaction_cost=transaction_cost,
            price_column=price_column,
            signal_column=signal_column,
        )
        return self.run_with_config(market_data, signals, config=config)

    def run_with_config(
        self,
        market_data: pd.DataFrame,
        signals: pd.DataFrame,
        *,
        config: BacktestConfig,
    ) -> BacktestResult:
        """Run a deterministic backtest from an explicit config."""
        prices = _price_series(market_data, config.price_column)
        target_position = _signal_series(signals, config.signal_column)
        frame = pd.concat(
            [prices.rename("price"), target_position.rename("target_position")],
            axis=1,
            join="inner",
        ).dropna()
        if frame.empty:
            raise ValueError("market_data and signals must overlap on at least one timestamp.")

        frame = frame.sort_index()
        frame["target_position"] = frame["target_position"].clip(lower=-1.0, upper=1.0)
        frame["returns"] = frame["price"].pct_change().fillna(0.0)
        frame["effective_position"] = frame["target_position"].shift(1).fillna(0.0)
        frame["turnover"] = (
            frame["target_position"].diff().abs().fillna(frame["target_position"].abs())
        )
        frame["gross_return"] = frame["effective_position"] * frame["returns"]
        frame["cost_return"] = frame["turnover"] * config.transaction_cost
        frame["strategy_return"] = frame["gross_return"] - frame["cost_return"]
        frame["equity"] = config.initial_capital * (1.0 + frame["strategy_return"]).cumprod()
        frame["running_peak"] = frame["equity"].cummax()
        frame["drawdown"] = frame["equity"] / frame["running_peak"] - 1.0

        equity_curve = frame[
            [
                "price",
                "returns",
                "target_position",
                "effective_position",
                "strategy_return",
                "equity",
                "drawdown",
            ]
        ].copy()
        positions = frame[["target_position", "effective_position", "turnover"]].copy()
        trades = _build_trades(frame, config)
        summary = _summary(frame, trades, config)
        return BacktestResult(
            equity_curve=equity_curve,
            positions=positions,
            trades=trades,
            summary=summary,
        )


def _price_series(market_data: pd.DataFrame, price_column: str) -> pd.Series:
    """Return a validated market price series."""
    if not isinstance(market_data, pd.DataFrame):
        raise TypeError("market_data must be a pandas DataFrame.")
    if market_data.empty:
        raise ValueError("market_data must contain at least one row.")
    if price_column not in market_data.columns:
        raise ValueError(f"price column missing from market data: {price_column}")
    prices = pd.to_numeric(market_data[price_column], errors="coerce")
    if prices.isna().any():
        raise ValueError(f"price column contains non-numeric values: {price_column}")
    if (prices <= 0).any():
        raise ValueError(f"price column contains non-positive values: {price_column}")
    return prices


def _signal_series(signals: pd.DataFrame, signal_column: str) -> pd.Series:
    """Return a validated strategy signal series."""
    if not isinstance(signals, pd.DataFrame):
        raise TypeError("signals must be a pandas DataFrame.")
    if signals.empty:
        raise ValueError("signals must contain at least one row.")
    if signal_column not in signals.columns:
        raise ValueError(f"signal column missing from signals: {signal_column}")
    signal = pd.to_numeric(signals[signal_column], errors="coerce")
    if signal.isna().any():
        raise ValueError(f"signal column contains non-numeric values: {signal_column}")
    return signal


def _build_trades(frame: pd.DataFrame, config: BacktestConfig) -> pd.DataFrame:
    """Build a trade ledger from target-position changes."""
    previous_position = frame["target_position"].shift(1).fillna(0.0)
    trade_mask = frame["turnover"] > 0
    trades = pd.DataFrame(
        {
            "timestamp": frame.index[trade_mask],
            "previous_position": previous_position[trade_mask].to_numpy(),
            "new_position": frame.loc[trade_mask, "target_position"].to_numpy(),
            "trade_size": (
                frame.loc[trade_mask, "target_position"] - previous_position[trade_mask]
            ).to_numpy(),
            "price": frame.loc[trade_mask, "price"].to_numpy(),
            "cost": (
                config.initial_capital * frame.loc[trade_mask, "turnover"] * config.transaction_cost
            ).to_numpy(),
        }
    )
    return trades.reset_index(drop=True)


def _summary(
    frame: pd.DataFrame,
    trades: pd.DataFrame,
    config: BacktestConfig,
) -> dict[str, float]:
    """Compute summary metrics for a completed backtest."""
    final_equity = float(frame["equity"].iloc[-1])
    risk_summary = summarize_returns(
        frame["strategy_return"],
        equity_curve=frame["equity"],
        periods_per_year=TRADING_DAYS_PER_YEAR,
    ).to_dict()
    return {
        "initial_capital": config.initial_capital,
        "final_equity": final_equity,
        "total_return": risk_summary["cumulative_return"],
        "max_drawdown": risk_summary["max_drawdown"],
        "trade_count": float(len(trades)),
        "turnover": float(frame["turnover"].sum()),
        "transaction_cost_paid": float(trades["cost"].sum()) if not trades.empty else 0.0,
        "annualized_return": risk_summary["annualized_return"],
        "annualized_volatility": risk_summary["annualized_volatility"],
        "value_at_risk": risk_summary["value_at_risk"],
        "conditional_value_at_risk": risk_summary["conditional_value_at_risk"],
        "sharpe": risk_summary["sharpe"],
        "sortino": risk_summary["sortino"],
    }


__all__ = [
    "BacktestConfig",
    "BacktestEngine",
    "BacktestResult",
    "TRADING_DAYS_PER_YEAR",
]
