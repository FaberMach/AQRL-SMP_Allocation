window.PORTFOLIO_PUBLIC_DATA = {
  "meta": {
    "priceDate": "2026-06-01",
    "targetCapital": 100000.0,
    "currentPortfolioValue": 100000.0,
    "modelPortfolioValue": 100000.0,
    "residualValue": 0.0,
    "cashCurrent": 0.0,
    "liquidityCurrentValue": 0.0,
    "cashTargetPct": 8.0,
    "cashMinimumPct": 5.0,
    "liquidityTargetPct": 15.0,
    "liquidityCurrentPct": 13.65,
    "residualCount": 0,
    "modelAssetCount": 26,
    "holdingsCount": 0,
    "watchlistCount": 5,
    "marketPriceCount": 53,
    "fxRateCount": 3,
    "notes": [
      "Versao publica normalizada: nao inclui valores reais, holdings, trades completos ou extratos.",
      "Mostra cenarios, temas, cobertura de precos e top ideias em escala-base de USD 100.000."
    ],
    "baseTopFiveShare": 31.0,
    "nonUsdShare": 2.0,
    "publicSanitized": true
  },
  "scenarios": [
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
        "tail": 1.0
      }
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
        "tail": 0.6
      }
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
        "tail": 1.35
      }
    }
  ],
  "themes": [
    {
      "id": "liquidity",
      "label": "Liquidez",
      "description": "Cash, XOVR e o bond ECOPET preservam a faixa de defesa do modelo.",
      "accent": "#d08b2e",
      "assets": [
        "Cash",
        "XOVR",
        "ECOPET_BOND"
      ],
      "assetCount": 3
    },
    {
      "id": "quality",
      "label": "Nucleo qualidade",
      "description": "MSFT, NVDA, AMZN, GOOGL, JPM e IBM financiam a carteira e reduzem ruído.",
      "accent": "#4aa3df",
      "assets": [
        "AMZN",
        "GOOGL",
        "MSFT",
        "NVDA",
        "IBM",
        "JPM"
      ],
      "assetCount": 6
    },
    {
      "id": "defense_space",
      "label": "Defesa e espaco",
      "description": "RKLB, ASTS, KTOS, SHLD e RTX capturam a tese geopolitica e orbital.",
      "accent": "#7e8cff",
      "assets": [
        "RTX",
        "KTOS",
        "SHLD",
        "RKLB",
        "ASTS"
      ],
      "assetCount": 5
    },
    {
      "id": "uranium",
      "label": "Uranio e nuclear",
      "description": "URA, NXE, SMR, UUUU e NAUFF refletem o ciclo de energia estrategica.",
      "accent": "#c86df0",
      "assets": [
        "URA",
        "NXE",
        "SMR",
        "UUUU",
        "NAUFF"
      ],
      "assetCount": 5
    },
    {
      "id": "minerals",
      "label": "Minerais criticos",
      "description": "COPX, ARR, MP e SGML conectam cobre, terras raras e lito ao superciclo.",
      "accent": "#2bc6a4",
      "assets": [
        "COPX",
        "ARR.AX",
        "MP",
        "SGML"
      ],
      "assetCount": 4
    },
    {
      "id": "tail",
      "label": "Cauda especulativa",
      "description": "QBTS, RGTI, LAES, HYMC e USGDF ficam como opcionalidade de cauda.",
      "accent": "#ff7a59",
      "assets": [
        "QBTS",
        "RGTI",
        "LAES",
        "HYMC",
        "USGDF"
      ],
      "assetCount": 5
    }
  ],
  "study": {
    "principles": [
      "Construa um basket, nao uma aposta unica.",
      "Aceite que varias teses falhem; poucos vencedores pagam a conta.",
      "Use ativos estrategicos com potencial de rerating estrutural.",
      "Preserve liquidez e respeite o piso de 5% em caixa.",
      "Dimensone optionalidade por tema, geografia e horizonte."
    ],
    "basketBlueprint": [
      {
        "label": "Rare earths",
        "weight": 20,
        "examples": [
          "ARR",
          "Ucore",
          "Aclara",
          "Energy Fuels"
        ]
      },
      {
        "label": "Uranium",
        "weight": 20,
        "examples": [
          "NXE",
          "DNN",
          "FCU",
          "DYL"
        ]
      },
      {
        "label": "Defense / space",
        "weight": 20,
        "examples": [
          "ASTS",
          "RKLB",
          "KTOS",
          "RCAT"
        ]
      },
      {
        "label": "AI biotech",
        "weight": 15,
        "examples": [
          "RXRX",
          "BEAM",
          "CRSP"
        ]
      },
      {
        "label": "Copper / lithium",
        "weight": 15,
        "examples": [
          "IVN",
          "SGML",
          "PMET",
          "LAAC"
        ]
      },
      {
        "label": "Nuclear",
        "weight": 10,
        "examples": [
          "SMR",
          "OKLO"
        ]
      }
    ],
    "topIdeas": [
      {
        "symbol": "ARR",
        "name": "American Rare Earths",
        "themeLabel": "Minerais criticos",
        "studyBucket": "rare_earths",
        "priority": "alta",
        "currency": "AUD",
        "currentPrice": 0.39,
        "currentPriceUsd": 0.28,
        "targetPrice": 0.57,
        "targetPriceUsd": 0.41,
        "upsidePct": 45.0,
        "thesis": "top 5; terras raras EUA, geopolítica, muito risco"
      },
      {
        "symbol": "ASTS",
        "name": "AST SpaceMobile",
        "themeLabel": "Defesa e espaco",
        "studyBucket": "defense_space",
        "priority": "alta",
        "currency": "USD",
        "currentPrice": 105.65,
        "currentPriceUsd": 105.65,
        "targetPrice": 147.91,
        "targetPriceUsd": 147.91,
        "upsidePct": 40.0,
        "thesis": "top 5; infraestrutura celular via satélite"
      },
      {
        "symbol": "NXE",
        "name": "NexGen Energy",
        "themeLabel": "Uranio e nuclear",
        "studyBucket": "uranium",
        "priority": "alta",
        "currency": "USD",
        "currentPrice": 11.4,
        "currentPriceUsd": 11.4,
        "targetPrice": 14.82,
        "targetPriceUsd": 14.82,
        "upsidePct": 30.0,
        "thesis": "top 5; ativo tier-1 em urânio"
      },
      {
        "symbol": "RKLB",
        "name": "Rocket Lab",
        "themeLabel": "Cauda especulativa",
        "studyBucket": "Espaço/defesa",
        "priority": "alta",
        "currency": "USD",
        "currentPrice": 122.39,
        "currentPriceUsd": 122.39,
        "targetPrice": 165.23,
        "targetPriceUsd": 165.23,
        "upsidePct": 35.0,
        "thesis": "top 5; execução operacional"
      },
      {
        "symbol": "SMR",
        "name": "NuScale Power",
        "themeLabel": "Cauda especulativa",
        "studyBucket": "Nuclear SMR",
        "priority": "alta",
        "currency": "USD",
        "currentPrice": 12.89,
        "currentPriceUsd": 12.89,
        "targetPrice": 16.76,
        "targetPriceUsd": 16.76,
        "upsidePct": 30.0,
        "thesis": "top 5; opcionalidade em SMRs"
      }
    ]
  },
  "marketPrices": [
    {
      "symbol": "ASTS",
      "yahoo": "ASTS",
      "currency": "USD",
      "currencyRaw": "USD",
      "closeLocal": 105.65,
      "closeUsd": 105.65,
      "fxToUsd": 1.0,
      "date": "2026-06-01",
      "error": "",
      "source": "yahoo",
      "status": "ok",
      "url": "https://query1.finance.yahoo.com/v8/finance/chart/ASTS?period1=1779062400&period2=1780531200&interval=1d&events=history"
    },
    {
      "symbol": "NXE",
      "yahoo": "NXE",
      "currency": "USD",
      "currencyRaw": "USD",
      "closeLocal": 11.4,
      "closeUsd": 11.4,
      "fxToUsd": 1.0,
      "date": "2026-06-01",
      "error": "",
      "source": "yahoo",
      "status": "ok",
      "url": "https://query1.finance.yahoo.com/v8/finance/chart/NXE?period1=1779062400&period2=1780531200&interval=1d&events=history"
    },
    {
      "symbol": "RKLB",
      "yahoo": "RKLB",
      "currency": "USD",
      "currencyRaw": "USD",
      "closeLocal": 122.39,
      "closeUsd": 122.39,
      "fxToUsd": 1.0,
      "date": "2026-06-01",
      "error": "",
      "source": "yahoo",
      "status": "ok",
      "url": "https://query1.finance.yahoo.com/v8/finance/chart/RKLB?period1=1779062400&period2=1780531200&interval=1d&events=history"
    },
    {
      "symbol": "SMR",
      "yahoo": "SMR",
      "currency": "USD",
      "currencyRaw": "USD",
      "closeLocal": 12.89,
      "closeUsd": 12.89,
      "fxToUsd": 1.0,
      "date": "2026-06-01",
      "error": "",
      "source": "yahoo",
      "status": "ok",
      "url": "https://query1.finance.yahoo.com/v8/finance/chart/SMR?period1=1779062400&period2=1780531200&interval=1d&events=history"
    }
  ],
  "moves": [],
  "holdings": [],
  "residuals": [],
  "watchlist": []
};
