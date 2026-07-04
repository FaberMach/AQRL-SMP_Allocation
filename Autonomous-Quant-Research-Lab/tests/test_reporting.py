import json
from pathlib import Path

import pandas as pd

from aqrl.research import BacktestEngine, BacktestReportWriter, BuyAndHoldStrategy


def test_backtest_report_writer_exports_artifact_bundle(tmp_path: Path) -> None:
    market_data = pd.DataFrame(
        {"close": [100.0, 101.0, 102.0]},
        index=pd.date_range("2026-01-01", periods=3, tz="UTC"),
    )
    signals = BuyAndHoldStrategy().generate_signals(market_data)
    result = BacktestEngine().run(market_data, signals, initial_capital=1_000)

    artifacts = BacktestReportWriter(tmp_path).write(result, run_name="demo")

    assert artifacts.summary_json.exists()
    assert artifacts.equity_curve_csv.exists()
    assert artifacts.positions_csv.exists()
    assert artifacts.trades_csv.exists()
    assert artifacts.report_markdown.exists()
    assert artifacts.report_html.exists()
    assert artifacts.manifest_json.exists()

    summary = json.loads(artifacts.summary_json.read_text(encoding="utf-8"))
    manifest = json.loads(artifacts.manifest_json.read_text(encoding="utf-8"))

    assert summary["final_equity"] > 0
    assert "AQRL Backtest Report" in artifacts.report_markdown.read_text(encoding="utf-8")
    assert manifest["root"].endswith("demo")
