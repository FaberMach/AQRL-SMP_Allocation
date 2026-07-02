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

  function App() {
    const defaultScenario = resolveDefaultScenario(data);
    const stored = readStoredPrefs();
    const storedScenarioValid = safeArray(data.scenarios).some((scenario) => scenario.id === stored.scenarioId);
    const initialScenarioId = storedScenarioValid ? stored.scenarioId : defaultScenario;
    const defaultCapital = Number(data.meta?.targetCapital || data.meta?.currentPortfolioValue || 0);
    const initialCapital = Number.isFinite(Number(stored.capital)) && Number(stored.capital) > 0
      ? Number(stored.capital)
      : defaultCapital;
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
    });

    const scenario = resolveScenario(data, prefs.scenarioId);
    const model = React.useMemo(() => buildModel(data, scenario, prefs.capital), [scenario, prefs.capital]);
    const isDesktop = useMediaQuery(theme.breakpoints.up("md"));

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
      });
    }, [prefs]);

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
    } else if (safeArray(data.study?.topIdeas).length) {
      summaryChips.push(`${integerFormatter.format(topIdeas.length)} top ideas`);
    }

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
                          : "A interface combina componentes de React e Material UI para rodar o modelo do estudo, monitorar precos globais de acoes, controlar cenarios e revisar os trades com hierarquia visual mais clara."}
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
