from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dashboard" / "data.js"


def parse_money(value: str) -> float:
    value = (value or "").strip().replace(",", "")
    return float(value) if value else 0.0


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


RATIONALS = {
    "Cash": "Realocar parte do caixa para ativos-alvo, preservando 8% em cash, acima do minimo de 5%.",
    "XOVR": "Aumentar equivalente defensivo para sustentar liquidez e reduzir volatilidade sem deixar tudo em cash.",
    "ECOPET_BOND": "Manter renda fixa em USD como bloco defensivo, com pequena recomposicao para 3% da carteira.",
    "AMZN": "Manter exposicao de qualidade em cloud, ads e consumo, apenas aparando excesso pequeno.",
    "GOOGL": "Aumentar para peso de nucleo pela combinacao de IA, search e cloud com valuation relativamente equilibrado.",
    "MSFT": "Preservar posicao core em cloud/IA, mas reduzir concentracao para financiar teses com maior convexidade.",
    "NVDA": "Continuar exposto a lideranca em IA, porem reduzir concentracao extrema e risco de valuation.",
    "IBM": "Reduzir ativo defensivo de menor convexidade para liberar capital para temas dos anexos.",
    "JPM": "Manter banco de qualidade, mas reduzir peso elevado e dependencia de financeiro tradicional.",
    "RTX": "Reforcar defesa core, com menor upside que RKLB/KTOS, mas melhor perfil defensivo.",
    "KTOS": "Aumentar exposicao a drones, sistemas autonomos e guerra eletronica, alinhado ao Stock Watch.",
    "SHLD": "Manter ETF de defesa como exposicao diversificada ao tema geopolitico.",
    "URA": "Aumentar bloco de uranio pelo ciclo nuclear, energia para IA e diversificacao via ETF.",
    "COPX": "Reforcar cobre como tese de eletrificacao global com risco mais diversificado via ETF.",
    "RKLB": "Aumentar uma das top 5 dos anexos, com execucao operacional real em espaco e defesa.",
    "ASTS": "Iniciar exposicao a infraestrutura celular via satelite, uma das maiores optionalities dos anexos.",
    "NXE": "Iniciar posicao em ativo tier-1 de uranio, destacado como qualidade geologica superior.",
    "SMR": "Iniciar exposicao a SMRs, tese nuclear com opcionalidade estrategica e alta volatilidade.",
    "ARR.AX": "Adicionar rare earths geopolitico dos EUA em tamanho controlado pelo risco elevado.",
    "MP": "Adicionar rare earths em producao nos EUA, com menor risco relativo que ARR.",
    "UUUU": "Adicionar hibrido de uranio, monazita e rare earths para ampliar a cesta estrategica.",
    "SGML": "Adicionar litio Brasil/ESG como optionality de supply chain critica.",
    "QBTS": "Reduzir quantum para tamanho de cesta, diminuindo risco de diluicao e volatilidade extrema.",
    "RGTI": "Manter optionality em quantum, mas com peso menor e compativel com risco binario.",
    "LAES": "Manter microcap de seguranca/semis apenas como componente pequeno da cesta.",
    "NAUFF": "Reduzir para posicao pequena, mantendo optionality no ciclo nuclear sem concentrar risco.",
}

CATEGORIES = {
    "Cash": "Cash/Equivalentes",
    "XOVR": "Cash/Equivalentes",
    "ECOPET_BOND": "Cash/Equivalentes",
    "AMZN": "Nucleo qualidade",
    "GOOGL": "Nucleo qualidade",
    "MSFT": "Nucleo qualidade",
    "NVDA": "Nucleo qualidade",
    "IBM": "Nucleo qualidade",
    "JPM": "Financeiro",
    "RTX": "Defesa/espaco",
    "KTOS": "Defesa/espaco",
    "SHLD": "Defesa/espaco",
    "RKLB": "Defesa/espaco",
    "ASTS": "Defesa/espaco",
    "URA": "Uranio/nuclear",
    "NXE": "Uranio/nuclear",
    "SMR": "Uranio/nuclear",
    "UUUU": "Uranio/nuclear",
    "NAUFF": "Uranio/nuclear",
    "COPX": "Minerais criticos",
    "ARR.AX": "Minerais criticos",
    "MP": "Minerais criticos",
    "SGML": "Minerais criticos",
    "QBTS": "Cauda especulativa",
    "RGTI": "Cauda especulativa",
    "LAES": "Cauda especulativa",
}

THESES = [
    {
        "title": "Nucleo qualidade",
        "assets": ["MSFT", "NVDA", "AMZN", "GOOGL", "JPM", "IBM", "RTX"],
        "rationale": "Preservar qualidade e liquidez, mas reduzir concentracoes que financiam o novo basket.",
    },
    {
        "title": "Defesa e espaco",
        "assets": ["RKLB", "ASTS", "KTOS", "SHLD", "RTX"],
        "rationale": "Aumentar exposicao a infraestrutura espacial, defesa autonoma e seguranca geopolitica.",
    },
    {
        "title": "Uranio e nuclear",
        "assets": ["URA", "NXE", "SMR", "UUUU", "NAUFF", "ECOPET_BOND"],
        "rationale": "Capturar demanda energetica estrutural, ciclo nuclear e renda fixa defensiva em USD.",
    },
    {
        "title": "Minerais criticos",
        "assets": ["ARR.AX", "MP", "COPX", "SGML"],
        "rationale": "Montar cesta de optionality em rare earths, cobre e litio com pesos controlados.",
    },
    {
        "title": "Cauda especulativa",
        "assets": ["QBTS", "RGTI", "LAES", "HYMC", "USGDF"],
        "rationale": "Reduzir risco binario e iliquidez, mantendo apenas opcionalidade dimensionada.",
    },
]


def build_data() -> dict:
    moves_csv = read_csv(ROOT / "analysis_outputs" / "rebalance_proposal.csv")
    holdings_csv = read_csv(ROOT / "analysis_outputs" / "ibkr_holdings_analysis.csv")
    watch_csv = read_csv(ROOT / "analysis_outputs" / "watchlist_analysis.csv")

    moves = [
        {
            "asset": row["asset"],
            "targetWeight": parse_money(row["target_weight_pct"]),
            "targetValue": parse_money(row["target_value_usd"]),
            "currentValue": parse_money(row["current_value_usd"]),
            "trade": parse_money(row["trade_usd"]),
            "category": CATEGORIES.get(row["asset"], "Outros"),
            "rationale": RATIONALS.get(row["asset"], "Ajuste para aproximar a carteira do peso alvo definido."),
        }
        for row in moves_csv
    ]

    holdings = [
        {
            "symbol": row["symbol"],
            "price": row["price_2026_06_01"],
            "currency": row["currency"],
            "target": row["target_dec_2026"],
            "upside": row["upside_to_target_pct"],
            "bias": row["action_bias"],
            "thesis": row["thesis"],
        }
        for row in holdings_csv
    ]

    watchlist = [
        {
            "symbol": row["symbol"],
            "yahoo": row["yahoo"],
            "price": row["price_2026_06_01"],
            "currency": row["currency"],
            "target": row["target_dec_2026"],
            "priority": row["priority"],
            "category": row["category"],
        }
        for row in watch_csv
    ]

    return {
        "meta": {
            "priceDate": "2026-06-01",
            "totalValue": 256021.52,
            "cashCurrent": 26854.02,
            "cashTargetPct": 8,
            "cashMinimumPct": 5,
            "equivalentsPct": 15,
            "notes": [
                "Precos de acoes pelo Yahoo Finance Chart API.",
                "Bond ECOPET 6.875% 04/29/2030 marcado com preco limpo 100,47.",
                "Metas sao cenario-base interno ate dezembro de 2026.",
            ],
        },
        "moves": moves,
        "holdings": holdings,
        "watchlist": watchlist,
        "theses": THESES,
    }


def main() -> None:
    payload = json.dumps(build_data(), ensure_ascii=False, indent=2)
    OUT.write_text(f"window.PORTFOLIO_DATA = {payload};\n", encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
