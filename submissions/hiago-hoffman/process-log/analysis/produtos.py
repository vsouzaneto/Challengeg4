import pandas as pd, numpy as np
from scipy.stats import chi2_contingency, binomtest
pd.set_option('display.width', 220); pd.set_option('display.max_columns', 30); pd.set_option('display.max_rows', 200)
p = pd.read_csv('products.csv'); t = pd.read_csv('sales_teams.csv')
s = pd.read_csv('sales_pipeline.csv', parse_dates=['engage_date', 'close_date'])
s['product'] = s['product'].replace({'GTXPro': 'GTX Pro'})
d = s.merge(t, on='sales_agent').merge(p, on='product')
c = d[d.deal_stage.isin(['Won', 'Lost'])].copy(); c['won'] = (c.deal_stage == 'Won').astype(int)
w = c[c.won == 1]

print('=== produto: volume, receita, win rate, ticket')
g = c.groupby('product').agg(fechados=('won', 'size'), ganhos=('won', 'sum'), wr=('won', 'mean'),
                             receita=('close_value', 'sum'), preco=('sales_price', 'first'))
g['%ganhos'] = (g.ganhos / g.ganhos.sum() * 100).round(1)
g['%receita'] = (g.receita / g.receita.sum() * 100).round(1)
g['ticket'] = (g.receita / g.ganhos).round(0); g['wr'] = (g.wr * 100).round(1)
g['abertos'] = d[d.deal_stage.isin(['Engaging', 'Prospecting'])].groupby('product').size()
print(g.sort_values('receita', ascending=False))

print('=== regiao x produto: % dos ganhos do produto')
print((pd.crosstab(w['product'], w.regional_office, normalize='index') * 100).round(1))
print('regiao share overall', (w.regional_office.value_counts(normalize=True) * 100).round(1).to_dict())
print('=== regiao x produto: win rate')
print((c.pivot_table(index='product', columns='regional_office', values='won', aggfunc='mean') * 100).round(1))
for pr, gg in c.groupby('product'):
    rp = chi2_contingency(pd.crosstab(gg.regional_office, gg.won))[1]
    ap = chi2_contingency(pd.crosstab(gg.sales_agent, gg.won))[1] if gg.sales_agent.nunique() > 1 else float('nan')
    print(pr, 'regiao chi2 p=', round(rp, 3), '| agente chi2 p=', round(ap, 3))

print('=== manager x produto: % dos ganhos do produto')
print((pd.crosstab(w['product'], w.manager, normalize='index') * 100).round(1))

print('=== top 5 vendedores por produto')
mix_all = w['product'].value_counts(normalize=True)
agent_tot = w.groupby('sales_agent').size()
for pr, gg in c.groupby('product'):
    a = gg.groupby('sales_agent').agg(fech=('won', 'size'), ganhos=('won', 'sum'), wr=('won', 'mean'), receita=('close_value', 'sum'))
    a['%prod'] = (a.ganhos / a.ganhos.sum() * 100).round(1)
    a['%mix_vend'] = (a.ganhos / agent_tot.reindex(a.index) * 100).round(1)
    a['lift'] = (a['%mix_vend'] / 100 / mix_all[pr]).round(2)
    a['p_wr'] = [round(binomtest(int(r.ganhos), int(r.fech), gg.won.mean()).pvalue, 3) for r in a.itertuples()]
    a['wr'] = (a.wr * 100).round(1)
    print('--', pr, '(WR produto', round(gg.won.mean() * 100, 1), ')')
    print(a.sort_values('ganhos', ascending=False).head(5))
    best = a[a.fech >= 20].sort_values('wr', ascending=False).head(3)
    print('   melhores WR (n>=20):', [(i, r.wr, r.fech, r.p_wr) for i, r in best.iterrows()])

print('=== concentracao: # vendedores p/ 50% dos ganhos do produto')
for pr, gg in w.groupby('product'):
    v = gg.sales_agent.value_counts(normalize=True).cumsum()
    print(pr, (v < 0.5).sum() + 1, 'de', gg.sales_agent.nunique())

print('=== abertos por produto x regiao (Engaging, idade <=138d)')
snap = pd.Timestamp('2017-12-31'); o = d[d.deal_stage == 'Engaging'].copy(); o['age'] = (snap - o.engage_date).dt.days
print(pd.crosstab(o['product'], [o.age <= 138]))
