# Passo 1: cruza as 5 tabelas e gera as bases consolidadas (bases.pkl)
# Gerado com Claude (IA) - desafio G4 data-001-churn
# Pastas: G4_DESAFIO/dados (CSVs originais, só leitura) -> G4_DESAFIO/analise
from pathlib import Path
RAIZ = Path(__file__).resolve().parents[3]          # G4_DESAFIO
DADOS = str(RAIZ / 'dados') + '/'
TRAB = RAIZ / "analise" / "DADOS_ORIGINAIS" / "scripts" / "_trabalho"; TRAB.mkdir(parents=True, exist_ok=True)
import pandas as pd, numpy as np
D=DADOS
a=pd.read_csv(D+'ravenstack_accounts.csv',parse_dates=['signup_date'])
s=pd.read_csv(D+'ravenstack_subscriptions.csv',parse_dates=['start_date','end_date'])
f=pd.read_csv(D+'ravenstack_feature_usage.csv',parse_dates=['usage_date'])
t=pd.read_csv(D+'ravenstack_support_tickets.csv',parse_dates=['submitted_at','closed_at'])
c=pd.read_csv(D+'ravenstack_churn_events.csv',parse_dates=['churn_date'])
SN=lambda b: np.where(b,'Sim','Não')
mes=lambda d: d.dt.to_period('M').dt.to_timestamp()
acc_ev=set(c.account_id)
A=a[['account_id','industry','country','referral_source','plan_tier']].rename(columns={'plan_tier':'plano_inicial_conta'})
flags=pd.DataFrame({'account_id':a.account_id,'conta_com_evento_churn':SN(a.account_id.isin(acc_ev)),'churn_flag_conta':SN(a.churn_flag)})

# Assinaturas
S=s.merge(A,on='account_id').merge(flags,on='account_id')
S['mes_inicio']=mes(S.start_date); S['mes_fim']=mes(S.end_date)
S['end_date_calc']=S.end_date.fillna(pd.Timestamp('2099-12-31'))
S['status']=np.where(S.end_date.isna(),'Ativa','Encerrada')
for col in ['is_trial','upgrade_flag','downgrade_flag','auto_renew_flag']: S[col]=SN(S[col])
S=S[['subscription_id','account_id','industry','country','referral_source','plano_inicial_conta','plan_tier','billing_frequency','seats','mrr_amount','arr_amount','is_trial','upgrade_flag','downgrade_flag','auto_renew_flag','start_date','mes_inicio','end_date','mes_fim','end_date_calc','status','conta_com_evento_churn','churn_flag_conta']]

# Churn eventos + MRR em risco
def mrr_at(acc,dt):
    x=s[s.account_id==acc]; m=(x.start_date<=dt)&(x.end_date.isna()|(x.end_date>dt)); return x[m].mrr_amount.sum(), m.sum()
C=c.merge(A,on='account_id').merge(flags[['account_id','churn_flag_conta']],on='account_id')
r=[mrr_at(i,d) for i,d in zip(C.account_id,C.churn_date)]
C['mrr_em_risco']=[x[0] for x in r]; C['assin_ativas_na_data']=[x[1] for x in r]
C['mes_churn']=mes(C.churn_date)
for col in ['preceding_upgrade_flag','preceding_downgrade_flag','is_reactivation']: C[col]=SN(C[col])
C['feedback_text']=C.feedback_text.fillna('(sem comentário)')
C=C[['churn_event_id','account_id','industry','country','referral_source','plano_inicial_conta','churn_date','mes_churn','reason_code','feedback_text','refund_amount_usd','preceding_upgrade_flag','preceding_downgrade_flag','is_reactivation','mrr_em_risco','assin_ativas_na_data','churn_flag_conta']]

# Uso
U=f.merge(s[['subscription_id','account_id','plan_tier','billing_frequency']],on='subscription_id').merge(A,on='account_id').merge(flags,on='account_id')
U['mes_uso']=mes(U.usage_date); U['duracao_min']=(U.usage_duration_secs/60).round(1)
U['is_beta_feature']=SN(U.is_beta_feature)
U['feature_num']=U.feature_name.str.replace('feature_','').astype(int)
U=U[['usage_id','subscription_id','account_id','industry','country','referral_source','plano_inicial_conta','plan_tier','billing_frequency','usage_date','mes_uso','feature_name','feature_num','usage_count','usage_duration_secs','duracao_min','error_count','is_beta_feature','conta_com_evento_churn','churn_flag_conta']]

# Tickets
T=t.merge(A,on='account_id').merge(flags,on='account_id')
T['mes_ticket']=mes(T.submitted_at); T['escalation_flag']=SN(T.escalation_flag)
T['satisfacao_respondida']=SN(T.satisfaction_score.notna())
T=T[['ticket_id','account_id','industry','country','referral_source','plano_inicial_conta','submitted_at','mes_ticket','closed_at','priority','resolution_time_hours','first_response_time_minutes','satisfaction_score','satisfacao_respondida','escalation_flag','conta_com_evento_churn','churn_flag_conta']]

# Contas
K=a.rename(columns={'plan_tier':'plano_inicial_conta','seats':'seats_inicial'}).copy()
K['mes_cadastro']=mes(K.signup_date)
g=s.groupby('account_id')
K=K.merge(pd.DataFrame({'qtd_assinaturas':g.size(),'qtd_assin_ativas':g.end_date.apply(lambda x:x.isna().sum()),
  'mrr_ativo_atual':s[s.end_date.isna()].groupby('account_id').mrr_amount.sum(),
  'mrr_cancelado_total':s[s.end_date.notna()].groupby('account_id').mrr_amount.sum(),
  'qtd_upgrades':g.upgrade_flag.sum(),'qtd_downgrades':g.downgrade_flag.sum()}).reset_index(),on='account_id',how='left')
gc=c.sort_values('churn_date').groupby('account_id')
K=K.merge(pd.DataFrame({'qtd_eventos_churn':gc.size(),'ultimo_churn':gc.churn_date.max(),'ultimo_motivo':gc.reason_code.last()}).reset_index(),on='account_id',how='left')
gu=U.groupby('account_id')
K=K.merge(pd.DataFrame({'uso_registros':gu.size(),'uso_count_total':gu.usage_count.sum(),'uso_horas':(gu.usage_duration_secs.sum()/3600).round(1),'erros_total':gu.error_count.sum()}).reset_index(),on='account_id',how='left')
gt=t.groupby('account_id')
K=K.merge(pd.DataFrame({'qtd_tickets':gt.size(),'satisfacao_media':gt.satisfaction_score.mean().round(2),'resolucao_media_h':gt.resolution_time_hours.mean().round(1),'qtd_escalacoes':gt.escalation_flag.sum()}).reset_index(),on='account_id',how='left')
for col in ['qtd_eventos_churn','mrr_cancelado_total','uso_registros','uso_count_total','uso_horas','erros_total','qtd_tickets','qtd_escalacoes','mrr_ativo_atual']: K[col]=K[col].fillna(0)
K['erros_por_uso']=np.where(K.uso_count_total>0,K.erros_total/K.uso_count_total,0).round(4)
K['conta_com_evento_churn']=SN(K.qtd_eventos_churn>0); K['churn_flag_conta']=SN(K.churn_flag); K['is_trial']=SN(K.is_trial)
K['ultimo_motivo']=K.ultimo_motivo.fillna('')
K=K[['account_id','account_name','industry','country','referral_source','plano_inicial_conta','seats_inicial','is_trial','signup_date','mes_cadastro','qtd_assinaturas','qtd_assin_ativas','mrr_ativo_atual','mrr_cancelado_total','qtd_upgrades','qtd_downgrades','qtd_eventos_churn','ultimo_churn','ultimo_motivo','uso_registros','uso_count_total','uso_horas','erros_total','erros_por_uso','qtd_tickets','satisfacao_media','resolucao_media_h','qtd_escalacoes','conta_com_evento_churn','churn_flag_conta']]
pd.to_pickle(dict(K=K,S=S,C=C,U=U,T=T),str(TRAB/'bases.pkl'))
for n,d in dict(K=K,S=S,C=C,U=U,T=T).items(): print(n,d.shape)
print(C.mrr_em_risco.describe())
