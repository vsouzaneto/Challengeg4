import pandas as pd
import json

SCORES_FILE = "/Users/montinegro/G4 AI Master/repo/submissions/adailton-montinegro/artifacts/ravenstack_account_risk_scores.csv"
OUTPUT_HTML = "/Users/montinegro/G4 AI Master/repo/submissions/adailton-montinegro/artifacts/executive_dashboard.html"

df = pd.read_csv(SCORES_FILE)

# Resumos
total_accs = len(df)
churn_accs = int(df['churn_flag'].sum())
active_accs = total_accs - churn_accs
active_mrr = float(df[~df['churn_flag']]['latest_mrr'].sum())
lost_mrr = float(df[df['churn_flag']]['latest_mrr'].sum())

html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>RavenStack — Diagnóstico de Churn Executivo</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 24px; }}
        .header {{ margin-bottom: 24px; }}
        h1 {{ margin: 0 0 8px 0; font-size: 28px; color: #38bdf8; }}
        p.subtitle {{ margin: 0; color: #94a3b8; font-size: 15px; }}
        .grid-kpi {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 28px; }}
        .kpi-card {{ background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 16px; }}
        .kpi-title {{ font-size: 13px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }}
        .kpi-value {{ font-size: 26px; font-weight: bold; margin: 8px 0 4px 0; color: #f1f5f9; }}
        .kpi-sub {{ font-size: 12px; color: #38bdf8; }}
        .kpi-danger {{ color: #f43f5e; }}
        .grid-charts {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 28px; }}
        .chart-box {{ background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 20px; }}
        .chart-box h3 {{ margin-top: 0; font-size: 16px; color: #e2e8f0; }}
        .table-box {{ background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 20px; overflow-x: auto; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }}
        th {{ background: #0f172a; color: #94a3b8; padding: 10px; border-bottom: 1px solid #334155; }}
        td {{ padding: 10px; border-bottom: 1px solid #1e293b; }}
        tr:hover {{ background: #243248; }}
        .badge {{ padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }}
        .badge-crit {{ background: rgba(244, 63, 94, 0.2); color: #f43f5e; }}
        .badge-att {{ background: rgba(251, 146, 60, 0.2); color: #fb923c; }}
        .badge-ok {{ background: rgba(52, 211, 153, 0.2); color: #34d399; }}
        .insight-box {{ background: #1e3a8a22; border-left: 4px solid #38bdf8; padding: 14px; border-radius: 4px; margin-bottom: 24px; font-size: 14px; line-height: 1.5; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🦅 RavenStack — Diagnóstico de Churn & Cockpit Executivo</h1>
        <p class="subtitle">Investigação Causal, Decomposição de Paradoxo e Matriz Prescritiva | G4 AI Master</p>
    </div>

    <div class="insight-box">
        <strong>Síntese Causal para o CEO:</strong> O churn não aumentou por falta de uso — o uso atingiu a máxima histórica em 2024-Q4 (32.227 eventos) impulsionado por novas contas de curta retenção (67.5% da coorte Q4 cancelou em semanas). O CSAT de 4.0 é falso devido a 41.2% de não-resposta; o sinal predecessor real é a <strong>taxa de escalação de suporte, que salta de 4.5% para 14.6% nas duas semanas anteriores ao cancelamento</strong>.
    </div>

    <div class="grid-kpi">
        <div class="kpi-card">
            <div class="kpi-title">Total de Contas</div>
            <div class="kpi-value">{total_accs}</div>
            <div class="kpi-sub">500 contas auditadas</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Contas Ativas</div>
            <div class="kpi-value">{active_accs}</div>
            <div class="kpi-sub">{active_accs/total_accs:.1%} da base retida</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Logo Churn Total</div>
            <div class="kpi-value kpi-danger">{churn_accs}</div>
            <div class="kpi-sub kpi-danger">{churn_accs/total_accs:.1%} churn acumulado</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">MRR Ativo</div>
            <div class="kpi-value">${active_mrr:,.0f}</div>
            <div class="kpi-sub">Receita mensal corrente</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">MRR Perdido (Churn)</div>
            <div class="kpi-value kpi-danger">${lost_mrr:,.0f}</div>
            <div class="kpi-sub kpi-danger">-${lost_mrr*12:,.0f} ARR sangrado</div>
        </div>
    </div>

    <div class="grid-charts">
        <div class="chart-box">
            <h3>Evolução Trimestral: O Ponto de Inflexão em 2024-Q4</h3>
            <canvas id="churnTrendChart"></canvas>
        </div>
        <div class="chart-box">
            <h3>O Sinal Crítico do Suporte: Escalações Pré-Churn</h3>
            <canvas id="supportEscChart"></canvas>
        </div>
    </div>

    <div class="grid-charts">
        <div class="chart-box">
            <h3>Taxa de Churn por Vertical de Indústria</h3>
            <canvas id="industryChart"></canvas>
        </div>
        <div class="chart-box">
            <h3>Importância Relativa de Features no Modelo Preditivo</h3>
            <canvas id="featuresChart"></canvas>
        </div>
    </div>

    <div class="table-box">
        <h3>Top 10 Contas Ativas em Maior Risco de Churn (Prescrição CS)</h3>
        <table>
            <thead>
                <tr>
                    <th>Conta</th>
                    <th>Vertical</th>
                    <th>Plano</th>
                    <th>MRR</th>
                    <th>Score Risco</th>
                    <th>Classificação</th>
                    <th>Ação Prescritiva Recomendada</th>
                </tr>
            </thead>
            <tbody>
"""

top_active_risk = df[~df['churn_flag']].sort_values(by='churn_risk_score', ascending=False).head(10)
for _, r in top_active_risk.iterrows():
    badge_cls = 'badge-crit' if r['risk_tier'] == 'Crítico (Alto Risco)' else 'badge-att'
    html_content += f"""
                <tr>
                    <td><strong>{r['account_name']}</strong> ({r['account_id']})</td>
                    <td>{r['industry']}</td>
                    <td>{r['plan_tier']}</td>
                    <td>${r['latest_mrr']:,.2f}</td>
                    <td><strong>{r['churn_risk_score']:.2f}</strong></td>
                    <td><span class="badge {badge_cls}">{r['risk_tier']}</span></td>
                    <td>{r['recommended_action']}</td>
                </tr>
    """

html_content += """
            </tbody>
        </table>
    </div>

    <script>
        // Chart 1: Churn Trend
        new Chart(document.getElementById('churnTrendChart'), {
            type: 'bar',
            data: {
                labels: ['2023-Q1', '2023-Q2', '2023-Q3', '2023-Q4', '2024-Q1', '2024-Q2', '2024-Q3', '2024-Q4'],
                datasets: [{
                    label: 'Eventos de Churn',
                    data: [6, 11, 19, 37, 54, 92, 130, 251],
                    backgroundColor: '#f43f5e',
                    borderRadius: 4
                }]
            },
            options: { responsive: true, plugins: { legend: { display: false } } }
        });

        // Chart 2: Support Escalation Pre-Churn
        new Chart(document.getElementById('supportEscChart'), {
            type: 'bar',
            data: {
                labels: ['60+ dias antes', '31-60 dias antes', '15-30 dias antes', '0-14 dias antes (Gatilho)'],
                datasets: [{
                    label: 'Taxa de Escalação (%)',
                    data: [5.0, 4.1, 4.5, 14.6],
                    backgroundColor: ['#38bdf8', '#38bdf8', '#fb923c', '#f43f5e'],
                    borderRadius: 4
                }]
            },
            options: { responsive: true, plugins: { legend: { display: false } } }
        });

        // Chart 3: Industry
        new Chart(document.getElementById('industryChart'), {
            type: 'bar',
            data: {
                labels: ['DevTools', 'FinTech', 'HealthTech', 'EdTech', 'Cybersecurity'],
                datasets: [{
                    label: 'Taxa de Churn (%)',
                    data: [31.0, 22.3, 21.9, 16.5, 16.0],
                    backgroundColor: ['#f43f5e', '#38bdf8', '#38bdf8', '#34d399', '#34d399'],
                    borderRadius: 4
                }]
            },
            options: { responsive: true, indexAxis: 'y', plugins: { legend: { display: false } } }
        });

        // Chart 4: Features
        new Chart(document.getElementById('featuresChart'), {
            type: 'bar',
            data: {
                labels: ['Taxa Erro Geral', 'Tempo Resolução Tickets', 'First Response Time', 'Uso Features Beta', 'Uso por Licença'],
                datasets: [{
                    label: 'Importância (%)',
                    data: [8.71, 6.34, 6.25, 6.19, 5.41],
                    backgroundColor: '#38bdf8',
                    borderRadius: 4
                }]
            },
            options: { responsive: true, indexAxis: 'y', plugins: { legend: { display: false } } }
        });
    </script>
</body>
</html>
"""

with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Relatório HTML interativo gerado com sucesso em: {OUTPUT_HTML}")
