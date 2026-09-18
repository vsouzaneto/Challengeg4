# Rubrica de diferenciação (G1)

Escrita **antes** de construir a solução, a partir das 5 respostas de baseline (`process-log/baseline/`). Cada item é verificável. O `g4-reviewer` usa esta tabela no G8, e a submissão só vai para PR com todos os itens em ✅.

Piso (o baseline já entrega, então não conta como diferencial): conclusão "sem sinal", ANOVA/t-test por dimensão, R² ≈ 0, painel com teste de significância.

| # | Diferenciador | Baseline mais próximo | Como verificar | Gate |
|---|---|---|---|---|
| D1 | **Explicar o mecanismo do "sem sinal":** prova de que as 4 métricas são Poisson com λ fixo, independente das features (razão var/média, qualidade de ajuste, λ igual entre segmentos) | Claude: "sino estreito, típico de ruído" (sem mecanismo) | `docs/data-quality-report.md` com teste e números | G2 |
| D2 | **Equivalência, não só ausência:** TOST contra um limiar de relevância prática definido antes, mais o MDE com o n disponível | Nenhum | `docs/statistical-report.md`: veredito DIFERENTE / EQUIVALENTE / INCONCLUSIVO por comparação | G3 |
| D3 | **Desmontar os "insights" do baseline com números:** 3,2x (teto real 1,02x), ER/followers (artefato 1/x), patrocínio −15% (real −0,005%) | Nenhum (as IAs não checam umas às outras) | Seção "O que NÃO funciona" citando `g1-baseline-claims-check.csv` | G3/G5 |
| D4 | **Lacuna do dado → falha do processo:** AS-IS em raias com FP-xx ligados a DQ-xx | Claude: "auditar a pipeline de coleta" (1 frase) | `docs/process/01..02` | G4 |
| D5 | **TO-BE com IA inserida por nível** (AUTO/ASSIST/HUMANO), com critério de promoção de nível e RACI (quem valida break-even, quem opera o controle) | ChatGPT: "todo sponsored post passa a ter controle" (sem dono) | `docs/process/03..05` | G4 |
| D6 | **Toda pergunta do brief respondida explicitamente:** custo implícito como função de break-even, threshold de seguidores, frequência (10–11 posts/creator, sem variação), audiência com alerta de falácia ecológica, hashtags (palavras aleatórias) | Claude responde 4 de ~10 | Tabela "pergunta → resposta → o que fazer" no README | G5/G7 |
| D7 | **Recorte de escopo pelo contexto do negócio:** estratégia para Instagram, TikTok e YouTube (os canais da empresa); Bilibili e RedNote só como controle | Todas as IAs tratam as 5 plataformas igualmente | Decisão registrada em `process-log/decisions.md` | G1 |
| D8 | **Ferramenta que roda o processo, não só mostra números:** gate de aprovação de patrocínio (data contract + MDE + break-even) e leitura de experimento (Escalar/Replicar/Iterar/Parar), com health check de CSV novo que **detectaria o padrão Gemini/Grok** | Claude: painel de significância; Gemini: planilha | App rodando + testes + screenshots | G6 |
| D9 | **Owners e prazos na estratégia:** máx. 7 decisões P0–P2 com owner, KPI e stop condition | Grok: P0/P1/P2 sem owner | `reports/strategy.md` | G5 |
| D10 | **Process log auditável:** baseline literal + checagem numérica + decisões humanas + erros da IA + crítica multi-modelo | — | `process-log/` completo | G8 |

## Anti-rubrica (se aparecer, é falha)
- Qualquer "X vezes mais" sem IC e sem n
- "ROI" sem custo
- Modelo preditivo apresentado como ferramenta (o R² do baseline já mostra que não serve)
- Recomendar realocação de verba entre plataformas ou faixas de creator com base neste dataset
