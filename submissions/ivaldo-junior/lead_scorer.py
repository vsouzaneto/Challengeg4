import pandas as pd
import numpy as np
import os
from datetime import datetime

def load_and_merge_data(base_path: str = "./") -> pd.DataFrame:
    try:
        accounts = pd.read_csv(os.path.join(base_path, 'accounts.csv'))
        products = pd.read_csv(os.path.join(base_path, 'products.csv'))
        sales_teams = pd.read_csv(os.path.join(base_path, 'sales_teams.csv'))
        sales_pipeline = pd.read_csv(os.path.join(base_path, 'sales_pipeline.csv'))
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Erro ao carregar os ficheiros CSV: {e}. Confirme se os dados estão no diretório: {base_path}")

    # Tratamento e higienização robusta das colunas
    for df_temp in [accounts, products, sales_teams, sales_pipeline]:
        df_temp.columns = df_temp.columns.str.strip()
        # QA: Strip all string columns to prevent trailing spaces
        for col in df_temp.select_dtypes(include=['object']).columns:
            df_temp[col] = df_temp[col].astype(str).str.strip()
            
    # Tratamento dinâmico de stage vs deal_stage no pipeline ANTES dos merges
    if 'stage' in sales_pipeline.columns and 'deal_stage' not in sales_pipeline.columns:
        sales_pipeline.rename(columns={'stage': 'deal_stage'}, inplace=True)
        
    df = sales_pipeline.merge(accounts, on='account', how='left')
    df = df.merge(products, on='product', how='left')
    df = df.merge(sales_teams, on='sales_agent', how='left')
    
    # QA: Fill NaNs for safety
    df['close_value'] = df.get('close_value', pd.Series(dtype=float)).fillna(0)
    df['employees'] = df.get('employees', pd.Series(dtype=float)).fillna(0)
    df['revenue'] = df.get('revenue', pd.Series(dtype=float)).fillna(0)
    df['sector'] = df.get('sector', pd.Series(dtype=str)).fillna('Desconhecido')
    df['deal_stage'] = df.get('deal_stage', pd.Series(dtype=str)).fillna('Unknown')
    
    # Tratamento de datas
    df['created_on'] = pd.to_datetime(df['created_on'])
    if 'close_date' in df.columns:
        df['close_date'] = pd.to_datetime(df['close_date'])
        
    # O tratamento de 'stage' já foi feito acima no sales_pipeline
        
    return df

def calculate_historical_baselines(df: pd.DataFrame) -> dict:
    historico = df[df['deal_stage'].isin(['Won', 'Lost'])].copy()
    
    baselines = {
        'sector_win_rate': {},
        'product_win_rate': {},
        'global_win_rate': 0.5,
        'sector_avg_ticket': {}
    }
    
    if historico.empty:
        return baselines
        
    baselines['global_win_rate'] = (historico['deal_stage'] == 'Won').mean()
    
    # Ticket médio por setor
    won_history = historico[historico['deal_stage'] == 'Won']
    if not won_history.empty and 'close_value' in won_history.columns:
        baselines['sector_avg_ticket'] = won_history.groupby('sector')['close_value'].mean().to_dict()
    
    # Win rate por setor
    sector_stats = historico.groupby('sector')['deal_stage'].apply(lambda x: (x == 'Won').mean()).to_dict()
    baselines['sector_win_rate'] = sector_stats
    
    # Win rate por produto
    product_stats = historico.groupby('product')['deal_stage'].apply(lambda x: (x == 'Won').mean()).to_dict()
    baselines['product_win_rate'] = product_stats
    
    return baselines

def score_active_pipeline(df: pd.DataFrame, baselines: dict) -> pd.DataFrame:
    df_active = df[~df['deal_stage'].isin(['Won', 'Lost'])].copy()
    
    if df_active.empty:
        return df_active
        
    ref_date = df['created_on'].max()
    df_active['days_open'] = (ref_date - df_active['created_on']).dt.days
    df_active['days_open'] = df_active['days_open'].apply(lambda x: max(0, x))
    
    scores = []
    explicacoes = []
    sinais_list = []
    global_wr = baselines.get('global_win_rate', 0.5)
    
    for _, row in df_active.iterrows():
        score = 50 
        motivos = []
        riscos = []
        
        # 1. Maturidade do funil
        stage = row.get('deal_stage', '')
        if stage == 'Engaging':
            score += 20
            motivos.append("Estágio de negociação avançado (Engaging)")
        elif stage == 'Prospecting':
            score += 5
            motivos.append("Fase inicial (Prospecting)")
            
        # 2. Força do Segmento
        sector = row.get('sector', '')
        win_rate = baselines['sector_win_rate'].get(sector, global_wr)
        
        if win_rate > global_wr * 1.2:
            score += 15
            motivos.append(f"Setor forte ({win_rate:.0%} de conversão histórica)")
        elif win_rate < global_wr * 0.8:
            score -= 10
            riscos.append(f"Setor com baixo histórico de conversão ({win_rate:.0%})")
            
        # 3. Porte da conta (Employees)
        emp = row.get('employees', 0)
        if pd.notna(emp):
            if emp > 1000:
                score += 15
                motivos.append("Conta Enterprise (Elevado Potencial)")
            elif 250 <= emp <= 1000:
                score += 5
                motivos.append("Conta Mid-Market")
            elif emp < 50:
                score -= 5
                riscos.append("Conta Small Business")
                
        # 4. Decaimento Logarítmico por Estagnação
        dias = row['days_open']
        if dias <= 15:
            score += 10
            motivos.append(f"Oportunidade aquecida ({int(dias)} dias)")
        elif dias > 45:
            penalty = min(30, 10 * np.log1p(dias - 45))
            score -= penalty
            riscos.append(f"Lead estagnado há mais de {int(dias)} dias")
            
        score = max(0, min(100, score))
        scores.append(int(score))
        
        frase = ""
        if motivos:
            frase += "🟢 Fatores Fortes: " + " | ".join(motivos) + ". "
        if riscos:
            frase += "🔴 Atenção: " + " | ".join(riscos) + "."
            
        if not frase:
            frase = "⚪ Oportunidade em qualificação neutra."
            
        explicacoes.append(frase.strip())
        
        total_sinais = len(motivos) + len(riscos)
        if stage == 'Engaging':
            sinais_curtos = f"● Engaging | +{total_sinais - 1} sinais" if total_sinais > 1 else "● Engaging"
        else:
            sinais_curtos = f"● {stage} | +{total_sinais} sinais" if total_sinais > 0 else "● Regular"
        sinais_list.append(sinais_curtos)
        
    df_active['Lead Score'] = scores
    df_active['Explainability'] = explicacoes
    df_active['Sinais'] = sinais_list
    
    def get_priority(s):
        if s >= 70:
            return "🔥 Alta Prioridade"
        elif s >= 45:
            return "⚡ Média Prioridade"
        else:
            return "❄️ Baixa Prioridade"
            
    df_active['Priority'] = df_active['Lead Score'].apply(get_priority)
    df_active = df_active.sort_values('Lead Score', ascending=False)
    
    return df_active
