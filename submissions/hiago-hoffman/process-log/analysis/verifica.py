import pandas as pd, numpy as np
from scipy.stats import binomtest, false_discovery_control
pd.set_option('display.width', 220); pd.set_option('display.max_columns', 30)
p = pd.read_csv('products.csv'); t = pd.read_csv('sales_teams.csv')
s = pd.read_csv('sales_pipeline.csv', parse_dates=['engage_date', 'close_date'])
s['product'] = s['product'].replace({'GTXPro': 'GTX Pro'})
d = s.merge(t, on='sales_agent').merge(p, on='product')
c = d[d.deal_stage.isin(['Won', 'Lost'])].copy(); c['won'] = (c.deal_stage == 'Won').astype(int)
c['cycle'] = (c.close_date - c.engage_date).dt.days
SNAP = pd.Timestamp('2017-12-31')

print('=== 1. Checagem das afirmacoes do documento')
m1 = c[(c.close_date.dt.month - 1) % 3 == 0]
print('fechamentos no 1o mes do trimestre:', len(m1), 'ciclo max:', m1.cycle.max())
rows = []
for (ag, pr), g in c.groupby(['sales_agent', 'product']):
    base = c[c['product'] == pr].won.mean()
    rows.append((ag, pr, len(g), binomtest(int(g.won.sum()), len(g), base).pvalue))
r = pd.DataFrame(rows, columns=['ag', 'pr', 'n', 'p'])
r['q'] = false_discovery_control(r.p, method='bh')
print('combinacoes vendedor x produto:', len(r), '| p<0.01:', (r.p < 0.01).sum(), '| q<0.10:', (r.q < 0.10).sum())
print(r.sort_values('p').head(3).round(4).to_string(index=False))

print('\n=== 2. Empirical Bayes: forca de encolhimento aprendida por dimensao')
# metodo dos momentos: var observada entre grupos vs var binomial esperada
def eb(col, df=c):
    g = df.groupby(col).won.agg(['sum', 'size']); mu = df.won.mean()
    rate = g['sum'] / g['size']
    var_obs = np.average((rate - mu) ** 2, weights=g['size'])
    var_noise = np.average(mu * (1 - mu) / g['size'], weights=g['size'])
    tau2 = max(var_obs - var_noise, 0)          # variancia "real" entre grupos
    k = np.inf if tau2 == 0 else mu * (1 - mu) / tau2 - 1   # forca da priori (em deals)
    return len(g), round(var_obs ** .5 * 100, 2), round(var_noise ** .5 * 100, 2), round(tau2 ** .5 * 100, 2), k, int(g['size'].median())
c['agent_x_product'] = c.sales_agent + '|' + c['product']
c['region_x_product'] = c.regional_office + '|' + c['product']
print(f"{'dimensao':18s} grupos  dp_obs  dp_ruido  dp_real   k(prior)  n_mediano  peso_do_grupo_mediano")
for col in ['product', 'series', 'regional_office', 'manager', 'sales_agent', 'account', 'agent_x_product', 'region_x_product']:
    n, so, sn, st, k, nm = eb(col)
    w = 0 if np.isinf(k) else nm / (nm + k)
    print(f"{col:18s} {n:6d}  {so:6.2f}  {sn:8.2f}  {st:7.2f}  {k:9.0f}  {nm:9d}  {w:6.2f}")

print('\n=== 3. Quantis do ciclo de ganhos (limiares aprendidos)')
print(c[c.won == 1].cycle.quantile([.5, .75, .9, .95, .99, 1]).to_dict())
print('ciclo de perdas:', c[c.won == 0].cycle.quantile([.25, .5, .75]).to_dict())

print('\n=== 4. Riscos competitivos semanais (fechados + abertos censurados)')
e = d[d.engage_date.notna()].copy()
e['dur'] = np.where(e.close_date.notna(), (e.close_date - e.engage_date).dt.days, (SNAP - e.engage_date).dt.days)
e['wk'] = e.dur // 7
e['ev'] = e.deal_stage.map({'Won': 'W', 'Lost': 'L'}).fillna('C')
maxwk = int(e.wk.max())
H = []
for k in range(maxwk + 1):
    at_risk = (e.wk >= k).sum(); ev = e[e.wk == k]
    H.append((k, at_risk, (ev.ev == 'W').sum(), (ev.ev == 'L').sum()))
H = pd.DataFrame(H, columns=['wk', 'risk', 'W', 'L'])
H['hw'] = H.W / H.risk; H['hl'] = H.L / H.risk
H['S'] = (1 - H.hw - H.hl).cumprod().shift(fill_value=1)
def p_win_from(week):
    h = H[H.wk >= week]; S = (1 - h.hw - h.hl).cumprod().shift(fill_value=1)
    return (S * h.hw).sum()
def p_win_30d(week):
    h = H[(H.wk >= week) & (H.wk < week + 4)]; S = (1 - h.hw - h.hl).cumprod().shift(fill_value=1)
    return (S * h.hw).sum()
print('idade  em_risco  P(ganhar em algum momento)  P(ganhar em 30d)')
for days in [0, 14, 30, 60, 90, 120, 133, 140, 170, 250]:
    w = days // 7
    print(f"{days:4d}d {int(H.loc[H.wk == w, 'risk'].iloc[0]):8d}   {p_win_from(w):.3f}                      {p_win_30d(w):.3f}")
print('semanas com eventos: ultima =', H[(H.W + H.L) > 0].wk.max(), '| em risco depois dela:', int(H.loc[H.wk == H[(H.W + H.L) > 0].wk.max() + 1, 'risk'].iloc[0]))

print('\n=== 5. Razao valor realizado / preco, por produto (ganhos)')
w_ = c[c.won == 1]; print((w_.close_value / w_.sales_price).groupby(w_['product']).agg(['mean', 'std', 'size']).round(3))
