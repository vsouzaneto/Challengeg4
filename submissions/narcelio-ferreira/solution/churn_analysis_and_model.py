import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

def main():
    print("=== RavenStack: Diagnostico de Churn & Modelo Preditivo ===")
    data_dir = "../../"
    try:
        accounts = pd.read_csv(os.path.join(data_dir, 'ravenstack_accounts.csv'))
        subs = pd.read_csv(os.path.join(data_dir, 'ravenstack_subscriptions.csv'))
        usage = pd.read_csv(os.path.join(data_dir, 'ravenstack_feature_usage.csv'))
        tickets = pd.read_csv(os.path.join(data_dir, 'ravenstack_support_tickets.csv'))
        churn = pd.read_csv(os.path.join(data_dir, 'ravenstack_churn_events.csv'))
    except FileNotFoundError:
        print("[!] Ficheiros CSV nao encontrados na raiz. Execute com os dados para calcular.")
        return

    usage_col = [col for col in usage.columns if 'event' in col or 'count' in col or 'usage' in col]
    num_col = usage_col[0] if usage_col else usage.select_dtypes(include=[np.number]).columns[0]
    usage_summary = usage.groupby('subscription_id').agg(
        total_usage_events=(num_col, 'sum'),
        avg_usage_events=(num_col, 'mean')
    ).reset_index()

    ticket_summary = tickets.groupby('account_id').agg(
        total_tickets=('ticket_id', 'count')
    ).reset_index()

    df = subs.merge(accounts, on='account_id', how='left')
    df = df.merge(usage_summary, on='subscription_id', how='left').fillna({'total_usage_events': 0, 'avg_usage_events': 0})
    df = df.merge(ticket_summary, on='account_id', how='left').fillna({'total_tickets': 0})

    churn_subs = churn['subscription_id'].unique()
    df['is_churned'] = df['subscription_id'].isin(churn_subs).astype(int)

    print(f"\n[+] Total de Assinaturas Analisadas: {len(df)}")
    print(f"[+] Taxa de Churn Base (Contas): {df['is_churned'].mean():.2%}")

    features = ['mrr', 'total_usage_events', 'total_tickets']
    features = [f for f in features if f in df.columns]
    
    X = df[features].fillna(0)
    y = df['is_churned']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    active_subs = df[df['is_churned'] == 0].copy()
    active_subs['churn_risk_prob'] = model.predict_proba(active_subs[features])[:, 1]

    top_risk = active_subs.sort_values(by='churn_risk_prob', ascending=False).head(10)
    print("\n--- TOP CONTAS ATIVAS EM RISCO IMINENTE (ACAO DO CS) ---")
    cols_to_show = ['account_id', 'subscription_id', 'churn_risk_prob']
    if 'mrr' in top_risk.columns:
        cols_to_show.append('mrr')
    print(top_risk[cols_to_show])

if __name__ == '__main__':
    main()
