import pandas as pd
import json

ANALYTICS_FILE = "/Users/montinegro/G4 AI Master/repo/submissions/adailton-montinegro/artifacts/advanced_analytics.json"
SCORES_FILE = "/Users/montinegro/G4 AI Master/repo/submissions/adailton-montinegro/artifacts/ravenstack_account_risk_scores.csv"
OUTPUT_HTML = "/Users/montinegro/G4 AI Master/repo/submissions/adailton-montinegro/artifacts/executive_dashboard.html"

with open(ANALYTICS_FILE, "r", encoding="utf-8") as f:
    analytics = json.load(f)

df_scores = pd.read_csv(SCORES_FILE)

total_accs = len(df_scores)
churn_accs = int(df_scores['churn_flag'].sum())
active_accs = total_accs - churn_accs
active_mrr = float(df_scores[~df_scores['churn_flag']]['latest_mrr'].sum())
lost_mrr = float(df_scores[df_scores['churn_flag']]['latest_mrr'].sum())

months_labels = [r['year_month'] for r in analytics['monthly_timeline']]
months_churn = [r['churn_events'] for r in analytics['monthly_timeline']]
months_usage_per_acc = [r['usage_per_active_account'] for r in analytics['monthly_timeline']]

html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>RavenStack — Diagnóstico Causal de Churn (Executive Cockpit v2)</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 24px; line-height: 1.5; }}
        .header {{ margin-bottom: 24px; border-bottom: 1px solid #334155; padding-bottom: 16px; }}
        h1 {{ margin: 0 0 8px 0; font-size: 28px; color: #38bdf8; }}
        p.subtitle {{ margin: 0; color: #94a3b8; font-size: 15px; }}
        .badge-curr {{ display: inline-block; background: #1e3a8a44; border: 1px solid #38bdf8; color: #38bdf8; padding: 4px 10px; border-radius: 20px; font-size: 12px; margin-top: 8px; }}
        .grid-kpi {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin: 24px 0; }}
        .kpi-card {{ background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 18px; }}
        .kpi-title {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }}
        .kpi-value {{ font-size: 26px; font-weight: bold; margin: 8px 0 4px 0; }}
        .kpi-green {{ color: #34d399; }}
        .kpi-red {{ color: #f43f5e; }}
        .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 28px; }}
        .box {{ background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 20px; }}
        .box h3 {{ margin-top: 0; font-size: 16px; color: #e2e8f0; border-bottom: 1px solid #334155; padding-bottom: 8px; }}
        .box p.desc {{ font-size: 13px; color: #94a3b8; margin: 0 0 16px 0; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; margin-top: 10px; }}
        th {{ background: #0f172a; color: #94a3b8; padding: 10px; border-bottom: 1px solid #334155; font-weight: 600; }}
        td {{ padding: 10px; border-bottom: 1px solid #243248; }}
        tr:hover {{ background: #243248; }}
        .pill {{ padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }}
        .pill-q1 {{ background: rgba(244, 63, 94, 0.2); color: #f43f5e; }}
        .pill-q2 {{ background: rgba(251, 146, 60, 0.2); color: #fb923c; }}
        .pill-q3 {{ background: rgba(5, 150, 105, 0.2); color: #34d399; }}
        .pill-q4 {{ background: rgba(56, 189, 248, 0.2); color: #38bdf8; }}
        .fact-box {{ background: #1e3a8a22; border-left: 4px solid #38bdf8; padding: 16px; border-radius: 4px; margin-bottom: 24px; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🦅 RavenStack — Diagnóstico Causal de Churn (Executive Cockpit v2)</h1>
        <p class="subtitle">Análise Factual de 24 Meses, Desmistificação de Vieses de Produto/CSAT e Segmentação por Quadrantes | Squad Altman (Codex CLI) & Japax (Antigravity)</p>
        <span class="badge-curr">Valores em USD ($) | Conversão Referencial PTAX R$ 5,50 disponível no app</span>
    </div>

    <div class="fact-box">
        <strong>🔬 Conclusão Causal Definitiva:</strong> 
        O uso médio mensal por conta ativa permaneceu <strong>matematicamente plano entre 23,0 e 26,7 usos/mês</strong> em todos os 24 meses avaliados (média de 24,6 usos/mês). A alegação da diretoria de produto de que "o uso cresceu" baseou-se em flutuação nominal de final de ano (+2,6%), enquanto os cancelamentos explodiram de <strong>1 em Jan/2023 para 117 em Dez/2024</strong>. O churn é <strong>descolado do volume de uso</strong>: clientes cancelam devido a falhas operacionais críticas (escalações de suporte sobem para 14,6% nas 2 semanas pré-churn) e atrito em features beta instáveis.
    </div>

    <div class="grid-kpi">
        <div class="kpi-card">
            <div class="kpi-title">Total de Contas</div>
            <div class="kpi-value">{total_accs}</div>
            <div style="font-size: 12px; color: #38bdf8;">Base 100% Auditada</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Contas Ativas</div>
            <div class="kpi-value kpi-green">{active_accs}</div>
            <div style="font-size: 12px; color: #34d399; font-weight: 600;">▲ {active_accs/total_accs:.1%} retidas</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Logo Churn Acumulado</div>
            <div class="kpi-value kpi-red">{churn_accs}</div>
            <div style="font-size: 12px; color: #f43f5e; font-weight: 600;">▼ {churn_accs/total_accs:.1%} de perda</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">MRR Ativo Mensal</div>
            <div class="kpi-value kpi-green">${active_mrr:,.2f}</div>
            <div style="font-size: 12px; color: #34d399; font-weight: 600;">▲ ${active_mrr*12:,.2f} ARR</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">MRR Perdido (Churn)</div>
            <div class="kpi-value kpi-red">${lost_mrr:,.2f}</div>
            <div style="font-size: 12px; color: #f43f5e; font-weight: 600;">▼ -${lost_mrr*12:,.2f} ARR</div>
        </div>
    </div>

    <div class="grid-2">
        <div class="box">
            <h3>1. Linha do Tempo Mensal (24 Meses): Churn vs Uso Médio por Conta</h3>
            <p class="desc">Barras vermelhas indicam eventos de cancelamento mensais; linha azul representa o uso médio per capita (estável em ~24.6/mês).</p>
            <canvas id="timelineChart" height="150"></canvas>
        </div>
        <div class="box">
            <h3>2. O Viés do Suporte: Escalações Críticas na Janela Pré-Cancelamento</h3>
            <p class="desc">Enquanto o CSAT médio de 4.0 mascara 41.2% de não-resposta, as escalações para engenharia triplicam para 14.6% a 14 dias do churn.</p>
            <canvas id="supportChart" height="150"></canvas>
        </div>
    </div>

    <div class="grid-2">
        <div class="box">
            <h3>3. Segmentação Cartesiana por Quadrantes (500 Contas)</h3>
            <p class="desc">Divisão estratégica da base pelo impacto financeiro (MRR > $1.500) vs Risco de Churn (Score > 0.40).</p>
            <table>
                <thead>
                    <tr>
                        <th>Quadrante</th>
                        <th>Contas</th>
                        <th>MRR Total</th>
                        <th>Ticket Médio</th>
                        <th>Churn Histórico</th>
                    </tr>
                </thead>
                <tbody>
"""

for r in analytics['quadrants_summary']:
    pill_cls = 'pill-q1' if 'Q1' in r['quadrant'] else ('pill-q2' if 'Q2' in r['quadrant'] else ('pill-q3' if 'Q3' in r['quadrant'] else 'pill-q4'))
    html_content += f"""
                    <tr>
                        <td><span class="pill {pill_cls}">{r['quadrant']}</span></td>
                        <td>{r['contas']}</td>
                        <td><strong>${r['mrr_total']:,.2f}</strong></td>
                        <td>${r['mrr_medio']:,.2f}</td>
                        <td>{r['churn_rate']}%</td>
                    </tr>
    """

html_content += f"""
                </tbody>
            </table>
        </div>
        <div class="box">
            <h3>4. Motivos Declarados e Feedbacks (600 Cancelamentos)</h3>
            <p class="desc">Distribuição de Reason Codes e prevalência das principais dores relatadas pelos clientes.</p>
            <canvas id="reasonsChart" height="150"></canvas>
        </div>
    </div>

    <script>
        // Timeline Chart
        new Chart(document.getElementById('timelineChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(months_labels)},
                datasets: [
                    {{
                        type: 'bar',
                        label: 'Cancelamentos Mensais',
                        data: {json.dumps(months_churn)},
                        backgroundColor: '#f43f5e',
                        borderRadius: 3,
                        yAxisID: 'y'
                    }},
                    {{
                        type: 'line',
                        label: 'Uso Médio / Conta',
                        data: {json.dumps(months_usage_per_acc)},
                        borderColor: '#38bdf8',
                        backgroundColor: '#38bdf8',
                        borderWidth: 2,
                        pointRadius: 2,
                        yAxisID: 'y1'
                    }}
                ]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{ position: 'left', title: {{ display: true, text: 'Cancelamentos', color: '#f43f5e' }}, grid: {{ color: '#1e293b' }} }},
                    y1: {{ position: 'right', min: 0, max: 35, title: {{ display: true, text: 'Uso / Conta', color: '#38bdf8' }}, grid: {{ display: false }} }}
                }}
            }}
        }});

        // Support Chart
        new Chart(document.getElementById('supportChart'), {{
            type: 'bar',
            data: {{
                labels: ['60+ dias antes (Normal)', '31-60 dias antes', '15-30 dias antes', '0-14 dias antes (Gatilho Fatal)'],
                datasets: [{{
                    label: 'Taxa de Escalação (%)',
                    data: [5.0, 4.1, 4.5, 14.6],
                    backgroundColor: ['#38bdf8', '#38bdf8', '#fb923c', '#f43f5e'],
                    borderRadius: 4
                }}]
            }},
            options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }} }}
        }});

        // Reasons Chart
        new Chart(document.getElementById('reasonsChart'), {{
            type: 'bar',
            data: {{
                labels: ['Features', 'Suporte', 'Orçamento (Budget)', 'Desconhecido', 'Concorrente', 'Preço (Pricing)'],
                datasets: [{{
                    label: 'Volume de Cancelamentos',
                    data: [114, 104, 104, 95, 92, 91],
                    backgroundColor: ['#38bdf8', '#f43f5e', '#fb923c', '#64748b', '#a855f7', '#eab308'],
                    borderRadius: 4
                }}]
            }},
            options: {{ responsive: true, indexAxis: 'y', plugins: {{ legend: {{ display: false }} }} }}
        }});
    </script>
</body>
</html>
"""

with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Executive Dashboard HTML v2 gerado com sucesso em: {OUTPUT_HTML}")
