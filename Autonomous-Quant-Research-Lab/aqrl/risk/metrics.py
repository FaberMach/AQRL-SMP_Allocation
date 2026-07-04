"""Return analytics and risk metrics for AQRL."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252
type ReturnMethod = Literal["simple", "log"]


@dataclass(frozen=True, slots=True)
class RiskSummary:
    """Canonical summary of return-stream risk metrics."""

    observation_count: int
    cumulative_return: float
    annualized_return: float
    annualized_volatility: float
    max_drawdown: float
    value_at_risk: float
    conditional_value_at_risk: float
    sharpe: float
    sortino: float

    def __post_init__(self) -> None:
        if not isinstance(self.observation_count, int):
            raise TypeError("observation_count must be an integer.")
        if self.observation_count < 0:
            raise ValueError("observation_count must be non-negative.")

    def to_dict(self) -> dict[str, float]:
        """Serialize the summary to a flat metrics dictionary."""
        return {
            "observation_count": float(self.observation_count),
            "cumulative_return": self.cumulative_return,
            "annualized_return": self.annualized_return,
            "annualized_volatility": self.annualized_volatility,
            "max_drawdown": self.max_drawdown,
            "value_at_risk": self.value_at_risk,
            "conditional_value_at_risk": self.conditional_value_at_risk,
            "sharpe": self.sharpe,
            "sortino": self.sortino,
        }


def calculate_returns(
    values: pd.Series,
    *,
    method: ReturnMethod = "simple",
    dropna: bool = True,
) -> pd.Series:
    """Calculate simple or log returns from a positive value series."""
    value_series = _numeric_series(values, "values")
    if (value_series <= 0).any():
        raise ValueError("values must be strictly positive.")

    if method == "simple":
        returns = value_series.pct_change()
    elif method == "log":
        returns = pd.Series(
            np.log(value_series / value_series.shift(1)),
            index=value_series.index,
            name="returns",
        )
    else:
        raise ValueError("method must be 'simple' or 'log'.")

    if dropna:
        returns = returns.dropna()
    return returns.rename("returns")


def cumulative_return(returns: pd.Series) -> float:
    """Return the compounded cumulative return for a return stream."""
    clean = _return_series(returns)
    if clean.empty:
        return 0.0
    return float(np.expm1(np.log1p(clean).sum()))


def annualized_return(
    returns: pd.Series,
    *,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> float:
    """Return compounded annualized return."""
    clean = _return_series(returns)
    if clean.empty:
        return 0.0
    _validate_periods_per_year(periods_per_year)
    cumulative = cumulative_return(clean)
    if cumulative <= -1.0:
        return -1.0
    exponent = periods_per_year / len(clean)
    return float((1.0 + cumulative) ** exponent - 1.0)


def annualized_volatility(
    returns: pd.Series,
    *,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> float:
    """Return annualized population volatility."""
    clean = _return_series(returns)
    if clean.empty:
        return 0.0
    _validate_periods_per_year(periods_per_year)
    return float(clean.std(ddof=0) * np.sqrt(periods_per_year))


def drawdown_series(values: pd.Series) -> pd.Series:
    """Calculate drawdown from an equity or wealth series."""
    value_series = _numeric_series(values, "values")
    if value_series.empty:
        return value_series.rename("drawdown")
    if (value_series <= 0).any():
        raise ValueError("values must be strictly positive.")
    running_peak = value_series.cummax()
    return (value_series / running_peak - 1.0).rename("drawdown")


def max_drawdown(values: pd.Series) -> float:
    """Return the maximum drawdown for an equity or wealth series."""
    drawdowns = drawdown_series(values)
    if drawdowns.empty:
        return 0.0
    return float(drawdowns.min())


def value_at_risk(
    returns: pd.Series,
    *,
    confidence: float = 0.95,
) -> float:
    """Return historical VaR as the lower-tail return quantile."""
    clean = _return_series(returns)
    if clean.empty:
        return 0.0
    _validate_confidence(confidence)
    return float(clean.quantile(1.0 - confidence))


def conditional_value_at_risk(
    returns: pd.Series,
    *,
    confidence: float = 0.95,
) -> float:
    """Return historical CVaR as the mean of returns at or below VaR."""
    clean = _return_series(returns)
    if clean.empty:
        return 0.0
    threshold = value_at_risk(clean, confidence=confidence)
    tail = clean[clean <= threshold]
    if tail.empty:
        return threshold
    return float(tail.mean())


def sharpe_ratio(
    returns: pd.Series,
    *,
    risk_free_rate: float = 0.0,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> float:
    """Return annualized Sharpe ratio."""
    excess = _excess_returns(returns, risk_free_rate, periods_per_year)
    volatility = annualized_volatility(excess, periods_per_year=periods_per_year)
    if volatility == 0.0:
        return 0.0
    return float(excess.mean() * periods_per_year / volatility)


def sortino_ratio(
    returns: pd.Series,
    *,
    risk_free_rate: float = 0.0,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> float:
    """Return annualized Sortino ratio using downside volatility."""
    excess = _excess_returns(returns, risk_free_rate, periods_per_year)
    downside = excess[excess < 0.0]
    if downside.empty:
        return 0.0
    downside_volatility = float(downside.std(ddof=0) * np.sqrt(periods_per_year))
    if downside_volatility == 0.0:
        return 0.0
    return float(excess.mean() * periods_per_year / downside_volatility)


def summarize_returns(
    returns: pd.Series,
    *,
    equity_curve: pd.Series | None = None,
    risk_free_rate: float = 0.0,
    confidence: float = 0.95,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> RiskSummary:
    """Return the canonical risk summary for a return stream."""
    clean = _return_series(returns)
    _validate_periods_per_year(periods_per_year)
    _validate_confidence(confidence)

    if equity_curve is None:
        equity = (1.0 + clean).cumprod()
    else:
        equity = _numeric_series(equity_curve, "equity_curve")

    return RiskSummary(
        observation_count=len(clean),
        cumulative_return=cumulative_return(clean),
        annualized_return=annualized_return(clean, periods_per_year=periods_per_year),
        annualized_volatility=annualized_volatility(
            clean,
            periods_per_year=periods_per_year,
        ),
        max_drawdown=max_drawdown(equity) if not equity.empty else 0.0,
        value_at_risk=value_at_risk(clean, confidence=confidence),
        conditional_value_at_risk=conditional_value_at_risk(clean, confidence=confidence),
        sharpe=sharpe_ratio(
            clean,
            risk_free_rate=risk_free_rate,
            periods_per_year=periods_per_year,
        ),
        sortino=sortino_ratio(
            clean,
            risk_free_rate=risk_free_rate,
            periods_per_year=periods_per_year,
        ),
    )


def _numeric_series(values: pd.Series, field_name: str) -> pd.Series:
    """Validate and coerce a numeric Series."""
    if not isinstance(values, pd.Series):
        raise TypeError(f"{field_name} must be a pandas Series.")
    numeric = pd.to_numeric(values, errors="coerce")
    if numeric.isna().any():
        raise ValueError(f"{field_name} contains missing or non-numeric values.")
    return numeric.astype(float)


def _return_series(returns: pd.Series) -> pd.Series:
    """Validate a numeric return Series."""
    clean = _numeric_series(returns, "returns")
    if (clean <= -1.0).any():
        raise ValueError("returns must be greater than -100%.")
    return clean.dropna()


def _excess_returns(
    returns: pd.Series,
    risk_free_rate: float,
    periods_per_year: int,
) -> pd.Series:
    """Return periodic excess returns over an annual risk-free rate."""
    if not isinstance(risk_free_rate, int | float):
        raise TypeError("risk_free_rate must be numeric.")
    _validate_periods_per_year(periods_per_year)
    return _return_series(returns) - float(risk_free_rate) / periods_per_year


def _validate_periods_per_year(periods_per_year: int) -> None:
    """Validate annualization frequency."""
    if not isinstance(periods_per_year, int):
        raise TypeError("periods_per_year must be an integer.")
    if periods_per_year <= 0:
        raise ValueError("periods_per_year must be positive.")


def _validate_confidence(confidence: float) -> None:
    """Validate a probability confidence level."""
    if not isinstance(confidence, int | float):
        raise TypeError("confidence must be numeric.")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be between 0 and 1.")


__all__ = [
    "TRADING_DAYS_PER_YEAR",
    "ReturnMethod",
    "RiskSummary",
    "annualized_return",
    "annualized_volatility",
    "calculate_returns",
    "conditional_value_at_risk",
    "cumulative_return",
    "drawdown_series",
    "max_drawdown",
    "sharpe_ratio",
    "sortino_ratio",
    "summarize_returns",
    "value_at_risk",
]
