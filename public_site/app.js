(() => {
  const data = window.PORTFOLIO_DATA || window.PORTFOLIO_PUBLIC_DATA || {};
  const view = document.body?.dataset?.view === "public" ? "public" : "full";
  const React = window.React;
  const ReactDOM = window.ReactDOM;
  const htm = window.htm;
  const MUI = window.MaterialUI;

  if (!React || !ReactDOM || !htm || !MUI) {
    const root = document.getElementById("root");
    if (root) {
      root.innerHTML = "<p>Falha ao carregar as bibliotecas do dashboard.</p>";
    }
    return;
  }

  const html = htm.bind(React.createElement);
  const {
    Alert,
    AppBar,
    Box,
    Button,
    Card,
    CardContent,
    Chip,
    Container,
    CssBaseline,
    Divider,
    FormControl,
    GlobalStyles,
    Grid,
    LinearProgress,
    MenuItem,
    Paper,
    Select,
    Stack,
    Tab,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Tabs,
    TextField,
    ThemeProvider,
    ToggleButton,
    ToggleButtonGroup,
    Toolbar,
    Tooltip,
    Typography,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    createTheme,
    useMediaQuery,
  } = MUI;

  const LOCAL_STORAGE_KEY = "portfolio-global-model-ui-v3";
  const tabConfig = {
    overview: {
      label: "Resumo",
      public: true,
      full: true,
    },
    market: {
      label: "Mercado",
      public: true,
      full: true,
    },
    execution: {
      label: "Execucao",
      public: false,
      full: true,
    },
    study: {
      label: "Estudo",
      public: true,
      full: true,
    },
    sectors: {
      label: "Setores",
      public: true,
      full: true,
    },
    risk: {
      label: "Risco",
      public: true,
      full: true,
    },
    simulator: {
      label: "Simulador",
      public: false,
      full: true,
    },
    universe: {
      label: "Universo",
      public: false,
      full: true,
    },
  };

  const themeAccentMap = new Map();
  for (const theme of Array.isArray(data.themes) ? data.themes : []) {
    themeAccentMap.set(theme.id, theme.accent);
  }
  themeAccentMap.set("residual", "#ff7a59");

  const regionPalette = {
    "United States": "#4aa3df",
    Canada: "#7e8cff",
    Australia: "#2bc6a4",
    "United Kingdom": "#d08b2e",
    Brazil: "#ff7a59",
    Colombia: "#c86df0",
    Argentina: "#5b8cff",
    Other: "#8f99a8",
  };

  const currencyPalette = {
    USD: "#4aa3df",
    CAD: "#7e8cff",
    AUD: "#2bc6a4",
    GBP: "#d08b2e",
    Other: "#8f99a8",
  };

  const sectorBucketMeta = {
    rare_earths: {
      label: "Terras raras",
      description: "Supply chain critica, geopolitica e rerating industrial.",
      themeId: "minerals",
    },
    uranium: {
      label: "Urânio",
      description: "Ciclo nuclear, energia estrategica e hedge de longo prazo.",
      themeId: "uranium",
    },
    copper_lithium: {
      label: "Cobre e lítio",
      description: "Eletrificacao, infraestrutura e metais de transicao.",
      themeId: "minerals",
    },
    defense_space: {
      label: "Defesa e espaço",
      description: "Drones, satelites, sensoriamento e autonomia.",
      themeId: "defense_space",
    },
    ai_biotech: {
      label: "AI biotech",
      description: "Biotech assistida por IA e opcionalidade de pesquisa.",
      themeId: "tail",
    },
    nuclear: {
      label: "Nuclear",
      description: "SMRs e infraestrutura de energia limpa com opcionalidade.",
      themeId: "uranium",
    },
    water: {
      label: "Água",
      description: "Tema defensivo ligado a escassez e infraestrutura.",
      themeId: "quality",
    },
    agriculture: {
      label: "Agricultura",
      description: "Demanda estrutural por produtividade e insumos.",
      themeId: "quality",
    },
    geral: {
      label: "Geral",
      description: "Bucket auxiliar para itens que nao se encaixam nos temas.",
      themeId: "quality",
    },
  };

  const riskProfiles = {
    balanced: {
      label: "Balanceado",
      minCash: 5,
      minLiquidity: 15,
      maxTopFive: 35,
      maxSingleName: 12,
      maxNonUsd: 60,
      maxSector: 28,
      maxResiduals: 6,
    },
    defensive: {
      label: "Defensivo",
      minCash: 8,
      minLiquidity: 18,
      maxTopFive: 30,
      maxSingleName: 10,
      maxNonUsd: 55,
      maxSector: 24,
      maxResiduals: 4,
    },
    convex: {
      label: "Convexo",
      minCash: 4,
      minLiquidity: 12,
      maxTopFive: 38,
      maxSingleName: 14,
      maxNonUsd: 65,
      maxSector: 32,
      maxResiduals: 8,
    },
  };

  const priorityPalette = {
    alta: "#46d1be",
    media: "#4aa3df",
    baixa: "#d08b2e",
  };

  const actionPalette = {
    Comprar: { color: "#46d1be", background: "rgba(70, 209, 190, 0.14)" },
    Reduzir: { color: "#ff7a59", background: "rgba(255, 122, 89, 0.14)" },
    Manter: { color: "#7e8cff", background: "rgba(126, 140, 255, 0.14)" },
    Liquidez: { color: "#d08b2e", background: "rgba(208, 139, 46, 0.14)" },
  };

  const statusPalette = {
    ok: { label: "Disponivel", color: "#46d1be", background: "rgba(70, 209, 190, 0.14)" },
    missing: { label: "Sem preco", color: "#ff7a59", background: "rgba(255, 122, 89, 0.14)" },
  };

  const usdWholeFormatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });
  const usdPreciseFormatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 4,
  });
  const priceFormatter = new Intl.NumberFormat("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 4,
  });
  const fxFormatter = new Intl.NumberFormat("en-US", {
    minimumFractionDigits: 4,
    maximumFractionDigits: 6,
  });
  const pctFormatter = new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  });
  const integerFormatter = new Intl.NumberFormat("en-US");

  function safeArray(value) {
    return Array.isArray(value) ? value : [];
  }

  function clamp(value, min, max) {
    return Math.min(max, Math.max(min, value));
  }

  function formatMoney(value) {
    return usdWholeFormatter.format(Number.isFinite(value) ? value : 0);
  }

  function formatPreciseMoney(value) {
    return usdPreciseFormatter.format(Number.isFinite(value) ? value : 0);
  }

  function formatPct(value) {
    return `${pctFormatter.format(Number.isFinite(value) ? value : 0)}%`;
  }

  function formatPrice(value) {
    if (!Number.isFinite(value) || value <= 0) {
      return "Sem preco";
    }
    return priceFormatter.format(value);
  }

  function formatStockPrice(value, currency) {
    if (!Number.isFinite(value) || value <= 0) {
      return "Sem preco";
    }
    return `${priceFormatter.format(value)} ${currency || ""}`.trim();
  }

  function formatFx(value) {
    if (!Number.isFinite(value) || value <= 0) {
      return "Sem FX";
    }
    return fxFormatter.format(value);
  }

  function formatDate(value) {
    return value || "--";
  }

  function formatPriority(value) {
    return value || "media";
  }

  function formatStudyBucket(value) {
    return value || "geral";
  }

  function getThemeAccent(themeId) {
    return themeAccentMap.get(themeId) || "#8f99a8";
  }

  function getStudyBucketAccent(bucket) {
    if (bucket === "rare_earths" || bucket === "copper_lithium") {
      return themeAccentMap.get("minerals") || "#2bc6a4";
    }
    if (bucket === "uranium" || bucket === "nuclear") {
      return themeAccentMap.get("uranium") || "#c86df0";
    }
    if (bucket === "defense_space") {
      return themeAccentMap.get("defense_space") || "#7e8cff";
    }
    if (bucket === "ai_biotech") {
      return themeAccentMap.get("tail") || "#ff7a59";
    }
    return themeAccentMap.get("quality") || "#4aa3df";
  }

  function readStoredPrefs() {
    try {
      const raw = window.localStorage.getItem(LOCAL_STORAGE_KEY);
      if (!raw) {
        return {};
      }
      const parsed = JSON.parse(raw);
      return parsed && typeof parsed === "object" ? parsed : {};
    } catch {
      return {};
    }
  }

  function storePrefs(nextPrefs) {
    try {
      window.localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(nextPrefs));
    } catch {
      // Ignore storage errors in restricted contexts.
    }
  }

  function aggregateSeries(currentRows, targetRows, options) {
    const {
      keyField,
      labelField,
      order = [],
      currentTotal = 0,
      targetTotal = 0,
      palette = {},
    } = options;

    const currentMap = new Map();
    const targetMap = new Map();

    for (const row of currentRows) {
      const key = row?.[keyField];
      if (!key) {
        continue;
      }
      const value = Number(row.currentValue) || 0;
      const entry = currentMap.get(key) || {
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
      const key = row?.[keyField];
      if (!key) {
        continue;
      }
      const value = Number(row.targetValue) || 0;
      const entry = targetMap.get(key) || {
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

    return orderedKeys
      .map((key) => {
        const current = currentMap.get(key) || { key, label: key, value: 0, count: 0 };
        const target = targetMap.get(key) || { key, label: key, value: 0, count: 0 };
        const accent = palette[key] || getThemeAccent(key);
        const currentWeight = currentTotal > 0 ? (current.value / currentTotal) * 100 : 0;
        const targetWeight = targetTotal > 0 ? (target.value / targetTotal) * 100 : 0;
        return {
          key,
          label: current.label || target.label || key,
          accent,
          currentValue: current.value,
          targetValue: target.value,
          currentWeight,
          targetWeight,
          currentWeightText: formatPct(currentWeight),
          targetWeightText: formatPct(targetWeight),
          currentText: formatMoney(current.value),
          targetText: formatMoney(target.value),
          delta: target.value - current.value,
          deltaText: formatMoney(target.value - current.value),
          count: Math.max(current.count, target.count),
        };
      })
      .filter((row) => row.currentValue !== 0 || row.targetValue !== 0);
  }

  function buildModel(portfolioData, scenario, capital) {
    const meta = portfolioData.meta || {};
    const currentTotal = Number(meta.currentPortfolioValue) || 0;
    const threshold = Math.max(1000, capital * 0.005);
    const liquidityTargetPct =
      (Number(scenario?.cashTargetPct) || 0) +
      (Number(scenario?.xovrTargetPct) || 0) +
      (Number(scenario?.bondTargetPct) || 0);
    const investablePct = clamp(100 - liquidityTargetPct, 0, 100);

    const fixedWeights = {
      Cash: Number(scenario?.cashTargetPct) || 0,
      XOVR: Number(scenario?.xovrTargetPct) || 0,
      ECOPET_BOND: Number(scenario?.bondTargetPct) || 0,
    };

    const moves = safeArray(portfolioData.moves);
    const residuals = safeArray(portfolioData.residuals);
    const variableRows = moves.filter((move) => !move.fixed);
    const themeOrder = safeArray(portfolioData.themes).map((theme) => theme.id);
    const themePalette = Object.fromEntries(
      safeArray(portfolioData.themes).map((theme) => [theme.id, theme.accent])
    );
    themePalette.residual = "#ff7a59";

    const themeMultipliers = scenario?.themeMultipliers || {};
    const rawSum = variableRows.reduce((sum, move) => {
      const baseWeight = Number(move.baseWeightPct) || 0;
      const multiplier = Number(themeMultipliers[move.themeId]) || 1;
      return sum + baseWeight * multiplier;
    }, 0);
    const scale = rawSum > 0 ? investablePct / rawSum : 1;

    const modelRows = moves.map((move) => {
      const baseWeight = Number(move.baseWeightPct) || 0;
      const multiplier = Number(themeMultipliers[move.themeId]) || 1;
      const targetWeight = move.fixed
        ? fixedWeights[move.asset] ?? baseWeight
        : baseWeight * multiplier * scale;
      const targetValue = (capital * targetWeight) / 100;
      const currentValue = Number(move.currentValue) || 0;
      const currentWeight = currentTotal > 0 ? (currentValue / currentTotal) * 100 : 0;
      const trade = targetValue - currentValue;
      const action = move.fixed
        ? "Liquidez"
        : trade > threshold
          ? "Comprar"
          : trade < -threshold
            ? "Reduzir"
            : "Manter";

      return {
        ...move,
        baseWeightPct: baseWeight,
        targetWeight,
        targetValue,
        currentWeight,
        trade,
        action,
        absTrade: Math.abs(trade),
      };
    });

    const currentExposureRows = [...moves, ...residuals];
    const themeRows = aggregateSeries(currentExposureRows, modelRows, {
      keyField: "themeId",
      labelField: "themeLabel",
      order: [...themeOrder, "residual"],
      currentTotal,
      targetTotal: capital,
      palette: themePalette,
    });
    const regionRows = aggregateSeries(currentExposureRows, modelRows, {
      keyField: "region",
      labelField: "region",
      currentTotal,
      targetTotal: capital,
      palette: regionPalette,
    });
    const currencyRows = aggregateSeries(currentExposureRows, modelRows, {
      keyField: "currency",
      labelField: "currency",
      currentTotal,
      targetTotal: capital,
      palette: currencyPalette,
    });

    const themeCatalog = safeArray(portfolioData.themes).map((theme) => {
      const assetCount = Number(theme.assetCount || safeArray(theme.assets).length || 0);
      return {
        ...theme,
        assetCount,
        share: 0,
        assetsLabel: safeArray(theme.assets).join(" · "),
      };
    });
    const themeCountTotal = themeCatalog.reduce((sum, item) => sum + item.assetCount, 0) || themeCatalog.length;
    for (const theme of themeCatalog) {
      theme.share = themeCountTotal > 0 ? (theme.assetCount / themeCountTotal) * 100 : 0;
    }

    const marketPrices = safeArray(portfolioData.marketPrices).map((row) => ({
      ...row,
      status: row.status || (Number.isFinite(row.closeUsd) ? "ok" : "missing"),
    }));
    const topFiveShare = modelRows
      .filter((row) => !row.fixed)
      .slice()
      .sort((a, b) => Number(b.targetWeight) - Number(a.targetWeight))
      .slice(0, 5)
      .reduce((sum, row) => sum + (Number(row.targetWeight) || 0), 0);
    const usdShare = currencyRows.find((row) => row.key === "USD")?.targetWeight || 0;
    const nonUsdShare = Math.max(0, 100 - usdShare);

    const holdings = safeArray(portfolioData.holdings)
      .map((row) => ({ ...row }))
      .sort(
        (a, b) =>
          Number(b.inModel) - Number(a.inModel) || Number(b.currentValue) - Number(a.currentValue)
      );
    const watchlist = safeArray(portfolioData.watchlist)
      .map((row) => ({ ...row }))
      .sort((a, b) => {
        const rank = { alta: 0, media: 1, baixa: 2 };
        return (rank[a.priority] ?? 9) - (rank[b.priority] ?? 9) || Number(b.upsidePct) - Number(a.upsidePct);
      });
    const tradeRows = modelRows
      .slice()
      .sort((a, b) => Number(b.absTrade) - Number(a.absTrade) || Number(b.targetWeight) - Number(a.targetWeight));

    return {
      capital,
      currentTotal,
      threshold,
      liquidityTargetPct,
      liquidityTargetValue: (capital * liquidityTargetPct) / 100,
      investablePct,
      investableValue: (capital * investablePct) / 100,
      modelRows,
      tradeRows,
      themeRows,
      regionRows,
      currencyRows,
      themeCatalog,
      marketPrices,
      holdings,
      watchlist,
      topFiveShare,
      nonUsdShare,
      marketOkCount: marketPrices.filter((row) => row.status === "ok").length,
      marketMissingCount: marketPrices.filter((row) => row.status !== "ok").length,
      hasTradeModel: moves.length > 0,
      hasHoldings: holdings.length > 0,
      hasWatchlist: watchlist.length > 0,
      hasExports: Boolean(portfolioData.exports),
      residualCount: Number(meta.residualCount) || residuals.length || 0,
      residualValue: Number(meta.residualValue) || 0,
    };
  }

  function resolveDefaultScenario(portfolioData) {
    const scenarios = safeArray(portfolioData.scenarios);
    return scenarios[0]?.id || "study";
  }

  function resolveScenario(portfolioData, scenarioId) {
    return safeArray(portfolioData.scenarios).find((scenario) => scenario.id === scenarioId) ||
      safeArray(portfolioData.scenarios)[0] || {
        id: "study",
        label: "Base",
        description: "",
        cashTargetPct: 0,
        xovrTargetPct: 0,
        bondTargetPct: 0,
        themeMultipliers: {},
      };
  }

  function normalizeText(value) {
    return String(value ?? "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .trim()
      .toLowerCase();
  }

  function normalizeSymbolKey(value) {
    return String(value ?? "")
      .trim()
      .toUpperCase()
      .replace(/\s+/g, "");
  }

  function normalizeCurrencyCode(value) {
    const code = normalizeSymbolKey(value);
    if (!code) {
      return "USD";
    }
    if (code === "GBX" || code === "GBPX") {
      return "GBP";
    }
    return code;
  }

  function parseFlexibleNumber(value) {
    if (value === null || value === undefined) {
      return 0;
    }
    const raw = String(value).trim();
    if (!raw) {
      return 0;
    }
    let cleaned = raw.replace(/[^0-9,.-]/g, "");
    const commaCount = (cleaned.match(/,/g) || []).length;
    const dotCount = (cleaned.match(/\./g) || []).length;
    if (commaCount > 0 && dotCount > 0) {
      if (cleaned.lastIndexOf(",") > cleaned.lastIndexOf(".")) {
        cleaned = cleaned.replace(/\./g, "").replace(/,/g, ".");
      } else {
        cleaned = cleaned.replace(/,/g, "");
      }
    } else if (commaCount > 0) {
      cleaned = cleaned.replace(/,/g, ".");
    }
    const parsed = Number(cleaned);
    return Number.isFinite(parsed) ? parsed : 0;
  }

  function detectCsvDelimiter(headerLine) {
    const semicolons = (headerLine.match(/;/g) || []).length;
    const commas = (headerLine.match(/,/g) || []).length;
    const tabs = (headerLine.match(/\t/g) || []).length;
    if (tabs > commas && tabs > semicolons) {
      return "\t";
    }
    if (semicolons > commas) {
      return ";";
    }
    return ",";
  }

  function parseCsvLine(line, delimiter) {
    const cells = [];
    let current = "";
    let quoted = false;
    for (let index = 0; index < line.length; index += 1) {
      const char = line[index];
      if (char === '"') {
        if (quoted && line[index + 1] === '"') {
          current += '"';
          index += 1;
        } else {
          quoted = !quoted;
        }
      } else if (char === delimiter && !quoted) {
        cells.push(current);
        current = "";
      } else {
        current += char;
      }
    }
    cells.push(current);
    return cells.map((cell) => cell.trim());
  }

  function normalizePortfolioHeader(value) {
    const key = normalizeText(value).replace(/\s+/g, "_");
    const headerMap = {
      symbol: "symbol",
      ticker: "symbol",
      ativo: "symbol",
      asset: "symbol",
      codigo: "symbol",
      code: "symbol",
      name: "name",
      nome: "name",
      quantidade: "quantity",
      qty: "quantity",
      shares: "quantity",
      units: "quantity",
      unitsheld: "quantity",
      price: "price",
      preco: "price",
      precounitario: "price",
      current_price: "price",
      last_price: "price",
      market_price: "price",
      value: "value",
      valor: "value",
      market_value: "value",
      current_value: "value",
      price_usd: "priceUsd",
      current_price_usd: "priceUsd",
      market_value_usd: "valueUsd",
      current_value_usd: "valueUsd",
      currency: "currency",
      moeda: "currency",
      ccy: "currency",
      fx_to_usd: "fxToUsd",
      fx: "fxToUsd",
      sector: "sector",
      setor: "sector",
      category: "sector",
      bucket: "sector",
      tema: "sector",
      thesis: "notes",
      tese: "notes",
      notes: "notes",
      observacao: "notes",
      observation: "notes",
      price_date: "priceDate",
      date: "priceDate",
    };
    return headerMap[key] || key;
  }

  function parsePortfolioCsv(text) {
    const normalized = String(text || "")
      .replace(/\r\n?/g, "\n")
      .trim();
    if (!normalized) {
      return [];
    }
    const lines = normalized.split("\n").filter((line) => line.trim().length > 0);
    if (!lines.length) {
      return [];
    }
    const delimiter = detectCsvDelimiter(lines[0]);
    const headers = parseCsvLine(lines[0], delimiter).map(normalizePortfolioHeader);
    return lines.slice(1).map((line) => {
      const values = parseCsvLine(line, delimiter);
      const entry = {};
      headers.forEach((header, index) => {
        entry[header] = values[index] ?? "";
      });
      return entry;
    });
  }

  function createPortfolioDraftRow(values = {}) {
    return {
      id:
        values.id ||
        `portfolio-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`,
      symbol: values.symbol || values.ticker || values.asset || "",
      name: values.name || values.symbol || values.ticker || "",
      quantity: values.quantity ?? "",
      price: values.price ?? "",
      value: values.value ?? values.valueUsd ?? "",
      currency: values.currency || "USD",
      sector: values.sector || values.category || "",
      notes: values.notes || "",
      priceUsd: values.priceUsd ?? "",
      valueUsd: values.valueUsd ?? "",
      fxToUsd: values.fxToUsd ?? "",
      priceDate: values.priceDate || "",
    };
  }

  function coercePortfolioDraftRows(rows) {
    return safeArray(rows)
      .map((row) => createPortfolioDraftRow(row))
      .filter((row) =>
        [
          row.symbol,
          row.name,
          row.quantity,
          row.price,
          row.value,
          row.currency,
          row.sector,
          row.notes,
        ].some((cell) => String(cell || "").trim().length > 0)
      );
  }

  function buildPortfolioDraftRowsFromData(portfolioData) {
    const rows = [];
    const currentRows = [
      ...safeArray(portfolioData.holdings),
      ...safeArray(portfolioData.residuals),
    ];
    for (const row of currentRows) {
      const currentValue = Number(row.currentValue) || 0;
      if (currentValue <= 0) {
        continue;
      }
      const currentPrice = Number(row.currentPrice) || 0;
      rows.push(
        createPortfolioDraftRow({
          symbol: row.symbol || row.asset || "",
          name: row.name || row.symbol || row.asset || "",
          quantity: currentPrice > 0 ? currentValue / currentPrice : "",
          price: currentPrice > 0 ? currentPrice : "",
          value: currentValue,
          currency: row.currency || "USD",
          sector: row.themeLabel || row.category || row.themeId || "",
          notes: row.thesis || row.bias || "",
          priceUsd: Number(row.currentPriceUsd) || "",
          valueUsd: currentValue,
          fxToUsd: Number(row.fxToUsd) || "",
          priceDate: row.priceDate || "",
        })
      );
    }
    return rows.sort((a, b) => parseFlexibleNumber(b.valueUsd || b.value) - parseFlexibleNumber(a.valueUsd || a.value));
  }

  function resolveSectorBucket(value) {
    const text = normalizeText(value);
    if (!text) {
      return "geral";
    }
    if (text.includes("rare") || text.includes("terra") || text.includes("earth")) {
      return "rare_earths";
    }
    if (text.includes("uran")) {
      return "uranium";
    }
    if (text.includes("cobre") || text.includes("liti") || text.includes("miner")) {
      return "copper_lithium";
    }
    if (text.includes("defens") || text.includes("espaco") || text.includes("space") || text.includes("satel")) {
      return "defense_space";
    }
    if (text.includes("biotech") || text.includes("biotech") || text.includes("ai")) {
      return "ai_biotech";
    }
    if (text.includes("nuclear") || text.includes("smr")) {
      return "nuclear";
    }
    if (text.includes("agua") || text.includes("water")) {
      return "water";
    }
    if (text.includes("agric")) {
      return "agriculture";
    }
    return "geral";
  }

  function buildSectorInsights(portfolioData) {
    const watchlistSource = safeArray(portfolioData.watchlist);
    const fallbackSource = safeArray(portfolioData.study?.topIdeas).map((idea) => ({
      ...idea,
      studyBucket: idea.studyBucket || resolveSectorBucket(idea.themeLabel || idea.category || idea.symbol),
      priority: idea.priority || "media",
      upsidePct: idea.upsidePct || 0,
      source: "Top ideas",
    }));
    const sourceRows = watchlistSource.length ? watchlistSource : fallbackSource;
    const groups = new Map();

    for (const row of sourceRows) {
      const bucket = row.studyBucket || resolveSectorBucket(row.category || row.themeLabel || row.symbol);
      const meta = sectorBucketMeta[bucket] || sectorBucketMeta.geral;
      const priorityScore = row.priority === "alta" ? 3 : row.priority === "media" ? 2 : 1;
      const upside = parseFlexibleNumber(row.upsidePct || row.upside_to_target_pct);
      const score = priorityScore * 10 + upside + (row.symbol && safeArray(portfolioData.study?.topIdeas).some((idea) => idea.symbol === row.symbol) ? 5 : 0);
      const current = groups.get(bucket) || {
        id: bucket,
        bucket,
        label: meta.label,
        description: meta.description,
        accent: getStudyBucketAccent(bucket),
        themeId: meta.themeId,
        items: [],
        totalScore: 0,
        totalUpside: 0,
      };
      current.items.push({
        symbol: row.symbol || "--",
        name: row.name || row.symbol || "--",
        upsidePct: upside,
        priority: row.priority || "media",
        thesis: row.thesis || "",
        source: row.source || "",
        currency: row.currency || "",
        score,
      });
      current.totalScore += score;
      current.totalUpside += upside;
      groups.set(bucket, current);
    }

    return Array.from(groups.values())
      .map((group) => {
        group.items.sort((left, right) => right.score - left.score || right.upsidePct - left.upsidePct);
        group.count = group.items.length;
        group.averageUpside = group.count ? group.totalUpside / group.count : 0;
        group.topPicks = group.items.slice(0, 3);
        group.bestPick = group.topPicks[0] || null;
        group.summary = group.topPicks
          .map((item) => `${item.symbol} (${formatPct(item.upsidePct)})`)
          .join(" · ");
        return group;
      })
      .sort((left, right) => right.totalScore - left.totalScore || right.averageUpside - left.averageUpside);
  }

  function buildImportedPortfolioModel(portfolioData, draftRows, scenario, capital) {
    const referenceMoves = safeArray(portfolioData.moves);
    const referenceResiduals = safeArray(portfolioData.residuals);
    const priceLookup = new Map();
    for (const row of safeArray(portfolioData.marketPrices)) {
      const symbolKey = normalizeSymbolKey(row.symbol || row.yahoo);
      if (symbolKey) {
        priceLookup.set(symbolKey, row);
      }
    }
    const fxLookup = new Map();
    for (const row of safeArray(portfolioData.fxRates)) {
      const currency = normalizeCurrencyCode(row.currency);
      if (currency) {
        fxLookup.set(currency, Number(row.rate) || 1);
      }
    }
    const moveLookup = new Map();
    for (const move of referenceMoves) {
      const key = normalizeSymbolKey(move.asset);
      if (key) {
        moveLookup.set(key, move);
      }
    }
    const residualLookup = new Map();
    for (const residual of referenceResiduals) {
      const key = normalizeSymbolKey(residual.symbol);
      if (key) {
        residualLookup.set(key, residual);
      }
    }

    const normalizedRows = coercePortfolioDraftRows(draftRows)
      .map((row) => {
        const symbolKey = normalizeSymbolKey(row.symbol || row.ticker || row.asset || row.name);
        const moveTemplate = moveLookup.get(symbolKey);
        const residualTemplate = residualLookup.get(symbolKey);
        const priceTemplate = priceLookup.get(symbolKey);
        const currencyRaw = row.currency || moveTemplate?.currencyRaw || residualTemplate?.currencyRaw || priceTemplate?.currency || "USD";
        const currency = normalizeCurrencyCode(currencyRaw);
        const fxRate =
          parseFlexibleNumber(row.fxToUsd) ||
          Number(moveTemplate?.fxToUsd) ||
          Number(residualTemplate?.fxToUsd) ||
          Number(priceTemplate?.fxToUsd) ||
          fxLookup.get(currency) ||
          1;
        const quantity = parseFlexibleNumber(row.quantity);
        const priceLocal =
          parseFlexibleNumber(row.price) ||
          parseFlexibleNumber(moveTemplate?.currentPrice) ||
          parseFlexibleNumber(residualTemplate?.currentPrice) ||
          parseFlexibleNumber(priceTemplate?.closeLocal);
        const priceUsd =
          parseFlexibleNumber(row.priceUsd) ||
          parseFlexibleNumber(moveTemplate?.currentPriceUsd) ||
          parseFlexibleNumber(residualTemplate?.currentPriceUsd) ||
          parseFlexibleNumber(priceTemplate?.closeUsd);
        const valueUsdInput =
          parseFlexibleNumber(row.valueUsd) ||
          parseFlexibleNumber(row.currentValueUsd);
        const valueLocalInput =
          parseFlexibleNumber(row.value) ||
          parseFlexibleNumber(row.currentValue);
        let currentValueUsd = 0;
        if (valueUsdInput > 0) {
          currentValueUsd = valueUsdInput;
        } else if (quantity > 0 && priceUsd > 0) {
          currentValueUsd = quantity * priceUsd;
        } else if (quantity > 0 && priceLocal > 0) {
          currentValueUsd = quantity * priceLocal * fxRate;
        } else if (valueLocalInput > 0) {
          currentValueUsd = valueLocalInput * fxRate;
        } else if (moveTemplate) {
          currentValueUsd = Number(moveTemplate.currentValue) || 0;
        } else if (residualTemplate) {
          currentValueUsd = Number(residualTemplate.currentValue) || 0;
        }
        const currentValueLocal =
          valueLocalInput > 0
            ? valueLocalInput
            : quantity > 0 && priceLocal > 0
              ? quantity * priceLocal
              : fxRate > 0
                ? currentValueUsd / fxRate
                : currentValueUsd;
        const currentPriceLocal =
          priceLocal > 0
            ? priceLocal
            : quantity > 0 && currentValueLocal > 0
              ? currentValueLocal / quantity
              : parseFlexibleNumber(moveTemplate?.currentPrice) ||
                parseFlexibleNumber(residualTemplate?.currentPrice) ||
                parseFlexibleNumber(priceTemplate?.closeLocal);
        const currentPriceUsd =
          priceUsd > 0
            ? priceUsd
            : quantity > 0 && currentValueUsd > 0
              ? currentValueUsd / quantity
              : parseFlexibleNumber(moveTemplate?.currentPriceUsd) ||
                parseFlexibleNumber(residualTemplate?.currentPriceUsd) ||
                parseFlexibleNumber(priceTemplate?.closeUsd) ||
                (currentPriceLocal > 0 ? currentPriceLocal * fxRate : 0);
        const sectorBucket = resolveSectorBucket(row.sector || row.category || row.notes || moveTemplate?.themeLabel || residualTemplate?.themeLabel);
        const sectorMeta = sectorBucketMeta[sectorBucket] || sectorBucketMeta.geral;

        return {
          id: row.id,
          symbol: symbolKey || normalizeSymbolKey(row.name) || row.name || "",
          name: row.name || moveTemplate?.asset || residualTemplate?.symbol || symbolKey,
          quantity,
          currentPriceLocal,
          currentPriceUsd,
          currentValueLocal,
          currentValueUsd,
          currency,
          currencyRaw,
          fxToUsd: fxRate,
          sectorBucket,
          sectorLabel: sectorMeta.label,
          notes: row.notes || "",
          sourceSymbol: symbolKey,
        };
      })
      .filter((row) => row.symbol && (row.currentValueUsd > 0 || row.quantity > 0 || row.currentPriceLocal > 0 || row.currentPriceUsd > 0));

    const normalizedLookup = new Map();
    for (const row of normalizedRows) {
      const key = normalizeSymbolKey(row.symbol);
      if (!key) {
        continue;
      }
      const existing = normalizedLookup.get(key);
      if (existing) {
        existing.quantity += row.quantity;
        existing.currentValueUsd += row.currentValueUsd;
        existing.currentValueLocal += row.currentValueLocal;
        existing.currentPriceLocal = row.currentPriceLocal || existing.currentPriceLocal;
        existing.currentPriceUsd = row.currentPriceUsd || existing.currentPriceUsd;
        existing.notes = existing.notes || row.notes;
        existing.sectorBucket = existing.sectorBucket || row.sectorBucket;
        existing.sectorLabel = existing.sectorLabel || row.sectorLabel;
      } else {
        normalizedLookup.set(key, { ...row });
      }
    }

    const uploadedRows = Array.from(normalizedLookup.values());
    const uploadedValue = uploadedRows.reduce((sum, row) => sum + (Number(row.currentValueUsd) || 0), 0);
    const uploadedCurrentLiquidityValue = uploadedRows.reduce((sum, row) => {
      return row.symbol === "Cash" || row.symbol === "XOVR" || row.symbol === "ECOPET_BOND"
        ? sum + (Number(row.currentValueUsd) || 0)
        : sum;
    }, 0);
    const uploadedCashValue = uploadedRows.reduce((sum, row) => {
      return row.symbol === "Cash" ? sum + (Number(row.currentValueUsd) || 0) : sum;
    }, 0);

    const baseRows = referenceMoves.map((move) => {
      const row = normalizedLookup.get(normalizeSymbolKey(move.asset));
      if (!row) {
        return {
          ...move,
          currentValue: 0,
          currentValueLocal: 0,
          currentPrice: Number(move.currentPrice) || 0,
          currentPriceUsd: Number(move.currentPriceUsd) || 0,
          currency: move.currency,
          currencyRaw: move.currencyRaw,
          fxToUsd: Number(move.fxToUsd) || 1,
        };
      }
      return {
        ...move,
        currentValue: row.currentValueUsd,
        currentValueLocal: row.currentValueLocal,
        currentPrice: row.currentPriceLocal,
        currentPriceUsd: row.currentPriceUsd,
        currency: row.currency,
        currencyRaw: row.currencyRaw,
        fxToUsd: row.fxToUsd,
        priceError: "",
      };
    });

    const baseLookup = new Set(baseRows.map((row) => normalizeSymbolKey(row.asset)));
    const residualRows = [];
    for (const row of uploadedRows) {
      if (baseLookup.has(normalizeSymbolKey(row.symbol))) {
        continue;
      }
      const residualTemplate = residualLookup.get(normalizeSymbolKey(row.symbol));
      const sectorMeta = sectorBucketMeta[row.sectorBucket] || sectorBucketMeta.geral;
      residualRows.push({
        ...(residualTemplate || {}),
        symbol: row.symbol,
        name: row.name || residualTemplate?.name || row.symbol,
        themeId: residualTemplate?.themeId || sectorMeta.themeId,
        themeLabel: residualTemplate?.themeLabel || sectorMeta.label,
        category: row.sectorLabel || residualTemplate?.category || sectorMeta.label,
        region: residualTemplate?.region || "Other",
        currency: row.currency,
        currencyRaw: row.currencyRaw,
        fxToUsd: row.fxToUsd,
        currentPrice: row.currentPriceLocal,
        currentPriceUsd: row.currentPriceUsd,
        targetPrice: residualTemplate?.targetPrice || 0,
        targetPriceUsd: residualTemplate?.targetPriceUsd || 0,
        currentValueLocal: row.currentValueLocal,
        currentValue: row.currentValueUsd,
        baseWeightPct: 0,
        baseTargetValue: 0,
        baseTradeValue: 0,
        upsidePct: residualTemplate?.upsidePct || 0,
        bias: row.notes || residualTemplate?.bias || "",
        thesis: row.notes || residualTemplate?.thesis || "Posição importada manualmente.",
        fixed: false,
        priceDate: residualTemplate?.priceDate || row.priceDate || portfolioData.meta?.priceDate || "",
        priceError: "",
      });
    }

    const simMeta = {
      ...portfolioData.meta,
      currentPortfolioValue: uploadedValue,
      holdingsCount: uploadedRows.length,
      residualCount: residualRows.length,
      residualValue: residualRows.reduce((sum, row) => sum + (Number(row.currentValue) || 0), 0),
      liquidityCurrentValue: uploadedCurrentLiquidityValue,
      liquidityCurrentPct: uploadedValue > 0 ? (uploadedCurrentLiquidityValue / uploadedValue) * 100 : 0,
      cashCurrent: uploadedCashValue,
    };
    const simData = {
      ...portfolioData,
      meta: simMeta,
      moves: baseRows,
      residuals: residualRows,
    };
    const simulationCapital =
      Number(capital) > 0 ? Number(capital) : uploadedValue > 0 ? uploadedValue : Number(portfolioData.meta?.targetCapital) || 0;
    const model = buildModel(simData, scenario, simulationCapital);

    return {
      model,
      uploadedRows,
      uploadedValue,
      uploadedCurrentLiquidityValue,
      uploadedCashValue,
      importedCount: uploadedRows.length,
      baseMatchedCount: uploadedRows.length - residualRows.length,
      residualCount: residualRows.length,
      residualRows,
      simulationCapital,
      unmappedSymbols: residualRows.map((row) => row.symbol),
    };
  }

  function evaluateRiskLimit(value, limit, direction = "max") {
    if (!Number.isFinite(value) || !Number.isFinite(limit) || limit <= 0) {
      return { state: "neutral", gap: 0 };
    }
    if (direction === "min") {
      if (value >= limit) {
        return { state: "ok", gap: value - limit };
      }
      if (value >= limit * 0.9) {
        return { state: "watch", gap: value - limit };
      }
      return { state: "breach", gap: value - limit };
    }
    if (value <= limit) {
      return { state: "ok", gap: limit - value };
    }
    if (value <= limit * 1.1) {
      return { state: "watch", gap: limit - value };
    }
    return { state: "breach", gap: limit - value };
  }

  function buildRiskChecks(model, snapshot, policy) {
    const rules = policy || riskProfiles.balanced;
    const currentLiquidityPct = Number(snapshot.currentLiquidityPct ?? snapshot.liquidityCurrentPct ?? model.liquidityTargetPct) || 0;
    const cashPct = Number(snapshot.cashPct ?? snapshot.currentCashPct ?? 0) || 0;
    const largestName = safeArray(model.modelRows)
      .filter((row) => !row.fixed)
      .reduce((max, row) => Math.max(max, Number(row.targetWeight) || 0), 0);
    const largestSector = safeArray(model.themeRows)
      .filter((row) => row.key !== "residual")
      .reduce((max, row) => Math.max(max, Number(row.targetWeight) || 0), 0);
    const checks = [
      {
        key: "cash",
        label: "Cash mínimo",
        value: cashPct,
        limit: rules.minCash,
        direction: "min",
        detail: "Garanta caixa suficiente para rebalancear sem depender de vendas forçadas.",
      },
      {
        key: "liquidity",
        label: "Liquidez total",
        value: currentLiquidityPct,
        limit: rules.minLiquidity,
        direction: "min",
        detail: "Inclui Cash, XOVR e ECOPET_BOND como corredor de defesa.",
      },
      {
        key: "topFive",
        label: "Top 5",
        value: Number(model.topFiveShare) || 0,
        limit: rules.maxTopFive,
        direction: "max",
        detail: "Controle a concentração dos cinco maiores nomes do livro.",
      },
      {
        key: "largestName",
        label: "Maior nome",
        value: largestName,
        limit: rules.maxSingleName,
        direction: "max",
        detail: "Evita que uma única tese domine o orçamento de risco.",
      },
      {
        key: "nonUsd",
        label: "Não-USD",
        value: Number(model.nonUsdShare) || 0,
        limit: rules.maxNonUsd,
        direction: "max",
        detail: "Protege a carteira contra ruído cambial excessivo.",
      },
      {
        key: "largestSector",
        label: "Maior setor",
        value: largestSector,
        limit: rules.maxSector,
        direction: "max",
        detail: "Evita superconcentração em um tema só, mesmo quando a tese é forte.",
      },
      {
        key: "residuals",
        label: "Residuais",
        value: Number(model.residualCount) || 0,
        limit: rules.maxResiduals,
        direction: "max",
        detail: "Mantém o bloco fora do modelo sob controle para nao mascarar risco.",
      },
    ];
    return checks.map((check) => ({
      ...check,
      result: evaluateRiskLimit(check.value, check.limit, check.direction),
    }));
  }

  function buildRiskRecommendations(checks) {
    const notes = [];
    const has = (key, state = "breach") => checks.some((check) => check.key === key && check.result.state === state);
    if (has("cash")) {
      notes.push("Reforcar caixa ou reduzir cauda ate voltar ao piso de liquidez.");
    }
    if (has("liquidity")) {
      notes.push("Preservar o corredor defensivo de liquidez antes de aumentar o beta.");
    }
    if (has("topFive")) {
      notes.push("Cortar o excesso do top 5 e redistribuir em temas menos correlacionados.");
    }
    if (has("largestName")) {
      notes.push("Diminuir o maior nome isolado para aliviar risco idiossincratico.");
    }
    if (has("nonUsd")) {
      notes.push("Reduzir exposição cambial fora de USD ou usar hedge parcial.");
    }
    if (has("largestSector")) {
      notes.push("Rebalancear o setor dominante para melhorar a diversificacao tematica.");
    }
    if (has("residuals")) {
      notes.push("Limpar ou isolar residuais para nao mascarar a leitura do modelo.");
    }
    if (!notes.length) {
      notes.push("A carteira respeita os limites principais e pode seguir para o cenário selecionado.");
    }
    return notes;
  }

  function TabPanel(props) {
    const { active, value, children } = props;
    if (active !== value) {
      return null;
    }
    return html`<${Box} role="tabpanel" sx=${{ pt: 3 }}>${children}</${Box}>`;
  }

  function SectionTitle({ eyebrow, title, subtitle, action }) {
    return html`
      <${Stack}
        direction="row"
        justifyContent="space-between"
        alignItems="flex-start"
        spacing=${2}
        sx=${{ mb: 2 }}
      >
        <${Box}>
          ${eyebrow
            ? html`<${Typography}
                variant="overline"
                sx=${{
                  display: "block",
                  mb: 0.5,
                  color: "secondary.main",
                  letterSpacing: "0.16em",
                  fontWeight: 700,
                }}
              >
                ${eyebrow}
              </${Typography}>`
            : null}
          <${Typography}
            variant="h5"
            sx=${{
              fontFamily: '"Space Grotesk", "IBM Plex Sans", sans-serif',
              fontWeight: 700,
              letterSpacing: "-0.03em",
            }}
          >
            ${title}
          </${Typography}>
          ${subtitle
            ? html`<${Typography}
                variant="body2"
                color="text.secondary"
                sx=${{ mt: 0.8, maxWidth: 920, lineHeight: 1.75 }}
              >
                ${subtitle}
              </${Typography}>`
            : null}
        </${Box}>
        ${action ? html`<${Box}>${action}</${Box}>` : null}
      </${Stack}>
    `;
  }

  function SurfaceCard({ children, sx = {} }) {
    return html`
      <${Paper}
        elevation=${0}
        sx=${{
          borderRadius: 4,
          border: "1px solid rgba(255,255,255,0.08)",
          background:
            "linear-gradient(180deg, rgba(11,18,30,0.96) 0%, rgba(10,16,28,0.84) 100%)",
          boxShadow: "0 28px 70px rgba(0,0,0,0.32)",
          backdropFilter: "blur(18px)",
          WebkitBackdropFilter: "blur(18px)",
          ...sx,
        }}
      >
        ${children}
      </${Paper}>
    `;
  }

  function MetricCard({ accent, label, value, helper }) {
    return html`
      <${Card}
        elevation=${0}
        sx=${{
          position: "relative",
          overflow: "hidden",
          borderRadius: 4,
          border: "1px solid rgba(255,255,255,0.08)",
          background:
            "linear-gradient(180deg, rgba(11,18,30,0.96) 0%, rgba(10,16,28,0.84) 100%)",
          boxShadow: "0 20px 50px rgba(0,0,0,0.25)",
        }}
      >
        <${Box}
          sx=${{
            height: 4,
            background: `linear-gradient(90deg, ${accent}, transparent 92%)`,
          }}
        />
        <${CardContent} sx=${{ p: 2.25, minHeight: 128 }}>
          <${Typography}
            variant="overline"
            sx=${{
              display: "block",
              color: "text.secondary",
              letterSpacing: "0.16em",
              fontWeight: 700,
            }}
          >
            ${label}
          </${Typography}>
          <${Typography}
            variant="h4"
            sx=${{
              mt: 1.2,
              fontFamily: '"Space Grotesk", "IBM Plex Sans", sans-serif',
              fontWeight: 700,
              letterSpacing: "-0.04em",
            }}
          >
            ${value}
          </${Typography}>
          <${Typography} variant="body2" color="text.secondary" sx=${{ mt: 1, lineHeight: 1.55 }}>
            ${helper}
          </${Typography}>
        </${CardContent}>
      </${Card}>
    `;
  }

  function RailMetric({ label, value, caption, accent }) {
    return html`
      <${Paper}
        elevation=${0}
        sx=${{
          p: 2,
          borderRadius: 3,
          border: "1px solid rgba(255,255,255,0.08)",
          background: "rgba(255,255,255,0.03)",
        }}
      >
        <${Stack} direction="row" justifyContent="space-between" spacing=${2} alignItems="flex-start">
          <${Box}>
            <${Typography} variant="caption" color="text.secondary" sx=${{ letterSpacing: "0.12em" }}>
              ${label}
            </${Typography}>
            <${Typography}
              variant="h6"
              sx=${{
                mt: 0.5,
                fontFamily: '"Space Grotesk", "IBM Plex Sans", sans-serif',
                fontWeight: 700,
              }}
            >
              ${value}
            </${Typography}>
          </${Box}>
          <${Chip}
            size="small"
            label=${caption}
            sx=${{
              bgcolor: `${accent}22`,
              color: accent,
              border: `1px solid ${accent}55`,
              fontWeight: 700,
            }}
          />
        </${Stack}>
      </${Paper}>
    `;
  }

  function DistributionRow({ row, mode }) {
    const showCurrent = mode === "full" && Number.isFinite(row.currentWeight) && row.currentWeight > 0;
    const showTarget = Number.isFinite(row.targetWeight) && row.targetWeight > 0;
    const summaryLabel =
      mode === "full"
        ? `${row.currentWeightText} atual / ${row.targetWeightText} alvo`
        : `${row.assetCount} ativos / ${formatPct(row.share)} da cesta`;
    const detailText =
      mode === "full" ? `${row.currentText} atual / ${row.targetText} alvo` : row.assetsLabel || row.description;

    return html`
      <${Paper}
        elevation=${0}
        sx=${{
          p: 2,
          borderRadius: 3,
          border: "1px solid rgba(255,255,255,0.08)",
          background: "rgba(255,255,255,0.03)",
        }}
      >
        <${Stack} direction="row" justifyContent="space-between" spacing=${2} alignItems="flex-start">
          <${Box} sx=${{ minWidth: 0 }}>
            <${Typography}
              variant="subtitle1"
              sx=${{
                fontWeight: 700,
                color: row.accent || "primary.main",
                letterSpacing: "-0.02em",
              }}
            >
              ${row.label}
            </${Typography}>
            <${Typography} variant="body2" color="text.secondary" sx=${{ mt: 0.5, lineHeight: 1.5 }}>
              ${row.description || detailText}
            </${Typography}>
          </${Box}>
          <${Stack} direction="row" spacing=${1} flexWrap="wrap" sx=${{ justifyContent: "flex-end" }}>
            <${Chip}
              size="small"
              label=${summaryLabel}
              sx=${{
                bgcolor: `${row.accent || "#8f99a8"}22`,
                color: row.accent || "#8f99a8",
                border: `1px solid ${row.accent || "#8f99a8"}55`,
                fontWeight: 700,
              }}
            />
            ${mode === "full"
              ? html`<${Chip}
                  size="small"
                  label=${`delta ${row.delta >= 0 ? "+" : ""}${formatMoney(row.delta)}`}
                  sx=${{
                    bgcolor: row.delta >= 0 ? "rgba(70,209,190,0.14)" : "rgba(255,122,89,0.14)",
                    color: row.delta >= 0 ? "#46d1be" : "#ff7a59",
                    border: `1px solid ${row.delta >= 0 ? "#46d1be" : "#ff7a59"}55`,
                    fontWeight: 700,
                  }}
                />`
              : null}
          </${Stack}>
        </${Stack}>

        <${Box} sx=${{ mt: 1.5, position: "relative" }}>
          <${LinearProgress}
            variant="determinate"
            value=${clamp(showTarget ? row.targetWeight : row.share, 0, 100)}
            sx=${{
              height: 14,
              borderRadius: 999,
              bgcolor: "rgba(255,255,255,0.05)",
              "& .MuiLinearProgress-bar": {
                borderRadius: 999,
                bgcolor: row.accent || "#4aa3df",
              },
            }}
          />
          ${showCurrent
            ? html`<${Box} sx=${{ mt: -1.5, px: 0.5 }}>
                <${LinearProgress}
                  variant="determinate"
                  value=${clamp(row.currentWeight, 0, 100)}
                  sx=${{
                    height: 5,
                    borderRadius: 999,
                    bgcolor: "transparent",
                    "& .MuiLinearProgress-bar": {
                      borderRadius: 999,
                      bgcolor: "rgba(255,255,255,0.44)",
                    },
                  }}
                />
              </${Box}>`
            : null}
        </${Box}>

        <${Stack} direction="row" justifyContent="space-between" spacing=${2} sx=${{ mt: 1 }}>
          <${Typography} variant="caption" color="text.secondary">
            ${mode === "full" ? row.currentText : row.assetsLabel || ""}
          </${Typography}>
          <${Typography} variant="caption" color="text.secondary">
            ${detailText}
          </${Typography}>
        </${Stack}>
      </${Paper}>
    `;
  }

  function IdeaCard({ idea }) {
    const accent = getStudyBucketAccent(idea.studyBucket);
    return html`
      <${Card}
        elevation=${0}
        sx=${{
          height: "100%",
          borderRadius: 4,
          border: "1px solid rgba(255,255,255,0.08)",
          background:
            "linear-gradient(180deg, rgba(12,20,34,0.98) 0%, rgba(10,16,28,0.84) 100%)",
          position: "relative",
          overflow: "hidden",
          boxShadow: "0 20px 50px rgba(0,0,0,0.24)",
          "&::before": {
            content: '""',
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            height: 4,
            background: `linear-gradient(90deg, ${accent}, transparent 92%)`,
          },
        }}
      >
        <${CardContent} sx=${{ p: 2.2, minHeight: 220 }}>
          <${Stack} direction="row" justifyContent="space-between" alignItems="flex-start" spacing=${2}>
            <${Box}>
              <${Typography}
                variant="h6"
                sx=${{
                  fontWeight: 700,
                  fontFamily: '"Space Grotesk", "IBM Plex Sans", sans-serif',
                  letterSpacing: "-0.03em",
                }}
              >
                ${idea.symbol}
              </${Typography}>
              <${Typography} variant="body2" color="text.secondary" sx=${{ mt: 0.2 }}>
                ${idea.name}
              </${Typography}>
            </${Box}>
            <${Chip}
              size="small"
              label=${formatPriority(idea.priority)}
              sx=${{
                bgcolor: `${priorityPalette[idea.priority] || "#8f99a8"}22`,
                color: priorityPalette[idea.priority] || "#8f99a8",
                border: `1px solid ${priorityPalette[idea.priority] || "#8f99a8"}55`,
                fontWeight: 700,
              }}
            />
          </${Stack}>
          <${Typography}
            variant="caption"
            sx=${{ display: "block", mt: 1.4, color: accent, fontWeight: 700, letterSpacing: "0.08em" }}
          >
            ${idea.themeLabel} / ${formatStudyBucket(idea.studyBucket)}
          </${Typography}>
          <${Typography} variant="body2" color="text.secondary" sx=${{ mt: 1.1, lineHeight: 1.6 }}>
            ${idea.thesis}
          </${Typography}>
          <${Stack} spacing=${1} sx=${{ mt: 2 }}>
            <${Typography} variant="body2" sx=${{ fontWeight: 700 }}>
              ${formatPct(idea.upsidePct)} upside
            </${Typography}>
            <${Typography} variant="caption" color="text.secondary">
              ${formatStockPrice(idea.currentPrice, idea.currency)} &rarr; ${formatStockPrice(idea.targetPrice, idea.currency)}
            </${Typography}>
            <${Typography} variant="caption" color="text.secondary">
              ${idea.currency} / ${idea.source || "Study"}
            </${Typography}>
          </${Stack}>
        </${CardContent}>
      </${Card}>
    `;
  }

  function BlueprintAccordion({ entry, index }) {
    const accent = getStudyBucketAccent(
      entry.label === "Rare earths"
        ? "rare_earths"
        : entry.label === "Uranium"
          ? "uranium"
          : entry.label === "Defense / space"
            ? "defense_space"
            : entry.label === "AI biotech"
              ? "ai_biotech"
              : entry.label === "Copper / lithium"
                ? "copper_lithium"
                : "nuclear"
    );

    return html`
      <${Accordion}
        elevation=${0}
        disableGutters
        sx=${{
          borderRadius: 3,
          overflow: "hidden",
          border: "1px solid rgba(255,255,255,0.08)",
          background: "rgba(255,255,255,0.03)",
          "&:before": { display: "none" },
          mb: index === undefined ? 0 : 1.2,
        }}
      >
        <${AccordionSummary}
          expandIcon=${html`<${Box} sx=${{ color: "text.secondary", fontSize: 22 }}>⌄</${Box}>`}
          sx=${{
            "& .MuiAccordionSummary-content": {
              alignItems: "center",
              justifyContent: "space-between",
            },
          }}
        >
          <${Stack} direction="row" spacing=${1.2} alignItems="center" sx=${{ width: "100%" }}>
            <${Chip}
              size="small"
              label=${`${entry.weight}%`}
              sx=${{
                bgcolor: `${accent}22`,
                color: accent,
                border: `1px solid ${accent}55`,
                fontWeight: 700,
              }}
            />
            <${Typography} sx=${{ fontWeight: 700, flexGrow: 1 }}>${entry.label}</${Typography}>
          </${Stack}>
        </${AccordionSummary}>
        <${AccordionDetails} sx=${{ pt: 0, pb: 2, px: 2.25 }}>
          <${Typography} variant="body2" color="text.secondary" sx=${{ lineHeight: 1.6 }}>
            ${safeArray(entry.examples).join(" · ")}
          </${Typography}>
        </${AccordionDetails}>
      </${Accordion}>
    `;
  }

  function MarketRow({ row }) {
    const status = statusPalette[row.status] || statusPalette.missing;
    const currencyColor = currencyPalette[row.currency] || currencyPalette.Other;

    return html`
      <${TableRow}
        hover
        sx=${{
          "& td": { borderBottomColor: "rgba(255,255,255,0.08)" },
        }}
      >
        <${TableCell}>
          <${Typography} sx=${{ fontWeight: 700 }}>${row.symbol}</${Typography}>
          <${Typography} variant="caption" color="text.secondary">
            ${row.currencyRaw || row.currency || "--"}
          </${Typography}>
        </${TableCell}>
        <${TableCell}>${row.yahoo || row.symbol}</${TableCell}>
        <${TableCell}>
          <${Chip}
            size="small"
            label=${row.currency || "?"}
            sx=${{
              bgcolor: `${currencyColor}22`,
              color: currencyColor,
              border: `1px solid ${currencyColor}55`,
              fontWeight: 700,
            }}
          />
        </${TableCell}>
        <${TableCell}>
          <${Typography} sx=${{ fontWeight: 700 }}>
            ${formatStockPrice(row.closeLocal, row.currency)}
          </${Typography}>
          <${Typography} variant="caption" color="text.secondary">
            ${row.currencyRaw || row.currency || "--"}
          </${Typography}>
        </${TableCell}>
        <${TableCell}>${formatFx(row.fxToUsd)}</${TableCell}>
        <${TableCell}>${row.closeUsd != null ? formatPreciseMoney(row.closeUsd) : "Sem preco"}</${TableCell}>
        <${TableCell}>${formatDate(row.date)}</${TableCell}>
        <${TableCell}>
          <${Chip}
            size="small"
            label=${status.label}
            sx=${{
              bgcolor: status.background,
              color: status.color,
              border: `1px solid ${status.color}55`,
              fontWeight: 700,
            }}
          />
        </${TableCell}>
      </${TableRow}>
    `;
  }

  function TradeRow({ row }) {
    const action = actionPalette[row.action] || actionPalette.Manter;
    const theme = safeArray(data.themes).find((item) => item.id === row.themeId);

    return html`
      <${TableRow}
        hover
        sx=${{
          "& td": { borderBottomColor: "rgba(255,255,255,0.08)" },
        }}
      >
        <${TableCell}>
          <${Typography} sx=${{ fontWeight: 700 }}>${row.asset}</${Typography}>
          <${Typography} variant="caption" color="text.secondary">
            ${row.role || row.category || "--"}
          </${Typography}>
        </${TableCell}>
        <${TableCell}>
          <${Chip}
            size="small"
            label=${row.themeLabel}
            sx=${{
              bgcolor: `${(theme && theme.accent) || row.accent || "#8f99a8"}22`,
              color: (theme && theme.accent) || row.accent || "#8f99a8",
              border: `1px solid ${(theme && theme.accent) || row.accent || "#8f99a8"}55`,
              fontWeight: 700,
            }}
          />
        </${TableCell}>
        <${TableCell}>${row.region}</${TableCell}>
        <${TableCell}>
          <${Typography} sx=${{ fontWeight: 700 }}>${formatMoney(row.currentValue)}</${Typography}>
          <${Typography} variant="caption" color="text.secondary">
            ${formatPct(row.currentWeight)}
          </${Typography}>
        </${TableCell}>
        <${TableCell}>
          <${Typography} sx=${{ fontWeight: 700 }}>${formatMoney(row.targetValue)}</${Typography}>
          <${Typography} variant="caption" color="text.secondary">
            ${formatPct(row.targetWeight)}
          </${Typography}>
        </${TableCell}>
        <${TableCell} sx=${{ color: row.trade >= 0 ? "#46d1be" : "#ff7a59", fontWeight: 700 }}>
          ${row.trade >= 0 ? "+" : ""}${formatMoney(row.trade)}
        </${TableCell}>
        <${TableCell}>
          <${Chip}
            size="small"
            label=${row.action}
            sx=${{
              bgcolor: action.background,
              color: action.color,
              border: `1px solid ${action.color}55`,
              fontWeight: 700,
            }}
          />
        </${TableCell}>
        <${TableCell}>
          <${Typography} variant="body2" sx=${{ lineHeight: 1.6 }}>
            ${row.thesis}
          </${Typography}>
        </${TableCell}>
      </${TableRow}>
    `;
  }

  function HoldingRow({ row }) {
    const status = statusPalette[row.status] || statusPalette.ok;
    const theme = safeArray(data.themes).find((item) => item.id === row.themeId);
    return html`
      <${TableRow} hover sx=${{ "& td": { borderBottomColor: "rgba(255,255,255,0.08)" } }}>
        <${TableCell}>
          <${Typography} sx=${{ fontWeight: 700 }}>${row.symbol}</${Typography}>
          <${Typography} variant="caption" color="text.secondary">
            ${theme?.label || row.themeLabel || "--"}
          </${Typography}>
        </${TableCell}>
        <${TableCell}>
          <${Chip}
            size="small"
            label=${status.label}
            sx=${{
              bgcolor: status.background,
              color: status.color,
              border: `1px solid ${status.color}55`,
              fontWeight: 700,
            }}
          />
        </${TableCell}>
        <${TableCell}>
          <${Typography} sx=${{ fontWeight: 700 }}>
            ${formatStockPrice(row.currentPrice, row.currency)}
          </${Typography}>
          <${Typography} variant="caption" color="text.secondary">
            ${row.priceError ? "Sem preco" : formatPreciseMoney(row.currentPriceUsd)}
          </${Typography}>
        </${TableCell}>
        <${TableCell}>
          <${Typography} sx=${{ fontWeight: 700 }}>
            ${formatStockPrice(row.targetPrice, row.currency)}
          </${Typography}>
          <${Typography} variant="caption" color="text.secondary">
            ${row.priceError ? "Sem preco" : formatPreciseMoney(row.targetPriceUsd)}
          </${Typography}>
        </${TableCell}>
        <${TableCell}>${formatPct(row.upsidePct)}</${TableCell}>
        <${TableCell}>${row.bias || "--"}</${TableCell}>
      </${TableRow}>
    `;
  }

  function WatchlistRow({ row }) {
    const priority = formatPriority(row.priority);
    const accent = priorityPalette[priority] || "#8f99a8";
    return html`
      <${TableRow} hover sx=${{ "& td": { borderBottomColor: "rgba(255,255,255,0.08)" } }}>
        <${TableCell}>
          <${Typography} sx=${{ fontWeight: 700 }}>${row.symbol}</${Typography}>
          <${Typography} variant="caption" color="text.secondary">
            ${row.themeLabel || "--"}
          </${Typography}>
        </${TableCell}>
        <${TableCell}>${row.studyBucket || "--"}</${TableCell}>
        <${TableCell}>
          <${Typography} sx=${{ fontWeight: 700 }}>
            ${formatStockPrice(row.currentPrice, row.currency)}
          </${Typography}>
          <${Typography} variant="caption" color="text.secondary">
            ${row.priceError ? "Sem preco" : formatPreciseMoney(row.currentPriceUsd)}
          </${Typography}>
        </${TableCell}>
        <${TableCell}>
          <${Typography} sx=${{ fontWeight: 700 }}>
            ${formatStockPrice(row.targetPrice, row.currency)}
          </${Typography}>
          <${Typography} variant="caption" color="text.secondary">
            ${row.priceError ? "Sem preco" : formatPreciseMoney(row.targetPriceUsd)}
          </${Typography}>
        </${TableCell}>
        <${TableCell}>
          <${Chip}
            size="small"
            label=${priority}
            sx=${{
              bgcolor: `${accent}22`,
              color: accent,
              border: `1px solid ${accent}55`,
              fontWeight: 700,
            }}
          />
        </${TableCell}>
      </${TableRow}>
    `;
  }

  function PortfolioDraftRow({ row, index, onChange, onRemove, onDuplicate }) {
    return html`
      <${Paper}
        elevation=${0}
        sx=${{
          p: 2,
          borderRadius: 4,
          border: "1px solid rgba(255,255,255,0.08)",
          background: "rgba(255,255,255,0.03)",
        }}
      >
        <${Stack} spacing=${1.5}>
          <${Stack} direction="row" justifyContent="space-between" alignItems="center" spacing=${2}>
            <${Box}>
              <${Typography} sx=${{ fontWeight: 700 }}>
                Linha ${index + 1}
              </${Typography}>
              <${Typography} variant="caption" color="text.secondary">
                Edite por ticker, quantidade, preço local ou valor em USD.
              </${Typography}>
            </${Box}>
            <${Stack} direction="row" spacing=${1} flexWrap="wrap">
              <${Button} size="small" variant="outlined" onClick=${onDuplicate}>Duplicar</${Button}>
              <${Button} size="small" color="error" variant="outlined" onClick=${onRemove}>
                Remover
              </${Button}>
            </${Stack}>
          </${Stack}>

          <${Grid} container spacing=${1.25}>
            <${Grid} item xs=${12} sm=${6} md=${2.4}>
              <${TextField}
                label="Ticker"
                value=${row.symbol}
                onChange=${(event) => onChange("symbol", event.target.value)}
                fullWidth=${true}
                size="small"
              />
            </${Grid}>
            <${Grid} item xs=${12} sm=${6} md=${2.4}>
              <${TextField}
                label="Nome"
                value=${row.name}
                onChange=${(event) => onChange("name", event.target.value)}
                fullWidth=${true}
                size="small"
              />
            </${Grid}>
            <${Grid} item xs=${12} sm=${6} md=${1.8}>
              <${TextField}
                label="Quantidade"
                value=${row.quantity}
                onChange=${(event) => onChange("quantity", event.target.value)}
                fullWidth=${true}
                size="small"
                inputMode="decimal"
              />
            </${Grid}>
            <${Grid} item xs=${12} sm=${6} md=${1.8}>
              <${TextField}
                label="Preço"
                value=${row.price}
                onChange=${(event) => onChange("price", event.target.value)}
                fullWidth=${true}
                size="small"
                inputMode="decimal"
              />
            </${Grid}>
            <${Grid} item xs=${12} sm=${6} md=${1.8}>
              <${TextField}
                label="Valor"
                value=${row.value}
                onChange=${(event) => onChange("value", event.target.value)}
                fullWidth=${true}
                size="small"
                inputMode="decimal"
              />
            </${Grid}>
            <${Grid} item xs=${12} sm=${6} md=${1.8}>
              <${TextField}
                label="Moeda"
                value=${row.currency}
                onChange=${(event) => onChange("currency", event.target.value)}
                fullWidth=${true}
                size="small"
              />
            </${Grid}>
            <${Grid} item xs=${12} sm=${6} md=${3}>
              <${TextField}
                label="Setor"
                value=${row.sector}
                onChange=${(event) => onChange("sector", event.target.value)}
                fullWidth=${true}
                size="small"
              />
            </${Grid}>
            <${Grid} item xs=${12} sm=${6} md=${9}>
              <${TextField}
                label="Notas / tese"
                value=${row.notes}
                onChange=${(event) => onChange("notes", event.target.value)}
                fullWidth=${true}
                size="small"
                multiline=${true}
                minRows=${2}
              />
            </${Grid}>
          </${Grid}>
        </${Stack}>
      </${Paper}>
    `;
  }

  function SectorGroupCard({ group, selected, onClick }) {
    const accent = group.accent || getStudyBucketAccent(group.bucket);
    return html`
      <${Card}
        elevation=${0}
        onClick=${onClick}
        sx=${{
          height: "100%",
          cursor: "pointer",
          borderRadius: 4,
          border: selected ? `1px solid ${accent}88` : "1px solid rgba(255,255,255,0.08)",
          background: selected
            ? `linear-gradient(180deg, ${accent}18 0%, rgba(10,16,28,0.88) 100%)`
            : "linear-gradient(180deg, rgba(12,20,34,0.98) 0%, rgba(10,16,28,0.84) 100%)",
          transition: "transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease",
          boxShadow: selected ? `0 20px 55px ${accent}24` : "0 20px 50px rgba(0,0,0,0.24)",
          "&:hover": {
            transform: "translateY(-2px)",
          },
        }}
      >
        <${CardContent} sx=${{ p: 2.2, height: "100%" }}>
          <${Stack} spacing=${1.2}>
            <${Stack} direction="row" justifyContent="space-between" alignItems="flex-start" spacing=${2}>
              <${Box}>
                <${Typography}
                  variant="h6"
                  sx=${{
                    fontWeight: 700,
                    fontFamily: '"Space Grotesk", "IBM Plex Sans", sans-serif',
                    letterSpacing: "-0.03em",
                  }}
                >
                  ${group.label}
                </${Typography}>
                <${Typography} variant="body2" color="text.secondary" sx=${{ mt: 0.2, lineHeight: 1.5 }}>
                  ${group.description}
                </${Typography}>
              </${Box}>
              <${Chip}
                size="small"
                label=${group.count}
                sx=${{
                  bgcolor: `${accent}22`,
                  color: accent,
                  border: `1px solid ${accent}55`,
                  fontWeight: 700,
                }}
              />
            </${Stack}>

            <${Stack} direction="row" spacing=${1} flexWrap="wrap">
              <${Chip}
                size="small"
                label=${`${formatPct(group.averageUpside || 0)} upside médio`}
                sx=${{
                  bgcolor: "rgba(74,163,223,0.12)",
                  color: "#9dd4ff",
                  border: "1px solid rgba(74,163,223,0.35)",
                  fontWeight: 700,
                }}
              />
              <${Chip}
                size="small"
                label=${group.bestPick ? `Topo: ${group.bestPick.symbol}` : "Sem picks"}
                sx=${{
                  bgcolor: "rgba(255,255,255,0.06)",
                  color: "text.secondary",
                  border: "1px solid rgba(255,255,255,0.08)",
                  fontWeight: 700,
                }}
              />
            </${Stack}>

            <${Box}>
              <${Typography} variant="caption" color="text.secondary" sx=${{ display: "block", mb: 0.75 }}>
                Top picks
              </${Typography}>
              <${Stack} spacing=${0.8}>
                ${group.topPicks.map(
                  (item) => html`
                    <${Stack}
                      key=${item.symbol}
                      direction="row"
                      justifyContent="space-between"
                      alignItems="center"
                      spacing=${1}
                      sx=${{
                        py: 0.65,
                        px: 1,
                        borderRadius: 2,
                        background: "rgba(255,255,255,0.03)",
                        border: "1px solid rgba(255,255,255,0.06)",
                      }}
                    >
                      <${Box} sx=${{ minWidth: 0 }}>
                        <${Typography} sx=${{ fontWeight: 700, lineHeight: 1.2 }}>
                          ${item.symbol}
                        </${Typography}>
                        <${Typography} variant="caption" color="text.secondary" sx=${{ display: "block" }}>
                          ${item.name}
                        </${Typography}>
                      </${Box}>
                      <${Box} sx=${{ textAlign: "right" }}>
                        <${Typography} sx=${{ fontWeight: 700, color: accent }}>
                          ${formatPct(item.upsidePct)}
                        </${Typography}>
                        <${Typography} variant="caption" color="text.secondary">
                          ${formatPriority(item.priority)}
                        </${Typography}>
                      </${Box}>
                    </${Stack}>
                  `
                )}
              </${Stack}>
            </${Box}>
          </${Stack}>
        </${CardContent}>
      </${Card}>
    `;
  }

  function RiskCheckCard({ check }) {
    const tone = {
      ok: { color: "#46d1be", background: "rgba(70,209,190,0.14)" },
      watch: { color: "#d08b2e", background: "rgba(208,139,46,0.14)" },
      breach: { color: "#ff7a59", background: "rgba(255,122,89,0.14)" },
      neutral: { color: "#8f99a8", background: "rgba(143,153,168,0.14)" },
    }[check.result.state] || {
      color: "#8f99a8",
      background: "rgba(143,153,168,0.14)",
    };

    return html`
      <${Paper}
        elevation=${0}
        sx=${{
          p: 2,
          borderRadius: 4,
          border: `1px solid ${tone.color}55`,
          background: "rgba(255,255,255,0.03)",
        }}
      >
        <${Stack} spacing=${1}>
          <${Stack} direction="row" justifyContent="space-between" alignItems="center" spacing=${2}>
            <${Typography} sx=${{ fontWeight: 700 }}>
              ${check.label}
            </${Typography}>
            <${Chip}
              size="small"
              label=${check.result.state === "ok" ? "OK" : check.result.state === "watch" ? "Atenção" : check.result.state === "breach" ? "Breach" : "N/A"}
              sx=${{
                bgcolor: tone.background,
                color: tone.color,
                border: `1px solid ${tone.color}55`,
                fontWeight: 700,
              }}
            />
          </${Stack}>
          <${Typography} variant="body2" color="text.secondary" sx=${{ lineHeight: 1.5 }}>
            ${check.detail}
          </${Typography}>
          <${Stack} direction="row" justifyContent="space-between" spacing=${2}>
            <${Box}>
              <${Typography} variant="caption" color="text.secondary" sx=${{ display: "block" }}>
                Atual
              </${Typography}>
              <${Typography} sx=${{ fontWeight: 700 }}>
                ${formatPct(check.value)}
              </${Typography}>
            </${Box}>
            <${Box} sx=${{ textAlign: "right" }}>
              <${Typography} variant="caption" color="text.secondary" sx=${{ display: "block" }}>
                Limite
              </${Typography}>
              <${Typography} sx=${{ fontWeight: 700 }}>
                ${formatPct(check.limit)}
              </${Typography}>
            </${Box}>
          </${Stack}>
        </${Stack}>
      </${Paper}>
    `;
  }

  function App() {
    const defaultScenario = resolveDefaultScenario(data);
    const stored = readStoredPrefs();
    const storedScenarioValid = safeArray(data.scenarios).some((scenario) => scenario.id === stored.scenarioId);
    const initialScenarioId = storedScenarioValid ? stored.scenarioId : defaultScenario;
    const defaultCapital = Number(data.meta?.targetCapital || data.meta?.currentPortfolioValue || 0);
    const initialCapital = Number.isFinite(Number(stored.capital)) && Number(stored.capital) > 0
      ? Number(stored.capital)
      : defaultCapital;
    const initialPortfolioRows = coercePortfolioDraftRows(stored.portfolioRows).length
      ? coercePortfolioDraftRows(stored.portfolioRows)
      : buildPortfolioDraftRowsFromData(data);
    const initialRiskProfileId = riskProfiles[stored.riskProfileId]
      ? stored.riskProfileId
      : initialScenarioId === "defensive"
        ? "defensive"
        : initialScenarioId === "convex"
          ? "convex"
          : "balanced";
    const availableTabs = Object.entries(tabConfig)
      .filter(([key, cfg]) => cfg[view])
      .map(([key, cfg]) => ({ id: key, label: cfg.label }));

    const [prefs, setPrefs] = React.useState({
      scenarioId: initialScenarioId,
      capital: initialCapital,
      tab: stored.tab || availableTabs[0]?.id || "overview",
      filter: ["Todos", "Comprar", "Reduzir", "Manter", "Liquidez"].includes(stored.filter)
        ? stored.filter
        : "Todos",
      sort: ["absTrade", "targetWeight", "theme"].includes(stored.sort) ? stored.sort : "absTrade",
      portfolioRows: initialPortfolioRows,
      portfolioCapital:
        Number.isFinite(Number(stored.portfolioCapital)) && Number(stored.portfolioCapital) > 0
          ? Number(stored.portfolioCapital)
          : initialCapital,
      riskProfileId: initialRiskProfileId,
      selectedSector: stored.selectedSector || "",
    });

    const scenario = resolveScenario(data, prefs.scenarioId);
    const model = React.useMemo(() => buildModel(data, scenario, prefs.capital), [scenario, prefs.capital]);
    const isDesktop = useMediaQuery(theme.breakpoints.up("md"));
    const sectorInsights = React.useMemo(() => buildSectorInsights(data), []);
    const portfolioRows = React.useMemo(() => coercePortfolioDraftRows(prefs.portfolioRows), [prefs.portfolioRows]);
    const importedSimulation = React.useMemo(
      () => buildImportedPortfolioModel(data, portfolioRows, scenario, prefs.portfolioCapital),
      [portfolioRows, scenario, prefs.portfolioCapital]
    );
    const riskPolicy = riskProfiles[prefs.riskProfileId] || riskProfiles.balanced;
    const portfolioRiskChecks = React.useMemo(
      () =>
        buildRiskChecks(
          importedSimulation.model,
          {
            cashPct:
              importedSimulation.uploadedValue > 0
                ? (importedSimulation.uploadedCashValue / importedSimulation.uploadedValue) * 100
                : Number(data.meta?.currentPortfolioValue) > 0
                  ? ((Number(data.meta?.cashCurrent) || 0) / Number(data.meta?.currentPortfolioValue)) * 100
                  : Number(data.meta?.cashTargetPct) || 0,
            currentLiquidityPct:
              importedSimulation.uploadedValue > 0
                ? (importedSimulation.uploadedCurrentLiquidityValue / importedSimulation.uploadedValue) * 100
                : Number(data.meta?.liquidityCurrentPct) || importedSimulation.model.liquidityTargetPct,
          },
          riskPolicy
        ),
      [importedSimulation, riskPolicy]
    );
    const riskRecommendations = React.useMemo(
      () => buildRiskRecommendations(portfolioRiskChecks),
      [portfolioRiskChecks]
    );
    const selectedSectorId =
      prefs.selectedSector && sectorInsights.some((group) => group.bucket === prefs.selectedSector)
        ? prefs.selectedSector
      : sectorInsights[0]?.bucket || "geral";
    const activeSectorGroup = sectorInsights.find((group) => group.bucket === selectedSectorId) || sectorInsights[0] || null;
    const importedTradeRows = importedSimulation.model.tradeRows
      .filter((row) => Math.abs(Number(row.absTrade) || 0) > 0.01)
      .slice()
      .sort((a, b) => Number(b.absTrade) - Number(a.absTrade));
    const [portfolioNotice, setPortfolioNotice] = React.useState("");

    const updatePortfolioRows = (nextRows) => {
      setPrefs((current) => ({
        ...current,
        portfolioRows: coercePortfolioDraftRows(nextRows),
      }));
    };

    const patchPortfolioRow = (index, field, value) => {
      const nextRows = portfolioRows.map((row, rowIndex) =>
        rowIndex === index ? { ...row, [field]: value } : row
      );
      updatePortfolioRows(nextRows);
    };

    const duplicatePortfolioRow = (index) => {
      const row = portfolioRows[index];
      if (!row) {
        return;
      }
      const nextRows = [
        ...portfolioRows.slice(0, index + 1),
        createPortfolioDraftRow(row),
        ...portfolioRows.slice(index + 1),
      ];
      updatePortfolioRows(nextRows);
      setPortfolioNotice("Linha duplicada com sucesso.");
    };

    const removePortfolioRow = (index) => {
      const nextRows = portfolioRows.filter((_, rowIndex) => rowIndex !== index);
      updatePortfolioRows(nextRows.length ? nextRows : [createPortfolioDraftRow()]);
      setPortfolioNotice("Linha removida do simulador.");
    };

    const addPortfolioRow = () => {
      updatePortfolioRows([...portfolioRows, createPortfolioDraftRow()]);
      setPortfolioNotice("Nova linha adicionada ao simulador.");
    };

    const loadCurrentPortfolio = () => {
      const rows = buildPortfolioDraftRowsFromData(data);
      updatePortfolioRows(rows.length ? rows : [createPortfolioDraftRow()]);
      setPrefs((current) => ({
        ...current,
        portfolioCapital: Number(data.meta?.currentPortfolioValue) || current.portfolioCapital || current.capital,
      }));
      setPortfolioNotice("Carteira atual carregada para simulação.");
    };

    const clearPortfolioRows = () => {
      updatePortfolioRows([createPortfolioDraftRow()]);
      setPortfolioNotice("Editor limpo para entrada manual.");
    };

    const handlePortfolioCsvUpload = (event) => {
      const file = event.target.files?.[0];
      event.target.value = "";
      if (!file) {
        return;
      }
      file
        .text()
        .then((text) => {
          const rows = parsePortfolioCsv(text).map((row) => createPortfolioDraftRow(row));
          if (!rows.length) {
            setPortfolioNotice(`Nenhuma linha valida foi encontrada em ${file.name}.`);
            return;
          }
          const preview = buildImportedPortfolioModel(data, rows, scenario, prefs.portfolioCapital);
          updatePortfolioRows(rows);
          setPrefs((current) => ({
            ...current,
            portfolioCapital: preview.uploadedValue || Number(data.meta?.currentPortfolioValue) || current.portfolioCapital || current.capital,
            tab: "simulator",
          }));
          setPortfolioNotice(`Arquivo ${file.name} importado com ${rows.length} linhas.`);
        })
        .catch((error) => {
          setPortfolioNotice(`Falha ao ler ${file.name}: ${error?.message || error}`);
        });
    };

    React.useEffect(() => {
      if (!availableTabs.some((tab) => tab.id === prefs.tab)) {
        setPrefs((current) => ({ ...current, tab: availableTabs[0]?.id || "overview" }));
      }
    }, [prefs.tab, availableTabs]);

    React.useEffect(() => {
      storePrefs({
        scenarioId: prefs.scenarioId,
        capital: prefs.capital,
        tab: prefs.tab,
        filter: prefs.filter,
        sort: prefs.sort,
        portfolioRows: prefs.portfolioRows,
        portfolioCapital: prefs.portfolioCapital,
        riskProfileId: prefs.riskProfileId,
        selectedSector: selectedSectorId,
      });
    }, [prefs, selectedSectorId]);

    React.useEffect(() => {
      const titleBase = view === "public" ? "Public Snapshot" : "Dashboard";
      document.title = `${scenario.label} - ${titleBase} | Global Portfolio Model Runner`;
    }, [scenario.label]);

    const notes = safeArray(data.meta?.notes);
    const topIdeas = safeArray(data.study?.topIdeas);
    const principles = safeArray(data.study?.principles);
    const basketBlueprint = safeArray(data.study?.basketBlueprint);
    const exportsData = data.exports || {};
    const currentTab = availableTabs.some((tab) => tab.id === prefs.tab) ? prefs.tab : availableTabs[0]?.id || "overview";
    const liquidityShare = Number(model.liquidityTargetPct) || 0;
    const marketCoverage = model.marketPrices.length
      ? Math.round((model.marketOkCount / model.marketPrices.length) * 100)
      : 0;
    const displayNonUsdShare =
      Number.isFinite(Number(data.meta?.nonUsdShare)) && Number(data.meta?.nonUsdShare) > 0
        ? Number(data.meta.nonUsdShare)
        : model.nonUsdShare;
    const themeCards = model.themeCatalog.length > 0 ? model.themeCatalog : safeArray(data.themes);
    const summaryChips = [
      `${formatDate(data.meta?.priceDate)} snapshot`,
      `${integerFormatter.format(model.marketPrices.length)} prices`,
      `${integerFormatter.format(Number(data.meta?.fxRateCount) || 0)} FX`,
      `${formatPct(displayNonUsdShare)} non-USD`,
    ];
    if (view === "full") {
      summaryChips.push(`${integerFormatter.format(model.residualCount)} residuals`);
      summaryChips.push(`${integerFormatter.format(portfolioRows.length)} linhas carteira`);
    } else if (safeArray(data.study?.topIdeas).length) {
      summaryChips.push(`${integerFormatter.format(topIdeas.length)} top ideas`);
    }
    summaryChips.push(`${integerFormatter.format(sectorInsights.length)} setores`);

    const metricCards = view === "full"
      ? [
          {
            accent: "#46d1be",
            label: "Capital base",
            value: formatMoney(model.capital),
            helper: "Base usada para calcular pesos e trades do modelo.",
          },
          {
            accent: "#d08b2e",
            label: "Liquidez atual",
            value: formatPct(Number(data.meta?.liquidityCurrentPct) || liquidityShare),
            helper: `${formatMoney(Number(data.meta?.liquidityCurrentValue) || model.liquidityTargetValue)} em caixa e protecoes.`,
          },
          {
            accent: "#4aa3df",
            label: "Capital investivel",
            value: formatMoney(model.investableValue),
            helper: `Depois do corredor de liquidez de ${formatPct(liquidityShare)}.`,
          },
          {
            accent: "#ff7a59",
            label: "Top 5 share",
            value: formatPct(model.topFiveShare),
            helper: "Concentracao aproximada dos cinco nomes mais pesados.",
          },
          {
            accent: "#7e8cff",
            label: "Nao-USD",
            value: formatPct(displayNonUsdShare),
            helper: "Proxy simples de diversificacao geografica e cambial.",
          },
          {
            accent: "#8f99a8",
            label: "Residuais",
            value: integerFormatter.format(model.residualCount),
            helper: formatMoney(model.residualValue),
          },
        ]
      : [
          {
            accent: "#46d1be",
            label: "Capital base",
            value: formatMoney(model.capital),
            helper: "Capital de leitura usado para o snapshot publico.",
          },
          {
            accent: "#d08b2e",
            label: "Liquidez atual",
            value: formatPct(Number(data.meta?.liquidityCurrentPct) || liquidityShare),
            helper: `${formatMoney(Number(data.meta?.liquidityCurrentValue) || model.liquidityTargetValue)} reportado no snapshot.`,
          },
          {
            accent: "#4aa3df",
            label: "Precos globais",
            value: integerFormatter.format(model.marketPrices.length),
            helper: `${model.marketOkCount} disponiveis e ${model.marketMissingCount} ausentes.`,
          },
          {
            accent: "#ff7a59",
            label: "Top ideas",
            value: integerFormatter.format(topIdeas.length),
            helper: "As cinco teses mais convexas continuam visiveis.",
          },
          {
            accent: "#7e8cff",
            label: "Nao-USD",
            value: formatPct(displayNonUsdShare),
            helper: "Leitura de diversificacao geografica do snapshot.",
          },
          {
            accent: "#8f99a8",
            label: "Temas",
            value: integerFormatter.format(themeCards.length),
            helper: "Cestas tematicas e bucket map do estudo.",
          },
        ];

    return html`
      <${ThemeProvider} theme=${theme}>
        <${CssBaseline} />
        <${GlobalStyles}
          styles=${{
            body: {
              backgroundColor: "#07111b",
            },
            "#root": {
              minHeight: "100vh",
            },
          }}
        />

        <${Box} sx=${{ minHeight: "100vh", pb: 6 }}>
          <${AppBar}
            position="sticky"
            elevation=${0}
            sx=${{
              backdropFilter: "blur(18px)",
              background: "rgba(7,17,27,0.76)",
              borderBottom: "1px solid rgba(255,255,255,0.08)",
            }}
          >
            <${Toolbar} sx=${{ minHeight: 72, gap: 2 }}>
              <${Box} sx=${{ flex: 1, minWidth: 0 }}>
                <${Typography}
                  variant="overline"
                  sx=${{
                    display: "block",
                    color: "secondary.main",
                    letterSpacing: "0.16em",
                    fontWeight: 700,
                  }}
                >
                  ${view === "public" ? "Snapshot sanitizado" : "Dashboard operacional"}
                </${Typography}>
                <${Typography}
                  variant="h6"
                  sx=${{
                    mt: 0.2,
                    fontFamily: '"Space Grotesk", "IBM Plex Sans", sans-serif',
                    fontWeight: 700,
                    letterSpacing: "-0.03em",
                  }}
                >
                  Global Portfolio Model Runner
                </${Typography}>
              </${Box}>
              <${Stack} direction="row" spacing=${1} flexWrap="wrap" sx=${{ justifyContent: "flex-end" }}>
                <${Chip}
                  label=${scenario.label}
                  sx=${{
                    bgcolor: "rgba(74,163,223,0.14)",
                    color: "#9dd4ff",
                    border: "1px solid rgba(74,163,223,0.35)",
                    fontWeight: 700,
                  }}
                />
                <${Chip}
                  label=${view === "public" ? "Public view" : "Full model"}
                  sx=${{
                    bgcolor: "rgba(208,139,46,0.14)",
                    color: "#ffd38d",
                    border: "1px solid rgba(208,139,46,0.35)",
                    fontWeight: 700,
                  }}
                />
                <${Chip}
                  label=${formatDate(data.meta?.priceDate)}
                  sx=${{
                    bgcolor: "rgba(70,209,190,0.14)",
                    color: "#a4f2e7",
                    border: "1px solid rgba(70,209,190,0.35)",
                    fontWeight: 700,
                  }}
                />
              </${Stack}>
            </${Toolbar}>
          </${AppBar}>

          <${Container} maxWidth="xl" sx=${{ pt: { xs: 2, md: 3 }, pb: 4 }}>
            <${SurfaceCard} sx=${{ p: { xs: 2.5, md: 3.5 }, mb: 2.5, position: "relative", overflow: "hidden" }}>
              <${Box}
                sx=${{
                  position: "absolute",
                  inset: 0,
                  background:
                    "radial-gradient(circle at 80% 0%, rgba(208,139,46,0.18), transparent 34%), radial-gradient(circle at 10% 10%, rgba(74,163,223,0.16), transparent 34%)",
                  pointerEvents: "none",
                }}
              />
              <${Grid} container spacing=${3} sx=${{ position: "relative", zIndex: 1 }}>
                <${Grid} item xs=${12} md=${7}>
                  <${Stack} spacing=${2.2}>
                    <${Box}>
                      <${Typography}
                        variant="overline"
                        sx=${{
                          display: "block",
                          color: "secondary.main",
                          letterSpacing: "0.16em",
                          fontWeight: 700,
                        }}
                      >
                        ${view === "public" ? "Public snapshot" : "Study-driven portfolio engine"}
                      </${Typography}>
                      <${Typography}
                        variant="h2"
                        sx=${{
                          mt: 1,
                          fontFamily: '"Space Grotesk", "IBM Plex Sans", sans-serif',
                          fontWeight: 700,
                          letterSpacing: "-0.05em",
                          lineHeight: 0.96,
                          fontSize: { xs: "2.4rem", md: "4rem" },
                        }}
                      >
                        ${view === "public"
                          ? "Snapshot publico da carteira global"
                          : "Rebalanceamento global com layout React e MUI"}
                      </${Typography}>
                      <${Typography}
                        variant="body1"
                        color="text.secondary"
                        sx=${{ mt: 1.8, maxWidth: 920, lineHeight: 1.75 }}
                        >
                        ${view === "public"
                          ? "A camada publica mostra resumo executivo, temas, precos globais e as cinco ideias mais convexas, sem expor holdings, residuals ou o livro completo."
                          : "Workspace unificado para rodar o modelo do estudo, importar carteiras CSV ou por input manual, monitorar precos globais de acoes, controlar cenarios, analisar setores e revisar risco com hierarquia visual mais clara."}
                      </${Typography}>
                    </${Box}>

                    <${Stack} spacing=${1.5}>
                      <${TextField}
                        label="Capital do modelo (USD)"
                        type="number"
                        value=${prefs.capital}
                        onChange=${(event) =>
                          setPrefs((current) => ({
                            ...current,
                            capital: Number(event.target.value) || 0,
                          }))}
                        inputProps=${{ min: 0, step: 1000, inputMode: "decimal" }}
                        fullWidth=${true}
                        sx=${{
                          maxWidth: 360,
                          "& .MuiOutlinedInput-root": {
                            background: "rgba(255,255,255,0.03)",
                          },
                        }}
                      />

                      <${ToggleButtonGroup}
                        value=${prefs.scenarioId}
                        exclusive=${true}
                        onChange=${(_, nextValue) => {
                          if (nextValue) {
                            setPrefs((current) => ({ ...current, scenarioId: nextValue }));
                          }
                        }}
                        fullWidth=${true}
                        sx=${{
                          display: "grid",
                          gap: 1,
                          gridTemplateColumns: { xs: "1fr", md: "repeat(3, minmax(0, 1fr))" },
                          "& .MuiToggleButtonGroup-grouped": {
                            borderRadius: 3,
                            border: "1px solid rgba(255,255,255,0.08) !important",
                            margin: 0,
                            alignItems: "stretch",
                            justifyContent: "flex-start",
                            textTransform: "none",
                            minHeight: 92,
                            padding: 1.5,
                          },
                        }}
                      >
                        ${safeArray(data.scenarios).map(
                          (item) => html`
                            <${ToggleButton}
                              key=${item.id}
                              value=${item.id}
                              sx=${{
                                display: "block",
                                color: "text.primary",
                                background:
                                  prefs.scenarioId === item.id
                                    ? "linear-gradient(180deg, rgba(74,163,223,0.16), rgba(255,255,255,0.04))"
                                    : "rgba(255,255,255,0.03)",
                              }}
                            >
                              <${Stack} spacing=${0.35} alignItems="flex-start">
                                <${Typography} sx=${{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
                                  ${item.label}
                                </${Typography}>
                                <${Typography} variant="caption" color="text.secondary" sx=${{ lineHeight: 1.4 }}>
                                  ${item.description}
                                </${Typography}>
                                <${Typography} variant="caption" color="secondary.main" sx=${{ mt: 0.3 }}>
                                  Liquidez ${formatPct((Number(item.cashTargetPct) || 0) + (Number(item.xovrTargetPct) || 0) + (Number(item.bondTargetPct) || 0))}
                                </${Typography}>
                              </${Stack}>
                            </${ToggleButton}>
                          `
                        )}
                      </${ToggleButtonGroup}>
                    </${Stack}>
                  </${Stack}>
                </${Grid}>

                <${Grid} item xs=${12} md=${5}>
                  <${Stack} spacing=${1.6}>
                    <${Paper}
                      elevation=${0}
                      sx=${{
                        p: 2.2,
                        borderRadius: 4,
                        border: "1px solid rgba(255,255,255,0.08)",
                        background: "rgba(255,255,255,0.04)",
                      }}
                    >
                      <${Stack} spacing=${0.5}>
                        <${Typography} variant="overline" color="secondary.main" sx=${{ letterSpacing: "0.16em", fontWeight: 700 }}>
                          ${view === "public" ? "Leitura publica" : "Leitura do cenario"}
                        </${Typography}>
                        <${Typography}
                          variant="h4"
                          sx=${{
                            fontFamily: '"Space Grotesk", sans-serif',
                            fontWeight: 700,
                            letterSpacing: "-0.04em",
                          }}
                        >
                          ${scenario.label}
                        </${Typography}>
                        <${Typography} variant="body2" color="text.secondary" sx=${{ lineHeight: 1.6 }}>
                          ${scenario.description}
                        </${Typography}>
                      </${Stack}>
                    </${Paper}>

                    <${Grid} container spacing=${1.5}>
                      <${Grid} item xs=${12} sm=${6}>
                        <${RailMetric}
                          label="Liquidez alvo"
                          value=${formatPct(model.liquidityTargetPct)}
                          caption="Target"
                          accent="#d08b2e"
                        />
                      </${Grid}>
                      <${Grid} item xs=${12} sm=${6}>
                        <${RailMetric}
                          label="Capital investivel"
                          value=${formatMoney(model.investableValue)}
                          caption="Deploy"
                          accent="#4aa3df"
                        />
                      </${Grid}>
                      <${Grid} item xs=${12} sm=${6}>
                        <${RailMetric}
                          label="Snapshot"
                          value=${formatDate(data.meta?.priceDate)}
                          caption="Data"
                          accent="#46d1be"
                        />
                      </${Grid}>
                      <${Grid} item xs=${12} sm=${6}>
                        <${RailMetric}
                          label="Non-USD"
                          value=${formatPct(displayNonUsdShare)}
                          caption="FX"
                          accent="#7e8cff"
                        />
                      </${Grid}>
                    </${Grid}>

                    <${Alert}
                      severity=${view === "public" ? "info" : "warning"}
                      variant="outlined"
                      sx=${{
                        borderColor: view === "public" ? "rgba(74,163,223,0.35)" : "rgba(208,139,46,0.35)",
                        bgcolor: view === "public" ? "rgba(74,163,223,0.08)" : "rgba(208,139,46,0.08)",
                        "& .MuiAlert-icon": {
                          color: view === "public" ? "#9dd4ff" : "#ffd38d",
                        },
                      }}
                    >
                      ${view === "public"
                        ? "Versao sanitizada: holdings, residuals e watchlist completa nao sao exibidos."
                        : "Modelo interno: trades, holdings e residuals permanecem visiveis para revisar risco e execucao."}
                    </${Alert}>
                  </${Stack}>
                </${Grid}>
              </${Grid}>
            </${SurfaceCard}>

            <${Stack} direction="row" spacing=${1} flexWrap="wrap" sx=${{ mb: 2 }}>
              ${summaryChips.map(
                (chip) => html`
                  <${Chip}
                    key=${chip}
                    label=${chip}
                    sx=${{
                      bgcolor: "rgba(255,255,255,0.04)",
                      color: "text.secondary",
                      border: "1px solid rgba(255,255,255,0.08)",
                      fontWeight: 700,
                    }}
                  />
                `
              )}
            </${Stack}>

            <${SurfaceCard} sx=${{ p: 1.25, mb: 2.5 }}>
              <${Tabs}
                value=${currentTab}
                onChange=${(_, nextValue) => setPrefs((current) => ({ ...current, tab: nextValue }))}
                variant=${isDesktop ? "standard" : "scrollable"}
                scrollButtons="auto"
                allowScrollButtonsMobile=${true}
                sx=${{
                  minHeight: 56,
                  "& .MuiTabs-indicator": {
                    height: 3,
                    borderRadius: 999,
                    background: "linear-gradient(90deg, #4aa3df, #d08b2e)",
                  },
                  "& .MuiTab-root": {
                    minHeight: 56,
                    textTransform: "none",
                    fontWeight: 700,
                    letterSpacing: "0.01em",
                  },
                }}
              >
                ${availableTabs.map(
                  (tabItem) => html`
                    <${Tab} key=${tabItem.id} value=${tabItem.id} label=${tabItem.label} />
                  `
                )}
              </${Tabs}>
            </${SurfaceCard}>

            <${TabPanel} active=${currentTab} value="overview">
              <${Stack} spacing=${2.5}>
                <${Grid} container spacing=${2}>
                  ${metricCards.map(
                    (metric) => html`
                      <${Grid} item xs=${12} sm=${6} lg=${2}>
                        <${MetricCard}
                          accent=${metric.accent}
                          label=${metric.label}
                          value=${metric.value}
                          helper=${metric.helper}
                        />
                      </${Grid}>
                    `
                  )}
                </${Grid}>

                <${Grid} container spacing=${2}>
                  <${Grid} item xs=${12} lg=${7}>
                    <${SurfaceCard} sx=${{ p: 2.5, height: "100%" }}>
                      <${SectionTitle}
                        eyebrow=${view === "public" ? "Mapa tematico" : "Peso por tema"}
                        title=${view === "public"
                          ? "Cestas tematicas do estudo"
                          : "Alocacao do cenario selecionado"}
                        subtitle=${view === "public"
                          ? "A versao publica usa a composicao por tema e a quantidade de ativos em cada cesta para manter a leitura estrutural sem expor a carteira completa."
                          : "Os pesos abaixo mostram a leitura do cenario selecionado, com current vs target para cada tema e a faixa de liquidez destacada."}
                      />
                      <${Stack} spacing=${1.4}>
                        ${view === "public"
                          ? themeCards.map(
                              (row) => html`<${DistributionRow} key=${row.id} row=${row} mode="public" />`
                            )
                          : model.themeRows.map(
                              (row) => html`<${DistributionRow} key=${row.key} row=${row} mode="full" />`
                            )}
                      </${Stack}>
                    </${SurfaceCard}>
                  </${Grid}>

                  <${Grid} item xs=${12} lg=${5}>
                    <${Stack} spacing=${2.5}>
                      ${view === "full"
                        ? html`
                            <${SurfaceCard} sx=${{ p: 2.5 }}>
                              <${SectionTitle}
                                eyebrow="Geografia"
                                title="Leitura global da carteira"
                                subtitle="A geografia ajuda a enxergar concentracao por pais e o risco de depender demais de um unico mercado."
                              />
                              <${Stack} spacing=${1.4}>
                                ${model.regionRows.map(
                                  (row) => html`<${DistributionRow} key=${row.key} row=${row} mode="full" />`
                                )}
                              </${Stack}>
                            </${SurfaceCard}>

                            <${SurfaceCard} sx=${{ p: 2.5 }}>
                              <${SectionTitle}
                                eyebrow="Moeda"
                                title="Exposicao cambial"
                                subtitle="O mapa de moeda mostra quanto da carteira e convertido para USD e quanto permanece exposto a outras divisas."
                              />
                              <${Stack} spacing=${1.4}>
                                ${model.currencyRows.map(
                                  (row) => html`<${DistributionRow} key=${row.key} row=${row} mode="full" />`
                                )}
                              </${Stack}>
                            </${SurfaceCard}>
                          `
                        : html`
                            <${SurfaceCard} sx=${{ p: 2.5 }}>
                              <${SectionTitle}
                                eyebrow="Nota publica"
                                title="Como interpretar este snapshot"
                                subtitle="A pagina publica e propositalmente mais enxuta. Os detalhes operacionais ficam escondidos, mas o modelo, os temas e as ideias principais continuam acessiveis."
                              />
                              <${Stack} spacing=${1.3}>
                                ${safeArray(notes).map(
                                  (note) => html`
                                    <${Alert} severity="info" variant="outlined" sx=${{ bgcolor: "rgba(74,163,223,0.08)" }}>
                                      ${note}
                                    </${Alert}>
                                  `
                                )}
                              </${Stack}>
                            </${SurfaceCard}>

                            <${SurfaceCard} sx=${{ p: 2.5 }}>
                              <${SectionTitle}
                                eyebrow="Sinalizador"
                                title="Cenario ativo"
                                subtitle="O cenario selecionado ajusta a liquidez, redistribui os temas e altera o peso relativo das teses mais convexas."
                              />
                              <${Stack} spacing=${1.2}>
                                <${RailMetric}
                                  label="Liquidez total"
                                  value=${formatPct(model.liquidityTargetPct)}
                                  caption="Target"
                                  accent="#d08b2e"
                                />
                                <${RailMetric}
                                  label="Top 5 share"
                                  value=${formatPct(Number(data.meta?.baseTopFiveShare) || model.topFiveShare)}
                                  caption="Concentracao"
                                  accent="#ff7a59"
                                />
                              </${Stack}>
                            </${SurfaceCard}>
                          `}

                      ${view === "full" && model.hasExports
                        ? html`
                            <${SurfaceCard} sx=${{ p: 2.5 }}>
                              <${SectionTitle}
                                eyebrow="Exports"
                                title="Arquivos prontos para analise"
                                subtitle="Os CSVs saem da pipeline e sao copiados para a versao publica, inclusive os arquivos do estudo e o snapshot de precos globais."
                              />
                              <${Stack} direction="row" spacing=${1} flexWrap="wrap">
                                ${exportsData.marketPricesFile
                                  ? html`<${Button}
                                      component="a"
                                      href=${exportsData.marketPricesFile}
                                      download=${true}
                                      variant="outlined"
                                    >
                                      Precos globais CSV
                                    </${Button}>`
                                  : null}
                                ${exportsData.fxRatesFile
                                  ? html`<${Button}
                                      component="a"
                                      href=${exportsData.fxRatesFile}
                                      download=${true}
                                      variant="outlined"
                                    >
                                      FX CSV
                                    </${Button}>`
                                  : null}
                                ${exportsData.scenarioSummaryFile
                                  ? html`<${Button}
                                      component="a"
                                      href=${exportsData.scenarioSummaryFile}
                                      download=${true}
                                      variant="outlined"
                                    >
                                      Resumo dos cenarios
                                    </${Button}>`
                                  : null}
                                ${(exportsData.scenarioFiles || []).map(
                                  (scenarioFile) => html`
                                    <${Button}
                                      key=${scenarioFile.file}
                                      component="a"
                                      href=${scenarioFile.file}
                                      download=${true}
                                      variant="contained"
                                      color="secondary"
                                      sx=${{ bgcolor: "secondary.main" }}
                                    >
                                      ${scenarioFile.label}
                                    </${Button}>
                                  `
                                )}
                              </${Stack}>
                            </${SurfaceCard}>
                          `
                        : null}
                    </${Stack}>
                  </${Grid}>
                </${Grid}>
              </${Stack}>
            </${TabPanel}>

            <${TabPanel} active=${currentTab} value="market">
              <${Stack} spacing=${2.5}>
                <${SurfaceCard} sx=${{ p: 2.5 }}>
                  <${SectionTitle}
                    eyebrow="Mercado global"
                    title="Precos locais, FX e equivalentes em USD"
                    subtitle="A tabela abaixo combina o snapshot local com a conversao cambial para um equivalente em USD."
                    action=${html`
                      <${Stack} direction="row" spacing=${1} flexWrap="wrap">
                        <${Chip} label=${`${model.marketOkCount} ok`} sx=${{ bgcolor: "rgba(70,209,190,0.14)", color: "#46d1be" }} />
                        <${Chip} label=${`${model.marketMissingCount} missing`} sx=${{ bgcolor: "rgba(255,122,89,0.14)", color: "#ff7a59" }} />
                        <${Chip} label=${`${model.marketPrices.length} ativos`} sx=${{ bgcolor: "rgba(74,163,223,0.14)", color: "#9dd4ff" }} />
                      </${Stack}>
                    `}
                  />
                  <${TableContainer}
                    component=${Paper}
                    elevation=${0}
                    sx=${{
                      borderRadius: 3,
                      border: "1px solid rgba(255,255,255,0.08)",
                      background: "rgba(255,255,255,0.03)",
                    }}
                  >
                    <${Table} stickyHeader size="small" sx=${{ minWidth: 980 }}>
                      <${TableHead}>
                        <${TableRow}>
                          <${TableCell}>Ativo</${TableCell}>
                          <${TableCell}>Yahoo</${TableCell}>
                          <${TableCell}>Moeda</${TableCell}>
                          <${TableCell}>Preco local</${TableCell}>
                          <${TableCell}>FX/USD</${TableCell}>
                          <${TableCell}>Preco USD</${TableCell}>
                          <${TableCell}>Data</${TableCell}>
                          <${TableCell}>Status</${TableCell}>
                        </${TableRow}>
                      </${TableHead}>
                      <${TableBody}>
                        ${model.marketPrices
                          .slice()
                          .sort((a, b) => String(a.symbol).localeCompare(String(b.symbol)))
                          .map((row) => html`<${MarketRow} key=${row.symbol} row=${row} />`)}
                      </${TableBody}>
                    </${Table}>
                  </${TableContainer}>
                </${SurfaceCard}>
              </${Stack}>
            </${TabPanel}>

            <${TabPanel} active=${currentTab} value="execution">
              <${Stack} spacing=${2.5}>
                <${SurfaceCard} sx=${{ p: 2.5 }}>
                  <${SectionTitle}
                    eyebrow="Execucao"
                    title="Trades do modelo"
                    subtitle="Os filtros ajudam a separar compras, reducoes, manutencao e a camada de liquidez."
                  />
                  <${Stack}
                    direction="row"
                    justifyContent="space-between"
                    alignItems="center"
                    spacing=${2}
                    sx=${{ mb: 2, flexWrap: "wrap" }}
                  >
                    <${ToggleButtonGroup}
                      value=${prefs.filter}
                      exclusive=${true}
                      onChange=${(_, nextValue) => {
                        if (nextValue) {
                          setPrefs((current) => ({ ...current, filter: nextValue }));
                        }
                      }}
                      size="small"
                      sx=${{
                        flexWrap: "wrap",
                        "& .MuiToggleButton-root": {
                          textTransform: "none",
                          fontWeight: 700,
                          borderColor: "rgba(255,255,255,0.08)",
                        },
                      }}
                    >
                      ${["Todos", "Comprar", "Reduzir", "Manter", "Liquidez"].map(
                        (item) => html`<${ToggleButton} key=${item} value=${item}>${item}</${ToggleButton}>`
                      )}
                    </${ToggleButtonGroup}>

                    <${FormControl} size="small" sx=${{ minWidth: 220 }}>
                      <${Select}
                        value=${prefs.sort}
                        onChange=${(event) => {
                          setPrefs((current) => ({ ...current, sort: event.target.value }));
                        }}
                      >
                        <${MenuItem} value="absTrade">Maior movimento</${MenuItem}>
                        <${MenuItem} value="targetWeight">Maior peso alvo</${MenuItem}>
                        <${MenuItem} value="theme">Tema</${MenuItem}>
                      </${Select}>
                    </${FormControl}>
                  </${Stack}>

                  ${model.hasTradeModel
                    ? html`
                        <${TableContainer}
                          component=${Paper}
                          elevation=${0}
                          sx=${{
                            borderRadius: 3,
                            border: "1px solid rgba(255,255,255,0.08)",
                            background: "rgba(255,255,255,0.03)",
                          }}
                        >
                          <${Table} stickyHeader size="small" sx=${{ minWidth: 1080 }}>
                            <${TableHead}>
                              <${TableRow}>
                                <${TableCell}>Ativo</${TableCell}>
                                <${TableCell}>Tema</${TableCell}>
                                <${TableCell}>Regiao</${TableCell}>
                                <${TableCell}>Atual</${TableCell}>
                                <${TableCell}>Alvo</${TableCell}>
                                <${TableCell}>Gap</${TableCell}>
                                <${TableCell}>Acao</${TableCell}>
                                <${TableCell}>Racional</${TableCell}>
                              </${TableRow}>
                            </${TableHead}>
                            <${TableBody}>
                              ${model.tradeRows
                                .filter((row) => prefs.filter === "Todos" || row.action === prefs.filter)
                                .sort((a, b) => {
                                  if (prefs.sort === "targetWeight") {
                                    return Number(b.targetWeight) - Number(a.targetWeight) || Number(b.absTrade) - Number(a.absTrade);
                                  }
                                  if (prefs.sort === "theme") {
                                    return String(a.themeLabel).localeCompare(String(b.themeLabel)) || Number(b.absTrade) - Number(a.absTrade);
                                  }
                                  return Number(b.absTrade) - Number(a.absTrade);
                                })
                                .map((row) => html`<${TradeRow} key=${row.asset} row=${row} />`)}
                            </${TableBody}>
                          </${Table}>
                        </${TableContainer}>
                      `
                    : html`
                        <${Alert} severity="info" variant="outlined" sx=${{ bgcolor: "rgba(74,163,223,0.08)" }}>
                          Este snapshot nao possui a camada de trades detalhados.
                        </${Alert}>
                      `}
                </${SurfaceCard}>
              </${Stack}>
            </${TabPanel}>

            <${TabPanel} active=${currentTab} value="study">
              <${Stack} spacing=${2.5}>
                <${Grid} container spacing=${2}>
                  <${Grid} item xs=${12} lg=${5}>
                    <${SurfaceCard} sx=${{ p: 2.5, height: "100%" }}>
                      <${SectionTitle}
                        eyebrow="Blueprint"
                        title="Basket sugerido pelo estudo"
                        subtitle="As faixas abaixo sintetizam a logica por tema sugerida no material anexado."
                      />
                      <${Stack} spacing=${1.2}>
                        ${basketBlueprint.map(
                          (entry, index) => html`<${BlueprintAccordion} key=${entry.label} entry=${entry} index=${index} />`
                        )}
                      </${Stack}>
                    </${SurfaceCard}>
                  </${Grid}>

                  <${Grid} item xs=${12} lg=${7}>
                    <${SurfaceCard} sx=${{ p: 2.5 }}>
                      <${SectionTitle}
                        eyebrow="Principios"
                        title="O que o estudo quer preservar"
                        subtitle="A lista de principios orienta concentracao, liquidez e optionalidade em varias teses ao mesmo tempo."
                      />
                      <${Stack} direction="row" spacing=${1} flexWrap="wrap" sx=${{ mb: 2 }}>
                        ${principles.map(
                          (principle) => html`
                            <${Chip}
                              key=${principle}
                              label=${principle}
                              sx=${{
                                mb: 1,
                                mr: 1,
                                bgcolor: "rgba(255,255,255,0.04)",
                                border: "1px solid rgba(255,255,255,0.08)",
                                color: "text.primary",
                                fontWeight: 600,
                              }}
                            />
                          `
                        )}
                      </${Stack}>

                      <${Divider} sx=${{ my: 2 }} />

                      <${SectionTitle}
                        eyebrow="Top ideas"
                        title="Cinco teses mais convexas"
                        subtitle="Os cards abaixo agrupam as teses que o estudo trata como mais assimetricas."
                      />
                      <${Grid} container spacing=${2}>
                        ${topIdeas.map(
                          (idea) => html`
                            <${Grid} item xs=${12} sm=${6} xl=${4} key=${idea.symbol}>
                              <${IdeaCard} idea=${idea} />
                            </${Grid}>
                          `
                        )}
                      </${Grid}>
                    </${SurfaceCard}>
                  </${Grid}>
                </${Grid}>
              </${Stack}>
            </${TabPanel}>

            <${TabPanel} active=${currentTab} value="sectors">
              <${Stack} spacing=${2.5}>
                <${SurfaceCard} sx=${{ p: 2.5 }}>
                  <${SectionTitle}
                    eyebrow="Setores"
                    title=${view === "public" ? "Leitura setorial pública" : "Stock picking por setores"}
                    subtitle=${view === "public"
                      ? "A versão pública agrupa apenas as ideias e temas principais do snapshot sanitizado."
                      : "A watchlist é agrupada por buckets setoriais para facilitar comparação de upside, prioridade e tese."}
                    action=${html`
                      <${Stack} direction="row" spacing=${1} flexWrap="wrap">
                        <${Chip}
                          label=${`${sectorInsights.length} grupos`}
                          sx=${{
                            bgcolor: "rgba(74,163,223,0.14)",
                            color: "#9dd4ff",
                            border: "1px solid rgba(74,163,223,0.35)",
                            fontWeight: 700,
                          }}
                        />
                        <${Chip}
                          label=${activeSectorGroup ? activeSectorGroup.label : "Sem seleção"}
                          sx=${{
                            bgcolor: "rgba(208,139,46,0.14)",
                            color: "#ffd38d",
                            border: "1px solid rgba(208,139,46,0.35)",
                            fontWeight: 700,
                          }}
                        />
                      </${Stack}>
                    `}
                  />

                  <${ToggleButtonGroup}
                    value=${selectedSectorId}
                    exclusive=${true}
                    onChange=${(_, nextValue) => {
                      if (nextValue) {
                        setPrefs((current) => ({ ...current, selectedSector: nextValue }));
                      }
                    }}
                    size="small"
                    sx=${{
                      display: "flex",
                      flexWrap: "wrap",
                      gap: 1,
                      "& .MuiToggleButton-root": {
                        textTransform: "none",
                        fontWeight: 700,
                        borderColor: "rgba(255,255,255,0.08)",
                        borderRadius: 999,
                        px: 2,
                      },
                    }}
                  >
                    ${sectorInsights.map(
                      (group) => html`<${ToggleButton} key=${group.bucket} value=${group.bucket}>${group.label}</${ToggleButton}>`
                    )}
                  </${ToggleButtonGroup}>
                </${SurfaceCard}>

                <${Grid} container spacing=${2}>
                  <${Grid} item xs=${12} lg=${7}>
                    <${Grid} container spacing=${2}>
                      ${sectorInsights.map(
                        (group) => html`
                          <${Grid} item xs=${12} sm=${6} key=${group.bucket}>
                            <${SectorGroupCard}
                              group=${group}
                              selected=${group.bucket === selectedSectorId}
                              onClick=${() => setPrefs((current) => ({ ...current, selectedSector: group.bucket }))}
                            />
                          </${Grid}>
                        `
                      )}
                    </${Grid}>
                  </${Grid}>

                  <${Grid} item xs=${12} lg=${5}>
                    <${Stack} spacing=${2.5}>
                      <${SurfaceCard} sx=${{ p: 2.5 }}>
                        <${SectionTitle}
                          eyebrow="Detalhe"
                          title=${activeSectorGroup ? activeSectorGroup.label : "Setor selecionado"}
                          subtitle=${activeSectorGroup ? activeSectorGroup.description : "Escolha um setor para abrir a leitura detalhada."}
                        />

                        ${activeSectorGroup
                          ? html`
                              <${Stack} spacing=${1.3}>
                                <${Stack} direction="row" spacing=${1} flexWrap="wrap">
                                  <${Chip}
                                    size="small"
                                    label=${`${activeSectorGroup.count} nomes`}
                                    sx=${{
                                      bgcolor: "rgba(74,163,223,0.14)",
                                      color: "#9dd4ff",
                                      border: "1px solid rgba(74,163,223,0.35)",
                                      fontWeight: 700,
                                    }}
                                  />
                                  <${Chip}
                                    size="small"
                                    label=${`${formatPct(activeSectorGroup.averageUpside || 0)} upside médio`}
                                    sx=${{
                                      bgcolor: "rgba(70,209,190,0.14)",
                                      color: "#46d1be",
                                      border: "1px solid rgba(70,209,190,0.35)",
                                      fontWeight: 700,
                                    }}
                                  />
                                  <${Chip}
                                    size="small"
                                    label=${activeSectorGroup.bestPick ? `Top: ${activeSectorGroup.bestPick.symbol}` : "Sem top pick"}
                                    sx=${{
                                      bgcolor: "rgba(255,255,255,0.05)",
                                      color: "text.secondary",
                                      border: "1px solid rgba(255,255,255,0.08)",
                                      fontWeight: 700,
                                    }}
                                  />
                                </${Stack}>

                                <${Alert} severity="info" variant="outlined" sx=${{ bgcolor: "rgba(74,163,223,0.08)" }}>
                                  ${activeSectorGroup.summary || "Sem picks suficientes para formar um resumo."}
                                </${Alert}>

                                <${TableContainer}
                                  component=${Paper}
                                  elevation=${0}
                                  sx=${{
                                    borderRadius: 3,
                                    border: "1px solid rgba(255,255,255,0.08)",
                                    background: "rgba(255,255,255,0.03)",
                                  }}
                                >
                                  <${Table} stickyHeader size="small" sx=${{ minWidth: 520 }}>
                                    <${TableHead}>
                                      <${TableRow}>
                                        <${TableCell}>Ticker</${TableCell}>
                                        <${TableCell}>Upside</${TableCell}>
                                        <${TableCell}>Prioridade</${TableCell}>
                                      </${TableRow}>
                                    </${TableHead}>
                                    <${TableBody}>
                                      ${activeSectorGroup.items.map(
                                        (item) => html`
                                          <${TableRow} key=${item.symbol}>
                                            <${TableCell}>
                                              <${Typography} sx=${{ fontWeight: 700 }}>${item.symbol}</${Typography}>
                                              <${Typography} variant="caption" color="text.secondary">
                                                ${item.name}
                                              </${Typography}>
                                            </${TableCell}>
                                            <${TableCell}>${formatPct(item.upsidePct)}</${TableCell}>
                                            <${TableCell}>${formatPriority(item.priority)}</${TableCell}>
                                          </${TableRow}>
                                        `
                                      )}
                                    </${TableBody}>
                                  </${Table}>
                                </${TableContainer}>
                              </${Stack}>
                            `
                          : html`
                              <${Alert} severity="info" variant="outlined" sx=${{ bgcolor: "rgba(74,163,223,0.08)" }}>
                                Nenhum setor disponível nesta visualização.
                              </${Alert}>
                            `}
                      </${SurfaceCard}>

                      <${SurfaceCard} sx=${{ p: 2.5 }}>
                        <${SectionTitle}
                          eyebrow="Leitura"
                          title="Como usar este painel"
                          subtitle="Escolha um bucket, abra as melhores teses e compare o upside com a prioridade do estudo."
                        />
                        <${Stack} spacing=${1.2}>
                          <${Alert} severity="success" variant="outlined" sx=${{ bgcolor: "rgba(70,209,190,0.08)" }}>
                            Foque em setores com upside alto e tese clara antes de aumentar peso.
                          </${Alert}>
                          <${Alert} severity="warning" variant="outlined" sx=${{ bgcolor: "rgba(208,139,46,0.08)" }}>
                            Use o perfil de risco para decidir o tamanho da posição, nao apenas o upside.
                          </${Alert}>
                        </${Stack}>
                      </${SurfaceCard}>
                    </${Stack}>
                  </${Grid}>
                </${Grid}>
              </${Stack}>
            </${TabPanel}>

            <${TabPanel} active=${currentTab} value="risk">
              <${Stack} spacing=${2.5}>
                <${SurfaceCard} sx=${{ p: 2.5 }}>
                  <${SectionTitle}
                    eyebrow="Risco"
                    title=${view === "public" ? "Painel sanitizado de risco" : "Gestão de risco da carteira"}
                    subtitle=${view === "public"
                      ? "A leitura pública mostra apenas métricas agregadas do snapshot."
                      : "Escolha um perfil e acompanhe os limites principais antes de executar novas teses."}
                    action=${view === "full"
                      ? html`
                          <${FormControl} size="small" sx=${{ minWidth: 220 }}>
                            <${Select}
                              value=${prefs.riskProfileId}
                              onChange=${(event) =>
                                setPrefs((current) => ({ ...current, riskProfileId: event.target.value }))}
                            >
                              <${MenuItem} value="balanced">Balanceado</${MenuItem}>
                              <${MenuItem} value="defensive">Defensivo</${MenuItem}>
                              <${MenuItem} value="convex">Convexo</${MenuItem}>
                            </${Select}>
                          </${FormControl}>
                        `
                      : null}
                  />

                  <${Grid} container spacing=${2}>
                    <${Grid} item xs=${12} sm=${6} lg=${3}>
                      <${RailMetric}
                        label="Liquidez"
                        value=${formatPct(view === "full" ? (importedSimulation.uploadedValue > 0 ? (importedSimulation.uploadedCurrentLiquidityValue / importedSimulation.uploadedValue) * 100 : Number(data.meta?.liquidityCurrentPct) || 0) : Number(data.meta?.liquidityCurrentPct) || liquidityShare)}
                        caption="Atual"
                        accent="#d08b2e"
                      />
                    </${Grid}>
                    <${Grid} item xs=${12} sm=${6} lg=${3}>
                      <${RailMetric}
                        label="Top 5"
                        value=${formatPct(view === "full" ? importedSimulation.model.topFiveShare : Number(data.meta?.baseTopFiveShare) || model.topFiveShare)}
                        caption="Conc."
                        accent="#ff7a59"
                      />
                    </${Grid}>
                    <${Grid} item xs=${12} sm=${6} lg=${3}>
                      <${RailMetric}
                        label="Não-USD"
                        value=${formatPct(view === "full" ? importedSimulation.model.nonUsdShare : displayNonUsdShare)}
                        caption="FX"
                        accent="#7e8cff"
                      />
                    </${Grid}>
                    <${Grid} item xs=${12} sm=${6} lg=${3}>
                      <${RailMetric}
                        label="Residuais"
                        value=${integerFormatter.format(view === "full" ? importedSimulation.residualCount : Number(data.meta?.residualCount) || 0)}
                        caption="Out"
                        accent="#8f99a8"
                      />
                    </${Grid}>
                  </${Grid}>
                </${SurfaceCard}>

                ${view === "full"
                  ? html`
                      <${Grid} container spacing=${2}>
                        ${portfolioRiskChecks.map(
                          (check) => html`
                            <${Grid} item xs=${12} md=${6} lg=${4}>
                              <${RiskCheckCard} key=${check.key} check=${check} />
                            </${Grid}>
                          `
                        )}
                      </${Grid}>

                      <${SurfaceCard} sx=${{ p: 2.5 }}>
                        <${SectionTitle}
                          eyebrow="Ações"
                          title="O que fazer agora"
                          subtitle="As recomendações abaixo seguem os limites do perfil selecionado e o estado da carteira simulada."
                        />
                        <${Stack} spacing=${1.2}>
                          ${riskRecommendations.map(
                            (note) => html`
                              <${Alert} key=${note} severity="warning" variant="outlined" sx=${{ bgcolor: "rgba(208,139,46,0.08)" }}>
                                ${note}
                              </${Alert}>
                            `
                          )}
                        </${Stack}>
                      </${SurfaceCard}>
                    `
                  : html`
                      <${SurfaceCard} sx=${{ p: 2.5 }}>
                        <${SectionTitle}
                          eyebrow="Leitura pública"
                          title="Resumo agregado do risco"
                          subtitle="A versão pública preserva a narrativa de risco sem expor a carteira operacional."
                        />
                        <${Stack} spacing=${1.2}>
                          ${safeArray(notes).map(
                            (note) => html`
                              <${Alert} severity="info" variant="outlined" sx=${{ bgcolor: "rgba(74,163,223,0.08)" }}>
                                ${note}
                              </${Alert}>
                            `
                          )}
                        </${Stack}>
                      </${SurfaceCard}>
                    `}
              </${Stack}>
            </${TabPanel}>

            <${TabPanel} active=${currentTab} value="simulator">
              <${Stack} spacing=${2.5}>
                <${SurfaceCard} sx=${{ p: 2.5 }}>
                  <${SectionTitle}
                    eyebrow="Simulador"
                    title="Importe uma carteira CSV ou edite manualmente"
                    subtitle="Aceita ticker, quantidade, preço local, valor em USD, moeda e setor. Tickers fora do modelo ficam como residuais."
                    action=${html`
                      <${Stack} direction="row" spacing=${1} flexWrap="wrap">
                        <${Button} variant="outlined" onClick=${loadCurrentPortfolio}>Carregar carteira atual</${Button}>
                        <${Button} variant="outlined" onClick=${clearPortfolioRows}>Limpar</${Button}>
                        <${Button} component="label" variant="contained" color="secondary" sx=${{ bgcolor: "secondary.main" }}>
                          Upload CSV
                          <input hidden type="file" accept=".csv,text/csv" onChange=${handlePortfolioCsvUpload} />
                        </${Button}>
                      </${Stack}>
                    `}
                  />
                  ${portfolioNotice
                    ? html`
                        <${Alert} severity="info" variant="outlined" sx=${{ mb: 2, bgcolor: "rgba(74,163,223,0.08)" }}>
                          ${portfolioNotice}
                        </${Alert}>
                      `
                    : null}

                  <${Grid} container spacing=${2}>
                    <${Grid} item xs=${12} lg=${7}>
                      <${Stack} spacing=${1.5}>
                        <${SurfaceCard} sx=${{ p: 2.2 }}>
                          <${Stack} spacing=${1.5}>
                            <${Stack} direction="row" justifyContent="space-between" alignItems="center" spacing=${2}>
                              <${Box}>
                                <${Typography} sx=${{ fontWeight: 700 }}>
                                  Capital para a simulação
                                </${Typography}>
                                <${Typography} variant="caption" color="text.secondary">
                                  O cenário usa este capital para recalcular pesos e trades.
                                </${Typography}>
                              </${Box}>
                              <${Chip}
                                label=${scenario.label}
                                sx=${{
                                  bgcolor: "rgba(74,163,223,0.14)",
                                  color: "#9dd4ff",
                                  border: "1px solid rgba(74,163,223,0.35)",
                                  fontWeight: 700,
                                }}
                              />
                            </${Stack}>

                            <${TextField}
                              label="Capital da carteira (USD)"
                              type="number"
                              value=${prefs.portfolioCapital}
                              onChange=${(event) =>
                                setPrefs((current) => ({
                                  ...current,
                                  portfolioCapital: Number(event.target.value) || 0,
                                }))}
                              inputProps=${{ min: 0, step: 1000, inputMode: "decimal" }}
                              fullWidth=${true}
                              sx=${{
                                maxWidth: 360,
                                "& .MuiOutlinedInput-root": {
                                  background: "rgba(255,255,255,0.03)",
                                },
                              }}
                            />

                            <${Stack} direction="row" spacing=${1} flexWrap="wrap">
                              <${Button} variant="outlined" onClick=${addPortfolioRow}>Adicionar linha</${Button}>
                              <${Button}
                                variant="text"
                                onClick=${() =>
                                  setPrefs((current) => ({
                                    ...current,
                                    portfolioCapital: importedSimulation.uploadedValue || current.portfolioCapital || current.capital,
                                  }))}
                              >
                                Usar valor importado
                              </${Button}>
                            </${Stack}>
                          </${Stack}>
                        </${SurfaceCard}>

                        <${Stack} spacing=${1.5}>
                          ${portfolioRows.map(
                            (row, index) => html`
                              <${PortfolioDraftRow}
                                key=${row.id}
                                row=${row}
                                index=${index}
                                onChange=${(field, value) => patchPortfolioRow(index, field, value)}
                                onRemove=${() => removePortfolioRow(index)}
                                onDuplicate=${() => duplicatePortfolioRow(index)}
                              />
                            `
                          )}
                        </${Stack}>
                      </${Stack}>
                    </${Grid}>

                    <${Grid} item xs=${12} lg=${5}>
                      <${Stack} spacing=${2.5}>
                        <${SurfaceCard} sx=${{ p: 2.5 }}>
                          <${SectionTitle}
                            eyebrow="Resumo"
                            title="Leitura da carteira importada"
                            subtitle="Os números abaixo usam o arquivo ou a edição manual para simular o cenário ativo."
                          />
                          <${Grid} container spacing=${1.5}>
                            <${Grid} item xs=${12} sm=${6}>
                              <${RailMetric}
                                label="Valor importado"
                                value=${formatMoney(importedSimulation.uploadedValue)}
                                caption="USD"
                                accent="#46d1be"
                              />
                            </${Grid}>
                            <${Grid} item xs=${12} sm=${6}>
                              <${RailMetric}
                                label="Capital simulado"
                                value=${formatMoney(importedSimulation.simulationCapital)}
                                caption="Base"
                                accent="#4aa3df"
                              />
                            </${Grid}>
                            <${Grid} item xs=${12} sm=${6}>
                              <${RailMetric}
                                label="Liquidez"
                                value=${formatPct(importedSimulation.uploadedValue > 0 ? (importedSimulation.uploadedCurrentLiquidityValue / importedSimulation.uploadedValue) * 100 : 0)}
                                caption="Atual"
                                accent="#d08b2e"
                              />
                            </${Grid}>
                            <${Grid} item xs=${12} sm=${6}>
                              <${RailMetric}
                                label="Residuais"
                                value=${integerFormatter.format(importedSimulation.residualCount)}
                                caption="Out"
                                accent="#8f99a8"
                              />
                            </${Grid}>
                          </${Grid}>
                          <${Stack} spacing=${1.2} sx=${{ mt: 2 }}>
                            <${Alert} severity="info" variant="outlined" sx=${{ bgcolor: "rgba(74,163,223,0.08)" }}>
                              ${importedSimulation.importedCount} linhas importadas e ${importedSimulation.baseMatchedCount} alinhadas ao modelo.
                            </${Alert}>
                            <${Alert} severity="warning" variant="outlined" sx=${{ bgcolor: "rgba(208,139,46,0.08)" }}>
                              ${importedSimulation.unmappedSymbols.length
                                ? `${importedSimulation.unmappedSymbols.length} tickers ficaram fora da cesta principal e foram tratados como residuais.`
                                : "Todos os tickers da carteira importada estão mapeados para o modelo principal."}
                            </${Alert}>
                          </${Stack}>
                        </${SurfaceCard}>

                        <${SurfaceCard} sx=${{ p: 2.5 }}>
                          <${SectionTitle}
                            eyebrow="Simulação"
                            title="Trades sugeridos"
                            subtitle="Comparação entre a carteira carregada e o cenario do modelo."
                          />
                          ${importedTradeRows.length
                            ? html`
                                <${TableContainer}
                                  component=${Paper}
                                  elevation=${0}
                                  sx=${{
                                    borderRadius: 3,
                                    border: "1px solid rgba(255,255,255,0.08)",
                                    background: "rgba(255,255,255,0.03)",
                                  }}
                                >
                                  <${Table} stickyHeader size="small" sx=${{ minWidth: 760 }}>
                                    <${TableHead}>
                                      <${TableRow}>
                                        <${TableCell}>Ativo</${TableCell}>
                                        <${TableCell}>Tema</${TableCell}>
                                        <${TableCell}>Atual</${TableCell}>
                                        <${TableCell}>Alvo</${TableCell}>
                                        <${TableCell}>Gap</${TableCell}>
                                      </${TableRow}>
                                    </${TableHead}>
                                    <${TableBody}>
                                      ${importedTradeRows.slice(0, 18).map(
                                        (row) => html`
                                          <${TableRow} key=${row.asset}>
                                            <${TableCell}>
                                              <${Typography} sx=${{ fontWeight: 700 }}>${row.asset}</${Typography}>
                                              <${Typography} variant="caption" color="text.secondary">
                                                ${row.action}
                                              </${Typography}>
                                            </${TableCell}>
                                            <${TableCell}>${row.themeLabel}</${TableCell}>
                                            <${TableCell}>${formatMoney(row.currentValue)}</${TableCell}>
                                            <${TableCell}>${formatMoney(row.targetValue)}</${TableCell}>
                                            <${TableCell} sx=${{ color: row.trade >= 0 ? "#46d1be" : "#ff7a59", fontWeight: 700 }}>
                                              ${row.trade >= 0 ? "+" : ""}${formatMoney(row.trade)}
                                            </${TableCell}>
                                          </${TableRow}>
                                        `
                                      )}
                                    </${TableBody}>
                                  </${Table}>
                                </${TableContainer}>
                              `
                            : html`
                                <${Alert} severity="info" variant="outlined" sx=${{ bgcolor: "rgba(74,163,223,0.08)" }}>
                                  Adicione linhas ou carregue um CSV para ver a tabela de trades sugeridos.
                                </${Alert}>
                              `}
                        </${SurfaceCard}>
                      </${Stack}>
                    </${Grid}>
                  </${Grid}>
                </${SurfaceCard}>
              </${Stack}>
            </${TabPanel}>

            <${TabPanel} active=${currentTab} value="universe">
              <${Stack} spacing=${2.5}>
                <${Grid} container spacing=${2}>
                  <${Grid} item xs=${12} lg=${6}>
                    <${SurfaceCard} sx=${{ p: 2.5 }}>
                      <${SectionTitle}
                        eyebrow="Universo atual"
                        title="Posicoes atuais"
                        subtitle="A tabela separa o que esta no modelo do que ficou como residual."
                      />
                      <${TableContainer}
                        component=${Paper}
                        elevation=${0}
                        sx=${{
                          borderRadius: 3,
                          border: "1px solid rgba(255,255,255,0.08)",
                          background: "rgba(255,255,255,0.03)",
                        }}
                      >
                        <${Table} stickyHeader size="small" sx=${{ minWidth: 760 }}>
                          <${TableHead}>
                            <${TableRow}>
                              <${TableCell}>Ticker</${TableCell}>
                              <${TableCell}>Status</${TableCell}>
                              <${TableCell}>Atual</${TableCell}>
                              <${TableCell}>Alvo</${TableCell}>
                              <${TableCell}>Upside</${TableCell}>
                              <${TableCell}>Vies</${TableCell}>
                            </${TableRow}>
                          </${TableHead}>
                          <${TableBody}>
                            ${model.holdings.map(
                              (row) => html`<${HoldingRow} key=${row.symbol} row=${row} />`
                            )}
                          </${TableBody}>
                        </${Table}>
                      </${TableContainer}>
                    </${SurfaceCard}>
                  </${Grid}>

                  <${Grid} item xs=${12} lg=${6}>
                    <${SurfaceCard} sx=${{ p: 2.5 }}>
                      <${SectionTitle}
                        eyebrow="Watchlist"
                        title="Lista de monitoramento"
                        subtitle="Itens fora da carteira ou ainda em observacao dentro do estudo."
                      />
                      <${TableContainer}
                        component=${Paper}
                        elevation=${0}
                        sx=${{
                          borderRadius: 3,
                          border: "1px solid rgba(255,255,255,0.08)",
                          background: "rgba(255,255,255,0.03)",
                        }}
                      >
                        <${Table} stickyHeader size="small" sx=${{ minWidth: 760 }}>
                          <${TableHead}>
                            <${TableRow}>
                              <${TableCell}>Ticker</${TableCell}>
                              <${TableCell}>Bucket</${TableCell}>
                              <${TableCell}>Preco</${TableCell}>
                              <${TableCell}>Meta</${TableCell}>
                              <${TableCell}>Prioridade</${TableCell}>
                            </${TableRow}>
                          </${TableHead}>
                          <${TableBody}>
                            ${model.watchlist.map(
                              (row) => html`<${WatchlistRow} key=${row.symbol} row=${row} />`
                            )}
                          </${TableBody}>
                        </${Table}>
                      </${TableContainer}>
                    </${SurfaceCard}>
                  </${Grid}>
                </${Grid}>
              </${Stack}>
            </${TabPanel}>

            <${SurfaceCard} sx=${{ p: 2.5, mt: 2.5 }}>
              <${Stack} direction="row" alignItems="flex-start" spacing=${2}>
                <${Box} sx=${{ flex: 1 }}>
                  <${Typography}
                    variant="overline"
                    sx=${{
                      display: "block",
                      mb: 0.5,
                      color: "secondary.main",
                      letterSpacing: "0.16em",
                      fontWeight: 700,
                    }}
                  >
                    Aviso
                  </${Typography}>
                  <${Typography} variant="body2" color="text.secondary" sx=${{ lineHeight: 1.7 }}>
                    ${view === "public"
                      ? "Este snapshot publico foi sanitizado para compartilhamento. Os arquivos e tabelas sensiveis ficam ocultos."
                      : "O dashboard organiza um cenario-base interno derivado do estudo e do extrato IBKR. Os precos de mercado e FX sao convertidos para USD e atualizados a partir do snapshot local. Nao e recomendacao financeira personalizada."}
                  </${Typography}>
                </${Box}>
                <${Stack} direction="row" spacing=${1} flexWrap="wrap" sx=${{ justifyContent: "flex-end" }}>
                  ${summaryChips.slice(0, 3).map(
                    (item) => html`
                      <${Chip}
                        key=${item}
                        label=${item}
                        sx=${{
                          bgcolor: "rgba(255,255,255,0.04)",
                          border: "1px solid rgba(255,255,255,0.08)",
                          color: "text.secondary",
                        }}
                      />
                    `
                  )}
                </${Stack}>
              </${Stack}>
            </${SurfaceCard}>
          </${Container}>
        </${Box}>
      </${ThemeProvider}>
    `;
  }

  const theme = createTheme({
    palette: {
      mode: "dark",
      primary: { main: "#4aa3df", light: "#9dd4ff", dark: "#2c78b2" },
      secondary: { main: "#d08b2e", light: "#ffd38d", dark: "#9a6114" },
      background: {
        default: "#07111b",
        paper: "rgba(10,16,28,0.88)",
      },
      text: {
        primary: "#eff5ff",
        secondary: "#9ba8bb",
      },
      success: { main: "#46d1be" },
      warning: { main: "#d08b2e" },
      error: { main: "#ff7a59" },
      info: { main: "#7e8cff" },
    },
    shape: {
      borderRadius: 16,
    },
    typography: {
      fontFamily: '"IBM Plex Sans", "Segoe UI", sans-serif',
      h1: { fontFamily: '"Space Grotesk", "IBM Plex Sans", sans-serif' },
      h2: { fontFamily: '"Space Grotesk", "IBM Plex Sans", sans-serif' },
      h3: { fontFamily: '"Space Grotesk", "IBM Plex Sans", sans-serif' },
      h4: { fontFamily: '"Space Grotesk", "IBM Plex Sans", sans-serif' },
      h5: { fontFamily: '"Space Grotesk", "IBM Plex Sans", sans-serif' },
      h6: { fontFamily: '"Space Grotesk", "IBM Plex Sans", sans-serif' },
    },
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          body: {
            backgroundColor: "#07111b",
          },
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: "none",
            fontWeight: 700,
          },
        },
      },
      MuiChip: {
        styleOverrides: {
          root: {
            fontWeight: 700,
          },
        },
      },
      MuiTab: {
        styleOverrides: {
          root: {
            textTransform: "none",
            fontWeight: 700,
          },
        },
      },
      MuiTableCell: {
        styleOverrides: {
          head: {
            fontWeight: 700,
          },
        },
      },
    },
  });

  const root = ReactDOM.createRoot(document.getElementById("root"));
  root.render(html`<${App} />`);
})();
