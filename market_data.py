from __future__ import annotations

import json
import ssl
import csv
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from io import StringIO
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


SSL_CONTEXT = ssl._create_unverified_context()


def normalize_currency(currency: str | None) -> tuple[str, float]:
    """Return a normalized currency code and a local price multiplier."""

    raw = (currency or "USD").strip()
    code = raw.upper()
    if not code or code == "USD":
        return "USD", 1.0
    if raw == "GBp" or code in {"GBX", "GBPX"}:
        return "GBP", 0.01
    return code, 1.0


def _unix(date_str: str) -> int:
    return int(datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc).timestamp())


def _stooq_symbol(yahoo_symbol: str) -> str | None:
    """Map simple US Yahoo tickers to Stooq symbols."""

    if not yahoo_symbol or "=" in yahoo_symbol or "." in yahoo_symbol:
        return None
    return f"{yahoo_symbol.lower().replace('-', '.')}.us"


def fetch_stooq_close(yahoo_symbol: str, date_str: str) -> dict:
    """Fetch the latest Stooq close on or before the requested date for US tickers."""

    symbol = _stooq_symbol(yahoo_symbol)
    normalized_date = datetime.fromisoformat(date_str).date()
    if not symbol:
        return {
            "symbol": yahoo_symbol,
            "close": None,
            "currency": None,
            "date": None,
            "url": "",
            "error": "stooq fallback skipped for non-US/FX symbol",
            "source": "stooq",
        }

    start = (normalized_date - timedelta(days=14)).strftime("%Y%m%d")
    end = normalized_date.strftime("%Y%m%d")
    url = f"https://stooq.com/q/d/l/?s={quote(symbol, safe='')}&d1={start}&d2={end}&i=d"
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(req, timeout=20, context=SSL_CONTEXT) as resp:
            text = resp.read().decode("utf-8")
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        return {
            "symbol": yahoo_symbol,
            "close": None,
            "currency": None,
            "date": None,
            "url": url,
            "error": str(exc),
            "source": "stooq",
        }

    best = None
    try:
        rows = csv.DictReader(StringIO(text))
        for row in rows:
            row_date = row.get("Date") or ""
            close = row.get("Close") or ""
            if not row_date or not close or row_date > normalized_date.isoformat():
                continue
            best = {
                "symbol": yahoo_symbol,
                "close": float(close),
                "currency": "USD",
                "date": row_date,
                "url": url,
                "error": "",
                "source": "stooq",
            }
    except (TypeError, ValueError) as exc:
        return {
            "symbol": yahoo_symbol,
            "close": None,
            "currency": None,
            "date": None,
            "url": url,
            "error": str(exc),
            "source": "stooq",
        }

    if best:
        return best
    return {
        "symbol": yahoo_symbol,
        "close": None,
        "currency": None,
        "date": None,
        "url": url,
        "error": "no stooq close returned",
        "source": "stooq",
    }


@lru_cache(maxsize=512)
def fetch_chart_close(yahoo_symbol: str, date_str: str) -> dict:
    """Fetch the latest daily close on or before the requested date."""

    normalized_date = datetime.fromisoformat(date_str).date().isoformat()
    p1 = _unix(normalized_date) - 14 * 86400
    p2 = _unix(normalized_date) + 3 * 86400
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        f"{quote(yahoo_symbol, safe='')}?period1={p1}&period2={p2}&interval=1d&events=history"
    )
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(req, timeout=20, context=SSL_CONTEXT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        fallback = fetch_stooq_close(yahoo_symbol, normalized_date)
        if fallback["close"] is not None:
            return fallback
        return {
            "symbol": yahoo_symbol,
            "close": None,
            "currency": None,
            "date": None,
            "url": url,
            "error": str(exc),
            "source": "yahoo",
        }

    result = (data.get("chart", {}).get("result") or [None])[0]
    if not result:
        err = data.get("chart", {}).get("error")
        return {
            "symbol": yahoo_symbol,
            "close": None,
            "currency": None,
            "date": None,
            "url": url,
            "error": str(err or "no result"),
            "source": "yahoo",
        }

    timestamps = result.get("timestamp") or []
    quote_data = ((result.get("indicators") or {}).get("quote") or [{}])[0]
    closes = quote_data.get("close") or []
    currency = result.get("meta", {}).get("currency")

    best = None
    for ts, close in zip(timestamps, closes):
        if close is None:
            continue
        dt = datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat()
        row = {
            "symbol": yahoo_symbol,
            "close": float(close),
            "currency": currency,
            "date": dt,
            "url": url,
            "error": "",
            "source": "yahoo",
        }
        if dt <= normalized_date:
            best = row
        elif best is None:
            best = row

    if best:
        return best

    fallback = fetch_stooq_close(yahoo_symbol, normalized_date)
    if fallback["close"] is not None:
        return fallback

    return {
        "symbol": yahoo_symbol,
        "close": None,
        "currency": currency,
        "date": None,
        "url": url,
        "error": "no close returned",
        "source": "yahoo",
    }


@lru_cache(maxsize=128)
def fetch_fx_rate(currency: str, date_str: str | None = None) -> dict:
    """Fetch a USD FX rate for the given currency."""

    normalized_currency, local_multiplier = normalize_currency(currency)
    if normalized_currency == "USD":
        return {
            "currency": "USD",
            "rate": 1.0,
            "pair": "USD",
            "date": date_str,
            "error": "",
            "multiplier": local_multiplier,
        }

    target_date = date_str or datetime.now(timezone.utc).date().isoformat()
    direct_symbol = f"{normalized_currency}USD=X"
    direct = fetch_chart_close(direct_symbol, target_date)
    if direct["close"] is not None:
        return {
            "currency": normalized_currency,
            "rate": float(direct["close"]),
            "pair": direct_symbol,
            "date": direct["date"],
            "error": "",
            "multiplier": local_multiplier,
        }

    inverse_symbol = f"USD{normalized_currency}=X"
    inverse = fetch_chart_close(inverse_symbol, target_date)
    if inverse["close"] is not None and float(inverse["close"]) != 0:
        return {
            "currency": normalized_currency,
            "rate": 1.0 / float(inverse["close"]),
            "pair": inverse_symbol,
            "date": inverse["date"],
            "error": "",
            "multiplier": local_multiplier,
        }

    return {
        "currency": normalized_currency,
        "rate": None,
        "pair": direct_symbol,
        "date": None,
        "error": direct["error"] or inverse["error"] or "fx unavailable",
        "multiplier": local_multiplier,
    }


def build_fx_rate_map(currencies: list[str], date_str: str | None = None) -> dict[str, dict]:
    """Resolve FX rates for a list of currencies, always including USD."""

    rates = {"USD": {"currency": "USD", "rate": 1.0, "pair": "USD", "date": date_str, "error": "", "multiplier": 1.0}}
    for currency in sorted({(currency or "USD").strip() for currency in currencies if currency}):
        normalized, multiplier = normalize_currency(currency)
        if normalized in rates:
            continue
        resolved = fetch_fx_rate(normalized, date_str)
        resolved["multiplier"] = multiplier
        rates[normalized] = resolved
    return rates


def price_to_usd(price: float | None, currency: str | None, fx_map: dict[str, dict] | None = None) -> float | None:
    if price is None:
        return None
    normalized, multiplier = normalize_currency(currency)
    fx_rate = 1.0
    if fx_map:
        fx_rate = float((fx_map.get(normalized) or {}).get("rate") or 0.0)
    if normalized != "USD" and fx_rate <= 0:
        return None
    return float(price) * multiplier * fx_rate
