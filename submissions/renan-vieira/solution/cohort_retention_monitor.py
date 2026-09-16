"""
Monitor de Retencao por Cohort - RavenStack

Automacao que o time de CS/Growth pode rodar mensalmente (ex: todo dia 1)
para acompanhar a saude de ativacao dos clientes novos, cohort a cohort.

Por que isso e o KPI certo (e nao um score de risco por conta):
A analise mostrou que nenhum atributo de conta (industria, plano, canal,
MRR, uso individual, satisfacao) discrimina quem vai churnar. O sinal real
esta na COHORT: contas que assinaram mais recentemente estao churnando
muito mais rapido nos primeiros meses de vida do que contas antigas
(ex: % que churna em ate 2 meses saltou de 15% em 2023 para 48,7% em 2024).
Ou seja, o problema e de ativacao/onboarding, que se degrada ao longo do
tempo, e o jeito certo de monitorar isso e por cohort de entrada, nao por
score individual (que ja testamos e nao funciona neste dataset).

Uso:
    python3 cohort_retention_monitor.py accounts.csv churn_events.csv --cutoff 2024-12-31

Saida: tabela de % churned por meses-desde-signup, por cohort (trimestre
ou semestre), respeitando censura (nao mostra pontos ainda nao observaveis).
Alerta automatico se a cohort mais recente com pelo menos 60 dias de vida
estiver com churn em 2 meses acima do triplo da cohort mais antiga do
historico -- sinal de que a degradacao de ativacao continua piorando.
"""
import argparse
import pandas as pd
import numpy as np


def build_retention_curve(accounts_path, churn_events_path, cutoff_date, cohort_freq='2Q', max_months=12):
    accounts = pd.read_csv(accounts_path, parse_dates=['signup_date'])
    churn_events = pd.read_csv(churn_events_path, parse_dates=['churn_date'])
    cutoff = pd.Timestamp(cutoff_date)

    first_churn = churn_events.groupby('account_id')['churn_date'].min().rename('first_churn_date')
    acc = accounts.merge(first_churn, on='account_id', how='left')
    acc['cohort'] = acc['signup_date'].dt.to_period(cohort_freq).astype(str)

    curva = {}
    for cohort, grp in acc.groupby('cohort'):
        pct_churned = []
        for m in range(0, max_months + 1):
            observavel = grp[(cutoff - grp['signup_date']).dt.days >= m * 30]
            if len(observavel) == 0:
                pct_churned.append(np.nan)
                continue
            churnou_ate_m = observavel['first_churn_date'].notna() & (
                (observavel['first_churn_date'] - observavel['signup_date']).dt.days <= m * 30
            )
            pct_churned.append(round(churnou_ate_m.mean() * 100, 1))
        curva[cohort] = pct_churned

    curva_df = pd.DataFrame(curva, index=range(0, max_months + 1))
    curva_df.index.name = 'meses_desde_signup'
    return curva_df


def check_alert(curva_df, mes=2, fator_alerta=3.0):
    """Compara churn em `mes` meses da cohort mais recente observavel vs a mais antiga."""
    linha = curva_df.loc[mes].dropna()
    if len(linha) < 2:
        return None
    cohort_antiga, valor_antigo = linha.index[0], linha.iloc[0]
    cohort_recente, valor_recente = linha.index[-1], linha.iloc[-1]
    if valor_antigo > 0 and valor_recente >= valor_antigo * fator_alerta:
        return (f"ALERTA: churn em {mes} meses da cohort {cohort_recente} ({valor_recente}%) "
                f"esta {valor_recente/valor_antigo:.1f}x maior que a cohort {cohort_antiga} ({valor_antigo}%).")
    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Monitor de retencao por cohort')
    parser.add_argument('accounts_csv')
    parser.add_argument('churn_events_csv')
    parser.add_argument('--cutoff', required=True, help='Data de corte, ex: 2024-12-31')
    parser.add_argument('--cohort_freq', default='2Q', help='Frequencia da cohort (ex: Q, 2Q, M)')
    args = parser.parse_args()

    curva = build_retention_curve(args.accounts_csv, args.churn_events_csv, args.cutoff, args.cohort_freq)
    print(curva.to_string())
    alerta = check_alert(curva)
    if alerta:
        print()
        print(alerta)
