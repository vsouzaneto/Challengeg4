# Ritmo de compra a partir de jul/2024: que país, indústria ou canal cresceu, e há sinais de "venda errada"?
# Gerado com Claude (IA). Lê os CSVs originais sem alterá-los; grava planilha apartada.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.chart.series import SeriesLabel
from openpyxl.formatting.rule import FormulaRule
RAIZ = Path(__file__).resolve().parents[3]
DADOS = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / 'dados'
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else RAIZ / 'analise' / 'DADOS_CONSOLIDA_V1' / '03_Ritmo_de_Compra_Segmentos.xlsx'
a, s = ler(DADOS); s = classificar(s); s['rajada'] = rajada(s)
s = s.sort_values(['account_id', 'start_date']); s['dias_desde_compra_anterior'] = s.groupby('account_id').start_date.diff().dt.days
s = s.merge(a[['account_id', 'industry', 'country', 'referral_source', 'signup_date']], on='account_id')
P1, P2, P3 = '1. 2023', '2. Jan–Jun/24', '3. Jul–Dez/24'; PER = [P1, P2, P3]; MESES = {P1: 12, P2: 6, P3: 6}
s['periodo'] = np.where(s.start_date < '2024-01-01', P1, np.where(s.start_date < '2024-07-01', P2, P3)); s['mes_inicio'] = s.start_date.dt.strftime('%Y-%m')
sn = lambda b: np.where(b, 'Sim', 'Não')
s['em_rajada'] = sn(s.rajada); s['ate_3_dias_da_anterior'] = np.where(s.dias_desde_compra_anterior.isna(), '', sn(s.dias_desde_compra_anterior <= 3))
s['cancelada_ate_30_dias'] = sn(s.end_date.notna() & (s.dias_de_vida <= 30)); s['compra_extra_desfeita'] = sn(s.situacao == 'Compra extra desfeita'); s['virou_troca'] = sn(s.situacao == 'Migração')
s['trial'] = sn(s.is_trial); s['conta_nova'] = sn((s.start_date - s.signup_date).dt.days < 30)
s['anual_cancelada_ate_30_dias'] = sn((s.billing_frequency == 'annual') & s.end_date.notna() & (s.dias_de_vida <= 30))
a['periodo_cadastro'] = np.where(a.signup_date < '2024-01-01', P1, np.where(a.signup_date < '2024-07-01', P2, P3))
DIM = [('country', 'País'), ('industry', 'Indústria'), ('referral_source', 'Canal de aquisição')]
SIG = [('em_rajada', '% em rajada (3+ compras em 7 dias)'), ('ate_3_dias_da_anterior', '% comprada até 3 dias depois da anterior'), ('cancelada_ate_30_dias', '% cancelada em até 30 dias'),
       ('compra_extra_desfeita', '% compra extra desfeita'), ('virou_troca', '% encerrada em troca'), ('anual_cancelada_ate_30_dias', '% anual cancelada em até 30 dias'), ('trial', '% trial'), ('conta_nova', '% comprada por conta nova (< 30 dias)')]
lv = Livro(); leia = lv.aba('LEIA-ME'); w1 = lv.aba('1_Crescimento'); w2 = lv.aba('2_Sinais_jul_dez_24'); w3 = lv.aba('3_Antes_x_Depois'); w4 = lv.aba('4_Mes_a_mes_canal')
B = 'Base_Assinaturas'
lv.base(B, s, ['subscription_id', 'account_id', 'country', 'industry', 'referral_source', 'plan_tier', 'billing_frequency', 'mrr_amount', 'start_date', 'mes_inicio', 'periodo', 'dias_desde_compra_anterior'] + [k for k, _ in SIG] + ['situacao'],
        {'start_date': DT, 'mrr_amount': USD})
lv.base('Base_Contas', a, ['account_id', 'country', 'industry', 'referral_source', 'signup_date', 'periodo_cadastro'], {'signup_date': DT})
PE = lv.R(B, 'periodo'); HG, HB2 = fill('0F766E'), fill('2A78D6'); HR_ = fill('B45309')

# ---------- 1_Crescimento ----------
ws = w1; titulo(ws, 'Quem cresceu a partir de jul/2024? Assinaturas novas por mês, por segmento',
    'Assinaturas iniciadas por mês (média do período). "Crescimento" = jul–dez/24 ÷ jan–jun/24. "Ganhou participação?" compara a fatia do segmento nas compras de jul–dez/24 com a de jan–jun/24. Contas novas = cadastros no período (tabela de contas).', 'L', 44)
r = 4; destaques = []
for col, lab in DIM:
    H(ws, r, [lab, 'Assinaturas/mês 2023', 'Assinaturas/mês jan–jun/24', 'Assinaturas/mês jul–dez/24', 'Crescimento (×)', 'Participação jan–jun/24', 'Participação jul–dez/24', 'Ganhou participação? (confiável?)', 'Contas novas jan–jun/24', 'Contas novas jul–dez/24'],
      [HD, HX, HX, HB2, HB2, HX, HB2, HX, HX, HB2], 52); r += 1; r0 = r
    n2, n3 = int((s.periodo == P2).sum()), int((s.periodo == P3).sum())
    for v in sorted(s[col].unique()):
        C(ws, r, 1, v, bold=True); cd = f'{lv.R(B, col)},$A{r}'
        for j, p in zip((2, 3, 4), PER): C(ws, r, j, f'=COUNTIFS({cd},{PE},"{p}")/{MESES[p]}', '0.0')
        C(ws, r, 5, f'=D{r}/C{r}', '0.00"×"'); C(ws, r, 6, f'=COUNTIFS({cd},{PE},"{P2}")/COUNTIFS({PE},"{P2}")', '0.0%'); C(ws, r, 7, f'=COUNTIFS({cd},{PE},"{P3}")/COUNTIFS({PE},"{P3}")', '0.0%')
        k3, k2 = int(((s[col] == v) & (s.periodo == P3)).sum()), int(((s[col] == v) & (s.periodo == P2)).sum()); cv = conf(k3, n3, k2, n2)
        if cv == 'Sim': cv = 'Sim, ganhou' if k3 / n3 > k2 / n2 else 'Sim, perdeu'
        if cv.startswith('Sim'): destaques.append(f'{v} ({k3 / n3:.0%} contra {k2 / n2:.0%}; {cv.split(", ")[1]})')
        C(ws, r, 8, cv)
        for j, p in zip((9, 10), (P2, P3)): C(ws, r, j, f'=COUNTIFS({lv.R("Base_Contas", col)},$A{r},{lv.R("Base_Contas", "periodo_cadastro")},"{p}")', '#,##0')
        r += 1
    C(ws, r, 1, 'Total', bold=True, fl=GRY)
    for j in (2, 3, 4, 9, 10): C(ws, r, j, f'=SUM({L(j)}{r0}:{L(j)}{r-1})', '0.0' if j < 9 else '#,##0', True, GRY)
    C(ws, r, 5, f'=D{r}/C{r}', '0.00"×"', True, GRY)
    ch = BarChart(); ch.type = 'bar'; ch.title = f'Crescimento das compras (jul–dez/24 ÷ jan–jun/24) — {lab}'; ch.height = 6.5; ch.width = 13; ch.legend = None
    ch.add_data(Reference(ws, min_col=5, min_row=r0, max_row=r - 1), titles_from_data=False); ch.set_categories(Reference(ws, min_col=1, min_row=r0, max_row=r - 1))
    ch.series[0].graphicalProperties.solidFill = '2A78D6'; ch.y_axis.scaling.min = 0; ch.y_axis.scaling.max = 3.5; ch.y_axis.number_format = '0.0'; ws.add_chart(ch, f'L{r0 - 1}')
    r += 3 if r - r0 > 6 else 6
ws.conditional_formatting.add(f'H4:H{r}', FormulaRule(formula=['LEFT(H4,3)="Sim"'], fill=YEL))
nota(ws, r, 'Leitura: TODOS os segmentos passaram a comprar mais por mês a partir de jul/24 (de 1,7 a 3,2 vezes; média 2,7). Cresceram acima da média (ganharam participação): EUA, Cybersecurity e canal orgânico. Abaixo: Alemanha (a que menos cresceu), HealthTech e canal partner. Os cadastros de contas NOVAS cresceram bem menos (121 → 152, +26%) do que as compras (+174%): o salto veio de clientes que já existiam comprando mais assinaturas.', 'J', 60)
larguras(ws, [18, 11, 11, 11, 10, 11, 11, 20, 10, 10])

# ---------- 2_Sinais_jul_dez_24 ----------
S3 = s[s.periodo == P3]
ws = w2; titulo(ws, 'Há sinais de "venda errada" em algum segmento? Assinaturas iniciadas em jul–dez/2024',
    'Sinais de compra mal feita: compra em rajada, compra poucos dias depois da anterior, cancelamento em até 30 dias, compra extra desfeita, troca, anual cancelada em até 30 dias. "Confiável?" compara o segmento com todos os outros juntos, no mesmo período.', 'Q', 44)
r = 4
KEY = ['em_rajada', 'cancelada_ate_30_dias', 'compra_extra_desfeita']
for col, lab in DIM:
    hdr = [lab, 'Assinaturas jul–dez/24']; fl = [HD, HX]
    for k, nm in SIG:
        hdr.append(nm); fl.append(HR_ if k in KEY else HX)
        if k in KEY: hdr.append('Confiável?'); fl.append(HX)
    H(ws, r, hdr, fl, 64); r += 1; r0 = r
    for v in sorted(s[col].unique()):
        C(ws, r, 1, v, bold=True); cd = f'{lv.R(B, col)},$A{r},{PE},"{P3}"'; C(ws, r, 2, f'=COUNTIFS({cd})', '#,##0'); j = 3
        x, y = S3[S3[col] == v], S3[S3[col] != v]
        for k, nm in SIG:
            den = f'COUNTIFS({cd},{lv.R(B, k)},"<>")' if k == 'ate_3_dias_da_anterior' else f'$B{r}'
            C(ws, r, j, f'=COUNTIFS({cd},{lv.R(B, k)},"Sim")/{den}', '0.0%'); j += 1
            if k in KEY: C(ws, r, j, conf((x[k] == 'Sim').sum(), len(x), (y[k] == 'Sim').sum(), len(y))); j += 1
        r += 1
    C(ws, r, 1, 'Todos', bold=True, fl=GRY); C(ws, r, 2, f'=COUNTIFS({PE},"{P3}")', '#,##0', True, GRY); j = 3
    for k, nm in SIG:
        den = f'COUNTIFS({PE},"{P3}",{lv.R(B, k)},"<>")' if k == 'ate_3_dias_da_anterior' else f'$B{r}'
        C(ws, r, j, f'=COUNTIFS({PE},"{P3}",{lv.R(B, k)},"Sim")/{den}', '0.0%', True, GRY); j += 1
        if k in KEY: C(ws, r, j, '', fl=GRY); j += 1
    r += 3
amarelo(ws, f'A4:N{r}')
nota(ws, r, 'Leitura: o cancelamento em até 30 dias fica entre 5% e 8% em praticamente todos os segmentos, sem diferença confiável — não há um país, indústria ou canal "vendendo errado" sozinho. A compra em rajada é mais comum no canal orgânico (≈30%), em DevTools (≈27%) e nos EUA (≈23%), e mais rara na Alemanha (≈3%), em HealthTech e no canal partner (≈17%). Compra extra desfeita um pouco maior no Canadá e no canal ads, menor nos EUA (diferenças pequenas). Como o orgânico não tem vendedor, a rajada aponta mais para o processo de compra (autoatendimento/checkout) do que para um time de vendas.', 'N', 70)
larguras(ws, [18, 11] + [11] * 11)

# ---------- 3_Antes_x_Depois ----------
ws = w3; titulo(ws, 'A piora foi em todos os segmentos ao mesmo tempo?', 'Mesma medida antes (jan–jun/24) e depois (jul–dez/24) de jul/2024, em cada segmento.', 'I')
r = 4
for col, lab in DIM:
    H(ws, r, [lab, '% em rajada jan–jun/24', '% em rajada jul–dez/24', '% cancelada em até 30 dias jan–jun/24', '% cancelada em até 30 dias jul–dez/24', 'Cancelamento em 30 dias piorou? (confiável?)', 'Dias típicos entre compras jan–jun/24', 'Dias típicos entre compras jul–dez/24'],
      [HD, HX, HR_, HX, HR_, HX, HX, HR_], 58); r += 1
    for v in sorted(s[col].unique()) + ['Todos']:
        isT = v == 'Todos'; C(ws, r, 1, v, bold=True, fl=GRY if isT else None)
        cd = (lambda p: f'{PE},"{p}"') if isT else (lambda p: f'{lv.R(B, col)},$A{r},{PE},"{p}"')
        for j, k, p in [(2, 'em_rajada', P2), (3, 'em_rajada', P3), (4, 'cancelada_ate_30_dias', P2), (5, 'cancelada_ate_30_dias', P3)]:
            C(ws, r, j, f'=COUNTIFS({cd(p)},{lv.R(B, k)},"Sim")/COUNTIFS({cd(p)})', '0.0%', fl=GRY if isT else None)
        x2 = s[(s.periodo == P2) & ((s[col] == v) if not isT else True)]; x3 = s[(s.periodo == P3) & ((s[col] == v) if not isT else True)]
        C(ws, r, 6, conf((x3.cancelada_ate_30_dias == 'Sim').sum(), len(x3), (x2.cancelada_ate_30_dias == 'Sim').sum(), len(x2)), fl=GRY if isT else None)
        C(ws, r, 7, float(x2.dias_desde_compra_anterior.median()), '0', fl=GRY if isT else None); C(ws, r, 8, float(x3.dias_desde_compra_anterior.median()), '0', fl=GRY if isT else None); r += 1
    r += 1
amarelo(ws, f'F4:F{r}')
nota(ws, r, 'Leitura: em quase TODOS os segmentos a compra em rajada salta (de ~3% para ~20%; a exceção é a Alemanha, que fica em ~3–5%), o cancelamento em até 30 dias sobe (de <1% para ~6%) e o intervalo típico entre compras da mesma conta encurta (de ~4 semanas para ~1,5 semana). A mudança foi geral e simultânea — típico de uma mudança de processo, sistema ou regra comercial, não de um vendedor ou mercado específico. Colunas G e H (mediana) são calculadas pelo programa.', 'H', 56)
larguras(ws, [18, 11, 11, 13, 13, 20, 12, 12])

# ---------- 4_Mes_a_mes_canal ----------
ws = w4; titulo(ws, 'Assinaturas novas por mês e por canal, e % em rajada', 'Assinaturas iniciadas em cada mês.', 'I')
CAN = sorted(s.referral_source.unique()); meses = sorted(s.mes_inicio.unique())
H(ws, 4, ['Mês'] + CAN + ['Total', '% em rajada (todos)'], [HD] + [HX] * len(CAN) + [HD, HR_], 34); r = 5
for m in meses:
    C(ws, r, 1, m, bold=True)
    for j, cn in enumerate(CAN, 2): C(ws, r, j, f'=COUNTIFS({lv.R(B, "mes_inicio")},$A{r},{lv.R(B, "referral_source")},"{cn}")', '#,##0')
    C(ws, r, 2 + len(CAN), f'=SUM(B{r}:{L(1 + len(CAN))}{r})', '#,##0', True); C(ws, r, 3 + len(CAN), f'=COUNTIFS({lv.R(B, "mes_inicio")},$A{r},{lv.R(B, "em_rajada")},"Sim")/{L(2 + len(CAN))}{r}', '0%'); r += 1
ch = LineChart(); ch.title = 'Assinaturas novas por mês, por canal'; ch.height = 8; ch.width = 20
for j, cn in enumerate(CAN, 2):
    ch.add_data(Reference(ws, min_col=j, min_row=5, max_row=r - 1), titles_from_data=False); ch.series[-1].tx = SeriesLabel(v=cn); ch.series[-1].graphicalProperties.line.width = 20000
ch.set_categories(Reference(ws, min_col=1, min_row=5, max_row=r - 1)); ch.legend.position = 'b'; ws.add_chart(ch, 'J4')
larguras(ws, [10] + [9] * (len(CAN) + 2))

leiame(leia, [('RITMO DE COMPRA A PARTIR DE JUL/2024 — quem cresceu e há "venda errada"?', dict(bold=True, size=15)),
    ('Planilha apartada. Lê os CSVs originais sem alterá-los. Base: tabela de assinaturas + país/indústria/canal da conta.', dict(italic=True, color=GRAY)),
    ('', {}), ('RESPOSTAS', dict(bold=True, size=12)),
    ('1. Quem cresceu?  → aba 1', dict(bold=True)),
    ('   Todos: de jan–jun/24 para jul–dez/24, as compras por mês ficam 2 a 3 vezes maiores em todos os países, indústrias e canais. Ganharam participação de forma confiável: ' + '; '.join(d for d in destaques if 'ganhou' in d) + '. Perderam: ' + '; '.join(d for d in destaques if 'perdeu' in d) + '.', {}),
    ('   O número de contas novas quase não mudou: o crescimento veio de clientes que já existiam comprando mais assinaturas, mais rápido.', {}),
    ('2. Algum segmento está vendendo errado?  → aba 2', dict(bold=True)),
    ('   Não isoladamente. Cancelamento em até 30 dias, compra extra desfeita e troca ficam parecidos em todos. A compra em rajada é mais comum no canal orgânico e em DevTools e mais rara na Alemanha, em HealthTech e no canal partner.', {}),
    ('3. A piora foi geral?  → aba 3', dict(bold=True)),
    ('   Sim. Rajada, cancelamento em 30 dias e o encurtamento do intervalo entre compras aparecem em todos os segmentos ao mesmo tempo, a partir de jul/24. Isso indica uma mudança de processo (como se compra/registra uma assinatura), não um mercado ou vendedor.', {}),
    ('4. Mês a mês  → aba 4: assinaturas novas por canal e % em rajada.', dict(bold=True)),
    ('', {}), ('PERGUNTA PARA A EMPRESA', dict(bold=True, size=12)),
    ('O que mudou em jul–ago/2024 no processo de compra? (novo checkout/autoatendimento, campanha, regra de cobrança por assinatura em vez de por seat, integração de sistema que duplica pedidos?) Nenhum dado das 5 tabelas registra isso.', {}),
    ('', {}), ('DEFINIÇÕES E LIMITES', dict(bold=True, size=12)),
    ('• Rajada = 3+ assinaturas da mesma conta em 7 dias corridos. Compra extra desfeita = até 30 dias de vida, havendo outra mais antiga do mesmo plano ativa. Troca = nova assinatura da conta até 7 dias antes/depois.', {}),
    ('• Assinaturas de dez/24 têm menos tempo para serem canceladas em 30 dias: compare segmentos dentro do mesmo período. Base fictícia.', {})])
lv.salvar(OUT); print('ok', OUT); print(destaques)
