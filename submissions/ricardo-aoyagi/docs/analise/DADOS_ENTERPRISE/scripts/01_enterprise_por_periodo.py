# ENTERPRISE como centro da investigação, em 4 períodos: 2023 · jan–jun/24 · jul–out/24 · nov–dez/24.
# Preço/seats, reduções no tempo, "regressão de plano", features, reclamações e perfil (indústria/canal/país) de quem reduziu.
# Gerado com Claude (IA). Lê os CSVs originais sem alterá-los; grava planilha apartada.
import sys
from pathlib import Path
from math import lgamma, exp, log
import pandas as pd, numpy as np
RAIZ = Path(__file__).resolve().parents[3]
DADOS = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / 'dados'
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else RAIZ / 'analise' / 'DADOS_ENTERPRISE' / '01_Enterprise_por_Periodo.xlsx'
JP = 7; MES = 30.4375
PER = [('1. 2023', '2023-01-01', '2023-12-31', 12), ('2. Jan–Jun/24', '2024-01-01', '2024-06-30', 6), ('3. Jul–Out/24', '2024-07-01', '2024-10-31', 4), ('4. Nov–Dez/24', '2024-11-01', '2024-12-31', 2)]
PN = [p[0] for p in PER]; PLANOS = ['Basic', 'Pro', 'Enterprise']
a = pd.read_csv(DADOS/'ravenstack_accounts.csv'); s = pd.read_csv(DADOS/'ravenstack_subscriptions.csv', parse_dates=['start_date','end_date'])
f = pd.read_csv(DADOS/'ravenstack_feature_usage.csv'); t = pd.read_csv(DADOS/'ravenstack_support_tickets.csv', parse_dates=['submitted_at'])

# ---------- utilidades ----------
def lbin(n, k, p): return lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1) + (k * log(p) if k else 0) + ((n - k) * log(1 - p) if n - k else 0)
def p_taxas(k1, e1, k2, e2):
    """compara duas taxas (casos ÷ exposição): teste exato condicional (binomial)."""
    n = k1 + k2
    if n == 0: return 1.0
    p = e1 / (e1 + e2); p0 = exp(lbin(n, k1, p))
    return min(1.0, sum(exp(lbin(n, k, p)) for k in range(n + 1) if exp(lbin(n, k, p)) <= p0 * (1 + 1e-7)))
def conf_taxa(k1, e1, k2, e2):
    if k1 + k2 < 10: return 'Poucos casos para concluir'
    return 'Sim' if p_taxas(k1, e1, k2, e2) < 0.05 else 'Não (pode ser coincidência)'
def fisher_p(a_, b_, c_, d_):
    n1, n2, m1 = a_ + b_, c_ + d_, a_ + c_; N = n1 + n2
    if N == 0 or n1 == 0 or n2 == 0 or m1 == 0 or m1 == N: return 1.0
    lc = lambda n, k: lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)
    pmf = lambda x: exp(lc(n1, x) + lc(n2, m1 - x) - lc(N, m1)); p0 = pmf(a_); lo, hi = max(0, m1 - n2), min(m1, n1)
    return min(1.0, sum(pmf(x) for x in range(lo, hi + 1) if pmf(x) <= p0 * (1 + 1e-7)))
def conf(k1, n1, k2, n2):
    if k1 + k2 < 10: return 'Poucos casos para concluir'
    return 'Sim' if fisher_p(k1, n1 - k1, k2, n2 - k2) < 0.05 else 'Não (pode ser coincidência)'
def periodo(d):
    if pd.isna(d): return ''
    for n, i0, i1, _ in PER:
        if pd.Timestamp(i0) <= d <= pd.Timestamp(i1): return n
    return ''

# ---------- situação de cada assinatura encerrada (mesma regra das planilhas anteriores) ----------
def tipo(r):
    o = s[(s.account_id == r.account_id) & (s.subscription_id != r.subscription_id)]
    at = o[(o.start_date <= r.end_date) & (o.end_date.isna() | (o.end_date > r.end_date))]
    pe = o[(o.start_date - r.end_date).abs().dt.days <= JP]; de = o[(o.start_date > r.end_date) & (o.start_date <= r.end_date + pd.Timedelta(days=JP))]
    if len(at) == 0 and len(de) == 0: return 'Saída do cliente'
    return 'Migração' if len(pe) else 'Redução'
s['situacao'] = 'Ativa'; m = s.end_date.notna(); s.loc[m, 'situacao'] = s[m].apply(tipo, axis=1)
S = s.merge(a[['account_id', 'industry', 'country', 'referral_source']], on='account_id')
S['periodo_inicio'] = S.start_date.apply(periodo); S['periodo_fim'] = S.end_date.apply(periodo)
S['cobranca'] = S.billing_frequency.map({'annual': 'Anual', 'monthly': 'Mensal'}); S['trial'] = np.where(S.is_trial, 'Sim', 'Não')
S['preco_por_seat'] = np.where(S.mrr_amount > 0, S.mrr_amount / S.seats, np.nan)      # MRR já é mensal; para anual, ARR ÷ 12 = MRR (conferido: ARR = 12 × MRR em 100%)
S['arr_div_12_por_seat'] = np.where(S.arr_amount > 0, S.arr_amount / 12 / S.seats, np.nan)
for n, i0, i1, _ in PER:   # assinaturas-mês ativas em cada período (exposição)
    i0, i1 = pd.Timestamp(i0), pd.Timestamp(i1) + pd.Timedelta(days=1)
    ini = S.start_date.clip(lower=i0); fim = S.end_date.fillna(pd.Timestamp('2025-01-01')).clip(upper=i1)
    S[f'meses_ativos_{n[:1]}'] = ((fim - ini).dt.days.clip(lower=0) / MES).round(3)
S['reduzida'] = (S.situacao == 'Redução').astype(int); S['mrr_reduzido'] = S.mrr_amount * S.reduzida
# depois de uma redução Enterprise, a conta ainda tem outra Enterprise ativa?
def resto(r):
    if not (r.plan_tier == 'Enterprise' and r.situacao == 'Redução'): return pd.Series({'outras_enterprise_ativas': None, 'outras_basic_pro_ativas': None, 'apos_reducao': ''})
    o = s[(s.account_id == r.account_id) & (s.subscription_id != r.subscription_id) & (s.start_date <= r.end_date) & (s.end_date.isna() | (s.end_date > r.end_date))]
    e = int((o.plan_tier == 'Enterprise').sum()); bp = int((o.plan_tier != 'Enterprise').sum())
    return pd.Series({'outras_enterprise_ativas': e, 'outras_basic_pro_ativas': bp, 'apos_reducao': 'Seguiu com outra Enterprise' if e else ('Ficou só com Basic/Pro' if bp else 'Ficou sem assinatura')})
S = pd.concat([S, S.apply(resto, axis=1)], axis=1)
# ---------- uso por feature (Enterprise), ligado ao período de INÍCIO da assinatura ----------
E = S[S.plan_tier == 'Enterprise']
FU = f.merge(E[['subscription_id', 'periodo_inicio', 'situacao']], on='subscription_id').groupby(['subscription_id', 'periodo_inicio', 'situacao', 'feature_name']).agg(
    registros=('usage_id', 'size'), registros_com_erro=('error_count', lambda x: int((x > 0).sum())), registros_beta=('is_beta_feature', 'sum')).reset_index()
FU['feature_num'] = FU.feature_name.str.replace('feature_', '').astype(int)
FEATS = sorted(FU.feature_name.unique(), key=lambda z: int(z.split('_')[1]))
# ---------- tickets: contas Enterprise no período ----------
T = t.copy(); T['periodo'] = T.submitted_at.apply(periodo)
ent_acc = {n: set(E[E[f'meses_ativos_{n[:1]}'] > 0].account_id) for n in PN}
red_acc = {n: set(E[(E.situacao == 'Redução') & (E.periodo_fim == n)].account_id) for n in PN}
T['conta_enterprise_no_periodo'] = [('Sim' if (p and r.account_id in ent_acc[p]) else 'Não') for p, r in zip(T.periodo, T.itertuples())]
T['conta_reduziu_enterprise_no_periodo'] = [('Sim' if (p and r.account_id in red_acc[p]) else 'Não') for p, r in zip(T.periodo, T.itertuples())]
T['escalado'] = np.where(T.escalation_flag, 'Sim', 'Não'); T['respondeu_satisfacao'] = np.where(T.satisfaction_score.notna(), 'Sim', 'Não')
CT = pd.DataFrame([dict(periodo=n, contas_enterprise=len(ent_acc[n]), contas_que_reduziram=len(red_acc[n])) for n in PN])

# ======================== planilha ========================
from openpyxl import Workbook
from openpyxl.utils import get_column_letter as L
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import CellIsRule, ColorScaleRule
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.chart import BarChart, LineChart, Reference
FONT = 'Arial'; GRAY = '52514E'; Fn = lambda **k: Font(name=FONT, **k)
HD = PatternFill('solid', fgColor='1F2937'); HE = PatternFill('solid', fgColor='0F766E'); HB = PatternFill('solid', fgColor='2A78D6'); HP = PatternFill('solid', fgColor='7C3AED'); HR = PatternFill('solid', fgColor='B45309'); HX = PatternFill('solid', fgColor='374151')
YEL = PatternFill('solid', fgColor='FFF3CD'); GRY = PatternFill('solid', fgColor='EDEDED')
thin = Side(style='thin', color='D0D0D0'); BOX = Border(top=thin, bottom=thin, left=thin, right=thin)
USD = '"US$ "#,##0;-"US$ "#,##0;"-"'; USD2 = '"US$ "#,##0.00'
wb = Workbook(); wb.remove(wb.active)
def S_(n): ws = wb.create_sheet(n); ws.sheet_view.showGridLines = False; return ws
leia = S_('LEIA-ME'); w1 = S_('1_Preco_e_Seats'); w2 = S_('2_Reducoes_no_tempo'); w3 = S_('3_Regressao_de_plano'); w4 = S_('4_Features'); w5 = S_('5_Reclamacoes'); w6 = S_('6_Perfil_das_reducoes'); w7 = S_('7_Lista_Reducoes')
BS = {}
def py(v):
    if v is None or v is pd.NaT or (isinstance(v, float) and np.isnan(v)): return None
    if isinstance(v, pd.Timestamp): return v.to_pydatetime()
    return v.item() if hasattr(v, 'item') else v
def base(nome, df, cols, fmts):
    ws = wb.create_sheet(nome); ws.append(cols)
    for row in df[cols].itertuples(index=False): ws.append([py(v) for v in row])
    n = len(df) + 1; BS[nome] = (cols, n)
    for i, cn in enumerate(cols, 1):
        h = ws.cell(1, i); h.font = Fn(bold=True, color='FFFFFF', size=9); h.fill = HD; ws.column_dimensions[L(i)].width = max(11, min(22, len(cn) + 2))
        if cn in fmts:
            for r in range(2, n + 1): ws.cell(r, i).number_format = fmts[cn]
    tb = Table(displayName='t' + nome, ref=f'A1:{L(len(cols))}{n}'); tb.tableStyleInfo = TableStyleInfo(name='TableStyleLight1', showRowStripes=True); ws.add_table(tb); ws.freeze_panes = 'B2'
def Rg(b, col): cols, n = BS[b]; i = cols.index(col) + 1; return f"{b}!${L(i)}$2:${L(i)}${n}"
D = 'dd/mm/yyyy'
colsS = ['subscription_id', 'account_id', 'industry', 'country', 'referral_source', 'plan_tier', 'cobranca', 'trial', 'seats', 'mrr_amount', 'arr_amount', 'preco_por_seat', 'arr_div_12_por_seat',
         'start_date', 'end_date', 'periodo_inicio', 'periodo_fim', 'situacao', 'reduzida', 'mrr_reduzido', 'meses_ativos_1', 'meses_ativos_2', 'meses_ativos_3', 'meses_ativos_4', 'apos_reducao']
base('Base_Assinaturas', S, colsS, {'start_date': D, 'end_date': D, 'mrr_amount': USD, 'arr_amount': USD, 'mrr_reduzido': USD, 'preco_por_seat': USD2, 'arr_div_12_por_seat': USD2})
base('Base_Uso_Enterprise', FU, ['subscription_id', 'periodo_inicio', 'situacao', 'feature_name', 'feature_num', 'registros', 'registros_com_erro', 'registros_beta'], {})
base('Base_Tickets', T, ['ticket_id', 'account_id', 'submitted_at', 'periodo', 'priority', 'escalado', 'satisfaction_score', 'respondeu_satisfacao', 'conta_enterprise_no_periodo', 'conta_reduziu_enterprise_no_periodo'], {'submitted_at': D})
base('Base_Contas_Periodo', CT, ['periodo', 'contas_enterprise', 'contas_que_reduziram'], {})
BA = 'Base_Assinaturas'; PLc, PIc, PFc, SIc = Rg(BA, 'plan_tier'), Rg(BA, 'periodo_inicio'), Rg(BA, 'periodo_fim'), Rg(BA, 'situacao')
def H(ws, row, labels, fills, h=46):
    for j, (x, fl) in enumerate(zip(labels, fills), 1):
        c_ = ws.cell(row, j, x); c_.font = Fn(bold=True, color='FFFFFF', size=9); c_.fill = fl; c_.alignment = Alignment(wrap_text=True, horizontal='center', vertical='center'); c_.border = BOX
    ws.row_dimensions[row].height = h
def C(ws, r, c_, v, fmt=None, bold=False, fill=None):
    x = ws.cell(r, c_, v); x.font = Fn(size=9, bold=bold); x.border = BOX; x.alignment = Alignment(vertical='center', wrap_text=True)
    if fmt: x.number_format = fmt
    if fill: x.fill = fill
    return x
def title(ws, t1, t2, merge='J'):
    ws['A1'] = t1; ws['A1'].font = Fn(bold=True, size=15); ws['A2'] = t2; ws['A2'].font = Fn(italic=True, size=9, color=GRAY); ws['A2'].alignment = Alignment(wrap_text=True); ws.merge_cells(f'A2:{merge}2'); ws.row_dimensions[2].height = 32
def note(ws, r, tx, merge='J', h=34, color=GRAY):
    ws.cell(r, 1, tx).font = Fn(italic=True, size=9, color=color); ws.cell(r, 1).alignment = Alignment(wrap_text=True, vertical='top'); ws.merge_cells(f'A{r}:{merge}{r}'); ws.row_dimensions[r].height = h
FILLP = {'Basic': HB, 'Pro': HP, 'Enterprise': HE}

# ---------- 1_Preco_e_Seats ----------
ws = w1; title(ws, 'Houve aumento de preço? O que mudou em seats e valor das assinaturas Enterprise?', 'Assinaturas PAGAS iniciadas em cada período (trials têm MRR zero e ficam de fora do preço). Preço por seat = MRR ÷ seats; para anual também conferimos ARR ÷ 12 ÷ seats.')
H(ws, 4, ['Período de início', 'Plano', 'Assinaturas pagas iniciadas', 'Preço por seat: mínimo', 'Preço por seat: médio', 'Preço por seat: máximo', 'Anual: ARR ÷ 12 ÷ seats (médio)', 'Seats por assinatura (média)', 'MRR por assinatura (média)', '% anual', '% trial (entre todas as iniciadas)'],
  [HD, HD, HD, HE, HE, HE, HE, HX, HX, HX, HX]); r = 5; rows_ent = []
PS, AR = Rg(BA, 'preco_por_seat'), Rg(BA, 'arr_div_12_por_seat'); TR = Rg(BA, 'trial')
for pl in PLANOS:
    for n in PN:
        cd = f'{PIc},"{n}",{PLc},"{pl}",{TR},"Não"'
        C(ws, r, 1, n, bold=True); C(ws, r, 2, pl, bold=True); ws.cell(r, 2).fill = FILLP[pl]; ws.cell(r, 2).font = Fn(size=9, bold=True, color='FFFFFF')
        C(ws, r, 3, f'=COUNTIFS({cd})', '#,##0'); C(ws, r, 4, f'=_xlfn.MINIFS({PS},{cd})', USD2); C(ws, r, 5, f'=AVERAGEIFS({PS},{cd})', USD2); C(ws, r, 6, f'=_xlfn.MAXIFS({PS},{cd})', USD2)
        C(ws, r, 7, f'=AVERAGEIFS({AR},{cd},{Rg(BA,"cobranca")},"Anual")', USD2); C(ws, r, 8, f'=AVERAGEIFS({Rg(BA,"seats")},{cd})', '0.0'); C(ws, r, 9, f'=AVERAGEIFS({Rg(BA,"mrr_amount")},{cd})', USD)
        C(ws, r, 10, f'=COUNTIFS({cd},{Rg(BA,"cobranca")},"Anual")/C{r}', '0%'); C(ws, r, 11, f'=COUNTIFS({PIc},"{n}",{PLc},"{pl}",{TR},"Sim")/COUNTIFS({PIc},"{n}",{PLc},"{pl}")', '0%')
        if pl == 'Enterprise': rows_ent.append(r)
        r += 1
    r += 1
note(ws, r, 'Leitura: o preço por seat é exatamente o mesmo em todos os períodos e em todas as assinaturas (Enterprise US$ 199, Pro US$ 49, Basic US$ 19), mensal ou anual (ARR ÷ 12 dá o mesmo valor). NÃO houve aumento de preço nesta base. O que varia de um período para outro é o número de seats por assinatura, e com ele o valor de cada assinatura.', merge='K', h=44)
for col_, w in zip('ABCDEFGHIJK', [15, 11, 11, 11, 11, 11, 13, 11, 13, 8, 11]): ws.column_dimensions[col_].width = w
ch = BarChart(); ch.type = 'col'; ch.title = 'Enterprise: seats por assinatura iniciada, por período'; ch.height = 6.5; ch.width = 13; ch.legend = None
ch.add_data(Reference(ws, min_col=8, min_row=rows_ent[0], max_row=rows_ent[-1]), titles_from_data=False); ch.set_categories(Reference(ws, min_col=1, min_row=rows_ent[0], max_row=rows_ent[-1])); ch.series[0].graphicalProperties.solidFill = '0F766E'; ch.y_axis.scaling.min = 0; ws.add_chart(ch, 'M4')
ch = BarChart(); ch.type = 'col'; ch.title = 'Enterprise: preço por seat (médio), por período'; ch.height = 6.5; ch.width = 13; ch.legend = None
ch.add_data(Reference(ws, min_col=5, min_row=rows_ent[0], max_row=rows_ent[-1]), titles_from_data=False); ch.set_categories(Reference(ws, min_col=1, min_row=rows_ent[0], max_row=rows_ent[-1])); ch.series[0].graphicalProperties.solidFill = '0F766E'
ch.y_axis.scaling.min = 0; ws.add_chart(ch, 'M18')

# ---------- 2_Reducoes_no_tempo ----------
ws = w2; title(ws, 'As reduções Enterprise aumentaram ao longo do tempo? Foi só no Enterprise?', 'Reduções = assinaturas encerradas sem reposição em até 7 dias, com a conta seguindo cliente. Como os períodos têm tamanhos diferentes, a taxa é "reduções a cada 100 assinaturas ativas por mês" (assinaturas-mês).')
H(ws, 4, ['Período', 'Plano', 'Assinaturas-mês ativas', 'Reduções no período', 'Reduções a cada 100 assinaturas por mês', 'MRR perdido em reduções', 'MRR perdido por mês', 'Migrações no período', 'Comparado aos períodos anteriores do mesmo plano: diferente?', 'Comparado a Basic+Pro no mesmo período: diferente?'],
  [HD, HD, HX, HR, HR, HR, HR, HX, HX, HX]); r = 5; rr = {}
for pl in PLANOS:
    for i, (n, _, _, mo) in enumerate(PER):
        col = f'meses_ativos_{n[:1]}'
        k1 = int(((S.plan_tier == pl) & (S.situacao == 'Redução') & (S.periodo_fim == n)).sum()); e1 = float(S[S.plan_tier == pl][col].sum())
        prev = PN[:i]
        if prev:
            k2 = int(((S.plan_tier == pl) & (S.situacao == 'Redução') & (S.periodo_fim.isin(prev))).sum()); e2 = float(sum(S[S.plan_tier == pl][f'meses_ativos_{q[:1]}'].sum() for q in prev)); cprev = conf_taxa(k1, e1, k2, e2)
        else: cprev = '—'
        k3 = int(((S.plan_tier != pl) & (S.situacao == 'Redução') & (S.periodo_fim == n)).sum()); e3 = float(S[S.plan_tier != pl][col].sum())
        C(ws, r, 1, n, bold=True); C(ws, r, 2, pl, bold=True); ws.cell(r, 2).fill = FILLP[pl]; ws.cell(r, 2).font = Fn(size=9, bold=True, color='FFFFFF')
        C(ws, r, 3, f'=SUMIFS({Rg(BA, col)},{PLc},"{pl}")', '#,##0'); C(ws, r, 4, f'=COUNTIFS({PLc},"{pl}",{SIc},"Redução",{PFc},"{n}")', '#,##0'); C(ws, r, 5, f'=D{r}/C{r}*100', '0.00')
        C(ws, r, 6, f'=SUMIFS({Rg(BA,"mrr_reduzido")},{PLc},"{pl}",{PFc},"{n}")', USD); C(ws, r, 7, f'=F{r}/{mo}', USD); C(ws, r, 8, f'=COUNTIFS({PLc},"{pl}",{SIc},"Migração",{PFc},"{n}")', '#,##0')
        C(ws, r, 9, cprev); C(ws, r, 10, conf_taxa(k1, e1, k3, e3) if pl == 'Enterprise' else '—'); rr[(pl, n)] = r; r += 1
    r += 1
ws.conditional_formatting.add(f'I5:J{r}', CellIsRule(operator='equal', formula=['"Sim"'], fill=YEL))
note(ws, r, 'Leitura: a taxa de redução do Enterprise sobe com o tempo, com o maior valor em nov–dez/24. Mas ela sobe também em Basic e Pro, e o Enterprise não fica diferente dos outros planos em nenhum período. O que pesa no Enterprise é o valor: em nov–dez/24 a perda por mês em reduções Enterprise é cerca de 7 vezes a de jul–out/24 — o dobro de reduções por mês e assinaturas reduzidas maiores (MRR médio ≈ US$ 6,5 mil, contra ≈ US$ 3,8 mil). Das 44 reduções de nov–dez, 33 foram em dezembro e 12 só entre 29 e 31/12.', merge='J', h=40)
for col_, w in zip('ABCDEFGHIJ', [15, 11, 12, 11, 13, 14, 13, 11, 24, 24]): ws.column_dimensions[col_].width = w
ch = LineChart(); ch.title = 'Reduções a cada 100 assinaturas por mês, por plano'; ch.height = 7.5; ch.width = 16
for pl, cor in zip(PLANOS, ['2A78D6', '7C3AED', '0F766E']):
    ch.add_data(Reference(ws, min_col=5, min_row=rr[(pl, PN[0])], max_row=rr[(pl, PN[-1])]), titles_from_data=False); ch.series[-1].tx = None
    from openpyxl.chart.series import SeriesLabel
    ch.series[-1].tx = SeriesLabel(v=pl); ch.series[-1].graphicalProperties.line.solidFill = cor; ch.series[-1].graphicalProperties.line.width = 22000
ch.set_categories(Reference(ws, min_col=1, min_row=rr[('Basic', PN[0])], max_row=rr[('Basic', PN[-1])])); ch.legend.position = 'b'; ws.add_chart(ch, 'L4')
ch = BarChart(); ch.type = 'col'; ch.title = 'Enterprise: MRR perdido em reduções por mês (US$)'; ch.height = 7; ch.width = 16; ch.legend = None
ch.add_data(Reference(ws, min_col=7, min_row=rr[('Enterprise', PN[0])], max_row=rr[('Enterprise', PN[-1])]), titles_from_data=False); ch.set_categories(Reference(ws, min_col=1, min_row=rr[('Enterprise', PN[0])], max_row=rr[('Enterprise', PN[-1])]))
ch.series[0].graphicalProperties.solidFill = 'B45309'; ch.y_axis.number_format = '#,##0'; ws.add_chart(ch, 'L20')

# ---------- 3_Regressao_de_plano ----------
ws = w3; title(ws, 'Quem reduziu uma assinatura Enterprise deixou de ser cliente Enterprise?', 'Para cada redução Enterprise, olhamos as outras assinaturas ativas da conta no dia: ainda tinha outra Enterprise, ou ficou só com Basic/Pro?', merge='H')
AP = Rg(BA, 'apos_reducao')
H(ws, 4, ['Período do fim', 'Reduções Enterprise', 'Seguiu com outra Enterprise', '%', 'Ficou só com Basic/Pro (regrediu de plano)', '%', 'Ficou sem assinatura', '%'], [HD, HR, HE, HE, HR, HR, HX, HX]); r = 5
for n in PN + ['Todos']:
    cd = f'{PLc},"Enterprise",{SIc},"Redução"' + (f',{PFc},"{n}"' if n != 'Todos' else '')
    fl = GRY if n == 'Todos' else None
    C(ws, r, 1, n, bold=True, fill=fl); C(ws, r, 2, f'=COUNTIFS({cd})', '#,##0', fill=fl)
    for j, v in zip((3, 5, 7), ['Seguiu com outra Enterprise', 'Ficou só com Basic/Pro', 'Ficou sem assinatura']):
        C(ws, r, j, f'=COUNTIFS({cd},{AP},"{v}")', '#,##0', fill=fl); C(ws, r, j + 1, f'=IF(B{r}>0,{L(j)}{r}/B{r},"")', '0%', fill=fl)
    r += 1
note(ws, r + 1, 'Leitura: em quase 9 de cada 10 reduções a conta continua com outra assinatura Enterprise ativa. É redução de contrato (menos assinaturas/seats Enterprise), não troca de plano: poucas contas "regridem" para ficar só com Basic/Pro.', merge='H')
for col_, w in zip('ABCDEFGH', [15, 12, 14, 7, 16, 7, 12, 7]): ws.column_dimensions[col_].width = w

# ---------- 4_Features ----------
UE = 'Base_Uso_Enterprise'; UPI, UFN, URG, URE = Rg(UE, 'periodo_inicio'), Rg(UE, 'feature_name'), Rg(UE, 'registros'), Rg(UE, 'registros_com_erro')
ws = w4; title(ws, 'Alguma feature apareceu no Enterprise só a partir de um período? Alguma passou a dar mais erro?', 'Período = período de INÍCIO da assinatura a que o uso está ligado (as datas de uso não são confiáveis). "% das assinaturas" = Enterprise iniciadas no período com ao menos 1 registro da feature.', merge='M')
H(ws, 4, ['Feature'] + [f'{n}: % das assinaturas' for n in PN] + ['Aparece em todos os períodos?'] + [f'{n}: % registros com erro' for n in PN] + ['Erro mudou entre 2023 e nov–dez/24? (confiável?)'],
  [HD] + [HE] * 4 + [HX] + [HR] * 4 + [HX], 58); r = 5; f0 = r
nE = {n: int((E.periodo_inicio == n).sum()) for n in PN}
for fe in FEATS:
    C(ws, r, 1, fe, bold=True)
    for j, n in enumerate(PN, 2): C(ws, r, j, f'=COUNTIFS({UPI},"{n}",{UFN},$A{r})/COUNTIFS({PIc},"{n}",{PLc},"Enterprise")', '0%')
    C(ws, r, 6, f'=IF(COUNTIF(B{r}:E{r},0)=0,"Sim","NÃO")')
    for j, n in enumerate(PN, 7): C(ws, r, j, f'=IFERROR(SUMIFS({URE},{UPI},"{n}",{UFN},$A{r})/SUMIFS({URG},{UPI},"{n}",{UFN},$A{r}),"")', '0%')
    x = FU[FU.feature_name == fe]; a1 = x[x.periodo_inicio == PN[0]]; a4 = x[x.periodo_inicio == PN[-1]]
    C(ws, r, 11, conf(int(a4.registros_com_erro.sum()), int(a4.registros.sum()), int(a1.registros_com_erro.sum()), int(a1.registros.sum()))); r += 1
fl = r - 1
ws.conditional_formatting.add(f'B{f0}:E{fl}', ColorScaleRule(start_type='min', start_color='FFFFFF', end_type='max', end_color='5EAAA8'))
ws.conditional_formatting.add(f'F{f0}:F{fl}', CellIsRule(operator='equal', formula=['"NÃO"'], fill=YEL)); ws.conditional_formatting.add(f'K{f0}:K{fl}', CellIsRule(operator='equal', formula=['"Sim"'], fill=YEL))
r += 1; H(ws, r, ['Resumo Enterprise'] + PN, [HD] + [HE] * 4, 30); r += 1
for lab, fx, fm in [('Assinaturas Enterprise iniciadas', lambda n: f'=COUNTIFS({PIc},"{n}",{PLc},"Enterprise")', '#,##0'),
                    ('% dos registros com erro', lambda n: f'=SUMIFS({URE},{UPI},"{n}")/SUMIFS({URG},{UPI},"{n}")', '0.0%'),
                    ('% dos registros em feature beta', lambda n: f'=SUMIFS({Rg(UE,"registros_beta")},{UPI},"{n}")/SUMIFS({URG},{UPI},"{n}")', '0.0%')]:
    C(ws, r, 1, lab, bold=True)
    for j, n in enumerate(PN, 2): C(ws, r, j, fx(n), fm)
    r += 1
note(ws, r + 1, 'Leitura: TODAS as 40 features aparecem no Enterprise desde 2023 (nenhuma "surge" num período posterior) e a proporção de erro total fica parecida ao longo do tempo (≈30%). Duas features têm mais erro depois de 2023 (feature_10 e feature_24: de ~15% para ~40% dos registros), mas existem desde 2023 e, entre 40 testes, 2 "Sim" podem ser acaso: vale checar com o time de produto. Nesta base, não há sinal de uma feature nova que explique as reduções. A marca "beta" é aleatória (≈10% dos registros de todas as features) e não identifica lançamento.', merge='K', h=44)
ws.column_dimensions['A'].width = 12
for j in range(2, 12): ws.column_dimensions[L(j)].width = 12
ws.column_dimensions['K'].width = 24; ws.freeze_panes = 'B5'

# ---------- 5_Reclamacoes ----------
BT = 'Base_Tickets'; TP_, TE_, TRd = Rg(BT, 'periodo'), Rg(BT, 'conta_enterprise_no_periodo'), Rg(BT, 'conta_reduziu_enterprise_no_periodo')
ws = w5; title(ws, 'As reclamações das contas Enterprise mudaram de um período para outro?', 'Tickets pela data de abertura, de contas que tinham assinatura Enterprise ativa no período. Atenção: 54% dos tickets da base têm data anterior ao cadastro da conta; use como tendência, não como prova.', merge='J')
CP = 'Base_Contas_Periodo'
H(ws, 4, ['Período', 'Contas Enterprise no período', 'Tickets', 'Tickets a cada 100 contas por mês', '% urgentes', '% escalados', 'Satisfação média (3 a 5)', '% sem nota de satisfação', 'Contas que reduziram Enterprise no período', 'Tickets dessas contas no período'],
  [HD, HE, HE, HE, HE, HE, HE, HE, HR, HR]); r = 5
for i, (n, _, _, mo) in enumerate(PER):
    cd = f'{TP_},"{n}",{TE_},"Sim"'
    C(ws, r, 1, n, bold=True); C(ws, r, 2, f'=INDEX({Rg(CP,"contas_enterprise")},MATCH(A{r},{Rg(CP,"periodo")},0))', '#,##0'); C(ws, r, 3, f'=COUNTIFS({cd})', '#,##0'); C(ws, r, 4, f'=C{r}/B{r}/{mo}*100', '0.0')
    C(ws, r, 5, f'=COUNTIFS({cd},{Rg(BT,"priority")},"urgent")/C{r}', '0%'); C(ws, r, 6, f'=COUNTIFS({cd},{Rg(BT,"escalado")},"Sim")/C{r}', '0%')
    C(ws, r, 7, f'=IFERROR(AVERAGEIFS({Rg(BT,"satisfaction_score")},{cd}),"")', '0.00'); C(ws, r, 8, f'=COUNTIFS({cd},{Rg(BT,"respondeu_satisfacao")},"Não")/C{r}', '0%')
    C(ws, r, 9, f'=INDEX({Rg(CP,"contas_que_reduziram")},MATCH(A{r},{Rg(CP,"periodo")},0))', '#,##0'); C(ws, r, 10, f'=COUNTIFS({TP_},"{n}",{TRd},"Sim")', '#,##0'); r += 1
note(ws, r + 1, 'Leitura: volume de tickets por conta, urgência, escalação e satisfação ficam parecidos entre os períodos. Em nov–dez/24 há um pouco mais de tickets urgentes (30% contra ~23%). As contas que reduziram Enterprise abrem tickets no mesmo ritmo ou abaixo das demais no próprio período. As reclamações não acompanham as reduções.', merge='J')
for col_, w in zip('ABCDEFGHIJ', [15, 12, 9, 12, 9, 9, 11, 11, 14, 12]): ws.column_dimensions[col_].width = w

# ---------- 6_Perfil_das_reducoes ----------
ws = w6; title(ws, 'Quem mais reduziu Enterprise: indústria, canal e país, por período', 'Reduções Enterprise a cada 100 assinaturas Enterprise ativas por mês, em cada categoria. "Diferente das demais?" compara a categoria com o resto do Enterprise no mesmo período (com menos de 10 reduções: "Poucos casos").', merge='N')
r = 4; destaques = []
for col, lab in [('industry', 'Indústria'), ('referral_source', 'Canal de aquisição'), ('country', 'País')]:
    ws.cell(r, 1, lab).font = Fn(bold=True, size=12); r += 1
    hdr = [lab]; fills = [HD]
    for n in PN: hdr += [f'{n}: reduções', f'{n}: a cada 100 por mês', f'{n}: diferente?']; fills += [HR, HR, HX]
    hdr += ['Todos os períodos: reduções', 'Todos: MRR perdido']; fills += [HR, HR]
    H(ws, r, hdr, fills, 58); r += 1; r0 = r
    for v in sorted(E[col].unique()):
        C(ws, r, 1, v, bold=True); j = 2
        for n in PN:
            mc = f'meses_ativos_{n[:1]}'; msk = E[col] == v
            k1 = int(((E.situacao == 'Redução') & (E.periodo_fim == n) & msk).sum()); e1 = float(E[msk][mc].sum()); k2 = int(((E.situacao == 'Redução') & (E.periodo_fim == n) & ~msk).sum()); e2 = float(E[~msk][mc].sum())
            cd = f'{PLc},"Enterprise",{Rg(BA, col)},$A{r}'
            C(ws, r, j, f'=COUNTIFS({cd},{SIc},"Redução",{PFc},"{n}")', '#,##0'); C(ws, r, j + 1, f'=IFERROR({L(j)}{r}/SUMIFS({Rg(BA, mc)},{cd})*100,"")', '0.00')
            cv = conf_taxa(k1, e1, k2, e2); C(ws, r, j + 2, cv)
            if cv == 'Sim': destaques.append(f'{lab} {v} em {n[3:]}: {k1/e1*100:.2f} contra {k2/e2*100:.2f} a cada 100 por mês')
            j += 3
        C(ws, r, j, f'=COUNTIFS({PLc},"Enterprise",{Rg(BA, col)},$A{r},{SIc},"Redução")', '#,##0'); C(ws, r, j + 1, f'=SUMIFS({Rg(BA,"mrr_reduzido")},{PLc},"Enterprise",{Rg(BA, col)},$A{r})', USD); r += 1
    C(ws, r, 1, 'Enterprise total', bold=True, fill=GRY); j = 2
    for n in PN:
        C(ws, r, j, f'=SUM({L(j)}{r0}:{L(j)}{r-1})', '#,##0', True, GRY); C(ws, r, j + 1, f'={L(j)}{r}/SUMIFS({Rg(BA, "meses_ativos_" + n[:1])},{PLc},"Enterprise")*100', '0.00', True, GRY); C(ws, r, j + 2, '', fill=GRY); j += 3
    C(ws, r, j, f'=SUM({L(j)}{r0}:{L(j)}{r-1})', '#,##0', True, GRY); C(ws, r, j + 1, f'=SUM({L(j+1)}{r0}:{L(j+1)}{r-1})', USD, True, GRY); r += 2
ws.conditional_formatting.add(f'A4:N{r}', CellIsRule(operator='equal', formula=['"Sim"'], fill=YEL))
note(ws, r, 'Leitura: em 2023 há só 4 reduções (poucos casos). Nos outros períodos, nenhuma indústria ou canal se destaca com segurança; a única célula "Sim" é França em nov–dez/24 (5 reduções), sinal fraco — entre tantas comparações, um "Sim" isolado pode ser acaso. A redução se espalha em proporção parecida ao tamanho de cada grupo. Em US$, quem mais pesa são os EUA (US$ 238 mil dos 458 mil), por terem mais assinaturas Enterprise.', merge='N', h=40)
ws.column_dimensions['A'].width = 16
for j in range(2, 15): ws.column_dimensions[L(j)].width = 10
ws.freeze_panes = 'B4'

# ---------- 7_Lista_Reducoes ----------
LR = E[E.situacao == 'Redução'].sort_values('end_date')
t30 = [int(((t.account_id == r_.account_id) & (t.submitted_at <= r_.end_date) & (t.submitted_at > r_.end_date - pd.Timedelta(days=30))).sum()) for r_ in LR.itertuples()]
LR = LR.assign(tickets_30d_antes=t30, dias_de_vida=(LR.end_date - LR.start_date).dt.days,
               features_mais_usadas=LR.subscription_id.map(lambda z: ', '.join(f[f.subscription_id == z].feature_name.value_counts().index[:3])),
               pct_registros_com_erro=LR.subscription_id.map(lambda z: round(float((f[f.subscription_id == z].error_count > 0).mean()), 3) if (f.subscription_id == z).any() else None))
cl = ['periodo_fim', 'subscription_id', 'account_id', 'industry', 'country', 'referral_source', 'cobranca', 'seats', 'mrr_amount', 'start_date', 'end_date', 'dias_de_vida', 'apos_reducao', 'outras_enterprise_ativas', 'outras_basic_pro_ativas', 'tickets_30d_antes', 'features_mais_usadas', 'pct_registros_com_erro']
nm = ['Período', 'Assinatura', 'Conta', 'Indústria', 'País', 'Canal', 'Cobrança', 'Seats', 'MRR (US$)', 'Início', 'Fim', 'Dias de vida', 'Depois da redução', 'Outras Enterprise ativas', 'Outras Basic/Pro ativas', 'Tickets nos 30 dias antes', 'Features mais usadas', '% registros com erro']
ws = w7; ws['A1'] = f'As {len(LR)} reduções Enterprise (jan/23–dez/24)'; ws['A1'].font = Fn(bold=True, size=15)
H(ws, 3, nm, [HD] * len(nm), 46)
for i, row in enumerate(LR[cl].itertuples(index=False), 4):
    for j, v in enumerate(row, 1):
        x = ws.cell(i, j, py(v)); x.font = Fn(size=9); x.border = BOX
        if cl[j - 1] in ('start_date', 'end_date'): x.number_format = D
        if cl[j - 1] == 'mrr_amount': x.number_format = USD
        if cl[j - 1] == 'pct_registros_com_erro': x.number_format = '0%'
ws.auto_filter.ref = f'A3:{L(len(cl))}{3+len(LR)}'; ws.freeze_panes = 'D4'
for j, w in enumerate([13, 11, 10, 13, 6, 9, 8, 6, 11, 10, 10, 7, 22, 9, 9, 9, 30, 9], 1): ws.column_dimensions[L(j)].width = w

# ---------- LEIA-ME ----------
red_m = {n: (int(((S.plan_tier == 'Enterprise') & (S.situacao == 'Redução') & (S.periodo_fim == n)).sum()), float(S[S.plan_tier == 'Enterprise'][f'meses_ativos_{n[:1]}'].sum()), int(S[(S.plan_tier == 'Enterprise') & (S.periodo_fim == n)].mrr_reduzido.sum()), mo) for n, _, _, mo in PER}
fmt = lambda v: f'US$ {v:,.0f}'.replace(',', '.')
seg = LR.apos_reducao.value_counts()
ws = leia; ws.column_dimensions['A'].width = 3; ws.column_dimensions['B'].width = 125
Lm = [('ENTERPRISE em 4 períodos: preço, seats, features, reclamações e quem reduziu', dict(bold=True, size=15)),
      ('Planilha apartada. Lê os CSVs originais sem alterá-los. Períodos: 2023 · jan–jun/24 · jul–out/24 · nov–dez/24. "Redução" = assinatura encerrada sem reposição em até 7 dias, com a conta seguindo cliente.', dict(italic=True, color=GRAY)),
      ('', {}), ('PERGUNTAS E RESPOSTAS', dict(bold=True, size=12)),
      ('1. Houve aumento de preço?  → aba 1', dict(bold=True)),
      ('   NÃO. O preço por seat é o mesmo em todas as assinaturas e períodos (Enterprise US$ 199; Pro 49; Basic 19), mensal ou anual (ARR ÷ 12 dá o mesmo). O valor médio das assinaturas varia só porque o número de seats varia.', {}),
      ('2. As reduções Enterprise aumentaram? Só no Enterprise?  → aba 2', dict(bold=True)),
      ('   Reduções a cada 100 assinaturas Enterprise por mês: ' + ' · '.join(f'{n[3:]}: {k/e*100:.2f}' for n, (k, e, v, mo) in red_m.items()) + '. MRR perdido por mês: ' + ' · '.join(f'{n[3:]}: {fmt(v/mo)}' for n, (k, e, v, mo) in red_m.items()) + '.', {}),
      ('   A taxa sobe também em Basic e Pro; o Enterprise não fica diferente dos outros planos em nenhum período. O que cresce muito no Enterprise é o VALOR perdido, porque há muito mais assinaturas Enterprise ativas e cada uma vale caro.', {}),
      ('3. Os clientes "regrediram" de plano?  → aba 3', dict(bold=True)),
      (f'   Pouco. Em {int(seg.get("Seguiu com outra Enterprise", 0))} das {len(LR)} reduções a conta seguiu com outra assinatura Enterprise; só {int(seg.get("Ficou só com Basic/Pro", 0))} ficaram apenas com Basic/Pro. É redução de contrato dentro do Enterprise, não troca de plano.', {}),
      ('4. Alguma feature surgiu num período e coincide com as reduções?  → aba 4', dict(bold=True)),
      ('   NÃO. As 40 features aparecem no Enterprise desde 2023 e a proporção de erro total é parecida em todos os períodos (≈30%). Não há "feature nova" identificável (a marca beta é aleatória). Ponto a checar: feature_10 e feature_24 passaram a dar mais erro depois de 2023 (sinal fraco).', {}),
      ('5. As reclamações mudaram?  → aba 5', dict(bold=True)),
      ('   NÃO de forma relevante: tickets por conta, escalação e satisfação ficam parecidos (urgentes sobem um pouco em nov–dez/24); quem reduz abre tickets no mesmo ritmo ou abaixo das demais contas.', {}),
      ('6. Quem mais reduziu (indústria, canal, país)?  → abas 6 e 7', dict(bold=True)),
      ('   Nenhuma indústria ou canal se destaca com segurança. ' + ('Único destaque, fraco: ' + '; '.join(destaques) + ' (poucos casos; pode ser acaso). ' if destaques else '') + 'Em quantidade e em US$, as reduções acompanham o tamanho de cada grupo: EUA 48 das 89 reduções; Cybersecurity, DevTools e FinTech lideram em quantidade; canais equilibrados. A aba 7 lista as 89 reduções, uma por linha.', {}),
      ('', {}), ('IMPLICAÇÃO', dict(bold=True, size=12)),
      ('Nesta base, a perda do Enterprise não vem de aumento de preço, de feature nova, de piora de erros nem de reclamações. Vem de contas Enterprise que encerram parte das suas assinaturas (menos seats/licenças) e continuam clientes. Como o Enterprise cresceu muito em 2024 e cada assinatura vale caro, a mesma taxa de redução vira uma perda em US$ muito maior. A causa de "por que reduzem" não está registrada nestas tabelas: é preciso ouvir essas contas (lista na aba 7).', {}),
      ('', {}), ('LIMITES', dict(bold=True, size=12)),
      ('• Base fictícia. Poucas reduções por período (4 a 44). Datas de uso e de tickets pouco confiáveis (uso ligado ao período de início da assinatura; tickets como tendência).', {})]
for i, (tx, st_) in enumerate(Lm, 1):
    x = ws.cell(i, 2, tx); x.font = Fn(**st_) if st_ else Fn(); x.alignment = Alignment(wrap_text=True, vertical='top')
wb.calculation.fullCalcOnLoad = True; wb.active = 1
OUT.parent.mkdir(parents=True, exist_ok=True); wb.save(OUT); print('ok', OUT)
print({n: (k, round(e), round(k / e * 100, 2), v, round(v / mo)) for n, (k, e, v, mo) in red_m.items()}); print(seg.to_dict()); print('destaques', destaques)
