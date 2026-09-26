import pandas as pd, numpy as np
from scipy import stats
import warnings; warnings.filterwarnings('ignore')
df=pd.read_csv('social_media_dataset.csv')
df['date']=pd.to_datetime(df.post_date,format='%m/%d/%y %I:%M %p')
df['eng']=df.likes+df.shares+df.comments_count; df['er']=df.eng/df.views
df['fol_bin']=pd.cut(df.follower_count,[0,10e3,50e3,100e3,500e3,1e6],labels=['<10K','10-50K','50-100K','100-500K','500K-1M'])
print(df.fol_bin.value_counts().sort_index().to_dict())
print('er/followers ratio',(df.eng/df.follower_count).describe().round(3).to_dict())
# Poisson check: KS vs poisson for views
for c in ['views','likes','shares','comments_count']:
    lam=df[c].mean(); x=df[c].values
    # compare quantiles
    q=[.01,.25,.5,.75,.99]
    print(c,np.quantile(x,q).round(0),stats.poisson.ppf(q,lam))
# inter-metric correlations
print(df[['views','likes','shares','comments_count','follower_count','content_length']].corr().round(3))
# creator effect (ICC) via one-way ANOVA
for y in ['er','likes']:
    grp=[g[y].values for _,g in df.groupby('creator_id')]
    print('creator effect',y,stats.f_oneway(*grp).pvalue)
# creators appearing on platforms / content types
print('creators per platform-type combos', df.groupby('creator_id')[['platform','content_type','content_category','language']].nunique().median().to_dict())
# sponsored vs organic within strata (platform x type x category x fol_bin)
strata=['platform','content_type','content_category','fol_bin']
diffs=[]
for k,g in df.groupby(strata,observed=True):
    a=g[g.is_sponsored].er; b=g[~g.is_sponsored].er
    if len(a)>30 and len(b)>30: diffs.append((k,(a.mean()/b.mean()-1)*100,stats.mannwhitneyu(a,b).pvalue,len(g)))
d=pd.DataFrame(diffs,columns=['s','lift%','p','n'])
w=d.n/d.n.sum()
print('strata',len(d),'weighted lift % ',(d['lift%']*w).sum().round(3),'p<.05',(d.p<.05).sum(),'range',d['lift%'].min().round(2),d['lift%'].max().round(2))
# OLS with controls
import statsmodels.formula.api as smf
df['sp']=df.is_sponsored.astype(int)
mod=smf.ols('er ~ sp + C(platform)+C(content_type)+C(content_category)+C(fol_bin)+C(language)+C(audience_age_distribution)+C(audience_gender_distribution)+C(audience_location)+content_length',data=df).fit()
print('OLS R2',round(mod.rsquared,5),'adjR2',round(mod.rsquared_adj,5),'F p',mod.f_pvalue,'sp coef',mod.params['sp'],'CI',mod.conf_int().loc['sp'].values)
print('sp effect in pp of ER', mod.params['sp']*100)
# Sponsored per 1K followers - disclosure, sponsor cat
print(df.groupby('disclosure_type').er.agg(['mean','count']).round(4))
# top 1% vs rest profile
top=df.er>=df.er.quantile(.99)
for c in ['platform','content_type','content_category','is_sponsored','fol_bin']:
    t=pd.crosstab(top,df[c]); print(c,'chi2 p',round(stats.chi2_contingency(t)[1],3))
# noise mining trap: best 3-way segment in train (2023-24) vs test (2024-25)
cut=pd.Timestamp('2024-05-29'); tr=df[df.date<cut]; te=df[df.date>=cut]
seg=['platform','content_type','content_category','fol_bin']
a=tr.groupby(seg,observed=True).er.agg(['mean','count']); a=a[a['count']>=100]
b=te.groupby(seg,observed=True).er.mean()
base_tr=tr.er.mean(); base_te=te.er.mean()
a['lift_tr']=(a['mean']/base_tr-1)*100; a['lift_te']=(b.reindex(a.index)/base_te-1)*100
a=a.sort_values('lift_tr',ascending=False)
print(a.head(5).round(2)); print(a.tail(3).round(2))
print('corr train vs test lift', a[['lift_tr','lift_te']].corr().iloc[0,1].round(3))
# modelo preditivo: OLS com interacoes, treino 2023-24 -> teste 2024-25
import statsmodels.formula.api as smf
f='er ~ C(platform)*C(content_type)*C(content_category) + C(fol_bin)*C(platform) + sp*C(platform) + C(language)+C(audience_age_distribution)+C(audience_gender_distribution)+C(audience_location)+content_length'
tr=tr.assign(sp=tr.is_sponsored.astype(int)); te=te.assign(sp=te.is_sponsored.astype(int))
mm=smf.ols(f,data=tr).fit(); pred=mm.predict(te)
r2=1-((te.er-pred)**2).sum()/((te.er-te.er.mean())**2).sum()
print('model params',len(mm.params),'train R2',round(mm.rsquared,4),'test R2',round(r2,5))
# hashtags
tags=df.hashtags.fillna('').str.split(',').explode(); tags=tags[tags!='']
print('unique tags',tags.nunique(),'top',tags.value_counts().head(8).to_dict())
ex=df.assign(tag=df.hashtags.fillna('').str.split(',')).explode('tag'); ex=ex[ex.tag!='']
tc=ex.groupby('tag').er.agg(['mean','count']); tc=tc[tc['count']>=100]
tc['z']=(tc['mean']-df.er.mean())/(df.er.std()/np.sqrt(tc['count']))
print('tags n>=100',len(tc),'|z|>1.96',(tc.z.abs()>1.96).sum(),'|z|>bonf',(tc.z.abs()>stats.norm.ppf(1-0.025/len(tc))).sum())
print(tc.sort_values('z').iloc[[0,1,-2,-1]].round(4))
# data consistency
print('sponsored with sponsor none?',((df.is_sponsored)&(df.sponsor_name=='Not sponsors')).sum())
print('age values',df.audience_age_distribution.unique(),'gender',df.audience_gender_distribution.unique())
print('content_length by type',df.groupby('content_type').content_length.agg(['min','median','max']).to_dict())
print('posts per month',df.groupby(df.date.dt.to_period('Q')).size().to_dict())
print('same url multiple creators',df.groupby('content_url').creator_id.nunique().max())
print('platform x lang',pd.crosstab(df.platform,df.language,normalize='index').round(2))
