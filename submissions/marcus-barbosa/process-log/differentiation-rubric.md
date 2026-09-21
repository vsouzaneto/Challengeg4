# Rubrica de diferenciação — escrita antes de codar

**Data:** 2026-09-21, antes de abrir qualquer CSV.
**Objetivo:** o README do G4 avisa que "parecido com o baseline não é suficiente". Esta rubrica define, de forma mensurável, o que esta entrega faz que os três baselines em `baselines/` não fazem. Ao final, cada linha recebe evidência (arquivo, teste ou número) ou é marcada como não atingida.

## O que o baseline já faz (não conta como diferencial)

Resumo de `baselines/00-sintese.md`: Streamlit + pandas; score 0–100 por soma ponderada de 6 fatores (estágio, momentum vs. mediana do ciclo, valor por preço de lista, win rate de conta, setor, porte, às vezes produto e vendedor×produto); suavização bayesiana k=5; data de referência = última data do dataset; normalização GTXPro; faixas fixas 70/45; filtros por vendedor, manager e região; frase por fator; "próximo passo"; visão de manager; README com Setup/Lógica/Limitações; backtest **recomendado como futuro, nunca executado**.

## Diferenciadores

| # | Lacuna do baseline | O que esta entrega faz | Como se prova |
|---|---|---|---|
| D1 | Nenhum baseline abre os CSVs; toda afirmação sobre o dado é de memória | Auditoria de dados como etapa 0, gerada por script: linhas, nulos, joins antes/depois, `GTXPro`, % de deals sem conta, datas inconsistentes, faixa temporal | `solution/01_audit.py` → `docs/data_health_report.md` com números |
| D2 | Nenhuma hipótese é testada; os pesos são "ponto de partida defensável" | Hipóteses do Marcus escritas antes dos dados, cada uma confirmada ou refutada com número; fatores nascem das hipóteses que sobreviveram | `process-log/hypotheses.md` com coluna de resultado |
| D3 | Peso nominal ≠ peso efetivo: fatores de win rate variam em faixa estreita e viram constantes; ninguém mede | Poder discriminativo medido por fator (spread entre quartis, variância da contribuição); fator sem sinal é removido ou declarado fraco na interface | Tabela "peso nominal vs. efetivo" em `docs/methodology.md`; aviso na UI para fator fraco |
| D4 | Win rates calculadas com o próprio deal e com deals fechados depois (leakage); `close_value`/`close_date` tratados de forma inconsistente | Taxas históricas com corte temporal (só deals fechados antes da data de referência); `close_value` e `close_date` de deals abertos nunca entram no score | Teste de invariância: alterar `close_value`/`close_date` de deal aberto não muda o score |
| D5 | Backtest recomendado, nunca executado; e ninguém nota que backtest em Won/Lost não valida momentum nem estágio | Backtest executado em duas camadas: (a) win rate por faixa de score nos deals fechados, monotônico; (b) **backtest por snapshot**: reconstruir o pipeline aberto em datas passadas, pontuar e medir quanto do top-N fechou Won depois, o que valida momentum e estágio | Tabelas em `docs/backtest.md`; script `solution/03_backtest.py` |
| D6 | Faixas 70/45 fixas antes de ver a distribuição; empates em massa nos deals Prospecting | Faixas calibradas por quantil na distribuição real; desempate explícito e documentado para deals com poucos atributos | Histograma do score e regra de desempate em `methodology.md` |
| D7 | Snapshot de 2017 fixo; "segunda-feira de manhã" não é reproduzível | Controle de data de referência ("as-of") na interface: o vendedor ou o avaliador escolhe a segunda-feira e vê o pipeline como estava naquele dia | Componente na UI + screenshot em duas datas diferentes |
| D8 | Ranking + "próximo passo" genérico | Brief de segunda-feira opinativo: must-acts por vendedor, must-acts por manager (deals a intervir, agentes sobrecarregados) e camada sistêmica de RevOps (ex.: deals órfãos sem conta como problema de processo) | Tela "Brief" com três blocos; exemplos no README |
| D9 | Três faixas (foco / nutrir / desprioritizar) sem regra de transição | Cinco categorias de ação com critério explícito de entrada e saída (Focar agora / Follow-up / Reengajar / Qualificar ou descartar / Requalificar) | Tabela de regras em `methodology.md`; teste por categoria |
| D10 | Testes ausentes ou smoke tests dependentes do CSV real | ≥30 testes de invariantes rodando sem o CSV real (fixture pequena versionada): faixa 0–100, determinismo, deal sem conta pontuado, GTXPro normalizado, ref_date = max(close_date), win rate = Won/(Won+Lost), anti-leakage, monotonicidade das categorias | `pytest -q` verde; contagem no README |
| D11 | Sem versões fixadas, sem validação em ambiente limpo, deps deprecadas | `requirements.txt` com versões fixas; validação em venv novo documentada; roda sem chave de API; deploy público | Log da validação em `docs/methodology.md`; URL pública |
| D12 | Process log descrito, nunca entregue | Ledger de decisões com origem (Marcus / consenso / IA) e contagem; ≥5 erros reais da IA com causa raiz; auditoria adversarial por agente independente; commits incrementais com autoria real; chat export e screenshots | `process-log/*.md`, `git log`, `screenshots/`, `chat-exports/` |
| D13 | "Ajuda a decidir" afirmado, nunca medido | Critério de sucesso mensurável para a Head de RevOps: lift de win rate do quintil superior vs. média, % do valor do pipeline coberto pelo top-N, e plano de piloto com grupo de controle e gate de go/no-go | Seção "Como saber se funcionou" no README |
| D14 | Metodologia dispersa entre texto e código | `docs/methodology.md` liga cada número, fator, peso e regra ao script que o gerou, do CSV bruto ao score | Links diretos arquivo:linha em cada afirmação numérica |
| D15 | Ícones ✅ em quase todo fator; falsa precisão | Explicação em linguagem de vendedor que diz quando um fator é fraco ou neutro, sem inflar; frase por fator gerada de regra auditável | Exemplos reais de breakdown no README para 3 deals |
| D16 | Vendedor ora excluído, ora com 15%, sem teste | Decisão sobre usar ou não o histórico do vendedor tomada com dado: medir spread de win rate por agente e por agente×produto, discutir viés circular, e registrar a escolha no ledger | Número + decisão em `decisions.md` |

## Como esta rubrica será usada

1. Antes de codar cada módulo, verificar quais linhas ele cobre.
2. A banca de agentes revisores recebe esta tabela e só marca a linha como atingida com a evidência indicada.
3. Linhas não atingidas ficam explícitas na seção de limitações, nunca omitidas.
