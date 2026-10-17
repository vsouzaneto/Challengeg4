# AI Master — Support Intelligence

Protótipo do Challenge 002 — Redesign de Suporte.

## Objetivo
Centralizar os quatro entregáveis do challenge em uma aplicação única:
1. Diagnóstico operacional
2. Proposta de automação com IA
3. Protótipo funcional
4. Process log

A camada `Data Quality & Audit` é transversal e impede o uso de métricas não sustentadas pelos datasets.

## Execução local
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abra `http://127.0.0.1:5000`.

## Dados
Coloque os CSVs originais em `data/raw/`. O endpoint `/api/audit` detecta e audita automaticamente os arquivos suportados.

Nenhum KPI é preenchido com dados fictícios.
