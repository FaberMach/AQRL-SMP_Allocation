const data = window.PORTFOLIO_DATA;

const state = {
  filter: "Todos",
  sort: "absTrade",
};

const filters = ["Todos", "Comprar", "Vender", "Manter", "Cash/Equivalentes"];

const money = (value) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);

const pct = (value) =>
  new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(value) + "%";

function actionFor(move) {
  if (move.category === "Cash/Equivalentes") return "Cash/Equivalentes";
  if (move.currentValue === 0 && move.trade > 0) return "Comprar";
  if (move.trade > 1000) return "Comprar";
  if (move.trade < -1000) return "Vender";
  return "Manter";
}

function actionClass(action) {
  return {
    Comprar: "buy",
    Vender: "sell",
    Manter: "hold",
    "Cash/Equivalentes": "cash",
  }[action] || "hold";
}

function renderKpis() {
  document.getElementById("kpiTotal").textContent = money(data.meta.totalValue);
  document.getElementById("kpiCash").textContent = money(data.meta.cashCurrent);
  document.getElementById("kpiCashTarget").textContent = pct(data.meta.cashTargetPct);
  document.getElementById("kpiEquivalents").textContent = pct(data.meta.equivalentsPct);
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
      renderFilters();
      renderTrades();
    });
  });
}

function sortedMoves() {
  const rows = data.moves
    .map((move) => ({ ...move, action: actionFor(move) }))
    .filter((move) => state.filter === "Todos" || move.action === state.filter);

  if (state.sort === "targetWeight") {
    return rows.sort((a, b) => b.targetWeight - a.targetWeight);
  }
  if (state.sort === "category") {
    return rows.sort((a, b) => a.category.localeCompare(b.category) || Math.abs(b.trade) - Math.abs(a.trade));
  }
  return rows.sort((a, b) => Math.abs(b.trade) - Math.abs(a.trade));
}

function renderMajorMoves() {
  const moves = [...data.moves].sort((a, b) => Math.abs(b.trade) - Math.abs(a.trade)).slice(0, 8);
  document.getElementById("tradeCount").textContent = `${data.moves.length} ativos`;
  document.getElementById("majorMoves").innerHTML = moves
    .map((move) => {
      const action = actionFor(move);
      return `
        <article class="move-card ${actionClass(action)}">
          <div>
            <span class="ticker">${move.asset}</span>
            <strong>${move.trade >= 0 ? "+" : ""}${money(move.trade)}</strong>
          </div>
          <p>${move.rationale}</p>
        </article>
      `;
    })
    .join("");
}

function renderAllocationBars() {
  const max = Math.max(...data.moves.map((move) => Math.max(move.currentValue, move.targetValue)));
  const rows = [...data.moves].sort((a, b) => Math.abs(b.trade) - Math.abs(a.trade)).slice(0, 12);
  document.getElementById("allocationBars").innerHTML = rows
    .map((move) => {
      const currentWidth = Math.max(2, (move.currentValue / max) * 100);
      const targetWidth = Math.max(2, (move.targetValue / max) * 100);
      return `
        <div class="bar-row">
          <div class="bar-label">
            <strong>${move.asset}</strong>
            <span>${pct(move.targetWeight)} alvo</span>
          </div>
          <div class="bar-track">
            <span class="bar current" style="width:${currentWidth}%"></span>
            <span class="bar target" style="width:${targetWidth}%"></span>
          </div>
        </div>
      `;
    })
    .join("");
}

function renderTrades() {
  const rows = sortedMoves();
  document.getElementById("tradeTable").innerHTML = rows
    .map((move) => {
      const action = move.action;
      return `
        <tr>
          <td><strong>${move.asset}</strong><span class="sub">${move.category}</span></td>
          <td><span class="badge ${actionClass(action)}">${action}</span></td>
          <td>${money(move.currentValue)}</td>
          <td>${money(move.targetValue)}</td>
          <td class="${move.trade >= 0 ? "positive" : "negative"}">${move.trade >= 0 ? "+" : ""}${money(move.trade)}</td>
          <td>${pct(move.targetWeight)}</td>
          <td>${move.rationale}</td>
        </tr>
      `;
    })
    .join("");
}

function renderTheses() {
  document.getElementById("thesisGrid").innerHTML = data.theses
    .map(
      (thesis) => `
        <article class="thesis-card">
          <h3>${thesis.title}</h3>
          <div class="chips">${thesis.assets.map((asset) => `<span>${asset}</span>`).join("")}</div>
          <p>${thesis.rationale}</p>
        </article>
      `
    )
    .join("");
}

function priceLabel(row) {
  if (!row.price) return "Sem preco";
  return `${row.price} ${row.currency}`;
}

function renderReferenceTables() {
  document.getElementById("holdingsTable").innerHTML = data.holdings
    .map(
      (row) => `
        <tr>
          <td><strong>${row.symbol}</strong></td>
          <td>${priceLabel(row)}</td>
          <td>${row.target || "Sem meta"}</td>
          <td>${row.upside}%</td>
          <td>${row.bias}</td>
        </tr>
      `
    )
    .join("");

  document.getElementById("watchlistTable").innerHTML = data.watchlist
    .map(
      (row) => `
        <tr>
          <td><strong>${row.symbol}</strong><span class="sub">${row.yahoo}</span></td>
          <td>${row.category}</td>
          <td>${priceLabel(row)}</td>
          <td>${row.target || "Sem meta"}</td>
          <td><span class="priority ${row.priority}">${row.priority}</span></td>
        </tr>
      `
    )
    .join("");
}

function init() {
  renderKpis();
  renderFilters();
  renderMajorMoves();
  renderAllocationBars();
  renderTrades();
  renderTheses();
  renderReferenceTables();
  document.getElementById("sortSelect").addEventListener("change", (event) => {
    state.sort = event.target.value;
    renderTrades();
  });
}

init();
