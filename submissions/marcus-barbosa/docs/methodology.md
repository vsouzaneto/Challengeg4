# Metodologia: do CSV bruto ao score

Cada número deste documento tem o script que o gerou. Rodar os scripts na ordem reproduz tudo: `01_audit.py`, `02_explore.py`, `03_backtest.py`, `app.py`. Datas e taxas abaixo são as do dataset (2016 a 2017); a data de referência do produto é 2017-12-31, o último fechamento observado.

## 1. Pergunta e regra do método

A Head de RevOps pediu uma ferramenta que diga ao vendedor onde focar. A regra que orientou tudo: nenhum fator entra no score sem que a hipótese que o sustenta tenha sobrevivido a um teste nos dados, e nenhum número é apresentado sem denominador. Os testes estão em `process-log/hypotheses.md` (27 hipóteses, 8 confirmadas) e o código em `solution/02_explore.py`.

## 2. Dados e auditoria (`01_audit.py` → `docs/data_health_report.md`)

Quatro CSVs do Kaggle, 8.800 oportunidades, 85 contas, 7 produtos, 35 vendedores. O que a auditoria encontrou e que muda o desenho:

| Fato | Número | Onde |
|---|---|---|
| Estágios | Won 4.238, Lost 2.473, Engaging 1.589, Prospecting 500 | `data_health_report.md`, seção Estágios |
| Deals abertos sem conta | 1.425 de 2.089 (68,2%); entre fechados, zero | seção Integridade das chaves |
| Nome de produto divergente | `GTXPro` no pipeline, `GTX Pro` no catálogo; normalizado em `leadscorer/data.py` (`PRODUCT_ALIASES`) | seção Integridade |
| Datas | engage_date de 2016-10-20 a 2017-12-27; close_date de 2017-03-01 a 2017-12-31; zero ciclos negativos | seção Datas |
| Idade dos Engaging em 2017-12-31 | mediana 165 dias; 1.558 de 1.589 acima do ciclo mediano dos fechados (45 dias) | seção Idade |
| Spread de win rate por dimensão | produto 4,8 pp, setor 3,7 pp, região 1,4 pp, gerente 2,3 pp, vendedor 15,4 pp | seção Win rate |

Duas bordas da base determinam toda a calibração (H21, H12c em `hypotheses.md`): não há fechamento antes de 2017-03-01 embora haja engajamentos desde outubro de 2016, então as derrotas rápidas de 2016 (metade dos Lost morre em até 14 dias) não existem na base; e nenhum deal, ganho ou perdido, tem ciclo acima de 138 dias.

## 3. O que separa ganho de perda (`02_explore.py` → `docs/exploration_results.md`)

Sobreviveu:

1. Quem morre, morre cedo. Ciclo mediano dos Lost é 14 dias, dos Won é 57 (Mann-Whitney p=10⁻²⁶, H8b). Entre deals que fecharam, P(ganhar | passou de 14 dias) sobe de 61% para 67% e fica estável até 120 dias (H10b, janela limpa, n=3.718).
2. Idade explica se o deal fecha. No painel de snapshots, deals com conta e até 90 dias fecham (ganho ou perda) em 83% a 90% dos casos nos 138 dias seguintes; entre 121 e 138 dias, em 14% (seção 4).
3. Valor concentrado: 417 de 2.089 deals abertos (20%) carregam 50% do valor de lista (H20). O valor fechado é 0,998 do preço de lista (H7), então o preço de lista é o ticket.
4. Estrutura do pipeline: 81% dos Engaging estão além de 138 dias (H11); 68% dos abertos não têm conta, em ambos os estágios (H17); toda a prospecção sem data está na região Central (`app.py`, visão RevOps).

Não sobreviveu (e por isso não entra no score):

| Fator | Teste | Resultado |
|---|---|---|
| Vendedor | χ² sobre 30 vendedores com n≥79 | p=0,26 (H1) |
| Vendedor × produto | gap entre quartis observado vs. nulo binomial com os mesmos n, 500 simulações | 8,7 pp observado, 9,9 pp no nulo, p=0,89 (H2b) |
| Produto | χ² | spread 4,8 pp, p=0,37 (H4) |
| Preço de lista como sinal de chance | Spearman | ρ=−0,01, p=0,41 (H5) |
| Setor, porte, subsidiária | χ² | p=0,97; 0,50; 0,74 (H15, H14, H16) |
| Desconto por vendedor | razão close_value/preço | mediana 0,998, spread 0,04 (H7) |
| Sazonalidade | χ² só na janela limpa | 11,8 pp, p=9×10⁻⁷ (H12c): existe variação mensal, mas não é atributo do deal e a versão sem janela limpa (44,6 pp) era artefato de truncamento |
| Conta recorrente | por trimestre, sem meses truncados | inconclusivo (H13b) |

## 4. Chance de ganhar em 90 dias (`leadscorer/calibration.py`)

A taxa Won/(Won+Lost) responde "dado que fechou, ganhou?", e ignora a fatia do pipeline que nunca fecha. A pergunta do vendedor é outra: "aberto hoje, fecha ganho nos próximos 90 dias?". Por isso a chance é calibrada por painel de snapshots:

1. Para cada fim de mês t de 2017-03-31 até (data de referência − 90 dias), reconstrói-se o pipeline em Engaging aberto em t (engajado até t, não fechado até t) e observa-se se fechou ganho até t + 90. Para 2017-12-31 são 7 datas, de março a setembro; 8.456 linhas deal × data com conta cadastrada.
2. Faixas de idade fixadas antes da calibração: 0-14 (janela em que metade das derrotas acontece), 15-90, 91-120, 121-138. Faixa com menos de 50 linhas é fundida com a anterior.
3. Só deals com conta cadastrada: nos dados, nenhum deal sem conta fechou (0 de 2.531 linhas), mas não é possível saber se a conta é preenchida no fechamento ou se deals sem conta não são trabalhados. A conta vira ação de higiene, não fator; a tabela abaixo também mostra a taxa incluindo deals sem conta, que é o limite pessimista.

| Faixa de idade | Chance em 90 d (com conta) | IC 95% (Wilson) | n (deal × data) | Incluindo deals sem conta |
|---|---:|---|---:|---:|
| 0-14 dias | 46,7% | 44,5% a 48,9% | 2.020 | 37,5% |
| 15-90 dias | 54,7% | 53,4% a 56,0% | 5.702 | 40,8% |
| 91-120 dias | 44,2% | 40,3% a 48,2% | 595 | 24,6% |
| 121-138 dias | 12,9% | 8,4% a 19,5% | 139 | 4,6% |

Nada posterior à data de referência entra: no backtest, a calibração em 2017-06-30 usa só o snapshot de março (teste `test_panel_uses_only_outcomes_inside_horizon`). Quando não há painel suficiente antes da data, o código cai para a taxa condicional a fechar e diz isso na interface (`Calibration.mode`).

## 5. Score e categorias (`leadscorer/scoring.py`)

- valor esperado = chance da faixa de idade × preço de lista;
- score 0-100 = percentil do valor esperado entre os deals acionáveis (Engaging até 138 dias). "Score 88" significa "vale mais que 88% do pipeline acionável";
- sem chance e sem score: Engaging além de 138 dias (nenhum deal fechou depois disso) e Prospecting (não há histórico de prospecção → engajamento);
- categorias: Confirmar se está vivo (além de 138 dias), Primeiras duas semanas (idade ≤ 14), Focar agora (score ≥ 70, top 30% do acionável, cerca de 3 por vendedor), Manter follow-up (resto), Qualificar ou descartar (Prospecting). Conta ausente é uma ação a mais, Cadastrar conta, não uma penalidade;
- ordem dentro do mesmo score: valor de lista, depois conta cadastrada, depois idade menor. Vendedor, produto e setor não participam (testes `test_agent_product_sector_do_not_change_score`, `test_deal_without_account_gets_score_and_flag`).

Em 2017-12-31: 2.089 deals abertos, 298 acionáveis, 86 em Focar agora, 7 nas primeiras duas semanas, 205 em follow-up, 1.291 em Confirmar se está vivo, 500 em Qualificar ou descartar. Pipeline nominal de US$ 4.966.215; 64,4% desse valor está além de 138 dias; o acionável vale US$ 693.565 de lista e US$ 271.568 esperados em 90 dias.

## 6. Backtest walk-forward (`03_backtest.py` → `docs/backtest.md`)

Quatro datas (30/06, 31/07, 31/08, 30/09 de 2017). Em cada uma, a chance é calibrada só com snapshots cujo horizonte terminou antes da data, o pipeline aberto é pontuado e observam-se os 90 dias seguintes.

O que o backtest sustenta:

- O bloco Confirmar se está vivo é exato: dos 149, 275, 408 e 530 deals além de 138 dias em cada data, nenhum fechou depois, nem ganho nem perdido.
- A chance calibrada com o passado acompanha a observada entre deals com conta (por exemplo, 0-14 dias em 30/06: prevista 53%, observada 49%), com erro maior nas faixas de 91 a 138 dias enquanto há poucos snapshots.
- Entre deals com conta, o win rate em 90 dias fica entre 34% e 56% por faixa de score, sem ordenação clara pelo score.

O que o backtest não sustenta, dito sem rodeio: na captura de valor ganho pelo top-N, o score empata com ordenar por preço de lista, no mesmo conjunto e no pipeline inteiro. A chance é quase plana entre 15 e 120 dias, então o valor esperado ordena como o preço. O que o método faz que ordenar por preço não faz: tira do topo o que a história diz que não fecha (64% do valor nominal), diz o que fazer com cada bloco, e não inventa chance onde não há histórico.

## 7. Testes (`solution/tests`, 21 testes)

Invariantes: score em [0,100] ou ausente só fora do suporte; determinismo; vendedor, produto e setor não mudam o score; conta não muda o score; `close_value` e `close_date` de deal aberto não mudam o score; valor esperado monotônico no score; o mesmo preço recebe scores diferentes conforme a idade; categorias seguem as regras; snapshots nunca cruzam a data de referência; painel só usa desfechos dentro do horizonte; calibração cai para o fallback e declara isso em base pequena; data de referência é a última do dataset, nunca hoje; junções preservam todas as linhas; alias de produto normalizado. A fixture dos testes é sintética e mínima (`tests/conftest.py`) e não é usada em nenhuma análise.

## 8. Reprodução

`99_clean_env_check.ps1` cria um venv novo, instala `requirements.txt` (versões fixas), roda testes, auditoria, exploração, backtest e um smoke test do app. Nenhuma chave de API é necessária. Os CSVs vêm do Kaggle (`download_data.py`, API ou zip manual); os hashes SHA-256 dos arquivos usados estão no início de `data_health_report.md` quando gerado pelo script de download.

## 9. Limites

- A base é sintética na origem (Maven Analytics) e tem bordas artificiais: teto de 138 dias e janela de fechamentos a partir de março de 2017. As taxas valem para esta base, não para o CRM real de ninguém.
- Não há registro de atividade (ligações, e-mails, reuniões), nem histórico de transições de estágio, nem a data em que a conta foi preenchida. Por isso a conta não pode ser fator e a prospecção não recebe chance.
- A chance com conta é um limite otimista e a chance incluindo deals sem conta é um limite pessimista; a verdade para um deal trabalhado está entre os dois.
- O score não bate ordenar por preço na captura de valor em 2017. Se o CRM real tiver atividade e transições, o mesmo painel de snapshots calibra fatores novos sem mudar a arquitetura.
- Um vendedor (Darcel Schlecht) tem 194 deals abertos e nenhum acionável; o método não resolve carteira sem histórico, só a expõe.
