from __future__ import annotations

import csv
import json
import math
import os
import ssl
import time
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from market_data import build_fx_rate_map, fetch_chart_close as market_fetch_chart_close, normalize_currency, price_to_usd


WORKDIR = Path(__file__).resolve().parent
OUTDIR = WORKDIR / "analysis_outputs"
OUTDIR.mkdir(exist_ok=True)
SSL_CONTEXT = ssl._create_unverified_context()

PRICE_DATE = os.environ.get("PRICE_DATE", "2026-06-01")
CASH_USD = 26854.02
NAV_SOURCE_MAY7 = 234662.78
ECOPET_BOND_FACE = 6000.0
ECOPET_BOND_PRICE_20260601 = 100.47


@dataclass(frozen=True)
class Holding:
    symbol: str
    yahoo: str
    quantity: float
    category: str
    thesis: str
    target_multiple: float
    action_bias: str
    source: str = "IBKR"


@dataclass(frozen=True)
class Watch:
    name: str
    symbol: str
    yahoo: str
    category: str
    thesis: str
    target_multiple: float
    priority: str
    source: str


HOLDINGS = [
    Holding("ICG", "ICG.CN", 8, "Microcap Canada", "posição residual CAD; baixa liquidez", 1.00, "manter apenas residual"),
    Holding("AMZN", "AMZN", 50, "Core tech", "cloud, ads e consumo; qualidade alta", 1.14, "manter/aumentar moderado"),
    Holding("COPX", "COPX", 100, "ETF cobre", "eletrificação e déficit estrutural de cobre", 1.12, "manter"),
    Holding("GOOGL", "GOOGL", 25, "Core tech", "IA/search/cloud; valuation ainda razoável", 1.12, "manter"),
    Holding("HYMC", "HYMC", 10, "Microcap metais", "opcionalidade alta, execução fraca", 0.90, "zerar ou residual"),
    Holding("IBM", "IBM", 100, "Value tech", "defensiva, IA corporativa, menor convexidade", 1.04, "reduzir"),
    Holding("ICGB", "", 3, "Residual sem cotação", "posição com preço zero no extrato IBKR", 1.00, "sem ação econômica"),
    Holding("ICGC", "", 3, "Residual sem cotação", "posição com preço zero no extrato IBKR", 1.00, "sem ação econômica"),
    Holding("ICGD", "", 3, "Residual sem cotação", "posição com preço zero no extrato IBKR", 1.00, "sem ação econômica"),
    Holding("ICGE", "", 3, "Residual sem cotação", "posição com preço zero no extrato IBKR", 1.00, "sem ação econômica"),
    Holding("ICGF", "", 3, "Residual sem cotação", "posição com preço zero no extrato IBKR", 1.00, "sem ação econômica"),
    Holding("JPM", "JPM", 100, "Financeiro core", "banco de qualidade, mas peso atual alto", 1.06, "reduzir"),
    Holding("KTOS", "KTOS", 60, "Defesa", "drones, sistemas autônomos e defesa", 1.18, "manter"),
    Holding("LAES", "LAES", 1000, "Semicondutores/segurança", "microcap com opcionalidade e risco", 1.25, "reduzir para cesta"),
    Holding("MSFT", "MSFT", 50, "Core tech", "cloud/IA; qualidade máxima", 1.10, "manter"),
    Holding("NAUFF", "NAUFF", 2000, "Urânio", "opcionalidade em ciclo nuclear", 1.25, "manter pequeno"),
    Holding("NTDOY", "NTDOY", 75, "Consumo/games", "qualidade, mas fora das teses anexas", 1.07, "reduzir"),
    Holding("NVDA", "NVDA", 200, "AI semis", "liderança em IA, valuation exige disciplina", 1.10, "reduzir peso"),
    Holding("QBTS", "QBTS", 500, "Quantum", "alto beta e risco de diluição", 1.20, "reduzir"),
    Holding("RGTI", "RGTI", 200, "Quantum", "alto beta e risco de diluição", 1.20, "reduzir"),
    Holding("RKLB", "RKLB", 60, "Espaço/defesa", "uma das top 5 dos anexos; execução real", 1.35, "aumentar"),
    Holding("RTX", "RTX", 30, "Defesa core", "defesa defensiva, menor upside que KTOS/RKLB", 1.08, "manter"),
    Holding("SHLD", "SHLD", 150, "ETF defesa", "defesa/segurança como tema estrutural", 1.12, "manter"),
    Holding("URA", "URA", 100, "ETF urânio", "ciclo nuclear e demanda de energia para IA", 1.15, "manter"),
    Holding("USGDF", "USGDF", 1000, "Microcap", "posição residual ilíquida", 1.00, "zerar se possível"),
    Holding("XOVR", "XOVR", 100, "Renda fixa ETF", "equivalente defensivo/cash-like", 1.04, "manter como caixa equivalente"),
]


WATCHLIST = [
    Watch("American Rare Earths", "ARR", "ARR.AX", "Rare earths", "top 5; terras raras EUA, geopolítica, muito risco", 1.45, "alta", "Análise top 5 / Stock Watch"),
    Watch("AST SpaceMobile", "ASTS", "ASTS", "Espaço", "top 5; infraestrutura celular via satélite", 1.40, "alta", "Análise top 5 / Stock Watch"),
    Watch("NexGen Energy", "NXE", "NXE", "Urânio", "top 5; ativo tier-1 em urânio", 1.30, "alta", "Análise top 5 / Stock Watch"),
    Watch("Rocket Lab", "RKLB", "RKLB", "Espaço/defesa", "top 5; execução operacional", 1.35, "alta", "Análise top 5 / Stock Watch"),
    Watch("NuScale Power", "SMR", "SMR", "Nuclear SMR", "top 5; opcionalidade em SMRs", 1.30, "alta", "Análise top 5 / Stock Watch"),
    Watch("MP Materials", "MP", "MP", "Rare earths", "produção de rare earths nos EUA; menor risco que ARR", 1.20, "media", "Stock Watch"),
    Watch("Lynas Rare Earths", "LYC", "LYC.AX", "Rare earths", "cadeia ex-China em escala", 1.15, "media", "Stock Watch"),
    Watch("Ucore Rare Metals", "Ucore", "UURAF", "Rare earths", "refino/separação, similar a ARR", 1.35, "media", "Stock Watch"),
    Watch("Aclara Resources", "Aclara", "ARA.TO", "Rare earths", "heavy rare earths com narrativa ESG", 1.30, "media", "Stock Watch"),
    Watch("Energy Fuels", "UUUU", "UUUU", "Urânio/rare earths", "urânio + monazita + rare earths", 1.25, "media", "Stock Watch"),
    Watch("Denison Mines", "DNN", "DNN", "Urânio", "ISR optionality no ciclo nuclear", 1.25, "media", "Stock Watch"),
    Watch("Global Atomic", "GLO", "GLO.TO", "Urânio", "alto leverage com risco Níger", 1.30, "baixa", "Stock Watch"),
    Watch("Deep Yellow", "DYL", "DYL.AX", "Urânio", "ciclo nuclear longo", 1.20, "media", "Stock Watch"),
    Watch("Fission Uranium", "FCU", "FCU.TO", "Urânio", "Athabasca estratégico", 1.20, "media", "Stock Watch"),
    Watch("Ivanhoe Mines", "IVN", "IVN.TO", "Cobre", "opcionalidade global em cobre", 1.18, "media", "Stock Watch"),
    Watch("Solaris Resources", "SLS", "SLS.TO", "Cobre", "exploração de cobre; alto risco", 1.25, "baixa", "Stock Watch"),
    Watch("Arizona Sonoran Copper", "ASCU", "ASCU.TO", "Cobre", "cobre doméstico americano", 1.20, "baixa", "Stock Watch"),
    Watch("NGEx Minerals", "NGEX", "NGEX.V", "Cobre", "altíssimo risco/recompensa", 1.30, "baixa", "Stock Watch"),
    Watch("Sigma Lithium", "SGML", "SGML", "Lítio", "Brasil + ESG + spodumene", 1.25, "media", "Stock Watch"),
    Watch("Patriot Battery Metals", "PMET", "PMET.V", "Lítio", "opcionalidade canadense", 1.25, "baixa", "Stock Watch"),
    Watch("Atlantic Lithium", "ALL", "ALL.L", "Lítio", "Gana + opcionalidade africana", 1.20, "baixa", "Stock Watch"),
    Watch("Lithium Argentina", "LAAC", "LAAC", "Lítio", "ex-Lithium Americas Argentina", 1.18, "baixa", "Stock Watch"),
    Watch("Kratos", "KTOS", "KTOS", "Defesa", "drones e sistemas autônomos", 1.18, "media", "Stock Watch"),
    Watch("Palantir", "PLTR", "PLTR", "IA/defesa", "IA militar/inteligência; valuation alto", 1.12, "media", "Stock Watch"),
    Watch("Red Cat", "RCAT", "RCAT", "Defesa drones", "microcap em drones militares", 1.35, "baixa", "Stock Watch"),
    Watch("BlackSky", "BKSY", "BKSY", "Espaço", "imagens em tempo real", 1.25, "baixa", "Stock Watch"),
    Watch("Planet Labs", "PL", "PL", "Espaço/dados", "dados orbitais + IA", 1.22, "baixa", "Stock Watch"),
    Watch("Recursion", "RXRX", "RXRX", "AI biotech", "drug discovery + IA", 1.25, "baixa", "Stock Watch"),
    Watch("Beam Therapeutics", "BEAM", "BEAM", "Biotech", "base editing", 1.25, "baixa", "Stock Watch"),
    Watch("CRISPR Therapeutics", "CRSP", "CRSP", "Biotech", "gene editing com opcionalidade", 1.20, "baixa", "Stock Watch"),
    Watch("Oklo", "OKLO", "OKLO", "Nuclear", "microreatores + IA/energia", 1.25, "media", "Stock Watch"),
    Watch("Cadiz", "CDZI", "CDZI", "Água", "escassez hídrica", 1.15, "baixa", "Stock Watch"),
    Watch("Nutrien", "NTR", "NTR", "Agricultura", "potássio/fertilizantes estratégicos", 1.08, "media", "Stock Watch"),
    Watch("Mosaic", "MOS", "MOS", "Agricultura", "segurança alimentar global", 1.08, "media", "Stock Watch"),
]


TARGET_WEIGHTS = {
    "Cash": 0.08,
    "XOVR": 0.04,
    "ECOPET_BOND": 0.03,
    "AMZN": 0.05,
    "GOOGL": 0.05,
    "MSFT": 0.06,
    "NVDA": 0.08,
    "IBM": 0.04,
    "JPM": 0.06,
    "RTX": 0.03,
    "KTOS": 0.04,
    "SHLD": 0.04,
    "URA": 0.05,
    "COPX": 0.04,
    "RKLB": 0.06,
    "ASTS": 0.04,
    "NXE": 0.04,
    "SMR": 0.03,
    "ARR.AX": 0.02,
    "MP": 0.02,
    "UUUU": 0.02,
    "SGML": 0.02,
    "QBTS": 0.02,
    "RGTI": 0.015,
    "LAES": 0.015,
    "NAUFF": 0.01,
}


def unix(date_str: str) -> int:
    return int(datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc).timestamp())


def fetch_chart_close(yahoo_symbol: str, date_str: str = PRICE_DATE) -> dict:
    return market_fetch_chart_close(yahoo_symbol, date_str)


def money(x: float | None) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return ""
    return f"{x:,.2f}"


def md_table(rows: list[dict], columns: list[str]) -> str:
    if not rows:
        return ""
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        vals = [str(row.get(col, "")).replace("\n", " ") for col in columns]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def main() -> None:
    all_yahoo = sorted(({h.yahoo for h in HOLDINGS} | {w.yahoo for w in WATCHLIST}) - {""})
    price_rows = {}
    for i, sym in enumerate(all_yahoo, 1):
        price_rows[sym] = fetch_chart_close(sym)
        print(f"{i:02d}/{len(all_yahoo)} {sym}: {price_rows[sym].get('close')} {price_rows[sym].get('currency')} {price_rows[sym].get('error')}")
        time.sleep(0.15)

    fx_rates = build_fx_rate_map([row["currency"] for row in price_rows.values() if row.get("currency")], PRICE_DATE)

    price_output_rows = []
    for sym in all_yahoo:
        fetched = price_rows.get(sym, {})
        normalized_currency, local_multiplier = normalize_currency(fetched.get("currency"))
        fx_rate = fx_rates.get(normalized_currency, {}).get("rate")
        local_close = fetched.get("close")
        if local_close is not None:
            local_close = float(local_close) * local_multiplier
        usd_close = price_to_usd(local_close, normalized_currency, fx_rates)
        price_output_rows.append({
            "symbol": sym,
            "close": money(local_close),
            "currency": normalized_currency,
            "currency_raw": fetched.get("currency") or "",
            "fx_to_usd": f"{fx_rate:.6f}" if isinstance(fx_rate, (int, float)) and fx_rate is not None else "",
            "close_usd": money(usd_close),
            "date": fetched.get("date") or "",
            "source": fetched.get("source") or "yahoo",
            "url": fetched.get("url") or "",
            "error": fetched.get("error") or "",
        })

    with (OUTDIR / "prices_2026-06-01.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["symbol", "close", "currency", "currency_raw", "fx_to_usd", "close_usd", "date", "source", "url", "error"])
        writer.writeheader()
        writer.writerows(price_output_rows)

    holding_rows = []
    total_equity = 0.0
    holding_value_map = {}
    for h in HOLDINGS:
        fetched = price_rows.get(h.yahoo, {"close": None, "currency": "", "error": "sem ticker Yahoo; preço zero no extrato"})
        normalized_currency, local_multiplier = normalize_currency(fetched.get("currency"))
        fx_rate = fx_rates.get(normalized_currency, {}).get("rate")
        price_local = fetched.get("close")
        if price_local is not None:
            price_local = float(price_local) * local_multiplier
        price_usd = price_to_usd(price_local, normalized_currency, fx_rates)
        value_local = h.quantity * price_local if price_local is not None else None
        value_usd = price_to_usd(value_local, normalized_currency, fx_rates)
        if value_usd is not None:
            total_equity += value_usd
            holding_value_map[h.symbol] = value_usd
        else:
            holding_value_map[h.symbol] = 0.0
        target_local = price_local * h.target_multiple if price_local is not None else None
        target_usd = price_to_usd(target_local, normalized_currency, fx_rates)
        holding_rows.append({
            "symbol": h.symbol,
            "yahoo": h.yahoo,
            "quantity": h.quantity,
            "price_2026_06_01": money(price_local),
            "price_usd": money(price_usd),
            "currency": normalized_currency,
            "currency_raw": fetched.get("currency") or "",
            "fx_to_usd": f"{fx_rate:.6f}" if isinstance(fx_rate, (int, float)) and fx_rate is not None else "",
            "market_value_local": money(value_local),
            "market_value_usd": money(value_usd),
            "market_value_usd_if_usd": money(value_usd),
            "target_dec_2026": money(target_local),
            "target_dec_2026_usd": money(target_usd),
            "upside_to_target_pct": f"{(h.target_multiple - 1) * 100:.1f}",
            "category": h.category,
            "action_bias": h.action_bias,
            "thesis": h.thesis,
            "price_error": fetched.get("error") or "",
            "price_date": fetched.get("date") or "",
        })

    with (OUTDIR / "ibkr_holdings_analysis.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(holding_rows[0].keys()))
        writer.writeheader()
        writer.writerows(holding_rows)

    watch_rows = []
    for w in WATCHLIST:
        fetched = price_rows[w.yahoo]
        normalized_currency, local_multiplier = normalize_currency(fetched.get("currency"))
        fx_rate = fx_rates.get(normalized_currency, {}).get("rate")
        price_local = fetched.get("close")
        if price_local is not None:
            price_local = float(price_local) * local_multiplier
        price_usd = price_to_usd(price_local, normalized_currency, fx_rates)
        target_local = price_local * w.target_multiple if price_local is not None else None
        target_usd = price_to_usd(target_local, normalized_currency, fx_rates)
        watch_rows.append({
            "name": w.name,
            "symbol": w.symbol,
            "yahoo": w.yahoo,
            "price_2026_06_01": money(price_local),
            "price_usd": money(price_usd),
            "currency": normalized_currency,
            "currency_raw": fetched.get("currency") or "",
            "fx_to_usd": f"{fx_rate:.6f}" if isinstance(fx_rate, (int, float)) and fx_rate is not None else "",
            "target_dec_2026": money(target_local),
            "target_dec_2026_usd": money(target_usd),
            "upside_to_target_pct": f"{(w.target_multiple - 1) * 100:.1f}",
            "priority": w.priority,
            "category": w.category,
            "thesis": w.thesis,
            "source": w.source,
            "price_error": fetched.get("error") or "",
            "price_date": fetched.get("date") or "",
        })

    with (OUTDIR / "watchlist_analysis.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(watch_rows[0].keys()))
        writer.writeheader()
        writer.writerows(watch_rows)

    # Portfolio value estimate uses all listed assets converted to USD plus cash and the ECOPET bond.
    ecopet_bond_value = ECOPET_BOND_FACE * ECOPET_BOND_PRICE_20260601 / 100
    portfolio_value = total_equity + CASH_USD + ecopet_bond_value
    rebalance_rows = []
    for sym, weight in TARGET_WEIGHTS.items():
        target_value = portfolio_value * weight
        current_value = 0.0
        if sym == "Cash":
            current_value = CASH_USD
        elif sym == "ECOPET_BOND":
            current_value = ecopet_bond_value
        else:
            current_value = holding_value_map.get(sym, 0.0)
        rebalance_rows.append({
            "asset": sym,
            "target_weight_pct": f"{weight * 100:.1f}",
            "target_value_usd": money(target_value),
            "current_value_usd": money(current_value),
            "trade_usd": money(target_value - current_value),
        })

    with (OUTDIR / "rebalance_proposal.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rebalance_rows[0].keys()))
        writer.writeheader()
        writer.writerows(rebalance_rows)

    top_trades = sorted(
        rebalance_rows,
        key=lambda r: abs(float(r["trade_usd"].replace(",", "") or 0)),
        reverse=True,
    )
    holding_table = [
        {
            "Ticker": r["symbol"],
            "Preço 2026-06-01": r["price_2026_06_01"],
            "Moeda": r["currency"],
            "Meta dez/26": r["target_dec_2026"],
            "Upside %": r["upside_to_target_pct"],
            "Viés": r["action_bias"],
        }
        for r in holding_rows
    ]
    watch_table = [
        {
            "Ticker": r["symbol"],
            "Yahoo": r["yahoo"],
            "Preço 2026-06-01": r["price_2026_06_01"],
            "Moeda": r["currency"],
            "Meta dez/26": r["target_dec_2026"],
            "Prioridade": r["priority"],
            "Categoria": r["category"],
        }
        for r in watch_rows
    ]
    trade_table = [
        {
            "Ativo": r["asset"],
            "Peso alvo %": r["target_weight_pct"],
            "Valor alvo USD": r["target_value_usd"],
            "Valor atual USD": r["current_value_usd"],
            "Compra/Venda USD": r["trade_usd"],
        }
        for r in top_trades
    ]

    report = OUTDIR / "rebalance_report.md"
    report.write_text(
        "\n".join([
            "# Portfolio IBKR - atualização e rebalanceamento",
            "",
            f"Data de preço: fechamento de {PRICE_DATE}. Fonte de preços: Yahoo Finance Chart API, URLs registradas em `prices_2026-06-01.csv`.",
            "Bond ECOPET 6.875% 04/29/2030: preço público conferido para ISIN US279158AN94; valor limpo usado 100,47.",
            "",
            "## Carteira estimada",
            "",
            f"- Cash IBKR: USD {money(CASH_USD)}.",
            f"- Valor estimado de ações convertido para USD em {PRICE_DATE}: USD {money(total_equity)}.",
            f"- Bond ECOPET 6.875% 04/29/2030: preço limpo usado 100,47; valor estimado USD {money(ecopet_bond_value)}.",
            f"- Valor total estimado usado no rebalanceamento: USD {money(portfolio_value)}.",
            f"- Caixa alvo: 8,0%, acima do mínimo requerido de 5,0%.",
            "- Observação: ativos em CAD, AUD, GBP e GBp foram convertidos para USD usando o câmbio do mesmo snapshot. As posições ICGB-ICGF constam no extrato com preço zero e foram tratadas como residuais sem valor econômico.",
            "",
            "## Metodologia das metas para dez/2026",
            "",
            f"As metas são projeções internas de cenário-base até dezembro de 2026, calculadas como preço de fechamento de {PRICE_DATE} multiplicado por um fator por tese/risco. Onde não há cobertura confiável no endpoint público, o fator privilegia qualidade, convexidade, liquidez e aderência aos anexos. Não é recomendação financeira personalizada.",
            "",
            "## Proposta resumida",
            "",
            "- Preservar núcleo de qualidade: MSFT, NVDA, AMZN, GOOGL, JPM, IBM e RTX, mas reduzir concentração em NVDA/JPM/IBM.",
            "- Aumentar aderência aos anexos: RKLB, ASTS, NXE, SMR, ARR, UUUU/URA, COPX e SGML.",
            "- Reduzir cauda especulativa redundante: QBTS, RGTI, LAES, HYMC, USGDF e posições ilíquidas/residuais.",
            "- Manter cash + equivalentes: 8% em cash, 4% em XOVR e 3% no bond ECOPET.",
            "",
            "## Holdings IBKR",
            "",
            md_table(holding_table, ["Ticker", "Preço 2026-06-01", "Moeda", "Meta dez/26", "Upside %", "Viés"]),
            "",
            "## Sugestões dos anexos",
            "",
            md_table(watch_table, ["Ticker", "Yahoo", "Preço 2026-06-01", "Moeda", "Meta dez/26", "Prioridade", "Categoria"]),
            "",
            "## Rebalanceamento proposto",
            "",
            md_table(trade_table, ["Ativo", "Peso alvo %", "Valor alvo USD", "Valor atual USD", "Compra/Venda USD"]),
            "",
            "## Pendências de preço",
            "",
            "Fission Uranium, Lithium Argentina, NGEx Minerals e Patriot Battery Metals não retornaram fechamento verificável para 2026-06-01 nos símbolos testados no Yahoo Finance. Foram mantidos no CSV com erro de preço quando aplicável; a proposta não depende deles.",
            "",
            "## Arquivos gerados",
            "",
            "- `prices_2026-06-01.csv`: preços baixados, câmbio e URLs de fonte.",
            "- `ibkr_holdings_analysis.csv`: holdings atuais, preço local e USD, meta e viés de ação.",
            "- `watchlist_analysis.csv`: sugestões dos anexos, preço local e USD, meta e prioridade.",
            "- `rebalance_proposal.csv`: pesos alvo e compra/venda estimada em USD.",
        ]),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
