"""Backtest reporting and artifact export helpers for AQRL."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aqrl.core.utils import normalize_name

from .backtest import BacktestResult


@dataclass(frozen=True, slots=True)
class BacktestArtifacts:
    """Paths written for a backtest report export."""

    root: Path
    summary_json: Path
    equity_curve_csv: Path
    positions_csv: Path
    trades_csv: Path
    report_markdown: Path
    report_html: Path
    manifest_json: Path

    def to_dict(self) -> dict[str, str]:
        """Serialize artifact paths to strings."""
        return {
            "root": str(self.root),
            "summary_json": str(self.summary_json),
            "equity_curve_csv": str(self.equity_curve_csv),
            "positions_csv": str(self.positions_csv),
            "trades_csv": str(self.trades_csv),
            "report_markdown": str(self.report_markdown),
            "report_html": str(self.report_html),
            "manifest_json": str(self.manifest_json),
        }


class BacktestReportWriter:
    """Write a complete backtest artifact bundle."""

    def __init__(self, root: Path | str = Path("artifacts/backtests")) -> None:
        self.root = Path(root).expanduser()

    def write(self, result: BacktestResult, *, run_name: str = "latest") -> BacktestArtifacts:
        """Write summary, CSVs, Markdown, HTML, and manifest files."""
        if not isinstance(result, BacktestResult):
            raise TypeError("result must be a BacktestResult.")
        run_id = _safe_run_name(run_name)
        run_root = self.root / run_id
        run_root.mkdir(parents=True, exist_ok=True)

        artifacts = BacktestArtifacts(
            root=run_root,
            summary_json=run_root / "summary.json",
            equity_curve_csv=run_root / "equity_curve.csv",
            positions_csv=run_root / "positions.csv",
            trades_csv=run_root / "trades.csv",
            report_markdown=run_root / "report.md",
            report_html=run_root / "report.html",
            manifest_json=run_root / "manifest.json",
        )

        artifacts.summary_json.write_text(
            json.dumps(_json_safe_mapping(result.summary), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        result.equity_curve.to_csv(artifacts.equity_curve_csv)
        result.positions.to_csv(artifacts.positions_csv)
        result.trades.to_csv(artifacts.trades_csv, index=False)
        markdown = render_backtest_markdown(result, title=f"AQRL Backtest Report: {run_id}")
        artifacts.report_markdown.write_text(markdown, encoding="utf-8")
        artifacts.report_html.write_text(render_backtest_html(markdown), encoding="utf-8")
        artifacts.manifest_json.write_text(
            json.dumps(artifacts.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return artifacts


def render_backtest_markdown(
    result: BacktestResult,
    *,
    title: str = "AQRL Backtest Report",
) -> str:
    """Render a compact Markdown backtest report."""
    if not isinstance(result, BacktestResult):
        raise TypeError("result must be a BacktestResult.")
    lines = [
        f"# {title}",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in sorted(result.summary.items()):
        lines.append(f"| {key} | {_format_metric(value)} |")
    lines.extend(
        [
            "",
            "## Dataset Shapes",
            "",
            f"- Equity curve rows: {len(result.equity_curve)}",
            f"- Position rows: {len(result.positions)}",
            f"- Trade rows: {len(result.trades)}",
        ]
    )
    return "\n".join(lines) + "\n"


def render_backtest_html(markdown: str) -> str:
    """Render a small standalone HTML report from Markdown text."""
    escaped = markdown.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AQRL Backtest Report</title>
  <style>
    body {{
      margin: 0;
      padding: 40px;
      font-family: Georgia, "Times New Roman", serif;
      background: #f8f0df;
      color: #17201c;
    }}
    main {{
      max-width: 960px;
      margin: auto;
      background: #fffaf0;
      border: 1px solid #decfb8;
      border-radius: 24px;
      padding: 28px;
      box-shadow: 0 18px 50px rgba(49, 37, 18, 0.12);
    }}
    pre {{ white-space: pre-wrap; line-height: 1.55; }}
  </style>
</head>
<body>
  <main>
    <pre>{escaped}</pre>
  </main>
</body>
</html>
"""


def _safe_run_name(run_name: str) -> str:
    """Normalize a filesystem-safe run name."""
    normalized = normalize_name(run_name, "run_name")
    if normalized in {".", ".."} or "/" in normalized or "\\" in normalized:
        raise ValueError("run_name must be a single path segment.")
    return normalized


def _json_safe_mapping(mapping: Mapping[str, Any]) -> dict[str, float]:
    """Convert numeric summary values into JSON-safe floats."""
    return {str(key): float(value) for key, value in mapping.items()}


def _format_metric(value: Any) -> str:
    """Format a metric value for Markdown."""
    if isinstance(value, int | float):
        return f"{float(value):.6f}"
    return str(value)


__all__ = [
    "BacktestArtifacts",
    "BacktestReportWriter",
    "render_backtest_html",
    "render_backtest_markdown",
]
