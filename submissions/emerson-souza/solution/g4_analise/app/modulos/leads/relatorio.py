"""Relatorio de Leads (Markdown e PDF) para a Head de RevOps."""

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

from .textos import dec, explicacao_metodo, moeda, num, pct, resumo_executivo

COLS = ["id_oportunidade", "vendedor", "produto", "conta", "score", "faixa", "valor_esperado", "motivos", "proxima_acao"]


def _linhas_deals(df):
    L = ["| Deal | Vendedor | Produto | Conta | Score | Faixa | Valor esperado | Por quê |", "|---|---|---|---|---|---|---|---|"]
    for d in df.itertuples():
        L.append(f"| {getattr(d, 'id_oportunidade', '')} | {d.vendedor} | {d.produto} | {getattr(d, 'conta', '') or '—'} | "
                 f"{d.score:.0f} | {d.faixa} | {moeda(d.valor_esperado)} | {d.motivos} |")
    return L


def markdown(r, nome):
    ab = r["abertos"]
    L = [f"# Priorização do pipeline — {nome}", f"_Gerado pelo G4 Analise em {datetime.now():%d/%m/%Y %H:%M}_", "", "## Resumo executivo"]
    L += [f"- {x}" for x in resumo_executivo(r)]
    L += ["", "## Plano de ação", "", "| # | Ação | Deals | Valor | Evidência |", "|---|---|---|---|---|"]
    for a in r["acoes"].itertuples():
        L.append(f"| {a.prioridade} | {a.acao} | {num(a.deals)} | {moeda(a.valor)} | {a.evidencia} |")
    vivos = ab[ab.lista == "Foco"]
    L += ["", "## Foco da semana (top 20 deals vivos por valor esperado)", ""] + _linhas_deals(vivos.head(20))
    L += ["", "## Requalificar (top 20 parados por valor)", ""] + _linhas_deals(ab[ab.parado].sort_values("valor", ascending=False).head(20))
    L += ["", "## Pipeline por vendedor", "", "| Vendedor | Gestor | Região | Abertos | Parados | Quentes | Valor esperado | Ganho histórico |",
          "|---|---|---|---|---|---|---|---|"]
    for v in r["vendedores"].itertuples():
        L.append(f"| {v.vendedor} | {getattr(v, 'gestor', '')} | {getattr(v, 'regiao', '')} | {v.abertos} | {v.parados} ({pct(v._7)}) | "
                 f"{v.quentes} | {moeda(v.valor_esperado)} | {pct(v._8)} |")
    L += ["", "## O que muda a chance (histórico)"]
    for f in r["fatores"].values():
        L += ["", f"**{f['rotulo']}** — p = {dec(f['p_valor'], 3)} ({f['evidencia']})", "", "| Grupo | Deals | Taxa de ganho | Pontos |", "|---|---|---|---|"]
        for g in f["tabela"].itertuples():
            L.append(f"| {g.grupo} | {g.deals} | {pct(g._4, 1)} | {g.pontos:+.1f} |")
    v = r["validacao"]
    if v:
        L += ["", "## Validação", f"Foto de {v['data_foto']:%d/%m/%Y}: {num(v['n_treino'])} deals para aprender, {num(v['n_teste'])} para testar. "
              f"AUC do score = {dec(v['auc'])}; AUC só pelo valor = {dec(v['auc_so_valor'])} (0,50 = acaso)."]
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


def _tabela(dados, larguras):
    t = Table(dados, colWidths=larguras, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E86AB")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                           ("GRID", (0, 0), (-1, -1), 0.3, colors.grey), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("FONTSIZE", (0, 0), (-1, -1), 7.5)]))
    return t


def pdf(r, nome):
    est = getSampleStyleSheet()
    corpo, sub = est["BodyText"], est["Heading2"]
    pequeno = est["BodyText"].clone("peq", fontSize=7, leading=8.5)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1.5 * cm, rightMargin=1.5 * cm, topMargin=1.5 * cm)
    E = [Paragraph(f"Priorização do pipeline — {nome}", est["Title"]), Paragraph(f"G4 Analise · {datetime.now():%d/%m/%Y %H:%M}", corpo),
         Spacer(1, 6), Paragraph("Resumo executivo", sub)] + [Paragraph("• " + _p(x), corpo) for x in resumo_executivo(r)]
    E += [Paragraph("Plano de ação", sub), _tabela([["#", "Ação", "Deals", "Valor", "Evidência"]] + [
        [a.prioridade, Paragraph(a.acao, pequeno), num(a.deals), moeda(a.valor), a.evidencia] for a in r["acoes"].itertuples()],
        [0.8 * cm, 9.5 * cm, 1.6 * cm, 3 * cm, 2.6 * cm])]
    c = r["curva"]
    if c:
        t = c["tabela"]
        fig, ax = plt.subplots(figsize=(7, 2.5))
        ax.plot(t.idade_dias, t["taxa_%"], color="#2E86AB")
        ax.axhline(100 * r["cortes"]["base"], color="#9AA5B1", ls="--", label="média")
        ax.set_xlabel("dias aberto")
        ax.set_ylabel("% de ganho")
        ax.set_title("Chance de ganhar dos deals que chegaram a cada idade")
        ax.legend()
        E += [Spacer(1, 6), Image(_png(fig), width=16 * cm, height=5.7 * cm)]
    vivos = r["abertos"][r["abertos"].lista == "Foco"].head(15)
    E += [Paragraph("Foco da semana (top 15 deals vivos por valor esperado)", sub), _tabela(
        [["Deal", "Vendedor", "Produto", "Score", "Valor esp.", "Por quê"]] + [
            [getattr(d, "id_oportunidade", ""), d.vendedor, d.produto, f"{d.score:.0f}", moeda(d.valor_esperado), Paragraph(d.motivos, pequeno)]
            for d in vivos.itertuples()], [1.8 * cm, 2.8 * cm, 2 * cm, 1.1 * cm, 2 * cm, 7.8 * cm])]
    E += [Paragraph("Como os números foram calculados", sub)] + [Paragraph("• " + _p(x), corpo) for x in explicacao_metodo(r)]
    E += [Paragraph("Qualidade dos dados e limitações", sub)] + [Paragraph("• " + x, corpo) for x in r["qualidade"]]
    doc.build(E)
    return buf.getvalue()
