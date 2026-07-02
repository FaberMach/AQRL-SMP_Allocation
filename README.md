# Global Portfolio Model Runner

Aplicacao local para rodar um modelo de gestao de carteiras globais com base no estudo anexado, no extrato IBKR e na watchlist setorial.

## O que a aplicacao faz

- Permite alternar entre cenarios de alocacao: `Base do estudo`, `Defensivo global` e `Convexidade`.
- Recalcula pesos, gaps e valores-alvo em tempo real a partir do capital informado.
- Inclui precos globais de acoes com conversao de moeda para USD, cobrindo ativos em USD, CAD, AUD e GBp/GBP.
- Mostra liquidez, concentracao, exposicao geografica e exposicao por moeda.
- Destaca posicoes residuais fora da cesta principal para nao mascarar risco.
- Exibe o blueprint institucional do estudo e as cinco teses mais convexas.

## Como abrir o dashboard

```powershell
py -m http.server 8000 -d dashboard
```

Depois abra:

- Desktop: <http://localhost:8000>
- Celular na mesma rede Wi-Fi: use o IP da maquina no formato `http://IP:8000`
- Versao publica sanitizada: abra `dashboard/public/index.html` no mesmo servidor ou diretamente no navegador.

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
- `validate_project.py`: valida pesos, cash minimo e sincronizacao dashboard/CSVs.
- `dashboard/`: app HTML/CSS/JS sem dependencias externas.
- `portfolio_rebalance_analysis.py`: gera os CSVs de precos, holdings, watchlist e proposta de rebalanceamento.

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

## Publicacao GitHub Pages

A pasta `docs/` contem uma versao interativa publica/sanitizada do dashboard, gerada a partir de `dashboard/public`.
Ela evita publicar o dashboard completo e os textos extraidos dos PDFs.

## Notas de modelo

- O capital base do snapshot atual e USD 256.021,53.
- A liquidez total do cenario base e 15% da carteira, com 8% em cash.
- O pricing snapshot usa a data de mercado configurada pelo script e converte moedas locais para USD antes de calcular o valor de carteira.
- Posicoes residuais fora do modelo aparecem separadas e continuam visiveis no dashboard.
- O material nao e recomendacao financeira personalizada.
