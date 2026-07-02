# Portfolio IBKR - atualização e rebalanceamento

Data de preço: fechamento de 2026-07-01. Fonte de preços: Yahoo Finance Chart API, URLs registradas em `prices_2026-06-01.csv`.
Bond ECOPET 6.875% 04/29/2030: preço público conferido para ISIN US279158AN94; valor limpo usado 100,47.

## Carteira estimada

- Cash IBKR: USD 26,854.02.
- Valor estimado de ações convertido para USD em 2026-07-01: USD 202,670.68.
- Bond ECOPET 6.875% 04/29/2030: preço limpo usado 100,47; valor estimado USD 6,028.20.
- Valor total estimado usado no rebalanceamento: USD 235,552.90.
- Caixa alvo: 8,0%, acima do mínimo requerido de 5,0%.
- Observação: ativos em CAD, AUD, GBP e GBp foram convertidos para USD usando o câmbio do mesmo snapshot. As posições ICGB-ICGF constam no extrato com preço zero e foram tratadas como residuais sem valor econômico.

## Metodologia das metas para dez/2026

As metas são projeções internas de cenário-base até dezembro de 2026, calculadas como preço de fechamento de 2026-07-01 multiplicado por um fator por tese/risco. Onde não há cobertura confiável no endpoint público, o fator privilegia qualidade, convexidade, liquidez e aderência aos anexos. Não é recomendação financeira personalizada.

## Proposta resumida

- Preservar núcleo de qualidade: MSFT, NVDA, AMZN, GOOGL, JPM, IBM e RTX, mas reduzir concentração em NVDA/JPM/IBM.
- Aumentar aderência aos anexos: RKLB, ASTS, NXE, SMR, ARR, UUUU/URA, COPX e SGML.
- Reduzir cauda especulativa redundante: QBTS, RGTI, LAES, HYMC, USGDF e posições ilíquidas/residuais.
- Manter cash + equivalentes: 8% em cash, 4% em XOVR e 3% no bond ECOPET.

## Holdings IBKR

| Ticker | Preço 2026-06-01 | Moeda | Meta dez/26 | Upside % | Viés |
| --- | --- | --- | --- | --- | --- |
| ICG | 0.44 | CAD | 0.44 | 0.0 | manter apenas residual |
| AMZN | 241.70 | USD | 275.54 | 14.0 | manter/aumentar moderado |
| COPX | 75.29 | USD | 84.32 | 12.0 | manter |
| GOOGL | 361.21 | USD | 404.56 | 12.0 | manter |
| HYMC | 23.07 | USD | 20.76 | -10.0 | zerar ou residual |
| IBM | 286.25 | USD | 297.70 | 4.0 | reduzir |
| ICGB |  | USD |  | 0.0 | sem ação econômica |
| ICGC |  | USD |  | 0.0 | sem ação econômica |
| ICGD |  | USD |  | 0.0 | sem ação econômica |
| ICGE |  | USD |  | 0.0 | sem ação econômica |
| ICGF |  | USD |  | 0.0 | sem ação econômica |
| JPM | 334.07 | USD | 354.11 | 6.0 | reduzir |
| KTOS | 53.04 | USD | 62.59 | 18.0 | manter |
| LAES | 3.10 | USD | 3.87 | 25.0 | reduzir para cesta |
| MSFT | 384.28 | USD | 422.71 | 10.0 | manter |
| NAUFF | 1.49 | USD | 1.86 | 25.0 | manter pequeno |
| NTDOY | 10.75 | USD | 11.50 | 7.0 | reduzir |
| NVDA | 197.58 | USD | 217.34 | 10.0 | reduzir peso |
| QBTS | 23.50 | USD | 28.20 | 20.0 | reduzir |
| RGTI | 18.68 | USD | 22.42 | 20.0 | reduzir |
| RKLB | 100.07 | USD | 135.09 | 35.0 | aumentar |
| RTX | 191.78 | USD | 207.12 | 8.0 | manter |
| SHLD | 61.20 | USD | 68.54 | 12.0 | manter |
| URA | 43.18 | USD | 49.66 | 15.0 | manter |
| USGDF | 0.11 | USD | 0.11 | 0.0 | zerar se possível |
| XOVR | 21.11 | USD | 21.95 | 4.0 | manter como caixa equivalente |

## Sugestões dos anexos

| Ticker | Yahoo | Preço 2026-06-01 | Moeda | Meta dez/26 | Prioridade | Categoria |
| --- | --- | --- | --- | --- | --- | --- |
| ARR | ARR.AX | 0.38 | AUD | 0.54 | alta | Rare earths |
| ASTS | ASTS | 86.10 | USD | 120.54 | alta | Espaço |
| NXE | NXE | 9.45 | USD | 12.28 | alta | Urânio |
| RKLB | RKLB | 100.07 | USD | 135.09 | alta | Espaço/defesa |
| SMR | SMR | 10.15 | USD | 13.19 | alta | Nuclear SMR |
| MP | MP | 54.28 | USD | 65.14 | media | Rare earths |
| LYC | LYC.AX | 18.09 | AUD | 20.80 | media | Rare earths |
| Ucore | UURAF | 3.39 | USD | 4.58 | media | Rare earths |
| Aclara | ARA.TO | 4.12 | CAD | 5.36 | media | Rare earths |
| UUUU | UUUU | 14.22 | USD | 17.78 | media | Urânio/rare earths |
| DNN | DNN | 3.08 | USD | 3.85 | media | Urânio |
| GLO | GLO.TO | 0.62 | CAD | 0.81 | baixa | Urânio |
| DYL | DYL.AX | 1.45 | AUD | 1.74 | media | Urânio |
| FCU | FCU.TO |  | USD |  | media | Urânio |
| IVN | IVN.TO | 11.11 | CAD | 13.11 | media | Cobre |
| SLS | SLS.TO | 11.93 | CAD | 14.91 | baixa | Cobre |
| ASCU | ASCU.TO | 8.06 | CAD | 9.67 | baixa | Cobre |
| NGEX | NGEX.V |  | USD |  | baixa | Cobre |
| SGML | SGML | 12.41 | USD | 15.51 | media | Lítio |
| PMET | PMET.V |  | USD |  | baixa | Lítio |
| ALL | ALL.L | 0.16 | GBP | 0.19 | baixa | Lítio |
| LAAC | LAAC |  | USD |  | baixa | Lítio |
| KTOS | KTOS | 53.04 | USD | 62.59 | media | Defesa |
| PLTR | PLTR | 125.73 | USD | 140.82 | media | IA/defesa |
| RCAT | RCAT | 10.55 | USD | 14.24 | baixa | Defesa drones |
| BKSY | BKSY | 28.74 | USD | 35.92 | baixa | Espaço |
| PL | PL | 31.61 | USD | 38.56 | baixa | Espaço/dados |
| RXRX | RXRX | 3.67 | USD | 4.59 | baixa | AI biotech |
| BEAM | BEAM | 33.48 | USD | 41.85 | baixa | Biotech |
| CRSP | CRSP | 55.62 | USD | 66.74 | baixa | Biotech |
| OKLO | OKLO | 52.45 | USD | 65.56 | media | Nuclear |
| CDZI | CDZI | 4.08 | USD | 4.69 | baixa | Água |
| NTR | NTR | 63.57 | USD | 68.66 | media | Agricultura |
| MOS | MOS | 21.30 | USD | 23.00 | media | Agricultura |

## Rebalanceamento proposto

| Ativo | Peso alvo % | Valor alvo USD | Valor atual USD | Compra/Venda USD |
| --- | --- | --- | --- | --- |
| NVDA | 8.0 | 18,844.23 | 39,516.00 | -20,671.77 |
| JPM | 6.0 | 14,133.17 | 33,407.00 | -19,273.83 |
| IBM | 4.0 | 9,422.12 | 28,625.00 | -19,202.88 |
| ASTS | 4.0 | 9,422.12 | 0.00 | 9,422.12 |
| NXE | 4.0 | 9,422.12 | 0.00 | 9,422.12 |
| RKLB | 6.0 | 14,133.17 | 6,004.20 | 8,128.97 |
| Cash | 8.0 | 18,844.23 | 26,854.02 | -8,009.79 |
| URA | 5.0 | 11,777.64 | 4,318.00 | 7,459.64 |
| XOVR | 4.0 | 9,422.12 | 2,111.00 | 7,311.12 |
| SMR | 3.0 | 7,066.59 | 0.00 | 7,066.59 |
| QBTS | 2.0 | 4,711.06 | 11,750.00 | -7,038.94 |
| KTOS | 4.0 | 9,422.12 | 3,182.40 | 6,239.72 |
| MSFT | 6.0 | 14,133.17 | 19,214.00 | -5,080.83 |
| ARR.AX | 2.0 | 4,711.06 | 0.00 | 4,711.06 |
| MP | 2.0 | 4,711.06 | 0.00 | 4,711.06 |
| UUUU | 2.0 | 4,711.06 | 0.00 | 4,711.06 |
| SGML | 2.0 | 4,711.06 | 0.00 | 4,711.06 |
| GOOGL | 5.0 | 11,777.64 | 9,030.25 | 2,747.40 |
| COPX | 4.0 | 9,422.12 | 7,529.00 | 1,893.12 |
| RTX | 3.0 | 7,066.59 | 5,753.40 | 1,313.19 |
| ECOPET_BOND | 3.0 | 7,066.59 | 6,028.20 | 1,038.39 |
| NAUFF | 1.0 | 2,355.53 | 2,980.00 | -624.47 |
| LAES | 1.5 | 3,533.29 | 3,100.00 | 433.29 |
| AMZN | 5.0 | 11,777.64 | 12,085.00 | -307.36 |
| SHLD | 4.0 | 9,422.12 | 9,180.00 | 242.12 |
| RGTI | 1.5 | 3,533.29 | 3,736.00 | -202.71 |

## Pendências de preço

Fission Uranium, Lithium Argentina, NGEx Minerals e Patriot Battery Metals não retornaram fechamento verificável para 2026-06-01 nos símbolos testados no Yahoo Finance. Foram mantidos no CSV com erro de preço quando aplicável; a proposta não depende deles.

## Arquivos gerados

- `prices_2026-06-01.csv`: preços baixados, câmbio e URLs de fonte.
- `ibkr_holdings_analysis.csv`: holdings atuais, preço local e USD, meta e viés de ação.
- `watchlist_analysis.csv`: sugestões dos anexos, preço local e USD, meta e prioridade.
- `rebalance_proposal.csv`: pesos alvo e compra/venda estimada em USD.