---
name: answer-first-churn
description: Estruturar diagnóstico executivo de churn com resposta primeiro, denominadores verificáveis e escada de evidências, reutilizando o pipeline e dependências existentes. Use para relatórios, dashboards e especificações de análise de churn.
---

# Resposta executiva de churn

Responda o que está acontecendo, quem concentra a perda e qual ação é justificável com a evidência disponível. Não condicione fatos descritivos à aprovação de um modelo causal ou preditivo. Esta skill orienta análise e comunicação; não autoriza contato com clientes, alteração de dados ou execução externa.

## Fluxo mínimo

1. Leia contratos, painel, diagnóstico e publicação existentes antes de criar algo. Reutilize unidade conta-cutoff, gates temporais, strict/observed e artefatos canônicos. Na RavenStack, comece em `src/ravenstack_churn/{panel,diagnosis,publish}.py`.
2. Teste separadamente “churn subiu”, “uso cresceu” e “satisfação está boa”. Informe calendário, população em risco, contas/eventos, numerador/denominador, cobertura e exclusões. Separe churn de clientes de churn de receita; volume total de uso por conta; satisfação dos respondentes de satisfação de toda a base.
3. Compare populações compatíveis e composição por coorte, plano, tempo de vida e exposição. Controle alterações de cobertura. Só atribua a divergência à composição após decompor ou padronizar pesos. Coorte definida por churn futuro serve à retrospectiva, não à seleção prospectiva de intervenção.
4. Classifique cada afirmação na tabela abaixo. Preserve ID, fonte, período, cálculo, limitações e contraevidência. A resposta inicial pode conter fatos úteis mesmo se todos os mecanismos permanecerem inconclusivos.
5. Recomende ação proporcional: auditoria/coleta, piloto mensurável ou intervenção sustentada, sempre dentro da autorização. Defina dono, prazo e métrica. Diferencie MRR perdido, MRR exposto e recuperação hipotética; não apresente cenário como impacto causal estimado.

## Escada de evidências

| Nível | Requisito |
|---|---|
| Fato confirmado | Resultado reproduzível no recorte declarado, com denominador e limitações que não invalidem esse enunciado. |
| Mecanismo sustentado | Temporalidade, comparação adequada, robustez e corroboração de fontes no mesmo período; pressupostos e alternativas explicitados. Ainda não é causa comprovada. |
| Hipótese plausível | Explicação compatível, mas evidência incompleta; nomear teste ou dado faltante. |
| Afirmação rejeitada | Contradição demonstrada ou conclusão além do que a evidência permite; rejeitar o enunciado exato, sem transformar baixa potência ou falha de modelo em prova de efeito nulo. |

Correlações, SHAP, importância de variáveis e odds ratios ajustados não demonstram causalidade. Refutações aprovadas também não provam pressupostos. Confira as advertências primárias de [Microsoft/SHAP](https://shap.readthedocs.io/en/latest/example_notebooks/overviews/Be%20careful%20when%20interpreting%20predictive%20models%20in%20search%20of%20causal%20insights.html) e [DoWhy](https://www.pywhy.org/dowhy/v0.13/user_guide/refuting_causal_estimates/index.html).

## Reuso sem dependência nova

Use pandas para agregação e decomposição; scipy para comparação ou reamostragem quando necessária; statsmodels para intervalos e associações já suportados. Respeite agrupamento por conta em painéis, multiplicidade de hipóteses e dados disponíveis no cutoff. Não ajuste indiscriminadamente por mediadores, variáveis posteriores ou potenciais colisores.

| Necessidade | Padrão existente e limite |
|---|---|
| Painel temporal e QA | [fighting-churn](https://github.com/richhuwtaylor/fighting-churn): adaptar janelas e períodos ativos ao painel local; exemplo simulado, sem transferir seus limiares ou conclusões. |
| Perguntas entre tabelas | [SaaS-Product-Analytics-SQL](https://github.com/shreycooo/SaaS-Product-Analytics-SQL): usar como checklist; achados do portfólio não são evidência sobre nossa execução. |
| Proporções e incerteza | [proportion_confint](https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.proportion_confint.html): Wilson disponível; não tratar conta-mês repetida como ensaio independente. |
| Tempo até churn, somente se necessário | [SurvfuncRight](https://www.statsmodels.org/stable/generated/statsmodels.duration.survfunc.SurvfuncRight.html): Kaplan–Meier/censura na dependência existente; requer cronologia confiável. [Databricks](https://www.databricks.com/notebooks/survival_analysis/survival_analysis_01_data_prep.html) ajuda a formular períodos de risco, sem importar Spark/lifelines. |

Busque implementações existentes antes de criar; GitHub fornece padrões inspecionáveis e Reddit pistas a confirmar em fontes primárias. Verifique licença antes de copiar código. Não instalar SHAP/DoWhy para justificar linguagem causal. Entregue resposta executiva, evidências rastreáveis e ações; mantenha detalhes técnicos depois da resposta.
