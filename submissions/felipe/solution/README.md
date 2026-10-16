# Solução técnica (RavenStack Intelligence)

| Item | Caminho |
|------|---------|
| Pipeline | `analytics/` · entry `run_analysis.py` |
| UI | `command-center/` → `npm run build` → `dist/` |
| Servidor | `serve_dashboard.py` → **127.0.0.1:8765** |
| Gate CE | `verify_submission.py` |

**Setup Windows completo:** `../start.bat`  
**Documentação:** `../docs/METODOLOGIA.md` · `../README.md`

Score de risco (0–100): eventos 30%, escalações 25%, canal event 15%, DevTools 10%, trial 10%, erros/uso 10% — `analytics/run_analysis.py` → `risk_score()`.
