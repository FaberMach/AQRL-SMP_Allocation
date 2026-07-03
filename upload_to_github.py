from __future__ import annotations

import base64
import json
import os
import ssl
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
REPO = os.environ.get("GITHUB_REPOSITORY", "FaberMach/AQRL-SMP_Allocation")
BRANCH = "main"
API = f"https://api.github.com/repos/{REPO}/contents"
SSL_CONTEXT = ssl._create_unverified_context()

FILES = [
    ".gitignore",
    "README.md",
    "market_data.py",
    "portfolio_rebalance_analysis.py",
    "generate_dashboard_data.py",
    "generate_reports.py",
    "validate_project.py",
    "run_pipeline.py",
    "prepare_public_site.py",
    "upload_public_site.py",
    "public_site/.github/workflows/pages.yml",
    "analysis_outputs/scenarios/convex.json",
    "analysis_outputs/scenarios/defensive.json",
    "analysis_outputs/scenarios/study.json",
    "analysis_outputs/fx_rates_2026-06-01.csv",
    "analysis_outputs/ibkr_holdings_analysis.csv",
    "analysis_outputs/market_prices_audit.csv",
    "analysis_outputs/prices_2026-06-01.csv",
    "analysis_outputs/rebalance_proposal.csv",
    "analysis_outputs/rebalance_report.md",
    "analysis_outputs/scenario_summary.csv",
    "analysis_outputs/ticker_aliases.csv",
    "analysis_outputs/watchlist_analysis.csv",
    "dashboard/app.js",
    "dashboard/data.js",
    "dashboard/exports/fx-rates.csv",
    "dashboard/exports/market-prices.csv",
    "dashboard/exports/scenario-convex.csv",
    "dashboard/exports/scenario-defensive.csv",
    "dashboard/exports/scenario-study.csv",
    "dashboard/exports/scenario-summary.csv",
    "dashboard/index.html",
    "dashboard/styles.css",
    "docs/MOBILE_ACCESS.md",
    "docs/PROJECT_REVIEW.md",
    "docs/REPOSITORY_SAVE_PLAN.md",
    "docs/EXECUTIVE_REPORT.md",
    "docs/app.js",
    "docs/data.js",
    "docs/executive_report.html",
    "docs/index.html",
    ".github/workflows/validate.yml",
]


def request(method: str, path: str, token: str, payload: dict | None = None) -> dict | None:
    url = f"{API}/{quote(path, safe='/')}?ref={BRANCH}" if method == "GET" else f"{API}/{quote(path, safe='/')}"
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(req, context=SSL_CONTEXT, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 404 and method == "GET":
            return None
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} failed: {exc.code} {body}") from exc


def upload_file(path: str, token: str) -> str:
    local = ROOT / path
    content = local.read_bytes()
    encoded = base64.b64encode(content).decode("ascii")
    existing = request("GET", path, token)
    payload = {
        "message": f"Update {path}" if existing else f"Add {path}",
        "content": encoded,
        "branch": BRANCH,
    }
    if existing:
        payload["sha"] = existing["sha"]
    result = request("PUT", path, token, payload)
    action = "updated" if existing else "created"
    commit = result["commit"]["sha"][:12] if result and "commit" in result else "unknown"
    return f"{action}: {path} ({commit})"


def main() -> None:
    token = os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("GH_TOKEN is required")
    for path in FILES:
        print(upload_file(path, token))


if __name__ == "__main__":
    main()
