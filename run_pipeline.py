from __future__ import annotations

import shutil
from pathlib import Path

import generate_dashboard_data
import generate_reports
import prepare_public_site
import validate_project


ROOT = Path(__file__).resolve().parent


def copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def sync_public_assets() -> None:
    dashboard_dir = ROOT / "dashboard"
    public_dir = dashboard_dir / "public"
    docs_dir = ROOT / "docs"

    # Share the React runtime and styling across the local dashboard, public snapshot and docs.
    for filename in ["app.js", "styles.css"]:
        source = dashboard_dir / filename
        copy_file(source, public_dir / filename)
        copy_file(source, docs_dir / filename)

    # Keep the public snapshot as the published docs entrypoint.
    copy_file(public_dir / "index.html", docs_dir / "index.html")
    copy_file(public_dir / "data.js", docs_dir / "data.js")


def copy_audit_exports() -> None:
    exports_dir = ROOT / "dashboard" / "exports"
    analysis_dir = ROOT / "analysis_outputs"
    docs_exports_dir = ROOT / "docs" / "exports"
    docs_exports_dir.mkdir(parents=True, exist_ok=True)
    copies = {
        "fx-rates.csv": "fx_rates_2026-06-01.csv",
        "market-prices.csv": "market_prices_audit.csv",
        "scenario-summary.csv": "scenario_summary.csv",
    }
    for source, target in copies.items():
        src = exports_dir / source
        if src.exists():
            shutil.copy2(src, analysis_dir / target)

    for path in exports_dir.glob("*.csv"):
        shutil.copy2(path, docs_exports_dir / path.name)


def main() -> None:
    data = generate_dashboard_data.build_data(write_outputs=True)
    generate_reports.main(data)
    copy_audit_exports()
    sync_public_assets()
    prepare_public_site.main(data)
    validate_project.main()


if __name__ == "__main__":
    main()
