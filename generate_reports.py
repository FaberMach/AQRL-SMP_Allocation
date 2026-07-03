from __future__ import annotations

import json
import re
import csv
from pathlib import Path

import generate_dashboard_data


ROOT = Path(__file__).resolve().parent
REPORT_MD = ROOT / "docs" / "EXECUTIVE_REPORT.md"
REPORT_HTML = ROOT / "docs" / "executive_report.html"
SCENARIO_DIR = ROOT / "analysis_outputs" / "scenarios"
ALIASES_CSV = ROOT / "analysis_outputs" / "ticker_aliases.csv"


def money(value: float | int | None) -> str:
    return f"USD {float(value or 0):,.0f}"


def pct(value: float | int | None) -> str:
    return f"{float(value or 0):.1f}%"


def html_escape(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def top_moves(data: dict, count: int = 8) -> list[dict]:
    return sorted(data["moves"], key=lambda row: abs(row["baseTradeValue"]), reverse=True)[:count]


def trade_rows(data: dict, side: str, count: int = 6) -> list[dict]:
    rows = [row for row in data["moves"] if not row.get("fixed")]
    if side == "buy":
        rows = [row for row in rows if row["baseTradeValue"] > 0]
        return sorted(rows, key=lambda row: row["baseTradeValue"], reverse=True)[:count]
    rows = [row for row in rows if row["baseTradeValue"] < 0]
    return sorted(rows, key=lambda row: row["baseTradeValue"])[:count]


def read_aliases() -> list[dict]:
    if not ALIASES_CSV.exists():
        return []
    with ALIASES_CSV.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def risk_snapshot(data: dict) -> dict:
    meta = data["meta"]
    base_model = generate_dashboard_data.build_model_snapshot(data, "study", meta["targetCapital"])
    missing_prices = [row for row in data["marketPrices"] if row["status"] != "ok" or row.get("error")]
    aliases = read_aliases()
    unresolved_aliases = [
        row for row in aliases if "unresolved" in (row.get("status") or "").lower()
    ]
    return {
        "topFiveSharePct": base_model["topFiveShare"],
        "nonUsdSharePct": base_model["nonUsdShare"],
        "liquidityCurrentPct": meta["liquidityCurrentPct"],
        "liquidityTargetPct": meta["liquidityTargetPct"],
        "residualCount": meta["residualCount"],
        "missingPriceCount": len(missing_prices),
        "aliasCount": len(aliases),
        "unresolvedAliasCount": len(unresolved_aliases),
    }


def scenario_snapshot(data: dict, scenario_id: str) -> dict:
    model = generate_dashboard_data.build_model_snapshot(data, scenario_id, data["meta"]["targetCapital"])
    moves = []
    for move in model["modelMoves"]:
        moves.append(
            {
                "asset": move["asset"],
                "theme": move["themeLabel"],
                "targetWeightPct": round(move["targetWeight"], 4),
                "currentValueUsd": round(move["currentValue"], 2),
                "targetValueUsd": round(move["targetValue"], 2),
                "tradeUsd": round(move["trade"], 2),
                "action": move["action"],
                "fixed": bool(move["fixed"]),
                "thesis": move["thesis"],
            }
        )
    return {
        "scenario": model["scenario"],
        "capitalUsd": round(model["capital"], 2),
        "liquidityTargetPct": round(model["liquidityTargetPct"], 4),
        "investablePct": round(model["investablePct"], 4),
        "topFiveSharePct": round(model["topFiveShare"], 4),
        "nonUsdSharePct": round(model["nonUsdShare"], 4),
        "themeSeries": model["themeSeries"],
        "regionSeries": model["regionSeries"],
        "currencySeries": model["currencySeries"],
        "moves": moves,
    }


def write_scenarios(data: dict) -> list[Path]:
    SCENARIO_DIR.mkdir(parents=True, exist_ok=True)
    paths = []
    for scenario in data["scenarios"]:
        snapshot = scenario_snapshot(data, scenario["id"])
        path = SCENARIO_DIR / f"{scenario['id']}.json"
        path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
        paths.append(path)
    return paths


def markdown_report(data: dict, scenario_paths: list[Path]) -> str:
    meta = data["meta"]
    moves = top_moves(data)
    risks = risk_snapshot(data)
    sell_first = trade_rows(data, "sell")
    buy_first = trade_rows(data, "buy")
    lines = [
        "# Relatorio Executivo - Global Rebalance",
        "",
        f"- Data de precos: {meta['priceDate']}",
        f"- Capital alvo: {money(meta['targetCapital'])}",
        f"- Valor atual estimado: {money(meta['currentPortfolioValue'])}",
        f"- Liquidez atual: {money(meta['liquidityCurrentValue'])} ({pct(meta['liquidityCurrentPct'])})",
        f"- Liquidez alvo: {pct(meta['liquidityTargetPct'])}",
        f"- Cash alvo minimo: {pct(meta['cashMinimumPct'])}; cash alvo do modelo: {pct(meta['cashTargetPct'])}",
        f"- Ativos modelados: {meta['modelAssetCount']}; residuais: {meta['residualCount']}; watchlist: {meta['watchlistCount']}",
        "",
        "## Tese central",
        "",
        "O modelo reduz concentracoes excessivas, preserva liquidez explicita e direciona risco para temas globais com convexidade: defesa/espaco, uranio/nuclear, minerais criticos e nucleo de qualidade.",
        "",
        "## Painel de risco",
        "",
        f"- Top 5 no cenario base: {pct(risks['topFiveSharePct'])}",
        f"- Exposicao nao USD no cenario base: {pct(risks['nonUsdSharePct'])}",
        f"- Liquidez atual versus alvo: {pct(risks['liquidityCurrentPct'])} -> {pct(risks['liquidityTargetPct'])}",
        f"- Residuais fora do modelo: {risks['residualCount']}",
        f"- Precificacoes com lacuna/erro no snapshot: {risks['missingPriceCount']}",
        f"- Aliases acompanhados: {risks['aliasCount']}; ainda sem confirmacao plena: {risks['unresolvedAliasCount']}",
        "",
        "## Gatilhos de revisao",
        "",
        "- Rebalancear se cash puro cair abaixo de 5% ou se cash + equivalentes cair abaixo de 12%.",
        "- Revisar concentracao se o top 5 superar 35% do portfolio no cenario base.",
        "- Travar novas compras em cauda especulativa se qualquer ticker residual sem tese passar de 1% do portfolio.",
        "- Revalidar ticker, bolsa e liquidez antes de executar ativos marcados como alias_candidate ou unresolved_exchange_alias.",
        "",
        "## Maiores movimentos",
        "",
        "| Ativo | Tema | Atual | Alvo base | Trade base | Racional |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for move in moves:
        lines.append(
            f"| {move['asset']} | {move['themeLabel']} | {money(move['currentValue'])} | {money(move['baseTargetValue'])} | {money(move['baseTradeValue'])} | {move['thesis']} |"
        )
    lines.extend(
        [
            "",
            "## Ordem operacional sugerida",
            "",
            "### Levantar liquidez / reduzir excesso",
            "",
            "| Ativo | Trade base | Racional |",
            "| --- | ---: | --- |",
        ]
    )
    for move in sell_first:
        lines.append(f"| {move['asset']} | {money(move['baseTradeValue'])} | {move['thesis']} |")
    lines.extend(
        [
            "",
            "### Compras prioritarias",
            "",
            "| Ativo | Trade base | Racional |",
            "| --- | ---: | --- |",
        ]
    )
    for move in buy_first:
        lines.append(f"| {move['asset']} | {money(move['baseTradeValue'])} | {move['thesis']} |")
    lines.extend(
        [
            "",
            "## Cenarios versionados",
            "",
        ]
    )
    for path in scenario_paths:
        lines.append(f"- `{path.as_posix().replace(str(ROOT.as_posix()) + '/', '')}`")
    lines.extend(
        [
            "",
            "## Controles e validacao",
            "",
            "- `py run_pipeline.py` regenera dashboard, exports, cenarios e validacao.",
            "- `py validate_project.py` confirma pesos em 100%, cash >= 5% e sincronizacao dashboard/CSVs.",
            "- A versao em `docs/` e sanitizada para publicacao; os textos extraidos dos PDFs ficam fora do upload remoto.",
        ]
    )
    return "\n".join(lines) + "\n"


def html_report(markdown: str) -> str:
    body = []
    for line in markdown.splitlines():
        if line.startswith("# "):
            body.append(f"<h1>{html_escape(line[2:])}</h1>")
        elif line.startswith("## "):
            body.append(f"<h2>{html_escape(line[3:])}</h2>")
        elif line.startswith("- "):
            body.append(f"<p class='bullet'>{html_escape(line[2:])}</p>")
        elif line.startswith("|"):
            body.append(f"<pre>{html_escape(line)}</pre>")
        elif not line.strip():
            body.append("")
        else:
            body.append(f"<p>{html_escape(line)}</p>")
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Relatorio Executivo - Global Rebalance</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px auto; max-width: 1100px; line-height: 1.5; color: #17211c; }}
    h1, h2 {{ line-height: 1.15; }}
    h1 {{ font-size: 34px; }}
    h2 {{ margin-top: 30px; font-size: 22px; }}
    .bullet {{ margin: 6px 0; padding-left: 16px; }}
    .bullet::before {{ content: "• "; margin-left: -16px; color: #1f7a4d; }}
    pre {{ white-space: pre-wrap; background: #f4f6f2; border: 1px solid #d9dfd5; padding: 8px; border-radius: 6px; }}
  </style>
</head>
<body>
{chr(10).join(body)}
</body>
</html>
"""


def main(data: dict | None = None) -> None:
    data = data or generate_dashboard_data.build_data(write_outputs=False)
    scenario_paths = write_scenarios(data)
    report_md = markdown_report(data, scenario_paths)
    REPORT_MD.write_text(report_md, encoding="utf-8")
    REPORT_HTML.write_text(html_report(report_md), encoding="utf-8")
    print(f"Wrote {REPORT_MD}")
    print(f"Wrote {REPORT_HTML}")
    print(f"Wrote {len(scenario_paths)} scenario files")


if __name__ == "__main__":
    main()
