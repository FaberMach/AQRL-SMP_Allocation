from __future__ import annotations

import shutil
from pathlib import Path

import generate_dashboard_data
import validate_project


ROOT = Path(__file__).resolve().parent


def copy_public_dashboard() -> None:
    public_dir = ROOT / "dashboard" / "public"
    docs_dir = ROOT / "docs"
    for filename in ["index.html", "app.js", "data.js"]:
        shutil.copy2(public_dir / filename, docs_dir / filename)


def copy_audit_exports() -> None:
    exports_dir = ROOT / "dashboard" / "exports"
    analysis_dir = ROOT / "analysis_outputs"
    copies = {
        "fx-rates.csv": "fx_rates_2026-06-01.csv",
        "market-prices.csv": "market_prices_audit.csv",
        "scenario-summary.csv": "scenario_summary.csv",
    }
    for source, target in copies.items():
        src = exports_dir / source
        if src.exists():
            shutil.copy2(src, analysis_dir / target)


def main() -> None:
    generate_dashboard_data.main()
    copy_audit_exports()
    copy_public_dashboard()
    validate_project.main()


if __name__ == "__main__":
    main()
