# Nov/Dez 2024 · Cada assinatura encerrada é: troca/ajuste, redução ou saída do cliente?
# Gerado com Claude (IA). Lê os CSVs originais sem alterá-los; grava planilha apartada. Só quantidades.
import sys
from pathlib import Path
import pandas as pd, numpy as np
RAIZ = Path(__file__).resolve().parents[3]
DADOS = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / 'dados'
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else RAIZ / 'analise' / 'DADOS_2024_NOV_DEZ' / '04_Tipos_de_Cancelamento.xlsx'
INI, FIM = pd.Timestamp('2024-11-01'), pd.Timestamp('2024-12-31'); LIMITE = 30; JANELAS = [3, 7, 14]; JP = 7
NIVEL = {'Basic': 1, 'Pro': 2, 'Enterprise': 3}
FAIXAS = [0, 5, 10, 20, 40, 80, 10**4]; LF = ['01–05', '06–10', '11–20', '21–40', '41–80', '81 ou mais']

a = pd.read_csv(DADOS/'ravenstack_accounts.csv', parse_dates=['signup_date'])
s = pd.read_csv(DADOS/'ravenstack_subscriptions.csv', parse_dates=['start_date','end_date'])
c = pd.read_csv(DADOS/'ravenstack_churn_events.csv', parse_dates=['churn_date'])
s['dias_de_vida'] = (s.end_date - s.start_date).dt.days
E = s[s.end_date.between(INI, FIM)].merge(a[['account_id', 'country']], on='account_id').copy()
E['velocidade'] = np.where(E.dias_de_vida < LIMITE, f'Rápida (< {LIMITE} dias)', f'Lenta ({LIMITE}+ dias)')
E['mes_fim'] = np.where(E.end_date.dt.month == 11, 'Nov/24', 'Dez/24')
E['cobranca'] = E.billing_frequency.map({'annual': 'Anual', 'monthly': 'Mensal'})
E['faixa_seats'] = pd.cut(E.seats, FAIXAS, labels=LF).astype(str)
E['dias_29_31_dez'] = np.where((E.end_date >= pd.Timestamp('2024-12-29')), 'Sim', 'Não')

def classificar(r, w):
    o = s[(s.account_id == r.account_id) & (s.subscription_id != r.subscription_id)]
    ativas = o[(o.start_date <= r.end_date) & (o.end_date.isna() | (o.end_date > r.end_date))]
    perto = o[(o.start_date - r.end_date).abs().dt.days <= w]
    depois = o[(o.start_date > r.end_date) & (o.start_date <= r.end_date + pd.Timedelta(days=w))]
    if len(ativas) == 0 and len(depois) == 0: return 'Saída do cliente', ativas, perto
    if len(perto) > 0: return 'Troca/ajuste', ativas, perto
    return 'Redução', ativas, perto
rows = []
for r in E.itertuples():
    out = {}
    for w in JANELAS:
        tp, ativas, perto = classificar(r, w); out[f'tipo_{w}d'] = tp
        if w == JP:
            out['outras_ativas_no_dia'] = len(ativas)
            out['assinaturas_novas_perto'] = ', '.join(perto.subscription_id) if len(perto) else ''
            if len(perto):
                p = perto.iloc[(perto.start_date - r.end_date).abs().argsort()].iloc[0]   # a nova mais próxima da data
                d = NIVEL[p.plan_tier] - NIVEL[r.plan_tier]
                out['nova_mais_proxima'] = p.subscription_id
                out['plano_da_nova'] = 'Mesmo plano' if d == 0 else ('Plano acima' if d > 0 else 'Plano abaixo')
                out['cobranca_da_nova'] = 'Mesma cobrança' if p.billing_frequency == r.billing_frequency else ('Mudou para anual' if p.billing_frequency == 'annual' else 'Mudou para mensal')
                out['seats_da_nova'] = 'Mesmos seats' if p.seats == r.seats else ('Mais seats' if p.seats > r.seats else 'Menos seats')
            else:
                out.update(nova_mais_proxima='', plano_da_nova='', cobranca_da_nova='', seats_da_nova='')
    rows.append(out)
E = pd.concat([E.reset_index(drop=True), pd.DataFrame(rows)], axis=1)
E['conta_tem_evento_novdez'] = np.where(E.account_id.isin(c[c.churn_date.between(INI, FIM)].account_id), 'Sim', 'Não')
TIPOS = ['Troca/ajuste', 'Redução', 'Saída do cliente']
# referência: chance de existir assinatura nova em ±7 dias de uma data qualquer de nov/dez (conta qualquer)
rng = np.random.default_rng(1); acc = s.account_id.unique(); hits = []
for _ in range(3000):
    ac = rng.choice(acc); d = INI + pd.Timedelta(days=int(rng.integers(0, 61)))
    hits.append(((s.account_id == ac) & ((s.start_date - d).abs().dt.days <= JP)).any())
REF = float(np.mean(hits))
# saídas reais de conta em todo o período (conta sem nenhuma assinatura ativa em algum momento após ter tido)
contas_sem_ativa_31_12 = int((~a.account_id.isin(s[s.end_date.isna()].account_id)).sum())

# ===================== planilha =====================
from openpyxl import Workbook
from openpyxl.utils import get_column_letter as L
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import CellIsRule
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.chart import BarChart, Reference
FONT = 'Arial'; GRAY = '52514E'; Fn = lambda **k: Font(name=FONT, **k)
HD = PatternFill('solid', fgColor='1F2937'); HT = PatternFill('solid', fgColor='0F766E'); HRd = PatternFill('solid', fgColor='B45309'); HS = PatternFill('solid', fgColor='B91C1C'); HX = PatternFill('solid', fgColor='374151')
GRY = PatternFill('solid', fgColor='EDEDED'); FT = PatternFill('solid', fgColor='CCFBF1'); FR = PatternFill('solid', fgColor='FEF3C7'); FS = PatternFill('solid', fgColor='FEE2E2')
thin = Side(style='thin', color='D0D0D0'); BOX = Border(top=thin, bottom=thin, left=thin, right=thin)
wb = Workbook(); wb.remove(wb.active)
def S_(n): ws = wb.create_sheet(n); ws.sheet_view.showGridLines = False; return ws
leia = S_('LEIA-ME'); rs = S_('Resumo'); tr = S_('Trocas'); pp = S_('Por_perfil')
def py(v):
    if v is None or v is pd.NaT or (isinstance(v, float) and np.isnan(v)): return None
    if isinstance(v, pd.Timestamp): return v.to_pydatetime()
    return v.item() if hasattr(v, 'item') else v
cols = ['subscription_id', 'account_id', 'velocidade', 'mes_fim', 'dias_29_31_dez', 'start_date', 'end_date', 'dias_de_vida', 'plan_tier', 'cobranca', 'seats', 'faixa_seats', 'country',
        'tipo_7d', 'tipo_3d', 'tipo_14d', 'outras_ativas_no_dia', 'assinaturas_novas_perto', 'nova_mais_proxima', 'plano_da_nova', 'cobranca_da_nova', 'seats_da_nova', 'conta_tem_evento_novdez']
nomes = ['Assinatura', 'Conta', 'Velocidade', 'Mês do fim', 'Fim entre 29 e 31/12?', 'Início', 'Fim', 'Dias de vida', 'Plano', 'Cobrança', 'Seats', 'Faixa de seats', 'País',
         'TIPO (janela 7 dias)', 'Tipo (janela 3 dias)', 'Tipo (janela 14 dias)', 'Outras assinaturas ativas no dia do fim', 'Assinaturas novas até 7 dias antes/depois', 'Nova mais próxima', 'Plano da nova vs cancelada',
         'Cobrança da nova vs cancelada', 'Seats da nova vs cancelada', 'Conta tem evento de churn em nov/dez?']
ws = wb.create_sheet('Lista_266'); ws.append(nomes)
for row in E[cols].sort_values('end_date').itertuples(index=False): ws.append([py(v) for v in row])
n = len(E) + 1
for i in range(1, len(cols) + 1):
    h = ws.cell(1, i); h.font = Fn(bold=True, color='FFFFFF', size=9); h.fill = HT if cols[i - 1].startswith('tipo_7') else HD; h.alignment = Alignment(wrap_text=True, vertical='center')
    ws.column_dimensions[L(i)].width = [11, 10, 13, 8, 9, 10, 10, 7, 10, 8, 6, 9, 6, 14, 12, 12, 10, 26, 10, 12, 13, 12, 11][i - 1]
    for r in range(2, n + 1):
        x = ws.cell(r, i); x.font = Fn(size=9)
        if cols[i - 1] in ('start_date', 'end_date'): x.number_format = 'dd/mm/yyyy'
ws.row_dimensions[1].height = 48
tb = Table(displayName='tLista266', ref=f'A1:{L(len(cols))}{n}'); tb.tableStyleInfo = TableStyleInfo(name='TableStyleLight1', showRowStripes=True); ws.add_table(tb); ws.freeze_panes = 'C2'
for tp, fl in zip(TIPOS, [FT, FR, FS]): ws.conditional_formatting.add(f'N2:P{n}', CellIsRule(operator='equal', formula=[f'"{tp}"'], fill=fl))
def RL(col): i = cols.index(col) + 1; return f'Lista_266!${L(i)}$2:${L(i)}${n}'
def H(ws, row, labels, fills, h=40):
    for j, (x, fl) in enumerate(zip(labels, fills), 1):
        c_ = ws.cell(row, j, x); c_.font = Fn(bold=True, color='FFFFFF', size=9); c_.fill = fl; c_.alignment = Alignment(wrap_text=True, horizontal='center', vertical='center'); c_.border = BOX
    ws.row_dimensions[row].height = h
def C(ws, r, c_, v, fmt=None, bold=False, fill=None):
    x = ws.cell(r, c_, v); x.font = Fn(size=9, bold=bold); x.border = BOX; x.alignment = Alignment(wrap_text=True, vertical='center')
    if fmt: x.number_format = fmt
    if fill: x.fill = fill
    return x
def title(ws, t1, t2):
    ws['A1'] = t1; ws['A1'].font = Fn(bold=True, size=15); ws['A2'] = t2; ws['A2'].font = Fn(italic=True, size=9, color=GRAY)
T7 = RL('tipo_7d')
def bloco_tipos(ws, r, titulo, col, valores, rotulo):
    ws.cell(r, 1, titulo).font = Fn(bold=True, size=12); r += 1
    H(ws, r, [rotulo, 'Encerradas', 'Troca/ajuste', '%', 'Redução', '%', 'Saída do cliente', '%'], [HD, HD, HT, HT, HRd, HRd, HS, HS]); r += 1; r0 = r
    for v in valores:
        cond = f'{RL(col)},"{v}"' if col else None
        C(ws, r, 1, v if col else 'Todas', bold=True); C(ws, r, 2, f'=COUNTIFS({cond})' if col else f'=COUNTA({RL("subscription_id")})', '#,##0')
        for j, tp in zip((3, 5, 7), TIPOS):
            C(ws, r, j, f'=COUNTIFS({T7},"{tp}"' + (f',{cond})' if col else ')'), '#,##0'); C(ws, r, j + 1, f'=IF($B{r}>0,{L(j)}{r}/$B{r},"")', '0%')
        r += 1
    return r + 1, r0

# ---------- Resumo ----------
ws = rs; title(ws, 'As 266 assinaturas encerradas em nov/dez: quantas foram perda de cliente?', f'Regra (janela de {JP} dias): SAÍDA = a conta ficou sem nenhuma assinatura ativa e não comprou outra em até {JP} dias · TROCA/AJUSTE = a conta abriu outra assinatura até {JP} dias antes ou depois · REDUÇÃO = a conta seguiu ativa, sem compra nova perto.')
ws['A2'].alignment = Alignment(wrap_text=True); ws.merge_cells('A2:H2'); ws.row_dimensions[2].height = 40
r, r_all = bloco_tipos(ws, 4, '1. Todas as encerradas', None, [None], '')
r, r_vel = bloco_tipos(ws, r, '2. Por velocidade', 'velocidade', [f'Rápida (< {LIMITE} dias)', f'Lenta ({LIMITE}+ dias)'], 'Velocidade')
r, r_mes = bloco_tipos(ws, r, '3. Por mês', 'mes_fim', ['Nov/24', 'Dez/24'], 'Mês do fim')
r, r_dz = bloco_tipos(ws, r, '4. O pico de 29 a 31/12', 'dias_29_31_dez', ['Sim', 'Não'], 'Fim entre 29 e 31/12?')
r, r_ev = bloco_tipos(ws, r, '5. A conta registrou evento de churn em nov/dez?', 'conta_tem_evento_novdez', ['Sim', 'Não'], 'Evento de churn?')
ws.cell(r, 1, '6. E se a janela fosse outra? (sensibilidade da regra)').font = Fn(bold=True, size=12); r += 1
H(ws, r, ['Janela', 'Encerradas', 'Troca/ajuste', '%', 'Redução', '%', 'Saída do cliente', '%'], [HD, HD, HT, HT, HRd, HRd, HS, HS]); r += 1
for w in JANELAS:
    tw = RL(f'tipo_{w}d'); C(ws, r, 1, f'{w} dias', bold=True); C(ws, r, 2, f'=COUNTA({RL("subscription_id")})', '#,##0')
    for j, tp in zip((3, 5, 7), TIPOS): C(ws, r, j, f'=COUNTIF({tw},"{tp}")', '#,##0'); C(ws, r, j + 1, f'={L(j)}{r}/$B{r}', '0%')
    r += 1
r += 1
C(ws, r, 1, f'Referência: chance de uma conta qualquer abrir assinatura em ±{JP} dias de uma data qualquer de nov/dez', bold=True); ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=3); C(ws, r, 4, round(REF, 3), '0%')
r += 1; C(ws, r, 1, 'Contas sem nenhuma assinatura ativa em 31/12/2024 (base inteira, 500 contas)', bold=True); ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=3); C(ws, r, 4, contas_sem_ativa_31_12, '#,##0')
r += 2
for tx in ['Leitura: nenhuma das 266 assinaturas encerradas em nov/dez levou a conta a ficar sem assinatura. Não houve saída de cliente no período. O que houve foi troca/ajuste (a conta abriu outra assinatura perto da data) e redução (a conta seguiu com as demais assinaturas).',
           f'Cuidado com a "troca": essas contas abrem assinaturas com frequência. Numa data qualquer, já existe {REF*100:.0f}% de chance de haver assinatura nova em ±{JP} dias. Por isso parte das "trocas" pode ser coincidência; o excesso acima dessa referência é o que indica troca de fato.',
           'A regra é simples e explicável de propósito. A aba Lista_266 mostra, para cada assinatura, quantas outras estavam ativas no dia e quais assinaturas novas apareceram perto.']:
    ws.cell(r, 1, tx).font = Fn(italic=True, size=9, color=GRAY); ws.cell(r, 1).alignment = Alignment(wrap_text=True); ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8); ws.row_dimensions[r].height = 30; r += 1
for col_, w in zip('ABCDEFGH', [26, 11, 11, 8, 11, 8, 11, 8]): ws.column_dimensions[col_].width = w
ch = BarChart(); ch.type = 'bar'; ch.grouping = 'percentStacked'; ch.overlap = 100; ch.title = 'Tipo de cancelamento (janela 7 dias)'; ch.height = 7; ch.width = 16
for j, cor in zip((3, 5, 7), ['0F766E', 'B45309', 'B91C1C']):
    ch.add_data(Reference(ws, min_col=j, min_row=r_vel - 1, max_row=r_vel + 1), titles_from_data=True); ch.series[-1].graphicalProperties.solidFill = cor
ch.set_categories(Reference(ws, min_col=1, min_row=r_vel, max_row=r_vel + 1)); ch.legend.position = 'b'; ws.add_chart(ch, 'J4')

# ---------- Trocas ----------
ws = tr; title(ws, 'Trocas/ajustes: o que a conta abriu no lugar?', f'Compara a assinatura cancelada com a assinatura nova mais próxima (até {JP} dias antes ou depois). Contagens por fórmula sobre Lista_266.')
r = 4
for titulo, col, vals in [('Plano', 'plano_da_nova', ['Mesmo plano', 'Plano acima', 'Plano abaixo']), ('Cobrança', 'cobranca_da_nova', ['Mesma cobrança', 'Mudou para anual', 'Mudou para mensal']),
                          ('Seats', 'seats_da_nova', ['Mesmos seats', 'Mais seats', 'Menos seats'])]:
    ws.cell(r, 1, f'{titulo} da nova vs a cancelada').font = Fn(bold=True, size=12); r += 1
    H(ws, r, ['', 'Rápidas', '%', 'Lentas', '%', 'Todas', '%'], [HD, HT, HT, HT, HT, HD, HD]); r += 1; r0 = r
    for v in vals:
        C(ws, r, 1, v, bold=True)
        for j, vel in ((2, f'Rápida (< {LIMITE} dias)'), (4, f'Lenta ({LIMITE}+ dias)')):
            C(ws, r, j, f'=COUNTIFS({T7},"Troca/ajuste",{RL(col)},A{r},{RL("velocidade")},"{vel}")', '#,##0'); C(ws, r, j + 1, f'={L(j)}{r}/SUM({L(j)}${r0}:{L(j)}${r0+2})', '0%')
        C(ws, r, 6, f'=B{r}+D{r}', '#,##0'); C(ws, r, 7, f'=F{r}/SUM(F${r0}:F${r0+2})', '0%'); r += 1
    r += 1
ws.cell(r, 1, 'Leitura: a troca não tem uma direção só. Há trocas para plano acima, abaixo e igual, e mudanças de cobrança e de seats para os dois lados: parece reconfiguração do contrato logo após a compra, não um movimento único (ex.: "todo mundo descendo de plano").').font = Fn(italic=True, size=9, color=GRAY)
ws.column_dimensions['A'].width = 22
for c_ in 'BCDEFG': ws.column_dimensions[c_].width = 11

# ---------- Por_perfil ----------
ws = pp; title(ws, 'Tipo de cancelamento por plano, cobrança, seats e país', f'Janela de {JP} dias. Contagens por fórmula sobre Lista_266.')
r = 4
r, _ = bloco_tipos(ws, r, 'Plano da assinatura cancelada', 'plan_tier', ['Basic', 'Pro', 'Enterprise'], 'Plano')
r, _ = bloco_tipos(ws, r, 'Cobrança', 'cobranca', ['Anual', 'Mensal'], 'Cobrança')
r, _ = bloco_tipos(ws, r, 'Faixa de seats', 'faixa_seats', LF, 'Seats')
r, _ = bloco_tipos(ws, r, 'País', 'country', sorted(E.country.unique()), 'País')
for col_, w in zip('ABCDEFGH', [16, 11, 11, 8, 11, 8, 11, 8]): ws.column_dimensions[col_].width = w

# ---------- LEIA-ME ----------
cnt = E.tipo_7d.value_counts(); rap = E[E.velocidade.str.startswith('Rápida')].tipo_7d.value_counts()
ws = leia; ws.column_dimensions['A'].width = 3; ws.column_dimensions['B'].width = 125
Lm = [('Nov/dez 2024 · As assinaturas encerradas foram troca, redução ou saída do cliente?', dict(bold=True, size=15)),
      ('Planilha apartada. Lê os CSVs originais sem alterá-los. Só quantidades.', dict(italic=True, color=GRAY)),
      ('', {}), ('A REGRA (simples e explicável)', dict(bold=True, size=12)),
      (f'Para cada uma das {len(E)} assinaturas encerradas em nov/dez, olhamos a conta no dia do encerramento:', {}),
      (f'• SAÍDA DO CLIENTE: a conta ficou sem nenhuma assinatura ativa e não abriu outra em até {JP} dias.', {}),
      (f'• TROCA/AJUSTE: a conta abriu outra assinatura até {JP} dias antes ou depois do encerramento.', {}),
      ('• REDUÇÃO: a conta continuou com outras assinaturas ativas, sem compra nova perto da data.', {}),
      ('A janela de 7 dias é uma escolha; a aba Resumo mostra o resultado também com 3 e 14 dias.', dict(italic=True, color=GRAY)),
      ('', {}), ('RESULTADO', dict(bold=True, size=12)),
      (f'• Saída do cliente: {cnt.get("Saída do cliente", 0)} de {len(E)}. Nenhuma conta ficou sem assinatura por causa desses encerramentos (com janela de 3 dias aparece 1 caso, que reabre em seguida).', {}),
      (f'• Troca/ajuste: {cnt.get("Troca/ajuste", 0)} ({cnt.get("Troca/ajuste", 0)/len(E)*100:.0f}%). Entre as rápidas: {rap.get("Troca/ajuste", 0)} de {int(rap.sum())} ({rap.get("Troca/ajuste", 0)/rap.sum()*100:.0f}%).', {}),
      (f'• Redução: {cnt.get("Redução", 0)} ({cnt.get("Redução", 0)/len(E)*100:.0f}%).', {}),
      (f'• Cuidado: essas contas abrem assinaturas com frequência (≈ {REF*100:.0f}% de chance de haver uma nova em ±{JP} dias numa data qualquer). Parte das "trocas" pode ser coincidência.', {}),
      ('• As trocas vão para os dois lados (plano acima/abaixo/igual, cobrança e seats mudando nos dois sentidos): reconfiguração do contrato, não um movimento único.', {}),
      ('', {}), ('O QUE ISSO SIGNIFICA', dict(bold=True, size=12)),
      ('O aumento de "churn" em nov/dez não é perda de clientes: é movimentação de assinaturas dentro de contas que continuam ativas. Para medir churn de verdade é preciso separar: saída do cliente (perda), redução (perda parcial) e troca/ajuste (não é perda). Com a regra atual, tudo entra no mesmo número.', {}),
      ('Próximo passo natural: trazer os valores em US$ para cada tipo, para ver quanto de receita realmente saiu (redução) e quanto apenas mudou de assinatura (troca).', {}),
      ('', {}), ('ABAS', dict(bold=True, size=12)),
      ('• Resumo: contagem por tipo, por velocidade, mês, pico de 29–31/12, evento de churn e janelas de 3/7/14 dias.   • Trocas: o que a conta abriu no lugar.   • Por_perfil: tipo por plano, cobrança, seats e país.   • Lista_266: uma linha por assinatura, com a explicação da classificação.', {}),
      ('', {}), ('LIMITES', dict(bold=True, size=12)),
      ('• Base fictícia. A regra olha só a tabela de assinaturas (a confiável). "Redução" pode incluir casos em que a conta já tinha a assinatura substituta antes da janela.', {})]
for i, (tx, st) in enumerate(Lm, 1):
    x = ws.cell(i, 2, tx); x.font = Fn(**st) if st else Fn(); x.alignment = Alignment(wrap_text=True, vertical='top')
wb.calculation.fullCalcOnLoad = True; wb.active = 1
OUT.parent.mkdir(parents=True, exist_ok=True); wb.save(OUT); print('ok', OUT)
print(cnt.to_dict(), rap.to_dict(), round(REF, 3), contas_sem_ativa_31_12)
for w in JANELAS: print(w, E[f'tipo_{w}d'].value_counts().to_dict())
tt = E[E.tipo_7d == 'Troca/ajuste']; print(tt.plano_da_nova.value_counts().to_dict(), tt.cobranca_da_nova.value_counts().to_dict(), tt.seats_da_nova.value_counts().to_dict())
print(E.groupby(['dias_29_31_dez']).tipo_7d.value_counts().to_dict()); print(E.groupby('mes_fim').tipo_7d.value_counts().to_dict())
