# Nov/Dez 2024 · Quanto de MRR (US$) saiu de fato? Separado por troca/ajuste e redução (mesma regra da planilha 04).
# Gerado com Claude (IA). Lê os CSVs originais sem alterá-los; grava planilha apartada.
import sys
from pathlib import Path
import pandas as pd, numpy as np
RAIZ = Path(__file__).resolve().parents[3]
DADOS = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / 'dados'
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else RAIZ / 'analise' / 'DADOS_2024_NOV_DEZ' / '06_Valores_por_Tipo.xlsx'
INI, FIM = pd.Timestamp('2024-11-01'), pd.Timestamp('2024-12-31'); LIMITE = 30; JP = 7; RAJ_N, RAJ_D = 3, 7

s = pd.read_csv(DADOS/'ravenstack_subscriptions.csv', parse_dates=['start_date','end_date'])
a = pd.read_csv(DADOS/'ravenstack_accounts.csv')
s = s.sort_values(['account_id', 'start_date', 'subscription_id']).reset_index(drop=True)
def rajada(gr):
    d = gr.start_date.values; f = np.zeros(len(gr), bool)
    for i in range(len(gr)):
        w = (d >= d[i]) & (d <= d[i] + np.timedelta64(RAJ_D - 1, 'D'))
        if w.sum() >= RAJ_N: f |= w
    return pd.Series(f, index=gr.index)
s['em_rajada'] = np.where(s.groupby('account_id', group_keys=False).apply(rajada), 'Sim', 'Não')
E = s[s.end_date.between(INI, FIM)].merge(a[['account_id', 'industry', 'country']], on='account_id').copy()
E['dias_de_vida'] = (E.end_date - E.start_date).dt.days
E['velocidade'] = np.where(E.dias_de_vida < LIMITE, f'Rápida (< {LIMITE} dias)', f'Lenta ({LIMITE}+ dias)')
E['mes_fim'] = np.where(E.end_date.dt.month == 11, 'Nov/24', 'Dez/24')
E['fim_29_31_dez'] = np.where(E.end_date >= pd.Timestamp('2024-12-29'), 'Sim', 'Não')
E['trial'] = np.where(E.is_trial, 'Sim', 'Não')
def tipo(r):
    o = s[(s.account_id == r.account_id) & (s.subscription_id != r.subscription_id)]
    ativas = o[(o.start_date <= r.end_date) & (o.end_date.isna() | (o.end_date > r.end_date))]
    perto = o[(o.start_date - r.end_date).abs().dt.days <= JP]; depois = o[(o.start_date > r.end_date) & (o.start_date <= r.end_date + pd.Timedelta(days=JP))]
    if len(ativas) == 0 and len(depois) == 0: return pd.Series({'tipo': 'Saída do cliente', 'nova_mais_proxima': '', 'mrr_nova': 0})
    if len(perto):
        p = perto.iloc[(perto.start_date - r.end_date).abs().argsort()].iloc[0]
        return pd.Series({'tipo': 'Troca/ajuste', 'nova_mais_proxima': p.subscription_id, 'mrr_nova': int(p.mrr_amount)})
    return pd.Series({'tipo': 'Redução', 'nova_mais_proxima': '', 'mrr_nova': 0})
E = pd.concat([E.reset_index(drop=True), E.apply(tipo, axis=1).reset_index(drop=True)], axis=1).sort_values('end_date').reset_index(drop=True)
# cada assinatura nova só é contada uma vez (a mesma nova pode estar perto de 2 cancelamentos)
E['nova_ja_contada'] = np.where((E.nova_mais_proxima != '') & E.nova_mais_proxima.duplicated(), 'Sim', 'Não')
E['mrr_nova_contado'] = np.where(E.nova_ja_contada == 'Sim', 0, E.mrr_nova)
MRR_1NOV = int(s[(s.start_date < INI) & (s.end_date.isna() | (s.end_date >= INI))].mrr_amount.sum())
NOVO = s[s.start_date.between(INI, FIM)]; MRR_NOVO = int(NOVO.mrr_amount.sum())
MRR_3112 = int(s[s.end_date.isna()].mrr_amount.sum())

# ===================== planilha =====================
from openpyxl import Workbook
from openpyxl.utils import get_column_letter as L
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import CellIsRule
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.chart import BarChart, Reference
FONT = 'Arial'; GRAY = '52514E'; Fn = lambda **k: Font(name=FONT, **k)
HD = PatternFill('solid', fgColor='1F2937'); HT = PatternFill('solid', fgColor='0F766E'); HRd = PatternFill('solid', fgColor='B45309'); HX = PatternFill('solid', fgColor='374151'); HL = PatternFill('solid', fgColor='B91C1C'); HG = PatternFill('solid', fgColor='15803D')
GRY = PatternFill('solid', fgColor='EDEDED'); YEL = PatternFill('solid', fgColor='FFF3CD')
thin = Side(style='thin', color='D0D0D0'); BOX = Border(top=thin, bottom=thin, left=thin, right=thin)
USD = '"US$ "#,##0;-"US$ "#,##0;"-"'
wb = Workbook(); wb.remove(wb.active)
def S_(n): ws = wb.create_sheet(n); ws.sheet_view.showGridLines = False; return ws
leia = S_('LEIA-ME'); rs = S_('Resumo_US$'); rc = S_('Recortes_US$')
cols = ['subscription_id', 'account_id', 'industry', 'country', 'velocidade', 'mes_fim', 'fim_29_31_dez', 'em_rajada', 'trial', 'start_date', 'end_date', 'dias_de_vida', 'plan_tier', 'seats', 'mrr_amount',
        'tipo', 'nova_mais_proxima', 'mrr_nova', 'nova_ja_contada', 'mrr_nova_contado']
nomes = ['Assinatura', 'Conta', 'Indústria', 'País', 'Velocidade', 'Mês do fim', 'Fim 29–31/12?', 'Comprada em rajada?', 'Trial?', 'Início', 'Fim', 'Dias de vida', 'Plano', 'Seats', 'MRR cancelado (US$)',
         'Tipo (janela 7 dias)', 'Nova mais próxima', 'MRR da nova (US$)', 'Nova já contada em outra linha?', 'MRR da nova considerado (US$)']
ws = wb.create_sheet('Lista_266'); ws.append(nomes)
def py(v):
    if v is None or v is pd.NaT or (isinstance(v, float) and np.isnan(v)): return None
    if isinstance(v, pd.Timestamp): return v.to_pydatetime()
    return v.item() if hasattr(v, 'item') else v
for row in E[cols].itertuples(index=False): ws.append([py(v) for v in row])
n = len(E) + 1
for i, cn in enumerate(cols, 1):
    h = ws.cell(1, i); h.font = Fn(bold=True, color='FFFFFF', size=9); h.fill = HD; h.alignment = Alignment(wrap_text=True, vertical='center')
    ws.column_dimensions[L(i)].width = [11, 10, 12, 6, 13, 8, 8, 9, 6, 10, 10, 7, 10, 6, 12, 13, 11, 11, 10, 12][i - 1]
    for r in range(2, n + 1):
        x = ws.cell(r, i); x.font = Fn(size=9)
        if cn in ('start_date', 'end_date'): x.number_format = 'dd/mm/yyyy'
        if cn.startswith('mrr'): x.number_format = USD
ws.row_dimensions[1].height = 44
tb = Table(displayName='tLista266US', ref=f'A1:{L(len(cols))}{n}'); tb.tableStyleInfo = TableStyleInfo(name='TableStyleLight1', showRowStripes=True); ws.add_table(tb); ws.freeze_panes = 'C2'
def RL(col): i = cols.index(col) + 1; return f'Lista_266!${L(i)}$2:${L(i)}${n}'
MC, MN, TP = RL('mrr_amount'), RL('mrr_nova_contado'), RL('tipo')
def H(ws, row, labels, fills, h=44):
    for j, (x, fl) in enumerate(zip(labels, fills), 1):
        c_ = ws.cell(row, j, x); c_.font = Fn(bold=True, color='FFFFFF', size=9); c_.fill = fl; c_.alignment = Alignment(wrap_text=True, horizontal='center', vertical='center'); c_.border = BOX
    ws.row_dimensions[row].height = h
def C(ws, r, c_, v, fmt=None, bold=False, fill=None):
    x = ws.cell(r, c_, v); x.font = Fn(size=9, bold=bold); x.border = BOX; x.alignment = Alignment(wrap_text=True, vertical='center')
    if fmt: x.number_format = fmt
    if fill: x.fill = fill
    return x
def note(ws, r, tx, merge='G', color=GRAY, h=30):
    ws.cell(r, 1, tx).font = Fn(italic=True, size=9, color=color); ws.cell(r, 1).alignment = Alignment(wrap_text=True, vertical='top'); ws.merge_cells(f'A{r}:{merge}{r}'); ws.row_dimensions[r].height = h

# ---------- Resumo_US$ ----------
ws = rs
ws['A1'] = 'Nov/dez 2024: quanto de MRR saiu de fato?'; ws['A1'].font = Fn(bold=True, size=15)
ws['A2'] = f'MRR = receita mensal da assinatura. Tipos pela mesma regra da planilha 04 (janela de {JP} dias). Valores por fórmula sobre Lista_266.'; ws['A2'].font = Fn(italic=True, size=9, color=GRAY)
r = 4; ws.cell(r, 1, '1. Do número "oficial" ao número real').font = Fn(bold=True, size=12); r += 1
H(ws, r, ['Passo', 'MRR (US$)', 'Assinaturas', '% do cancelado bruto', 'Como ler'], [HD, HD, HD, HD, HD]); r += 1; p0 = r
C(ws, r, 1, 'A. MRR cancelado em nov/dez (como a empresa conta hoje)', bold=True); C(ws, r, 2, f'=SUM({MC})', USD, True); C(ws, r, 3, f'=COUNTA({RL("subscription_id")})', '#,##0'); C(ws, r, 4, f'=B{r}/B${p0}', '0%')
C(ws, r, 5, 'Soma do MRR de todas as assinaturas encerradas. É o "churn de receita" que aparece nos painéis originais.'); r += 1
C(ws, r, 1, '   … das quais em trocas/ajustes', bold=False); C(ws, r, 2, f'=SUMIFS({MC},{TP},"Troca/ajuste")', USD); C(ws, r, 3, f'=COUNTIFS({TP},"Troca/ajuste")', '#,##0'); C(ws, r, 4, f'=B{r}/B${p0}', '0%'); C(ws, r, 5, 'A conta abriu outra assinatura até 7 dias antes/depois.'); r += 1
C(ws, r, 1, '   … das quais em reduções', bold=False); C(ws, r, 2, f'=SUMIFS({MC},{TP},"Redução")', USD); C(ws, r, 3, f'=COUNTIFS({TP},"Redução")', '#,##0'); C(ws, r, 4, f'=B{r}/B${p0}', '0%'); C(ws, r, 5, 'A conta seguiu ativa, sem compra nova perto.'); r += 1
C(ws, r, 1, '   … das quais em saídas de cliente', bold=False); C(ws, r, 2, f'=SUMIFS({MC},{TP},"Saída do cliente")', USD); C(ws, r, 3, f'=COUNTIFS({TP},"Saída do cliente")', '#,##0'); C(ws, r, 4, f'=B{r}/B${p0}', '0%'); C(ws, r, 5, 'Nenhuma em nov/dez.'); r += 1
pB = r; C(ws, r, 1, 'B. MRR das assinaturas novas abertas no lugar (trocas)', bold=True); C(ws, r, 2, f'=SUMIFS({MN},{TP},"Troca/ajuste")', USD, True); C(ws, r, 3, f'=COUNTIFS({TP},"Troca/ajuste",{RL("nova_ja_contada")},"Não")', '#,##0'); C(ws, r, 4, f'=B{r}/B${p0}', '0%')
C(ws, r, 5, 'MRR das assinaturas novas mais próximas de cada troca (cada nova contada uma vez só). É o que voltou.'); r += 1
pC = r; C(ws, r, 1, 'C. Saldo das trocas (B − cancelado em trocas)', bold=True); C(ws, r, 2, f'=B{pB}-B{p0+1}', USD, True); C(ws, r, 3, ''); C(ws, r, 4, f'=-B{r}/B${p0}', '0%')
C(ws, r, 5, 'Negativo = nas trocas a conta passou a pagar menos do que pagava.'); r += 1
pD = r; C(ws, r, 1, 'D. PERDA REAL de MRR em nov/dez (reduções + saídas − saldo das trocas)', bold=True, fill=YEL); C(ws, r, 2, f'=B{p0+2}+B{p0+3}-B{pC}', USD, True, YEL); C(ws, r, 3, '', fill=YEL); C(ws, r, 4, f'=B{r}/B${p0}', '0%', True, YEL)
C(ws, r, 5, 'O que de fato deixou de entrar por mês, descontando o que foi reaberto em assinaturas novas.', fill=YEL); r += 1
C(ws, r, 1, 'E. MRR que só mudou de assinatura (A − D)', bold=True); C(ws, r, 2, f'=B{p0}-B{pD}', USD, True); C(ws, r, 3, ''); C(ws, r, 4, f'=B{r}/B${p0}', '0%'); C(ws, r, 5, 'Parte do número oficial que não é perda: foi reaberta em outra assinatura da mesma conta.'); r += 2
note(ws, r, f'Cuidado: essas contas abrem assinaturas com frequência; parte das assinaturas novas "perto" de um cancelamento pode ser compra independente. Por isso a perda real fica entre D (descontando todas as trocas) e A (sem descontar nada).', merge='E', color='B45309'); r += 2
ws.cell(r, 1, '2. Contexto: o tamanho da carteira').font = Fn(bold=True, size=12); r += 1
H(ws, r, ['Indicador', 'MRR (US$)', 'Assinaturas', '', 'Como ler'], [HD, HD, HD, HD, HD]); r += 1; q0 = r
C(ws, r, 1, 'MRR ativo em 01/11/2024', bold=True); C(ws, r, 2, MRR_1NOV, USD); C(ws, r, 3, ''); C(ws, r, 4, ''); C(ws, r, 5, 'Calculado no script a partir da tabela de assinaturas.'); r += 1
C(ws, r, 1, 'MRR de todas as assinaturas abertas em nov/dez', bold=True); C(ws, r, 2, MRR_NOVO, USD); C(ws, r, 3, len(NOVO), '#,##0'); C(ws, r, 4, ''); C(ws, r, 5, 'Inclui as que entraram no lugar das trocas.'); r += 1
C(ws, r, 1, 'MRR ativo em 31/12/2024', bold=True); C(ws, r, 2, MRR_3112, USD); C(ws, r, 3, ''); C(ws, r, 4, ''); C(ws, r, 5, ''); r += 1
C(ws, r, 1, 'Cancelado bruto (A) ÷ MRR de 01/11', bold=True); C(ws, r, 2, f'=B{p0}/B{q0}', '0.0%'); C(ws, r, 5, 'Como o churn de receita de nov+dez aparece hoje.'); r += 1
C(ws, r, 1, 'Perda real (D) ÷ MRR de 01/11', bold=True, fill=YEL); C(ws, r, 2, f'=B{pD}/B{q0}', '0.0%', True, YEL); C(ws, r, 5, 'O mesmo indicador, só com o que de fato saiu.', fill=YEL); r += 2
note(ws, r, 'Leitura: mesmo descontando as trocas, a perda de MRR de nov/dez é relevante e vem quase toda de REDUÇÕES (assinaturas encerradas sem reposição em contas que continuam clientes). Ao mesmo tempo, a carteira cresceu muito no período: o MRR ativo subiu de 01/11 para 31/12.', merge='E')
for col_, w in zip('ABCDE', [58, 16, 11, 12, 70]): ws.column_dimensions[col_].width = w
ch = BarChart(); ch.type = 'bar'; ch.title = 'Do cancelado bruto à perda real (US$)'; ch.height = 6.5; ch.width = 16; ch.legend = None
ch.add_data(Reference(ws, min_col=2, min_row=p0, max_row=pD + 1), titles_from_data=False); ch.set_categories(Reference(ws, min_col=1, min_row=p0, max_row=pD + 1)); ch.series[0].graphicalProperties.solidFill = '374151'
ch.x_axis.number_format = '#,##0'; ws.add_chart(ch, 'G4')

# ---------- Recortes_US$ ----------
ws = rc
ws['A1'] = 'Perda real de MRR por recorte'; ws['A1'].font = Fn(bold=True, size=15)
ws['A2'] = 'Mesma conta da aba Resumo, aplicada a cada recorte: perda real = reduções + saídas − saldo das trocas.'; ws['A2'].font = Fn(italic=True, size=9, color=GRAY)
def bloco(ws, r, titulo, col, valores):
    ws.cell(r, 1, titulo).font = Fn(bold=True, size=12); r += 1
    H(ws, r, ['Recorte', 'Encerradas', 'MRR cancelado (bruto)', 'Em trocas: cancelado', 'Em trocas: reaberto', 'Em reduções', 'PERDA REAL', 'Perda real ÷ bruto'], [HD, HD, HL, HT, HT, HRd, HX, HX]); r += 1; r0 = r
    for v in valores:
        cd = f',{RL(col)},"{v}"'
        C(ws, r, 1, v, bold=True); C(ws, r, 2, f'=COUNTIFS({RL(col)},"{v}")', '#,##0'); C(ws, r, 3, f'=SUMIFS({MC}{cd})', USD)
        C(ws, r, 4, f'=SUMIFS({MC},{TP},"Troca/ajuste"{cd})', USD); C(ws, r, 5, f'=SUMIFS({MN},{TP},"Troca/ajuste"{cd})', USD)
        C(ws, r, 6, f'=SUMIFS({MC},{TP},"Redução"{cd})+SUMIFS({MC},{TP},"Saída do cliente"{cd})', USD); C(ws, r, 7, f'=F{r}+D{r}-E{r}', USD, True); C(ws, r, 8, f'=IF(C{r}>0,G{r}/C{r},"")', '0%'); r += 1
    C(ws, r, 1, 'Total', bold=True, fill=GRY)
    for j in range(2, 8): C(ws, r, j, f'=SUM({L(j)}{r0}:{L(j)}{r-1})', USD if j > 2 else '#,##0', True, GRY)
    C(ws, r, 8, f'=G{r}/C{r}', '0%', True, GRY)
    return r + 2
r = 4
r = bloco(ws, r, '1. Por velocidade', 'velocidade', [f'Rápida (< {LIMITE} dias)', f'Lenta ({LIMITE}+ dias)'])
r = bloco(ws, r, '2. Por mês', 'mes_fim', ['Nov/24', 'Dez/24'])
r = bloco(ws, r, '3. Pico de 29 a 31/12', 'fim_29_31_dez', ['Sim', 'Não'])
r = bloco(ws, r, '4. Comprada em rajada?', 'em_rajada', ['Sim', 'Não'])
r = bloco(ws, r, '5. Plano da assinatura cancelada', 'plan_tier', ['Basic', 'Pro', 'Enterprise'])
r = bloco(ws, r, '6. Indústria', 'industry', sorted(E.industry.unique()))
r = bloco(ws, r, '7. País', 'country', sorted(E.country.unique()))
note(ws, r, 'Obs.: "Em trocas: reaberto" pode ser negativo no saldo de um recorte quando a nova assinatura vale mais que a cancelada (troca para cima). Trials têm MRR zero.', merge='H')
for col_, w in zip('ABCDEFGH', [22, 10, 15, 15, 15, 14, 15, 11]): ws.column_dimensions[col_].width = w

# ---------- LEIA-ME ----------
bruto = int(E.mrr_amount.sum()); tc = int(E[E.tipo == 'Troca/ajuste'].mrr_amount.sum()); tn = int(E[E.tipo == 'Troca/ajuste'].mrr_nova_contado.sum()); rd = int(E[E.tipo != 'Troca/ajuste'].mrr_amount.sum())
real = rd + (tc - tn)
rap = E[E.velocidade.str.startswith('Rápida')]; real_rap = int(rap[rap.tipo != 'Troca/ajuste'].mrr_amount.sum() + rap[rap.tipo == 'Troca/ajuste'].mrr_amount.sum() - rap[rap.tipo == 'Troca/ajuste'].mrr_nova_contado.sum())
fmt = lambda v: f'US$ {v:,.0f}'.replace(',', '.')
ws = leia; ws.column_dimensions['A'].width = 3; ws.column_dimensions['B'].width = 125
Lm = [('Nov/dez 2024 · Quanto de MRR saiu de fato?', dict(bold=True, size=15)),
      ('Planilha apartada. Lê os CSVs originais sem alterá-los. Mesma classificação da planilha 04 (troca/ajuste, redução, saída; janela de 7 dias).', dict(italic=True, color=GRAY)),
      ('', {}), ('O CÁLCULO, EM PALAVRAS', dict(bold=True, size=12)),
      ('1. Somamos o MRR de todas as assinaturas encerradas em nov/dez: é o número que a empresa usa hoje.', {}),
      ('2. Nas trocas, somamos o MRR da assinatura nova aberta no lugar (a mais próxima da data; cada nova contada uma vez só).', {}),
      ('3. Perda real = MRR das reduções + MRR das saídas + (MRR cancelado nas trocas − MRR reaberto nas trocas).', {}),
      ('', {}), ('RESULTADO', dict(bold=True, size=12)),
      (f'• MRR cancelado em nov/dez (número de hoje): {fmt(bruto)}.', {}),
      (f'• Em trocas: {fmt(tc)} cancelados, {fmt(tn)} reabertos em assinaturas novas (saldo de {fmt(tc - tn)} a menos).', {}),
      (f'• Em reduções: {fmt(rd)}. Saídas de cliente: nenhuma.', {}),
      (f'• PERDA REAL: {fmt(real)} ({real / bruto * 100:.0f}% do número de hoje). Os outros {fmt(bruto - real)} ({(bruto - real) / bruto * 100:.0f}%) só mudaram de assinatura dentro da mesma conta.', {}),
      (f'• Nos cancelamentos rápidos (< 30 dias), a perda real é {fmt(real_rap)}, de {fmt(int(rap.mrr_amount.sum()))} cancelados.', {}),
      (f'• Contexto: o MRR ativo foi de {fmt(MRR_1NOV)} (01/11) para {fmt(MRR_3112)} (31/12); entraram {fmt(MRR_NOVO)} em assinaturas novas no período.', {}),
      ('', {}), ('COMO LER', dict(bold=True, size=12)),
      ('• A perda real fica entre o valor descontado (perda real) e o valor bruto: parte das assinaturas "novas perto" pode ser compra independente, não reposição.', {}),
      ('• Abas: Resumo_US$ (do número de hoje ao número real, e o tamanho da carteira) · Recortes_US$ (velocidade, mês, pico de 29–31/12, rajada, plano, indústria, país) · Lista_266 (cada assinatura com o MRR cancelado e o MRR da nova).', {}),
      ('', {}), ('LIMITES', dict(bold=True, size=12)),
      ('• Base fictícia. Usa só a tabela de assinaturas (a confiável). MRR = valor mensal registrado na assinatura; trials valem zero.', {})]
for i, (tx, st) in enumerate(Lm, 1):
    x = ws.cell(i, 2, tx); x.font = Fn(**st) if st else Fn(); x.alignment = Alignment(wrap_text=True, vertical='top')
wb.calculation.fullCalcOnLoad = True; wb.active = 1
OUT.parent.mkdir(parents=True, exist_ok=True); wb.save(OUT); print('ok', OUT)
print('bruto', bruto, 'troca canc', tc, 'troca nova', tn, 'reducao', rd, 'real', real, round(real / bruto, 3), 'rap', int(rap.mrr_amount.sum()), real_rap, '| 1nov', MRR_1NOV, 'novo', MRR_NOVO, '3112', MRR_3112)
for col in ['velocidade', 'mes_fim', 'fim_29_31_dez', 'em_rajada', 'plan_tier']:
    g = E.groupby(col).apply(lambda x: pd.Series({'bruto': x.mrr_amount.sum(), 'real': x[x.tipo != 'Troca/ajuste'].mrr_amount.sum() + x[x.tipo == 'Troca/ajuste'].mrr_amount.sum() - x[x.tipo == 'Troca/ajuste'].mrr_nova_contado.sum()}))
    print(g.to_dict('index'))
