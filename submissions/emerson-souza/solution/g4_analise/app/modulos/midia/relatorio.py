"""Relatorio de Midia (Markdown e PDF) para o Head de Marketing."""

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

from .textos import dec, explicacao_metodo, num, resumo_executivo


def markdown(r, nome):
    L = [f"# Estratégia de social media — {nome}", f"_Gerado pelo G4 Analise em {datetime.now():%d/%m/%Y %H:%M}_", "", "## Resumo executivo"]
    L += [f"- {x}" for x in resumo_executivo(r)]
    L += ["", "## Estratégia priorizada", "", "| # | O quê | Para quem | Quando | Evidência |", "|---|---|---|---|---|"]
    for a in r["estrategia"].itertuples():
        L.append(f"| {a.prioridade} | **{a.acao}**: {a.o_que} | {a.para_quem} | {a.quando} | {a.evidencia} |")
    L += ["", "## Quick wins desta semana"] + [f"{i}. {q}" for i, q in enumerate(r["quick_wins"], 1)]
    L += ["", "## O que gera engajamento (cada dimensão)", "", "| Dimensão | Diferença máx. | p | Veredito |", "|---|---|---|---|"]
    for d in r["drivers"].values():
        L.append(f"| {d['rotulo']} | {dec(d['efeito_%'], 2)}% | {dec(d['p_valor'], 3)} | {d['veredito']} |")
    pat = r["patrocinio"]
    if pat and "custo" in pat:
        L += ["", "## Patrocínio: custo por faixa de criador (premissa de custo)", "",
              "| Faixa | Posts patrocinados | Views médias | Engajamento | Custo por interação (US$) |", "|---|---|---|---|---|"]
        for x in pat["custo"].itertuples():
            L.append(f"| {x.faixa_seguidores} | {num(x.posts)} | {num(x.views_medias)} | {dec(x.eng_medio, 2)}% | {dec(x.custo_por_interacao, 3)} |")
    s = r["sanidade"]
    if s:
        L += ["", "## Teste de sanidade (dados copiados, efeito injetado)"]
        for k, v in s.items():
            L.append(f"- {k}: injetado +{dec(v['injetado_%'], 0)}%, encontrado {dec(v['encontrado_%'], 1)}% (p = {dec(v['p_valor'], 3)}) → "
                     + ("a ferramenta encontrou" if v["achou"] else "não encontrou"))
    L += ["", "## Como os números foram calculados"] + [f"- {x}" for x in explicacao_metodo(r)]
    L += ["", "## Qualidade dos dados e limitações"] + [f"- {x}" for x in r["qualidade"]]
    return "\n".join(L).replace("$", "\\$")


def _p(t):
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)


def _png(fig):
    b = io.BytesIO()
    fig.savefig(b, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    b.seek(0)
    return b


def pdf(r, nome):
    est = getSampleStyleSheet()
    corpo, sub = est["BodyText"], est["Heading2"]
    peq = est["BodyText"].clone("peq", fontSize=7.5, leading=9)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1.5 * cm, rightMargin=1.5 * cm, topMargin=1.5 * cm)
    E = [Paragraph(f"Estratégia de social media — {nome}", est["Title"]), Paragraph(f"G4 Analise · {datetime.now():%d/%m/%Y %H:%M}", corpo),
         Spacer(1, 6), Paragraph("Resumo executivo", sub)] + [Paragraph("• " + _p(x), corpo) for x in resumo_executivo(r)]
    dados = [["#", "O quê", "Para quem / quando", "Evidência"]] + [
        [a.prioridade, Paragraph(f"<b>{a.acao}</b>: {a.o_que}", peq), Paragraph(f"{a.para_quem} · {a.quando}", peq), Paragraph(a.evidencia, peq)]
        for a in r["estrategia"].itertuples()]
    t = Table(dados, colWidths=[0.8 * cm, 9.5 * cm, 4 * cm, 3.5 * cm], repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E86AB")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                           ("GRID", (0, 0), (-1, -1), 0.3, colors.grey), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("FONTSIZE", (0, 0), (-1, -1), 8)]))
    E += [Paragraph("Estratégia priorizada", sub), t]
    pat = r["patrocinio"]
    if pat and "custo" in pat:
        cu = pat["custo"]
        fig, ax = plt.subplots(1, 2, figsize=(8, 2.6))
        ax[0].bar(cu.faixa_seguidores, cu.views_medias, color="#2E86AB")
        ax[0].set_title("Views médias por faixa (iguais)")
        ax[0].tick_params(axis="x", labelsize=7)
        ax[1].bar(cu.faixa_seguidores, cu.custo_por_interacao, color="#D1495B")
        ax[1].set_title("Custo por interação (US$, premissa)")
        ax[1].tick_params(axis="x", labelsize=7)
        E += [Spacer(1, 6), Image(_png(fig), width=17 * cm, height=5.5 * cm)]
    E += [Paragraph("Como os números foram calculados", sub)] + [Paragraph("• " + _p(x), corpo) for x in explicacao_metodo(r)]
    E += [Paragraph("Qualidade dos dados e limitações", sub)] + [Paragraph("• " + x, corpo) for x in r["qualidade"]]
    doc.build(E)
    return buf.getvalue()
