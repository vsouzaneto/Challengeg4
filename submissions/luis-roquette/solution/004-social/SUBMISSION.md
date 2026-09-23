# Submissão — Luis Fernando Roquette — Challenge 004

## Sobre mim

- **Nome:** Luis Fernando Roquette
- **LinkedIn:** [linkedin.com/in/luisroquette](https://br.linkedin.com/in/luisroquette)
- **Challenge escolhido:** 004 — Estratégia Social Media

---

## Executive Summary

Analisei 52.214 posts de cinco plataformas e construí um cockpit local que converte evidência em decisão auditável. Nenhum contexto orgânico sustentou superioridade, e a cobertura comparável de patrocínio foi insuficiente para justificar escala ou ROI. Os dados também não permitem eleger com segurança um perfil de audiência. Recomendo um programa controlado de 30 dias, preservando o mix fora do teste e coletando custos e conversões.

---

## Solução

### Abordagem

Pesquisei o dataset e frameworks antes da SPEC, conduzi descoberta socrática, separei motor Pandas, persistência SQLite e interface Streamlit e reproduzi análise, exports e decisões com CSV real.

### Resultados / Findings

- Nenhum dos 20 contextos passou simultaneamente amostra, materialidade, estabilidade e força.
- Patrocínio teve somente 1,56% de cobertura comparável e não possui custos ou conversões para cálculo de ROI.
- Idade, gênero e localização tiveram 0% de cobertura em comparações controladas.
- [Cockpit, método e setup](README.md).

### Recomendações

1. Validar por 30 dias o melhor contexto elegível sem alterar o restante do mix.
2. Não escalar patrocínio sem custos, conversões e evidência estável.
3. Instrumentar audiência antes de criar personas ou segmentar investimento.

### Limitações

Engajamento não é ROI, views não são alcance único e os dados terminam em 2025. A atualização é manual e não há publicação ou investimento automático.

---

## Process Log — Como usei IA

### Ferramentas usadas

| Ferramenta | Para que usou |
|---|---|
| OpenAI Codex | Pesquisa, descoberta, SDD, implementação e regressões |
| Claude Code | Estruturação inicial dos artefatos de especificação |
| Chrome automatizado | Validação da interface, persistência e downloads |

### Workflow

1. Reli o briefing, pesquisei alternativas e conduzi 24 ondas socráticas.
2. Revisei SPEC e plano até duas passadas sem melhoria substancial.
3. Construí em fases e validei código, CSV, navegador e evidências visuais.

### Onde a IA errou e como corrigi

A IA confundiu seleções editoriais com a fila do motor, normalizou sobre candidatos incompletos e deixou controles CSV escaparem da neutralização. Corrigi cada causa na camada de origem e adicionei regressões.

### O que eu adicionei que a IA sozinha não faria

Preservei o Gestor de Social Media como operador principal e escolhi um MVP manual, explicável e auditável em vez de automações prematuras.

---

## Evidências

- [x] [Diário integral](../../process-log/004-social.md)
- [x] [Pesquisa](../../research/004-social.md)
- [x] [Análise executiva](analysis.md)
- [x] [Evidências reproduzíveis](evidence.csv)
- [x] [Provas visuais](../../process-log/evidence/004/)

---

_Submissão enviada em: 22/09/2026_
