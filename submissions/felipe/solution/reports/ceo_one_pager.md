# CEO — Uma página

**Pergunta:** Por que churn sobe se CSAT e uso estão ok?

**Resposta:** Vocês medem **eventos** (600) e reativações; o **churn líquido** são **110** contas (22%). **277** contas **ativas** já cancelaram antes (**US$ 665,190 MRR**) — CS vê contas vivas, board vê eventos.

**Três ações esta semana:** (1) KPI = líquido + MRR + reativação; (2) CS ligar fila top 50 (`cs_action_queue_top50.csv`); (3) cohort DevTools + canal event.

**Não culpar:** produto (uso 10.0 vs 10.0) nem CS (CSAT ~4).

**Detalhe:** `reports/executive_summary.md` · **App:** `python serve_dashboard.py` → http://127.0.0.1:8765
