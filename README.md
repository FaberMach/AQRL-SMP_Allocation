# Global Portfolio Model Runner

Aplicacao local para rodar um modelo de gestao de carteiras globais com base no estudo anexado, no extrato IBKR e na watchlist setorial.

## Links publicados

- Dashboard publico sanitizado: <https://fabermach.github.io/AQRL-SMP_Allocation/>
- Repositorio principal da ferramenta: <https://github.com/FaberMach/AQRL-SMP_Allocation>
- Ultima release publicada: <https://github.com/FaberMach/AQRL-SMP_Allocation/releases>

## O que a aplicacao faz

- Permite alternar entre cenarios de alocacao: `Base do estudo`, `Defensivo global` e `Convexidade`.
- Recalcula pesos, gaps e valores-alvo em tempo real a partir do capital informado.
- Aceita importacao de carteira via CSV ou entrada manual em tela e simula o cenario do modelo sobre essa carteira.
- Aceita leitura de HTML de relatório e converte o documento em seções, métricas e blocos editoriais vivos.
- Exibe leitura setorial da watchlist, com foco em stock picking por buckets e prioridade.
- Inclui um painel de risco com limites de liquidez, concentracao, FX e residuais.
- Inclui precos globais de acoes com conversao de moeda para USD, cobrindo ativos em USD, CAD, AUD e GBp/GBP.
- Inclui uma aba de TradingView com ticker tape, advanced chart e market overview para preços vivos.
- Mostra liquidez, concentracao, exposicao geografica e exposicao por moeda.
- Destaca posicoes residuais fora da cesta principal para nao mascarar risco.
- Exibe o blueprint institucional do estudo e as cinco teses mais convexas.
- Mantem `dashboard/`, `docs/` e `public_site/` como visoes/publicacoes do mesmo app, geradas pela mesma pipeline.

## Como abrir o dashboard

```powershell
py -m http.server 8000 -d dashboard
```

Depois abra:

- Desktop: <http://localhost:8000>
- Celular na mesma rede Wi-Fi: use o IP da maquina no formato `http://IP:8000`
- Versao publica online: <https://fabermach.github.io/AQRL-SMP_Allocation/>

No modo completo voce encontra as abas `Relatório`, `TradingView`, `Simulador`, `Setores` e `Risco` alem do fluxo atual de resumo, mercado, execucao, estudo e universo.

Se o IP da maquina mudar, rode:

```powershell
Get-NetIPAddress -AddressFamily IPv4
```

e use o IP da interface Wi-Fi.

## Fluxo de dados

- `analysis_outputs/`: CSVs gerados pela analise da carteira.
- `market_data.py`: funcoes de precos historicos e conversao FX.
- `generate_dashboard_data.py`: transforma os CSVs em `dashboard/data.js`.
- `dashboard/exports/`: CSVs de apoio com precos globais, FX e cenarios exportados.
- `dashboard/public/`: versao sanitizada do dashboard, sem holdings/residuais/watchlist.
- `prepare_public_site.py`: gera `public_site/` com payload publico normalizado, sem valores reais.
- `upload_public_site.py`: publica `public_site/` no repo `FaberMach/AQRL-SMP_Allocation`.
- `validate_project.py`: valida pesos, cash minimo e sincronizacao dashboard/CSVs.
- `generate_reports.py`: cria relatorio executivo e cenarios versionados em JSON.
- `dashboard/`: app HTML/CSS/JS sem dependencias externas.
- `portfolio_rebalance_analysis.py`: gera os CSVs de precos, holdings, watchlist e proposta de rebalanceamento.

## Base AQRL incorporada

A base completa do Autonomous Quant Research Lab agora vive dentro deste repositorio em `Autonomous-Quant-Research-Lab/`.

- `Autonomous-Quant-Research-Lab/aqrl/`: pacote Python com core, dados, features, portfolio, risco, research e dashboards.
- `Autonomous-Quant-Research-Lab/aqrl/dashboards/client_view.py`: client view local com backtest, regime e rebalance.
- `Autonomous-Quant-Research-Lab/tests/`: cobertura automatizada do pacote AQRL.
- `Autonomous-Quant-Research-Lab/scripts/start_client_view.ps1`: atalho para subir a visao local.

Para trabalhar nessa base:

```powershell
cd Autonomous-Quant-Research-Lab
poetry install
poetry run python -m aqrl.dashboards.client_view --open
poetry run pytest
```

## Regenerar os dados

Fluxo completo:

```powershell
py run_pipeline.py
```

Se voce quiser recalcular apenas o snapshot do dashboard:

```powershell
py -c "import generate_dashboard_data as g; g.main()"
```

Se quiser refazer tambem a analise de carteira:

```powershell
py portfolio_rebalance_analysis.py
py -c "import generate_dashboard_data as g; g.main()"
```

## Validar consistencia

```powershell
py validate_project.py
```

## Relatorio executivo

O pipeline gera:

- `docs/EXECUTIVE_REPORT.md`
- `docs/executive_report.html`
- `analysis_outputs/scenarios/*.json`

## Publicacao GitHub Pages

A pasta `docs/` contem a versao sanitizada usada dentro do repositorio principal.
A publicacao navegavel usa o repositorio `FaberMach/AQRL-SMP_Allocation`.

Fluxo publico:

```powershell
py prepare_public_site.py
$env:GH_TOKEN = gh auth token
$env:GITHUB_REPOSITORY = 'FaberMach/AQRL-SMP_Allocation'
py upload_public_site.py
Remove-Item Env:GH_TOKEN
Remove-Item Env:GITHUB_REPOSITORY
```

O payload publico e normalizado para USD 100.000 e remove holdings, residuals, watchlist completa, trades completos, extratos e valores reais da carteira.

## Notas de modelo

- O capital base do snapshot atual e USD 256.021,53.
- A liquidez total do cenario base e 15% da carteira, com 8% em cash.
- O pricing snapshot usa a data de mercado configurada pelo script e converte moedas locais para USD antes de calcular o valor de carteira.
- Posicoes residuais fora do modelo aparecem separadas e continuam visiveis no dashboard.
- O material nao e recomendacao financeira personalizada.
