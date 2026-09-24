"""Relatorio do Churn para baixar: Markdown e PDF (para o CEO)."""

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

from .textos import correlacao_causalidade, dec, explicacao_metodo, pct, resumo_executivo, valor


def markdown(r, nome_sessao):
    L = [f"# Diagnóstico de Churn — {nome_sessao}", f"_Gerado pelo G4 Analise em {datetime.now():%d/%m/%Y %H:%M}_", "",
         "## Resumo executivo"]
    L += [f"- {x}" for x in resumo_executivo(r)]
    L += ["", "## Plano de ação (priorizado)", "",
          "| # | Ação | Contas | MRR em jogo | Impacto estimado | Evidência |", "|---|---|---|---|---|---|"]
    for a in r["acoes"].itertuples():
        L.append(f"| {a.prioridade} | {a.acao} | {a.contas} | {valor(r, a.mrr_em_jogo)} | {valor(r, a.impacto_estimado_mrr)} | {a.evidencia} |")
    L += ["", "## Motivos declarados", "", "| Motivo | Contas | % | MRR perdido |", "|---|---|---|---|"]
    for m in r["motivos"].itertuples():
        L.append(f"| {m.motivo} | {m.contas} | {pct(m._3, 1)} | {valor(r, m.mrr_perdido)} |")
    L += ["", "## Sinais testados", "", "| Sinal | Contas com sinal | Churn com | Churn sem | p | Evidência |", "|---|---|---|---|---|---|"]
    for s in r["sinais"].itertuples():
        L.append(f"| {s.sinal} | {s.contas_com_sinal} | {pct(s._4, 1)} | {pct(s._5, 1)} | {dec(s.p_valor)} | {s.evidencia} |")
    L += ["", "## Segmentos"]
    for seg in r["segmentos"].values():
        L += ["", f"**{seg['rotulo']}** (p = {dec(seg['p_valor'])}; média {pct(seg['media_%'], 1)})", "",
              "| Grupo | Contas | Taxa | IC 95% |", "|---|---|---|---|"]
        for g in seg["tabela"].itertuples():
            L.append(f"| {g.grupo} | {g.contas} | {pct(g._4, 1)} | {pct(g._5)}–{pct(g._6)} |")
    top = r["ativos"].head(20)
    L += ["", "## Contas ativas prioritárias (top 20)", "", "| Conta | Prioridade | Risco | MRR | Por quê |", "|---|---|---|---|---|"]
    for i, c in top.iterrows():
        L.append(f"| {i} | {c.prioridade} | {c.score_risco:.0f} | {valor(r, c.mrr)} | {c.motivos_do_score} |")
    L += ["", "## Como os números foram calculados"] + [f"- {x}" for x in explicacao_metodo(r)]
    L += ["", "## Correlação × causalidade", correlacao_causalidade(), "", "## Qualidade dos dados"]
    L += [f"- {x}" for x in r["qualidade"]]
    return "\n".join(L).replace("$", "\\$")


def _sem_markdown(texto):
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto).replace("_", "")


def _grafico_png(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def pdf(r, nome_sessao):
    estilos = getSampleStyleSheet()
    corpo, titulo, sub = estilos["BodyText"], estilos["Title"], estilos["Heading2"]
    doc_buf = io.BytesIO()
    doc = SimpleDocTemplate(doc_buf, pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm, topMargin=1.5 * cm)
    E = [Paragraph(f"Diagnóstico de Churn — {nome_sessao}", titulo),
         Paragraph(f"G4 Analise · {datetime.now():%d/%m/%Y %H:%M}", corpo), Spacer(1, 8),
         Paragraph("Resumo executivo", sub)]
    E += [Paragraph("• " + _sem_markdown(x), corpo) for x in resumo_executivo(r)]

    E += [Spacer(1, 8), Paragraph("Plano de ação (priorizado pela evidência)", sub)]
    dados = [["#", "Ação", "Contas", "Impacto/mês", "Evidência"]] + [
        [a.prioridade, Paragraph(a.acao, corpo), a.contas, valor(r, a.impacto_estimado_mrr), Paragraph(a.evidencia, corpo)]
        for a in r["acoes"].itertuples()]
    t = Table(dados, colWidths=[0.8 * cm, 8 * cm, 1.6 * cm, 2.8 * cm, 4 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E86AB")),
                           ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                           ("VALIGN", (0, 0), (-1, -1), "TOP"), ("FONTSIZE", (0, 0), (-1, -1), 8)]))
    E.append(t)

    # graficos: motivos e segmento
    mot = r["motivos"]
    fig, ax = plt.subplots(figsize=(7, 2.6))
    ax.barh(mot.motivo[::-1], mot["%"][::-1], color="#2E86AB")
    ax.set_xlabel("% das contas canceladas")
    ax.set_title("Motivo declarado do cancelamento")
    E += [Spacer(1, 8), Image(_grafico_png(fig), width=16 * cm, height=6 * cm)]
    if "segmento" in r["segmentos"]:
        seg = r["segmentos"]["segmento"]
        tab = seg["tabela"]
        fig, ax = plt.subplots(figsize=(7, 2.6))
        ax.bar(tab.grupo, tab["taxa_%"], yerr=[tab["taxa_%"] - tab["ic_min_%"], tab["ic_max_%"] - tab["taxa_%"]],
               color="#2E86AB", capsize=4)
        ax.axhline(seg["media_%"], color="#D1495B", ls="--", label="média")
        ax.set_ylabel("% de churn")
        ax.set_title(f"Churn por segmento (barras = intervalo de 95%; p = {dec(seg['p_valor'])})")
        ax.legend()
        E += [Image(_grafico_png(fig), width=16 * cm, height=6 * cm)]

    E += [Paragraph("Como os números foram calculados", sub)] + [Paragraph("• " + _sem_markdown(x), corpo) for x in explicacao_metodo(r)]
    E += [Paragraph("Correlação × causalidade", sub), Paragraph(_sem_markdown(correlacao_causalidade()), corpo)]
    E += [Paragraph("Qualidade dos dados", sub)] + [Paragraph("• " + x, corpo) for x in r["qualidade"]]
    doc.build(E)
    return doc_buf.getvalue()
