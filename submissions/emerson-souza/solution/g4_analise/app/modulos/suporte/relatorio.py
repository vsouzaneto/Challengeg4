"""Relatorio do Suporte (Markdown e PDF) para o Diretor de Operacoes."""

import io
import re
from datetime import datetime

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.styles import getSampleStyleSheet  # noqa: E402
from reportlab.lib.units import cm  # noqa: E402
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle  # noqa: E402

from .textos import dec, explicacao_metodo, num, pct, reais, resumo_executivo


def markdown(r, nome):
    L = [f"# Diagnóstico de Suporte — {nome}", f"_Gerado pelo G4 Analise em {datetime.now():%d/%m/%Y %H:%M}_", "", "## Resumo executivo"]
    L += [f"- {x}" for x in resumo_executivo(r)]
    for d in r["gargalos"]["por_dimensao"].values():
        L += ["", f"## Tempo e acúmulo por {d['rotulo'].lower()} (tempo: p = {dec(d['p_tempo'])})", "",
              "| Grupo | Chamados | Mediana (h) | P90 (h) | Em aberto |", "|---|---|---|---|---|"]
        for _, x in d["tabela"].iterrows():
            L.append(f"| {x.iloc[0]} | {num(x.chamados)} | {dec(x.mediana_h, 1)} | {dec(x.p90_h, 1)} | {pct(x.get('em_aberto_%', float('nan')))} |")
    if r["satisfacao"]:
        L += ["", "## O que impacta a satisfação", "", "| Variável | p | Veredito |", "|---|---|---|"]
        for _, x in r["satisfacao"]["tabela"].iterrows():
            L.append(f"| {x['variável']} | {dec(x.p_valor, 3)} | {x.veredito} |")
    if r["desperdicio"]:
        L += ["", "## Desperdício (horas acima da meta)", "", "| Prioridade | Meta (h) | Estouraram | Horas acima | Custo |", "|---|---|---|---|---|"]
        for _, x in r["desperdicio"]["por_prioridade"].iterrows():
            L.append(f"| {x.prioridade} | {x.meta_h} | {int(x.estouraram)} de {int(x.chamados)} | {num(x.horas_acima_meta)} | {reais(x['custo_R$'])} |")
    c, a = r["classificador"], r["automacao"]
    if c:
        L += ["", "## Classificador (Dataset 2)", "", "| Abordagem | Acurácia | F1 |", "|---|---|---|"]
        for _, x in c["comparacao"].iterrows():
            L.append(f"| {x.abordagem} | {pct(100 * x['acurácia'], 1)} | {'' if x.f1_macro != x.f1_macro else dec(x.f1_macro)} |")
    if a:
        L += ["", "## Automação proposta", "", "| Faixa | % dos tickets | Acerto |", "|---|---|---|"]
        for _, x in a["faixas"].iterrows():
            L.append(f"| {x.faixa} | {pct(x['tickets_%'])} | {pct(x['acerto_%'], 1)} |")
        L += ["", "**Nunca automatizar:** " + "; ".join(f"{k}: {v} chamados" for k, v in a["bloqueados_por_regra"].items())
              + "; categoria Administrative rights; confiança baixa.",
              f"**Retorno estimado:** {num(a['horas_mes'])} h/mês ({reais(a['reais_mes'])}/mês)."]
    L += ["", "## Como os números foram calculados"] + [f"- {x}" for x in explicacao_metodo(r)]
    L += ["", "## Qualidade dos dados"] + [f"- {x}" for x in r["qualidade"]]
    return "\n".join(L).replace("$", "\\$")


def _p(texto):
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto)


def _png(fig):
    b = io.BytesIO()
    fig.savefig(b, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    b.seek(0)
    return b


def pdf(r, nome):
    est = getSampleStyleSheet()
    corpo, sub = est["BodyText"], est["Heading2"]
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm, topMargin=1.5 * cm)
    E = [Paragraph(f"Diagnóstico de Suporte — {nome}", est["Title"]), Paragraph(f"G4 Analise · {datetime.now():%d/%m/%Y %H:%M}", corpo),
         Spacer(1, 8), Paragraph("Resumo executivo", sub)] + [Paragraph("• " + _p(x), corpo) for x in resumo_executivo(r)]
    g = r["gargalos"]["por_dimensao"]
    if "prioridade" in g:
        t = g["prioridade"]["tabela"]
        fig, ax = plt.subplots(figsize=(7, 2.6))
        ax.bar(t.prioridade.astype(str), t.mediana_h, yerr=[t.mediana_h - t.ic_min_h, t.ic_max_h - t.mediana_h], color="#2E86AB", capsize=4)
        ax.set_ylabel("horas (mediana)")
        ax.set_title(f"Tempo de atendimento por prioridade (p = {dec(g['prioridade']['p_tempo'])})")
        E += [Spacer(1, 6), Image(_png(fig), width=16 * cm, height=6 * cm)]
    a = r["automacao"]
    if a:
        E += [Paragraph("Automação proposta", sub)]
        dados = [["Faixa", "% dos tickets", "Acerto"]] + [[x.faixa, pct(x["tickets_%"]), pct(x["acerto_%"], 1)] for _, x in a["faixas"].iterrows()]
        tb = Table(dados, colWidths=[8 * cm, 3.5 * cm, 3.5 * cm])
        tb.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E86AB")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                ("GRID", (0, 0), (-1, -1), 0.3, colors.grey), ("FONTSIZE", (0, 0), (-1, -1), 9)]))
        E += [tb, Spacer(1, 6), Paragraph(f"<b>Nunca automatizar:</b> cancelamento, reembolso, prioridade crítica, permissão de acesso "
                                         f"e confiança baixa. <b>Retorno estimado:</b> {num(a['horas_mes'])} h/mês ({reais(a['reais_mes'])}/mês).", corpo)]
    E += [Paragraph("Como os números foram calculados", sub)] + [Paragraph("• " + _p(x), corpo) for x in explicacao_metodo(r)]
    E += [Paragraph("Qualidade dos dados", sub)] + [Paragraph("• " + x.replace("{", "").replace("}", ""), corpo) for x in r["qualidade"]]
    doc.build(E)
    return buf.getvalue()
