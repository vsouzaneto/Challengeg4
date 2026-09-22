---
status: passing
canonical: false
area: frontend
created: 2026-09-21
last_updated: 2026-09-21
---

# SPEC-017 Rotas de sobre por challenge

Reverse da seção viva `http://localhost:3020/#about` (2026-09-21) e contrato das rotas que recontam essa seção com o README de cada pacote Databricks.

A home mantém `#about` (Wisconsin). Sobre no header deixa de apontar só para ela.

## Reverse — anatomia observada

A seção mora em `FeaturesSection`, `id="about"`, dentro da home.

| Bloco | O que a página faz |
| --- | --- |
| Sobrancelha | "Sobre" |
| Título | "A clareza da predição, / Sem chute." |
| Lista | Quatro faixas numeradas 01–04. Cada uma tem título, um parágrafo e um desenho animado (`deploy`, `ai`, `collab`, `security`). |

Não há seletor nem estatística. A história é uma orientação em quatro passos.

## Contrato das rotas

Cada challenge repete a seção: título em duas linhas, um parágrafo de enquadramento, quatro faixas com os mesmos desenhos. O texto sai do README do pacote (estrutura, ementa, como rodar, armadilha). Não usa a massa da Receita Federal.

| Menu | Challenge | Rota | README |
| --- | --- | --- | --- |
| Sobre | 001 churn | `/about-challenge-001` | `notebook-data-001-churn/README.md` |
| Sobre | 002 support | `/about-challenge-002` | `notebook-process-002-support/README.md` |
| Sobre | 003 lead | `/about-challenge-003` | `notebook-build-003-lead-scorer/README.md` |
| Sobre | 004 social | `/about-challenge-004` | `notebook-marketing-004-social/README.md` |

As quatro faixas são os labs, na ordem do README:

| # | Papel | Duração na ementa |
| --- | --- | --- |
| 01 | Ingestão CSV → Delta | 30 min |
| 02 | Assistant, só colunas reais | 30 min |
| 03 | Dashboard, o entregável | 40 min |
| 04 | Kernel Kaggle adaptado | 40 min |

Header: **Sobre** é dropdown. Opções `001 churn`, `002 support`, `003 lead`, `004 social`. Cada página também expõe `id="about"`.

## Verificação

- [x] Quatro rotas respondem 200 e contêm `id="about"`.
- [x] Header expõe `/about-challenge-001` … `/about-challenge-004`.
- [x] `/#about` continua na home.

## Notas

Href: `aboutPath` em `src/frontend/lib/research/stories.ts`. Texto: `src/frontend/lib/about/stories.ts`.
