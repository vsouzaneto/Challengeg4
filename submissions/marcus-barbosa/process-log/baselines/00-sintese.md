# Síntese dos baselines — o que a IA produz sozinha

Gerada por um quarto agente que leu as três saídas brutas. Serve como definição operacional do 'baseline' que o README do G4 diz já possuir. Tudo que aparece aqui **não conta como diferencial**.

## O que é comum a 2 ou mais baselines

- Stack: Streamlit + pandas (+ plotly em A e B), app local com `streamlit run app.py`, sem banco/API/auth (A, B, C).
- Escopo: score 0–100 apenas para deals abertos (Prospecting/Engaging); Won/Lost viram histórico para calibrar taxas (A, B, C).
- Abordagem: regras + taxas históricas ('heurísticas calibradas nos dados'), explicitamente NÃO ML; justificativa = explicabilidade + budget 4–6h (A, B, C).
- Suavização bayesiana das win rates com prior k=5: rate = (wins + 5·média_global)/(n + 5) (A, B, C — fórmula idêntica nos três).
- Valor esperado do deal aberto = `products.sales_price` (preço de lista) em vez de `close_value`, normalizado por percentil para o produto caro não dominar (A, B, C). B e C dizem explicitamente que `close_value` é vazamento.
- Momentum/frescor/urgência = dias desde `engage_date` comparados com a mediana do ciclo (close_date − engage_date) dos deals Won (A por produto, B global, C por produto).
- Data de referência = última data do dataset (max de close_date/engage_date), pois não existe 'hoje' (A, B). C usa 'hoje − engage_date' sem definir.
- Fator estágio: Engaging >> Prospecting (A: 0,35/0,75 ou taxa observada; B: 40/100; C: 10/30 dentro do componente probabilidade).
- Fatores de conta: win rate histórica da conta, win rate do setor e porte (revenue) presentes nos três; deal sem conta recebe valor neutro/média global (A, B, C).
- Faixas de prioridade: ≥70 = foco/quente; 45–69 = nutrir/morno (C usa 40); <45 = desprioritizar/frio (A, B, C).
- Correção do nome de produto 'GTXPro' → 'GTX Pro' no pipeline vs catálogo (A, B).
- Filtros por vendedor, manager e escritório regional (bônus do brief) + estágio; B e C adicionam produto/setor (A, B, C).
- Explicabilidade: cada fator gera frase em linguagem de vendedor com pontos ganhos 'de X possíveis'; gráfico de barras de contribuição por fator no detalhe do deal (A, B, C).
- 'Próximo passo sugerido' derivado de faixa + estágio + momentum (fechar / reativar / qualificar / limpar) (A, B, C).
- Lista 'foco da semana/hoje' top-N + tabela completa + painel de detalhe + visão do manager (agregado por vendedor, deals esfriando) (A, B, C); export CSV (A, B).
- Arquitetura: módulo de scoring separado da UI (`scoring.py` ou pacote `scoring/`), `WEIGHTS` em dicionário de configuração no topo, `score_pipeline(df) -> df` (A, B, C).
- Vendedor como filtro, não como penalidade visível: A exclui do score; C dá peso baixo e o exibe como 'sua força neste produto'; ambos citam viés circular/desmotivação (A, C). B inclui 15% agente×produto sem discutir isso.
- Valor esperado ponderado = P(ganho) × valor estimado como segunda ordenação / KPI (A, B, C).
- README com seções Setup / Lógica (tabela de pesos) / Limitações + Process Log separado (A, B, C).
- Limitações declaradas idênticas: sem dados de atividade, dataset estático (sem CRM), não é modelo calibrado/validado, pesos manuais, sem auth, sem feedback loop (A, B, C).
- Backtest por quintil/decil de score vs win rate real recomendado — mas como extensão/futuro (A §9.3, B 'para escalar', C §3.6 '30 min'); nenhum executa.
- Próximos passos: integração CRM + recálculo diário, regressão logística/GBM mantendo explicação, sinais de atividade, SSO (A, B, C).

## Fatores de scoring propostos

| Fator | Pesos vistos | Em quantos baselines |
|---|---|---|
| Estágio do deal (Engaging vs Prospecting) | A: 15/100 (0,35 vs 0,75 ou taxa observada); B: 20% (40 vs 100); C: 30 pts de 100 no componente Probabilidade ×0,45 = 13,5% (Engaging 30 / Prospecting 10) | 3 |
| Momentum / frescor / urgência (dias desde engage_date vs mediana do ciclo Won) | A: 15/100 (1,0 até 1× ciclo, 0,45 em 1,5×, 0,05 em 3×; sem data = 0,5); B: 20% (100 até 1× mediana, linear até 0 em 2×; sem data = 50); C: 25% em formato sino (50 se <50% do ciclo, 100 entre 50–100%, 70 entre 100–150%, 20 acima de 150%, 10 Prospecting além do ciclo) | 3 |
| Valor do deal (sales_price do produto, percentil) | A: 20/100 (percentil dentro do pipeline aberto); B: 15% (percentil dentro do catálogo de 7 produtos); C: 70 pts de 100 no componente Valor ×0,30 = 21% | 3 |
| Histórico da conta (win rate suavizada da conta) | A: 20/100 (sem conta = média global ×0,9); B: 15% (sem conta = média global); C: 15 pts de 100 no comp. Probabilidade ×0,45 = 6,75% (Won=15 / só Lost=3 / sem histórico=8) | 3 |
| Win rate do setor da conta | A: 60% do fator 'perfil da conta' de 10 = 6/100; B: 5%; C: 15 pts de 100 no comp. Probabilidade ×0,45 = 6,75% | 3 |
| Porte da conta (revenue) | A: 40% do fator 'perfil' de 10 = 4/100 (tercis 0,35/0,6/0,85); B: 10% (log revenue min-max); C: 10 pts ×0,45 = 4,5% (fit por faixa de win rate) + 30 pts ×0,30 = 9% (potencial da conta) = 13,5% | 3 |
| Win rate do produto | A: 20/100; C: 20 pts de 100 no comp. Probabilidade ×0,45 = 9%; B: não usa (substitui por vendedor×produto) | 2 |
| Win rate do vendedor no produto | B: 15%; C: 10 pts ×0,45 = 4,5% (deliberadamente baixo, exibido como força, não penalidade); A: 0 (excluído de propósito por viés circular) | 2 |
| Valor esperado = P(ganho) × valor (desempate/KPI, não entra no score) | A: P = média de produto, conta, perfil e estágio; B: P = média de taxa da conta e taxa vendedor×produto; C: componente Valor 30% já embute; usado como métrica de manager | 3 |

## Lacunas: o que nenhum baseline fez ou verificou

- Nenhum baseline abre os CSVs: todas as afirmações sobre o dataset (GTXPro vs GTX Pro, Prospecting sem engage_date/account, 'win rate varia bastante por produto', ~85 contas, ciclo mediano) vêm de memória; nenhum mostra `df.describe()`, contagem de nulos, contagem de linhas antes/depois dos joins. A põe 'contar linhas' no checklist mas não executa.
- Nenhum verifica se os fatores 'aprendidos' discriminam de fato. Se as win rates por produto/setor/conta ficarem todas próximas da média global (~0,6), os fatores de 20 pts de A e 15%+5% de B viram constantes: o ranking passa a ser decidido por estágio + tempo + preço, contradizendo a premissa 'aprender com os dados, não inventar pesos' (A §1) sem que ninguém tenha checado.
- Nenhum compara peso nominal vs peso efetivo. Fatores de win rate variam numa faixa estreita (≈0,5–0,8) enquanto momentum e valor varrem 0–1; em A um fator de 20 pts contribui na prática ~6 pts de spread, em B histórico da conta (rate×100, ~50–80) contribui ~4,5 pts contra 20 do frescor. Nenhum mediu variância/contribuição por fator no pipeline real.
- Nenhum executa o backtest que os três recomendam. Nenhum resultado de win rate por quintil aparece; C deixa 'X×' em branco no resumo executivo. Também ninguém nota que o backtest sobre Won/Lost não consegue validar momentum/urgência (não há snapshot de 'quando estava aberto') nem estágio (todo fechado passou por Engaging) — só valida os sub-fatores de probabilidade/valor.
- Vazamento no backtest e nas taxas: as win rates de conta/produto/setor/vendedor são calculadas sobre todo o histórico, incluindo o próprio deal avaliado e deals fechados depois (sem leave-one-out nem corte temporal). Só B menciona ('vazamento leve'); ninguém trata.
- Nenhum analisa a distribuição de `days_in_pipeline` dos deals Engaging com data de referência = fim do dataset. Se boa parte dos Engaging engajou meses antes da última data, a maioria cai em 'esfriando/morto' (A mom≈0,05, B frescor 0, C 20 pts) e a 'lista de hoje' fica dominada por poucos deals recentes — hipótese não testada.
- Nenhum examina o que sobra para deals em Prospecting: sem engage_date (momentum neutro), possivelmente sem conta (histórico/setor/porte neutros) e estágio fixo, restam só produto e preço → ~7 scores distintos, empatados em massa. Ordem dentro do empate é arbitrária; ninguém propõe desempate explícito além de 'expected_value' (A).
- Artefato de ordenação não examinado: deal Prospecting sem data recebe momentum neutro (A 0,5 / B 50) e pode superar em momentum um deal Engaging real a 1,6× do ciclo (A ≈0,4 / B 40). Nenhum discute se isso é desejado.
- Percentil de valor sobre 7 produtos (B: no catálogo; A: no pipeline com empates) gera apenas 7 valores discretos; se o produto mais vendido for o mais barato, a maioria dos deals recebe valor baixo. Nenhum checa a distribuição resultante nem considera ticket médio Won por conta×produto (C só sugere).
- Nenhum trata `account` ausente em deals fora de Prospecting: se houver mais linhas sem conta do que deals Prospecting (a verificar no CSV), o fator conta cai para neutro numa fatia maior do que A/B assumem, e o join left com accounts gera NaN em sector/revenue silenciosamente.
- Uso real 'segunda-feira de manhã' não é reproduzível: a ferramenta mostra um snapshot de 2017 fixo. Nenhum oferece controle de 'data as-of' para simular o uso ao longo do tempo nem discute como o avaliador vai perceber o valor sem esse recurso.
- Testes: só A tem testes e são smoke tests que dependem do CSV real (`load_all('data')`); nenhum testa a matemática de suavização, momentum ou faixas com dados sintéticos; B e C não têm testes. Nenhum verificou se o código roda (não há saída de execução, screenshot ou log).
- Nenhum valida o checklist 'score não é monotônico com valor' (A) nem mostra o top-10 real para o teste de 'faz sentido para um vendedor?'.
- Process log: os três dizem que é obrigatório e A dá a estrutura, mas nenhum fornece evidência concreta (prompts usados, decisões contra a IA, iterações de peso com prints).
- Nenhum trata deals com `engage_date` posterior à data de referência ou ciclos negativos (close_date < engage_date) ao calcular a mediana do ciclo Won; nenhum trata NaN em `sales_price` após merge se o nome do produto não bater.
- Compatibilidade de versões: A e B usam `use_container_width=True` (deprecado no Streamlit ≥1.49 em favor de `width='stretch'`) e A usa `st.cache_data` retornando DataFrame com `.attrs` (persistência de attrs via pickle a verificar). Ninguém fixa versões nem valida em ambiente limpo.
- Nenhum define como o vendedor dá feedback ou marca 'contactado' na v1 (A só lista como extensão), logo o fator momentum nunca reseta — a lista 'esfriando' é a mesma toda semana.
- Nenhum discute critério de sucesso mensurável para o avaliador (ex.: lift do quintil superior, % do pipeline coberto pelo top-10, tempo até primeira decisão), apenas afirma que 'ajuda a decidir'.

## Afirmações provavelmente erradas ou sem dado

- A (§3.2, README): 'os 7 produtos convertem em taxas muito diferentes; é o sinal mais forte do histórico' e 'produto e conta são os maiores discriminadores' — afirmação sem nenhum número; no dataset CRM Sales as win rates por produto e por setor tendem a ficar próximas da média global, o que faria do fator de 20 pts um quase-constante. Chute sem dado.
- A/B/C: a suavização bayesiana k=5 é apresentada como decisão-chave ('conta com 1 deal Won teria 100%'), mas com ~85 contas e milhares de deals fechados cada conta tende a ter dezenas de deals — o prior de 5 quase não move nada. O cenário justificador provavelmente não existe no dataset; o mecanismo é inofensivo, mas a justificativa é inventada.
- A (`features._stage_conversion`): assume que 'deals sem engage_date (só Prospecting) são desconhecidos', mas todos os Won/Lost têm engage_date, então `engaged_rate == global_rate` e Prospecting = global×0,6 (multiplicador arbitrário). O `STAGE_BASE` 0,35/0,75 documentado nunca é usado porque `stage_conversion` sempre tem as duas chaves — documentação e código divergem.
- A (§3.4 vs `scorer.py`): a flag 'Esfriando' é definida no texto como 'momentum < 0,3', mas o código usa `ratio > COOLING_RATIO (1,5)`, onde momentum ainda vale 0,45. Inconsistência doc/código.
- A (§3.5 exemplo): 'Conta Acme Corp fechou 7 de 9 (+18 pts)' — com k=5 e média ~0,63 a taxa suavizada é ≈0,72 → ≈14 pts, não 18; 'GTX Pro win rate 68%' e 'ciclo típico de 30 dias' são números ilustrativos apresentados como se fossem do dataset.
- A (`p_win`): chamado de 'P(ganho)' mas é a média aritmética de dois win rates, um índice composto (0,6·setor + 0,4·porte, que não é probabilidade) e um fator de estágio — não é probabilidade calibrada; o 'valor esperado' derivado dele é uma métrica arbitrária rotulada como dinheiro.
- A (`explain`): ícone ✅ para pts/peso ≥ 0,6 — como win rates ficam ~0,6+, produto/conta/setor aparecem ✅ em quase todo deal, esvaziando a explicação.
- B (§1): 'Vendedor × produto ... é sinal real de fit' com 15% de peso, sem discutir o viés circular que A e C tratam explicitamente, e sem verificar que a matriz 35 agentes × 7 produtos tem amostra suficiente (com ~27 deals por célula o k=5 pouco corrige). Além disso, o README de B diz 'pesos refletem julgamento, não fitting' enquanto o app deixa o usuário alterar pesos por slider — a 'lógica explicável' deixa de ser fixa/documentável.
- B (frescor): usa mediana global do ciclo, mas o próprio texto justifica com 'ciclo típico daquele produto'; e dá nota máxima (100) a deals de 0 dias, contradizendo a lógica de C (deal muito cedo não é urgente). Escolha não justificada.
- B (`expected_value`): preço × média(taxa conta, taxa vendedor×produto) ignora o estágio — um deal Prospecting recebe o mesmo VE que um Engaging idêntico.
- C (§3.4): tabela de urgência inclui 'Deal em Prospecting há mais que o ciclo típico' e a fórmula 'hoje − engage_date', mas Prospecting no dataset não tem engage_date e C nunca define 'hoje' (se for a data real de 2026, todo deal é 'provavelmente morto'). Regra inaplicável como escrita.
- C (§3.2): 'Histórico da conta: conta já tem deal Won = 15; só Lost = 3; sem histórico = 8' — com ~85 contas e dezenas de deals cada, praticamente toda conta com histórico tem algum Won → o sub-critério vale 15 para quase todos, zero discriminação. 'Taxa do produto escalada 0–20' sem definir a escala (linear de 0%? min-max entre produtos?).
- C (§1 vs §3.1): apresenta 'Score = Probabilidade × Valor × Urgência' e depois adota a forma aditiva 45/30/25; os pesos 45/30/25 são declarados 'ponto de partida defensável' sem nenhuma justificativa quantitativa além de 'o backtest é o que os torna justificados' — que não foi feito.
- A e C citam o brief entre aspas ('algo que o vendedor abra e saiba onde focar', 'regras + heurísticas bem apresentadas valem mais que XGBoost sem interface') — não é possível verificar se são citações literais; tratar como paráfrase.
- A (§2): '~85 contas, 7 produtos, 35 vendedores, ~8.800 deals' e 'Prospecting costumam não ter engage_date nem account' — plausíveis mas não verificados; se `account` faltar em mais linhas que os ~500 Prospecting, a afirmação está incompleta e o impacto do fator conta neutro é maior do que o descrito.
- A/B: faixas ≥70 / 45–69 / <45 foram escolhidas antes de ver a distribuição de scores; com fatores de win rate comprimidos em ~0,6, o score máximo realista fica bem abaixo de 100 e pode haver quase nenhum deal 'Foco' ou quase todos 'Nutrir'. Thresholds fixos sem calibração à distribuição real.
