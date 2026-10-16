# SPEC-001 — RavenStack Intelligence (Felipe)

## Objetivo

Diagnóstico executivo de churn com **5 tabelas**, tese **porta giratória**, fila CS priorizada por MRR × risco e **Command Center** com filtros globais.

## Entradas

- `data/ravenstack_*.csv` (5 arquivos)
- Pipeline: `solution/run_analysis.py`

## Saídas obrigatórias

| Artefato | Uso |
|----------|-----|
| `outputs/account_master.csv` | Grão conta |
| `outputs/fila_cs_top50.csv` | Operação CS |
| `outputs/data_quality_summary.*` | Integridade cadastro vs eventos |
| `outputs/dashboard_bundle.json` | UI React |
| `reports/ceo_one_pager.md` | Board 5 min |
| `reports/data_quality_ceo.md` | Forense dados |
| `reports/model_and_limits.md` | Limites do modelo |

## UI (Command Center)

- KPIs filtráveis, gráficos com drill-down, fila CS (top 80)
- Card **Integridade dos dados**
- Drawer por conta (`?conta=<id>`, copiar ID)
- Recomendação #1 em destaque

## API opcional (localhost)

`python api_server.py` → `127.0.0.1:8766` — `/health`, `/kpis`, `/account/{id}`

## Validação

- `start.bat` (rápido) ou `start.bat --full` (pipeline + build + verify + pytest)
- `python verify_submission.py`

## Não-objetivos

- Deploy público sem auth
- Causalidade automática (ver `causality_register.md`)
