# Arquitetura

## Objetivo
Transformar o dataset do Challenge 003 num sistema de priorização comercial utilizável dentro de um CRM real.

## Stack
- Odoo Community
- n8n
- ChatGPT
- Ambiente: https://g4.mftechsolutions.pt

## Fluxo
Dataset G4 → PRODUCTS → IMPORT / SYNC → Odoo Community → ENRICH / PRIORITIZE → FocusScore + prioridade + tags + atividades → WIN INTELLIGENCE

## Responsabilidades
**Odoo:** pipeline, oportunidades, prioridade, equipas, tags, atividades e deadlines.

**n8n:** importação, sincronização, enrichment, scoring, routing, atividades e análise Won/Lost.

**ChatGPT:** crítica de arquitetura, revisão de código, troubleshooting, análise de leakage e desenho estatístico.

## Read-only analytics
O workflow G4 — WIN INTELLIGENCE foi desenhado para ser read-only em relação ao Odoo. A análise histórica não modifica oportunidades, scores nem estados do CRM.
