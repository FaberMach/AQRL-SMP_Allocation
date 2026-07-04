"""Local client view for interacting with AQRL model primitives."""

from __future__ import annotations

import json
import webbrowser
from argparse import ArgumentParser, Namespace
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Literal, cast
from urllib.parse import parse_qs, urlparse

import pandas as pd

from aqrl.features import (
    FeatureConfig,
    RegimeConfig,
    build_market_features,
    classify_market_regimes,
)
from aqrl.portfolio import PortfolioConstraints, SimpleRebalancer
from aqrl.research import BacktestEngine, BuyAndHoldStrategy, MovingAverageCrossoverStrategy

StrategyName = Literal["buy_and_hold", "moving_average_crossover"]
DEFAULT_STRATEGY: StrategyName = "moving_average_crossover"
DEFAULT_SHORT_WINDOW = 3
DEFAULT_LONG_WINDOW = 8
DEFAULT_INITIAL_CAPITAL = 100_000.0
DEFAULT_TRANSACTION_COST = 0.001
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


@dataclass(frozen=True, slots=True)
class DemoModelConfig:
    """Configuration accepted by the local demo model endpoint."""

    strategy: StrategyName = DEFAULT_STRATEGY
    short_window: int = DEFAULT_SHORT_WINDOW
    long_window: int = DEFAULT_LONG_WINDOW
    initial_capital: float = DEFAULT_INITIAL_CAPITAL
    transaction_cost: float = DEFAULT_TRANSACTION_COST

    def __post_init__(self) -> None:
        if self.strategy not in {"buy_and_hold", "moving_average_crossover"}:
            raise ValueError("strategy must be buy_and_hold or moving_average_crossover.")
        if not isinstance(self.short_window, int) or not isinstance(self.long_window, int):
            raise TypeError("window values must be integers.")
        if self.short_window <= 0 or self.long_window <= 0:
            raise ValueError("window values must be positive.")
        if self.strategy == "moving_average_crossover" and self.short_window >= self.long_window:
            raise ValueError("short_window must be smaller than long_window.")
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

    @classmethod
    def from_query(cls, query: Mapping[str, Sequence[str]]) -> DemoModelConfig:
        """Build config from HTTP query parameters."""
        raw_strategy = _query_str(query, "strategy", DEFAULT_STRATEGY)
        if raw_strategy not in {"buy_and_hold", "moving_average_crossover"}:
            raise ValueError("strategy must be buy_and_hold or moving_average_crossover.")
        strategy = cast(StrategyName, raw_strategy)
        return cls(
            strategy=strategy,
            short_window=_query_int(query, "short_window", DEFAULT_SHORT_WINDOW),
            long_window=_query_int(query, "long_window", DEFAULT_LONG_WINDOW),
            initial_capital=_query_float(query, "initial_capital", DEFAULT_INITIAL_CAPITAL),
            transaction_cost=_query_float(query, "transaction_cost", DEFAULT_TRANSACTION_COST),
        )


def run_demo_model(config: DemoModelConfig | None = None) -> dict[str, Any]:
    """Run a deterministic local AQRL model flow for the client view."""
    active_config = DemoModelConfig() if config is None else config
    market_data = _demo_market_data()
    strategy = (
        BuyAndHoldStrategy()
        if active_config.strategy == "buy_and_hold"
        else MovingAverageCrossoverStrategy(
            short_window=active_config.short_window,
            long_window=active_config.long_window,
        )
    )
    signals = strategy.fit(market_data).generate_signals(market_data)
    result = BacktestEngine().run(
        market_data,
        signals,
        initial_capital=active_config.initial_capital,
        transaction_cost=active_config.transaction_cost,
    )
    features = build_market_features(
        market_data,
        config=FeatureConfig(momentum_window=active_config.short_window),
    )
    regimes = classify_market_regimes(
        features,
        config=RegimeConfig(momentum_threshold=0.005),
    )
    latest_trend = str(regimes["trend_regime"].iloc[-1])
    desired_weights = (
        {"AAPL": 0.7, "MSFT": 0.3} if latest_trend == "bull" else {"AAPL": 0.4, "MSFT": 0.6}
    )
    rebalance_plan = SimpleRebalancer().rebalance(
        {"AAPL": 0.5, "MSFT": 0.5},
        desired_weights,
        constraints=PortfolioConstraints(max_weight=0.8),
    )

    return {
        "config": {
            "strategy": active_config.strategy,
            "short_window": active_config.short_window,
            "long_window": active_config.long_window,
            "initial_capital": active_config.initial_capital,
            "transaction_cost": active_config.transaction_cost,
        },
        "summary": dict(result.summary),
        "latest_regime": _last_record(regimes),
        "latest_features": _last_record(features),
        "rebalance": {
            "target_weights": dict(rebalance_plan.target_weights),
            "trades": dict(rebalance_plan.trades),
            "turnover": rebalance_plan.turnover,
        },
        "equity_curve": _frame_records(result.equity_curve.tail(20)),
        "signals": _frame_records(signals.tail(20)),
    }


def create_client_view_server(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
) -> ThreadingHTTPServer:
    """Create the local AQRL client-view HTTP server."""
    return ThreadingHTTPServer((host, port), ClientViewHandler)


def serve_client_view(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    *,
    open_browser: bool = False,
) -> None:
    """Serve the local AQRL client view."""
    server = create_client_view_server(host=host, port=port)
    url = f"http://{host}:{port}"
    print(f"AQRL client view listening at {url}")
    print(f"Health check: {url}/health")
    print("Press Ctrl+C to stop.")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    finally:
        server.server_close()


class ClientViewHandler(BaseHTTPRequestHandler):
    """HTTP handler serving the AQRL client view and JSON endpoint."""

    def do_GET(self) -> None:  # noqa: N802
        """Serve the client page or demo-model JSON payload."""
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send_html(CLIENT_VIEW_HTML)
            return
        if parsed.path in {"/health", "/api/health"}:
            self._send_json({"status": "ok", "service": "aqrl-client-view"}, status=HTTPStatus.OK)
            return
        if parsed.path == "/api/demo":
            self._send_demo_response(parse_qs(parsed.query))
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def log_message(self, format: str, *args: object) -> None:
        """Silence default HTTP access logs for a quieter local client."""

    def _send_demo_response(self, query: Mapping[str, Sequence[str]]) -> None:
        """Send a JSON demo-model response or validation error."""
        try:
            payload = run_demo_model(DemoModelConfig.from_query(query))
            status = HTTPStatus.OK
        except (TypeError, ValueError) as exc:
            payload = {"error": str(exc)}
            status = HTTPStatus.BAD_REQUEST
        self._send_json(payload, status=status)

    def _send_html(self, html: str) -> None:
        """Send an HTML response."""
        encoded = html.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_json(self, payload: Mapping[str, Any], *, status: HTTPStatus) -> None:
        """Send a JSON response."""
        encoded = json.dumps(payload, ensure_ascii=False, indent=2, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def _demo_market_data() -> pd.DataFrame:
    """Build deterministic demo prices for the local client view."""
    closes = [
        100.0,
        101.2,
        100.8,
        102.5,
        103.7,
        104.1,
        103.3,
        105.8,
        107.2,
        108.5,
        107.9,
        109.6,
        111.4,
        112.8,
        111.9,
        113.7,
        115.1,
        116.5,
        118.0,
        117.2,
        119.8,
        121.4,
        122.6,
        124.1,
    ]
    return pd.DataFrame(
        {"close": closes},
        index=pd.date_range("2026-01-01", periods=len(closes), tz="UTC", name="timestamp"),
    )


def _frame_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    """Convert a DataFrame into JSON-friendly records with timestamp values."""
    prepared = frame.copy()
    prepared.insert(0, "timestamp", [str(value) for value in prepared.index])
    return [
        {str(key): _json_value(value) for key, value in record.items()}
        for record in prepared.to_dict(orient="records")
    ]


def _last_record(frame: pd.DataFrame) -> dict[str, Any]:
    """Return the last row of a DataFrame as a JSON-friendly record."""
    record = frame.tail(1).to_dict(orient="records")[0]
    return {str(key): _json_value(value) for key, value in record.items()}


def _json_value(value: Any) -> Any:
    """Convert common pandas/numpy scalar values into JSON-safe primitives."""
    if hasattr(value, "item"):
        return value.item()
    return value


def _query_str(query: Mapping[str, Sequence[str]], key: str, default: str) -> str:
    """Return a string query parameter."""
    values = query.get(key)
    if not values:
        return default
    return str(values[0])


def _query_int(query: Mapping[str, Sequence[str]], key: str, default: int) -> int:
    """Return an integer query parameter."""
    values = query.get(key)
    if not values:
        return default
    return int(values[0])


def _query_float(query: Mapping[str, Sequence[str]], key: str, default: float) -> float:
    """Return a float query parameter."""
    values = query.get(key)
    if not values:
        return default
    return float(values[0])


CLIENT_VIEW_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AQRL Client View</title>
  <style>
    :root {
      --bg: #f4efe4;
      --ink: #17201c;
      --muted: #607064;
      --panel: #fffaf0;
      --accent: #b3471f;
      --accent-2: #1d6f5f;
      --line: #decfb8;
      --danger: #8f1d1d;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(179, 71, 31, 0.18), transparent 32rem),
        linear-gradient(135deg, #f8f0df, var(--bg));
    }
    main { max-width: 1120px; margin: 0 auto; padding: 48px 20px; }
    .hero {
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 24px;
      align-items: stretch;
    }
    h1 { font-size: clamp(2.4rem, 6vw, 5.4rem); line-height: 0.92; margin: 0; }
    .kicker {
      color: var(--accent);
      font-weight: 700;
      letter-spacing: 0.12em;
      text-transform: uppercase;
    }
    .panel {
      background: rgba(255, 250, 240, 0.88);
      border: 1px solid var(--line);
      box-shadow: 0 18px 50px rgba(49, 37, 18, 0.12);
      border-radius: 28px;
      padding: 24px;
    }
    form { display: grid; gap: 14px; }
    label { display: grid; gap: 6px; color: var(--muted); font-size: 0.9rem; }
    input, select, button {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 12px 14px;
      font: inherit;
      background: #fffdf7;
      color: var(--ink);
    }
    button, .button {
      cursor: pointer;
      color: #fffaf0;
      border: 0;
      background: linear-gradient(135deg, var(--accent), var(--accent-2));
      font-weight: 700;
      text-align: center;
      text-decoration: none;
    }
    .button.secondary { background: #17201c; }
    .actions { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-top: 24px;
    }
    .metric { min-height: 116px; }
    .metric small { color: var(--muted); display: block; }
    .metric strong { display: block; margin-top: 10px; font-size: 1.55rem; }
    pre {
      overflow: auto;
      max-height: 360px;
      background: #18221d;
      color: #f8f0df;
      border-radius: 20px;
      padding: 18px;
    }
    canvas {
      width: 100%;
      height: 260px;
      background: #fffdf7;
      border: 1px solid var(--line);
      border-radius: 20px;
    }
    .status { color: var(--muted); margin-top: 14px; }
    .status.error { color: var(--danger); }
    @media (max-width: 820px) {
      .hero, .grid, .actions { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <div class="panel">
        <p class="kicker">AQRL Local Model Client</p>
        <h1>Ask the lab what this market wants to be.</h1>
        <p>
          Tune a baseline strategy, run the local AQRL backtest/risk/regime pipeline,
          and inspect the model payload without leaving your machine.
        </p>
      </div>
      <form class="panel" id="controls">
        <label>Strategy
          <select name="strategy">
            <option value="moving_average_crossover">Moving average crossover</option>
            <option value="buy_and_hold">Buy and hold</option>
          </select>
        </label>
        <label>Short window <input name="short_window" type="number" min="1" value="3" /></label>
        <label>Long window <input name="long_window" type="number" min="2" value="8" /></label>
        <label>Initial capital
          <input name="initial_capital" type="number" min="1" value="100000" />
        </label>
        <label>Transaction cost
          <input name="transaction_cost" type="number" min="0" step="0.0001" value="0.001" />
        </label>
        <div class="actions">
          <button type="submit">Run AQRL model</button>
          <a class="button secondary" id="download" href="#" download="aqrl-demo-payload.json">
            Download JSON
          </a>
        </div>
        <p class="status" id="status">Checking local model endpoint...</p>
      </form>
    </section>
    <section class="grid" id="metrics"></section>
    <section class="panel" style="margin-top: 24px;">
      <h2>Equity Curve</h2>
      <canvas id="equityChart" width="980" height="260"></canvas>
    </section>
    <section class="panel" style="margin-top: 24px;">
      <h2>Model Payload</h2>
      <pre id="payload">Run the model to see JSON output.</pre>
    </section>
  </main>
  <script>
    const form = document.querySelector("#controls");
    const metrics = document.querySelector("#metrics");
    const payload = document.querySelector("#payload");
    const status = document.querySelector("#status");
    const download = document.querySelector("#download");
    const canvas = document.querySelector("#equityChart");
    const ctx = canvas.getContext("2d");

    const fmt = new Intl.NumberFormat("en-US", { maximumFractionDigits: 4 });
    function metric(label, value) {
      return `<article class="panel metric">
        <small>${label}</small><strong>${value}</strong>
      </article>`;
    }
    function drawEquityCurve(points) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      if (!points?.length) return;
      const values = points.map((point) => Number(point.equity));
      const min = Math.min(...values);
      const max = Math.max(...values);
      const span = Math.max(max - min, 1);
      ctx.strokeStyle = "#1d6f5f";
      ctx.lineWidth = 4;
      ctx.beginPath();
      values.forEach((value, index) => {
        const x = 28 + (index / Math.max(values.length - 1, 1)) * (canvas.width - 56);
        const y = canvas.height - 28 - ((value - min) / span) * (canvas.height - 56);
        if (index === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();
      ctx.fillStyle = "#17201c";
      ctx.font = "16px Georgia";
      ctx.fillText(`Min $${fmt.format(min)} · Max $${fmt.format(max)}`, 28, 28);
    }
    async function runModel(event) {
      event?.preventDefault();
      const query = new URLSearchParams(new FormData(form));
      status.textContent = "Running local AQRL model...";
      status.classList.remove("error");
      let data;
      try {
        const response = await fetch(`/api/demo?${query}`);
        data = await response.json();
      } catch (error) {
        status.textContent = `Could not reach local model endpoint: ${error}`;
        status.classList.add("error");
        return;
      }
      payload.textContent = JSON.stringify(data, null, 2);
      download.href = URL.createObjectURL(
        new Blob([JSON.stringify(data, null, 2)], { type: "application/json" })
      );
      if (data.error) {
        metrics.innerHTML = metric("Error", data.error);
        status.textContent = data.error;
        status.classList.add("error");
        return;
      }
      status.textContent = "Local model endpoint is online.";
      metrics.innerHTML = [
        metric("Final Equity", `$${fmt.format(data.summary.final_equity)}`),
        metric("Total Return", fmt.format(data.summary.total_return)),
        metric("Sharpe", fmt.format(data.summary.sharpe)),
        metric("Regime", data.latest_regime.regime),
        metric("VaR", fmt.format(data.summary.value_at_risk)),
        metric("CVaR", fmt.format(data.summary.conditional_value_at_risk)),
        metric("Turnover", fmt.format(data.rebalance.turnover)),
        metric("Target AAPL", fmt.format(data.rebalance.target_weights.AAPL))
      ].join("");
      drawEquityCurve(data.equity_curve);
    }
    form.addEventListener("submit", runModel);
    runModel();
  </script>
</body>
</html>
"""


def main(argv: Sequence[str] | None = None) -> None:
    """CLI entry point for the local client view."""
    args = _parse_args(argv)
    serve_client_view(host=args.host, port=args.port, open_browser=args.open)


def _parse_args(argv: Sequence[str] | None = None) -> Namespace:
    """Parse command-line arguments for the client view."""
    parser = ArgumentParser(description="Serve the AQRL local client view.")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host interface to bind.")
    parser.add_argument("--port", default=DEFAULT_PORT, type=int, help="Port to bind.")
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the client view in the default browser after starting.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    main()


__all__ = [
    "CLIENT_VIEW_HTML",
    "ClientViewHandler",
    "DEFAULT_HOST",
    "DEFAULT_INITIAL_CAPITAL",
    "DEFAULT_LONG_WINDOW",
    "DEFAULT_PORT",
    "DEFAULT_SHORT_WINDOW",
    "DEFAULT_STRATEGY",
    "DEFAULT_TRANSACTION_COST",
    "DemoModelConfig",
    "StrategyName",
    "create_client_view_server",
    "main",
    "run_demo_model",
    "serve_client_view",
]
