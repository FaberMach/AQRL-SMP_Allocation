window.PORTFOLIO_PUBLIC_DATA = {
  "meta": {
    "priceDate": "2026-06-30",
    "targetCapital": 235552.91,
    "currentPortfolioValue": 235552.9,
    "modelPortfolioValue": 234403.47,
    "residualValue": 1149.43,
    "cashCurrent": 26854.02,
    "liquidityCurrentValue": 34993.22,
    "cashTargetPct": 8.0,
    "cashMinimumPct": 5.0,
    "liquidityTargetPct": 15.0,
    "liquidityCurrentPct": 14.86,
    "residualCount": 4,
    "modelAssetCount": 26,
    "holdingsCount": 21,
    "watchlistCount": 34,
    "marketPriceCount": 53,
    "fxRateCount": 3,
    "notes": [
      "O modelo usa o fechamento mais recente do snapshot em 2026-06-30 e converte tudo para USD.",
      "Cash, XOVR e bond ECOPET formam a faixa de liquidez/defesa.",
      "Posicoes residuais fora do modelo aparecem separadas para nao mascarar risco."
    ],
    "baseTopFiveShare": 31.0,
    "nonUsdShare": 2.0
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
        "currentPrice": 0.38,
        "currentPriceUsd": 0.26,
        "targetPrice": 0.54,
        "targetPriceUsd": 0.37,
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
        "currentPrice": 86.1,
        "currentPriceUsd": 86.1,
        "targetPrice": 120.54,
        "targetPriceUsd": 120.54,
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
        "currentPrice": 9.45,
        "currentPriceUsd": 9.45,
        "targetPrice": 12.28,
        "targetPriceUsd": 12.28,
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
        "currentPrice": 100.07,
        "currentPriceUsd": 100.07,
        "targetPrice": 135.09,
        "targetPriceUsd": 135.09,
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
        "currentPrice": 10.15,
        "currentPriceUsd": 10.15,
        "targetPrice": 13.19,
        "targetPriceUsd": 13.19,
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
      "closeLocal": 86.1,
      "closeUsd": 86.1,
      "fxToUsd": 1.0,
      "date": "2026-07-01",
      "error": "",
      "status": "ok",
      "url": "https://query1.finance.yahoo.com/v8/finance/chart/ASTS?period1=1781654400&period2=1783123200&interval=1d&events=history"
    },
    {
      "symbol": "NXE",
      "yahoo": "NXE",
      "currency": "USD",
      "currencyRaw": "USD",
      "closeLocal": 9.45,
      "closeUsd": 9.45,
      "fxToUsd": 1.0,
      "date": "2026-07-01",
      "error": "",
      "status": "ok",
      "url": "https://query1.finance.yahoo.com/v8/finance/chart/NXE?period1=1781654400&period2=1783123200&interval=1d&events=history"
    },
    {
      "symbol": "RKLB",
      "yahoo": "RKLB",
      "currency": "USD",
      "currencyRaw": "USD",
      "closeLocal": 100.07,
      "closeUsd": 100.07,
      "fxToUsd": 1.0,
      "date": "2026-07-01",
      "error": "",
      "status": "ok",
      "url": "https://query1.finance.yahoo.com/v8/finance/chart/RKLB?period1=1781654400&period2=1783123200&interval=1d&events=history"
    },
    {
      "symbol": "SMR",
      "yahoo": "SMR",
      "currency": "USD",
      "currencyRaw": "USD",
      "closeLocal": 10.15,
      "closeUsd": 10.15,
      "fxToUsd": 1.0,
      "date": "2026-07-01",
      "error": "",
      "status": "ok",
      "url": "https://query1.finance.yahoo.com/v8/finance/chart/SMR?period1=1781654400&period2=1783123200&interval=1d&events=history"
    }
  ]
};
