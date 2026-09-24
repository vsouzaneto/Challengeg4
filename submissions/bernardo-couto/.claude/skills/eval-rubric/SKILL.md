---
name: eval-rubric
description: Rubrica de avaliação do Challenge 003 (Lead Scorer) reconstruída a partir dos critérios oficiais do G4, com escala 0–5 por critério, sinais de baseline (o que uma IA produz sozinha) e sinais de julgamento humano. Use para autoavaliar a entrega em marcos e antes do PR.
user-invocable: false
---

# Rubrica — Challenge 003 Lead Scorer

Fontes: `../../challenges/build-003-lead-scorer/README.md` (critérios de qualidade, requisitos mínimos, dicas), `../../submission-guide.md` (forte vs. fraca), `../../README.md` (o que é avaliado, baseline).

## Portões (reprovam sozinhos)

- Não roda seguindo o README → reprovado.
- Não usa os dados reais do dataset → reprovado.
- Scoring é só ordenar por valor → não cumpre requisito mínimo.
- Vendedor não entende por que o score é alto/baixo → não cumpre requisito mínimo.
- Sem process log → desclassificado.
- Arquivos alterados fora de `submissions/bernardo-couto/` → PR rejeitado.

## Critérios (0–5 cada)

| # | Critério (texto do G4) | 0–1 | 3 | 5 |
|---|---|---|---|---|
| C1 | Funciona de verdade? Dá pra rodar seguindo as instruções? | Falha no setup | Roda com ajuste manual | Roda em máquina limpa em ≤5 min, testes verdes |
| C2 | O scoring faz sentido? Usa as features certas? Vai além do óbvio? | Valor × stage | Regras razoáveis sem validação | Prob × valor × urgência, backtest temporal vs. baselines, incerteza declarada, achados dos dados incorporados (sobrevivência, conta ausente) |
| C3 | O vendedor (não-técnico) consegue usar e entender? | Tabela crua | Score + motivo genérico | Top N com reason codes em linguagem de vendedor, próxima ação, confiança visível |
| C4 | A interface ajuda a tomar decisão ou só mostra dados? | Dashboard de KPIs | Ranking filtrável | Responde "o que faço hoje?", visão por persona, deals em risco, exportável |
| C5 | O código é limpo o suficiente pra outro dev dar manutenção? | Notebook monolítico | Scripts organizados | Pacote testado, regras puras, UI fina, lint limpo, lock de dependências |
| C6 | Documentação: setup, lógica, limitações | Ausente/parcial | Presente mas genérica | Setup verificado, lógica com números, limitações honestas e específicas |
| C7 | Process log: iteração e julgamento | 1 prompt → 1 resposta | Narrativa sem erros da IA | Decisões datadas, ≥1 erro da IA corrigido com evidência, o que só o humano fez |
| C8 | Distância do baseline | Indistinguível | Alguns diferenciais | Um avaliador que viu o baseline reconhece imediatamente julgamento humano |

## Sinais de baseline (contam zero como diferencial)

Score = valor × peso por stage; "features óbvias" listadas na dica do brief sem análise; Streamlit com `st.dataframe` ordenado; limitações "precisaria de mais dados"; process log narrando prompts sem conflito; uso de `today()`; ignorar deals sem conta; random split; nenhum baseline comparado.

## Sinais de julgamento humano (contam)

Achados contra-intuitivos verificados nos dados e usados no produto; decisão explícita de não fazer algo; baseline batido com número; erro da IA pego e corrigido; reason codes escritos na voz do vendedor; consciência do snapshot temporal; cobertura para 68% de deals sem conta; teste que impede regressão de leakage; UI pensada por persona.

## Calibração adicional da rubrica

**Mínimo esperado (não conta como diferencial):** soma ponderada de 4–7 fatores; UI com breakdown + frase + "próxima ação"; filtros por vendedor/manager/região; os achados 63% win rate, 68% sem conta, GTXPro, 14 vs 57 dias, 138 dias, referência 31/12/2017; "explicabilidade > caixa-preta" como justificativa para não validar nada; visão por papel.

**Diferencial real:** walk-forward com baselines explícitos e IC (bater "mais novo primeiro" ou explicar por que não); testes anti-leakage no pytest; hipóteses antes dos dados com refutações; erros da IA com causa-raiz; pontuar deals sem conta; ações persistidas que realimentam o score; controle as-of na UI; pipeline reproduzível com artefatos versionados e execução agendada; API com OpenAPI completo; hooks reais versionados; auditor cego que derrubou algo.

**Derruba nota:** node_modules/venv/.venv no diff; arquivos fora da pasta (inclusive `.gitignore` da raiz); process log só narrativo ou em link externo; um commit gigante; dados sintéticos; setup que exige chave de API ou infra externa; duas datas de referência; fatores que não discriminam; chamar regras de "IA".

**Risco específico desta submissão:** Spark e Docker como pré-requisitos. Exigir caminho curto (`docker compose up` abre UI + API com artefatos commitados) e caminho completo (pipeline com JDK), ambos verificados em ambiente limpo.
