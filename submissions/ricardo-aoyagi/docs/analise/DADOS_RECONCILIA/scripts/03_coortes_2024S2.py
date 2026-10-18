# Passo 3: o que mudou nas assinaturas do 2º semestre de 2024 e em dezembro? + checagem no subconjunto limpo
# (gerado com Claude/IA). Lê os CSVs originais sem alterá-los; grava uma planilha apartada.
import sys
from pathlib import Path
from math import lgamma, exp
import pandas as pd, numpy as np
RAIZ = Path(__file__).resolve().parents[3]
DADOS = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / 'dados'
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else RAIZ / 'analise' / 'DADOS_RECONCILIA' / '03_Coortes_2024S2.xlsx'
FIM = pd.Timestamp('2024-12-31'); CORTE = pd.Timestamp('2024-07-01'); SEED = 42; N_PERM = 5000
rng = np.random.default_rng(SEED)

a = pd.read_csv(DADOS/'ravenstack_accounts.csv', parse_dates=['signup_date'])
s = pd.read_csv(DADOS/'ravenstack_subscriptions.csv', parse_dates=['start_date','end_date'])
f = pd.read_csv(DADOS/'ravenstack_feature_usage.csv', parse_dates=['usage_date'])
t = pd.read_csv(DADOS/'ravenstack_support_tickets.csv', parse_dates=['submitted_at','closed_at'])
c = pd.read_csv(DADOS/'ravenstack_churn_events.csv', parse_dates=['churn_date'])

def fisher_p(a_, b_, c_, d_):
    """Fisher exato bilateral para a tabela [[a,b],[c,d]]."""
    n1, n2, m1 = a_ + b_, c_ + d_, a_ + c_; N = n1 + n2
    lc = lambda n, k: lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)
    pmf = lambda x: exp(lc(n1, x) + lc(n2, m1 - x) - lc(N, m1))
    p0 = pmf(a_); lo, hi = max(0, m1 - n2), min(m1, n1)
    return min(1.0, sum(pmf(x) for x in range(lo, hi + 1) if pmf(x) <= p0 * (1 + 1e-7)))

# ---------------- base de assinaturas ----------------
S = s.merge(a[['account_id', 'signup_date', 'industry', 'country', 'referral_source']], on='account_id')
S['duracao_dias'] = (S.end_date.fillna(FIM) - S.start_date).dt.days
S['coorte'] = np.where(S.start_date >= CORTE, '2024-S2', 'Até 2024-S1')
S['observavel_30d'] = np.where(S.start_date <= FIM - pd.Timedelta(days=30), 'Sim', 'Não')
S['encerrou_30d'] = np.where(S.end_date.notna() & (S.duracao_dias <= 30), 1, 0)
S['f_plano'] = S.plan_tier; S['f_cobranca'] = S.billing_frequency
S['f_trial'] = np.where(S.is_trial, 'Trial', 'Pago'); S['f_auto_renew'] = np.where(S.auto_renew_flag, 'Sim', 'Não')
S['f_upgrade'] = np.where(S.upgrade_flag, 'Sim', 'Não'); S['f_downgrade'] = np.where(S.downgrade_flag, 'Sim', 'Não')
S['f_seats'] = pd.cut(S.seats, [0, 5, 15, 40, 10**6], labels=['1–5', '6–15', '16–40', '41+']).astype(str)
S['f_industria'] = S.industry; S['f_pais'] = S.country; S['f_canal'] = S.referral_source
idade = (S.start_date - S.signup_date).dt.days
S['f_idade_conta'] = pd.cut(idade, [-1, 30, 90, 180, 365, 10**4], labels=['Conta nova (≤ 30 dias)', '31–90 dias', '91–180 dias', '181–365 dias', 'Mais de 365 dias']).astype(str)
S['mes_fim'] = S.end_date.dt.to_period('M').dt.to_timestamp()
S['dia_fim'] = S.end_date.dt.day
S['ultimos_3_dias_mes'] = np.where(S.end_date.notna() & (S.end_date.dt.day >= S.end_date.dt.days_in_month - 2), 'Sim', np.where(S.end_date.notna(), 'Não', ''))
FATORES = [('f_plano', 'Plano da assinatura'), ('f_cobranca', 'Cobrança'), ('f_trial', 'Trial'), ('f_auto_renew', 'Renovação automática'),
           ('f_upgrade', 'Upgrade na assinatura'), ('f_downgrade', 'Downgrade na assinatura'), ('f_seats', 'Seats da assinatura'),
           ('f_idade_conta', 'Idade da conta ao assinar'), ('f_industria', 'Indústria'), ('f_pais', 'País'), ('f_canal', 'Canal de aquisição')]
O = S[S.observavel_30d == 'Sim']
rows = []; comp = []
for col, lab in FATORES:
    tab = pd.crosstab(O[col], O.coorte)
    # composição: o peso de cada categoria mudou entre as coortes? (permutação da coorte)
    obs_share = pd.crosstab(O[col], O.coorte, normalize='columns')
    stat = lambda lab_c: np.abs(pd.crosstab(O[col].values, lab_c, normalize='columns').diff(axis=1).iloc[:, -1]).sum()
    st0 = stat(O.coorte.values); cnt = 0
    for _ in range(1000): cnt += stat(rng.permutation(O.coorte.values)) >= st0 - 1e-12
    comp.append(dict(fator=lab, p_composicao=(cnt + 1) / 1001))
    for v in sorted(O[col].unique()):
        x = O[O[col] == v]; g1 = x[x.coorte == '2024-S2']; g0 = x[x.coorte == 'Até 2024-S1']
        p = fisher_p(int(g1.encerrou_30d.sum()), len(g1) - int(g1.encerrou_30d.sum()), int(g0.encerrou_30d.sum()), len(g0) - int(g0.encerrou_30d.sum()))
        rows.append(dict(fator=lab, coluna=col, valor=v, p_fisher=p))
R = pd.DataFrame(rows); CP = pd.DataFrame(comp)
# dezembro
dez = S[S.end_date.notna() & (S.mes_fim == pd.Timestamp('2024-12-01'))]
print('dez encerradas', len(dez), 'nos 3 últimos dias', (dez.ultimos_3_dias_mes == 'Sim').sum())

# ---------------- base de contas + subconjunto limpo ----------------
K = a[['account_id', 'industry', 'referral_source', 'plan_tier', 'seats', 'signup_date', 'churn_flag']].copy()
K['tem_evento'] = K.account_id.isin(c.account_id); K['tem_assin_encerrada'] = K.account_id.isin(s[s.end_date.notna()].account_id)
K['grupo'] = np.select([K.churn_flag & K.tem_evento & K.tem_assin_encerrada, ~K.churn_flag & ~K.tem_evento & ~K.tem_assin_encerrada],
                       ['Churn (3 concordam)', 'Ativa (3 concordam)'], 'Divergente')
g = s.groupby('account_id')
K['mrr_ativo'] = K.account_id.map(s[s.end_date.isna()].groupby('account_id').mrr_amount.sum()).fillna(0)
K['assinaturas'] = K.account_id.map(g.size())
K['pct_assin_2024S2'] = K.account_id.map(g.start_date.apply(lambda x: (x >= CORTE).mean()))
K['meses_de_casa'] = (FIM - K.signup_date).dt.days / 30.4375
fu = f.merge(s[['subscription_id', 'account_id']], on='subscription_id'); gu = fu.groupby('account_id')
K['uso_total'] = K.account_id.map(gu.usage_count.sum()).fillna(0)
K['erros_100_usos'] = (K.account_id.map(gu.error_count.sum()).fillna(0) / K.uso_total.replace(0, np.nan) * 100)
gt = t.groupby('account_id'); K['tickets'] = K.account_id.map(gt.size()).fillna(0); K['satisfacao_media'] = K.account_id.map(gt.satisfaction_score.mean())
K['teve_upgrade'] = K.account_id.map(g.upgrade_flag.any()).astype(int); K['teve_downgrade'] = K.account_id.map(g.downgrade_flag.any()).astype(int)
K['is_devtools'] = (K.industry == 'DevTools').astype(int); K['is_partner'] = (K.referral_source == 'partner').astype(int)
METR = [('mrr_ativo', 'MRR ativo (US$)'), ('assinaturas', 'Assinaturas por conta'), ('pct_assin_2024S2', '% das assinaturas iniciadas em 2024-S2'),
        ('meses_de_casa', 'Meses desde o cadastro'), ('seats', 'Seats (cadastro)'), ('uso_total', 'Uso total (usage_count)'), ('erros_100_usos', 'Erros por 100 usos'),
        ('tickets', 'Tickets por conta'), ('satisfacao_media', 'Satisfação média'), ('teve_upgrade', '% com upgrade'), ('teve_downgrade', '% com downgrade'),
        ('is_devtools', '% DevTools'), ('is_partner', '% canal partner')]
cl = K[K.grupo != 'Divergente']; lab_cl = (cl.grupo == 'Churn (3 concordam)').values
pclean = {}
for col, lab in METR:
    v = cl[col].values.astype(float); ok = ~np.isnan(v); vv, ll = v[ok], lab_cl[ok]
    d0 = abs(vv[ll].mean() - vv[~ll].mean()); cnt = 0
    for _ in range(N_PERM):
        p_ = rng.permutation(ll); cnt += abs(vv[p_].mean() - vv[~p_].mean()) >= d0 - 1e-12
    pclean[col] = (cnt + 1) / (N_PERM + 1)
# churn_flag por indústria na base toda (para explicar o DevTools)
flag_ind = K.groupby('industry').churn_flag.mean()

# ---------------- planilha ----------------
from openpyxl import Workbook
from openpyxl.utils import get_column_letter as L
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import CellIsRule
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.chart import BarChart, LineChart, Reference
FONT = 'Arial'; GRAY = '52514E'; Fn = lambda **k: Font(name=FONT, **k)
HD = PatternFill('solid', fgColor='1F2937'); HA = PatternFill('solid', fgColor='6B7280'); HB = PatternFill('solid', fgColor='1D4ED8'); HC = PatternFill('solid', fgColor='B45309')
YEL = PatternFill('solid', fgColor='FFF3CD'); RED = PatternFill('solid', fgColor='F8D7DA'); GR = PatternFill('solid', fgColor='EDEDED')
thin = Side(style='thin', color='D0D0D0'); BOX = Border(top=thin, bottom=thin, left=thin, right=thin)
wb = Workbook(); wb.remove(wb.active)
def S_(n): ws = wb.create_sheet(n); ws.sheet_view.showGridLines = False; return ws
leia = S_('LEIA-ME'); cf = S_('Coorte_x_Fator'); dz = S_('Dezembro'); tm = S_('Sinais_no_tempo'); sl = S_('Subconjunto_limpo')
BS = {}
def base(nome, df, cols, fmts):
    ws = wb.create_sheet(nome); ws.append(cols)
    for row in df[cols].itertuples(index=False):
        out = []
        for v in row:
            if v is None or v is pd.NaT or (isinstance(v, float) and np.isnan(v)): out.append(None)
            elif isinstance(v, pd.Timestamp): out.append(v.to_pydatetime())
            elif isinstance(v, (np.floating, float)): out.append(round(float(v), 4))
            else: out.append(v.item() if hasattr(v, 'item') else v)
        ws.append(out)
    n = len(df) + 1; BS[nome] = (cols, n)
    for i, cn in enumerate(cols, 1):
        h = ws.cell(1, i); h.font = Fn(bold=True, color='FFFFFF', size=9); h.fill = HD; ws.column_dimensions[L(i)].width = max(11, min(24, len(cn) + 2))
        if cn in fmts:
            for r in range(2, n + 1): ws.cell(r, i).number_format = fmts[cn]
    tb = Table(displayName='t' + nome, ref=f'A1:{L(len(cols))}{n}'); tb.tableStyleInfo = TableStyleInfo(name='TableStyleLight1', showRowStripes=True); ws.add_table(tb); ws.freeze_panes = 'B2'
def Rg(b, col): cols, n = BS[b]; i = cols.index(col) + 1; return f"{b}!${L(i)}$2:${L(i)}${n}"
D = 'dd/mm/yyyy'
colsS = ['subscription_id', 'account_id', 'start_date', 'end_date', 'duracao_dias', 'mrr_amount', 'coorte', 'observavel_30d', 'encerrou_30d', 'mes_fim', 'dia_fim', 'ultimos_3_dias_mes'] + [c_ for c_, _ in FATORES]
base('Base_Assinaturas', S, colsS, {'start_date': D, 'end_date': D, 'mes_fim': 'mmm/yy'})
K['signup_date_'] = K.signup_date
colsK = ['account_id', 'grupo', 'industry', 'referral_source', 'churn_flag', 'tem_evento', 'tem_assin_encerrada'] + [c_ for c_, _ in METR]
base('Base_Contas', K, colsK, {})
T = t.copy(); T['mes'] = T.submitted_at.dt.to_period('M').dt.to_timestamp(); T['escalado'] = T.escalation_flag.astype(int)
base('Base_Tickets', T, ['ticket_id', 'account_id', 'mes', 'resolution_time_hours', 'first_response_time_minutes', 'satisfaction_score', 'escalado', 'priority'], {'mes': 'mmm/yy'})
Fu = f.copy(); Fu['mes'] = Fu.usage_date.dt.to_period('M').dt.to_timestamp()
base('Base_Uso', Fu, ['usage_id', 'mes', 'usage_count', 'error_count'], {'mes': 'mmm/yy'})
def hdr(ws, row, labels, fills, h=40):
    for j, (x, fl) in enumerate(zip(labels, fills), 1):
        c_ = ws.cell(row, j, x); c_.font = Fn(bold=True, color='FFFFFF', size=9); c_.fill = fl; c_.alignment = Alignment(wrap_text=True, horizontal='center', vertical='center'); c_.border = BOX
    ws.row_dimensions[row].height = h
def cell(ws, r, c_, v, fmt=None, bold=False, fill=None):
    x = ws.cell(r, c_, v); x.font = Fn(size=9, bold=bold); x.border = BOX
    if fmt: x.number_format = fmt
    if fill: x.fill = fill
    return x

# ---- Coorte_x_Fator ----
ws = cf
ws['A1'] = 'O que mudou nas assinaturas iniciadas no 2º semestre de 2024?'; ws['A1'].font = Fn(bold=True, size=15)
ws['A2'] = ('Só assinaturas com 30 dias observáveis (início até 01/12/2024). "% encerra em 30 dias" = assinaturas encerradas com até 30 dias de vida. '
            'Composição = peso de cada categoria dentro da coorte. Contagens e % são fórmulas; p-valores vêm do script (Fisher exato e permutação).')
ws['A2'].font = Fn(italic=True, size=9, color=GRAY); ws.merge_cells('A2:N2'); ws['A2'].alignment = Alignment(wrap_text=True); ws.row_dimensions[2].height = 30
hdr(ws, 4, ['Fator', 'Categoria', 'Até 2024-S1: assinaturas', 'Até 2024-S1: encerram em 30 dias', 'Até 2024-S1: %', '2024-S2: assinaturas', '2024-S2: encerram em 30 dias', '2024-S2: %',
            'Aumento (S2 ÷ antes)', 'p (Fisher)', 'Composição até S1', 'Composição S2', 'Mudança de composição (p.p.)', 'p da composição (fator)', '% S2 esperado só pela mudança de mix'],
    [HD, HD, HA, HA, HA, HB, HB, HB, HC, HC, HA, HB, HC, HC, HC])
r = 5; obs = f'{Rg("Base_Assinaturas","observavel_30d")},"Sim"'; coh = Rg('Base_Assinaturas', 'coorte'); enc = Rg('Base_Assinaturas', 'encerrou_30d')
# linha total
cell(ws, r, 1, 'TODAS', bold=True, fill=GR); cell(ws, r, 2, 'Todas', bold=True, fill=GR)
cell(ws, r, 3, f'=COUNTIFS({obs},{coh},"Até 2024-S1")', '#,##0', True, GR); cell(ws, r, 4, f'=SUMIFS({enc},{obs},{coh},"Até 2024-S1")', '#,##0', True, GR); cell(ws, r, 5, f'=D{r}/C{r}', '0.0%', True, GR)
cell(ws, r, 6, f'=COUNTIFS({obs},{coh},"2024-S2")', '#,##0', True, GR); cell(ws, r, 7, f'=SUMIFS({enc},{obs},{coh},"2024-S2")', '#,##0', True, GR); cell(ws, r, 8, f'=G{r}/F{r}', '0.0%', True, GR)
cell(ws, r, 9, f'=IF(E{r}>0,H{r}/E{r},"")', '0.0"x"', True, GR)
o_ = O; g1 = o_[o_.coorte == '2024-S2']; g0 = o_[o_.coorte != '2024-S2']
cell(ws, r, 10, round(fisher_p(int(g1.encerrou_30d.sum()), len(g1) - int(g1.encerrou_30d.sum()), int(g0.encerrou_30d.sum()), len(g0) - int(g0.encerrou_30d.sum())), 6), '0.0000', True, GR)
for j in (11, 12, 13, 14, 15): cell(ws, r, j, '', fill=GR)
r = 6; tot_row = 5
for col, lab in FATORES:
    first = r; fc = Rg('Base_Assinaturas', col)
    for _, x in R[R.coluna == col].iterrows():
        v = f'"{x.valor}"'
        cell(ws, r, 1, lab if r == first else ''); cell(ws, r, 2, x.valor, bold=True)
        cell(ws, r, 3, f'=COUNTIFS({obs},{coh},"Até 2024-S1",{fc},{v})', '#,##0'); cell(ws, r, 4, f'=SUMIFS({enc},{obs},{coh},"Até 2024-S1",{fc},{v})', '#,##0'); cell(ws, r, 5, f'=IF(C{r}>0,D{r}/C{r},"")', '0.0%')
        cell(ws, r, 6, f'=COUNTIFS({obs},{coh},"2024-S2",{fc},{v})', '#,##0'); cell(ws, r, 7, f'=SUMIFS({enc},{obs},{coh},"2024-S2",{fc},{v})', '#,##0'); cell(ws, r, 8, f'=IF(F{r}>0,G{r}/F{r},"")', '0.0%')
        cell(ws, r, 9, f'=IF(AND(ISNUMBER(E{r}),E{r}>0),H{r}/E{r},"sem casos antes")', '0.0"x"'); cell(ws, r, 10, round(x.p_fisher, 6), '0.0000')
        cell(ws, r, 11, f'=C{r}/C${tot_row}', '0.0%'); cell(ws, r, 12, f'=F{r}/F${tot_row}', '0.0%'); cell(ws, r, 13, f'=(L{r}-K{r})*100', '+0.0;-0.0;0.0')
        cell(ws, r, 14, round(float(CP[CP.fator == lab].p_composicao.iloc[0]), 4) if r == first else '', '0.000')
        cell(ws, r, 15, '')
        r += 1
    ws.cell(r - (r - first), 15).value = f'=SUMPRODUCT(L{first}:L{r-1},E{first}:E{r-1})'; ws.cell(first, 15).number_format = '0.0%'
    ws.cell(first, 1).font = Fn(size=9, bold=True)
last = r - 1
ws.conditional_formatting.add(f'J5:J{last}', CellIsRule(operator='lessThan', formula=['0.05'], fill=YEL))
ws.conditional_formatting.add(f'N6:N{last}', CellIsRule(operator='lessThan', formula=['0.05'], fill=YEL))
ws.cell(5, 15).value = '=E5'; ws.cell(5, 15).number_format = '0.0%'
r += 1
for tx in ['Leitura: o % que encerra em 30 dias sobe em praticamente todas as categorias de todos os fatores. O mix muda em alguns fatores (idade da conta, indústria, país, canal: p da composição < 0,05), mas a coluna O mostra que essa mudança, sozinha, deixaria a taxa de 2024-S2 perto da antiga (linha TODAS, coluna E).',
           'Coluna O = taxa que 2024-S2 teria se cada categoria mantivesse a taxa antiga e só o mix mudasse. Como fica muito abaixo da taxa real de 2024-S2 (H5), o aumento NÃO vem do mix: é do PERÍODO e atinge todos. A causa está em algo que não aparece nestas tabelas (produto, preço, concorrência, cobrança, onboarding).',
           'p (Fisher) compara S2 vs antes dentro da categoria. Categorias pequenas podem não atingir p < 0,05 mesmo com aumento grande.']:
    ws.cell(r, 1, tx).font = Fn(italic=True, size=9, color=GRAY); r += 1
for col_, w in zip('ABCDEFGHIJKLMNO', [24, 22, 11, 11, 8, 11, 11, 8, 10, 9, 10, 10, 11, 11, 13]): ws.column_dimensions[col_].width = w
ws.freeze_panes = 'C5'
ch = BarChart(); ch.type = 'bar'; ch.grouping = 'clustered'; ch.title = '% que encerra em até 30 dias: antes vs 2024-S2 (por plano)'; ch.height = 7; ch.width = 16
pr = [i for i in range(6, last + 1) if ws.cell(i, 1).value == 'Plano da assinatura' or (ws.cell(i, 1).value == '' and i < 9)]
ch.add_data(Reference(ws, min_col=5, min_row=4, max_row=8), titles_from_data=True); ch.add_data(Reference(ws, min_col=8, min_row=4, max_row=8), titles_from_data=True)
ch.set_categories(Reference(ws, min_col=2, min_row=5, max_row=8)); ch.series[0].graphicalProperties.solidFill = 'C3C2B7'; ch.series[1].graphicalProperties.solidFill = '2A78D6'
ch.x_axis.number_format = '0%'; ch.legend.position = 'b'; ws.add_chart(ch, 'Q4')

# ---- Dezembro ----
ws = dz
ws['A1'] = 'Dezembro de 2024: o que há de diferente nos encerramentos?'; ws['A1'].font = Fn(bold=True, size=15)
ws['A2'] = 'Contagens por fórmula sobre Base_Assinaturas. "Esperado" = média diária dos 11 primeiros meses de 2024 escalada pelo número de assinaturas ativas (aproximação).'; ws['A2'].font = Fn(italic=True, size=9, color=GRAY)
ws['A4'] = '1. Encerramentos por dia em dezembro/2024'; ws['A4'].font = Fn(bold=True, size=12)
hdr(ws, 5, ['Dia', 'Assinaturas encerradas', 'MRR encerrado (US$)'], [HD, HB, HB])
dc = Rg('Base_Assinaturas', 'end_date')
for i in range(31):
    rr = 6 + i; d_ = pd.Timestamp(2024, 12, i + 1).to_pydatetime()
    cell(ws, rr, 1, d_, 'dd/mm'); cell(ws, rr, 2, f'=COUNTIFS({dc},A{rr})', '#,##0'); cell(ws, rr, 3, f'=SUMIFS({Rg("Base_Assinaturas","mrr_amount")},{dc},A{rr})', '#,##0')
cell(ws, 37, 1, 'Total', bold=True, fill=GR); cell(ws, 37, 2, '=SUM(B6:B36)', '#,##0', True, GR); cell(ws, 37, 3, '=SUM(C6:C36)', '#,##0', True, GR)
cell(ws, 38, 1, 'Dias 29–31', bold=True); cell(ws, 38, 2, '=SUM(B34:B36)', '#,##0', True); cell(ws, 38, 3, '=SUM(C34:C36)', '#,##0', True)
cell(ws, 39, 1, 'Média/dia dias 1–28'); cell(ws, 39, 2, '=AVERAGE(B6:B33)', '0.0'); cell(ws, 40, 1, 'Média/dia dias 29–31'); cell(ws, 40, 2, '=AVERAGE(B34:B36)', '0.0')
ch = BarChart(); ch.type = 'col'; ch.title = 'Assinaturas encerradas por dia, dez/2024'; ch.height = 7; ch.width = 18; ch.legend = None
ch.add_data(Reference(ws, min_col=2, min_row=5, max_row=36), titles_from_data=True); ch.set_categories(Reference(ws, min_col=1, min_row=6, max_row=36)); ch.series[0].graphicalProperties.solidFill = '2A78D6'; ws.add_chart(ch, 'F4')
ws['A43'] = '2. Fim de mês é comum? % dos encerramentos nos 3 últimos dias do mês'; ws['A43'].font = Fn(bold=True, size=12)
hdr(ws, 44, ['Mês', 'Encerradas', 'Nos 3 últimos dias', '%'], [HD, HB, HB, HB])
mf = Rg('Base_Assinaturas', 'mes_fim'); u3 = Rg('Base_Assinaturas', 'ultimos_3_dias_mes')
meses = pd.date_range('2024-01-01', '2024-12-01', freq='MS')
for i, m in enumerate(meses):
    rr = 45 + i
    cell(ws, rr, 1, m.to_pydatetime(), 'mmm/yy'); cell(ws, rr, 2, f'=COUNTIFS({mf},A{rr})', '#,##0'); cell(ws, rr, 3, f'=COUNTIFS({mf},A{rr},{u3},"Sim")', '#,##0'); cell(ws, rr, 4, f'=IF(B{rr}>0,C{rr}/B{rr},"")', '0%')
rr = 45 + len(meses); cell(ws, rr, 1, 'jan–nov/24', bold=True, fill=GR); cell(ws, rr, 2, f'=SUM(B45:B{rr-2})', '#,##0', True, GR); cell(ws, rr, 3, f'=SUM(C45:C{rr-2})', '#,##0', True, GR); cell(ws, rr, 4, f'=C{rr}/B{rr}', '0%', True, GR)
ws.cell(rr + 1, 1, 'Referência: 3 dias de ~30 ≈ 10% se os encerramentos fossem espalhados ao longo do mês.').font = Fn(italic=True, size=9, color=GRAY)
r0 = rr + 3; ws.cell(r0, 1, '3. Quem encerrou em dezembro: tempo de vida e perfil').font = Fn(bold=True, size=12)
hdr(ws, r0 + 1, ['Indicador', 'Encerradas em dez/24', 'Encerradas jan–nov/24'], [HD, HB, HA])
dd = Rg('Base_Assinaturas', 'duracao_dias'); mfd = Rg('Base_Assinaturas', 'mes_fim'); DEZ = 'DATE(2024,12,1)'
ind = [('Assinaturas', f'=COUNTIFS({mfd},{DEZ})', f'=COUNTIFS({mfd},">="&DATE(2024,1,1),{mfd},"<"&{DEZ})', '#,##0'),
       ('% com até 30 dias de vida', f'=COUNTIFS({mfd},{DEZ},{dd},"<=30")/B{r0+2}', f'=COUNTIFS({mfd},">="&DATE(2024,1,1),{mfd},"<"&{DEZ},{dd},"<=30")/C{r0+2}', '0%'),
       ('% iniciadas no mesmo mês', f'=COUNTIFS({mfd},{DEZ},{Rg("Base_Assinaturas","start_date")},">="&{DEZ})/B{r0+2}', '', '0%'),
       ('% trial', f'=COUNTIFS({mfd},{DEZ},{Rg("Base_Assinaturas","f_trial")},"Trial")/B{r0+2}', f'=COUNTIFS({mfd},">="&DATE(2024,1,1),{mfd},"<"&{DEZ},{Rg("Base_Assinaturas","f_trial")},"Trial")/C{r0+2}', '0%'),
       ('% Enterprise', f'=COUNTIFS({mfd},{DEZ},{Rg("Base_Assinaturas","f_plano")},"Enterprise")/B{r0+2}', f'=COUNTIFS({mfd},">="&DATE(2024,1,1),{mfd},"<"&{DEZ},{Rg("Base_Assinaturas","f_plano")},"Enterprise")/C{r0+2}', '0%'),
       ('MRR encerrado (US$)', f'=SUMIFS({Rg("Base_Assinaturas","mrr_amount")},{mfd},{DEZ})', f'=SUMIFS({Rg("Base_Assinaturas","mrr_amount")},{mfd},">="&DATE(2024,1,1),{mfd},"<"&{DEZ})', '#,##0')]
for i, (lab, f1, f2, fm) in enumerate(ind):
    rr = r0 + 2 + i; cell(ws, rr, 1, lab, bold=True); cell(ws, rr, 2, f1, fm); cell(ws, rr, 3, f2, fm)
ws.cell(r0 + 9, 1, 'Leitura: dezembro mistura dois efeitos. (1) Muitas assinaturas novas encerrando em poucos dias (efeito do período). (2) Concentração anormal em 29–31/12, que pode ser fechamento de ano / renovação anual ou corte da extração: confirmar com a área antes de tratar como churn de cliente.').font = Fn(italic=True, size=9, color=GRAY)
ws.column_dimensions['A'].width = 30; ws.column_dimensions['B'].width = 16; ws.column_dimensions['C'].width = 18; ws.column_dimensions['D'].width = 10

# ---- Sinais_no_tempo ----
ws = tm
ws['A1'] = 'Sinais no tempo: churn subiu; suporte e uso não acompanharam'; ws['A1'].font = Fn(bold=True, size=15)
ws['A2'] = 'Tudo por fórmula sobre as bases. Datas de ticket e de uso têm problemas de coerência com a conta (ver 01_Evidencias); aqui olhamos só a tendência do mês, sem ligar a conta.'; ws['A2'].font = Fn(italic=True, size=9, color=GRAY)
hdr(ws, 4, ['Mês', 'Assinaturas iniciadas', 'Iniciadas que encerraram em 30 dias', '% encerra em 30 dias (coorte do mês)', 'Tickets', 'Satisfação média', 'Resolução média (h)', '1ª resposta média (min)', '% escalados', 'Uso total (usage_count)', 'Erros por 100 usos'],
    [HD, HB, HB, HB, HC, HC, HC, HC, HC, HA, HA], 54)
sd = Rg('Base_Assinaturas', 'start_date'); tmm = Rg('Base_Tickets', 'mes'); um = Rg('Base_Uso', 'mes')
for i, m in enumerate(pd.date_range('2023-01-01', '2024-11-01', freq='MS')):
    rr = 5 + i; nm = f'EDATE(A{rr},1)'
    cell(ws, rr, 1, m.to_pydatetime(), 'mmm/yy')
    cell(ws, rr, 2, f'=COUNTIFS({sd},">="&A{rr},{sd},"<"&{nm})', '#,##0'); cell(ws, rr, 3, f'=SUMIFS({enc},{sd},">="&A{rr},{sd},"<"&{nm})', '#,##0'); cell(ws, rr, 4, f'=IF(B{rr}>0,C{rr}/B{rr},"")', '0.0%')
    cell(ws, rr, 5, f'=COUNTIFS({tmm},A{rr})', '#,##0'); cell(ws, rr, 6, f'=IFERROR(AVERAGEIFS({Rg("Base_Tickets","satisfaction_score")},{tmm},A{rr}),"")', '0.00')
    cell(ws, rr, 7, f'=IFERROR(AVERAGEIFS({Rg("Base_Tickets","resolution_time_hours")},{tmm},A{rr}),"")', '0.0'); cell(ws, rr, 8, f'=IFERROR(AVERAGEIFS({Rg("Base_Tickets","first_response_time_minutes")},{tmm},A{rr}),"")', '0.0')
    cell(ws, rr, 9, f'=IFERROR(AVERAGEIFS({Rg("Base_Tickets","escalado")},{tmm},A{rr}),"")', '0%'); cell(ws, rr, 10, f'=SUMIFS({Rg("Base_Uso","usage_count")},{um},A{rr})', '#,##0')
    cell(ws, rr, 11, f'=IFERROR(SUMIFS({Rg("Base_Uso","error_count")},{um},A{rr})/J{rr}*100,"")', '0.00')
lt = 5 + 22
ws.cell(lt + 1, 1, 'Coortes até nov/24 (dez/24 ainda não teve 30 dias). Leitura: % que encerra em 30 dias sobe a partir de jul/24; satisfação, tempos de atendimento, escalação, uso e erros ficam estáveis. O CS está certo (satisfação ok) e o produto também (uso não caiu), mas nenhum desses indicadores acompanha o churn.').font = Fn(italic=True, size=9, color=GRAY)
for chd in [(4, 'A', '% de assinaturas novas que encerram em 30 dias, por mês de início', '2A78D6', '0%'), (6, 'A', 'Satisfação média dos tickets por mês', 'EB6834', '0.0'), (10, 'A', 'Uso total por mês (usage_count)', '1BAF7A', '#,##0')]:
    col_, _, ttl, cor, nf = chd
    ch = LineChart(); ch.title = ttl; ch.height = 6.5; ch.width = 17; ch.legend = None
    ch.add_data(Reference(ws, min_col=col_, min_row=4, max_row=lt), titles_from_data=True); ch.set_categories(Reference(ws, min_col=1, min_row=5, max_row=lt))
    ch.series[0].graphicalProperties.line.solidFill = cor; ch.series[0].graphicalProperties.line.width = 22000; ch.x_axis.number_format = 'mmm/yy'; ch.y_axis.number_format = nf
    ws.add_chart(ch, {4: 'M4', 6: 'M18', 10: 'M32'}[col_])
ws.column_dimensions['A'].width = 10
for j in range(2, 12): ws.column_dimensions[L(j)].width = 12

# ---- Subconjunto_limpo ----
ws = sl
ws['A1'] = 'Subconjunto limpo: 100 contas em que as 3 marcações concordam'; ws['A1'].font = Fn(bold=True, size=15)
ws['A2'] = '50 contas com churn nas 3 definições (churn_flag, evento e assinatura encerrada) vs 50 sem churn em nenhuma. Médias por fórmula; p = permutação (5.000 sorteios) entre os dois grupos limpos.'; ws['A2'].font = Fn(italic=True, size=9, color=GRAY)
hdr(ws, 4, ['Indicador', 'Churn (3 concordam)', 'Ativa (3 concordam)', 'Divergente (400)', 'Diferença (churn − ativa)', 'p (churn vs ativa)', 'Leitura'], [HD, HC, HB, HA, HD, HD, HD])
gr = Rg('Base_Contas', 'grupo')
cell(ws, 5, 1, 'Contas', bold=True)
for j, gname in enumerate(['Churn (3 concordam)', 'Ativa (3 concordam)', 'Divergente'], 2): cell(ws, 5, j, f'=COUNTIFS({gr},"{gname}")', '#,##0', True)
for i, (col, lab) in enumerate(METR):
    rr = 6 + i; pct = col in ('teve_upgrade', 'teve_downgrade', 'is_devtools', 'is_partner', 'pct_assin_2024S2'); fm = '0%' if pct else ('#,##0' if col in ('mrr_ativo', 'uso_total') else '0.00')
    cell(ws, rr, 1, lab, bold=True)
    for j, gname in enumerate(['Churn (3 concordam)', 'Ativa (3 concordam)', 'Divergente'], 2): cell(ws, rr, j, f'=IFERROR(AVERAGEIFS({Rg("Base_Contas",col)},{gr},"{gname}"),"")', fm)
    cell(ws, rr, 5, f'=B{rr}-C{rr}', ('+0%;-0%' if pct else ('+#,##0;-#,##0' if fm == '#,##0' else '+0.00;-0.00'))); cell(ws, rr, 6, round(pclean[col], 4), '0.000')
    cell(ws, rr, 7, f'=IF(F{rr}<0.05,"Diferença além do acaso","Sem diferença detectável")')
lr = 6 + len(METR) - 1
ws.conditional_formatting.add(f'F6:F{lr}', CellIsRule(operator='lessThan', formula=['0.05'], fill=YEL))
rr = lr + 2
ws.cell(rr, 1, 'churn_flag por indústria na base toda (500 contas)').font = Fn(bold=True, size=11); rr += 1
hdr(ws, rr, ['Indústria', 'Contas', 'Com churn_flag', '% churn_flag'], [HD, HD, HD, HD]); rr += 1
for ind_ in sorted(K.industry.unique()):
    cell(ws, rr, 1, ind_, bold=True); cell(ws, rr, 2, f'=COUNTIFS({Rg("Base_Contas","industry")},A{rr})', '#,##0'); cell(ws, rr, 3, f'=COUNTIFS({Rg("Base_Contas","industry")},A{rr},{Rg("Base_Contas","churn_flag")},TRUE)', '#,##0'); cell(ws, rr, 4, f'=C{rr}/B{rr}', '0%'); rr += 1
rr += 1
for tx in ['Leitura: as contas "limpas" são parecidas em receita, erros, tickets e satisfação. Diferenças que aparecem: mais assinaturas e mais uso no grupo churn (mecânico: quem tem mais assinaturas tem mais chance de ter uma encerrada e soma mais registros de uso), concentração em DevTools e pouca presença do canal partner.',
           'Cuidado: o grupo "churn" exige churn_flag = TRUE, e o churn_flag já é concentrado em DevTools na base toda (tabela acima). Como receita (P1/P2) e eventos (S1) NÃO mostram DevTools diferente (02_Triangulacao), isso é efeito do churn_flag, não confirmação independente.',
           'Amostra pequena (50 vs 50): serve para checar o que foi achado na base toda, não para descobrir causas novas.']:
    ws.cell(rr, 1, tx).font = Fn(italic=True, size=9, color=GRAY); rr += 1
ws.column_dimensions['A'].width = 36
for c_ in 'BCDEF': ws.column_dimensions[c_].width = 15
ws.column_dimensions['G'].width = 26

# ---- LEIA-ME ----
ws = leia; ws.column_dimensions['A'].width = 3; ws.column_dimensions['B'].width = 125
Lm = [('Passo 3 da reconciliação: o que mudou no 2º semestre de 2024 e em dezembro?', dict(bold=True, size=15)),
      ('Planilha apartada. Lê os CSVs originais sem alterá-los. Base principal = assinaturas (01_Evidencias); ponto de partida = aba Tempo de 02_Triangulacao.', dict(italic=True, color=GRAY)),
      ('', {}), ('PERGUNTAS', dict(bold=True, size=12)),
      ('1. As assinaturas que entraram em 2024-S2 são de outro tipo (plano, cliente, canal…) ou o mesmo tipo de assinatura passou a cancelar mais?  → aba Coorte_x_Fator', {}),
      ('2. O que há de diferente em dezembro/2024?  → aba Dezembro', {}),
      ('3. Suporte e uso pioraram junto com o churn?  → aba Sinais_no_tempo', {}),
      ('4. O que diferencia as contas em que as 3 marcações concordam?  → aba Subconjunto_limpo', {}),
      ('', {}), ('RESPOSTAS', dict(bold=True, size=12)),
      ('1. Mesmo tipo de assinatura, cancelando mais. A taxa de encerramento em 30 dias sobe de ~0,7% para ~4,2% (cerca de 6x) em praticamente todas as categorias de plano, cobrança, trial, seats, indústria, país, canal e idade da conta. O mix muda um pouco em alguns fatores, mas, mantidas as taxas antigas, essa mudança explicaria quase nada do aumento (coluna O). É um efeito do período, não do mix.', {}),
      ('2. Dezembro soma o efeito do período (muitas assinaturas novas encerrando em poucos dias) com uma concentração anormal de encerramentos em 29–31/12. Essa concentração precisa ser confirmada com a área (fechamento de ano, renovação, corte da extração) antes de ser lida como perda de cliente.', {}),
      ('3. Não. Satisfação, tempo de resolução, primeira resposta, escalação, uso e erros ficam estáveis enquanto o churn sobe. Por isso "CS diz que a satisfação está ok" e "produto diz que o uso cresceu" não contradizem o churn: esses indicadores simplesmente não captam o que está mudando.', {}),
      ('4. Contas limpas são parecidas em quase tudo. Mais assinaturas e mais uso no grupo churn é efeito mecânico; a concentração em DevTools vem do próprio churn_flag e não é confirmada por receita nem eventos.', {}),
      ('', {}), ('IMPLICAÇÃO PARA O DIAGNÓSTICO', dict(bold=True, size=12)),
      ('A causa raiz provável é um evento do período (a partir de jul/24) que afeta assinaturas novas de todos os perfis nos primeiros 30 dias: algo no produto, preço, cobrança, onboarding ou concorrência. Estas 5 tabelas não registram esse evento; o próximo passo é buscar fora delas (changelog de produto, mudanças de preço/cobrança, campanhas) e cruzar as datas.', {}),
      ('', {}), ('LIMITES', dict(bold=True, size=12)),
      ('• Base sintética. Coortes recentes têm menos tempo de observação (por isso o corte de 30 dias observáveis).', {}),
      ('• p-valores (Fisher exato, permutação) são calculados no script; contagens, % e médias são fórmulas sobre as abas Base_*.', {})]
for i, (tx, st) in enumerate(Lm, 1):
    x = ws.cell(i, 2, tx); x.font = Fn(**st) if st else Fn(); x.alignment = Alignment(wrap_text=True, vertical='top')
wb.calculation.fullCalcOnLoad = True; wb.active = 1
OUT.parent.mkdir(parents=True, exist_ok=True); wb.save(OUT); print('ok', OUT)
print(CP.to_string()); print({k: round(v, 4) for k, v in pclean.items()}); print(flag_ind.round(3).to_dict())
