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

| Revisor | Veredito | Nota /100 | Impressionado |
|---|---|---:|---|
| Final, independente | APPROVED | 87 | sim |

Parecer, na íntegra: "Os dois bloqueadores da rodada 1 foram resolvidos de fato: o transcript (707 KB) e a síntese da auditoria existem no caminho citado, e o §6 da metodologia agora quantifica o erro da chance calibrada (média de 10 pp, sentido sistemático em 8 de 11 células, células das datas principais) em vez de dizer que 'acompanha'. O executive summary foi reposicionado para pauta por bloco de idade mais diagnóstico, com o score rebaixado a desempate por valor, e o README passou a declarar o win rate plano por faixa de score, os 8 erros da IA e a origem 100% IA das hipóteses sem maquiagem. As limitações (deploy ausente, look-ahead da coluna 'com conta', score empata com preço) estão no lugar certo e com o mesmo teor da metodologia. O que impressiona segue sendo a entrega dizer contra si mesma com número e denominador antes que o avaliador precise dizer. Sobrou uma contradição factual nova entre os dois textos: o README localiza o erro máximo de 24 pontos em 31/08 na faixa 15-90, e o §6 o localiza em 31/07 na faixa 0-14; um dos dois está errado e é exatamente o tipo de deslize que a rodada 1 penalizou. A seção 'Rodada 2' de banca-final.md está vazia e precisa receber este parecer antes do PR. Deploy público e inscrição no ATS continuam fora do repositório, como declarado. Aprovo com essas pendências, que são de acabamento e não de método."

Pendências apontadas e o que foi feito:

| Pendência | Correção |
|---|---|
| Contradição sobre o erro máximo (README dizia 31/08 faixa 15-90; a tabela de `backtest.md` mostra 31/07 faixa 0-14, 40% prevista contra 16% observada) | README corrigido; a metodologia já estava certa |
| Seção "Rodada 2" vazia | preenchida acima |
| Deploy público (A10) | não feito; declarado em Limitações |
| Inscrição no ATS (E7) | ação do candidato |

## Leitura do resultado contra a definição de pronto

A meta declarada era 100/100 por bloco. O resultado é 87/100 no revisor final após correções, com aprovação e "impressionado", e notas por bloco entre 55 e 88 na rodada 1 (as mais baixas, D e F, vinham dos artefatos que ainda não existiam e foram entregues depois). Fica registrado como está: a meta não foi atingida em número, e as pendências que restam (deploy público e hipóteses de domínio de origem humana) são declaradas, não escondidas.
