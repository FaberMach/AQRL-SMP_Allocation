const data = window.PORTFOLIO_PUBLIC_DATA;
const STORAGE_KEY = "portfolio-global-model-state";

const scenarioMap = new Map(data.scenarios.map((scenario) => [scenario.id, scenario]));

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

const moneyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const pctFormatter = new Intl.NumberFormat("pt-BR", {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

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
      })
    );
  } catch {
    // Ignore storage failures.
  }
}

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

const storedState = loadStoredState();

const state = {
  scenarioId: data.scenarios.some((scenario) => scenario.id === storedState.scenarioId)
    ? storedState.scenarioId
    : data.scenarios[0]?.id ?? "study",
  capital:
    Number.isFinite(Number(storedState.capital)) && Number(storedState.capital) > 0
      ? Number(storedState.capital)
      : data.meta.targetCapital ?? data.meta.currentPortfolioValue ?? 0,
};

function currentCapital() {
  const parsed = Number(state.capital);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : data.meta.targetCapital;
}

function getScenario() {
  return scenarioMap.get(state.scenarioId) ?? data.scenarios[0];
}

function weightWidth(value) {
  if (!Number.isFinite(value) || value <= 0) {
    return 0;
  }
  return Math.max(2, Math.min(100, value));
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

function buildModel() {
  const scenario = getScenario();
  const capital = currentCapital();
  const liquidityTargetPct =
    scenario.cashTargetPct + scenario.xovrTargetPct + scenario.bondTargetPct;
  const investablePct = 100 - liquidityTargetPct;

  return {
    scenario,
    capital,
    liquidityTargetPct,
    liquidityTargetValue: (capital * liquidityTargetPct) / 100,
    investablePct,
    investableValue: (capital * investablePct) / 100,
  };
}

function renderHero(model) {
  document.getElementById("heroScenario").textContent = model.scenario.label;
  document.getElementById("heroScenarioDesc").textContent = model.scenario.description;
  document.getElementById("heroLiquidity").textContent = `${pct(model.liquidityTargetPct)} / ${money(model.liquidityTargetValue)}`;
  document.getElementById("heroInvestable").textContent = `${pct(model.investablePct)} / ${money(model.investableValue)}`;
  document.getElementById("heroPriceDate").textContent = data.meta.priceDate || "--";
  document.getElementById("heroTopIdeas").textContent = `${data.study.topIdeas.length} teses`;
}

function renderKpis(model) {
  document.getElementById("kpiCapital").textContent = money(model.capital);
  document.getElementById("kpiLiquidityCurrent").textContent = pct(data.meta.liquidityCurrentPct);
  document.getElementById("kpiMarketCount").textContent = `${data.meta.marketPriceCount}`;
  document.getElementById("kpiTopIdeas").textContent = `${data.study.topIdeas.length}`;
  document.getElementById("kpiNonUsd").textContent = pct(data.meta.nonUsdShare || 0);
  document.getElementById("themeCount").textContent = `${data.study.basketBlueprint.length} buckets`;
  document.getElementById("priceCoverage").textContent = `${data.meta.marketPriceCount} ativos / ${data.meta.fxRateCount} FX`;
}

function renderThemeBars() {
  const root = document.getElementById("themeBars");
  root.innerHTML = data.study.basketBlueprint
    .map((entry, index) => {
      const accent = data.themes[index % data.themes.length]?.accent ?? "#8f99a8";
      return `
        <div class="bar-row" style="--accent:${accent}">
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

function renderMarketPrices() {
  const rows = [...data.marketPrices].sort((a, b) => a.symbol.localeCompare(b.symbol));
  const root = document.getElementById("marketPriceTable");
  root.innerHTML = rows
    .map((row) => {
      const statusLabel = row.status === "ok" ? "Disponivel" : "Sem preco";
      const statusClass = row.status === "ok" ? "good" : "warn";
      const currencyAccent = {
        USD: "#4aa3df",
        CAD: "#7e8cff",
        AUD: "#2bc6a4",
        GBP: "#d08b2e",
        Other: "#8f99a8",
      }[row.currency] || "#8f99a8";

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

function renderTopIdeas() {
  document.getElementById("topIdeas").innerHTML = data.study.topIdeas
    .map((idea) => {
      const accent = {
        rare_earths: "#2bc6a4",
        uranium: "#c86df0",
        defense_space: "#7e8cff",
        ai_biotech: "#ff7a59",
      }[idea.studyBucket] || "#4aa3df";

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
            <span>${priceLabel(idea.currentPrice, idea.currency)} → ${priceLabel(idea.targetPrice, idea.currency)}</span>
          </div>
        </article>
      `;
    })
    .join("");
}

function refreshModel() {
  const model = buildModel();
  renderHero(model);
  renderKpis(model);
}

function init() {
  document.getElementById("capitalInput").value = currentCapital();
  renderScenarioTray();
  renderThemeBars();
  renderMarketPrices();
  renderTopIdeas();
  refreshModel();

  document.getElementById("capitalInput").addEventListener("input", (event) => {
    state.capital = Number(event.target.value) || currentCapital();
    persistState();
    refreshModel();
  });
}

persistState();
init();
