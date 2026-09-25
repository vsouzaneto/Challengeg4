import pandas as pd
import numpy as np
import json
import os

data_dir = r'C:\Users\JulianoAnanias\.gemini\antigravity\scratch\g4-challenge\data'

acc = pd.read_csv(os.path.join(data_dir, 'accounts.csv'))
prod = pd.read_csv(os.path.join(data_dir, 'products.csv'))
teams = pd.read_csv(os.path.join(data_dir, 'sales_teams.csv'))
pipe = pd.read_csv(os.path.join(data_dir, 'sales_pipeline.csv'))

# Tratamentos iniciais
pipe['engage_date'] = pd.to_datetime(pipe['engage_date'], errors='coerce')
pipe['close_date'] = pd.to_datetime(pipe['close_date'], errors='coerce')
max_dataset_date = pipe['close_date'].max()

# Ajuste preço GTXPro
closed = pipe[pipe['deal_stage'].isin(['Won', 'Lost'])].copy()
gtxpro_avg = closed[(closed['product'] == 'GTXPro') & (closed['deal_stage'] == 'Won')]['close_value'].mean()

prod_dict = {}
for _, row in prod.iterrows():
    p = row['product']
    price = row['sales_price']
    if pd.isna(price) and p == 'GTXPro':
        price = round(gtxpro_avg, 2)
    prod_dict[p] = {
        'product': p,
        'series': row['series'],
        'sales_price': float(price) if pd.notna(price) else 0.0
    }

# Median days to win per product
won_deals = pipe[pipe['deal_stage'] == 'Won'].copy()
won_deals['days_to_win'] = (won_deals['close_date'] - won_deals['engage_date']).dt.days
prod_median_days = won_deals.groupby('product')['days_to_win'].median().to_dict()
prod_win_rate = closed.groupby('product')['deal_stage'].apply(lambda x: (x == 'Won').mean()).to_dict()
prod_avg_ticket = won_deals.groupby('product')['close_value'].mean().to_dict()

# Adicionar métricas aos produtos
for p in prod_dict:
    prod_dict[p]['median_days_won'] = float(prod_median_days.get(p, 50.0))
    prod_dict[p]['win_rate'] = float(prod_win_rate.get(p, 0.63))
    prod_dict[p]['avg_won_ticket'] = float(prod_avg_ticket.get(p, prod_dict[p]['sales_price']))

# Métricas históricas de vendedores
agent_stats = closed.groupby('sales_agent').agg(
    total_closed=('deal_stage', 'count'),
    win_rate=('deal_stage', lambda x: (x == 'Won').mean()),
    avg_ticket=('close_value', lambda x: x[closed.loc[x.index, 'deal_stage'] == 'Won'].mean())
).to_dict('index')

# Histórico de contas (para força do relacionamento)
acc_history = {}
for acc_name, group in won_deals.groupby('account'):
    acc_history[acc_name] = {
        'won_count': int(len(group)),
        'total_revenue': float(group['close_value'].sum()),
        'products_bought': list(group['product'].unique()),
        'last_won_date': group['close_date'].max().strftime('%Y-%m-%d') if pd.notna(group['close_date'].max()) else None
    }

# Taxa de conversão por produto x setor
merged_closed = closed.merge(acc, on='account', how='left')
cross_prod_sector = merged_closed.groupby(['product', 'sector'])['deal_stage'].apply(lambda x: (x == 'Won').mean()).to_dict()

# Merge geral no pipeline
pipe_full = pipe.merge(acc, on='account', how='left')
pipe_full = pipe_full.merge(teams, on='sales_agent', how='left')

deals_list = []
for _, r in pipe_full.iterrows():
    p_name = r['product']
    p_info = prod_dict.get(p_name, {'median_days_won': 50.0, 'win_rate': 0.63, 'sales_price': 1000.0, 'series': 'Standard', 'avg_won_ticket': 1000.0})
    stage = r['deal_stage']
    is_active = stage in ['Engaging', 'Prospecting']
    
    # Calcular dias de engajamento
    if pd.notna(r['close_date']) and pd.notna(r['engage_date']):
        days_engage = int((r['close_date'] - r['engage_date']).days)
    elif pd.notna(r['engage_date']):
        days_engage = int((max_dataset_date - r['engage_date']).days)
    else:
        days_engage = 0
        
    median_days = p_info['median_days_won']
    relative_age = round(days_engage / median_days, 2) if median_days > 0 and pd.notna(r['engage_date']) else 0.0
    
    # 1. Valor esperado de referência: ticket médio dos ganhos × taxa histórica
    expected_ref_val = round(p_info['avg_won_ticket'] * p_info['win_rate'], 2)
    
    # 3. Aderência produto x setor
    sector_name = r['sector'] if pd.notna(r['sector']) else None
    prod_sector_adh = float(cross_prod_sector.get((p_name, sector_name), p_info['win_rate']))
    
    # 4 & 5. Força do relacionamento & Recompra
    acc_name = r['account'] if pd.notna(r['account']) else None
    acc_rel = acc_history.get(acc_name, None)
    if acc_rel:
        rel_strength = {
            'previous_wins': acc_rel['won_count'],
            'total_revenue': acc_rel['total_revenue'],
            'repurchase_type': 'Recompra' if p_name in acc_rel['products_bought'] else 'Expansão'
        }
    else:
        rel_strength = {
            'previous_wins': 0,
            'total_revenue': 0.0,
            'repurchase_type': 'Novo Negócio / Desconhecido'
        }
        
    # Classificação de FILA DE AÇÃO REVOPS
    # 1. Qualificar: ativos sem conta identificada
    # 2. Revisar continuidade: Engaging com idade relativa >= 2.0 (ultrapassa 2x ciclo mediano)
    # 3. Agir hoje: idade relativa no sweet-spot crítico (0.8 a 1.5) e ticket alto OU produto de alta conversão
    # 4. Avançar negociação: demais deals ativos regulares
    action_queue = 'Fechado'
    if is_active:
        if pd.isna(acc_name) or str(acc_name).strip() == '':
            action_queue = 'Qualificar'
        elif stage == 'Engaging' and relative_age >= 2.0:
            action_queue = 'Revisar Continuidade'
        elif stage == 'Engaging' and (p_name in ['GTK 500', 'GTX Plus Pro'] or relative_age >= 1.0):
            action_queue = 'Agir Hoje'
        else:
            action_queue = 'Avançar Negociação'
            
    # Cálculo de Lead Score (0 - 100)
    # Dimensões:
    # 1. Potencial Financeiro (25%)
    # 2. Conta & Setor (20%)
    # 3. Timing & Ciclo (25%)
    # 4. Agente de Vendas (15%)
    # 5. Relacionamento / Recompra (15%)
    
    # Score Financeiro (0-100)
    ref_price = p_info['sales_price']
    if ref_price >= 20000:
        score_val = 100
    elif ref_price >= 5000:
        score_val = 85
    elif ref_price >= 3000:
        score_val = 70
    elif ref_price >= 1000:
        score_val = 55
    elif ref_price >= 500:
        score_val = 40
    else:
        score_val = 25
        
    # Score Conta/Setor (0-100)
    if pd.isna(acc_name):
        score_acc = 20 # penalizado fortemente por falta de conta
    else:
        base_acc = 60
        if sector_name in ['marketing', 'entertainment', 'software']:
            base_acc += 20
        if rel_strength['previous_wins'] > 0:
            base_acc += 20
        score_acc = min(base_acc, 100)
        
    # Score Timing (0-100)
    if stage == 'Prospecting':
        score_time = 45 # ainda frio
    else:
        if relative_age < 0.3:
            score_time = 75 # início do engajamento
        elif relative_age <= 1.2:
            score_time = 95 # sweet spot de conversão
        elif relative_age < 2.0:
            score_time = 65 # esquentando demais
        else:
            score_time = 30 # deal estagnado / risco
            
    # Score Vendedor (0-100)
    agent_info = agent_stats.get(r['sales_agent'], {'win_rate': 0.63})
    score_agent = round(agent_info['win_rate'] * 100, 1)
    
    # Score Relacionamento (0-100)
    if rel_strength['previous_wins'] >= 3:
        score_rel = 100
    elif rel_strength['previous_wins'] >= 1:
        score_rel = 80
    elif pd.notna(acc_name):
        score_rel = 50
    else:
        score_rel = 15
        
    final_score = round(
        (score_val * 0.25) +
        (score_acc * 0.20) +
        (score_time * 0.25) +
        (score_agent * 0.15) +
        (score_rel * 0.15)
    )
    
    tier = 'Hot' if final_score >= 75 else ('Warm' if final_score >= 50 else 'Cold')
    
    deals_list.append({
        'id': r['opportunity_id'],
        'agent': r['sales_agent'],
        'manager': r['manager'] if pd.notna(r['manager']) else 'Sem Manager',
        'office': r['regional_office'] if pd.notna(r['regional_office']) else 'Sem Escritório',
        'product': p_name,
        'series': p_info['series'],
        'sales_price': p_info['sales_price'],
        'account': acc_name,
        'has_account': bool(pd.notna(acc_name)),
        'sector': sector_name,
        'revenue': float(r['revenue']) if pd.notna(r['revenue']) else None,
        'employees': int(r['employees']) if pd.notna(r['employees']) else None,
        'year_est': int(r['year_established']) if pd.notna(r['year_established']) else None,
        'stage': stage,
        'is_active': is_active,
        'engage_date': r['engage_date'].strftime('%Y-%m-%d') if pd.notna(r['engage_date']) else None,
        'close_date': r['close_date'].strftime('%Y-%m-%d') if pd.notna(r['close_date']) else None,
        'close_value': float(r['close_value']) if pd.notna(r['close_value']) else None,
        'days_engage': days_engage,
        'relative_age': relative_age,
        'median_cycle_days': median_days,
        'expected_ref_val': expected_ref_val,
        'action_queue': action_queue,
        'score': final_score,
        'tier': tier,
        'score_breakdown': {
            'value': score_val,
            'account': score_acc,
            'timing': score_time,
            'agent': round(score_agent),
            'relationship': score_rel
        },
        'relationship': rel_strength
    })

print(f"Total deals processados: {len(deals_list)}")
active_count = sum(1 for d in deals_list if d['is_active'])
print(f"Deals ativos: {active_count}")
from collections import Counter
queue_counts = Counter(d['action_queue'] for d in deals_list if d['is_active'])
print("Filas de ação nos ativos:", queue_counts)

# Salvar json de saída
out_file = r'C:\Users\JulianoAnanias\.gemini\antigravity\scratch\g4-challenge\pipeline_processed.json'
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump({
        'metadata': {
            'total_deals': len(deals_list),
            'active_deals': active_count,
            'last_date': max_dataset_date.strftime('%Y-%m-%d'),
            'products': prod_dict,
            'queue_summary': dict(queue_counts)
        },
        'deals': deals_list
    }, f, ensure_ascii=False)

print(f"Salvo em {out_file} com sucesso!")
