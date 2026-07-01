# Portfolio IBKR - atualização e rebalanceamento

Data de preço: fechamento de 2026-06-01. Fonte de preços: Yahoo Finance Chart API, URLs registradas em `prices_2026-06-01.csv`.
Bond ECOPET 6.875% 04/29/2030: preço público conferido para ISIN US279158AN94; valor limpo usado 100,47.

## Carteira estimada

- Cash IBKR: USD 26,854.02.
- Valor estimado de ações USD em 2026-06-01: USD 223,139.30.
- Bond ECOPET 6.875% 04/29/2030: preço limpo usado 100,47; valor estimado USD 6,028.20.
- Valor total estimado usado no rebalanceamento: USD 256,021.52.
- Caixa alvo: 8,0%, acima do mínimo requerido de 5,0%.
- Observação: ativos em CAD, AUD e GBp aparecem com preço na moeda original; não foram convertidos para USD no cálculo da carteira, exceto posições USD. As posições ICGB-ICGF constam no extrato com preço zero e foram tratadas como residuais sem valor econômico.

## Metodologia das metas para dez/2026

As metas são projeções internas de cenário-base até dezembro de 2026, calculadas como preço de fechamento de 2026-06-01 multiplicado por um fator por tese/risco. Onde não há cobertura confiável no endpoint público, o fator privilegia qualidade, convexidade, liquidez e aderência aos anexos. Não é recomendação financeira personalizada.

## Proposta resumida

- Preservar núcleo de qualidade: MSFT, NVDA, AMZN, GOOGL, JPM, IBM e RTX, mas reduzir concentração em NVDA/JPM/IBM.
- Aumentar aderência aos anexos: RKLB, ASTS, NXE, SMR, ARR, UUUU/URA, COPX e SGML.
- Reduzir cauda especulativa redundante: QBTS, RGTI, LAES, HYMC, USGDF e posições ilíquidas/residuais.
- Manter cash + equivalentes: 8% em cash, 4% em XOVR e 3% no bond ECOPET.

## Holdings IBKR

| Ticker | Preço 2026-06-01 | Moeda | Meta dez/26 | Upside % | Viés |
| --- | --- | --- | --- | --- | --- |
| ICG | 0.46 | CAD | 0.46 | 0.0 | manter apenas residual |
| AMZN | 261.26 | USD | 297.84 | 14.0 | manter/aumentar moderado |
| COPX | 90.06 | USD | 100.87 | 12.0 | manter |
| GOOGL | 376.37 | USD | 421.53 | 12.0 | manter |
| HYMC | 32.84 | USD | 29.56 | -10.0 | zerar ou residual |
| IBM | 320.42 | USD | 333.24 | 4.0 | reduzir |
| ICGB |  |  |  | 0.0 | sem ação econômica |
| ICGC |  |  |  | 0.0 | sem ação econômica |
| ICGD |  |  |  | 0.0 | sem ação econômica |
| ICGE |  |  |  | 0.0 | sem ação econômica |
| ICGF |  |  |  | 0.0 | sem ação econômica |
| JPM | 296.58 | USD | 314.37 | 6.0 | reduzir |
| KTOS | 63.49 | USD | 74.92 | 18.0 | manter |
| LAES | 3.55 | USD | 4.44 | 25.0 | reduzir para cesta |
| MSFT | 460.52 | USD | 506.57 | 10.0 | manter |
| NAUFF | 2.08 | USD | 2.60 | 25.0 | manter pequeno |
| NTDOY | 11.25 | USD | 12.04 | 7.0 | reduzir |
| NVDA | 224.36 | USD | 246.80 | 10.0 | reduzir peso |
| QBTS | 29.18 | USD | 35.02 | 20.0 | reduzir |
| RGTI | 25.63 | USD | 30.76 | 20.0 | reduzir |
| RKLB | 122.39 | USD | 165.23 | 35.0 | aumentar |
| RTX | 174.41 | USD | 188.36 | 8.0 | manter |
| SHLD | 65.62 | USD | 73.49 | 12.0 | manter |
| URA | 50.54 | USD | 58.12 | 15.0 | manter |
| USGDF | 0.12 | USD | 0.12 | 0.0 | zerar se possível |
| XOVR | 20.58 | USD | 21.40 | 4.0 | manter como caixa equivalente |

## Sugestões dos anexos

| Ticker | Yahoo | Preço 2026-06-01 | Moeda | Meta dez/26 | Prioridade | Categoria |
| --- | --- | --- | --- | --- | --- | --- |
| ARR | ARR.AX | 0.39 | AUD | 0.57 | alta | Rare earths |
| ASTS | ASTS | 105.65 | USD | 147.91 | alta | Espaço |
| NXE | NXE | 11.40 | USD | 14.82 | alta | Urânio |
| RKLB | RKLB | 122.39 | USD | 165.23 | alta | Espaço/defesa |
| SMR | SMR | 12.89 | USD | 16.76 | alta | Nuclear SMR |
| MP | MP | 69.29 | USD | 83.15 | media | Rare earths |
| LYC | LYC.AX | 18.67 | AUD | 21.47 | media | Rare earths |
| Ucore | UURAF | 4.09 | USD | 5.52 | media | Rare earths |
| Aclara | ARA.TO | 4.45 | CAD | 5.78 | media | Rare earths |
| UUUU | UUUU | 17.62 | USD | 22.03 | media | Urânio/rare earths |
| DNN | DNN | 3.43 | USD | 4.29 | media | Urânio |
| GLO | GLO.TO | 0.74 | CAD | 0.96 | baixa | Urânio |
| DYL | DYL.AX | 1.60 | AUD | 1.91 | media | Urânio |
| FCU | FCU.TO |  |  |  | media | Urânio |
| IVN | IVN.TO | 12.76 | CAD | 15.06 | media | Cobre |
| SLS | SLS.TO | 14.75 | CAD | 18.44 | baixa | Cobre |
| ASCU | ASCU.TO | 10.26 | CAD | 12.31 | baixa | Cobre |
| NGEX | NGEX.V |  |  |  | baixa | Cobre |
| SGML | SGML | 16.36 | USD | 20.45 | media | Lítio |
| PMET | PMET.V |  |  |  | baixa | Lítio |
| ALL | ALL.L | 16.65 | GBp | 19.98 | baixa | Lítio |
| LAAC | LAAC |  |  |  | baixa | Lítio |
| KTOS | KTOS | 63.49 | USD | 74.92 | media | Defesa |
| PLTR | PLTR | 160.65 | USD | 179.93 | media | IA/defesa |
| RCAT | RCAT | 14.84 | USD | 20.03 | baixa | Defesa drones |
| BKSY | BKSY | 42.38 | USD | 52.98 | baixa | Espaço |
| PL | PL | 46.46 | USD | 56.68 | baixa | Espaço/dados |
| RXRX | RXRX | 3.79 | USD | 4.74 | baixa | AI biotech |
| BEAM | BEAM | 31.14 | USD | 38.92 | baixa | Biotech |
| CRSP | CRSP | 54.19 | USD | 65.03 | baixa | Biotech |
| OKLO | OKLO | 66.89 | USD | 83.61 | media | Nuclear |
| CDZI | CDZI | 4.70 | USD | 5.40 | baixa | Água |
| NTR | NTR | 69.57 | USD | 75.14 | media | Agricultura |
| MOS | MOS | 23.33 | USD | 25.20 | media | Agricultura |

## Rebalanceamento proposto

| Ativo | Peso alvo % | Valor alvo USD | Valor atual USD | Compra/Venda USD |
| --- | --- | --- | --- | --- |
| NVDA | 8.0 | 20,481.72 | 44,872.00 | -24,390.28 |
| IBM | 4.0 | 10,240.86 | 32,042.00 | -21,801.14 |
| JPM | 6.0 | 15,361.29 | 29,658.00 | -14,296.71 |
| ASTS | 4.0 | 10,240.86 | 0.00 | 10,240.86 |
| NXE | 4.0 | 10,240.86 | 0.00 | 10,240.86 |
| QBTS | 2.0 | 5,120.43 | 14,590.00 | -9,469.57 |
| XOVR | 4.0 | 10,240.86 | 2,058.00 | 8,182.86 |
| RKLB | 6.0 | 15,361.29 | 7,343.40 | 8,017.89 |
| URA | 5.0 | 12,801.08 | 5,054.00 | 7,747.08 |
| SMR | 3.0 | 7,680.65 | 0.00 | 7,680.65 |
| MSFT | 6.0 | 15,361.29 | 23,026.00 | -7,664.71 |
| KTOS | 4.0 | 10,240.86 | 3,809.40 | 6,431.46 |
| Cash | 8.0 | 20,481.72 | 26,854.02 | -6,372.30 |
| ARR.AX | 2.0 | 5,120.43 | 0.00 | 5,120.43 |
| MP | 2.0 | 5,120.43 | 0.00 | 5,120.43 |
| UUUU | 2.0 | 5,120.43 | 0.00 | 5,120.43 |
| SGML | 2.0 | 5,120.43 | 0.00 | 5,120.43 |
| GOOGL | 5.0 | 12,801.08 | 9,409.25 | 3,391.83 |
| RTX | 3.0 | 7,680.65 | 5,232.30 | 2,448.35 |
| ECOPET_BOND | 3.0 | 7,680.65 | 6,028.20 | 1,652.45 |
| NAUFF | 1.0 | 2,560.22 | 4,160.00 | -1,599.78 |
| RGTI | 1.5 | 3,840.32 | 5,126.00 | -1,285.68 |
| COPX | 4.0 | 10,240.86 | 9,006.00 | 1,234.86 |
| SHLD | 4.0 | 10,240.86 | 9,843.00 | 397.86 |
| LAES | 1.5 | 3,840.32 | 3,550.00 | 290.32 |
| AMZN | 5.0 | 12,801.08 | 13,063.00 | -261.92 |

## Pendências de preço

Fission Uranium, Lithium Argentina, NGEx Minerals e Patriot Battery Metals não retornaram fechamento verificável para 2026-06-01 nos símbolos testados no Yahoo Finance. Foram mantidos no CSV com erro de preço quando aplicável; a proposta não depende deles.

## Arquivos gerados

- `prices_2026-06-01.csv`: preços baixados e URLs de fonte.
- `ibkr_holdings_analysis.csv`: holdings atuais, preço, meta e viés de ação.
- `watchlist_analysis.csv`: sugestões dos anexos, preço, meta e prioridade.
- `rebalance_proposal.csv`: pesos alvo e compra/venda estimada em USD.