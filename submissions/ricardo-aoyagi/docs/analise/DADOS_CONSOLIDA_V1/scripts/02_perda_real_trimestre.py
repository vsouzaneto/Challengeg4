# Quanto do "churn" contado hoje é perda de receita de verdade? Por trimestre (jan/23–dez/24), em quantidade e em US$ (MRR).
# Gerado com Claude (IA). Lê os CSVs originais sem alterá-los; grava planilha apartada.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.series import SeriesLabel
RAIZ = Path(__file__).resolve().parents[3]
DADOS = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / 'dados'
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else RAIZ / 'analise' / 'DADOS_CONSOLIDA_V1' / '02_Perda_Real_por_Trimestre.xlsx'
a, s = ler(DADOS); s = classificar(s)
E = s[s.end_date.notna()].copy(); E['trimestre_fim'] = E.end_date.apply(trimestre); E['trial'] = np.where(E.is_trial, 'Sim', 'Não')
CAT = ['Migração', 'Compra extra desfeita', 'Redução real', 'Saída do cliente']
lv = Livro(); leia = lv.aba('LEIA-ME'); w1 = lv.aba('1_Resumo_CEO'); w2 = lv.aba('2_Quantidade'); w3 = lv.aba('3_Valor_US$'); w4 = lv.aba('4_Por_plano')
B = 'Base_Encerradas'
lv.base(B, E, ['subscription_id', 'account_id', 'plan_tier', 'trial', 'seats', 'mrr_amount', 'start_date', 'end_date', 'dias_de_vida', 'trimestre_fim', 'situacao', 'assinatura_nova', 'mrr_reposto'],
        {'start_date': DT, 'end_date': DT, 'mrr_amount': USD, 'mrr_reposto': USD})
TQ, SI, MR, RP, PL = lv.R(B, 'trimestre_fim'), lv.R(B, 'situacao'), lv.R(B, 'mrr_amount'), lv.R(B, 'mrr_reposto'), lv.R(B, 'plan_tier')
F = {k: fill(v) for k, v in COR.items()}; HP = fill('B91C1C'); HN = fill('0E7C66')

# ---------- 2_Quantidade ----------
ws = w2; titulo(ws, 'Assinaturas encerradas por trimestre: o que foi perda e o que não foi (quantidade)',
    'Cada assinatura encerrada é contada hoje como "churn". Aqui ela é separada em: Migração (a conta abriu outra assinatura até 7 dias antes/depois — troca, não é perda), Compra extra desfeita (assinatura com até 30 dias, a conta já tinha outra mais antiga do mesmo plano ativa — desfez uma compra a mais, não é perda), Redução real (a conta desligou uma assinatura e seguiu cliente — perda) e Saída do cliente (ficou sem assinatura — perda).', 'J', 64)
H(ws, 4, ['Trimestre do fim', '"Churn" como contado hoje (assinaturas encerradas)', 'Migração (troca)', 'Compra extra desfeita', 'Redução real', 'Saída do cliente', 'PERDA REAL (redução real + saída)', 'NÃO era perda (migração + compra extra)', '% do "churn" de hoje que é perda real'],
  [HD, F['Churn de hoje'], F['Migração'], F['Compra extra desfeita'], F['Redução real'], F['Saída do cliente'], HP, HN, HX], 58)
r = 5
for q in TRIM:
    C(ws, r, 1, q, bold=True); C(ws, r, 2, f'=COUNTIFS({TQ},$A{r})', '#,##0')
    for j, k in enumerate(CAT, 3): C(ws, r, j, f'=COUNTIFS({TQ},$A{r},{SI},"{k}")', '#,##0')
    C(ws, r, 7, f'=E{r}+F{r}', '#,##0', True); C(ws, r, 8, f'=C{r}+D{r}', '#,##0'); C(ws, r, 9, f'=IF(B{r}>0,G{r}/B{r},"")', '0%'); r += 1
q2 = r; C(ws, r, 1, 'Total 24 meses', bold=True, fl=GRY)
for j in range(2, 9): C(ws, r, j, f'=SUM({L(j)}5:{L(j)}{r-1})', '#,##0', True, GRY)
C(ws, r, 9, f'=G{r}/B{r}', '0%', True, GRY)
ch = BarChart(); ch.type = 'col'; ch.grouping = 'stacked'; ch.overlap = 100; ch.title = 'Assinaturas encerradas por trimestre: o que era troca e o que era perda'; ch.height = 9; ch.width = 22
for j, k in zip((3, 4, 5, 6), CAT):
    ch.add_data(Reference(ws, min_col=j, min_row=5, max_row=q2 - 1), titles_from_data=False); ch.series[-1].tx = SeriesLabel(v=k); ch.series[-1].graphicalProperties.solidFill = COR[k]; ch.series[-1].graphicalProperties.line.solidFill = COR[k]
ch.set_categories(Reference(ws, min_col=1, min_row=5, max_row=q2 - 1)); ch.legend.position = 'b'; ch.gapWidth = 60; ws.add_chart(ch, f'A{q2 + 3}')
larguras(ws, [16, 16, 12, 12, 12, 12, 14, 14, 13])

# ---------- 3_Valor_US$ ----------
ws = w3; titulo(ws, 'MRR encerrado por trimestre: o que foi perda de receita e o que não foi (US$ por mês)',
    'Valores em MRR (receita mensal). Na migração, a assinatura encerrada foi trocada por outra: o "reposto" é o MRR da assinatura nova (cada nova contada uma única vez) e só a DIFERENÇA é perda (ou ganho, se a nova for mais cara). Compra extra desfeita não é perda. PERDA REAL = diferença nas trocas + redução real + saída.', 'L', 56)
H(ws, 4, ['Trimestre do fim', '"Churn" de receita como contado hoje', 'Migração: MRR encerrado', 'Migração: MRR reposto na assinatura nova', 'Migração: diferença (encerrado − reposto)', 'Compra extra desfeita', 'Redução real', 'Saída do cliente', 'PERDA REAL',
          'NÃO era perda', '% do "churn" de hoje que é perda real', 'Gráfico: reposto (até o encerrado)', 'Gráfico: diferença perdida na troca', 'Gráfico: ganho na troca'],
  [HD, F['Churn de hoje'], F['Migração'], F['Migração'], F['Diferença na troca'], F['Compra extra desfeita'], F['Redução real'], F['Saída do cliente'], HP, HN, HX, GRY, GRY, GRY], 64)
r = 5
for q in TRIM:
    C(ws, r, 1, q, bold=True); C(ws, r, 2, f'=SUMIFS({MR},{TQ},$A{r})', USD)
    C(ws, r, 3, f'=SUMIFS({MR},{TQ},$A{r},{SI},"Migração")', USD); C(ws, r, 4, f'=SUMIFS({RP},{TQ},$A{r},{SI},"Migração")', USD); C(ws, r, 5, f'=C{r}-D{r}', USD)
    for j, k in zip((6, 7, 8), CAT[1:]): C(ws, r, j, f'=SUMIFS({MR},{TQ},$A{r},{SI},"{k}")', USD)
    C(ws, r, 9, f'=E{r}+G{r}+H{r}', USD, True); C(ws, r, 10, f'=B{r}-I{r}', USD); C(ws, r, 11, f'=IF(B{r}>0,I{r}/B{r},"")', '0%')
    C(ws, r, 12, f'=MIN(C{r},D{r})', USD); C(ws, r, 13, f'=MAX(0,E{r})', USD); C(ws, r, 14, f'=MAX(0,-E{r})', USD); r += 1
v2 = r; C(ws, r, 1, 'Total 24 meses', bold=True, fl=GRY)
for j in range(2, 11): C(ws, r, j, f'=SUM({L(j)}5:{L(j)}{r-1})', USD, True, GRY)
C(ws, r, 11, f'=I{r}/B{r}', '0%', True, GRY)
for j in (12, 13, 14): C(ws, r, j, f'=SUM({L(j)}5:{L(j)}{r-1})', USD, True, GRY)
ch = BarChart(); ch.type = 'col'; ch.grouping = 'stacked'; ch.overlap = 100; ch.title = '"Churn" de receita de hoje, aberto: o que voltou/não era perda e o que foi perda (US$ de MRR)'; ch.height = 10; ch.width = 24
for j, nm, cor in [(12, 'Não era perda: reposto na troca', COR['Migração']), (6, 'Não era perda: compra extra desfeita', COR['Compra extra desfeita']), (13, 'Perda: diferença na troca', COR['Diferença na troca']),
                   (7, 'Perda: redução real', COR['Redução real']), (8, 'Perda: saída do cliente', COR['Saída do cliente'])]:
    ch.add_data(Reference(ws, min_col=j, min_row=5, max_row=v2 - 1), titles_from_data=False); ch.series[-1].tx = SeriesLabel(v=nm); ch.series[-1].graphicalProperties.solidFill = cor; ch.series[-1].graphicalProperties.line.solidFill = cor
ch.set_categories(Reference(ws, min_col=1, min_row=5, max_row=v2 - 1)); ch.legend.position = 'b'; ch.gapWidth = 60; ch.y_axis.number_format = '#,##0'; ws.add_chart(ch, f'A{v2 + 3}')
nota(ws, v2 + 1, 'Colunas L a N só alimentam o gráfico. Quando a assinatura nova é mais cara que a encerrada (ganho na troca, coluna N), o ganho já está descontado da PERDA REAL (coluna I).', 'K', 28)
larguras(ws, [16, 15, 14, 15, 15, 14, 14, 13, 15, 14, 12, 13, 13, 12])

# ---------- 4_Por_plano ----------
ws = w4; titulo(ws, 'Por plano, 24 meses: "churn" de hoje x perda por redução e saída', 'Mesmas regras das abas 2 e 3, somando jan/23–dez/24. As trocas (migrações) ficam fora da perda por plano porque muitas mudam de plano (ex.: encerra Basic e abre Enterprise): o saldo das trocas só faz sentido no total.', 'K', 46)
H(ws, 4, ['Plano', 'Encerradas', 'Migração', 'Compra extra desfeita', 'Redução real', 'Saída', '"Churn" de hoje (US$)', 'Migração: MRR encerrado (US$)', 'Compra extra desfeita (US$)', 'PERDA do plano: redução real + saída (US$)', '% do "churn" de hoje'],
  [HD, F['Churn de hoje'], F['Migração'], F['Compra extra desfeita'], F['Redução real'], F['Saída do cliente'], F['Churn de hoje'], F['Migração'], F['Compra extra desfeita'], HP, HX], 58); r = 5
for pl in ['Basic', 'Pro', 'Enterprise']:
    C(ws, r, 1, pl, bold=True); C(ws, r, 2, f'=COUNTIFS({PL},$A{r})', '#,##0')
    for j, k in enumerate(CAT, 3): C(ws, r, j, f'=COUNTIFS({PL},$A{r},{SI},"{k}")', '#,##0')
    C(ws, r, 7, f'=SUMIFS({MR},{PL},$A{r})', USD); C(ws, r, 8, f'=SUMIFS({MR},{PL},$A{r},{SI},"Migração")', USD); C(ws, r, 9, f'=SUMIFS({MR},{PL},$A{r},{SI},"Compra extra desfeita")', USD)
    C(ws, r, 10, f'=SUMIFS({MR},{PL},$A{r},{SI},"Redução real")+SUMIFS({MR},{PL},$A{r},{SI},"Saída do cliente")', USD, True); C(ws, r, 11, f'=J{r}/G{r}', '0%'); r += 1
C(ws, r, 1, 'Total', bold=True, fl=GRY)
for j in range(2, 11): C(ws, r, j, f'=SUM({L(j)}5:{L(j)}{r-1})', USD if j >= 7 else '#,##0', True, GRY)
C(ws, r, 11, f'=J{r}/G{r}', '0%', True, GRY); r += 1
C(ws, r, 1, '+ saldo das trocas (todas)', bold=True); C(ws, r, 10, f"='3_Valor_US$'!E{v2}", USD); r += 1
C(ws, r, 1, 'PERDA REAL total', bold=True, fl=GRY); C(ws, r, 10, f'=J{r-2}+J{r-1}', USD, True, GRY)
nota(ws, r + 2, 'Leitura: o Enterprise concentra a perda por redução: cada assinatura vale muito mais (US$ 199 por seat, contra 49 e 19).', 'K', 28)
larguras(ws, [24, 11, 11, 12, 11, 9, 15, 15, 14, 16, 11])

# ---------- 1_Resumo_CEO ----------
ws = w1; titulo(ws, 'Churn: o que é contado hoje x o que foi perda de verdade', 'Por trimestre, jan/23–dez/24. Barras cinzas = como o churn é contado hoje (toda assinatura encerrada). Barras vermelhas = perda real (redução real + saída do cliente; em US$, também a diferença nas trocas). Detalhes nas abas 2, 3 e 4.', 'K', 36)
H(ws, 4, ['Trimestre', 'Quantidade: "churn" de hoje', 'Quantidade: perda real', 'US$: "churn" de hoje', 'US$: perda real', '% perda real (US$)'], [HD, F['Churn de hoje'], HP, F['Churn de hoje'], HP, HX], 46); r = 5
for i, q in enumerate(TRIM):
    C(ws, r, 1, q, bold=True); C(ws, r, 2, f"='2_Quantidade'!B{5+i}", '#,##0'); C(ws, r, 3, f"='2_Quantidade'!G{5+i}", '#,##0')
    C(ws, r, 4, f"='3_Valor_US$'!B{5+i}", USD); C(ws, r, 5, f"='3_Valor_US$'!I{5+i}", USD); C(ws, r, 6, f'=IF(D{r}>0,E{r}/D{r},"")', '0%'); r += 1
rt = r; C(ws, r, 1, 'Total 24 meses', bold=True, fl=GRY)
for j in range(2, 6): C(ws, r, j, f'=SUM({L(j)}5:{L(j)}{r-1})', USD if j >= 4 else '#,##0', True, GRY)
C(ws, r, 6, f'=E{r}/D{r}', '0%', True, GRY)
for k, (cols, tt, fm) in enumerate([((2, 3), 'Assinaturas encerradas por trimestre: "churn" de hoje x perda real', '#,##0'), ((4, 5), 'MRR encerrado por trimestre (US$): "churn" de hoje x perda real', '#,##0')]):
    ch = BarChart(); ch.type = 'col'; ch.title = tt; ch.height = 8; ch.width = 17; ch.gapWidth = 50
    for j, nm, cor in zip(cols, ['Churn como contado hoje', 'Perda real'], ['9CA3AF', 'B91C1C']):
        ch.add_data(Reference(ws, min_col=j, min_row=5, max_row=rt - 1), titles_from_data=False); ch.series[-1].tx = SeriesLabel(v=nm); ch.series[-1].graphicalProperties.solidFill = cor; ch.series[-1].graphicalProperties.line.solidFill = cor
    ch.set_categories(Reference(ws, min_col=1, min_row=5, max_row=rt - 1)); ch.legend.position = 'b'; ch.y_axis.number_format = fm; ch.y_axis.majorGridlines = None
    ws.add_chart(ch, f'H{4 + k * 17}')
nota(ws, rt + 2, 'Leitura: até o 1º trimestre de 2024, quase todo o "churn" contado era perda real (≈90% em US$), mas pequena. No 2º e 3º trimestres de 2024, só cerca de 55–60% era perda. No 4º trimestre de 2024 o "churn" de hoje dispara (US$ 872 mil), mas só 38% (US$ 331 mil) foi perda real: o resto foram trocas e compras extras desfeitas. A perda real também cresce no 4º trimestre, puxada por reduções de assinaturas Enterprise.', 'F', 84)
larguras(ws, [16, 13, 13, 15, 15, 11])

# ---------- LEIA-ME ----------
tot = E.groupby('situacao').agg(n=('subscription_id', 'size'), v=('mrr_amount', 'sum'))
mig_enc, mig_rep = int(E[E.situacao == 'Migração'].mrr_amount.sum()), int(E[E.situacao == 'Migração'].mrr_reposto.sum())
real = mig_enc - mig_rep + int(tot.v.get('Redução real', 0)) + int(tot.v.get('Saída do cliente', 0)); hoje = int(E.mrr_amount.sum())
fmt = lambda v: f'US$ {v:,.0f}'.replace(',', '.')
leiame(leia, [('PERDA REAL x "CHURN" CONTADO HOJE — por trimestre, em quantidade e em US$', dict(bold=True, size=15)),
    ('Planilha apartada. Lê os CSVs originais sem alterá-los. Base: tabela de assinaturas (a única coerente). Valores em MRR (receita mensal).', dict(italic=True, color=GRAY)),
    ('', {}), ('COMO CADA ASSINATURA ENCERRADA FOI CLASSIFICADA', dict(bold=True, size=12)),
    ('• Migração (troca): a mesma conta abriu outra assinatura até 7 dias antes ou depois. NÃO é perda; em US$, só a diferença entre a encerrada e a nova conta.', {}),
    ('• Compra extra desfeita: a assinatura durou até 30 dias e a conta já tinha outra assinatura MAIS ANTIGA do mesmo plano ativa. A conta desfez uma compra a mais e voltou ao que pagava antes. NÃO é perda.', {}),
    ('• Redução real: a conta desligou uma assinatura (sem troca e sem ser compra extra recente) e continuou cliente. É perda de receita.', {}),
    ('• Saída do cliente: a conta ficou sem nenhuma assinatura ativa. É perda (só 4 casos em 24 meses, e todos voltaram depois).', {}),
    ('• Por que assinaturas "gêmeas" (mesmo plano e mesmos seats) com mais de 30 dias continuam como perda: na base, quase metade das assinaturas ativas tem uma gêmea; ter uma igual não prova troca.', dict(italic=True, color=GRAY)),
    ('', {}), ('RESULTADO EM 24 MESES (jan/23–dez/24)', dict(bold=True, size=12)),
    (f'• "Churn" como contado hoje: {len(E):,} assinaturas encerradas, {fmt(hoje)} de MRR.'.replace(',', '.'), {}),
    (f'• Não era perda: {int(tot.n.get("Migração", 0))} migrações (reposto {fmt(mig_rep)}) e {int(tot.n.get("Compra extra desfeita", 0))} compras extras desfeitas ({fmt(int(tot.v.get("Compra extra desfeita", 0)))}).', {}),
    (f'• PERDA REAL: {int(tot.n.get("Redução real", 0)) + int(tot.n.get("Saída do cliente", 0))} assinaturas e {fmt(real)} de MRR = {real / hoje:.0%} do "churn" de hoje: redução real {fmt(int(tot.v.get("Redução real", 0)))}, saída {fmt(int(tot.v.get("Saída do cliente", 0)))} e diferença nas trocas {fmt(mig_enc - mig_rep)}.', dict(bold=True)),
    ('', {}), ('ABAS', dict(bold=True, size=12)),
    ('• 1_Resumo_CEO: dois gráficos simples por trimestre ("churn" de hoje x perda real, em quantidade e em US$).', {}),
    ('• 2_Quantidade e 3_Valor_US$: o "churn" de hoje aberto nas 4 situações, por trimestre, com gráfico empilhado.', {}),
    ('• 4_Por_plano: as mesmas contas por plano, nos 24 meses.', {}),
    ('• Base_Encerradas: uma linha por assinatura encerrada, com a situação e o MRR reposto. Todas as abas são fórmulas sobre esta base.', {}),
    ('', {}), ('LIMITES', dict(bold=True, size=12)),
    ('• Base fictícia. As janelas de 7 dias (troca) e 30 dias (compra extra) são escolhas da análise. Diferença em relação à planilha 07 (US$ 718 mil de perda real): aqui a compra extra desfeita deixou de contar como perda.', {})])
lv.salvar(OUT); print('ok', OUT)
print(tot.to_dict()); print('hoje', hoje, 'reposto', mig_rep, 'dif troca', mig_enc - mig_rep, 'perda real', real)
