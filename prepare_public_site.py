from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import generate_dashboard_data


ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
PUBLIC = ROOT / "public_site"


def scrub_payload(payload: dict) -> dict:
    payload = json.loads(json.dumps(payload))
    meta = payload.get("meta", {})
    meta.update(
        {
            "targetCapital": 100000.0,
            "currentPortfolioValue": 100000.0,
            "modelPortfolioValue": 100000.0,
            "residualValue": 0.0,
            "cashCurrent": 0.0,
            "liquidityCurrentValue": 0.0,
            "holdingsCount": 0,
            "watchlistCount": len(payload.get("study", {}).get("topIdeas", [])),
            "residualCount": 0,
            "publicSanitized": True,
            "notes": [
                "Versao publica normalizada: nao inclui valores reais, holdings, trades completos ou extratos.",
                "Mostra cenarios, temas, cobertura de precos e top ideias em escala-base de USD 100.000.",
            ],
        }
    )
    payload["meta"] = meta
    payload["moves"] = []
    payload["holdings"] = []
    payload["residuals"] = []
    payload["watchlist"] = []
    return payload


def main(data: dict | None = None) -> None:
    PUBLIC.mkdir(parents=True, exist_ok=True)

    for name in ["index.html", "app.js", "styles.css", "executive_report.html"]:
        shutil.copy2(DOCS / name, PUBLIC / name)

    workflow_dir = PUBLIC / ".github" / "workflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    (workflow_dir / "pages.yml").write_text(
        "name: Deploy public dashboard\n\n"
        "on:\n"
        "  push:\n"
        "    branches: [main]\n"
        "  workflow_dispatch:\n\n"
        "permissions:\n"
        "  contents: read\n"
        "  pages: write\n"
        "  id-token: write\n\n"
        "concurrency:\n"
        "  group: pages\n"
        "  cancel-in-progress: true\n\n"
        "jobs:\n"
        "  deploy:\n"
        "    environment:\n"
        "      name: github-pages\n"
        "      url: ${{ steps.deployment.outputs.page_url }}\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - name: Checkout\n"
        "        uses: actions/checkout@v4\n"
        "      - name: Configure Pages\n"
        "        uses: actions/configure-pages@v5\n"
        "      - name: Upload artifact\n"
        "        uses: actions/upload-pages-artifact@v3\n"
        "        with:\n"
        "          path: .\n"
        "      - name: Deploy to GitHub Pages\n"
        "        id: deployment\n"
        "        uses: actions/deploy-pages@v4\n",
        encoding="utf-8",
    )

    index_path = PUBLIC / "index.html"
    index_html = index_path.read_text(encoding="utf-8")
    index_html = re.sub(r"Global Portfolio Model Runner", "Global Rebalance Public Dashboard", index_html)
    index_path.write_text(index_html, encoding="utf-8")

    payload_data = data or generate_dashboard_data.build_data(write_outputs=False)
    payload = scrub_payload(generate_dashboard_data.build_public_payload(payload_data))
    (PUBLIC / "data.js").write_text(
        "window.PORTFOLIO_PUBLIC_DATA = "
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + ";\n",
        encoding="utf-8",
    )
    (PUBLIC / ".nojekyll").write_text("", encoding="utf-8")
    (PUBLIC / "README.md").write_text(
        "# Global Rebalance Public Dashboard\n\n"
        "Public, normalized GitHub Pages build for the Global Rebalance model.\n\n"
        "- Live dashboard: https://fabermach.github.io/AQRL-SMP_Allocation/\n"
        "- Main repository: https://github.com/FaberMach/AQRL-SMP_Allocation\n\n"
        "This public version excludes real holdings, detailed trades, residuals, account extracts and complete watchlists.\n",
        encoding="utf-8",
    )
    print(f"Wrote {PUBLIC}")


if __name__ == "__main__":
    main()
