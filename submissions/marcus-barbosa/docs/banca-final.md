# Banca final: revisão por agentes independentes

Definição de pronto do candidato (`docs/marcos.md`, bloco F): revisores independentes com a rubrica real do avaliador dão nota por bloco de entregável, e um revisor final diz se a entrega impressiona. A banca foi executada por agentes que não participaram da construção, com acesso ao repositório e instrução de pontuar como o avaliador do G4 pontua (`docs/rubrica-do-avaliador.md`). Por limite de consumo, a banca foi enxuta: dois revisores e um revisor final, todos com esforço médio.

## Rodada 1 (2026-09-21, antes das últimas correções)

| Revisor | Lente | Veredito | Nota /10 | A | B | C | D | E | F |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | avaliador do G4 (4 eixos, armadilhas das reviews públicas) | CHANGES_REQUESTED | 7,5 | 82 | 85 | 78 | 55 | 80 | 60 |
| 2 | Head de RevOps + engenheiro sênior | APPROVED | 8,3 | 78 | 84 | 88 | 70 | 75 | 60 |
| Final | independente, leu README, metodologia e as duas revisões | impressionado: sim | 82/100 | | | | | | |

Bloqueadores apontados e o que foi feito:

| Apontamento | Origem | Correção |
|---|---|---|
| README marcava chat export e banca final como entregues, e os arquivos não existiam | revisores 1 e 2, final | este documento e `process-log/chat-exports/` criados e versionados antes do PR; `05_check_repo.py` confere caminhos citados |
| `methodology.md` §6 dizia que a chance calibrada "acompanha" a observada, contra a tabela do backtest (desvios de até 24 pontos) | revisores 1 e 2, final | §6 reescrito com erro absoluto médio (10 pp), máximo (24 pp), sentido sistemático (superestima em 8 de 11 células) e as células das datas principais |
| Win rate por faixa de score é plano e não estava dito no README | revisor 2 | README e metodologia trazem as cinco faixas por data |
| Executive summary vendia "Lead Scorer" quando o backtest sustenta pauta por bloco de idade mais diagnóstico, com o score como desempate por valor | revisor 2, final | executive summary reposicionado |
| `scoring.py` imprimia "chance de fechar 0%" quando a faixa 121-138 estava sem suporte, e "100%" no modo fallback | revisor 2 | frase omitida quando não há painel para a faixa |
| Contagem de erros da IA: README dizia 7, o registro tem 8 | revisores 1 e 2 | README com os 8 |
| Célula da H10 quebrada em `hypotheses.md` | revisor 1 | corrigida |
| Hipóteses 100% de origem IA custam no eixo de uso de IA | revisores 1 e 2, final | mantido como está, por honestidade; o README explica a delegação e o controle adotado em vez de inventar hipóteses com data retroativa |
| Deploy público (A10) | revisores 1 e 2, final | não feito nesta versão; depende de conta do candidato no Streamlit Community Cloud |
| Inscrição no ATS (E7) | revisor 2 | ação do candidato, fora do repositório |

O revisor final, sobre o que impressiona: "a entrega diz contra si mesma antes que o avaliador precise dizer" (score empata com preço no top-N, régua de 138 dias é artefato da base, conta não pode ser fator por look-ahead, cada número com denominador e script). Sobre o que não impressiona: o nome "Lead Scorer" prometia mais do que o backtest sustenta, a frase de §6 e os dois artefatos ausentes.

## Rodada 2 (revisor final, após as correções)

Registrada abaixo quando executada.
