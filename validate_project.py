from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def read_csv(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_money(value: str | None) -> float:
    cleaned = (value or "").replace(",", "").strip()
    return float(cleaned) if cleaned else 0.0


def load_dashboard_data() -> dict:
    text = (ROOT / "dashboard" / "data.js").read_text(encoding="utf-8")
    prefix = "window.PORTFOLIO_DATA = "
    if not text.startswith(prefix):
        raise AssertionError("dashboard/data.js does not expose window.PORTFOLIO_DATA")
    return json.loads(text[len(prefix) :].rstrip(";\n"))


def main() -> None:
    rebalance = read_csv("analysis_outputs/rebalance_proposal.csv")
    holdings = read_csv("analysis_outputs/ibkr_holdings_analysis.csv")
    watchlist = read_csv("analysis_outputs/watchlist_analysis.csv")
    dashboard = load_dashboard_data()

    target_weight = sum(parse_money(row["target_weight_pct"]) for row in rebalance)
    if round(target_weight, 6) != 100:
        raise AssertionError(f"target weights must sum to 100, got {target_weight}")

    cash = next(row for row in rebalance if row["asset"] == "Cash")
    if parse_money(cash["target_weight_pct"]) < 5:
        raise AssertionError("cash target must be at least 5%")

    move_assets = {row["asset"] for row in rebalance}
    dashboard_assets = {row["asset"] for row in dashboard["moves"]}
    missing = move_assets - dashboard_assets
    if missing:
        raise AssertionError(f"dashboard is missing rebalance assets: {sorted(missing)}")

    economic_holdings = [
        row for row in holdings
        if parse_money(row.get("market_value_usd") or row.get("market_value_usd_if_usd")) > 0
        or row["symbol"] in {"ICG", "HYMC", "NTDOY", "USGDF"}
    ]
    dashboard_holding_symbols = {row["symbol"] for row in dashboard.get("holdings", [])}
    dashboard_residual_symbols = {row["symbol"] for row in dashboard.get("residuals", [])}
    missing_holdings = {row["symbol"] for row in economic_holdings} - dashboard_holding_symbols - dashboard_residual_symbols
    if missing_holdings:
        raise AssertionError(f"dashboard is missing economic holdings: {sorted(missing_holdings)}")

    if len(dashboard["watchlist"]) != len(watchlist):
        raise AssertionError("dashboard watchlist count differs from CSV")

    print(
        json.dumps(
            {
                "status": "ok",
                "target_weight_pct": target_weight,
                "cash_target_pct": parse_money(cash["target_weight_pct"]),
                "moves": len(rebalance),
                "holdings": len(dashboard.get("holdings", [])),
                "residuals": len(dashboard.get("residuals", [])),
                "watchlist": len(watchlist),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
