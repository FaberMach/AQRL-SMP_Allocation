# Relatorio Executivo - Global Rebalance

- Data de precos: 2026-06-01
- Capital alvo: USD 256,024
- Valor atual estimado: USD 256,024
- Liquidez atual: USD 34,940 (13.7%)
- Liquidez alvo: 15.0%
- Cash alvo minimo: 5.0%; cash alvo do modelo: 8.0%
- Ativos modelados: 26; residuais: 4; watchlist: 34

## Tese central

O modelo reduz concentracoes excessivas, preserva liquidez explicita e direciona risco para temas globais com convexidade: defesa/espaco, uranio/nuclear, minerais criticos e nucleo de qualidade.

## Painel de risco

- Top 5 no cenario base: 31.0%
- Exposicao nao USD no cenario base: 2.0%
- Liquidez atual versus alvo: 13.7% -> 15.0%
- Residuais fora do modelo: 4
- Precificacoes com lacuna/erro no snapshot: 4
- Aliases acompanhados: 4; ainda sem confirmacao plena: 1

## Gatilhos de revisao

- Rebalancear se cash puro cair abaixo de 5% ou se cash + equivalentes cair abaixo de 12%.
- Revisar concentracao se o top 5 superar 35% do portfolio no cenario base.
- Travar novas compras em cauda especulativa se qualquer ticker residual sem tese passar de 1% do portfolio.
- Revalidar ticker, bolsa e liquidez antes de executar ativos marcados como alias_candidate ou unresolved_exchange_alias.

## Maiores movimentos

| Ativo | Tema | Atual | Alvo base | Trade base | Racional |
| --- | --- | ---: | ---: | ---: | --- |
| NVDA | Nucleo qualidade | USD 44,872 | USD 20,482 | USD -24,390 | Continuar exposto a lideranca em IA, porem com disciplina de tamanho. |
| IBM | Nucleo qualidade | USD 32,042 | USD 10,241 | USD -21,801 | Reduzir ativo defensivo de menor convexidade para liberar capital para teses do estudo. |
| JPM | Nucleo qualidade | USD 29,658 | USD 15,361 | USD -14,297 | Manter banco de qualidade, mas reduzir peso elevado e dependencia de financeiro tradicional. |
| ASTS | Defesa e espaco | USD 0 | USD 10,241 | USD 10,241 | Iniciar exposicao a infraestrutura celular via satelite, uma das maiores optionalidades. |
| NXE | Uranio e nuclear | USD 0 | USD 10,241 | USD 10,241 | Iniciar posicao em ativo tier-1 de uranio, destacado como qualidade geologica superior. |
| QBTS | Cauda especulativa | USD 14,590 | USD 5,120 | USD -9,470 | Reduzir quantum para tamanho de cesta, diminuindo risco de diluicao e volatilidade extrema. |
| XOVR | Liquidez | USD 2,058 | USD 10,241 | USD 8,183 | Aumentar equivalente defensivo para reduzir volatilidade sem sair de caixa. |
| RKLB | Defesa e espaco | USD 7,343 | USD 15,361 | USD 8,018 | Aumentar uma das top 5 do estudo, com execucao operacional real em espaco e defesa. |

## Ordem operacional sugerida

### Levantar liquidez / reduzir excesso

| Ativo | Trade base | Racional |
| --- | ---: | --- |
| NVDA | USD -24,390 | Continuar exposto a lideranca em IA, porem com disciplina de tamanho. |
| IBM | USD -21,801 | Reduzir ativo defensivo de menor convexidade para liberar capital para teses do estudo. |
| JPM | USD -14,297 | Manter banco de qualidade, mas reduzir peso elevado e dependencia de financeiro tradicional. |
| QBTS | USD -9,470 | Reduzir quantum para tamanho de cesta, diminuindo risco de diluicao e volatilidade extrema. |
| MSFT | USD -7,665 | Preservar posicao core em cloud/IA, mas reduzir concentracao para financiar convexidade. |
| NAUFF | USD -1,600 | Reduzir para posicao pequena, mantendo opcionalidade no ciclo nuclear sem concentrar risco. |

### Compras prioritarias

| Ativo | Trade base | Racional |
| --- | ---: | --- |
| ASTS | USD 10,241 | Iniciar exposicao a infraestrutura celular via satelite, uma das maiores optionalidades. |
| NXE | USD 10,241 | Iniciar posicao em ativo tier-1 de uranio, destacado como qualidade geologica superior. |
| RKLB | USD 8,018 | Aumentar uma das top 5 do estudo, com execucao operacional real em espaco e defesa. |
| URA | USD 7,747 | Aumentar bloco de uranio pelo ciclo nuclear e pela demanda de energia para IA. |
| SMR | USD 7,681 | Iniciar exposicao a SMRs, tese nuclear com opcionalidade estrategica. |
| KTOS | USD 6,432 | Aumentar exposicao a drones, sistemas autonomos e guerra eletronica. |

## Cenarios versionados

- `analysis_outputs/scenarios/study.json`
- `analysis_outputs/scenarios/defensive.json`
- `analysis_outputs/scenarios/convex.json`

## Controles e validacao

- `py run_pipeline.py` regenera dashboard, exports, cenarios e validacao.
- `py validate_project.py` confirma pesos em 100%, cash >= 5% e sincronizacao dashboard/CSVs.
- A versao em `docs/` e sanitizada para publicacao; os textos extraidos dos PDFs ficam fora do upload remoto.
