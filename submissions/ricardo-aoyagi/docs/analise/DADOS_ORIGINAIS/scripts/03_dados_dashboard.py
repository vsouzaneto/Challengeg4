# Passo 3: gera os JSONs agregados usados no dashboard
# Gerado com Claude (IA) - desafio G4 data-001-churn
# Pastas: G4_DESAFIO/dados (CSVs originais, só leitura) -> G4_DESAFIO/analise
from pathlib import Path
RAIZ = Path(__file__).resolve().parents[3]          # G4_DESAFIO
DADOS = str(RAIZ / 'dados') + '/'
TRAB = RAIZ / "analise" / "DADOS_ORIGINAIS" / "scripts" / "_trabalho"; TRAB.mkdir(parents=True, exist_ok=True)
import pandas as pd, numpy as np, json
B=pd.read_pickle(TRAB/'bases.pkl'); K,S,C,U,T=B['K'],B['S'],B['C'],B['U'],B['T']
O=str(TRAB/'dash')+'/'; (TRAB/'dash').mkdir(exist_ok=True)
INDS=['Todas']+sorted(K.industry.unique()); PLANS=['Todos','Basic','Pro','Enterprise']
months=pd.date_range('2023-01-01','2024-12-01',freq='MS')
def fi(df,ind,col='industry'): return df if ind=='Todas' else df[df[col]==ind]
def fp(df,pl,col='plan_tier'): return df if pl=='Todos' else df[df[col]==pl]
r2=lambda x: None if x is None or (isinstance(x,float) and np.isnan(x)) else round(float(x),4)
mensal=[]; kpis=[]
for ind in INDS:
    k=fi(K,ind); c=fi(C,ind)
    for pl in PLANS:
        s=fp(fi(S,ind),pl); u=fp(fi(U,ind),pl)
        for m in months:
            act=s[(s.start_date<m)&(s.end_date_calc>=m)]
            mi=act.mrr_amount.sum(); mc=s[s.mes_fim==m].mrr_amount.sum()
            ev=(c.mes_churn==m).sum(); ac=(k.signup_date<m).sum(); us=u[u.mes_uso==m].usage_count.sum()
            mensal.append(dict(industria=ind,plano=pl,mes=m.strftime('%Y-%m-%d'),novas_contas=int((k.mes_cadastro==m).sum()),
              novas_assinaturas=int((s.mes_inicio==m).sum()),mrr_novo=int(s[s.mes_inicio==m].mrr_amount.sum()),
              assinaturas_encerradas=int((s.mes_fim==m).sum()),mrr_cancelado=int(mc),mrr_inicio_mes=int(mi),
              churn_receita=r2(mc/mi) if mi>0 else None,eventos_churn=int(ev),mrr_em_risco=int(c[c.mes_churn==m].mrr_em_risco.sum()),
              contas_inicio_mes=int(ac),churn_contas=r2(ev/ac) if ac>0 else None,uso_total=int(us),assinaturas_ativas_inicio=len(act),
              uso_por_assinatura=round(us/len(act),2) if len(act)>0 else None))
        last=pd.Timestamp('2024-12-01')
        act=s[s.status=='Ativa']
        kpis.append(dict(industria=ind,plano=pl,mrr_ativo=int(act.mrr_amount.sum()),assinaturas_ativas=len(act),
            mrr_cancelado_total=int(s[s.status=='Encerrada'].mrr_amount.sum()),assinaturas_encerradas=int((s.status=='Encerrada').sum()),
            contas=len(k),contas_com_evento=int((k.conta_com_evento_churn=='Sim').sum()),eventos_churn=len(c),
            churn_receita_dez24=[x for x in mensal if x['industria']==ind and x['plano']==pl and x['mes']=='2024-12-01'][0]['churn_receita'],
            churn_contas_dez24=[x for x in mensal if x['industria']==ind and x['plano']==pl and x['mes']=='2024-12-01'][0]['churn_contas']))
# segmentos
seg=[]
for lab,col in [('Indústria','industry'),('Plano inicial da conta','plano_inicial_conta'),('País','country'),('Canal de aquisição','referral_source')]:
    for v in sorted(K[col].unique()):
        k=K[K[col]==v]; c=C[C[col]==v]; s=S[S[col]==v]
        ma=k.mrr_ativo_atual.sum(); mc=s[s.status=='Encerrada'].mrr_amount.sum()
        seg.append(dict(dimensao=lab,segmento=v,contas=len(k),contas_com_evento=int((k.conta_com_evento_churn=='Sim').sum()),
          pct_contas_com_evento=r2((k.conta_com_evento_churn=='Sim').mean()),contas_churn_flag=int((k.churn_flag_conta=='Sim').sum()),
          pct_churn_flag=r2((k.churn_flag_conta=='Sim').mean()),eventos_churn=len(c),mrr_em_risco=int(c.mrr_em_risco.sum()),
          mrr_ativo=int(ma),mrr_cancelado=int(mc),pct_mrr_cancelado=r2(mc/(ma+mc))))
# motivos
mot=[]
for ind in INDS:
    c=fi(C,ind)
    for r in sorted(C.reason_code.unique()):
        x=c[c.reason_code==r]
        mot.append(dict(industria=ind,motivo=r,eventos=len(x),pct_eventos=r2(len(x)/len(c)),mrr_em_risco=int(x.mrr_em_risco.sum()),refund=round(float(x.refund_amount_usd.sum()),2),reativacoes=int((x.is_reactivation=='Sim').sum())))
# features
feat=[]
for ind in INDS:
    for pl in PLANS:
        u=fp(fi(U,ind),pl)
        for d,col in [('evento','conta_com_evento_churn'),('flag','churn_flag_conta')]:
            for i in range(1,41):
                fn=f'feature_{i}'; x=u[u.feature_name==fn]; a=x[x[col]=='Sim']; b=x[x[col]=='Não']
                e100=lambda z: r2(z.error_count.sum()/z.usage_count.sum()*100) if z.usage_count.sum()>0 else None
                feat.append(dict(industria=ind,plano=pl,definicao=d,feature=fn,feature_num=i,registros=len(x),uso_total=int(x.usage_count.sum()),
                  horas=round(x.usage_duration_secs.sum()/3600,1),erros=int(x.error_count.sum()),erros_100=e100(x),
                  pct_beta=r2((x.is_beta_feature=='Sim').mean()) if len(x) else None,
                  registros_com=len(a),registros_sem=len(b),pct_registros_com=r2(len(a)/len(x)) if len(x) else None,
                  uso_medio_com=r2(a.usage_count.mean()) if len(a) else None,uso_medio_sem=r2(b.usage_count.mean()) if len(b) else None,
                  min_medio_com=r2(a.duracao_min.mean()) if len(a) else None,min_medio_sem=r2(b.duracao_min.mean()) if len(b) else None,
                  erros_100_com=e100(a),erros_100_sem=e100(b)))
# comparativo
comp=[]
IND_DEF=[('Contas','contas','int'),('MRR ativo médio por conta','mrr','usd'),('MRR cancelado médio por conta','mrrc','usd'),('Assinaturas por conta','assin','dec'),
 ('Upgrades por conta','upg','dec'),('Downgrades por conta','dng','dec'),('Uso total por conta (usage_count)','uso','dec'),('Horas de uso por conta','horas','dec'),
 ('Erros por 100 usos','e100','dec'),('Tickets por conta','tick','dec'),('Satisfação média (1–5)','sat','dec'),('% tickets com satisfação respondida','satr','pct'),
 ('Tempo médio de resolução (h)','res','dec'),('Primeira resposta média (min)','frt','dec'),('% tickets escalados','esc','pct'),('% tickets urgent','urg','pct')]
for ind in INDS:
    for d,col in [('evento','conta_com_evento_churn'),('flag','churn_flag_conta')]:
        vals={}
        for g in ['Sim','Não']:
            k=fi(K,ind); k=k[k[col]==g]; t=fi(T,ind); t=t[t[col]==g]; n=len(k)
            vals[g]=dict(contas=n,mrr=k.mrr_ativo_atual.sum()/n,mrrc=k.mrr_cancelado_total.sum()/n,assin=k.qtd_assinaturas.mean(),upg=k.qtd_upgrades.mean(),
              dng=k.qtd_downgrades.mean(),uso=k.uso_count_total.mean(),horas=k.uso_horas.mean(),e100=k.erros_total.sum()/k.uso_count_total.sum()*100,
              tick=len(t)/n,sat=t.satisfaction_score.mean(),satr=t.satisfaction_score.notna().mean(),res=t.resolution_time_hours.mean(),
              frt=t.first_response_time_minutes.mean(),esc=(t.escalation_flag=='Sim').mean(),urg=(t.priority=='urgent').mean())
        for o,(lab,key,fmt) in enumerate(IND_DEF):
            a,b=vals['Sim'][key],vals['Não'][key]
            comp.append(dict(industria=ind,definicao=d,ordem=o+1,indicador=lab,formato=fmt,com_churn=r2(a),sem_churn=r2(b),diferenca=r2(a-b),
                diferenca_pct=r2((a-b)/b) if b else None))
# contas
cont=K[['account_id','account_name','industry','country','referral_source','plano_inicial_conta','signup_date','qtd_assin_ativas','mrr_ativo_atual','mrr_cancelado_total','qtd_eventos_churn','ultimo_churn','ultimo_motivo','uso_count_total','erros_por_uso','qtd_tickets','satisfacao_media','qtd_escalacoes','conta_com_evento_churn','churn_flag_conta']].copy()
cont['signup_date']=cont.signup_date.dt.strftime('%Y-%m-%d'); cont['ultimo_churn']=cont.ultimo_churn.dt.strftime('%Y-%m-%d').fillna('')
cont['erros_100']=(cont.pop('erros_por_uso')*100).round(2)
for c_ in ['qtd_assin_ativas','mrr_ativo_atual','mrr_cancelado_total','qtd_eventos_churn','uso_count_total','qtd_tickets','qtd_escalacoes']: cont[c_]=cont[c_].astype(int)
cont=cont.rename(columns={'industry':'industria','country':'pais','referral_source':'canal','plano_inicial_conta':'plano_inicial'})
cont=cont.sort_values('mrr_ativo_atual',ascending=False)
cont['satisfacao_media']=cont.satisfacao_media.where(cont.satisfacao_media.notna(),None)
for n,d in dict(mensal=mensal,kpis=kpis,segmentos=seg,motivos=mot,features=feat,comparativo=comp).items():
    json.dump(d,open(O+n+'.json','w'),ensure_ascii=False)
cont.to_json(O+'contas.json',orient='records',force_ascii=False)
import os
for f in sorted(os.listdir(O)): print(f, os.path.getsize(O+f))
print([x for x in kpis if x['industria']=='Todas' and x['plano']=='Todos'])

# chave única por linha (usada pelo dashboard)
for n,keys in [('mensal',['industria','plano','mes']),('features',['industria','plano','definicao','feature']),('comparativo',['industria','definicao','ordem']),('motivos',['industria','motivo']),('kpis',['industria','plano']),('segmentos',['dimensao','segmento'])]:
    d=json.load(open(O+n+'.json'))
    d=[dict(chave='|'.join(str(r[k]) for k in keys),**r) for r in d]
    json.dump(d,open(O+n+'.json','w'),ensure_ascii=False,separators=(',',':'))
