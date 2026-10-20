# Sonda exploratória inicial: testa se engajamento depende de alguma feature (hipótese: dados sintéticos = ruído).
# Uso: .venv/bin/python process-log/probe_eda.py data/raw/social_media_dataset.csv
import sys, pandas as pd, numpy as np
from scipy import stats
df = pd.read_csv(sys.argv[1])
print(df.shape); print(df.dtypes.value_counts().to_dict())
num = ['views','likes','shares','comments_count','follower_count','content_length']
print(df[num].describe().round(1).T)
print("nulls:", df.isna().sum()[lambda s: s>0].to_dict())
df['eng'] = (df.likes+df.shares+df.comments_count)/df.views
print("\ncorr (spearman):\n", df[num+['eng']].corr('spearman').round(3))
for c in ['platform','content_type','content_category','is_sponsored','language','audience_age_distribution','audience_gender_distribution','audience_location','disclosure_type','sponsor_category']:
    g = df.groupby(c)['eng'].agg(['count','mean']).round(4)
    h = stats.kruskal(*[x.values for _,x in df.groupby(c)['eng']])
    print(f"\n{c}: kruskal p={h.pvalue:.3g}\n{g.T.to_string()}")
print("\nlikes/views ratio stats:", (df.likes/df.views).describe().round(4).to_dict())
print("views var/mean:", df.views.var()/df.views.mean())
print("creators:", df.creator_id.nunique(), "followers per creator nunique (mean):", df.groupby('creator_id').follower_count.nunique().mean())
print("hashtags n tags:", df.hashtags.fillna('').str.split(',').map(lambda l: len([t for t in l if t])).value_counts().sort_index().to_dict())
d = pd.to_datetime(df.post_date, format='%m/%d/%y %I:%M %p'); print("dates:", d.min(), d.max())
print("monthly mean eng:", df.groupby(d.dt.to_period('Q')).eng.mean().round(4).to_dict())
print("zero-ish engagement posts:", (df.likes==0).sum(), (df.views<1000).sum())
