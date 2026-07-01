# SMP - Strategic Market Portfolio

Dashboard local e artefatos de analise para rebalanceamento de uma carteira IBKR com base em:

- Extrato IBKR de 2026-05-07.
- Fechamentos de mercado de 2026-06-01.
- Anexos de teses e watchlist setorial.
- Requisito de manter ao menos 5% em cash ou equivalentes.

## Como abrir o dashboard

```powershell
py -m http.server 8000 -d dashboard
```

Depois abra:

- Desktop: <http://localhost:8000>
- Celular na mesma rede Wi-Fi: <http://192.168.15.22:8000>

Se o IP da maquina mudar, rode:

```powershell
Get-NetIPAddress -AddressFamily IPv4
```

e use o IP da interface Wi-Fi no formato `http://IP:8000`.

## Conteudo principal

- `dashboard/`: app HTML/CSS/JS sem dependencias externas.
- `analysis_outputs/`: CSVs e relatorio final da analise.
- `portfolio_rebalance_analysis.py`: script que baixa precos, gera metas e cria os CSVs de saida.
- `extracted_text/`: texto extraido dos PDFs usados como fonte.
- `docs/PROJECT_REVIEW.md`: revisao do projeto e melhorias propostas.

## Metodologia resumida

O rebalanceamento usa o valor estimado de USD 256.021,52 e define pesos alvo que somam 100%.
A proposta mantem 8% em cash, 4% em XOVR e 3% no bond ECOPET, totalizando 15% em cash/equivalentes.

As metas para dezembro de 2026 sao um cenario-base interno, calculado a partir dos fechamentos de 2026-06-01 e de fatores por tese/risco. Isto nao e recomendacao financeira personalizada.

## Principais movimentos

- Reduzir concentracao: NVDA, IBM, JPM, QBTS, MSFT.
- Aumentar/iniciar: ASTS, NXE, XOVR, RKLB, URA, SMR, KTOS.
- Preservar liquidez: cash alvo de 8% e equivalentes defensivos de 15%.

## Regenerar os dados

```powershell
py portfolio_rebalance_analysis.py
```

Depois atualize o snapshot do dashboard, se necessario, em `dashboard/data.js`.

Ou gere o snapshot automaticamente a partir dos CSVs:

```powershell
py generate_dashboard_data.py
```
