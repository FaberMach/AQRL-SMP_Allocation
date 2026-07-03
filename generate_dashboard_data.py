from __future__ import annotations

import csv
import json
from pathlib import Path

from market_data import build_fx_rate_map, normalize_currency, price_to_usd


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dashboard" / "data.js"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_money(value: str | None) -> float:
    cleaned = (value or "").strip().replace(",", "")
    if not cleaned or cleaned == "--":
        return 0.0
    return float(cleaned)


def parse_pct(value: str | None) -> float:
    cleaned = (value or "").strip().replace("%", "")
    if not cleaned:
        return 0.0
    return float(cleaned)


def money(value: float | int | None) -> str:
    if value is None:
        return "USD 0"
    sign = "-" if float(value) < 0 else ""
    return f"{sign}USD {abs(float(value)):,.0f}"


def pct(value: float | int | None) -> str:
    if value is None:
        value = 0.0
    return f"{float(value):.1f}%"


def infer_currency(symbol: str, yahoo: str) -> str:
    if symbol in {"Cash", "XOVR", "ECOPET_BOND"}:
        return "USD"
    if yahoo.endswith(".AX"):
        return "AUD"
    if yahoo.endswith(".TO") or yahoo.endswith(".V") or symbol == "ICG":
        return "CAD"
    if yahoo.endswith(".L"):
        return "GBP"
    return "USD"


def infer_region(symbol: str, yahoo: str) -> str:
    if symbol in {"Cash", "XOVR"}:
        return "United States"
    if symbol == "ECOPET_BOND":
        return "Colombia"
    if symbol in {"SGML"}:
        return "Brazil"
    if symbol in {"LAAC"}:
        return "Argentina"
    if yahoo.endswith(".AX"):
        return "Australia"
    if yahoo.endswith(".TO") or yahoo.endswith(".V") or symbol == "ICG":
        return "Canada"
    if yahoo.endswith(".L"):
        return "United Kingdom"
    return "United States"


THEMES = [
    {
        "id": "liquidity",
        "label": "Liquidez",
        "description": "Cash, XOVR e o bond ECOPET preservam a faixa de defesa do modelo.",
        "accent": "#d08b2e",
        "assets": ["Cash", "XOVR", "ECOPET_BOND"],
    },
    {
        "id": "quality",
        "label": "Nucleo qualidade",
        "description": "MSFT, NVDA, AMZN, GOOGL, JPM e IBM financiam a carteira e reduzem ruído.",
        "accent": "#4aa3df",
        "assets": ["AMZN", "GOOGL", "MSFT", "NVDA", "IBM", "JPM"],
    },
    {
        "id": "defense_space",
        "label": "Defesa e espaco",
        "description": "RKLB, ASTS, KTOS, SHLD e RTX capturam a tese geopolitica e orbital.",
        "accent": "#7e8cff",
        "assets": ["RTX", "KTOS", "SHLD", "RKLB", "ASTS"],
    },
    {
        "id": "uranium",
        "label": "Uranio e nuclear",
        "description": "URA, NXE, SMR, UUUU e NAUFF refletem o ciclo de energia estrategica.",
        "accent": "#c86df0",
        "assets": ["URA", "NXE", "SMR", "UUUU", "NAUFF"],
    },
    {
        "id": "minerals",
        "label": "Minerais criticos",
        "description": "COPX, ARR, MP e SGML conectam cobre, terras raras e lito ao superciclo.",
        "accent": "#2bc6a4",
        "assets": ["COPX", "ARR.AX", "MP", "SGML"],
    },
    {
        "id": "tail",
        "label": "Cauda especulativa",
        "description": "QBTS, RGTI, LAES, HYMC e USGDF ficam como opcionalidade de cauda.",
        "accent": "#ff7a59",
        "assets": ["QBTS", "RGTI", "LAES", "HYMC", "USGDF"],
    },
]


REGION_PALETTE = {
    "United States": "#4aa3df",
    "Canada": "#ff7a59",
    "Australia": "#2bc6a4",
    "United Kingdom": "#d08b2e",
    "Brazil": "#52b788",
    "Argentina": "#7e8cff",
    "Colombia": "#c86df0",
}


CURRENCY_PALETTE = {
    "USD": "#4aa3df",
    "CAD": "#ff7a59",
    "AUD": "#2bc6a4",
    "GBP": "#d08b2e",
}


THEME_BY_ASSET = {
    "Cash": "liquidity",
    "XOVR": "liquidity",
    "ECOPET_BOND": "liquidity",
    "AMZN": "quality",
    "GOOGL": "quality",
    "MSFT": "quality",
    "NVDA": "quality",
    "IBM": "quality",
    "JPM": "quality",
    "RTX": "defense_space",
    "KTOS": "defense_space",
    "SHLD": "defense_space",
    "RKLB": "defense_space",
    "ASTS": "defense_space",
    "URA": "uranium",
    "NXE": "uranium",
    "SMR": "uranium",
    "UUUU": "uranium",
    "NAUFF": "uranium",
    "COPX": "minerals",
    "ARR.AX": "minerals",
    "MP": "minerals",
    "SGML": "minerals",
    "QBTS": "tail",
    "RGTI": "tail",
    "LAES": "tail",
    "HYMC": "tail",
    "USGDF": "tail",
}


ROLE_BY_ASSET = {
    "Cash": "Reserva",
    "XOVR": "Reserva",
    "ECOPET_BOND": "Reserva",
    "AMZN": "Ancoragem",
    "GOOGL": "Ancoragem",
    "MSFT": "Ancoragem",
    "NVDA": "Ancoragem",
    "IBM": "Ancoragem",
    "JPM": "Ancoragem",
    "RTX": "Estrutural",
    "KTOS": "Estrutural",
    "SHLD": "Estrutural",
    "RKLB": "Estrutural",
    "ASTS": "Estrutural",
    "URA": "Estrutural",
    "NXE": "Estrutural",
    "SMR": "Estrutural",
    "UUUU": "Estrutural",
    "NAUFF": "Estrutural",
    "COPX": "Opcionalidade",
    "ARR.AX": "Opcionalidade",
    "MP": "Opcionalidade",
    "SGML": "Opcionalidade",
    "QBTS": "Cauda",
    "RGTI": "Cauda",
    "LAES": "Cauda",
    "HYMC": "Cauda",
    "USGDF": "Cauda",
}


RATIONALS = {
    "Cash": "Preservar liquidez estrategica e cumprir o piso de 5% com folga.",
    "XOVR": "Aumentar equivalente defensivo para reduzir volatilidade sem sair de caixa.",
    "ECOPET_BOND": "Manter renda fixa em USD como camada defensiva do modelo.",
    "AMZN": "Manter qualidade em cloud, ads e consumo, apenas aparando excesso pequeno.",
    "GOOGL": "Aumentar para peso de nucleo pela combinacao de IA, search e cloud.",
    "MSFT": "Preservar posicao core em cloud/IA, mas reduzir concentracao para financiar convexidade.",
    "NVDA": "Continuar exposto a lideranca em IA, porem com disciplina de tamanho.",
    "IBM": "Reduzir ativo defensivo de menor convexidade para liberar capital para teses do estudo.",
    "JPM": "Manter banco de qualidade, mas reduzir peso elevado e dependencia de financeiro tradicional.",
    "RTX": "Reforcar defesa core, com menor upside que RKLB e KTOS, mas melhor perfil defensivo.",
    "KTOS": "Aumentar exposicao a drones, sistemas autonomos e guerra eletronica.",
    "SHLD": "Manter ETF de defesa como exposicao diversificada ao tema geopolitico.",
    "URA": "Aumentar bloco de uranio pelo ciclo nuclear e pela demanda de energia para IA.",
    "COPX": "Reforcar cobre como tese de eletrificacao global com risco mais diversificado.",
    "RKLB": "Aumentar uma das top 5 do estudo, com execucao operacional real em espaco e defesa.",
    "ASTS": "Iniciar exposicao a infraestrutura celular via satelite, uma das maiores optionalidades.",
    "NXE": "Iniciar posicao em ativo tier-1 de uranio, destacado como qualidade geologica superior.",
    "SMR": "Iniciar exposicao a SMRs, tese nuclear com opcionalidade estrategica.",
    "ARR.AX": "Adicionar rare earths geopolitico dos EUA em tamanho controlado pelo risco elevado.",
    "MP": "Adicionar rare earths em producao nos EUA, com menor risco relativo que ARR.",
    "UUUU": "Adicionar hibrido de uranio, monazita e rare earths para ampliar a cesta estrategica.",
    "SGML": "Adicionar litio Brasil/ESG como opcionalidade de supply chain critica.",
    "QBTS": "Reduzir quantum para tamanho de cesta, diminuindo risco de diluicao e volatilidade extrema.",
    "RGTI": "Manter opcionalidade em quantum, mas com peso menor e compativel com risco binario.",
    "LAES": "Manter microcap de seguranca/semis apenas como componente pequeno da cesta.",
    "NAUFF": "Reduzir para posicao pequena, mantendo opcionalidade no ciclo nuclear sem concentrar risco.",
}


SCENARIOS = [
    {
        "id": "study",
        "label": "Base do estudo",
        "description": "Replica o plano principal e preserva o corredor de liquidez de 15%.",
        "cashTargetPct": 8.0,
        "xovrTargetPct": 4.0,
        "bondTargetPct": 3.0,
        "themeMultipliers": {
            "quality": 1.0,
            "defense_space": 1.0,
            "uranium": 1.0,
            "minerals": 1.0,
            "tail": 1.0,
        },
    },
    {
        "id": "defensive",
        "label": "Defensivo global",
        "description": "Sobe caixa, corta a cauda e privilegia o nucleo de qualidade.",
        "cashTargetPct": 10.0,
        "xovrTargetPct": 4.0,
        "bondTargetPct": 3.0,
        "themeMultipliers": {
            "quality": 1.06,
            "defense_space": 0.95,
            "uranium": 0.9,
            "minerals": 0.85,
            "tail": 0.6,
        },
    },
    {
        "id": "convex",
        "label": "Convexidade",
        "description": "Reduz caixa e amplifica optionalidade em energia, defesa e minerais.",
        "cashTargetPct": 6.0,
        "xovrTargetPct": 4.0,
        "bondTargetPct": 3.0,
        "themeMultipliers": {
            "quality": 0.94,
            "defense_space": 1.05,
            "uranium": 1.16,
            "minerals": 1.12,
            "tail": 1.35,
        },
    },
]


STUDY = {
    "principles": [
        "Construa um basket, nao uma aposta unica.",
        "Aceite que varias teses falhem; poucos vencedores pagam a conta.",
        "Use ativos estrategicos com potencial de rerating estrutural.",
        "Preserve liquidez e respeite o piso de 5% em caixa.",
        "Dimensone optionalidade por tema, geografia e horizonte.",
    ],
    "basketBlueprint": [
        {
            "label": "Rare earths",
            "weight": 20,
            "examples": ["ARR", "Ucore", "Aclara", "Energy Fuels"],
        },
        {
            "label": "Uranium",
            "weight": 20,
            "examples": ["NXE", "DNN", "FCU", "DYL"],
        },
        {
            "label": "Defense / space",
            "weight": 20,
            "examples": ["ASTS", "RKLB", "KTOS", "RCAT"],
        },
        {
            "label": "AI biotech",
            "weight": 15,
            "examples": ["RXRX", "BEAM", "CRSP"],
        },
        {
            "label": "Copper / lithium",
            "weight": 15,
            "examples": ["IVN", "SGML", "PMET", "LAAC"],
        },
        {
            "label": "Nuclear",
            "weight": 10,
            "examples": ["SMR", "OKLO"],
        },
    ],
}


WATCHLIST_BUCKETS = {
    "Rare earths": ("rare_earths", "minerals"),
    "Urânio": ("uranium", "uranium"),
    "Uranio": ("uranium", "uranium"),
    "Cobre": ("copper_lithium", "minerals"),
    "Lítio": ("copper_lithium", "minerals"),
    "Lítio / cobre": ("copper_lithium", "minerals"),
    "Defesa": ("defense_space", "defense_space"),
    "IA/defesa": ("defense_space", "defense_space"),
    "Espaço": ("defense_space", "defense_space"),
    "AI biotech": ("ai_biotech", "tail"),
    "Biotech": ("ai_biotech", "tail"),
    "Nuclear": ("nuclear", "uranium"),
    "Água": ("water", "quality"),
    "Agricultura": ("agriculture", "quality"),
}


TOP_IDEAS = ["ARR", "ASTS", "NXE", "RKLB", "SMR"]


EXPORT_DIR = ROOT / "dashboard" / "exports"
PUBLIC_DIR = ROOT / "dashboard" / "public"


def parse_optional_money(value: str | None) -> float | None:
    cleaned = (value or "").strip().replace(",", "")
    if not cleaned or cleaned == "--":
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def format_fx(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.6f}"


def format_price_export(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.6f}"


def write_csv_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_price_book(price_rows: list[dict], price_date: str | None = None) -> tuple[dict[str, dict], list[dict], dict[str, dict]]:
    currencies: list[str] = []
    for row in price_rows:
        currency_source = row.get("currency_raw") or row.get("currency")
        if currency_source:
            currencies.append(currency_source)

    fx_rates = build_fx_rate_map(currencies, price_date)
    price_book: dict[str, dict] = {}
    market_prices: list[dict] = []

    for row in price_rows:
        symbol = row.get("symbol") or row.get("yahoo") or ""
        raw_currency = (row.get("currency_raw") or row.get("currency") or "USD").strip() or "USD"
        currency, local_multiplier = normalize_currency(raw_currency)

        close_local = parse_optional_money(row.get("close"))
        if close_local is None:
            close_local = parse_optional_money(row.get("price_2026_06_01"))
        if close_local is not None and not row.get("currency_raw"):
            close_local *= local_multiplier

        fx_rate = parse_optional_money(row.get("fx_to_usd"))
        if fx_rate is None:
            fx_rate = (fx_rates.get(currency) or {}).get("rate")

        close_usd = parse_optional_money(row.get("close_usd"))
        if close_usd is None and close_local is not None and fx_rate is not None:
            close_usd = close_local * fx_rate

        entry = {
            "symbol": symbol,
            "yahoo": symbol,
            "currency": currency,
            "currencyRaw": raw_currency,
            "closeLocal": close_local,
            "closeUsd": close_usd,
            "fxToUsd": fx_rate,
            "date": row.get("date") or row.get("price_date") or "",
            "error": row.get("error") or row.get("price_error") or "",
            "source": row.get("source") or "snapshot",
            "status": "ok" if close_local is not None else "missing",
            "url": row.get("url") or "",
        }
        market_prices.append(entry)
        price_book[symbol] = entry

    return price_book, market_prices, fx_rates


def resolve_quote(row: dict, price_book: dict[str, dict], fx_rates: dict[str, dict]) -> tuple[str, str, float | None, float | None, float | None, dict]:
    symbol = row.get("yahoo") or row.get("symbol") or row.get("asset") or ""
    quote = price_book.get(symbol, {})
    raw_currency = (
        row.get("currency_raw")
        or row.get("currency")
        or quote.get("currencyRaw")
        or quote.get("currency")
        or "USD"
    ).strip() or "USD"
    currency, local_multiplier = normalize_currency(raw_currency)

    price_local = parse_optional_money(row.get("price_2026_06_01"))
    if price_local is None:
        price_local = quote.get("closeLocal")
    if price_local is None:
        price_local = parse_optional_money(row.get("currentPrice"))
    if price_local is not None and not row.get("currency_raw") and raw_currency != currency:
        price_local *= local_multiplier

    fx_rate = parse_optional_money(row.get("fx_to_usd"))
    if fx_rate is None:
        fx_rate = quote.get("fxToUsd")
    if fx_rate is None:
        fx_rate = (fx_rates.get(currency) or {}).get("rate")

    price_usd = parse_optional_money(row.get("price_usd"))
    if price_usd is None and price_local is not None and fx_rate is not None:
        price_usd = price_local * fx_rate

    return currency, raw_currency, price_local, price_usd, fx_rate, quote


def classify_action(move: dict, trade: float, threshold: float) -> str:
    if move.get("fixed"):
        return "Liquidez"
    if trade > threshold:
        return "Comprar"
    if trade < -threshold:
        return "Reduzir"
    return "Manter"


def aggregate_series(
    current_rows: list[dict],
    target_rows: list[dict],
    *,
    key_field: str,
    label_field: str,
    current_total: float,
    target_total: float,
    order: list[str] | None = None,
    palette: dict[str, str] | None = None,
) -> list[dict]:
    current_map: dict[str, dict] = {}
    target_map: dict[str, dict] = {}
    palette = palette or {}
    order = order or []

    for row in current_rows:
        key = row.get(key_field)
        if not key:
            continue
        value = float(row.get("currentValue") or 0.0)
        entry = current_map.get(key) or {"key": key, "label": row.get(label_field) or key, "value": 0.0, "count": 0}
        entry["value"] += value
        entry["count"] += 1
        if not entry["label"] and row.get(label_field):
            entry["label"] = row.get(label_field)
        current_map[key] = entry

    for row in target_rows:
        key = row.get(key_field)
        if not key:
            continue
        value = float(row.get("targetValue") or 0.0)
        entry = target_map.get(key) or {"key": key, "label": row.get(label_field) or key, "value": 0.0, "count": 0}
        entry["value"] += value
        entry["count"] += 1
        if not entry["label"] and row.get(label_field):
            entry["label"] = row.get(label_field)
        target_map[key] = entry

    order_set = set(order)
    ordered_keys: list[str] = []
    for key in order:
        if key in current_map or key in target_map:
            ordered_keys.append(key)
    for key in list(current_map.keys()) + list(target_map.keys()):
        if key not in order_set and key not in ordered_keys:
            ordered_keys.append(key)

    rows: list[dict] = []
    theme_lookup = {theme["id"]: theme for theme in THEMES}
    for key in ordered_keys:
        current = current_map.get(key) or {"key": key, "label": key, "value": 0.0, "count": 0}
        target = target_map.get(key) or {"key": key, "label": key, "value": 0.0, "count": 0}
        accent = palette.get(key) or theme_lookup.get(key, {}).get("accent") or "#8f99a8"
        current_weight = (current["value"] / current_total * 100) if current_total > 0 else 0.0
        target_weight = (target["value"] / target_total * 100) if target_total > 0 else 0.0
        rows.append(
            {
                "key": key,
                "label": current["label"] or target["label"] or theme_lookup.get(key, {}).get("label") or key,
                "accent": accent,
                "currentValue": current["value"],
                "targetValue": target["value"],
                "currentWeight": current_weight,
                "targetWeight": target_weight,
                "currentText": money(current["value"]),
                "targetText": money(target["value"]),
                "currentWeightText": pct(current_weight),
                "targetWeightText": pct(target_weight),
                "count": max(current["count"], target["count"]),
            }
        )

    if not order:
        rows.sort(key=lambda row: (-row["targetWeight"], -row["currentWeight"]))

    return rows


def build_model_snapshot(data: dict, scenario_id: str, capital: float) -> dict:
    scenario = next((item for item in data["scenarios"] if item["id"] == scenario_id), data["scenarios"][0])
    current_total = data["meta"]["currentPortfolioValue"] or 0.0
    threshold = max(1000.0, capital * 0.005)

    liquidity_target_pct = scenario["cashTargetPct"] + scenario["xovrTargetPct"] + scenario["bondTargetPct"]
    investable_pct = 100 - liquidity_target_pct

    fixed_weights = {
        "Cash": scenario["cashTargetPct"],
        "XOVR": scenario["xovrTargetPct"],
        "ECOPET_BOND": scenario["bondTargetPct"],
    }

    variable_moves: list[dict] = []
    for move in data["moves"]:
        if move.get("fixed"):
            continue
        multiplier = scenario["themeMultipliers"].get(move["themeId"], 1.0)
        variable_moves.append({**move, "rawWeight": move["baseWeightPct"] * multiplier})

    raw_sum = sum(move["rawWeight"] for move in variable_moves)
    scale = investable_pct / raw_sum if raw_sum > 0 else 1.0

    model_moves: list[dict] = []
    for move in data["moves"]:
        if move.get("fixed"):
            target_weight = fixed_weights.get(move["asset"], move["baseWeightPct"])
        else:
            target_weight = move["baseWeightPct"] * scenario["themeMultipliers"].get(move["themeId"], 1.0) * scale
        target_value = capital * target_weight / 100
        trade = target_value - (move.get("currentValue") or 0.0)
        current_weight = (move.get("currentValue") or 0.0) / current_total * 100 if current_total > 0 else 0.0
        model_moves.append(
            {
                **move,
                "targetWeight": target_weight,
                "targetValue": target_value,
                "trade": trade,
                "currentWeight": current_weight,
                "action": classify_action(move, trade, threshold),
            }
        )

    move_map = {move["asset"]: move for move in model_moves}
    current_positions: list[dict] = []
    for holding in data["holdings"]:
        model_move = move_map.get(holding["symbol"])
        target_value = model_move["targetValue"] if model_move else 0.0
        current_positions.append(
            {
                **holding,
                "targetValue": target_value,
                "targetWeight": model_move["targetWeight"] if model_move else 0.0,
                "gap": target_value - (holding.get("currentValue") or 0.0),
            }
        )

    theme_order = [theme["id"] for theme in data["themes"]]
    current_exposure_rows = [*data["moves"], *data["residuals"]]
    theme_series = aggregate_series(
        current_exposure_rows,
        model_moves,
        key_field="themeId",
        label_field="themeLabel",
        order=theme_order + ["residual"],
        current_total=current_total,
        target_total=capital,
    )
    region_series = aggregate_series(
        current_exposure_rows,
        model_moves,
        key_field="region",
        label_field="region",
        current_total=current_total,
        target_total=capital,
        palette=REGION_PALETTE,
    )
    currency_series = aggregate_series(
        current_exposure_rows,
        model_moves,
        key_field="currency",
        label_field="currency",
        current_total=current_total,
        target_total=capital,
        palette=CURRENCY_PALETTE,
    )

    risky_moves = sorted((move for move in model_moves if not move.get("fixed")), key=lambda move: move["targetWeight"], reverse=True)
    top_five_share = sum(move["targetWeight"] for move in risky_moves[:5])
    usd_share = next((row["targetWeight"] for row in currency_series if row["key"] == "USD"), 0.0)
    non_usd_share = max(0.0, 100 - usd_share)

    return {
        "scenario": scenario,
        "capital": capital,
        "currentTotal": current_total,
        "liquidityTargetPct": liquidity_target_pct,
        "liquidityTargetValue": capital * liquidity_target_pct / 100,
        "investablePct": investable_pct,
        "investableValue": capital * investable_pct / 100,
        "modelMoves": model_moves,
        "currentPositions": current_positions,
        "themeSeries": theme_series,
        "regionSeries": region_series,
        "currencySeries": currency_series,
        "topFiveShare": top_five_share,
        "nonUsdShare": non_usd_share,
    }


def build_public_payload(data: dict) -> dict:
    top_symbols = {item["symbol"] for item in data["study"]["topIdeas"]}
    public_market_prices = [row for row in data["marketPrices"] if row["symbol"] in top_symbols]
    return {
        "meta": data["meta"],
        "scenarios": data["scenarios"],
        "themes": data["themes"],
        "study": {
            "principles": data["study"]["principles"],
            "basketBlueprint": data["study"]["basketBlueprint"],
            "topIdeas": data["study"]["topIdeas"],
        },
        "marketPrices": public_market_prices,
    }


def build_exports(data: dict) -> dict:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    market_rows = []
    for row in data["marketPrices"]:
        market_rows.append(
            {
                "symbol": row["symbol"],
                "currency": row["currency"],
                "currency_raw": row["currencyRaw"],
                "close_local": format_price_export(row["closeLocal"]),
                "close_usd": format_price_export(row["closeUsd"]),
                "fx_to_usd": format_fx(row["fxToUsd"]),
                "date": row["date"],
                "status": row["status"],
                "source": row["source"],
                "error": row["error"],
            }
        )
    write_csv_rows(EXPORT_DIR / "market-prices.csv", market_rows)

    fx_map = {row["currency"]: row for row in data["fxRates"]}
    fx_rows = []
    for currency in sorted(fx_map.keys()):
        fx = fx_map[currency]
        fx_rows.append(
            {
                "currency": currency,
                "pair": fx.get("pair") or "",
                "rate_to_usd": format_fx(fx.get("rate")),
                "multiplier": format_fx(fx.get("multiplier")),
                "date": fx.get("date") or "",
                "error": fx.get("error") or "",
            }
        )
    write_csv_rows(EXPORT_DIR / "fx-rates.csv", fx_rows)

    scenario_rows = []
    scenario_files = []
    for scenario in data["scenarios"]:
        model = build_model_snapshot(data, scenario["id"], data["meta"]["targetCapital"])
        scenario_file = f"scenario-{scenario['id']}.csv"
        scenario_files.append({"id": scenario["id"], "label": scenario["label"], "file": scenario_file})
        rows = []
        for move in model["modelMoves"]:
            rows.append(
                {
                    "asset": move["asset"],
                    "theme": move["themeLabel"],
                    "region": move["region"],
                    "currency": move["currency"],
                    "current_value_usd": money(move["currentValue"]),
                    "target_value_usd": money(move["targetValue"]),
                    "trade_usd": money(move["trade"]),
                    "target_weight_pct": f"{move['targetWeight']:.2f}",
                    "action": move["action"],
                    "fixed": "yes" if move["fixed"] else "no",
                    "thesis": move["thesis"],
                }
            )
        write_csv_rows(EXPORT_DIR / scenario_file, rows)
        scenario_rows.append(
            {
                "scenario": scenario["id"],
                "label": scenario["label"],
                "capital_usd": money(model["capital"]),
                "liquidity_target_pct": pct(model["liquidityTargetPct"]),
                "investable_pct": pct(model["investablePct"]),
                "top_five_share": pct(model["topFiveShare"]),
                "non_usd_share": pct(model["nonUsdShare"]),
                "file": scenario_file,
            }
        )

    write_csv_rows(EXPORT_DIR / "scenario-summary.csv", scenario_rows)

    public_payload = build_public_payload(data)
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_DIR.joinpath("data.js").write_text(
        f"window.PORTFOLIO_PUBLIC_DATA = {json.dumps(public_payload, ensure_ascii=False, indent=2)};\n",
        encoding="utf-8",
    )

    return {
        "marketPricesFile": "exports/market-prices.csv",
        "fxRatesFile": "exports/fx-rates.csv",
        "scenarioSummaryFile": "exports/scenario-summary.csv",
        "scenarioFiles": scenario_files,
        "publicDataFile": "public/data.js",
    }


def build_themes() -> list[dict]:
    return [
        {
            **theme,
            "assetCount": len(theme["assets"]),
        }
        for theme in THEMES
    ]


def build_data(
    proposal_rows: list[dict[str, str]] | None = None,
    holdings_rows: list[dict[str, str]] | None = None,
    watch_rows: list[dict[str, str]] | None = None,
    price_rows: list[dict[str, str]] | None = None,
    *,
    write_outputs: bool = False,
) -> dict:
    proposal_rows = proposal_rows or read_csv(ROOT / "analysis_outputs" / "rebalance_proposal.csv")
    holdings_rows = holdings_rows or read_csv(ROOT / "analysis_outputs" / "ibkr_holdings_analysis.csv")
    watch_rows = watch_rows or read_csv(ROOT / "analysis_outputs" / "watchlist_analysis.csv")
    price_rows = price_rows or read_csv(ROOT / "analysis_outputs" / "prices_2026-06-01.csv")

    proposal_by_symbol = {row["asset"]: row for row in proposal_rows}
    holdings_by_symbol = {row["symbol"]: row for row in holdings_rows}

    price_date = next((row.get("date") for row in price_rows if row.get("date")), "")
    price_book, market_prices, fx_rates = build_price_book(price_rows, price_date or None)

    moves: list[dict] = []
    for row in proposal_rows:
        symbol = row["asset"]
        holding = holdings_by_symbol.get(symbol, {})
        theme_id = THEME_BY_ASSET.get(symbol, "tail")
        theme = next((item for item in THEMES if item["id"] == theme_id), THEMES[-1])
        currency, currency_raw, current_price_local, current_price_usd, fx_rate, quote = resolve_quote(holding or row, price_book, fx_rates)
        quantity = parse_optional_money(holding.get("quantity")) or 0.0
        current_value = parse_optional_money(row.get("current_value_usd"))
        if current_value is None and current_price_usd is not None:
            current_value = quantity * current_price_usd
        if current_value is None:
            current_value = 0.0
        target_value = parse_optional_money(row.get("target_value_usd")) or 0.0
        base_trade_value = parse_optional_money(row.get("trade_usd"))
        if base_trade_value is None:
            base_trade_value = target_value - current_value
        target_price_local = parse_optional_money(holding.get("target_dec_2026"))
        if target_price_local is None and current_price_local is not None:
            target_price_local = current_price_local * (1 + (parse_pct(holding.get("upside_to_target_pct")) / 100 if holding.get("upside_to_target_pct") else 0.0))
        target_price_usd = parse_optional_money(holding.get("target_dec_2026_usd"))
        if target_price_usd is None and target_price_local is not None and fx_rate is not None:
            target_price_usd = target_price_local * fx_rate
        moves.append(
            {
                "asset": symbol,
                "themeId": theme_id,
                "themeLabel": theme["label"],
                "category": theme["label"] if symbol in {"Cash", "XOVR", "ECOPET_BOND"} else row["asset"],
                "role": ROLE_BY_ASSET.get(symbol, "Posicao"),
                "region": infer_region(symbol, holding.get("yahoo", symbol)),
                "currency": currency,
                "currencyRaw": currency_raw,
                "fxToUsd": fx_rate,
                "baseWeightPct": parse_pct(row["target_weight_pct"]),
                "baseTargetValue": target_value,
                "currentValue": current_value,
                "currentValueLocal": quantity * current_price_local if current_price_local is not None else 0.0,
                "currentPrice": current_price_local if current_price_local is not None else 0.0,
                "currentPriceUsd": current_price_usd if current_price_usd is not None else 0.0,
                "baseTradeValue": base_trade_value,
                "targetPrice": target_price_local if target_price_local is not None else 0.0,
                "targetPriceUsd": target_price_usd if target_price_usd is not None else 0.0,
                "upsidePct": parse_pct(holding.get("upside_to_target_pct")),
                "bias": holding.get("action_bias", ""),
                "thesis": RATIONALS.get(symbol, holding.get("thesis", "")),
                "fixed": symbol in {"Cash", "XOVR", "ECOPET_BOND"},
                "priceDate": quote.get("date") or holding.get("price_date") or row.get("price_date") or "",
                "priceError": quote.get("error") or holding.get("price_error") or "",
            }
        )

    holdings: list[dict] = []
    for row in holdings_rows:
        symbol = row["symbol"]
        proposal = proposal_by_symbol.get(symbol)
        currency, currency_raw, current_price_local, current_price_usd, fx_rate, quote = resolve_quote(row, price_book, fx_rates)
        quantity = parse_optional_money(row.get("quantity")) or 0.0
        current_value_local = parse_optional_money(row.get("market_value_local"))
        if current_value_local is None and current_price_local is not None:
            current_value_local = quantity * current_price_local
        current_value = parse_optional_money(row.get("market_value_usd"))
        if current_value is None and current_price_usd is not None:
            current_value = quantity * current_price_usd
        if current_value is None:
            current_value = 0.0
        target_price_local = parse_optional_money(row.get("target_dec_2026"))
        if target_price_local is None and current_price_local is not None:
            target_price_local = current_price_local * (1 + (parse_pct(row.get("upside_to_target_pct")) / 100 if row.get("upside_to_target_pct") else 0.0))
        target_price_usd = parse_optional_money(row.get("target_dec_2026_usd"))
        if target_price_usd is None and target_price_local is not None and fx_rate is not None:
            target_price_usd = target_price_local * fx_rate
        target_value = parse_optional_money(row.get("target_value_usd"))
        if target_value is None and target_price_usd is not None:
            target_value = quantity * target_price_usd
        model_weight = parse_pct(proposal["target_weight_pct"]) if proposal else 0.0
        if current_value <= 0 and model_weight <= 0:
            continue
        theme_id = THEME_BY_ASSET.get(symbol, "tail") if proposal else "residual"
        theme = next((item for item in THEMES if item["id"] == theme_id), None)
        holdings.append(
            {
                "symbol": symbol,
                "name": symbol,
                "themeId": theme_id,
                "themeLabel": theme["label"] if theme else "Residual",
                "region": infer_region(symbol, row["yahoo"]),
                "currency": currency,
                "currencyRaw": currency_raw,
                "fxToUsd": fx_rate,
                "currentPrice": current_price_local if current_price_local is not None else 0.0,
                "currentPriceUsd": current_price_usd if current_price_usd is not None else 0.0,
                "targetPrice": target_price_local if target_price_local is not None else 0.0,
                "targetPriceUsd": target_price_usd if target_price_usd is not None else 0.0,
                "upsidePct": parse_pct(row.get("upside_to_target_pct")),
                "bias": row.get("action_bias", ""),
                "thesis": row.get("thesis", ""),
                "currentValueLocal": current_value_local if current_value_local is not None else 0.0,
                "currentValue": current_value,
                "modelTargetWeightPct": model_weight,
                "targetValue": target_value or 0.0,
                "status": "No modelo" if proposal else "Residual",
                "inModel": bool(proposal),
                "proposalSymbol": symbol if proposal else "",
                "priceDate": quote.get("date") or row.get("price_date") or "",
                "priceError": quote.get("error") or row.get("price_error") or "",
            }
        )

    residuals = [row for row in holdings if not row["inModel"]]

    watchlist: list[dict] = []
    for row in watch_rows:
        bucket, theme_id = WATCHLIST_BUCKETS.get(row["category"], (row["category"], "tail"))
        theme = next((item for item in THEMES if item["id"] == theme_id), THEMES[-1])
        currency, currency_raw, current_price_local, current_price_usd, fx_rate, quote = resolve_quote(row, price_book, fx_rates)
        target_price_local = parse_optional_money(row.get("target_dec_2026"))
        if target_price_local is None and current_price_local is not None:
            target_price_local = current_price_local * (1 + (parse_pct(row.get("upside_to_target_pct")) / 100 if row.get("upside_to_target_pct") else 0.0))
        target_price_usd = parse_optional_money(row.get("target_dec_2026_usd"))
        if target_price_usd is None and target_price_local is not None and fx_rate is not None:
            target_price_usd = target_price_local * fx_rate
        watchlist.append(
            {
                "name": row["name"],
                "symbol": row["symbol"],
                "yahoo": row["yahoo"],
                "themeId": theme_id,
                "themeLabel": theme["label"],
                "studyBucket": bucket,
                "category": row["category"],
                "region": infer_region(row["symbol"], row["yahoo"]),
                "currency": currency,
                "currencyRaw": currency_raw,
                "fxToUsd": fx_rate,
                "currentPrice": current_price_local if current_price_local is not None else 0.0,
                "currentPriceUsd": current_price_usd if current_price_usd is not None else 0.0,
                "targetPrice": target_price_local if target_price_local is not None else 0.0,
                "targetPriceUsd": target_price_usd if target_price_usd is not None else 0.0,
                "upsidePct": parse_pct(row.get("upside_to_target_pct")),
                "priority": row["priority"],
                "thesis": row["thesis"],
                "source": row["source"],
                "priceError": quote.get("error") or row.get("price_error") or "",
                "priceDate": quote.get("date") or row.get("price_date") or "",
            }
        )

    top_ideas = []
    watch_by_symbol = {row["symbol"]: row for row in watchlist}
    for symbol in TOP_IDEAS:
        row = watch_by_symbol.get(symbol)
        if row:
            top_ideas.append(
                {
                    "symbol": row["symbol"],
                    "name": row["name"],
                    "themeLabel": row["themeLabel"],
                    "studyBucket": row["studyBucket"],
                    "priority": row["priority"],
                    "currency": row["currency"],
                    "currentPrice": row["currentPrice"],
                    "currentPriceUsd": row["currentPriceUsd"],
                    "targetPrice": row["targetPrice"],
                    "targetPriceUsd": row["targetPriceUsd"],
                    "upsidePct": row["upsidePct"],
                    "thesis": row["thesis"],
                }
            )

    model_total = sum(row["currentValue"] for row in moves)
    residual_total = sum(row["currentValue"] for row in residuals)
    current_total = model_total + residual_total
    cash_current = next((row["currentValue"] for row in moves if row["asset"] == "Cash"), 0.0)
    liquidity_current = sum(row["currentValue"] for row in moves if row["asset"] in {"Cash", "XOVR", "ECOPET_BOND"})
    target_capital = sum(row["baseTargetValue"] for row in moves)

    data = {
        "meta": {
            "priceDate": price_date or "",
            "targetCapital": round(target_capital, 2),
            "currentPortfolioValue": round(current_total, 2),
            "modelPortfolioValue": round(model_total, 2),
            "residualValue": round(residual_total, 2),
            "cashCurrent": round(cash_current, 2),
            "liquidityCurrentValue": round(liquidity_current, 2),
            "cashTargetPct": 8.0,
            "cashMinimumPct": 5.0,
            "liquidityTargetPct": 15.0,
            "liquidityCurrentPct": round((liquidity_current / current_total * 100) if current_total else 0.0, 2),
            "residualCount": len(residuals),
            "modelAssetCount": len(moves),
            "holdingsCount": len(holdings),
            "watchlistCount": len(watchlist),
            "marketPriceCount": len(market_prices),
            "fxRateCount": max(0, len(fx_rates) - 1),
            "notes": [
                f"O modelo usa o fechamento mais recente do snapshot em {price_date or PRICE_DATE} e converte tudo para USD.",
                "Cash, XOVR e bond ECOPET formam a faixa de liquidez/defesa.",
                "Posicoes residuais fora do modelo aparecem separadas para nao mascarar risco.",
            ],
        },
        "scenarios": SCENARIOS,
        "themes": build_themes(),
        "study": {
            **STUDY,
            "topIdeas": top_ideas,
        },
        "marketPrices": market_prices,
        "fxRates": [
            {"currency": currency, **fx_rates[currency]}
            for currency in sorted(fx_rates.keys())
        ],
        "moves": moves,
        "holdings": holdings,
        "residuals": residuals,
        "watchlist": watchlist,
    }

    base_model = build_model_snapshot(data, data["scenarios"][0]["id"], target_capital)
    data["meta"]["baseTopFiveShare"] = round(base_model["topFiveShare"], 2)
    data["meta"]["nonUsdShare"] = round(base_model["nonUsdShare"], 2)

    if write_outputs:
        exports_summary = build_exports(data)
        data["exports"] = exports_summary
        OUT.write_text(f"window.PORTFOLIO_DATA = {json.dumps(data, ensure_ascii=False, indent=2)};\n", encoding="utf-8")
        print(f"Wrote {OUT}")
    return data


def main() -> None:
    build_data(write_outputs=True)


if __name__ == "__main__":
    main()
