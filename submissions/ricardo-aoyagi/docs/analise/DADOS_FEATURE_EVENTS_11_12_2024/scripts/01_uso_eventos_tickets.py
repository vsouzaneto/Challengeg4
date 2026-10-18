# Uso de features → eventos de churn (nov/dez 2024) e tickets: churneados x não churneados.
# Parte das tabelas de USO e de EVENTOS. A tabela de assinaturas é usada só para saber a conta de cada assinatura
# (e, na aba 4, para mostrar que a data de uso não acompanha a vida da assinatura).
# Gerado com Claude (IA). Lê os CSVs originais sem alterá-los; grava planilha apartada.
import sys
from pathlib import Path
from math import lgamma, exp
import pandas as pd, numpy as np
RAIZ = Path(__file__).resolve().parents[3]
DADOS = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / 'dados'
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else RAIZ / 'analise' / 'DADOS_FEATURE_EVENTS_11_12_2024' / '01_Uso_Eventos_Tickets.xlsx'
I0, I1 = pd.Timestamp('2024-11-01'), pd.Timestamp('2024-12-31'); JAN = 30
a = pd.read_csv(DADOS/'ravenstack_accounts.csv'); s = pd.read_csv(DADOS/'ravenstack_subscriptions.csv', parse_dates=['start_date', 'end_date'])
f = pd.read_csv(DADOS/'ravenstack_feature_usage.csv', parse_dates=['usage_date']); c = pd.read_csv(DADOS/'ravenstack_churn_events.csv', parse_dates=['churn_date'])
t = pd.read_csv(DADOS/'ravenstack_support_tickets.csv', parse_dates=['submitted_at'])

# ---------- testes de "diferença confiável?" ----------
def fisher_p(a_, b_, c_, d_):
    n1, n2, m1 = a_ + b_, c_ + d_, a_ + c_; N = n1 + n2
    if N == 0 or n1 == 0 or n2 == 0 or m1 == 0 or m1 == N: return 1.0
    lc = lambda n, k: lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)
    pmf = lambda x: exp(lc(n1, x) + lc(n2, m1 - x) - lc(N, m1)); p0 = pmf(a_); lo, hi = max(0, m1 - n2), min(m1, n1)
    return min(1.0, sum(pmf(x) for x in range(lo, hi + 1) if pmf(x) <= p0 * (1 + 1e-7)))
def conf(k1, n1, k2, n2):
    if k1 + k2 < 10: return 'Poucos casos para concluir'
    return 'Sim' if fisher_p(int(k1), int(n1 - k1), int(k2), int(n2 - k2)) < 0.05 else 'Não (pode ser coincidência)'
RNG = np.random.default_rng(2024)
def conf_media(x, y, B=4000):
    """compara médias de dois grupos embaralhando os rótulos (sem fórmulas estatísticas)."""
    x, y = np.asarray(x, float), np.asarray(y, float); x, y = x[~np.isnan(x)], y[~np.isnan(y)]
    if len(x) < 10 or len(y) < 10: return 'Poucos casos para concluir'
    d0 = abs(x.mean() - y.mean()); z = np.concatenate([x, y]); n = len(x); k = 0
    for _ in range(B):
        RNG.shuffle(z); k += abs(z[:n].mean() - z[n:].mean()) >= d0 - 1e-12
    return 'Sim' if (k + 1) / (B + 1) < 0.05 else 'Não (pode ser coincidência)'

# ---------- grupos de contas ----------
CN = c[(c.churn_date >= I0) & (c.churn_date <= I1)].copy()
ev_nd = set(CN.account_id); ev_out = set(c.account_id) - ev_nd
G1, G2, G3 = '1. Evento em nov/dez', '2. Evento só em outro mês', '3. Nunca teve evento'
GR = [G1, G2, G3]
a['grupo'] = np.where(a.account_id.isin(ev_nd), G1, np.where(a.account_id.isin(ev_out), G2, G3))
f = f.merge(s[['subscription_id', 'account_id', 'start_date', 'end_date']], on='subscription_id'); f['com_erro'] = (f.error_count > 0).astype(int); f['beta'] = f.is_beta_feature.astype(int)
f = f.merge(a[['account_id', 'grupo']], on='account_id')
FN = f[(f.usage_date >= I0) & (f.usage_date <= I1)].copy()
FN['tem_evento_novdez'] = np.where(FN.account_id.isin(ev_nd), 'Sim', 'Não')
FN = FN.sort_values(['account_id', 'feature_name', 'usage_date']); FN['primeiro_da_conta_na_feature'] = np.where(FN.duplicated(['account_id', 'feature_name']), 0, 1)
FN['antes_do_inicio_da_assinatura'] = np.where(FN.usage_date < FN.start_date, 'Sim', 'Não'); FN['depois_do_fim_da_assinatura'] = np.where(FN.end_date.notna() & (FN.usage_date > FN.end_date), 'Sim', 'Não')

# ---------- base por conta ----------
def agg(df, suf):
    g = df.groupby('account_id').agg(**{f'registros{suf}': ('usage_id', 'size'), f'usos{suf}': ('usage_count', 'sum'), f'horas{suf}': ('usage_duration_secs', lambda x: x.sum() / 3600),
        f'registros_com_erro{suf}': ('com_erro', 'sum'), f'erros{suf}': ('error_count', 'sum'), f'registros_beta{suf}': ('beta', 'sum'), f'features_diferentes{suf}': ('feature_name', 'nunique')})
    return g
K = a.set_index('account_id')[['grupo', 'industry', 'country', 'referral_source']].join(agg(f, '')).join(agg(FN, '_novdez'))
K['assinaturas'] = s.groupby('account_id').size()
K['assinaturas_ativas_novdez'] = s[(s.start_date <= I1) & (s.end_date.isna() | (s.end_date >= I0))].groupby('account_id').size()
TK = t.groupby('account_id').agg(tickets=('ticket_id', 'size'))
K = K.join(TK).fillna(0).reset_index()
for col in [x for x in K.columns if x not in ('account_id', 'grupo', 'industry', 'country', 'referral_source', 'horas', 'horas_novdez')]: K[col] = K[col].astype(int)
K['tem_evento_novdez'] = np.where(K.grupo == G1, 'Sim', 'Não'); K['usou_em_novdez'] = np.where(K.registros_novdez > 0, 'Sim', 'Não')
K['pct_registros_com_erro'] = K.registros_com_erro / K.registros.replace(0, np.nan); K['minutos_por_uso'] = K.horas * 60 / K.usos.replace(0, np.nan)
K['pct_registros_com_erro_novdez'] = K.registros_com_erro_novdez / K.registros_novdez.replace(0, np.nan)

# ---------- antes / depois de cada evento de nov/dez ----------
rows = []; se = s[s.end_date.notna()]
for r in CN.sort_values('churn_date').itertuples():
    u = f[f.account_id == r.account_id]
    b = u[(u.usage_date < r.churn_date) & (u.usage_date >= r.churn_date - pd.Timedelta(days=JAN))]; d = u[(u.usage_date > r.churn_date) & (u.usage_date <= r.churn_date + pd.Timedelta(days=JAN))]
    tk = t[(t.account_id == r.account_id) & (t.submitted_at < r.churn_date) & (t.submitted_at >= r.churn_date - pd.Timedelta(days=JAN))]
    fim = ((se.account_id == r.account_id) & ((se.end_date - r.churn_date).abs().dt.days <= 7)).any()
    rows.append(dict(churn_event_id=r.churn_event_id, account_id=r.account_id, churn_date=r.churn_date, motivo=r.reason_code, comentario=r.feedback_text if isinstance(r.feedback_text, str) else '(vazio)',
        registros_30d_antes=len(b), registros_com_erro_30d_antes=int(b.com_erro.sum()), registros_30d_depois=len(d), dias_observaveis_depois=int(min(JAN, (I1 - r.churn_date).days)),
        usou_depois=('Sim' if len(d) else 'Não'), sem_uso_30d_antes=('Sim' if len(b) == 0 else 'Não'), tickets_30d_antes=len(tk), fim_de_assinatura_em_7_dias=('Sim' if fim else 'Não')))
EV = pd.DataFrame(rows)
# referência: contas SEM evento, em datas sorteadas de nov/dez, mesma pergunta "sem uso nos 30 dias antes?"
outras = sorted(set(f.account_id) - set(c.account_id)); dias = pd.date_range(I0, I1); ref = []
for _ in range(1000):
    acc = RNG.choice(outras); d0 = pd.Timestamp(RNG.choice(dias)); u = f[(f.account_id == acc) & (f.usage_date < d0) & (f.usage_date >= d0 - pd.Timedelta(days=JAN))]
    ref.append(len(u) == 0)
REF_SEM_USO = float(np.mean(ref))

# ---------- conta x feature (base inteira) ----------
KF = f.groupby(['account_id', 'grupo', 'feature_name']).agg(registros=('usage_id', 'size'), registros_com_erro=('com_erro', 'sum')).reset_index()
FEATS = sorted(f.feature_name.unique(), key=lambda z: int(z.split('_')[1]))
# ---------- uso por mês x assinaturas ativas; registros por assinatura ----------
meses = pd.period_range('2023-01', '2024-12', freq='M')
UM = pd.DataFrame(dict(mes=[m.strftime('%Y-%m') for m in meses], registros_de_uso=[int((f.usage_date.dt.to_period('M') == m).sum()) for m in meses],
                       assinaturas_ativas=[int(((s.start_date <= m.end_time) & (s.end_date.isna() | (s.end_date >= m.start_time))).sum()) for m in meses],
                       eventos_de_churn=[int((c.churn_date.dt.to_period('M') == m).sum()) for m in meses]))
def per(d): return '1. 2023' if d.year == 2023 else ('2. Jan–Jun/24' if d.month <= 6 else ('3. Jul–Out/24' if d.month <= 10 else '4. Nov–Dez/24'))
SA = s[['subscription_id', 'account_id', 'start_date', 'end_date']].copy(); SA['periodo_inicio'] = SA.start_date.apply(per); SA['dias_de_vida'] = ((SA.end_date.fillna(pd.Timestamp('2025-01-01')) - SA.start_date).dt.days)
SA['registros_de_uso'] = SA.subscription_id.map(f.groupby('subscription_id').size()).fillna(0).astype(int)
SA['faixa_vida'] = pd.cut(SA.dias_de_vida, [-1, 30, 90, 180, 365, 10**4], labels=['Até 30 dias', '31–90 dias', '91–180 dias', '181–365 dias', 'Mais de 365 dias']).astype(str)
TT = t.merge(a[['account_id', 'grupo']], on='account_id'); TT['escalado'] = np.where(TT.escalation_flag, 'Sim', 'Não'); TT['sem_nota'] = np.where(TT.satisfaction_score.isna(), 'Sim', 'Não')
TT['em_novdez'] = np.where((TT.submitted_at >= I0) & (TT.submitted_at <= I1), 'Sim', 'Não')

# ======================== planilha ========================
from openpyxl import Workbook
from openpyxl.utils import get_column_letter as L
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import CellIsRule
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.chart.series import SeriesLabel
from openpyxl.chart.axis import ChartLines
FONT = 'Arial'; GRAY = '52514E'; Fn = lambda **k: Font(name=FONT, **k)
HD = PatternFill('solid', fgColor='1F2937'); H1 = PatternFill('solid', fgColor='B45309'); H2 = PatternFill('solid', fgColor='7C3AED'); H3 = PatternFill('solid', fgColor='0F766E'); HX = PatternFill('solid', fgColor='374151')
YEL = PatternFill('solid', fgColor='FFF3CD'); GRY = PatternFill('solid', fgColor='EDEDED'); GF = {G1: H1, G2: H2, G3: H3}
thin = Side(style='thin', color='D0D0D0'); BOX = Border(top=thin, bottom=thin, left=thin, right=thin); D = 'dd/mm/yyyy'
wb = Workbook(); wb.remove(wb.active)
def S_(n): ws = wb.create_sheet(n); ws.sheet_view.showGridLines = False; return ws
leia = S_('LEIA-ME'); w1 = S_('1_Uso_NovDez'); w2 = S_('2_Antes_e_depois_do_evento'); w3 = S_('3_Motivo_x_Uso'); w4 = S_('4_Data_de_uso'); w5 = S_('5_Perfil_de_uso_base_inteira'); w6 = S_('6_Features_por_grupo'); w7 = S_('7_Tickets_por_grupo')
BS = {}
def py(v):
    if v is None or v is pd.NaT or (isinstance(v, float) and np.isnan(v)): return None
    if isinstance(v, pd.Timestamp): return v.to_pydatetime()
    return v.item() if hasattr(v, 'item') else v
def base(nome, df, cols, fmts={}):
    ws = wb.create_sheet(nome); ws.append(cols)
    for row in df[cols].itertuples(index=False): ws.append([py(v) for v in row])
    n = len(df) + 1; BS[nome] = (cols, n)
    for i, cn in enumerate(cols, 1):
        h = ws.cell(1, i); h.font = Fn(bold=True, color='FFFFFF', size=9); h.fill = HD; ws.column_dimensions[L(i)].width = max(11, min(24, len(cn) + 2))
        if cn in fmts:
            for r in range(2, n + 1): ws.cell(r, i).number_format = fmts[cn]
    tb = Table(displayName='t' + nome, ref=f'A1:{L(len(cols))}{n}'); tb.tableStyleInfo = TableStyleInfo(name='TableStyleLight1', showRowStripes=True); ws.add_table(tb); ws.freeze_panes = 'B2'
def Rg(b, col): cols, n = BS[b]; i = cols.index(col) + 1; return f"{b}!${L(i)}$2:${L(i)}${n}"
def H(ws, row, labels, fills, h=46):
    for j, (x, fl) in enumerate(zip(labels, fills), 1):
        if x is None: continue
        c_ = ws.cell(row, j, x); c_.font = Fn(bold=True, color='FFFFFF', size=9); c_.fill = fl; c_.alignment = Alignment(wrap_text=True, horizontal='center', vertical='center'); c_.border = BOX
    ws.row_dimensions[row].height = h
def C(ws, r, c_, v, fmt=None, bold=False, fill=None):
    x = ws.cell(r, c_, v); x.font = Fn(size=9, bold=bold); x.border = BOX; x.alignment = Alignment(vertical='center', wrap_text=True)
    if fmt: x.number_format = fmt
    if fill: x.fill = fill
    return x
def title(ws, t1, t2, merge='H'):
    ws['A1'] = t1; ws['A1'].font = Fn(bold=True, size=15); ws['A2'] = t2; ws['A2'].font = Fn(italic=True, size=9, color=GRAY); ws['A2'].alignment = Alignment(wrap_text=True, vertical='top'); ws.merge_cells(f'A2:{merge}2'); ws.row_dimensions[2].height = 40
def note(ws, r, tx, merge='H', h=40):
    ws.cell(r, 1, tx).font = Fn(italic=True, size=9, color=GRAY); ws.cell(r, 1).alignment = Alignment(wrap_text=True, vertical='top'); ws.merge_cells(f'A{r}:{merge}{r}'); ws.row_dimensions[r].height = h
def widths(ws, ws_):
    for j, w in enumerate(ws_, 1): ws.column_dimensions[L(j)].width = w
def yel(ws, rng): ws.conditional_formatting.add(rng, CellIsRule(operator='equal', formula=['"Sim"'], fill=YEL))

base('Base_Contas', K, ['account_id', 'grupo', 'tem_evento_novdez', 'industry', 'country', 'referral_source', 'assinaturas', 'assinaturas_ativas_novdez', 'registros', 'usos', 'horas', 'registros_com_erro', 'erros', 'registros_beta', 'features_diferentes',
    'pct_registros_com_erro', 'minutos_por_uso', 'registros_novdez', 'usos_novdez', 'horas_novdez', 'registros_com_erro_novdez', 'registros_beta_novdez', 'features_diferentes_novdez', 'pct_registros_com_erro_novdez', 'usou_em_novdez', 'tickets'],
    {'horas': '0.0', 'horas_novdez': '0.0', 'pct_registros_com_erro': '0%', 'pct_registros_com_erro_novdez': '0%', 'minutos_por_uso': '0.00'})
base('Base_Uso_NovDez', FN, ['usage_id', 'subscription_id', 'account_id', 'usage_date', 'feature_name', 'usage_count', 'error_count', 'com_erro', 'beta', 'tem_evento_novdez', 'primeiro_da_conta_na_feature', 'start_date', 'end_date', 'antes_do_inicio_da_assinatura', 'depois_do_fim_da_assinatura'], {'usage_date': D, 'start_date': D, 'end_date': D})
base('Base_Eventos_NovDez', EV, list(EV.columns), {'churn_date': D})
base('Base_Conta_Feature', KF, ['account_id', 'grupo', 'feature_name', 'registros', 'registros_com_erro'])
base('Base_Uso_Mes', UM, list(UM.columns))
base('Base_Assinaturas', SA, ['subscription_id', 'account_id', 'start_date', 'end_date', 'periodo_inicio', 'dias_de_vida', 'faixa_vida', 'registros_de_uso'], {'start_date': D, 'end_date': D})
base('Base_Tickets', TT, ['ticket_id', 'account_id', 'grupo', 'submitted_at', 'em_novdez', 'priority', 'escalado', 'resolution_time_hours', 'first_response_time_minutes', 'satisfaction_score', 'sem_nota'], {'submitted_at': D})
BK, BU, BE, BF, BT = 'Base_Contas', 'Base_Uso_NovDez', 'Base_Eventos_NovDez', 'Base_Conta_Feature', 'Base_Tickets'

# ---------- 1_Uso_NovDez ----------
ws = w1; title(ws, 'Uso de features em nov/dez de 2024: contas com evento de churn x sem evento', 'Uso filtrado pela DATA DE USO (nov/dez). Evento = registro na tabela de eventos de churn com data em nov/dez. Médias por conta que teve algum uso em nov/dez.', 'F')
H(ws, 4, ['Por conta (média)', 'Com evento em nov/dez', 'Sem evento em nov/dez', 'Diferença confiável?'], [HD, H1, H3, HX]); r = 5
KU = K[K.usou_em_novdez == 'Sim']; kx, ky = KU[KU.tem_evento_novdez == 'Sim'], KU[KU.tem_evento_novdez == 'Não']
C(ws, r, 1, 'Contas com uso em nov/dez', bold=True)
for j, v in ((2, 'Sim'), (3, 'Não')): C(ws, r, j, f'=COUNTIFS({Rg(BK,"tem_evento_novdez")},"{v}",{Rg(BK,"usou_em_novdez")},"Sim")', '#,##0')
C(ws, r, 4, '—'); r += 1
for lab, col, fm in [('Registros de uso', 'registros_novdez', '0.00'), ('Quantidade de usos', 'usos_novdez', '0.0'), ('Horas de uso', 'horas_novdez', '0.0'), ('Features diferentes usadas', 'features_diferentes_novdez', '0.00'),
                     ('Assinaturas ativas em nov/dez', 'assinaturas_ativas_novdez', '0.00')]:
    C(ws, r, 1, lab, bold=True)
    for j, v in ((2, 'Sim'), (3, 'Não')): C(ws, r, j, f'=AVERAGEIFS({Rg(BK,col)},{Rg(BK,"tem_evento_novdez")},"{v}",{Rg(BK,"usou_em_novdez")},"Sim")', fm)
    C(ws, r, 4, conf_media(kx[col], ky[col])); r += 1
for lab, num in [('% dos registros com erro', 'com_erro'), ('% dos registros em feature beta', 'beta')]:
    C(ws, r, 1, lab, bold=True)
    for j, v in ((2, 'Sim'), (3, 'Não')): C(ws, r, j, f'=SUMIFS({Rg(BU,num)},{Rg(BU,"tem_evento_novdez")},"{v}")/COUNTIFS({Rg(BU,"tem_evento_novdez")},"{v}")', '0.0%')
    x1, x2 = FN[FN.tem_evento_novdez == 'Sim'][num], FN[FN.tem_evento_novdez == 'Não'][num]; C(ws, r, 4, conf(x1.sum(), len(x1), x2.sum(), len(x2))); r += 1
yel(ws, f'D5:D{r}')
r += 1; H(ws, r, ['Feature (nov/dez)', '% das contas com evento que usaram', '% das contas sem evento que usaram', 'Diferença confiável?', '% registros com erro: com evento', '% registros com erro: sem evento', 'Erro: diferença confiável?'], [HD, H1, H3, HX, H1, H3, HX]); r += 1; r0 = r
nE, nN = len(kx), len(ky); FE = FN.tem_evento_novdez
for fe in FEATS:
    x = FN[FN.feature_name == fe]; k1 = x[x.tem_evento_novdez == 'Sim'].account_id.nunique(); k2 = x[x.tem_evento_novdez == 'Não'].account_id.nunique()
    C(ws, r, 1, fe, bold=True)
    for j, v, ref in ((2, 'Sim', '$B$5'), (3, 'Não', '$C$5')): C(ws, r, j, f'=SUMIFS({Rg(BU,"primeiro_da_conta_na_feature")},{Rg(BU,"feature_name")},$A{r},{Rg(BU,"tem_evento_novdez")},"{v}")/{ref}', '0%')
    C(ws, r, 4, conf(k1, nE, k2, nN))
    for j, v in ((5, 'Sim'), (6, 'Não')): C(ws, r, j, f'=IFERROR(SUMIFS({Rg(BU,"com_erro")},{Rg(BU,"feature_name")},$A{r},{Rg(BU,"tem_evento_novdez")},"{v}")/COUNTIFS({Rg(BU,"feature_name")},$A{r},{Rg(BU,"tem_evento_novdez")},"{v}"),"")', '0%')
    e1, e2 = x[x.tem_evento_novdez == 'Sim'].com_erro, x[x.tem_evento_novdez == 'Não'].com_erro; C(ws, r, 7, conf(e1.sum(), len(e1), e2.sum(), len(e2))); r += 1
yel(ws, f'D{r0}:G{r}')
note(ws, r + 1, 'Leitura: contas com e sem evento de churn em nov/dez usam o produto na mesma quantidade, nas mesmas features e com a mesma proporção de erros. As poucas células "Sim" (se houver) são o esperado por acaso em 40 comparações.', 'G')
widths(ws, [30, 14, 14, 24, 14, 14, 24]); ws.freeze_panes = 'B5'

# ---------- 2_Antes_e_depois_do_evento ----------
ws = w2; title(ws, 'O uso muda em volta do evento de churn?', f'Para cada um dos {len(EV)} eventos de nov/dez: uso da conta nos {JAN} dias antes e depois da data do evento (todas as assinaturas da conta). Depois do evento, a observação é cortada em 31/12/2024.', 'F')
H(ws, 4, ['Medida', 'Valor', 'Comentário'], [HD, H1, HX]); r = 5
E_ = lambda col: Rg(BE, col)
items = [('Eventos de churn em nov/dez', f'=COUNTA({E_("churn_event_id")})', '#,##0', ''),
         ('Contas com evento', f'=SUMPRODUCT(1/COUNTIF({E_("account_id")},{E_("account_id")}))', '#,##0', 'Algumas contas têm 2 a 4 eventos no período.'),
         (f'Registros de uso nos {JAN} dias antes, por evento', f'=AVERAGE({E_("registros_30d_antes")})', '0.00', ''),
         (f'Registros de uso depois, por evento, a cada {JAN} dias observáveis', f'=SUM({E_("registros_30d_depois")})/SUM({E_("dias_observaveis_depois")})*{JAN}', '0.00', 'Mesmo ritmo de antes: o uso não cai depois do "churn".'),
         ('Eventos em que a conta usou o produto DEPOIS do evento', f'=COUNTIF({E_("usou_depois")},"Sim")/COUNTA({E_("churn_event_id")})', '0%', 'Quem "saiu" continua usando.'),
         (f'% com erro nos registros dos {JAN} dias antes', f'=SUM({E_("registros_com_erro_30d_antes")})/SUM({E_("registros_30d_antes")})', '0.0%', 'Igual à média geral da base (≈31%).'),
         ('% de registros com erro na base inteira', f'=SUM({Rg(BK,"registros_com_erro")})/SUM({Rg(BK,"registros")})', '0.0%', ''),
         (f'Eventos sem nenhum uso nos {JAN} dias antes', f'=COUNTIF({E_("sem_uso_30d_antes")},"Sim")/COUNTA({E_("churn_event_id")})', '0%', ''),
         (f'Referência: contas sem evento, em datas sorteadas de nov/dez, sem uso nos {JAN} dias antes', REF_SEM_USO, '0%', 'Calculado pelo programa (1.000 sorteios). Silêncio antes do evento é tão comum quanto em qualquer conta.'),
         (f'Eventos com ticket nos {JAN} dias antes', f'=COUNTIF({E_("tickets_30d_antes")},">0")/COUNTA({E_("churn_event_id")})', '0%', 'Datas de ticket pouco confiáveis: use como tendência.'),
         ('Eventos que coincidem (±7 dias) com o fim de alguma assinatura da conta', f'=COUNTIF({E_("fim_de_assinatura_em_7_dias")},"Sim")/COUNTA({E_("churn_event_id")})', '0%', 'A maioria dos "churns" registrados não tem nenhuma assinatura terminando perto.')]
for lab, fx, fm, cm in items:
    C(ws, r, 1, lab, bold=True); C(ws, r, 2, fx, fm); C(ws, r, 3, cm); r += 1
note(ws, r + 1, 'Leitura: nada muda em volta do evento. O uso antes e depois é o mesmo, o erro é o da média e o "silêncio" antes do evento é tão comum quanto em contas sem evento. O evento de churn não marca uma saída real do cliente.', 'F')
widths(ws, [52, 12, 70])

# ---------- 3_Motivo_x_Uso ----------
ws = w3; title(ws, 'O motivo registrado no evento combina com o uso e com o comentário do cliente?', f'Motivo (reason_code) x uso da conta nos {JAN} dias antes do evento. Embaixo: motivo x comentário escrito (feedback_text).', 'H')
H(ws, 4, ['Motivo registrado', 'Eventos', f'Registros de uso nos {JAN} dias antes (média)', '% registros com erro', f'Com ticket nos {JAN} dias antes', 'Erro diferente dos outros motivos?'], [HD, H1, H1, H1, H1, HX]); r = 5; r0 = r
MOT = EV.motivo.value_counts().index.tolist()
for m in MOT:
    C(ws, r, 1, m, bold=True); C(ws, r, 2, f'=COUNTIF({E_("motivo")},$A{r})', '#,##0'); C(ws, r, 3, f'=AVERAGEIFS({E_("registros_30d_antes")},{E_("motivo")},$A{r})', '0.00')
    C(ws, r, 4, f'=IFERROR(SUMIFS({E_("registros_com_erro_30d_antes")},{E_("motivo")},$A{r})/SUMIFS({E_("registros_30d_antes")},{E_("motivo")},$A{r}),"")', '0%')
    C(ws, r, 5, f'=COUNTIFS({E_("motivo")},$A{r},{E_("tickets_30d_antes")},">0")/B{r}', '0%')
    x, y = EV[EV.motivo == m], EV[EV.motivo != m]; C(ws, r, 6, conf(x.registros_com_erro_30d_antes.sum(), x.registros_30d_antes.sum(), y.registros_com_erro_30d_antes.sum(), y.registros_30d_antes.sum())); r += 1
yel(ws, f'F{r0}:F{r}')
r += 1; COM = ['too expensive', 'missing features', 'switched to competitor', '(vazio)']
H(ws, r, ['Motivo \\ Comentário'] + COM + ['Total'], [HD] + [HX] * 4 + [HD], 34); r += 1; rc = r
for m in MOT:
    C(ws, r, 1, m, bold=True)
    for j, cm in enumerate(COM, 2): C(ws, r, j, f'=COUNTIFS({E_("motivo")},$A{r},{E_("comentario")},"{cm}")', '#,##0')
    C(ws, r, 6, f'=SUM(B{r}:E{r})', '#,##0', True); r += 1
note(ws, r + 1, 'Leitura: o motivo registrado não muda o uso nem o erro antes do evento (quem marcou "features" usa e erra igual a quem marcou "budget"). E o comentário do cliente não acompanha o motivo: "too expensive" aparece com qualquer motivo. Motivo e comentário parecem preenchidos de forma independente.', 'H')
widths(ws, [20, 12, 16, 14, 14, 24, 10, 10])

# ---------- 4_Data_de_uso ----------
ws = w4; title(ws, 'Por que filtrar o uso por data não funciona: a data de uso não acompanha as assinaturas', 'Três provas: (A) o uso total por mês fica parado enquanto as assinaturas ativas multiplicam; (B) toda assinatura tem ~5 registros, não importa quando começou nem quanto durou; (C) registros de nov/dez caem fora da vida da própria assinatura.', 'I')
H(ws, 4, ['(A) Mês', 'Registros de uso', 'Assinaturas ativas', 'Registros por assinatura ativa', 'Eventos de churn'], [HD, H3, HX, H3, H1]); r = 5; ra = r
for m in UM.mes:
    C(ws, r, 1, m, bold=True); C(ws, r, 2, f'=INDEX({Rg("Base_Uso_Mes","registros_de_uso")},MATCH(A{r},{Rg("Base_Uso_Mes","mes")},0))', '#,##0')
    C(ws, r, 3, f'=INDEX({Rg("Base_Uso_Mes","assinaturas_ativas")},MATCH(A{r},{Rg("Base_Uso_Mes","mes")},0))', '#,##0'); C(ws, r, 4, f'=B{r}/C{r}', '0.00')
    C(ws, r, 5, f'=INDEX({Rg("Base_Uso_Mes","eventos_de_churn")},MATCH(A{r},{Rg("Base_Uso_Mes","mes")},0))', '#,##0'); r += 1
rb_ = r - 1
ch = LineChart(); ch.title = 'Registros de uso x assinaturas ativas, por mês'; ch.height = 7.5; ch.width = 17
for col_, nm, cor in ((2, 'Registros de uso', '0F766E'), (3, 'Assinaturas ativas', '374151')):
    ch.add_data(Reference(ws, min_col=col_, min_row=ra, max_row=rb_), titles_from_data=False); ch.series[-1].tx = SeriesLabel(v=nm); ch.series[-1].graphicalProperties.line.solidFill = cor; ch.series[-1].graphicalProperties.line.width = 22000
ch.set_categories(Reference(ws, min_col=1, min_row=ra, max_row=rb_)); ch.legend.position = 'b'; ws.add_chart(ch, 'K4')
r += 1; PI = ['1. 2023', '2. Jan–Jun/24', '3. Jul–Out/24', '4. Nov–Dez/24']; FV = ['Até 30 dias', '31–90 dias', '91–180 dias', '181–365 dias', 'Mais de 365 dias']
BA = 'Base_Assinaturas'
H(ws, r, ['(B) Registros de uso por assinatura'] + PI + ['Todas'], [HD] + [H3] * 5, 34); r += 1
for fv in FV + ['Todas']:
    C(ws, r, 1, f'Vida: {fv}' if fv != 'Todas' else 'Todas as durações', bold=True, fill=GRY if fv == 'Todas' else None)
    for j, p in enumerate(PI + ['Todas'], 2):
        cd = (f',{Rg(BA,"periodo_inicio")},"{p}"' if p != 'Todas' else '') + (f',{Rg(BA,"faixa_vida")},"{fv}"' if fv != 'Todas' else '')
        C(ws, r, j, f'=IFERROR(AVERAGEIFS({Rg(BA,"registros_de_uso")}{cd}),"")' if cd else f'=AVERAGE({Rg(BA,"registros_de_uso")})', '0.0', fill=GRY if fv == 'Todas' else None)
    r += 1
r += 1; H(ws, r, ['(C) Registros de uso com data em nov/dez', 'Quantidade', '%'], [HD, H3, H3], 30); r += 1; rt = r
C(ws, r, 1, 'Total', bold=True); C(ws, r, 2, f'=COUNTA({Rg(BU,"usage_id")})', '#,##0'); C(ws, r, 3, 1, '0%'); r += 1
for lab, col in (('Data ANTES do início da própria assinatura', 'antes_do_inicio_da_assinatura'), ('Data DEPOIS do fim da própria assinatura', 'depois_do_fim_da_assinatura')):
    C(ws, r, 1, lab, bold=True); C(ws, r, 2, f'=COUNTIF({Rg(BU,col)},"Sim")', '#,##0'); C(ws, r, 3, f'=B{r}/B{rt}', '0%'); r += 1
note(ws, r + 1, 'Leitura: cerca de 1.000 registros de uso por mês, do primeiro ao último mês, enquanto as assinaturas ativas multiplicam muitas vezes. Cada assinatura tem ~5 registros, seja de 2023 ou de dez/24, dure 10 dias ou 2 anos. Ou seja, as datas de uso parecem distribuídas ao acaso: filtrar "uso de nov/dez" pega uma amostra aleatória, não o que os clientes fizeram nesses meses. Também por isso a afirmação "o uso cresceu" não se sustenta nesta tabela.', 'I', 56)
widths(ws, [36, 13, 13, 13, 13, 11, 10, 10, 10])

# ---------- 5_Perfil_de_uso_base_inteira ----------
ws = w5; title(ws, 'Perfil de uso de cada conta na base inteira (sem olhar a data de uso)', 'Todos os registros de uso de cada conta, em qualquer data. Grupo 1 = evento de churn em nov/dez/24; 2 = evento só em outros meses; 3 = nunca teve evento ("não churneado"). "Diferença confiável?" compara o grupo 1 com o grupo 3.', 'F')
H(ws, 4, ['Por conta (média)'] + GR + ['Grupo 1 x Grupo 3: diferença confiável?'], [HD, H1, H2, H3, HX]); r = 5
C(ws, r, 1, 'Contas', bold=True)
for j, g in enumerate(GR, 2): C(ws, r, j, f'=COUNTIF({Rg(BK,"grupo")},"{g}")', '#,##0')
C(ws, r, 5, '—'); r += 1
k1, k3 = K[K.grupo == G1], K[K.grupo == G3]
for lab, col, fm in [('Assinaturas', 'assinaturas', '0.0'), ('Registros de uso', 'registros', '0.0'), ('Quantidade de usos', 'usos', '0.0'), ('Horas de uso', 'horas', '0.0'), ('Minutos por uso', 'minutos_por_uso', '0.00'),
                     ('Features diferentes usadas (de 40)', 'features_diferentes', '0.0'), ('Erros por conta', 'erros', '0.0'), ('% dos registros com erro (média das contas)', 'pct_registros_com_erro', '0.0%')]:
    C(ws, r, 1, lab, bold=True)
    for j, g in enumerate(GR, 2): C(ws, r, j, f'=AVERAGEIFS({Rg(BK,col)},{Rg(BK,"grupo")},"{g}")', fm)
    C(ws, r, 5, conf_media(k1[col], k3[col])); r += 1
for lab, num in (('% de todos os registros com erro', 'registros_com_erro'), ('% de todos os registros em feature beta', 'registros_beta')):
    C(ws, r, 1, lab, bold=True)
    for j, g in enumerate(GR, 2): C(ws, r, j, f'=SUMIFS({Rg(BK,num)},{Rg(BK,"grupo")},"{g}")/SUMIFS({Rg(BK,"registros")},{Rg(BK,"grupo")},"{g}")', '0.0%')
    C(ws, r, 5, conf(k1[num].sum(), k1.registros.sum(), k3[num].sum(), k3.registros.sum())); r += 1
yel(ws, f'E5:E{r}')
ch = BarChart(); ch.type = 'col'; ch.title = '% dos registros com erro, por grupo'; ch.height = 6.5; ch.width = 12; ch.legend = None
ch.add_data(Reference(ws, min_col=2, max_col=4, min_row=r - 2), from_rows=True, titles_from_data=False); ch.set_categories(Reference(ws, min_col=2, max_col=4, min_row=4)); ch.y_axis.scaling.min = 0; ch.y_axis.number_format = '0%'
ch.series[0].graphicalProperties.solidFill = '0F766E'; ws.add_chart(ch, 'G4')
note(ws, r + 1, 'Leitura: os três grupos são praticamente idênticos em quantidade de uso, tempo de uso, variedade de features e erros. Quem teve evento de churn usa o produto exatamente como quem nunca teve.', 'F')
widths(ws, [40, 15, 15, 15, 26, 4])

# ---------- 6_Features_por_grupo ----------
ws = w6; title(ws, 'Cada feature: quem usa e quanto erra, por grupo (base inteira)', '% das contas do grupo que usaram a feature ao menos uma vez e % dos registros da feature com erro. "Confiável?" compara grupo 1 (evento nov/dez) com grupo 3 (nunca teve evento).', 'J')
H(ws, 4, ['Feature', f'% contas que usam: {G1}', f'% contas que usam: {G2}', f'% contas que usam: {G3}', 'Uso 1 x 3: confiável?', f'% erro: {G1}', f'% erro: {G2}', f'% erro: {G3}', 'Erro 1 x 3: confiável?'],
  [HD, H1, H2, H3, HX, H1, H2, H3, HX], 70); r = 5; r0 = r
nG = {g: int((a.grupo == g).sum()) for g in GR}
for fe in FEATS:
    x = KF[KF.feature_name == fe]; C(ws, r, 1, fe, bold=True)
    for j, g in enumerate(GR, 2): C(ws, r, j, f'=COUNTIFS({Rg(BF,"feature_name")},$A{r},{Rg(BF,"grupo")},"{g}")/COUNTIF({Rg(BK,"grupo")},"{g}")', '0%')
    C(ws, r, 5, conf(int((x.grupo == G1).sum()), nG[G1], int((x.grupo == G3).sum()), nG[G3]))
    for j, g in enumerate(GR, 6): C(ws, r, j, f'=SUMIFS({Rg(BF,"registros_com_erro")},{Rg(BF,"feature_name")},$A{r},{Rg(BF,"grupo")},"{g}")/SUMIFS({Rg(BF,"registros")},{Rg(BF,"feature_name")},$A{r},{Rg(BF,"grupo")},"{g}")', '0%')
    e1, e3 = x[x.grupo == G1], x[x.grupo == G3]; C(ws, r, 9, conf(e1.registros_com_erro.sum(), e1.registros.sum(), e3.registros_com_erro.sum(), e3.registros.sum())); r += 1
yel(ws, f'E{r0}:I{r}')
note(ws, r + 1, 'Leitura: em 40 features, só 1 ou 2 "Sim" — o esperado por acaso. A feature_10 é a que aparece mais usada (e com um pouco mais de erro) entre quem teve churn; ela também apareceu na análise Enterprise com mais erro depois de 2023. Sinal fraco, para perguntar ao time de produto, não causa comprovada.', 'I', 44)
widths(ws, [12, 13, 13, 13, 22, 11, 11, 11, 22]); ws.freeze_panes = 'B5'

# ---------- 7_Tickets_por_grupo ----------
ws = w7; title(ws, 'Tickets: contas com churn x contas sem churn', 'Base inteira de tickets (a data do ticket é pouco confiável). ATENÇÃO: a tabela de tickets NÃO tem assunto, categoria nem texto da reclamação — só prioridade, tempos, escalação e nota. Dá para comparar COMO foram os tickets, não O QUE foi reclamado.', 'F')
H(ws, 4, ['Medida'] + GR + ['Grupo 1 x Grupo 3: diferença confiável?'], [HD, H1, H2, H3, HX]); r = 5
GT = lambda g: f'{Rg(BT,"grupo")},"{g}"'
t1, t3 = TT[TT.grupo == G1], TT[TT.grupo == G3]
C(ws, r, 1, 'Tickets', bold=True)
for j, g in enumerate(GR, 2): C(ws, r, j, f'=COUNTIFS({GT(g)})', '#,##0')
C(ws, r, 5, '—'); r += 1
C(ws, r, 1, 'Tickets por conta', bold=True)
for j, g in enumerate(GR, 2): C(ws, r, j, f'=AVERAGEIFS({Rg(BK,"tickets")},{Rg(BK,"grupo")},"{g}")', '0.00')
C(ws, r, 5, conf_media(k1.tickets, k3.tickets)); r += 1
C(ws, r, 1, 'Contas com ao menos 1 ticket', bold=True)
for j, g in enumerate(GR, 2): C(ws, r, j, f'=COUNTIFS({Rg(BK,"grupo")},"{g}",{Rg(BK,"tickets")},">0")/COUNTIF({Rg(BK,"grupo")},"{g}")', '0%')
C(ws, r, 5, conf(int((k1.tickets > 0).sum()), len(k1), int((k3.tickets > 0).sum()), len(k3))); r += 1
for lab, col, val, fn in [('% urgentes', 'priority', 'urgent', lambda x: x.priority == 'urgent'), ('% prioridade alta', 'priority', 'high', lambda x: x.priority == 'high'),
                          ('% prioridade média', 'priority', 'medium', lambda x: x.priority == 'medium'), ('% prioridade baixa', 'priority', 'low', lambda x: x.priority == 'low'),
                          ('% escalados', 'escalado', 'Sim', lambda x: x.escalation_flag), ('% sem nota de satisfação', 'sem_nota', 'Sim', lambda x: x.satisfaction_score.isna())]:
    C(ws, r, 1, lab, bold=True)
    for j, g in enumerate(GR, 2): C(ws, r, j, f'=COUNTIFS({GT(g)},{Rg(BT,col)},"{val}")/COUNTIFS({GT(g)})', '0.0%')
    C(ws, r, 5, conf(int(fn(t1).sum()), len(t1), int(fn(t3).sum()), len(t3))); r += 1
for lab, col, fm in [('Tempo de resolução (horas, média)', 'resolution_time_hours', '0.0'), ('1ª resposta (minutos, média)', 'first_response_time_minutes', '0.0'), ('Satisfação média (só existem notas 3, 4 e 5)', 'satisfaction_score', '0.00')]:
    C(ws, r, 1, lab, bold=True)
    for j, g in enumerate(GR, 2): C(ws, r, j, f'=AVERAGEIFS({Rg(BT,col)},{GT(g)})', fm)
    C(ws, r, 5, conf_media(t1[col], t3[col])); r += 1
for nota in (3, 4, 5):
    C(ws, r, 1, f'% dos tickets com nota {nota}', bold=True)
    for j, g in enumerate(GR, 2): C(ws, r, j, f'=COUNTIFS({GT(g)},{Rg(BT,"satisfaction_score")},{nota})/COUNTIFS({GT(g)})', '0.0%')
    C(ws, r, 5, conf(int((t1.satisfaction_score == nota).sum()), len(t1), int((t3.satisfaction_score == nota).sum()), len(t3))); r += 1
yel(ws, f'E5:E{r}')
r += 1; H(ws, r, ['Só tickets abertos em nov/dez'] + GR + [None], [HD, H1, H2, H3, HX], 30); r += 1
for lab, fx, fm in [('Tickets em nov/dez', lambda g: f'=COUNTIFS({GT(g)},{Rg(BT,"em_novdez")},"Sim")', '#,##0'),
                    ('Tickets em nov/dez por conta', lambda g: f'=COUNTIFS({GT(g)},{Rg(BT,"em_novdez")},"Sim")/COUNTIF({Rg(BK,"grupo")},"{g}")', '0.00'),
                    ('% urgentes', lambda g: f'=COUNTIFS({GT(g)},{Rg(BT,"em_novdez")},"Sim",{Rg(BT,"priority")},"urgent")/COUNTIFS({GT(g)},{Rg(BT,"em_novdez")},"Sim")', '0%'),
                    ('% escalados', lambda g: f'=COUNTIFS({GT(g)},{Rg(BT,"em_novdez")},"Sim",{Rg(BT,"escalado")},"Sim")/COUNTIFS({GT(g)},{Rg(BT,"em_novdez")},"Sim")', '0%')]:
    C(ws, r, 1, lab, bold=True)
    for j, g in enumerate(GR, 2): C(ws, r, j, fx(g), fm)
    r += 1
note(ws, r + 1, 'Leitura: quem teve churn não abre mais tickets, não tem tickets mais graves, não é atendido mais devagar e não está menos satisfeito do que quem nunca teve churn. Única diferença confiável: o grupo 1 tem mais tickets de prioridade ALTA (28% x 23%) — mas tem menos URGENTES (23% x 28%), e a soma das duas é a mesma (~51%): muda o rótulo, não a gravidade. E a pergunta "quais reclamações" não tem resposta nesta base: o conteúdo do ticket não foi registrado.', 'F', 52)
widths(ws, [40, 15, 15, 15, 26])

# ---------- LEIA-ME ----------
ws = leia; ws.column_dimensions['A'].width = 3; ws.column_dimensions['B'].width = 125
Lm = [('USO DE FEATURES → EVENTOS DE CHURN (nov/dez 2024) e TICKETS: churneados x não churneados', dict(bold=True, size=15)),
      ('Planilha apartada. Lê os CSVs originais sem alterá-los. Parte das tabelas de uso e de eventos de churn; a tabela de assinaturas entra só para saber a conta de cada assinatura (e como prova na aba 4).', dict(italic=True, color=GRAY)),
      ('', {}), ('GRUPOS DE CONTAS', dict(bold=True, size=12)),
      (f'1. Evento em nov/dez: {nG[G1]} contas com evento de churn datado em nov/dez de 2024 ({len(EV)} eventos).', {}),
      (f'2. Evento só em outro mês: {nG[G2]} contas com evento de churn, mas nenhum em nov/dez.', {}),
      (f'3. Nunca teve evento ("não churneado"): {nG[G3]} contas.', {}),
      ('', {}), ('PERGUNTAS E RESPOSTAS', dict(bold=True, size=12)),
      ('1. Em nov/dez, quem teve evento de churn usou o produto de outro jeito?  → aba 1', dict(bold=True)),
      ('   Não. Mesma quantidade de uso, mesmas features, mesma proporção de erro.', {}),
      ('2. O uso muda em volta do evento?  → aba 2', dict(bold=True)),
      ('   Não. O ritmo de uso depois do "churn" é o mesmo de antes, a maioria das contas segue usando, e o silêncio antes do evento é tão comum quanto em contas sem evento. A maioria dos eventos não coincide com o fim de nenhuma assinatura.', {}),
      ('3. O motivo registrado combina com o uso ou com o comentário?  → aba 3', dict(bold=True)),
      ('   Não. Quem marcou "features" usa e erra igual a quem marcou "budget"; o comentário do cliente aparece misturado com qualquer motivo.', {}),
      ('4. Por que o recorte por data de uso não mostra nada?  → aba 4', dict(bold=True)),
      ('   Porque a data de uso não acompanha as assinaturas: ~1.000 registros por mês o tempo todo, ~5 registros por assinatura independentemente de quando começou e de quanto durou, e registros de nov/dez fora da vida da própria assinatura. Na prática, as datas parecem sorteadas.', {}),
      ('5. Olhando a base inteira (sem data), o perfil de uso de quem teve churn é diferente?  → abas 5 e 6', dict(bold=True)),
      ('   Não. Os três grupos são praticamente idênticos. Feature a feature, só 1 ou 2 diferenças em 40, o esperado por acaso. Sinal fraco que se repete: feature_10 (mais usada e com um pouco mais de erro entre quem teve churn; também apareceu na análise Enterprise).', {}),
      ('6. Clientes com churn reclamam mais ou diferente nos tickets?  → aba 7', dict(bold=True)),
      ('   Não. Mesma quantidade de tickets, mesmos tempos de atendimento, mesma satisfação. Quem teve churn tem mais tickets "alta" e menos "urgente", mas a soma das duas prioridades é igual (~51%). E a tabela de tickets não registra o assunto da reclamação: não dá para saber O QUE foi reclamado.', {}),
      ('', {}), ('IMPLICAÇÃO', dict(bold=True, size=12)),
      ('Uso de features, tickets e eventos de churn não conversam entre si nesta base: parecem preenchidos de forma independente. A explicação do churn não está em uso nem em suporte; ela aparece no padrão de contratação e cancelamento de assinaturas (ver DADOS_2024_NOV_DEZ e DADOS_ENTERPRISE). Para a empresa: registrar o assunto dos tickets e amarrar o evento de churn ao cancelamento real da assinatura.', {}),
      ('', {}), ('LIMITES', dict(bold=True, size=12)),
      ('• Base fictícia. "Diferença confiável?" = teste de Fisher para proporções e embaralhamento de rótulos para médias, com corte de 5%; menos de 10 casos = "Poucos casos para concluir".', {}),
      ('• A referência de "sem uso nos 30 dias antes" (aba 2) é calculada pelo programa com sorteio fixo, por isso aparece como valor e não como fórmula.', {})]
for i, (tx, st_) in enumerate(Lm, 1):
    x = ws.cell(i, 2, tx); x.font = Fn(**st_) if st_ else Fn(); x.alignment = Alignment(wrap_text=True, vertical='top')
wb.calculation.fullCalcOnLoad = True; wb.active = 1
OUT.parent.mkdir(parents=True, exist_ok=True); wb.save(OUT); print('ok', OUT)
print('grupos', nG, 'eventos', len(EV), 'ref sem uso', round(REF_SEM_USO, 3))
