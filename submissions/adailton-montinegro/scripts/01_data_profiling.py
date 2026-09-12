import duckdb
import pandas as pd
import numpy as np

DATA_DIR = "/Users/montinegro/G4 AI Master/data/churn"

con = duckdb.connect(database=':memory:')

# Carregando tabelas no DuckDB
con.execute(f"""
    CREATE TABLE accounts AS SELECT * FROM read_csv_auto('{DATA_DIR}/ravenstack_accounts.csv');
    CREATE TABLE subscriptions AS SELECT * FROM read_csv_auto('{DATA_DIR}/ravenstack_subscriptions.csv');
    CREATE TABLE feature_usage AS SELECT * FROM read_csv_auto('{DATA_DIR}/ravenstack_feature_usage.csv');
    CREATE TABLE support_tickets AS SELECT * FROM read_csv_auto('{DATA_DIR}/ravenstack_support_tickets.csv');
    CREATE TABLE churn_events AS SELECT * FROM read_csv_auto('{DATA_DIR}/ravenstack_churn_events.csv');
""")

print("=== 1. CONTAGEM DE REGISTROS ===")
tables = ['accounts', 'subscriptions', 'feature_usage', 'support_tickets', 'churn_events']
for t in tables:
    cnt = con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
    print(f"{t}: {cnt} linhas")

print("\n=== 2. INTEGRIDADE REFERENCIAL (ÓRFÃOS) ===")
# Subscriptions sem account
sub_orphan = con.execute("""
    SELECT count(*) FROM subscriptions s 
    LEFT JOIN accounts a ON s.account_id = a.account_id 
    WHERE a.account_id IS NULL
""").fetchone()[0]
print(f"Subscriptions órfãs (sem account): {sub_orphan}")

# Feature usage sem subscription
feat_orphan = con.execute("""
    SELECT count(*) FROM feature_usage f 
    LEFT JOIN subscriptions s ON f.subscription_id = s.subscription_id 
    WHERE s.subscription_id IS NULL
""").fetchone()[0]
print(f"Feature usage órfão (sem subscription): {feat_orphan}")

# Support tickets sem account
ticket_orphan = con.execute("""
    SELECT count(*) FROM support_tickets t 
    LEFT JOIN accounts a ON t.account_id = a.account_id 
    WHERE a.account_id IS NULL
""").fetchone()[0]
print(f"Support tickets órfãos (sem account): {ticket_orphan}")

# Churn events sem account
churn_orphan = con.execute("""
    SELECT count(*) FROM churn_events c 
    LEFT JOIN accounts a ON c.account_id = a.account_id 
    WHERE a.account_id IS NULL
""").fetchone()[0]
print(f"Churn events órfãos (sem account): {churn_orphan}")

print("\n=== 3. UNICIDADE DE CHAVES PRIMÁRIAS ===")
for t, pk in [('accounts', 'account_id'), ('subscriptions', 'subscription_id'), 
              ('feature_usage', 'usage_id'), ('support_tickets', 'ticket_id'), 
              ('churn_events', 'churn_event_id')]:
    res = con.execute(f"SELECT count(distinct {pk}), count(*) FROM {t}").fetchone()
    print(f"{t}.{pk}: {res[0]} distintos / {res[1]} total (duplicatas: {res[1] - res[0]})")

print("\n=== 4. PERÍODOS TEMPORAIS (MIN/MAX DATES) ===")
print("accounts.signup_date:", con.execute("SELECT min(signup_date), max(signup_date) FROM accounts").fetchone())
print("subscriptions.start_date:", con.execute("SELECT min(start_date), max(start_date) FROM subscriptions").fetchone())
print("subscriptions.end_date:", con.execute("SELECT min(end_date), max(end_date) FROM subscriptions WHERE end_date IS NOT NULL").fetchone())
print("feature_usage.usage_date:", con.execute("SELECT min(usage_date), max(usage_date) FROM feature_usage").fetchone())
print("support_tickets.submitted_at:", con.execute("SELECT min(submitted_at), max(submitted_at) FROM support_tickets").fetchone())
print("churn_events.churn_date:", con.execute("SELECT min(churn_date), max(churn_date) FROM churn_events").fetchone())

print("\n=== 5. ANÁLISE DE MRR / ARR E CONCILIAÇÃO ===")
mrr_diff = con.execute("""
    SELECT count(*), 
           sum(CASE WHEN abs(arr_amount - (mrr_amount * 12)) > 0.01 THEN 1 ELSE 0 END) as diff_count
    FROM subscriptions
""").fetchone()
print(f"Assinaturas com ARR != MRR * 12: {mrr_diff[1]} de {mrr_diff[0]}")

print("\nDistribuição por plano em subscriptions:")
df_plans = con.execute("""
    SELECT plan_tier, billing_frequency, count(*) as cnt, 
           round(avg(mrr_amount), 2) as avg_mrr, 
           round(sum(mrr_amount), 2) as total_mrr
    FROM subscriptions
    GROUP BY plan_tier, billing_frequency
    ORDER BY plan_tier, billing_frequency
""").df()
print(df_plans.to_string())

print("\n=== 6. CHURN RATE (LOGO CHURN VS CHURN EVENTS) ===")
acc_churn = con.execute("""
    SELECT 
        count(*) as total_accounts,
        sum(CASE WHEN churn_flag THEN 1 ELSE 0 END) as churned_accounts,
        round(100.0 * sum(CASE WHEN churn_flag THEN 1 ELSE 0 END) / count(*), 2) as logo_churn_pct
    FROM accounts
""").fetchone()
print(f"Accounts: Total {acc_churn[0]}, Churn {acc_churn[1]} ({acc_churn[2]}%)")

sub_churn = con.execute("""
    SELECT 
        count(*) as total_subs,
        sum(CASE WHEN churn_flag THEN 1 ELSE 0 END) as churned_subs,
        round(100.0 * sum(CASE WHEN churn_flag THEN 1 ELSE 0 END) / count(*), 2) as sub_churn_pct
    FROM subscriptions
""").fetchone()
print(f"Subscriptions: Total {sub_churn[0]}, Churn {sub_churn[1]} ({sub_churn[2]}%)")

print("\nEventos de churn vs accounts com churn_flag=True:")
diff_acc_churn = con.execute("""
    SELECT 
        (SELECT count(distinct account_id) FROM accounts WHERE churn_flag) as acc_flag_true,
        (SELECT count(distinct account_id) FROM churn_events) as churn_event_accs,
        (SELECT count(*) FROM churn_events) as total_churn_events
""").fetchone()
print(f"Contas flag churn=True: {diff_acc_churn[0]} | Contas com evento de churn: {diff_acc_churn[1]} | Total eventos de churn: {diff_acc_churn[2]}")

print("\n=== 7. NULOS POR TABELA ===")
for t in tables:
    df_desc = con.execute(f"DESCRIBE {t}").df()
    null_report = []
    for col in df_desc['column_name']:
        n_null = con.execute(f"SELECT count(*) FROM {t} WHERE \"{col}\" IS NULL").fetchone()[0]
        if n_null > 0:
            total = con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
            null_report.append((col, n_null, round(100.0 * n_null / total, 1)))
    if null_report:
        print(f"--- Nulos em {t} ---")
        for c, n, p in null_report:
            print(f"  {c}: {n} ({p}%)")
    else:
        print(f"--- Nulos em {t}: Nenhum ---")
