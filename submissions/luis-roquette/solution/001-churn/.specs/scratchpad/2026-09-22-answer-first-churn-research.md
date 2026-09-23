# Pesquisa SDD 2a — resposta executiva de churn

Data: 2026-09-22. Escopo: pesquisa e skill; sem código, execução analítica ou alteração da SPEC. Orientação recebida: priorizar soluções existentes e fontes GitHub/Reddit antes de criar.

## Recomendação

Reutilizar o painel temporal, contratos e publicação canônica existentes. Publicar primeiro o que os dados permitem afirmar sobre perda de clientes, perda de receita, uso e satisfação; avaliar mecanismos depois. Um gate causal reprovado não apaga um fato descritivo válido. Não instalar DoWhy, SHAP, lifelines, Spark ou outro framework para essa mudança.

Esta arquitetura é uma síntese proposta a partir das fontes e do código local, não uma arquitetura pronta comprovada por algum repositório externo. A pesquisa validou documentação e padrões disponíveis; não reproduziu resultados de terceiros.

## Evidência local inspecionada

| Local relativo à solução | O que já existe | Implicação para a arquitetura |
|---|---|---|
| `src/ravenstack_churn/panel.py` | Janelas anteriores ao cutoff, coortes strict/observed, primeiro churn e MRR anterior ao evento | Reutilizar a unidade conta-cutoff e a política temporal; explicitar o significado de churn de conta versus assinatura. |
| `src/ravenstack_churn/diagnosis.py:build_claim_checks` | Uso por média de contas com cobertura e satisfação ponderada por respostas | A métrica atual de uso não é volume total; cobertura de satisfação não representa todos os clientes. Comparar denominadores antes de dizer que o CEO ou CS está errado. |
| `src/ravenstack_churn/diagnosis.py:evaluate_candidates` | Associação ajustada, sensibilidade, corroboração, saída accepted/inconclusive | Acrescentar níveis de evidência na futura arquitetura sem afrouxar os gates existentes nem transformar ausência de significância em rejeição. |
| `src/ravenstack_churn/publish.py:_build_report` | Decisão depende de finding aceito e abre com insuficiência quando nenhum passa | A resposta descritiva deve existir independentemente do modelo; o texto sobre nenhuma hipótese passar também precisa refletir o resultado real. |
| `artifacts/report.md`, `README.md`, `requirements.txt` | Artefato reporta tendências divergentes e problemas temporais; pandas/scipy/statsmodels já são dependências fixadas | Os números foram lidos, não recalculados nesta pesquisa. Não tratar artefato histórico como validação atual nem dependência declarada como importação testada. |

## Fontes consultadas: 8

| Fonte | Reutilização útil | Limite verificado |
|---|---|---|
| [SaaS-Product-Analytics-SQL](https://github.com/shreycooo/SaaS-Product-Analytics-SQL) | Referência de perguntas cruzando cinco tabelas, receita, retenção, suporte e uso em estrutura compatível com RavenStack. | README e apresentações são estudo de portfólio, não comprovação de causalidade. As conclusões sobre suporte e adoção beta não foram reproduzidas. Não copiar seus findings para nosso dataset. |
| [fighting-churn](https://github.com/richhuwtaylor/fighting-churn) | Painel de observações periódicas, janelas anteriores, períodos ativos, QA de eventos, métricas por exposição e coortes; diretórios de SQL/Python confirmados via GitHub API. | SocialNet7 é simulado; tolerâncias de gaps e horizontes são escolhas do exemplo. Regressão/calibração não provam efeito de intervenção. Reaproveitar o padrão no painel local, sem PostgreSQL novo. |
| [Microsoft / documentação SHAP sobre causalidade](https://shap.readthedocs.io/en/latest/example_notebooks/overviews/Be%20careful%20when%20interpreting%20predictive%20models%20in%20search%20of%20causal%20insights.html) | Exemplo de retenção distingue explicação de previsão e consequência de alterar uma variável. | SHAP, coeficientes e correlação não identificam causa. Nem importância alta nem direção intuitiva autorizam prometer redução de churn. |
| [DoWhy: refutação de estimativas](https://www.pywhy.org/dowhy/v0.13/user_guide/refuting_causal_estimates/index.html) | Tornar pressupostos explícitos e tentar refutar conclusões por controles negativos e sensibilidade. | Passar testes não prova que pressupostos causais são verdadeiros. Reutilizar a disciplina metodológica; não instalar DoWhy para classificar evidências descritivas. |
| [Databricks: preparação de sobrevivência](https://www.databricks.com/notebooks/survival_analysis/survival_analysis_01_data_prep.html) | Reconstrução do ciclo de assinatura, períodos de risco e tratamento explícito de reativação. | Notebook de 2020, dados KKBox e definição de gap própria. Conteúdo metodológico disponível na busca; renderização direta incompleta. Não importar sua infraestrutura nem seu limiar de 30 dias. |
| [statsmodels: SurvfuncRight](https://www.statsmodels.org/stable/generated/statsmodels.duration.survfunc.SurvfuncRight.html) | Kaplan–Meier com censura à direita e entrada tardia usando dependência existente, se tempo até churn for necessário. | Exige tempos e população em risco confiáveis; curvas não tornam comparação observacional causal. Sobrevivência é opcional, não pré-requisito da resposta ao CEO. |
| [statsmodels: proportion_confint](https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.proportion_confint.html) | Intervalos para proporções, incluindo Wilson, junto de numerador e denominador. | Intervalo binomial não resolve dependência entre observações repetidas da mesma conta; usar unidade independente ou método que respeite agrupamento. |
| [Reddit: retained/right-censored customers](https://www.reddit.com/r/datascience/comments/w5jli5/) | Busca identificou discussão pertinente sobre churn e censura. | Abertura direta falhou. É pista de descoberta, não fonte validada nem fundamento técnico; a documentação oficial de statsmodels sustenta a recomendação. |

Não copiar código dos repositórios sem verificar licença aplicável. Nenhum código externo foi copiado nesta pesquisa.

## Escada proposta

| Nível | Critério de publicação | Linguagem e consequência |
|---|---|---|
| Fato confirmado | Cálculo reproduzível, população, período, unidade, numerador/denominador e exclusões explícitos; limitações não invalidam aquela afirmação delimitada. | “Nesta população e janela, observamos X.” Pode justificar auditoria, monitoramento ou priorização operacional dentro do escopo autorizado. |
| Mecanismo sustentado | Ordem temporal válida, associação consistente em grupos comparáveis e sensibilidade, corroboração independente compatível com o mesmo período; confundidores e explicações alternativas declarados. | “Evidências sustentam este mecanismo, sob estas limitações.” Pode orientar piloto mensurável; não equivale a efeito causal identificado. |
| Hipótese plausível | Explicação compatível, porém amostra, cobertura, identificação ou cronologia insuficientes. | “É uma hipótese a testar.” Registrar o dado ou experimento que poderia confirmar/refutar; não inventar probabilidade ou ganho financeiro. |
| Afirmação rejeitada | Contradição reproduzível com o enunciado exato, ou inferência cuja conclusão excede a evidência. | “A afirmação X não se sustenta porque Y.” Rejeitar a formulação, sem concluir que o efeito é zero. Falha de modelo ou intervalo amplo significam inconclusão. |

## Desenho mínimo a levar à SPEC

1. **Responder às três alegações.** Verificar se churn realmente subiu com taxa e população em risco, além de contagem e MRR perdido. Para uso, mostrar volume total e uso por conta comparável. Para satisfação, separar respondentes, não respondentes e cobertura por contas/tickets. Todos usam intervalos de calendário explícitos.
2. **Explicar a aparente contradição.** Comparar coortes e composição; se necessário, padronizar pesos e usar painel de contas comparáveis. Médias divergentes são fatos; só chamar de efeito de composição ou paradoxo de Simpson após decomposição que os demonstre. A coorte definida por churn futuro é retrospectiva, não segmento acionável disponível no cutoff.
3. **Manter trilha de evidências.** Cada claim precisa de ID, nível, população/período, métrica, fonte/artefato, cobertura, sensibilidade e contraevidência. Vincular motivos/feedback ao evento e período pertinentes; o `_reason_corroborates` atual consulta o primeiro churn global, exigindo revisão de alinhamento antes de promover mecanismo.
4. **Separar decisão de inferência.** Auditoria e coleta prospectiva podem ser recomendadas mesmo sem causa identificada. Piloto tem dono, prazo, hipótese e critério de sucesso. Receita exposta, receita efetivamente perdida e recuperação hipotética são métricas diferentes; cenários de recuperação exigem premissas explícitas, não promessa.
5. **Reutilizar publicação existente.** Relatório e dashboard leem o mesmo conjunto canônico. pandas cobre agregação/decomposição; scipy cobre comparação/reamostragem quando necessária; statsmodels cobre intervalos e associações. Modelagem nova só entra se mudar a decisão e respeitar temporalidade, agrupamento por conta e multiplicidade de hipóteses.

Validação deste trabalho: revisão das fontes e pontos locais citados; nenhuma suíte de análise executada e nenhuma alteração na SPEC ou no pipeline. `python3 /Users/luisroquette/.codex/skills/.system/skill-creator/scripts/quick_validate.py submissions/luis-roquette/solution/001-churn/.claude/skills/answer-first-churn` retornou `Skill is valid!` (exit 0).
