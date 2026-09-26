import pandas as pd, numpy as np
from scipy import stats
df=pd.read_csv('social_media_dataset.csv')
df['date']=pd.to_datetime(df.post_date,format='%m/%d/%y %I:%M %p')
print('datas',df.date.min(),df.date.max())
m=['views','likes','shares','comments_count']
for c in m: print(c,'mean',df[c].mean().round(1),'var/mean',round(df[c].var()/df[c].mean(),3))
df['eng']=(df.likes+df.shares+df.comments_count)
df['er_views']=df.eng/df.views
df['er_fol']=df.eng/df.follower_count
print('er_views',df.er_views.describe().round(4).to_dict())
print('corr views~followers (spearman)',stats.spearmanr(df.views,df.follower_count))
print('corr likes~views',stats.pearsonr(df.likes,df.views))
print('zeros',(df[m]==0).sum().to_dict())
# per creator follower consistency
g=df.groupby('creator_id').follower_count.nunique(); print('followers unique per creator: median',g.median())
g=df.groupby('creator_id').platform.nunique(); print('platforms per creator median',g.median())
cats=['platform','content_type','content_category','language','is_sponsored','disclosure_type','sponsor_category','disclosure_location','audience_age_distribution','audience_gender_distribution','audience_location']
df['fol_bin']=pd.cut(df.follower_count,[0,10e3,50e3,100e3,500e3,1e6],labels=['<10K','10-50K','50-100K','100-500K','500K-1M'])
df['len_bin']=pd.qcut(df.content_length,5)
df['hour']=df.date.dt.hour; df['dow']=df.date.dt.dayofweek; df['month']=df.date.dt.to_period('M').astype(str)
df['n_tags']=df.hashtags.fillna('').apply(lambda s: 0 if s=='' else len(s.split(',')))
res=[]
for c in cats+['fol_bin','len_bin','hour','dow','month','n_tags']:
    for y in ['views','likes','shares','comments_count','er_views']:
        groups=[x[y].values for _,x in df.groupby(c,observed=True)]
        k=stats.kruskal(*groups)
        mx=df.groupby(c,observed=True)[y].mean(); spread=(mx.max()-mx.min())/df[y].mean()*100
        res.append((c,y,len(groups),round(k.pvalue,4),round(spread,2)))
r=pd.DataFrame(res,columns=['var','metric','n_groups','p','spread_max_min_%'])
print(r.to_string())
# Bonferroni
print('n tests',len(r),'p<0.05:',(r.p<0.05).sum(),'p<0.05/n:',(r.p<0.05/len(r)).sum())
