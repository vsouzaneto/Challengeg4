# Passo 4: testes de consistência entre as marcações de churn (só leitura)
# Gerado com Claude (IA) - desafio G4 data-001-churn
# Pastas: G4_DESAFIO/dados (CSVs originais, só leitura) -> G4_DESAFIO/analise
from pathlib import Path
RAIZ = Path(__file__).resolve().parents[3]          # G4_DESAFIO
DADOS = str(RAIZ / 'dados') + '/'
TRAB = RAIZ / "analise" / "DADOS_ORIGINAIS" / "scripts" / "_trabalho"; TRAB.mkdir(parents=True, exist_ok=True)
import pandas as pd, numpy as np
try:
    from scipy.stats import chi2_contingency
    pval = lambda ct: chi2_contingency(ct)[1]
except ImportError:
    pval = lambda ct: float('nan')   # pip install scipy para ver o p-valor
a=pd.read_csv(DADOS+'ravenstack_accounts.csv',parse_dates=['signup_date'])
s=pd.read_csv(DADOS+'ravenstack_subscriptions.csv',parse_dates=['start_date','end_date'])
c=pd.read_csv(DADOS+'ravenstack_churn_events.csv',parse_dates=['churn_date'])
a['evento']=a.account_id.isin(c.account_id); a['assin_encerrada']=a.account_id.isin(s[s.churn_flag].account_id)
print('== 1. As três marcações são independentes? ==')
for x,y in [('churn_flag','evento'),('churn_flag','assin_encerrada'),('evento','assin_encerrada')]:
    ct=pd.crosstab(a[x],a[y]); print(f'{x} x {y}: P({y}|{x}=Sim)={a[a[x]][y].mean():.0%}  P({y}|{x}=Não)={a[~a[x]][y].mean():.0%}  p={pval(ct):.2f}')
print('\n== 2. Combinações das três marcações por conta =='); print(a.groupby(['churn_flag','evento','assin_encerrada']).size())
print('\n== 3. Evento de churn coincide com fim de assinatura (±7 dias)? ==')
m=c.merge(s[s.end_date.notna()][['account_id','end_date']],on='account_id',how='left')
m['perto']=(m.churn_date-m.end_date).dt.days.abs()<=7; print(f"{m.groupby('churn_event_id').perto.any().mean():.1%} dos eventos")
print('\n== 4. Conta tinha assinatura ativa no dia do último evento? ==')
ult=c.groupby('account_id').churn_date.max()
ativ=[((s.account_id==i)&(s.start_date<=d)&(s.end_date.isna()|(s.end_date>d))).any() for i,d in ult.items()]
print(f'{np.mean(ativ):.1%} das contas com evento')
print('\n== 5. reason_code x feedback_text =='); ct=pd.crosstab(c.reason_code,c.feedback_text.fillna('(vazio)')); print(ct); print(f'p={pval(ct):.2f}')
print('\n== 6. is_reactivation x existência de evento anterior ==')
c=c.sort_values('churn_date'); c['tem_evento_anterior']=c.groupby('account_id').cumcount()>0
print(pd.crosstab(c.is_reactivation,c.tem_evento_anterior))
print('\n== 7. preceding_downgrade_flag x downgrade real nos 90 dias anteriores ==')
had=lambda acc,d,col: ((s.account_id==acc)&s[col]&(s.start_date<=d)&(s.start_date>=d-pd.Timedelta(days=90))).any()
c['downgrade_real']=[had(r.account_id,r.churn_date,'downgrade_flag') for r in c.itertuples()]
print(pd.crosstab(c.preceding_downgrade_flag,c.downgrade_real))
print('\n== 8. Datas de uso x assinatura ==')
f=pd.read_csv(DADOS+'ravenstack_feature_usage.csv',parse_dates=['usage_date']).merge(s[['subscription_id','account_id','start_date']],on='subscription_id').merge(a[['account_id','signup_date']],on='account_id')
print(f"uso antes do início da assinatura: {(f.usage_date<f.start_date).mean():.1%} | antes do cadastro da conta: {(f.usage_date<f.signup_date).mean():.1%}")
