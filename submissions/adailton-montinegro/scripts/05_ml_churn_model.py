import duckdb
import pandas as pd
import numpy as np
import json
import joblib
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score, average_precision_score, classification_report, brier_score_loss

DATA_DIR = "/Users/montinegro/G4 AI Master/data/churn"
OUTPUT_DIR = "/Users/montinegro/G4 AI Master/repo/submissions/adailton-montinegro/artifacts"
con = duckdb.connect(database=':memory:')

con.execute(f"""
    CREATE TABLE accounts AS SELECT * FROM read_csv_auto('{DATA_DIR}/ravenstack_accounts.csv');
    CREATE TABLE subscriptions AS SELECT * FROM read_csv_auto('{DATA_DIR}/ravenstack_subscriptions.csv');
    CREATE TABLE feature_usage AS SELECT * FROM read_csv_auto('{DATA_DIR}/ravenstack_feature_usage.csv');
    CREATE TABLE support_tickets AS SELECT * FROM read_csv_auto('{DATA_DIR}/ravenstack_support_tickets.csv');
    CREATE TABLE churn_events AS SELECT * FROM read_csv_auto('{DATA_DIR}/ravenstack_churn_events.csv');
""")

# 1. Feature Engineering consolidada por Account
query_features = """
WITH sub_summary AS (
    SELECT 
        account_id,
        count(subscription_id) as total_subs_history,
        sum(CASE WHEN upgrade_flag THEN 1 ELSE 0 END) as total_upgrades,
        sum(CASE WHEN downgrade_flag THEN 1 ELSE 0 END) as total_downgrades,
        arg_max(billing_frequency, start_date) as latest_billing_frequency,
        arg_max(auto_renew_flag, start_date) as latest_auto_renew,
        arg_max(mrr_amount, start_date) as latest_mrr,
        arg_max(arr_amount, start_date) as latest_arr
    FROM subscriptions
    GROUP BY account_id
),
usage_summary AS (
    SELECT 
        s.account_id,
        count(f.usage_id) as total_usage_events,
        coalesce(sum(f.usage_count), 0) as total_usage_count,
        coalesce(sum(f.usage_duration_secs), 0) as total_usage_duration,
        coalesce(sum(f.error_count), 0) as total_error_count,
        coalesce(sum(CASE WHEN f.is_beta_feature THEN f.usage_count ELSE 0 END), 0) as beta_usage_count,
        coalesce(sum(CASE WHEN f.is_beta_feature THEN f.error_count ELSE 0 END), 0) as beta_error_count
    FROM subscriptions s
    LEFT JOIN feature_usage f ON s.subscription_id = f.subscription_id
    GROUP BY s.account_id
),
support_summary AS (
    SELECT 
        account_id,
        count(ticket_id) as total_tickets,
        avg(first_response_time_minutes) as avg_frt_minutes,
        avg(resolution_time_hours) as avg_resolution_hours,
        sum(CASE WHEN escalation_flag THEN 1 ELSE 0 END) as total_escalations,
        sum(CASE WHEN priority IN ('high', 'urgent') THEN 1 ELSE 0 END) as high_urgent_tickets,
        avg(satisfaction_score) as avg_csat,
        sum(CASE WHEN satisfaction_score IS NULL THEN 1 ELSE 0 END) as unrated_csat_tickets
    FROM support_tickets
    GROUP BY account_id
),
churn_history AS (
    SELECT 
        account_id,
        count(churn_event_id) as historical_churn_events,
        sum(refund_amount_usd) as total_refunds_usd,
        sum(CASE WHEN is_reactivation THEN 1 ELSE 0 END) as total_reactivations
    FROM churn_events
    GROUP BY account_id
)
SELECT 
    a.account_id,
    a.account_name,
    a.industry,
    a.country,
    a.referral_source,
    a.plan_tier,
    a.seats,
    a.is_trial,
    -- Subscriptions
    coalesce(sub.total_subs_history, 0) as total_subs_history,
    coalesce(sub.total_upgrades, 0) as total_upgrades,
    coalesce(sub.total_downgrades, 0) as total_downgrades,
    coalesce(sub.latest_billing_frequency, 'monthly') as latest_billing_frequency,
    coalesce(sub.latest_auto_renew, true) as latest_auto_renew,
    coalesce(sub.latest_mrr, 500.0) as latest_mrr,
    -- Usage
    coalesce(u.total_usage_count, 0) as total_usage_count,
    coalesce(u.total_usage_duration, 0) as total_usage_duration,
    coalesce(u.total_error_count, 0) as total_error_count,
    round(100.0 * coalesce(u.total_error_count, 0) / nullif(coalesce(u.total_usage_count, 0), 0), 2) as error_rate_pct,
    coalesce(u.beta_usage_count, 0) as beta_usage_count,
    coalesce(u.beta_error_count, 0) as beta_error_count,
    round(coalesce(u.total_usage_count, 0) / nullif(a.seats, 0), 2) as usage_per_seat,
    -- Support
    coalesce(sup.total_tickets, 0) as total_tickets,
    coalesce(sup.avg_frt_minutes, 90.0) as avg_frt_minutes,
    coalesce(sup.avg_resolution_hours, 35.0) as avg_resolution_hours,
    coalesce(sup.total_escalations, 0) as total_escalations,
    coalesce(sup.high_urgent_tickets, 0) as high_urgent_tickets,
    coalesce(sup.avg_csat, 4.0) as avg_csat,
    coalesce(sup.unrated_csat_tickets, 0) as unrated_csat_tickets,
    -- Churn History
    coalesce(ch.historical_churn_events, 0) as historical_churn_events,
    coalesce(ch.total_refunds_usd, 0.0) as total_refunds_usd,
    -- Target
    a.churn_flag
FROM accounts a
LEFT JOIN sub_summary sub ON a.account_id = sub.account_id
LEFT JOIN usage_summary u ON a.account_id = u.account_id
LEFT JOIN support_summary sup ON a.account_id = sup.account_id
LEFT JOIN churn_history ch ON a.account_id = ch.account_id
"""

df = con.execute(query_features).df()
df['error_rate_pct'] = df['error_rate_pct'].fillna(0.0)
df['usage_per_seat'] = df['usage_per_seat'].fillna(0.0)

print(f"Dataset de modelagem gerado: {df.shape[0]} contas, {df.shape[1]} colunas.")

# Separação de features e target
target_col = 'churn_flag'
id_cols = ['account_id', 'account_name']
feature_cols = [c for c in df.columns if c not in [target_col] + id_cols]

categorical_cols = ['industry', 'country', 'referral_source', 'plan_tier', 'latest_billing_frequency']
numerical_cols = [c for c in feature_cols if c not in categorical_cols and c not in ['is_trial', 'latest_auto_renew']]
boolean_cols = ['is_trial', 'latest_auto_renew']

for b in boolean_cols:
    df[b] = df[b].astype(int)
numerical_cols.extend(boolean_cols)

X = df[feature_cols]
y = df[target_col].astype(int)

# Preprocessador robusto com Imputer + Scaler
num_pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', num_pipeline, numerical_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_cols)
    ]
)

models = {
    'Logistic Regression': LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=200, max_depth=6, class_weight='balanced', random_state=42),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=150, learning_rate=0.05, max_depth=4, random_state=42)
}

print("\n=== VALIDAÇÃO CRUZADA ESTRATIFICADA (5-FOLD) ===")
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

results = []
for name, model in models.items():
    pipe = Pipeline([('prep', preprocessor), ('clf', model)])
    scores = cross_validate(pipe, X, y, cv=cv, scoring=['roc_auc', 'average_precision', 'f1', 'precision', 'recall'])
    results.append({
        'Modelo': name,
        'ROC-AUC (Média)': round(scores['test_roc_auc'].mean(), 4),
        'ROC-AUC (DesvPad)': round(scores['test_roc_auc'].std(), 4),
        'PR-AUC (Média)': round(scores['test_average_precision'].mean(), 4),
        'F1-Score': round(scores['test_f1'].mean(), 4),
        'Precision': round(scores['test_precision'].mean(), 4),
        'Recall': round(scores['test_recall'].mean(), 4)
    })

df_res = pd.DataFrame(results)
print(df_res.to_string(index=False))

# Treinar o melhor modelo em toda a base para geração de scores e feature importance
best_pipe = Pipeline([
    ('prep', preprocessor), 
    ('clf', RandomForestClassifier(n_estimators=300, max_depth=6, class_weight='balanced', random_state=42))
])
best_pipe.fit(X, y)

# Extração de nomes de features pós One-Hot Encoding
onehot_cols = best_pipe.named_steps['prep'].named_transformers_['cat'].get_feature_names_out(categorical_cols).tolist()
all_features = numerical_cols + onehot_cols
importances = best_pipe.named_steps['clf'].feature_importances_

df_feat_imp = pd.DataFrame({
    'Feature': all_features,
    'Importance': importances
}).sort_values(by='Importance', ascending=False)

print("\n=== TOP 15 FEATURES MAIS IMPORTANTES (RANDOM FOREST) ===")
print(df_feat_imp.head(15).to_string(index=False))

# Gerar probabilidades calibradas de risco de churn para todas as 500 contas
probs = best_pipe.predict_proba(X)[:, 1]
df['churn_risk_score'] = np.round(probs, 4)

# Definir faixas de risco executivas
def get_risk_tier(score):
    if score >= 0.65:
        return 'Crítico (Alto Risco)'
    elif score >= 0.35:
        return 'Atenção (Médio Risco)'
    else:
        return 'Saudável (Baixo Risco)'

df['risk_tier'] = df['churn_risk_score'].apply(get_risk_tier)

# Ação prescritiva recomendada com base nas características de atrito
def get_prescriptive_action(row):
    if not row['churn_flag'] and row['risk_tier'] == 'Crítico (Alto Risco)':
        if row['total_escalations'] > 0 or row['avg_frt_minutes'] > 90:
            return 'Executive Sponsor + Revisão Prioritária de Suporte com Head de CS'
        elif row['error_rate_pct'] > 6.0:
            return 'Intervenção Técnica de Engenharia + Remoção de Betas Instáveis'
        elif row['latest_mrr'] > 3000:
            return 'Renegociação Contratual + Lock-in Anual com Desconto Estruturado'
        else:
            return 'Check-in Imediato de Adoção e Treinamento de Features Core'
    elif row['risk_tier'] == 'Atenção (Médio Risco)':
        return 'Monitoramento Ativo + Pesquisa Qualitativa de NPS/CSAT'
    else:
        return 'Manter Régua Automatizada de Sucesso do Cliente'

df['recommended_action'] = df.apply(get_prescriptive_action, axis=1)

# Salvar artefatos
output_csv = f"{OUTPUT_DIR}/ravenstack_account_risk_scores.csv"
export_cols = ['account_id', 'account_name', 'industry', 'country', 'plan_tier', 'seats', 
               'latest_mrr', 'churn_flag', 'churn_risk_score', 'risk_tier', 'recommended_action',
               'error_rate_pct', 'total_escalations', 'avg_frt_minutes', 'total_downgrades']
df[export_cols].sort_values(by='churn_risk_score', ascending=False).to_csv(output_csv, index=False)
print(f"\nScores e tabela prescritiva salvos com sucesso em: {output_csv}")

# Salvar métricas e feature importance em JSON
metrics_json = {
    'model_results': results,
    'top_features': df_feat_imp.head(15).to_dict(orient='records'),
    'risk_distribution': df['risk_tier'].value_counts().to_dict()
}
with open(f"{OUTPUT_DIR}/model_metrics.json", "w") as f:
    json.dump(metrics_json, f, indent=2)

print("Métricas do modelo salvas em artifacts/model_metrics.json.")
