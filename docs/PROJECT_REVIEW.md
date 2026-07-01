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

   Implementado em `generate_dashboard_data.py`. O proximo passo e adicionar testes que comparem o JS gerado com os CSVs.

2. Separar fontes sensiveis

   Os textos extraidos dos PDFs podem conter informacao privada. Para repositorio publico, considerar mover `extracted_text/` para armazenamento privado ou manter apenas um resumo sanitizado.

3. Converter moedas estrangeiras

   Alguns ativos estao em CAD, AUD e GBp. A versao atual mostra a moeda original; uma melhoria seria converter tudo para USD com FX de 2026-06-01.

4. Fortalecer precos indisponiveis

   FCU, LAAC, NGEX e PMET nao retornaram preco verificavel nos tickers testados. Manter uma tabela de aliases e eventos corporativos melhora cobertura.

5. Criar testes leves

   Adicionar validadores para:

   - Pesos alvo somarem 100%.
   - Cash alvo ficar acima de 5%.
   - Dashboard conter todos os ativos da proposta.
   - Dados do dashboard baterem com os CSVs.

6. Publicacao

   Para acesso mobile mais facil, publicar como GitHub Pages privado/publico conforme a sensibilidade dos dados. Para uso local, manter `py -m http.server`.

## Roadmap sugerido

- V1.1: teste automatizado de consistencia dos CSVs e dashboard.
- V1.2: conversao FX para todos os ativos nao USD.
- V1.3: versao sanitizada para GitHub Pages.
- V1.4: integracao com uma fonte de aliases/eventos corporativos.

## Cuidados antes de publicar

- Confirmar se o repositorio `FaberMach/SMP` sera publico ou privado.
- Revisar se o extrato IBKR e os textos extraidos podem ser versionados.
- Evitar commitar arquivos temporarios como `_tmp_cookie_copy/`, `upload_test/` e caches.
