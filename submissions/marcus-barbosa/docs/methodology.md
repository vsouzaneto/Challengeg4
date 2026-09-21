# Metodologia: do CSV bruto ao score

Cada número deste documento tem o script que o gerou. Rodar os scripts na ordem reproduz tudo: `01_audit.py`, `02_explore.py`, `03_backtest.py`, `app.py`. Os números abaixo foram lidos dos arquivos gerados em `docs/` (`data_health_metrics.json`, `exploration_results.json`, `backtest.json`) na versão final do código. A data de referência do produto é 2017-12-31, o último fechamento observado.

## 1. Pergunta e regra do método

A Head de RevOps pediu uma ferramenta que diga ao vendedor onde focar. A regra que orientou tudo: nenhum fator entra no score sem que a hipótese que o sustenta tenha sobrevivido a um teste nos dados, e nenhum número é apresentado sem denominador. Foram 27 hipóteses (`process-log/hypotheses.md`, código em `solution/02_explore.py`): 14 confirmadas pelo veredito automático, das quais duas (H2, H12) foram derrubadas pelos testes de robustez seguintes (H2b, H12c). Entram no score só as que sobreviveram e são atributo do deal: idade (H8b, H10b, H11) e valor (H7, H20). A conta entra como ação (H17) e a carga por vendedor entra na visão do gerente (H3).

## 2. Dados e auditoria (`01_audit.py` → `docs/data_health_report.md`)

Quatro CSVs do Kaggle, 8.800 oportunidades, 85 contas, 7 produtos, 35 vendedores; o SHA-256 de cada arquivo está no início do relatório. O que a auditoria encontrou e que muda o desenho:

| Fato | Número | Onde |
|---|---|---|
| Estágios | Won 4.238, Lost 2.473, Engaging 1.589, Prospecting 500 | seção Estágios |
| Deals abertos sem conta | 1.425 de 2.089 (68,2%); entre fechados, zero | seção Integridade das chaves |
| Nome de produto divergente | `GTXPro` no pipeline, `GTX Pro` no catálogo; normalizado em `leadscorer/data.py` | seção Integridade |
| Datas | engage_date de 2016-10-20 a 2017-12-27; close_date de 2017-03-01 a 2017-12-31; zero ciclos negativos | seção Datas |
| Idade dos Engaging em 2017-12-31 | mediana 165 dias; 1.558 de 1.589 acima do ciclo mediano dos fechados (45 dias) | seção Idade |
| Spread de win rate por dimensão | produto 4,8 pp, setor 3,7 pp, região 1,4 pp, gerente 2,3 pp, vendedor 15,4 pp | seção Win rate |

Duas bordas da base determinam a calibração (H21, H12c): não há fechamento antes de 2017-03-01 embora haja engajamentos desde outubro de 2016, então as derrotas rápidas de 2016 (metade dos Lost morre em até 14 dias) não existem na base; e nenhum ciclo concluído, ganho ou perdido, passa de 138 dias.

## 3. O que separa ganho de perda (`02_explore.py` → `docs/exploration_results.md`)

Sobreviveu:

1. Quem morre, morre cedo. Ciclo mediano dos Lost é 14 dias, dos Won é 57 (Mann-Whitney p=10⁻²⁶, H8b). Entre deals que fecharam, P(ganhar | passou de 14 dias) sobe de 61% para 67% (H10b, janela limpa, n=3.718); esse número condiciona a fechar e por isso não é a chance mostrada ao vendedor (seção 4).
2. A idade explica se o deal fecha. No painel de snapshots, deals abertos com até 90 dias fecham (ganho ou perda) em 59% a 61% dos 90 dias seguintes; entre 91 e 120 dias, em 26%; entre 121 e 138, em 2% (tabela da seção 4, coluna "fecha").
3. Valor concentrado: 417 de 2.089 deals abertos (20%) carregam 50% do valor de lista (H20). O valor fechado é 0,998 do preço de lista (H7), então o preço de lista é o ticket.
4. Estrutura do pipeline: 81% dos Engaging estão além de 138 dias (H11); 68% dos abertos não têm conta, em ambos os estágios (H17); toda a prospecção sem data está na região Central (`app.py`, visão RevOps, tabela por região).

Não sobreviveu, e por isso não entra no score:

| Fator | Teste | Resultado |
|---|---|---|
| Vendedor | χ² sobre 30 vendedores com n≥79 | p=0,26 (H1) |
| Vendedor × produto | gap entre quartis observado vs. Monte Carlo sob nulo binomial com os mesmos n, 500 simulações | 8,7 pp observado, 9,9 pp no nulo, p=0,89 (H2b) |
| Produto como taxa | χ² | spread 4,8 pp, p=0,37 (H4). O produto pesa só pelo preço |
| Preço como sinal de chance | Spearman | ρ=−0,01, p=0,41 (H5) |
| Setor, porte, subsidiária | χ² | p=0,97; 0,50; 0,74 (H15, H14, H16) |
| Desconto por vendedor | razão close_value/preço | mediana 0,998, spread 0,04 (H7) |
| Sazonalidade | χ² só na janela limpa | 11,8 pp, p=9×10⁻⁷ (H12c): existe variação mensal, mas não é atributo do deal, e a versão sem janela limpa (44,6 pp, H12) era artefato do truncamento |
| Conta recorrente | por trimestre, sem meses truncados | inconclusivo (H13b) |

## 4. Chance de ganhar em 90 dias (`leadscorer/calibration.py`)

A taxa Won/(Won+Lost) responde "dado que fechou, ganhou?" e ignora a fatia do pipeline que nunca fecha. A pergunta do vendedor é "aberto hoje, fecha ganho nos próximos 90 dias?". Por isso a chance é calibrada por painel de snapshots:

1. Para cada fim de mês t de 2017-03-31 até (data de referência − 90 dias), reconstrói-se o pipeline em Engaging aberto em t (engajado entre 2017-03-01 e t, não fechado até t) e observa-se se fechou ganho até t + 90. Para 2017-12-31 são 7 datas, de março a setembro: 4.375 deals únicos em 10.042 observações deal × data.
2. Faixas de idade fixadas antes da calibração: 0-14, 15-90, 91-120, 121-138. Faixa com menos de 30 deals únicos é agrupada com as faixas mais velhas (P(ganhar | idade ≥ limite)), nunca com a mais jovem; se nem assim houver amostra, a faixa fica sem chance na data e o deal não recebe score (`SUPPORT_THIN`).
3. Todos os deals abertos em t entram. A conta não filtra a calibração: o campo só é conhecido no estado final da base e todo deal fechado tem conta, então filtrar por ele seria olhar o futuro. A coluna "com conta hoje" é mostrada como limite otimista, rotulada assim.
4. O mesmo deal aparece em vários snapshots; o intervalo de confiança é por bootstrap de deals (200 reamostras), não de linhas.

| Faixa de idade | Chance de ganhar em 90 d | Intervalo 95% | Fecha (ganho ou perda) | Deals únicos | Observações | Com conta hoje (otimista) |
|---|---:|---|---:|---:|---:|---:|
| 0-14 dias | 37,5% | 35,5% a 39,2% | 61,2% | 2.514 | 2.514 | 46,7% |
| 15-90 dias | 39,8% | 38,1% a 41,3% | 59,2% | 3.446 | 6.609 | 54,4% |
| 91-120 dias | 18,3% | 15,2% a 20,8% | 26,1% | 677 | 677 | 37,2% |
| 121-138 dias | 1,2% | 0,0% a 2,5% | 1,7% | 242 | 242 | 3,9% |

Nada posterior à data de referência entra: `test_calibration_and_score_do_not_see_the_future` trunca a base na data (fechamentos futuros viram abertos, engajamentos futuros somem) e exige calibração e scores idênticos; `test_panel_respects_window_start_and_horizon` exige que deals engajados antes de 2017-03-01 e ganhos fora do horizonte fiquem fora. Quando não há painel suficiente antes da data, o código cai para a taxa condicional a fechar e diz isso na interface (`Calibration.mode`).

## 5. Score e categorias (`leadscorer/scoring.py`)

- valor esperado = chance da faixa de idade × preço de lista;
- score 0-100 = percentil do valor esperado entre os deals acionáveis (Engaging até 138 dias com chance estimável). "Score 88" significa "vale mais que 88% do pipeline acionável". O score só varia entre as quatro faixas de idade; dentro de uma faixa, ordena como o preço. Correlação de Spearman entre score e preço em 2017-12-31: 0,74;
- sem chance e sem score: Engaging além de 138 dias (nesta base, nenhum deal fechou depois), Prospecting (não há histórico de prospecção → engajamento) e faixas sem amostra na data;
- categorias, nesta ordem de precedência: Qualificar ou descartar (Prospecting), Confirmar se está vivo (além de 138 dias), Última janela: decidir esta semana (91 a 138 dias), Primeiras duas semanas: contato agora (até 14 dias), Focar agora (score ≥ 70, portanto 15 a 90 dias), Manter follow-up (resto). Conta ausente é uma ação a mais, Cadastrar conta, prefixada ao próximo passo, não uma penalidade;
- ordem dentro do mesmo score: valor de lista, depois conta cadastrada, depois idade menor. Vendedor e setor não participam (testes `test_agent_and_sector_do_not_change_score`, `test_account_is_action_not_factor`).

Em 2017-12-31: 2.089 deals abertos, 298 acionáveis, 37 em Focar agora, 7 nas primeiras duas semanas, 66 em follow-up, 188 na última janela, 1.291 em Confirmar se está vivo, 500 em Qualificar ou descartar. Pipeline nominal de US$ 4.966.215; 64,4% desse valor está além de 138 dias; o acionável vale US$ 693.565 de lista e US$ 144.017 esperados em 90 dias.

## 6. Backtest walk-forward (`03_backtest.py` → `docs/backtest.md`)

Datas principais 30/06 e 30/09 de 2017, espaçadas pelo horizonte para que os desfechos não se sobreponham; 31/07 e 31/08 como leitura de estabilidade (779 dos 1.403 ganhos aparecem em mais de uma data, e o documento diz isso). Em cada data, a chance é calibrada só com snapshots cujo horizonte terminou antes dela, o pipeline em Engaging aberto é pontuado e observam-se os 90 dias seguintes. A fatia Prospecting não é reconstruível em datas passadas e fica fora.

O que o backtest sustenta:

- A chance calibrada com o passado erra, em média, 10 pontos percentuais contra a observada (erro absoluto médio nas 11 células da tabela "prevista vs. observada" de `backtest.md`; máximo de 24 pontos em 31/07 na faixa 0-14). O sentido do erro é sistemático: superestima em 8 das 11 células, porque a taxa de ganho da base cai ao longo de 2017 (H12c) e o painel só enxerga o passado. Nas datas principais: 30/06, faixa 0-14 prevista 46% contra 49% observada e 15-90 prevista 53% contra 43%; 30/09, 0-14 prevista 44% contra 47%, 15-90 prevista 46% contra 28%, 91-120 prevista 7% contra 0%. Em 30/06 só o snapshot de março estava disponível e as faixas de 91 a 138 dias ficaram sem chance.
- O win rate em 90 dias por faixa de score é plano: em 30/06, 48%, 44%, 49%, 42% e 41% da faixa 0-20 à 81-100; em 30/09, 30%, 30%, 25%, 37% e 29%. O score ordena valor esperado, não probabilidade, e o backtest mostra isso.
- O bloco Última janela fecha pouco: em cada data, a tabela de categorias mostra o win rate e a taxa de fechamento em 90 dias dos deals entre 91 e 138 dias.
- O bloco Confirmar se está vivo é descrito, não validado: nesta base nenhum ciclo concluído passa de 138 dias, então um deal aberto há mais de 138 dias não pode ter fechado depois. A tabela mostra só o tamanho do bloco em cada data (149 a 530 deals).

O que o backtest não sustenta, dito sem rodeio: na captura de valor ganho pelo top-N, o score empata com ordenar por preço de lista, no mesmo conjunto e no pipeline inteiro (top-100: 23,3% do valor ganho em 30/06, 19,2% em 30/09, contra 5,9% e 4,2% do aleatório). O score só varia entre quatro faixas e, dentro de cada faixa, ordena como o preço. O que o método faz que ordenar por preço não faz: tira do topo o que a história diz que não fecha (64% do valor nominal), separa a última janela do follow-up, diz o que fazer com cada bloco e não inventa chance onde não há histórico.

## 7. Testes (`solution/tests`, 24 testes)

Invariantes: score em [0,100] ou ausente só fora do suporte; determinismo; vendedor e setor não mudam o score; conta não muda o score e vira ação; `close_value` e `close_date` de deal aberto não mudam o score; valor esperado monotônico no score; o mesmo preço recebe scores diferentes conforme a idade; categorias seguem as regras de precedência; faixa sem amostra fica sem score e diz isso; snapshots nunca cruzam a data de referência; painel respeita a janela limpa e o horizonte; base truncada na data dá a mesma calibração e os mesmos scores; faixa pequena agrupa só com faixas mais velhas; intervalo por deal; fallback declarado em base pequena; data de referência é a última do dataset; junções preservam todas as linhas; alias de produto normalizado; brief com orçamento e ação própria para cadastro; ações do gerente só com alvo concreto. A fixture dos testes é sintética e mínima (`tests/conftest.py`) e não é usada em nenhuma análise.

## 8. Reprodução

`99_clean_env_check.ps1` cria um venv novo, instala `requirements.txt` (versões fixas), roda testes, auditoria, exploração, backtest e um smoke test do app, aborta em qualquer exit code diferente de zero e grava `docs/clean_env_check.log`. `05_check_repo.py` confere que todo caminho citado nos Markdown existe e que nada necessário ficou fora do git (o `.gitignore` da raiz do repositório ignora `submissions/`; os arquivos entram com `git add -f`). Nenhuma chave de API é necessária. Os CSVs vêm do Kaggle (`download_data.py`, API ou zip manual); capturas de tela usam `requirements-dev.txt`.

## 9. Limites

- A base é sintética na origem e tem bordas artificiais: teto de 138 dias (distribuição de ciclo bimodal, 0-20 e 60-120 dias) e janela de fechamentos a partir de março de 2017. As taxas valem para esta base, e a régua de 138 dias precisa ser recalibrada em um CRM real.
- Não há atividade, transições de estágio nem a data em que a conta foi preenchida. Por isso a conta não pode ser fator e a prospecção não recebe chance.
- A chance é de "ganhar em 90 dias entre todos os deals abertos"; a coluna com conta hoje é um limite otimista com look-ahead e não deve ser lida como chance.
- O score não bate ordenar por preço na captura de valor em 2017.
- Um vendedor (Darcel Schlecht) tem 194 deals abertos e nenhum acionável; o método não resolve carteira sem histórico, só a expõe.
- Em datas anteriores a setembro de 2017 o painel não tem amostra para as faixas de 91 a 138 dias; o app mostra "amostra insuficiente" e não inventa número.
