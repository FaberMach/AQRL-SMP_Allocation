# Revisao do Projeto SMP

## Estado atual

O projeto ja entrega o essencial:

- Extracao textual dos PDFs de origem.
- Analise de holdings IBKR.
- Atualizacao de precos de fechamento de 2026-06-01.
- Projecao de metas para dezembro de 2026.
- Proposta de rebalanceamento com cash acima de 5%.
- Dashboard local, responsivo, sem dependencias externas.

## Pontos fortes

- O dashboard e simples de servir e abrir em desktop ou celular.
- Os dados finais ficam em CSV, bons para auditoria e planilhas.
- A estrategia esta organizada por trade, tese e bloco de risco.
- O rebalanceamento e explicitamente limitado por pesos alvo que somam 100%.

## Melhorias recomendadas

1. Automatizar o snapshot do dashboard

   Implementado em `generate_dashboard_data.py`. A consistencia agora tambem e validada por `validate_project.py`.

2. Separar fontes sensiveis

   Executado para a publicacao: `extracted_text/` fica ignorado localmente e foi removido do fluxo de upload. A versao publicada em `docs/` usa apenas payload sanitizado.

3. Converter moedas estrangeiras

   Implementado em `market_data.py`; o pipeline persiste `analysis_outputs/fx_rates_2026-06-01.csv`.

4. Fortalecer precos indisponiveis

   FCU, LAAC, NGEX e PMET nao retornaram preco verificavel nos tickers testados. A lista inicial esta registrada em `analysis_outputs/ticker_aliases.csv`.

5. Criar testes leves

   Implementado em `validate_project.py` para:

   - Pesos alvo somarem 100%.
   - Cash alvo ficar acima de 5%.
   - Dashboard conter todos os ativos da proposta.
   - Dados do dashboard baterem com os CSVs.

6. Publicacao

   A versao interativa para GitHub Pages fica em `public_site/`, usando o payload publico/sanitizado de `dashboard/public`. A publicacao navegavel agora aponta para o repositorio `FaberMach/AQRL-SMP_Allocation`.

## Roadmap sugerido

- V1.1: resolver aliases de tickers sem preco verificavel.
- V1.2: habilitar Pages tornando o repo publico ou usando outro host.
- V1.3: integracao com uma fonte de aliases/eventos corporativos.
- V1.4: exportar relatorio PDF executivo.

## Cuidados antes de publicar

- Confirmar se o repositorio `FaberMach/AQRL-SMP_Allocation` sera publico ou privado.
- Revisar se o extrato IBKR e os textos extraidos podem ser versionados.
- Evitar commitar arquivos temporarios como `_tmp_cookie_copy/`, `upload_test/` e caches.
