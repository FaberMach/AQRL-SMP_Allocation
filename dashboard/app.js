const data = window.PORTFOLIO_DATA;
const STORAGE_KEY = "portfolio-global-model-state";

const themeMap = new Map(data.themes.map((theme) => [theme.id, theme]));
themeMap.set("residual", {
  id: "residual",
  label: "Residual",
  description: "Posicoes fora do modelo principal.",
  accent: "#ff7a59",
  assets: [],
});

const scenarioMap = new Map(data.scenarios.map((scenario) => [scenario.id, scenario]));
const themeOrder = [...data.themes.map((theme) => theme.id), "residual"];
const filters = ["Todos", "Comprar", "Reduzir", "Manter", "Liquidez"];

function loadStoredState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return {};
    }
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

function persistState() {
  try {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        scenarioId: state.scenarioId,
        capital: state.capital,
        filter: state.filter,
        sort: state.sort,
      })
    );
  } catch {
    // Ignore storage errors in private browsing / restricted contexts.
  }
}

const REGION_PALETTE = {
  "United States": "#4aa3df",
  Canada: "#7e8cff",
  Australia: "#2bc6a4",
  "United Kingdom": "#d08b2e",
  Brazil: "#ff7a59",
  Colombia: "#c86df0",
  Argentina: "#5b8cff",
  Other: "#8f99a8",
};

const currencyPriceFormatter = new Intl.NumberFormat("en-US", {
  minimumFractionDigits: 0,
  maximumFractionDigits: 4,
});

const usdPriceFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  minimumFractionDigits: 2,
  maximumFractionDigits: 4,
});

const fxFormatter = new Intl.NumberFormat("en-US", {
  minimumFractionDigits: 4,
  maximumFractionDigits: 6,
});

const CURRENCY_PALETTE = {
  USD: "#4aa3df",
  CAD: "#7e8cff",
  AUD: "#2bc6a4",
  GBP: "#d08b2e",
  Other: "#8f99a8",
};

const storedState = loadStoredState();

const state = {
  scenarioId: data.scenarios.some((scenario) => scenario.id === storedState.scenarioId)
    ? storedState.scenarioId
    : data.scenarios[0]?.id ?? "study",
  capital:
    Number.isFinite(Number(storedState.capital)) && Number(storedState.capital) > 0
      ? Number(storedState.capital)
      : data.meta.targetCapital ?? data.meta.currentPortfolioValue ?? 0,
  filter: filters.includes(storedState.filter) ? storedState.filter : "Todos",
  sort: ["absTrade", "targetWeight", "theme"].includes(storedState.sort)
    ? storedState.sort
    : "absTrade",
};

const moneyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const pctFormatter = new Intl.NumberFormat("pt-BR", {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

function money(value) {
  return moneyFormatter.format(Number.isFinite(value) ? value : 0);
}

function pct(value) {
  return `${pctFormatter.format(Number.isFinite(value) ? value : 0)}%`;
}

function stockPrice(value) {
  return currencyPriceFormatter.format(Number.isFinite(value) ? value : 0);
}

function usdPrice(value) {
  return usdPriceFormatter.format(Number.isFinite(value) ? value : 0);
}

function fxRate(value) {
  return fxFormatter.format(Number.isFinite(value) ? value : 0);
}

function priceLabel(value, currency) {
  if (!value || value === "0.00" || value === "0") {
    return "Sem preco";
  }
  return `${stockPrice(Number(value))} ${currency || ""}`.trim();
}

function currentCapital() {
  const parsed = Number(state.capital);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : data.meta.targetCapital;
}

function getScenario() {
  return scenarioMap.get(state.scenarioId) ?? data.scenarios[0];
}

function getThemeAccent(themeId) {
  return themeMap.get(themeId)?.accent ?? "#8f99a8";
}

function getThemeLabel(themeId) {
  return themeMap.get(themeId)?.label ?? themeId;
}

function weightWidth(value) {
  if (!Number.isFinite(value) || value <= 0) {
    return 0;
  }
  return Math.max(2, Math.min(100, value));
}

function classifyAction(move, trade, threshold) {
  if (move.fixed) {
    return "Liquidez";
  }
  if (trade > threshold) {
    return "Comprar";
  }
  if (trade < -threshold) {
    return "Reduzir";
  }
  return "Manter";
}

function actionClass(action) {
  return {
    Comprar: "buy",
    Reduzir: "sell",
    Manter: "hold",
    Liquidez: "liquidity",
  }[action] || "hold";
}

function statusClass(status) {
  return {
    "No modelo": "good",
    Residual: "warn",
  }[status] || "neutral";
}

function aggregateSeries(currentRows, targetRows, options) {
  const { keyField, labelField, order = [], currentTotal, targetTotal, palette = {} } = options;

  const currentMap = new Map();
  const targetMap = new Map();

  for (const row of currentRows) {
    const key = row[keyField];
    if (!key) {
      continue;
    }
    const value = Number(row.currentValue) || 0;
    const entry = currentMap.get(key) ?? {
      key,
      label: row[labelField] || key,
      value: 0,
      count: 0,
    };
    entry.value += value;
    entry.count += 1;
    if (!entry.label && row[labelField]) {
      entry.label = row[labelField];
    }
    currentMap.set(key, entry);
  }

  for (const row of targetRows) {
    const key = row[keyField];
    if (!key) {
      continue;
    }
    const value = Number(row.targetValue) || 0;
    const entry = targetMap.get(key) ?? {
      key,
      label: row[labelField] || key,
      value: 0,
      count: 0,
    };
    entry.value += value;
    entry.count += 1;
    if (!entry.label && row[labelField]) {
      entry.label = row[labelField];
    }
    targetMap.set(key, entry);
  }

  const orderSet = new Set(order);
  const orderedKeys = [];
  for (const key of order) {
    if (currentMap.has(key) || targetMap.has(key)) {
      orderedKeys.push(key);
    }
  }
  for (const key of [...currentMap.keys(), ...targetMap.keys()]) {
    if (!orderSet.has(key) && !orderedKeys.includes(key)) {
      orderedKeys.push(key);
    }
  }

  const rows = orderedKeys.map((key) => {
    const current = currentMap.get(key) ?? { key, label: key, value: 0, count: 0 };
    const target = targetMap.get(key) ?? { key, label: key, value: 0, count: 0 };
    const theme = themeMap.get(key);
    const accent = palette[key] || theme?.accent || "#8f99a8";

    return {
      key,
      label: current.label || target.label || theme?.label || key,
      accent,
      currentValue: current.value,
      targetValue: target.value,
      currentWeight: currentTotal > 0 ? (current.value / currentTotal) * 100 : 0,
      targetWeight: targetTotal > 0 ? (target.value / targetTotal) * 100 : 0,
      currentText: money(current.value),
      targetText: money(target.value),
      currentWeightText: pct(currentTotal > 0 ? (current.value / currentTotal) * 100 : 0),
      targetWeightText: pct(targetTotal > 0 ? (target.value / targetTotal) * 100 : 0),
      count: Math.max(current.count, target.count),
    };
  });

  if (!order.length) {
    rows.sort((a, b) => b.targetWeight - a.targetWeight || b.currentWeight - a.currentWeight);
  }

  return rows;
}

function buildModel() {
  const scenario = getScenario();
  const capital = currentCapital();
  const currentTotal = data.meta.currentPortfolioValue || 0;
  const threshold = Math.max(1000, capital * 0.005);

  const liquidityTargetPct =
    scenario.cashTargetPct + scenario.xovrTargetPct + scenario.bondTargetPct;
  const investablePct = 100 - liquidityTargetPct;

  const fixedWeights = {
    Cash: scenario.cashTargetPct,
    XOVR: scenario.xovrTargetPct,
    ECOPET_BOND: scenario.bondTargetPct,
  };

  const variableMoves = data.moves
    .filter((move) => !move.fixed)
    .map((move) => {
      const multiplier = scenario.themeMultipliers[move.themeId] ?? 1;
      return {
        ...move,
        rawWeight: move.baseWeightPct * multiplier,
      };
    });

  const rawSum = variableMoves.reduce((sum, move) => sum + move.rawWeight, 0);
  const scale = rawSum > 0 ? investablePct / rawSum : 1;

  const modelMoves = data.moves.map((move) => {
    const targetWeight = move.fixed
      ? fixedWeights[move.asset] ?? move.baseWeightPct
      : move.baseWeightPct * (scenario.themeMultipliers[move.themeId] ?? 1) * scale;
    const targetValue = (capital * targetWeight) / 100;
    const trade = targetValue - move.currentValue;
    const currentWeight = currentTotal > 0 ? (move.currentValue / currentTotal) * 100 : 0;

    return {
      ...move,
      targetWeight,
      targetValue,
      trade,
      currentWeight,
      action: classifyAction(move, trade, threshold),
    };
  });

  const moveMap = new Map(modelMoves.map((move) => [move.asset, move]));
  const currentPositions = data.holdings.map((holding) => {
    const modelMove = moveMap.get(holding.symbol);
    const targetValue = modelMove?.targetValue ?? 0;
    const targetWeight = modelMove?.targetWeight ?? 0;
    const gap = targetValue - holding.currentValue;

    return {
      ...holding,
      targetValue,
      targetWeight,
      gap,
    };
  });

  const currentExposureRows = [...data.moves, ...data.residuals];

  const themeSeries = aggregateSeries(
    currentExposureRows,
    modelMoves,
    {
      keyField: "themeId",
      labelField: "themeLabel",
      order: themeOrder,
      currentTotal,
      targetTotal: capital,
    }
  );

  const regionSeries = aggregateSeries(
    currentExposureRows,
    modelMoves,
    {
      keyField: "region",
      labelField: "region",
      currentTotal,
      targetTotal: capital,
      palette: REGION_PALETTE,
    }
  );

  const currencySeries = aggregateSeries(
    currentExposureRows,
    modelMoves,
    {
      keyField: "currency",
      labelField: "currency",
      currentTotal,
      targetTotal: capital,
      palette: CURRENCY_PALETTE,
    }
  );

  const riskyMoves = modelMoves
    .filter((move) => !move.fixed)
    .slice()
    .sort((a, b) => b.targetWeight - a.targetWeight);

  const topFiveShare = riskyMoves.slice(0, 5).reduce((sum, move) => sum + move.targetWeight, 0);
  const usdShare = currencySeries.find((row) => row.key === "USD")?.targetWeight ?? 0;
  const nonUsdShare = Math.max(0, 100 - usdShare);

  return {
    scenario,
    capital,
    currentTotal,
    liquidityTargetPct,
    liquidityTargetValue: (capital * liquidityTargetPct) / 100,
    investablePct,
    investableValue: (capital * investablePct) / 100,
    modelMoves,
    currentPositions,
    themeSeries,
    regionSeries,
    currencySeries,
    topFiveShare,
    nonUsdShare,
  };
}

function renderScenarioTray() {
  const root = document.getElementById("scenarioTray");
  root.innerHTML = data.scenarios
    .map((scenario) => {
      const active = state.scenarioId === scenario.id ? "active" : "";
      const liquidityPct =
        scenario.cashTargetPct + scenario.xovrTargetPct + scenario.bondTargetPct;

      return `
        <button class="scenario-chip ${active}" data-scenario="${scenario.id}" type="button" role="tab" aria-selected="${state.scenarioId === scenario.id}">
          <strong>${scenario.label}</strong>
          <span>${pct(scenario.cashTargetPct)} cash · ${pct(liquidityPct)} liquidez</span>
        </button>
      `;
    })
    .join("");

  root.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      state.scenarioId = button.dataset.scenario;
      persistState();
      renderScenarioTray();
      refreshModel();
    });
  });
}

function renderFilters() {
  const root = document.getElementById("filterButtons");
  root.innerHTML = filters
    .map(
      (filter) =>
        `<button class="${state.filter === filter ? "active" : ""}" data-filter="${filter}" type="button">${filter}</button>`
    )
    .join("");

  root.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      state.filter = button.dataset.filter;
      persistState();
      renderFilters();
      renderTradeTable();
    });
  });
}

function renderHero(model) {
  document.getElementById("heroScenario").textContent = model.scenario.label;
  document.getElementById("heroScenarioDesc").textContent = model.scenario.description;
  document.getElementById("heroLiquidity").textContent = `${pct(model.liquidityTargetPct)} / ${money(model.liquidityTargetValue)}`;
  document.getElementById("heroInvestable").textContent = `${pct(model.investablePct)} / ${money(model.investableValue)}`;
  document.getElementById("heroResiduals").textContent = `${data.meta.residualCount} / ${money(data.meta.residualValue)}`;
  document.getElementById("heroPriceDate").textContent = data.meta.priceDate || "--";
}

function renderKpis(model) {
  document.getElementById("kpiCapital").textContent = money(model.capital);
  document.getElementById("kpiLiquidityCurrent").textContent = pct(data.meta.liquidityCurrentPct);
  document.getElementById("kpiInvestable").textContent = money(model.investableValue);
  document.getElementById("kpiConcentration").textContent = pct(model.topFiveShare);
  document.getElementById("kpiNonUsd").textContent = pct(model.nonUsdShare);
  document.getElementById("kpiResidualCount").textContent = `${data.meta.residualCount}`;
  document.getElementById("themeCount").textContent = `${model.themeSeries.length} buckets`;
  document.getElementById("priceCoverage").textContent = `${data.meta.marketPriceCount} ativos / ${data.meta.fxRateCount} FX`;
}

function renderBars(containerId, rows, options = {}) {
  const root = document.getElementById(containerId);
  root.innerHTML = rows
    .map((row) => {
      const currentWidth = weightWidth(row.currentWeight);
      const targetWidth = weightWidth(row.targetWeight);
      const chips = options.chips?.(row) || "";

      return `
        <div class="bar-row" style="--accent:${row.accent}">
          <div class="bar-label">
            <strong>${row.label}</strong>
            <span>${row.currentWeightText} atual · ${row.targetWeightText} alvo</span>
            <small>${row.currentText} atual · ${row.targetText} alvo</small>
          </div>
          <div class="bar-track">
            <span class="bar current" style="width:${currentWidth}%"></span>
            <span class="bar target" style="width:${targetWidth}%"></span>
          </div>
          ${chips ? `<div class="row-chips">${chips}</div>` : ""}
        </div>
      `;
    })
    .join("");
}

function renderThemeBars(model) {
  renderBars("themeBars", model.themeSeries);
}

function renderGeoBars(model) {
  renderBars("geoBars", model.regionSeries);
}

function renderCurrencyBars(model) {
  renderBars("currencyBars", model.currencySeries);
}

function renderTradeTable(model) {
  const rows = model.modelMoves
    .map((move) => ({ ...move, displayAction: move.action }))
    .filter((move) => state.filter === "Todos" || move.displayAction === state.filter);

  if (state.sort === "targetWeight") {
    rows.sort((a, b) => b.targetWeight - a.targetWeight || Math.abs(b.trade) - Math.abs(a.trade));
  } else if (state.sort === "theme") {
    rows.sort(
      (a, b) =>
        a.themeLabel.localeCompare(b.themeLabel) ||
        Math.abs(b.trade) - Math.abs(a.trade)
    );
  } else {
    rows.sort((a, b) => Math.abs(b.trade) - Math.abs(a.trade));
  }

  document.getElementById("tradeTable").innerHTML = rows
    .map((move) => {
      const theme = themeMap.get(move.themeId);
      return `
        <tr>
          <td>
            <strong>${move.asset}</strong>
            <span class="sub">${move.role}</span>
          </td>
          <td><span class="badge theme" style="--badge:${theme?.accent ?? move.accent}">${move.themeLabel}</span></td>
          <td><span class="badge region" style="--badge:${REGION_PALETTE[move.region] ?? REGION_PALETTE.Other}">${move.region}</span></td>
          <td>${money(move.currentValue)}</td>
          <td>${money(move.targetValue)}</td>
          <td class="${move.trade >= 0 ? "positive" : "negative"}">${move.trade >= 0 ? "+" : ""}${money(move.trade)}</td>
          <td><span class="badge ${actionClass(move.displayAction)}">${move.displayAction}</span></td>
          <td>${move.thesis}</td>
        </tr>
      `;
    })
    .join("");
}

function formatTargetPrice(value, currency) {
  if (!value || value === "0.00" || value === "0") {
    return "Sem meta";
  }
  return `${stockPrice(Number(value))} ${currency}`.trim();
}

function renderHoldingsTable() {
  const rows = [...data.holdings].sort(
    (a, b) =>
      Number(b.inModel) - Number(a.inModel) ||
      b.currentValue - a.currentValue
  );

  document.getElementById("holdingsTable").innerHTML = rows
    .map((row) => {
      const badgeClass = statusClass(row.status);
      const theme = themeMap.get(row.themeId);
      return `
        <tr class="${row.status === "Residual" ? "residual-row" : ""}">
          <td>
            <strong>${row.symbol}</strong>
            <span class="sub">${theme?.label ?? row.themeLabel}</span>
          </td>
          <td><span class="badge ${badgeClass}">${row.status}</span></td>
          <td>
            <strong>${priceLabel(row.currentPrice, row.currency)}</strong>
            <span class="sub">${row.priceError ? "Sem preco" : usdPrice(row.currentPriceUsd)}</span>
          </td>
          <td>
            <strong>${formatTargetPrice(row.targetPrice, row.currency)}</strong>
            <span class="sub">${row.priceError ? "Sem preco" : usdPrice(row.targetPriceUsd)}</span>
          </td>
          <td>${pct(row.upsidePct)}</td>
          <td>${row.bias}</td>
        </tr>
      `;
    })
    .join("");
}

function renderWatchlistTable() {
  const order = { alta: 0, media: 1, baixa: 2 };
  const rows = [...data.watchlist].sort(
    (a, b) =>
      (order[a.priority] ?? 9) - (order[b.priority] ?? 9) ||
      b.upsidePct - a.upsidePct
  );

  document.getElementById("watchlistTable").innerHTML = rows
    .map((row) => {
      return `
        <tr>
          <td>
            <strong>${row.symbol}</strong>
            <span class="sub">${row.themeLabel}</span>
          </td>
          <td>${row.studyBucket}</td>
          <td>
            <strong>${priceLabel(row.currentPrice, row.currency)}</strong>
            <span class="sub">${row.priceError ? "Sem preco" : usdPrice(row.currentPriceUsd)}</span>
          </td>
          <td>
            <strong>${formatTargetPrice(row.targetPrice, row.currency)}</strong>
            <span class="sub">${row.priceError ? "Sem preco" : usdPrice(row.targetPriceUsd)}</span>
          </td>
          <td><span class="priority ${row.priority}">${row.priority}</span></td>
        </tr>
      `;
    })
    .join("");
}

function renderMarketPrices() {
  const rows = [...data.marketPrices].sort((a, b) => a.symbol.localeCompare(b.symbol));
  const root = document.getElementById("marketPriceTable");
  root.innerHTML = rows
    .map((row) => {
      const statusLabel = row.status === "ok" ? "Disponivel" : "Sem preco";
      const statusClass = row.status === "ok" ? "good" : "warn";
      const currencyAccent = CURRENCY_PALETTE[row.currency] ?? CURRENCY_PALETTE.Other;

      return `
        <tr>
          <td>
            <strong>${row.symbol}</strong>
            <span class="sub">${row.currencyRaw || row.currency}</span>
          </td>
          <td>${row.yahoo || row.symbol}</td>
          <td><span class="badge region" style="--badge:${currencyAccent}">${row.currency}</span></td>
          <td>
            <strong>${priceLabel(row.closeLocal, row.currency)}</strong>
            <span class="sub">${row.currencyRaw || row.currency}</span>
          </td>
          <td>${row.fxToUsd != null ? fxRate(row.fxToUsd) : "Sem FX"}</td>
          <td>${row.closeUsd != null ? usdPrice(row.closeUsd) : "Sem preco"}</td>
          <td>${row.date || "--"}</td>
          <td><span class="badge ${statusClass}">${statusLabel}</span></td>
        </tr>
      `;
    })
    .join("");
}

function renderExportLinks() {
  const root = document.getElementById("exportLinks");
  const exportsData = data.exports || {};
  const links = [];

  const pushLink = (href, label, extraClass = "") => {
    if (!href) {
      return;
    }
    links.push(
      `<a class="export-link ${extraClass}" href="${href}" download>${label}</a>`
    );
  };

  pushLink(exportsData.marketPricesFile, "Precos globais CSV");
  pushLink(exportsData.fxRatesFile, "FX rates CSV");
  pushLink(exportsData.scenarioSummaryFile, "Resumo dos cenarios");
  pushLink("public/data.js", "Versao publica sanitizada", "public");

  (exportsData.scenarioFiles || []).forEach((scenarioFile) => {
    pushLink(scenarioFile.file, scenarioFile.label);
  });

  root.innerHTML = links.join("");
}

function renderStudy() {
  document.getElementById("studyPrinciples").innerHTML = data.study.principles
    .map((principle) => `<span>${principle}</span>`)
    .join("");

  const palette = data.themes.map((theme) => theme.accent);
  document.getElementById("blueprintBars").innerHTML = data.study.basketBlueprint
    .map((entry, index) => {
      const accent = palette[index % palette.length];
      return `
        <div class="blueprint-row" style="--accent:${accent}">
          <div class="bar-label">
            <strong>${entry.label}</strong>
            <span>${pct(entry.weight)} do basket</span>
            <small>${entry.examples.join(" · ")}</small>
          </div>
          <div class="bar-track">
            <span class="bar current" style="width:${weightWidth(entry.weight)}%"></span>
            <span class="bar target" style="width:${weightWidth(entry.weight)}%"></span>
          </div>
        </div>
      `;
    })
    .join("");
}

function accentForStudyBucket(bucket) {
  if (bucket === "rare_earths" || bucket === "copper_lithium") {
    return themeMap.get("minerals")?.accent ?? "#2bc6a4";
  }
  if (bucket === "uranium" || bucket === "nuclear") {
    return themeMap.get("uranium")?.accent ?? "#c86df0";
  }
  if (bucket === "defense_space") {
    return themeMap.get("defense_space")?.accent ?? "#7e8cff";
  }
  if (bucket === "ai_biotech") {
    return themeMap.get("tail")?.accent ?? "#ff7a59";
  }
  return themeMap.get("quality")?.accent ?? "#4aa3df";
}

function renderTopIdeas() {
  document.getElementById("topIdeas").innerHTML = data.study.topIdeas
    .map((idea) => {
      const accent = accentForStudyBucket(idea.studyBucket);
      return `
        <article class="idea-card" style="--accent:${accent}">
          <div class="idea-head">
            <strong>${idea.symbol}</strong>
            <span class="priority ${idea.priority}">${idea.priority}</span>
          </div>
          <h3>${idea.name}</h3>
          <p class="idea-meta">${idea.themeLabel} · ${idea.studyBucket}</p>
          <p>${idea.thesis}</p>
          <div class="idea-foot">
            <span>${pct(idea.upsidePct)} de upside</span>
            <span>${priceLabel(idea.currentPrice, idea.currency)} → ${formatTargetPrice(idea.targetPrice, idea.currency)}</span>
          </div>
        </article>
      `;
    })
    .join("");
}

function refreshModel() {
  const model = buildModel();
  lastModel = model;
  renderHero(model);
  renderKpis(model);
  renderThemeBars(model);
  renderGeoBars(model);
  renderCurrencyBars(model);
  renderTradeTable(model);
}

let lastModel = null;

function init() {
  document.getElementById("capitalInput").value = currentCapital();
  document.getElementById("sortSelect").value = state.sort;
  renderScenarioTray();
  renderFilters();
  renderMarketPrices();
  renderExportLinks();
  renderStudy();
  renderTopIdeas();
  renderHoldingsTable();
  renderWatchlistTable();
  refreshModel();

  document.getElementById("capitalInput").addEventListener("input", (event) => {
    state.capital = Number(event.target.value) || currentCapital();
    persistState();
    refreshModel();
  });

  document.getElementById("sortSelect").addEventListener("change", (event) => {
    state.sort = event.target.value;
    persistState();
    if (lastModel) {
      renderTradeTable(lastModel);
    }
  });

  persistState();
}

init();
