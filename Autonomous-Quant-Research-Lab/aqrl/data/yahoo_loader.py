"""Yahoo Finance market data loader for AQRL."""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import UTC, date, datetime
from typing import Any
from urllib.error import URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

import pandas as pd

from aqrl.core.exceptions import AQRLDataError
from aqrl.core.utils import ensure_mapping, normalize_name

from .base_loader import BaseLoader, LoadRequest, TimePoint
from .cache import DataCache


class YahooFinanceLoader(BaseLoader):
    """Load historical price data from Yahoo Finance's chart endpoint."""

    def __init__(
        self,
        *,
        cache: DataCache | None = None,
        timeout: float = 10.0,
        user_agent: str = "AQRL/0.1.0",
    ) -> None:
        self._cache = cache
        self._timeout = timeout
        self._user_agent = user_agent

    def _load(self, request: LoadRequest) -> pd.DataFrame:
        cache_key = self._cache_key("yahoo", request)
        if self._cache is not None and self._cache.exists(cache_key):
            cached = self._cache.get(cache_key)
            if isinstance(cached, pd.DataFrame):
                return cached.copy(deep=True)

        payload = self._fetch_chart_payload(request)
        frame = self._parse_chart_payload(payload, request)

        if self._cache is not None:
            self._cache.set(cache_key, frame.copy(deep=True))

        return frame

    def _fetch_chart_payload(self, request: LoadRequest) -> Mapping[str, Any]:
        """Fetch the raw Yahoo Finance JSON payload."""
        url = self.build_url(
            request.symbol,
            start=request.start,
            end=request.end,
            interval=request.interval,
        )
        http_request = Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": self._user_agent,
            },
        )
        try:
            with urlopen(http_request, timeout=self._timeout) as response:
                raw_payload = response.read()
        except URLError as exc:
            raise AQRLDataError(
                f"Failed to fetch Yahoo Finance data for {request.symbol}."
            ) from exc

        try:
            parsed = json.loads(raw_payload.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise AQRLDataError("Yahoo Finance response was not valid JSON.") from exc

        return ensure_mapping(parsed, "payload")

    def build_url(
        self,
        symbol: str,
        *,
        start: TimePoint | None = None,
        end: TimePoint | None = None,
        interval: str = "1d",
    ) -> str:
        """Build the Yahoo chart URL for a symbol and optional time window."""
        normalized_symbol = normalize_name(symbol, "symbol")
        params: dict[str, str] = {
            "interval": normalize_name(interval, "interval").lower(),
            "events": "div,splits",
            "includePrePost": "false",
        }
        if start is not None:
            params["period1"] = str(_to_epoch_seconds(start))
        if end is not None:
            params["period2"] = str(_to_epoch_seconds(end))
        query = urlencode(params)
        symbol_path = quote(normalized_symbol, safe="")
        return f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol_path}?{query}"

    def _parse_chart_payload(
        self, payload: Mapping[str, Any], request: LoadRequest
    ) -> pd.DataFrame:
        """Parse a Yahoo chart payload into a price DataFrame."""
        chart = ensure_mapping(payload.get("chart"), "chart")
        result = chart.get("result")
        if not isinstance(result, list) or not result:
            raise AQRLDataError("Yahoo Finance payload did not contain a result series.")

        series = ensure_mapping(result[0], "result[0]")
        timestamps = series.get("timestamp")
        if not isinstance(timestamps, list) or not timestamps:
            raise AQRLDataError("Yahoo Finance payload did not contain timestamps.")

        indicators = ensure_mapping(series.get("indicators"), "indicators")
        quotes = indicators.get("quote")
        if not isinstance(quotes, list) or not quotes:
            raise AQRLDataError("Yahoo Finance payload did not contain price quotes.")
        quote = ensure_mapping(quotes[0], "quote[0]")

        frame = pd.DataFrame(
            {
                "open": _align_series(quote.get("open"), len(timestamps), "open"),
                "high": _align_series(quote.get("high"), len(timestamps), "high"),
                "low": _align_series(quote.get("low"), len(timestamps), "low"),
                "close": _align_series(quote.get("close"), len(timestamps), "close"),
                "volume": _align_series(quote.get("volume"), len(timestamps), "volume"),
            },
            index=pd.to_datetime(timestamps, unit="s", utc=True),
        )
        frame.index.name = "timestamp"

        adjclose = indicators.get("adjclose")
        if isinstance(adjclose, list) and adjclose:
            adjclose_quote = ensure_mapping(adjclose[0], "adjclose[0]")
            if "adjclose" in adjclose_quote:
                frame["adj_close"] = _align_series(
                    adjclose_quote.get("adjclose"), len(timestamps), "adjclose"
                )
                if request.adjusted:
                    frame["raw_close"] = frame["close"]
                    frame["close"] = frame["adj_close"]

        meta = ensure_mapping(series.get("meta", {}), "meta")
        frame.attrs.update(
            {
                "adjusted": request.adjusted,
                "interval": request.interval,
                "source": "yahoo",
                "symbol": meta.get("symbol", request.symbol),
            }
        )
        return frame


def _align_series(values: Any, length: int, field_name: str) -> list[Any]:
    """Align a JSON series to the expected payload length."""
    if values is None:
        return [None] * length
    if not isinstance(values, list):
        raise AQRLDataError(f"Yahoo Finance field {field_name} must be a list or null.")
    if len(values) != length:
        raise AQRLDataError(f"Yahoo Finance field {field_name} length must match timestamps.")
    return list(values)


def _to_epoch_seconds(value: TimePoint) -> int:
    """Convert a supported time point into epoch seconds."""
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("datetime values must be timezone-aware.")
        return int(value.timestamp())
    if isinstance(value, date):
        return int(datetime(value.year, value.month, value.day, tzinfo=UTC).timestamp())
    if isinstance(value, str):
        parsed = pd.Timestamp(value)
        parsed = parsed.tz_localize(UTC) if parsed.tzinfo is None else parsed.tz_convert(UTC)
        return int(parsed.timestamp())
    raise TypeError("time points must be date, datetime, or string values.")


__all__ = ["YahooFinanceLoader"]
