# ADR 0002 — FastAPI + React em vez de Streamlit

**Status:** aceito · **Data:** 2026-09-23

## Contexto
A primeira versão da arquitetura previa Streamlit (rápido de construir, sem backend). O challenge valoriza uma ferramenta que o vendedor use de fato, e a entrega deve incluir uma API documentada (Swagger) e um frontend com o design system do G4.

## Decisão
Backend **FastAPI** (Python) servindo o parquet de scores via REST com OpenAPI 3.1 exemplar; frontend **React + Vite + TypeScript + Tailwind** consumindo a API com tipos gerados do OpenAPI. Entrega via **Docker Compose**.

## Alternativas
- Streamlit: mais rápido, mas UI limitada, sem API reutilizável, difícil aplicar design system e testar componentes.
- Next.js full-stack: uniria API e web em TS, mas o pipeline e o contrato `ScoredDeal` já vivem em Python (Pydantic → OpenAPI → TS é o caminho de menor atrito).

## Consequências
Mais peças e mais tempo de setup; em troca, contrato único do parquet ao navegador, Swagger como documentação viva, UI testável e fiel ao design system, e separação limpa entre calcular (pipeline), servir (API) e apresentar (web).
