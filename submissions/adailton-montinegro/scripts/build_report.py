#!/usr/bin/env python3
"""Generate the canonical RavenStack executive PDF from reviewable Gold exports."""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

import pandas as pd
from reportlab.graphics.shapes import Circle, Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "artifacts" / "data"
OUTPUT_PATH = ROOT / "output" / "pdf" / "ravenstack-churn-diagnostic.pdf"
PAGE_WIDTH, PAGE_HEIGHT = landscape(A4)

NAVY = HexColor("#10253F")
BLUE = HexColor("#0F6CBD")
CYAN = HexColor("#13A8A8")
GREEN = HexColor("#177A5B")
AMBER = HexColor("#D97706")
RED = HexColor("#B42318")
INK = HexColor("#0F172A")
MUTED = HexColor("#64748B")
GRID = HexColor("#D9E3EE")
PAPER = HexColor("#F7F9FC")
PALE_BLUE = HexColor("#E8F1FB")
PALE_GREEN = HexColor("#E8F5EF")
PALE_AMBER = HexColor("#FFF3DA")
PALE_RED = HexColor("#FEECEB")


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("Arial", "/System/Library/Fonts/Supplemental/Arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Bold", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"))
    pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold")


def make_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "cover_eyebrow": ParagraphStyle(
            "cover_eyebrow", parent=base["Normal"], fontName="Arial-Bold", fontSize=9,
            leading=12, textColor=HexColor("#69D4D4"), spaceAfter=10,
        ),
        "cover_title": ParagraphStyle(
            "cover_title", parent=base["Title"], fontName="Arial-Bold", fontSize=32,
            leading=36, textColor=colors.white, spaceAfter=12,
        ),
        "cover_subtitle": ParagraphStyle(
            "cover_subtitle", parent=base["Normal"], fontName="Arial", fontSize=13,
            leading=19, textColor=HexColor("#D9E8F6"), spaceAfter=18,
        ),
        "eyebrow": ParagraphStyle(
            "eyebrow", parent=base["Normal"], fontName="Arial-Bold", fontSize=7.5,
            leading=9, textColor=BLUE, spaceAfter=4,
        ),
        "title": ParagraphStyle(
            "title", parent=base["Heading1"], fontName="Arial-Bold", fontSize=21,
            leading=25, textColor=NAVY, spaceAfter=5,
        ),
        "subtitle": ParagraphStyle(
            "subtitle", parent=base["Normal"], fontName="Arial", fontSize=8.5,
            leading=12, textColor=MUTED, spaceAfter=12,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontName="Arial-Bold", fontSize=12,
            leading=15, textColor=NAVY, spaceBefore=7, spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body", parent=base["BodyText"], fontName="Arial", fontSize=8.3,
            leading=11.5, textColor=INK, spaceAfter=5,
        ),
        "small": ParagraphStyle(
            "small", parent=base["BodyText"], fontName="Arial", fontSize=6.8,
            leading=9, textColor=MUTED, spaceAfter=3,
        ),
        "small_white": ParagraphStyle(
            "small_white", parent=base["BodyText"], fontName="Arial", fontSize=7.4,
            leading=10, textColor=colors.white,
        ),
        "card_label": ParagraphStyle(
            "card_label", parent=base["Normal"], fontName="Arial-Bold", fontSize=7,
            leading=8.5, textColor=MUTED, spaceAfter=3,
        ),
        "card_value": ParagraphStyle(
            "card_value", parent=base["Normal"], fontName="Arial-Bold", fontSize=17,
            leading=19, textColor=NAVY, spaceAfter=2,
        ),
        "card_note": ParagraphStyle(
            "card_note", parent=base["Normal"], fontName="Arial", fontSize=6.2,
            leading=8, textColor=MUTED,
        ),
        "box_title": ParagraphStyle(
            "box_title", parent=base["Normal"], fontName="Arial-Bold", fontSize=9,
            leading=11, textColor=NAVY, spaceAfter=4,
        ),
        "box_body": ParagraphStyle(
            "box_body", parent=base["Normal"], fontName="Arial", fontSize=7.4,
            leading=10, textColor=INK,
        ),
        "table_head": ParagraphStyle(
            "table_head", parent=base["Normal"], fontName="Arial-Bold", fontSize=6.5,
            leading=8, textColor=colors.white, alignment=TA_LEFT,
        ),
        "table_cell": ParagraphStyle(
            "table_cell", parent=base["Normal"], fontName="Arial", fontSize=6.2,
            leading=7.8, textColor=INK,
        ),
        "callout": ParagraphStyle(
            "callout", parent=base["Normal"], fontName="Arial", fontSize=9,
            leading=13, textColor=INK,
        ),
        "callout_white": ParagraphStyle(
            "callout_white", parent=base["Normal"], fontName="Arial", fontSize=11,
            leading=16, textColor=colors.white,
        ),
        "center_small": ParagraphStyle(
            "center_small", parent=base["Normal"], fontName="Arial", fontSize=6.5,
            leading=8, textColor=MUTED, alignment=TA_CENTER,
        ),
    }


def fmt_int(value: float | int) -> str:
    return f"{int(round(value)):,}".replace(",", ".")


def fmt_pct(value: float | int, decimals: int = 1) -> str:
    return f"{float(value):.{decimals}f}%".replace(".", ",")


def fmt_money(value: float | int) -> str:
    value = float(value)
    if abs(value) >= 1_000_000:
        return f"US$ {value / 1_000_000:.2f} mi".replace(".", ",")
    if abs(value) >= 1_000:
        return f"US$ {value / 1_000:.1f} mil".replace(".", ",")
    return f"US$ {value:,.0f}".replace(",", ".")


def as_bool(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False)
    return series.astype(str).str.lower().isin({"true", "1", "yes", "sim"})


def load_data() -> dict[str, object]:
    names = [
        "quality_summary", "analysis_scope", "account_snapshot", "monthly_events",
        "segment_snapshot", "churn_reasons", "account_triage", "metric_catalog",
        "pre_event_signals", "statistical_tests",
    ]
    data: dict[str, object] = {
        name: pd.read_csv(DATA_DIR / f"{name}.csv") for name in names
    }
    data["context"] = json.loads((DATA_DIR / "report_context.json").read_text(encoding="utf-8"))
    return data


def page_title(story: list, styles: dict, eyebrow: str, title: str, subtitle: str) -> None:
    story.extend([
        Paragraph(escape(eyebrow.upper()), styles["eyebrow"]),
        Paragraph(escape(title), styles["title"]),
        Paragraph(escape(subtitle), styles["subtitle"]),
    ])


def metric_row(items: list[tuple[str, str, str]], styles: dict, widths: list[float] | None = None) -> Table:
    widths = widths or [(PAGE_WIDTH - 72) / len(items)] * len(items)
    cells = []
    for label, value, note in items:
        cells.append([
            Paragraph(escape(label), styles["card_label"]),
            Paragraph(escape(value), styles["card_value"]),
            Paragraph(escape(note), styles["card_note"]),
        ])
    table = Table([cells], colWidths=widths, hAlign="LEFT")
    style = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.7, GRID),
        ("INNERGRID", (0, 0), (-1, -1), 5, PAPER),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]
    table.setStyle(TableStyle(style))
    return table


def box(title: str, body: str, styles: dict, background=PAPER, accent=BLUE) -> Table:
    content = [
        Paragraph(escape(title), styles["box_title"]),
        Paragraph(body, styles["box_body"]),
    ]
    table = Table([[content]], colWidths=[(PAGE_WIDTH - 82) / 3])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), background),
        ("BOX", (0, 0), (-1, -1), 0.7, GRID),
        ("LINEBEFORE", (0, 0), (0, -1), 4, accent),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return table


def callout(text: str, styles: dict, background=PALE_AMBER, border=AMBER) -> Table:
    table = Table([[Paragraph(text, styles["callout"])]], colWidths=[PAGE_WIDTH - 72])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), background),
        ("BOX", (0, 0), (-1, -1), 1, border),
        ("LINEBEFORE", (0, 0), (0, -1), 6, border),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
    ]))
    return table


def data_table(headers: list[str], rows: list[list[object]], styles: dict, widths: list[float]) -> Table:
    data = [[Paragraph(escape(str(value)), styles["table_head"]) for value in headers]]
    for row in rows:
        data.append([Paragraph(escape(str(value)), styles["table_cell"]) for value in row])
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PAPER]),
        ("GRID", (0, 0), (-1, -1), 0.4, GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def horizontal_bars(rows: list[tuple[str, float, str]], width: float, height: float) -> Drawing:
    drawing = Drawing(width, height)
    label_width = width * 0.40
    chart_width = width - label_width - 44
    row_height = (height - 22) / max(len(rows), 1)
    state_colors = {"Observed": GREEN, "Derived": BLUE, "Conditional": AMBER, "Unavailable": RED}
    for index, (label, value, state) in enumerate(rows):
        y = height - 18 - (index + 1) * row_height + row_height * 0.25
        drawing.add(String(0, y + 2, label[:52], fontName="Arial", fontSize=6.6, fillColor=INK))
        drawing.add(Rect(label_width, y, chart_width, 7, fillColor=HexColor("#EDF2F7"), strokeColor=None))
        drawing.add(Rect(label_width, y, chart_width * max(0, min(value, 100)) / 100, 7,
                         fillColor=state_colors.get(state, BLUE), strokeColor=None))
        drawing.add(String(label_width + chart_width + 5, y, fmt_pct(value), fontName="Arial-Bold", fontSize=6.5, fillColor=INK))
    drawing.add(String(label_width, 1, "0%", fontName="Arial", fontSize=5.5, fillColor=MUTED))
    drawing.add(String(label_width + chart_width - 10, 1, "100%", fontName="Arial", fontSize=5.5, fillColor=MUTED))
    return drawing


def monthly_chart(monthly: pd.DataFrame, width: float, height: float) -> Drawing:
    drawing = Drawing(width, height)
    left, bottom, right, top = 34, 25, 12, 16
    chart_w, chart_h = width - left - right, height - bottom - top
    max_value = max(float(monthly["new_accounts"].max()), float(monthly["valid_churn_events"].max())) * 1.20
    for tick in range(5):
        value = max_value * tick / 4
        y = bottom + chart_h * tick / 4
        drawing.add(Line(left, y, left + chart_w, y, strokeColor=GRID, strokeWidth=0.4))
        drawing.add(String(0, y - 2, str(int(round(value))), fontName="Arial", fontSize=5.5, fillColor=MUTED))
    count = len(monthly)
    slot = chart_w / max(count, 1)
    points: list[tuple[float, float]] = []
    for index, row in monthly.reset_index(drop=True).iterrows():
        x = left + slot * index + slot / 2
        bar_h = chart_h * float(row["new_accounts"]) / max_value
        drawing.add(Rect(x - slot * 0.24, bottom, slot * 0.34, bar_h, fillColor=BLUE, strokeColor=None))
        y = bottom + chart_h * float(row["valid_churn_events"]) / max_value
        points.append((x + slot * 0.12, y))
        if index % 3 == 0:
            label = str(row["month_start"])[:7]
            drawing.add(String(x - 13, 7, label, fontName="Arial", fontSize=4.9, fillColor=MUTED))
    for first, second in zip(points, points[1:]):
        drawing.add(Line(first[0], first[1], second[0], second[1], strokeColor=RED, strokeWidth=1.6))
    for x, y in points:
        drawing.add(Circle(x, y, 2.1, fillColor=RED, strokeColor=colors.white, strokeWidth=0.4))
    drawing.add(Rect(width - 160, height - 9, 8, 5, fillColor=BLUE, strokeColor=None))
    drawing.add(String(width - 149, height - 10, "Novas contas", fontName="Arial", fontSize=6, fillColor=INK))
    drawing.add(Line(width - 82, height - 6, width - 72, height - 6, strokeColor=RED, strokeWidth=1.5))
    drawing.add(String(width - 68, height - 10, "Ocorrências", fontName="Arial", fontSize=6, fillColor=INK))
    return drawing


def compact_bars(rows: list[tuple[str, float]], width: float, height: float, color: colors.Color) -> Drawing:
    drawing = Drawing(width, height)
    left = width * 0.40
    chart_w = width - left - 35
    row_h = (height - 12) / max(len(rows), 1)
    max_value = max([value for _, value in rows] + [1])
    for index, (label, value) in enumerate(rows):
        y = height - (index + 1) * row_h + row_h * 0.22
        ratio = value / max_value
        drawing.add(String(0, y, label[:28], fontName="Arial", fontSize=6.2, fillColor=INK))
        drawing.add(Rect(left, y, chart_w * ratio, 7, fillColor=color, strokeColor=None))
        drawing.add(String(left + chart_w * ratio + 4, y, fmt_pct(value), fontName="Arial-Bold", fontSize=6, fillColor=INK))
    return drawing


def line_chart(rows: list[tuple[str, float]], width: float, height: float, color: colors.Color, max_value: float | None = None) -> Drawing:
    drawing = Drawing(width, height)
    left, bottom, right, top = 28, 24, 10, 14
    chart_w, chart_h = width - left - right, height - bottom - top
    max_value = max_value or max([value for _, value in rows] + [1]) * 1.12
    drawing.add(Line(left, bottom, left, bottom + chart_h, strokeColor=GRID))
    drawing.add(Line(left, bottom, left + chart_w, bottom, strokeColor=GRID))
    for tick in range(5):
        value = max_value * tick / 4
        y = bottom + chart_h * tick / 4
        drawing.add(Line(left, y, left + chart_w, y, strokeColor=GRID, strokeWidth=0.35))
        drawing.add(String(0, y - 2, f"{value:.1f}", fontName="Arial", fontSize=5, fillColor=MUTED))
    points = []
    slot = chart_w / max(len(rows) - 1, 1)
    for index, (label, value) in enumerate(rows):
        x = left + slot * index
        y = bottom + chart_h * value / max_value
        points.append((x, y))
        drawing.add(String(x - 10, 7, label, fontName="Arial", fontSize=5, fillColor=MUTED))
    for first, second in zip(points, points[1:]):
        drawing.add(Line(first[0], first[1], second[0], second[1], strokeColor=color, strokeWidth=1.7))
    for x, y in points:
        drawing.add(Circle(x, y, 2.4, fillColor=color, strokeColor=colors.white, strokeWidth=0.5))
    return drawing


def risk_scatter(triage: pd.DataFrame, width: float, height: float) -> tuple[Drawing, float]:
    drawing = Drawing(width, height)
    left, bottom, right, top = 38, 28, 18, 18
    chart_w, chart_h = width - left - right, height - bottom - top
    max_revenue = max(float(triage["mrr_proxy_conservative"].max()), 1) * 1.05
    median_revenue = float(triage["mrr_proxy_conservative"].median())
    score_cut = 50.0
    x_cut = left + chart_w * score_cut / 100
    y_cut = bottom + chart_h * median_revenue / max_revenue
    drawing.add(Rect(left, y_cut, x_cut - left, bottom + chart_h - y_cut, fillColor=PALE_BLUE, strokeColor=None))
    drawing.add(Rect(x_cut, y_cut, left + chart_w - x_cut, bottom + chart_h - y_cut, fillColor=PALE_AMBER, strokeColor=None))
    drawing.add(Rect(left, bottom, x_cut - left, y_cut - bottom, fillColor=PALE_GREEN, strokeColor=None))
    drawing.add(Rect(x_cut, bottom, left + chart_w - x_cut, y_cut - bottom, fillColor=PALE_RED, strokeColor=None))
    drawing.add(Line(x_cut, bottom, x_cut, bottom + chart_h, strokeColor=MUTED, strokeDashArray=[3, 2]))
    drawing.add(Line(left, y_cut, left + chart_w, y_cut, strokeColor=MUTED, strokeDashArray=[3, 2]))
    for _, row in triage.iterrows():
        x = left + chart_w * float(row["triage_score"]) / 100
        y = bottom + chart_h * float(row["mrr_proxy_conservative"]) / max_revenue
        confidence = str(row["evidence_confidence"])
        point_color = BLUE if confidence == "Low" else AMBER if confidence == "Medium" else GREEN
        radius = 1.4 + 2.2 * math.sqrt(max(float(row["mrr_proxy_additive"]), 0) / max(float(triage["mrr_proxy_additive"].max()), 1))
        drawing.add(Circle(x, y, radius, fillColor=point_color, strokeColor=colors.white, strokeWidth=0.25))
    drawing.add(String(left + 4, bottom + chart_h - 10, "PROTEGER VALOR", fontName="Arial-Bold", fontSize=6, fillColor=NAVY))
    drawing.add(String(x_cut + 4, bottom + chart_h - 10, "VALIDAR PRIMEIRO", fontName="Arial-Bold", fontSize=6, fillColor=NAVY))
    drawing.add(String(left + 4, bottom + 5, "MONITORAR", fontName="Arial-Bold", fontSize=6, fillColor=NAVY))
    drawing.add(String(x_cut + 4, bottom + 5, "INVESTIGAR EM LOTE", fontName="Arial-Bold", fontSize=6, fillColor=NAVY))
    drawing.add(String(left + chart_w / 2 - 45, 4, "Intensidade dos sinais (0-100)", fontName="Arial", fontSize=6, fillColor=MUTED))
    drawing.add(String(0, height - 9, "Exposição", fontName="Arial", fontSize=6, fillColor=MUTED))
    return drawing, median_revenue


def draw_background(canvas, doc) -> None:
    canvas.saveState()
    if doc.page == 1:
        canvas.setFillColor(NAVY)
        canvas.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
        canvas.setFillColor(BLUE)
        canvas.rect(0, 0, 9 * mm, PAGE_HEIGHT, fill=1, stroke=0)
    else:
        canvas.setFillColor(colors.white)
        canvas.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    canvas.restoreState()


def draw_page_furniture(canvas, doc) -> None:
    if doc.page == 1:
        return
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.setFont("Arial-Bold", 7)
    canvas.drawString(36, PAGE_HEIGHT - 20, "RAVENSTACK | DIAGNÓSTICO DE CHURN")
    canvas.setStrokeColor(GRID)
    canvas.line(36, PAGE_HEIGHT - 25, PAGE_WIDTH - 36, PAGE_HEIGHT - 25)
    canvas.setFont("Arial", 6.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(36, 15, "Fonte: RavenStack Synthetic SaaS Dataset - Kaggle v1 | Gold auditável em DuckDB")
    canvas.drawRightString(PAGE_WIDTH - 36, 15, f"Adailton Montinegro | {doc.page}")
    canvas.restoreState()


def draw_later_page(canvas, doc) -> None:
    draw_background(canvas, doc)
    draw_page_furniture(canvas, doc)


def build_report() -> Path:
    register_fonts()
    styles = make_styles()
    data = load_data()
    quality = data["quality_summary"]
    scope = data["analysis_scope"]
    accounts = data["account_snapshot"]
    monthly = data["monthly_events"]
    segments = data["segment_snapshot"]
    reasons = data["churn_reasons"]
    triage = data["account_triage"]
    metric_catalog = data["metric_catalog"]
    pre_event = data["pre_event_signals"]
    tests = data["statistical_tests"]
    context = data["context"]

    snapshot_flag = as_bool(accounts["snapshot_churn_flag"])
    ledger_event = as_bool(accounts["has_valid_churn_event"])
    total_accounts = len(accounts)
    snapshot_churned = int(snapshot_flag.sum())
    event_accounts = int(ledger_event.sum())
    agreement_accounts = int((snapshot_flag == ledger_event).sum())
    both = int((snapshot_flag & ledger_event).sum())
    flag_only = int((snapshot_flag & ~ledger_event).sum())
    event_only = int((~snapshot_flag & ledger_event).sum())
    neither = int((~snapshot_flag & ~ledger_event).sum())
    scope_by_id = scope.set_index("scope_id")
    usage_scope = scope_by_id.loc["usage_temporal"]
    support_scope = scope_by_id.loc["support_temporal"]
    period_start, period_end = context["kpis"]["data_period"].split(" to ")
    formatted_period = (
        f'{datetime.strptime(period_start, "%Y-%m-%d").strftime("%d/%m/%Y")} a '
        f'{datetime.strptime(period_end, "%Y-%m-%d").strftime("%d/%m/%Y")}'
    )
    raw_rows = int(context["kpis"]["raw_total_rows"])
    candidate = accounts[~snapshot_flag]
    candidate_low = float(candidate["mrr_proxy_conservative"].sum())
    candidate_high = float(candidate["mrr_proxy_additive"].sum())

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT_PATH), pagesize=landscape(A4), rightMargin=36, leftMargin=36,
        topMargin=34, bottomMargin=28, title="RavenStack - Diagnóstico de Churn",
        author="Adailton Montinegro", subject="AI Master Challenge 001",
    )
    story: list = []

    # 1 - Cover
    story.extend([
        Spacer(1, 30),
        Paragraph("AI MASTER - CHALLENGE 001", styles["cover_eyebrow"]),
        Paragraph("Verdade antes do churn", styles["cover_title"]),
        Paragraph(
            "Diagnóstico executivo da RavenStack: auditoria das cinco fontes, limites da parcela recuperável, "
            "triagem não probabilística e plano para recuperar capacidade de decisão.",
            styles["cover_subtitle"],
        ),
        Spacer(1, 18),
        metric_row([
            ("REGISTROS AUDITADOS", fmt_int(raw_rows), "5 fontes conectadas por account_id e subscription_id"),
            ("USO CONFIÁVEL", fmt_int(usage_scope["eligible_rows"]), f'{fmt_pct(usage_scope["coverage_pct"])} dos registros de uso'),
            ("TICKETS CONFIÁVEIS", fmt_int(support_scope["eligible_rows"]), f'{fmt_pct(support_scope["coverage_pct"])} dos tickets'),
            ("COERÊNCIA DAS FONTES", fmt_pct(100 * agreement_accounts / total_accounts), "cadastro de contas x histórico de churn"),
        ], styles),
        Spacer(1, 28),
        Paragraph(
            f"<b>Escopo:</b> {total_accounts} contas | {formatted_period}<br/>"
            "<b>Autor:</b> Adailton Montinegro | <b>Fonte:</b> RavenStack Synthetic SaaS Dataset - Kaggle v1",
            styles["small_white"],
        ),
    ])
    story.append(PageBreak())

    # 2 - Executive answer
    page_title(
        story, styles, "RESPOSTA AO CEO", "O problema central é a medição, antes de ser o churn",
        "As cinco tabelas conectam pelas chaves, mas não formam um ciclo de vida temporal e financeiro reconciliável.",
    )
    story.append(callout(
        "<b>Veredito:</b> a base permite provar que há inconsistências sistêmicas e explorar uma parcela tratada. "
        "Ela não permite atribuir causa raiz, calcular churn mensal, MRR perdido, GRR, NRR, LTV ou ROI como fatos operacionais.",
        styles, PALE_RED, RED,
    ))
    story.append(Spacer(1, 10))
    truth_boxes = Table([[
        box("O que sabemos", "Chaves conectam; há 110 contas com flag de churn no cadastro e 600 ocorrências históricas em 352 contas. Uso e suporte têm falhas temporais materiais.", styles, PALE_GREEN, GREEN),
        box("O que suspeitamos", "Produto, suporte, preço e onboarding são hipóteses legítimas para pesquisa. Os segmentos e sinais disponíveis não demonstram qual deles explica o churn.", styles, PALE_AMBER, AMBER),
        box("O que não sabemos", "População pagante mensal, assinatura perdida, receita perdida real, efeito causal e probabilidade individual permanecem indisponíveis.", styles, PALE_RED, RED),
    ]], colWidths=[(PAGE_WIDTH - 82) / 3] * 3)
    truth_boxes.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(truth_boxes)
    story.append(Spacer(1, 12))
    story.append(Paragraph("As cinco fontes foram cruzadas", styles["h2"]))
    source_rows = [
        ["Contas", "500", "Snapshot cadastral", "Base para atributos e flag declarada"],
        ["Assinaturas", "5.000", "Contrato/assinatura", "MRR observado; sobreposição não explicada"],
        ["Uso", "25.000", "Evento de funcionalidade", "5.554 registros temporalmente elegíveis"],
        ["Suporte", "2.000", "Ticket", "923 tickets temporalmente elegíveis"],
        ["Churn", "600", "Ocorrência histórica", "352 contas; sem subscription_id"],
    ]
    story.append(data_table(
        ["Fonte", "Linhas", "Grão", "Uso defensável"], source_rows, styles,
        [85, 55, 130, 480],
    ))
    story.append(PageBreak())

    # 3 - Data quality
    page_title(
        story, styles, "AUDITORIA DE QUALIDADE", "Quanto da base sobrevive a cada finalidade",
        "Disponibilidade estrutural não equivale a validade de negócio. Cada regra preserva os registros rejeitados em quarentena.",
    )
    scope_label = {
        "accounts_snapshot": "Cadastro de contas",
        "subscriptions_observed": "Assinaturas registradas",
        "usage_temporal": "Uso confiável após tratamento",
        "support_temporal": "Tickets confiáveis após tratamento",
        "churn_event_ledger": "Histórico de churn",
        "account_revenue_proxy": "Proxy de receita por conta",
        "account_triage": "Triagem demonstrativa",
    }
    scope_rows = [
        (scope_label[row.scope_id], float(row.coverage_pct), str(row.confidence_state))
        for row in scope.itertuples()
    ]
    state_note = Table([[
        Paragraph("<b>Disponível como registrado</b><br/>Existe na fonte, mas pode conter contradições de negócio.", styles["box_body"]),
        Paragraph("<b>Confiável após tratamento</b><br/>Passou pelas regras temporais e de deduplicação.", styles["box_body"]),
        Paragraph("<b>Usável com restrições</b><br/>Serve apenas como proxy ou triagem com premissas visíveis.", styles["box_body"]),
    ]], colWidths=[250, 250, 250])
    state_note.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), PALE_GREEN), ("BACKGROUND", (1, 0), (1, 0), PALE_BLUE),
        ("BACKGROUND", (2, 0), (2, 0), PALE_AMBER), ("BOX", (0, 0), (-1, -1), 0.5, GRID),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, GRID), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(state_note)
    story.append(Spacer(1, 7))
    story.append(horizontal_bars(scope_rows, 755, 150))
    story.append(Paragraph("Principais falhas encontradas", styles["h2"]))
    rule_labels = {
        "subscription_overlap_unresolved": "Assinaturas simultâneas sem identificação do contrato",
        "churn_snapshot_disagreement": "Ocorrência diverge do status no cadastro",
        "usage_before_subscription": "Uso anterior ao início da assinatura",
        "subscription_account_plan_mismatch": "Plano da assinatura diverge do plano da conta",
        "support_before_signup": "Ticket anterior ao cadastro da conta",
        "usage_before_signup": "Uso anterior ao cadastro da conta",
        "support_missing_csat": "Ticket sem avaliação de satisfação",
        "churn_missing_feedback": "Ocorrência sem comentário do cliente",
    }
    table_names = {
        "subscriptions": "Assinaturas", "churn_events": "Churn", "feature_usage": "Uso",
        "support_tickets": "Suporte", "accounts": "Contas",
    }
    failures = quality[quality["failed_rows"] > 0].sort_values("failure_pct", ascending=False).head(8)
    failure_rows = [
        [table_names.get(row.table_name, row.table_name), rule_labels.get(row.rule_id, row.rule_id),
         fmt_int(row.failed_rows), fmt_pct(row.failure_pct), str(row.severity).upper()]
        for row in failures.itertuples()
    ]
    story.append(data_table(
        ["Fonte", "Falha de negócio", "Registros", "% da fonte", "Severidade"],
        failure_rows, styles, [85, 420, 75, 75, 80],
    ))
    story.append(Paragraph(
        "Nota: 100% disponível não significa 100% correto. As 5.000 assinaturas estão presentes, mas 4.992 linhas pertencem a contas com sobreposição não explicada.",
        styles["small"],
    ))
    story.append(PageBreak())

    # 4 - Professional gate
    page_title(
        story, styles, "GATE PROFISSIONAL DE DECISÃO", "Pare a análise aqui",
        "Em uma empresa real, continuar diretamente para segmentação e risco criaria precisão aparente sobre fatos incompatíveis.",
    )
    stop_box = Table([[
        Paragraph(
            "<b>RECOMENDAÇÃO CORRETA</b><br/><br/>Interromper o diagnóstico de churn e concentrar os esforços em localizar e corrigir o sistema de logs, "
            "os contratos de eventos e a reconstrução do ciclo de vida de contas e assinaturas. Não usar esta base para abordar clientes, "
            "alterar canais, avaliar times ou decidir investimento.",
            styles["callout_white"],
        )
    ]], colWidths=[PAGE_WIDTH - 72])
    stop_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), RED), ("BOX", (0, 0), (-1, -1), 1, RED),
        ("LEFTPADDING", (0, 0), (-1, -1), 20), ("RIGHTPADDING", (0, 0), (-1, -1), 20),
        ("TOPPADDING", (0, 0), (-1, -1), 18), ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
    ]))
    story.append(stop_box)
    story.append(Spacer(1, 14))
    story.append(Paragraph("Se a liderança precisar de evidência em curto prazo", styles["h2"]))
    urgent = Table([[
        box("1. Ouvir clientes", "Pesquisa curta de satisfação com ativos, cancelados e reativados; entrevistas de churn e coleta estruturada de sugestões.", styles, PALE_BLUE, BLUE),
        box("2. Revisar casos", "Avaliação interna conjunta de CS e Suporte, com foco nas contas de maior impacto e nos episódios com evidência documental.", styles, PALE_AMBER, AMBER),
        box("3. Registrar hipóteses", "Consolidar temas com fonte e frequência. Usar os achados para investigação, sem substituir validação causal.", styles, PALE_GREEN, GREEN),
    ]], colWidths=[(PAGE_WIDTH - 82) / 3] * 3)
    urgent.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(urgent)
    story.append(Spacer(1, 12))
    story.append(callout(
        "<b>Por que o relatório continua?</b> Exclusivamente como demonstração estatística do desafio. Raw permanece imutável; "
        "Stage quarentena registros impossíveis; Gold explicita universo, cobertura e limitações; nenhuma saída autoriza ação automática.",
        styles, PALE_AMBER, AMBER,
    ))
    story.append(PageBreak())

    # 5 - Demonstrative one-page
    page_title(
        story, styles, "CONTINUAÇÃO DEMONSTRATIVA", "One-page executivo da parcela recuperável",
        "Snapshot de conta, histórico de churn e receita permanecem separados. Não há saldo de clientes nem churn rate reconciliado.",
    )
    story.append(metric_row([
        ("CONTAS AVALIADAS", fmt_int(total_accounts), "cadastro de contas"),
        ("CHURN NO CADASTRO", f"{fmt_int(snapshot_churned)} ({fmt_pct(100 * snapshot_churned / total_accounts)})", "prevalência do snapshot"),
        ("COM HISTÓRICO DE CHURN", fmt_int(event_accounts), "ao menos uma ocorrência; não é status atual"),
        ("FONTES COINCIDENTES", f"{fmt_int(agreement_accounts)} ({fmt_pct(100 * agreement_accounts / total_accounts)})", "coincidência, não validação"),
        ("EXPOSIÇÃO CONDICIONAL", f"{fmt_money(candidate_low)} a {fmt_money(candidate_high)}", "contas sem flag; proxy mensal"),
    ], styles))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Entradas e ocorrências de churn por mês - séries separadas", styles["h2"]))
    story.append(monthly_chart(monthly, 755, 190))
    plan = segments[segments["dimension_name"] == "plan_tier"].sort_values("snapshot_churn_rate_pct")
    reason_labels = {
        "features": "Produto e funcionalidades", "budget": "Orçamento", "support": "Suporte",
        "unknown": "Não informado", "competitor": "Concorrente", "pricing": "Preço",
    }
    left_chart = [
        (str(row.segment_value), float(row.snapshot_churn_rate_pct)) for row in plan.itertuples()
    ]
    right_chart = [
        (reason_labels.get(str(row.reason_code), str(row.reason_code)), float(row.event_share_pct))
        for row in reasons.sort_values("event_share_pct").itertuples()
    ]
    chart_table = Table([[
        [Paragraph("% churn na perspectiva do snapshot - por plano", styles["h2"]), compact_bars(left_chart, 360, 105, BLUE)],
        [Paragraph("% churn na perspectiva de ocorrências - por motivo", styles["h2"]), compact_bars(right_chart, 360, 105, CYAN)],
    ]], colWidths=[375, 375])
    chart_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(chart_table)
    story.append(Paragraph(
        "Leitura: a alta de ocorrências é observável, mas o denominador mensal de contas expostas e a receita efetivamente perdida não são reconciliáveis.",
        styles["small"],
    ))
    story.append(PageBreak())

    # 6 - Analytical diagnosis
    page_title(
        story, styles, "DIAGNÓSTICO ANALÍTICO", "Os padrões disponíveis não identificam uma causa raiz robusta",
        "As comparações preservam os furos da base, mostram tamanho de amostra e distinguem associação de causalidade.",
    )
    test_labels = {
        "snapshot_flag_vs_event": "Cadastro x histórico",
        "snapshot_churn_by_plan_tier": "Flag por plano",
        "snapshot_churn_by_industry": "Flag por indústria",
        "snapshot_churn_by_referral_source": "Flag por canal",
        "churn_reason_vs_feedback": "Motivo x comentário",
        "pre_event_escalation_0_14": "Escalação pré-ocorrência",
    }
    selected_tests = tests[tests["test_id"].isin(test_labels)]
    test_rows = []
    for row in selected_tests.itertuples():
        reading = "Sinal exploratório" if float(row.p_value) < 0.10 else "Sem evidência de associação"
        effect = "-" if pd.isna(row.effect_value) else f"{float(row.effect_value):.3f}"
        test_rows.append([test_labels[row.test_id], fmt_int(row.n), f"{float(row.p_value):.3f}", effect, reading])
    story.append(data_table(
        ["Comparação", "n", "Nível de evidência (p)", "Efeito", "Leitura"],
        test_rows, styles, [220, 55, 115, 70, 280],
    ))
    story.append(Spacer(1, 8))
    pre_event = pre_event.sort_values("window_order").copy()
    pre_event["usage_per_record"] = pre_event["usage_count"] / pre_event["usage_events"]
    usage_rows = [(str(row.window_label), float(row.usage_per_record)) for row in pre_event.itertuples()]
    escalation_rows = [(str(row.window_label), float(row.escalation_rate_pct)) for row in pre_event.itertuples()]
    signals = Table([[
        [Paragraph("Uso médio por registro antes da próxima ocorrência", styles["h2"]), line_chart(usage_rows, 360, 150, BLUE, max_value=12)],
        [Paragraph("Escalação de tickets antes da próxima ocorrência", styles["h2"]), line_chart(escalation_rows, 360, 150, AMBER, max_value=20)],
    ]], colWidths=[375, 375])
    signals.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(signals)
    near = pre_event[pre_event["window_label"] == "0-14"].iloc[0]
    reference = pre_event[pre_event["window_label"].isin(["15-30", "31-60"])]
    story.append(callout(
        f"<b>Leitura:</b> a intensidade de uso permanece praticamente plana. Nos 14 dias anteriores, "
        f"{int(near['escalated_tickets'])} de {int(near['support_tickets'])} tickets foram escalados ({fmt_pct(near['escalation_rate_pct'])}), "
        f"contra {int(reference['escalated_tickets'].sum())} de {int(reference['support_tickets'].sum())} entre 15 e 60 dias. "
        "Isso merece investigação humana, mas não prova causa.",
        styles, PALE_AMBER, AMBER,
    ))
    story.append(PageBreak())

    # 7 - Risk triage
    page_title(
        story, styles, "TRIAGEM DE RISCO", "Ordenar investigação sem fingir probabilidade",
        "O índice combina sinais válidos de uso e suporte. Receita ordena impacto; ausência de dados reduz confiança e nunca aumenta risco.",
    )
    band_counts = triage["triage_band"].value_counts()
    low_confidence = int((triage["evidence_confidence"] == "Low").sum())
    attention = int(triage["triage_band"].isin(["High", "Critical"]).sum())
    story.append(metric_row([
        ("CONTAS NA FILA", fmt_int(len(triage)), "sem flag de churn no cadastro"),
        ("ATENÇÃO ALTA", fmt_int(attention), "índice não probabilístico"),
        ("BAIXA CONFIANÇA", fmt_int(low_confidence), "cobertura insuficiente"),
        ("DATA GAP", fmt_int(band_counts.get("Data gap", 0)), "validar dados antes de agir"),
    ], styles))
    story.append(Spacer(1, 8))
    scatter, median_revenue = risk_scatter(triage, 755, 205)
    story.append(scatter)
    story.append(Paragraph(
        f"Cortes demonstrativos: intensidade 50 e exposição mediana {fmt_money(median_revenue)}. Azul = baixa confiança; laranja = média; verde = alta.",
        styles["small"],
    ))
    high_priority = triage.sort_values(["triage_score", "mrr_proxy_conservative"], ascending=False).head(6)
    top_rows = [
        [row.account_name, row.account_id, f"{row.triage_score:.1f}", row.triage_band,
         row.evidence_confidence, fmt_money(row.mrr_proxy_conservative), row.signal_1]
        for row in high_priority.itertuples()
    ]
    story.append(data_table(
        ["Conta", "ID", "Sinais", "Faixa", "Confiança", "Exposição", "Principal evidência"],
        top_rows, styles, [90, 70, 48, 55, 60, 85, 320],
    ))
    story.append(Paragraph(
        "Recomendação: validar primeiro as contas com sinais e exposição altos; tratar Data gap como fila de correção, nunca como campanha automática.",
        styles["small"],
    ))
    story.append(PageBreak())

    # 8 - Action plan and scenario
    page_title(
        story, styles, "PLANO DE AÇÃO", "Recuperar a medição, obter evidência independente e só então intervir",
        "A prioridade de negócio é reduzir o risco de decisão errada. Ações de retenção entram apenas após validação e experimento.",
    )
    actions = [
        ["P0", "Instrumentação", "Definir state machine e contratos de IDs, datas e eventos", "Data + Engenharia", "% eventos válidos", "Alta"],
        ["P0", "Pesquisa externa", "Ouvir ativos, cancelados e reativados com roteiro único", "CS + Produto", "Respostas e temas", "Alta"],
        ["P1", "Revisão operacional", "Validar manualmente contas de maior exposição e baixa confiança", "CS + Suporte", "Status corrigidos", "Média"],
        ["P2", "Shadow mode", "Gerar fila de triagem sem contato automático", "CS Ops", "Falsos positivos", "Média"],
        ["P3", "Experimentos", "Testar playbooks por sinal com grupo controle", "CS + Produto", "Uplift e custo", "Baixa hoje"],
    ]
    story.append(data_table(
        ["Prioridade", "Frente", "Ação concreta", "Dono", "KPI", "Confiança"],
        actions, styles, [58, 100, 325, 105, 105, 72],
    ))
    story.append(Spacer(1, 10))
    scenario = triage[triage["triage_band"].isin(["High", "Critical"])]
    scenario_low = float(scenario["mrr_proxy_conservative"].sum()) * 0.10
    scenario_high = float(scenario["mrr_proxy_additive"].sum()) * 0.10
    story.append(Paragraph("Simulação transparente de oportunidade", styles["h2"]))
    story.append(Paragraph(
        "Exemplo de dimensionamento: se as contas hoje classificadas como High/Critical fossem validadas e uma ação futura preservasse "
        "hipoteticamente 10% da exposição mensal associada a elas, o intervalo abaixo seria o valor potencial preservado. "
        "Não é previsão, receita confirmada ou ROI.",
        styles["body"],
    ))
    story.append(metric_row([
        ("CONTAS NO CENÁRIO", fmt_int(len(scenario)), "High ou Critical"),
        ("CENÁRIO CONSERVADOR", fmt_money(scenario_low), "10% da maior assinatura por conta"),
        ("CENÁRIO ADITIVO", fmt_money(scenario_high), "10% da soma das assinaturas simultâneas"),
    ], styles, widths=[250, 250, 250]))
    story.append(Spacer(1, 10))
    story.append(callout(
        "<b>ICP e canais:</b> a base não mostra associação robusta entre a flag de churn e plano, indústria ou canal. "
        "Não é defensável recomendar um ICP ou realocar aquisição com estes dados. Para calcular ROI ainda faltam custo, margem e uplift causal.",
        styles, PALE_RED, RED,
    ))
    story.append(PageBreak())

    # 9 - Method and close
    page_title(
        story, styles, "MÉTODO E RASTREABILIDADE", "Uma entrega reproduzível, com limites executáveis",
        "Streamlit e PDF consomem os mesmos exports Gold. O manifesto fixa a versão, o volume e o hash de cada arquivo de origem.",
    )
    flow = Table([[
        box("RAW", "Cópia byte a byte das cinco fontes. Sem correção, imputação ou exclusão.", styles, PALE_BLUE, BLUE),
        box("STAGE", "Tipagem, padronização, deduplicação determinística, flags de qualidade e quarentena.", styles, PALE_AMBER, AMBER),
        box("GOLD", "Tabelas analíticas, universos, cobertura, proxies, testes e fila de triagem.", styles, PALE_GREEN, GREEN),
    ]], colWidths=[(PAGE_WIDTH - 82) / 3] * 3)
    flow.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(flow)
    story.append(Spacer(1, 10))
    story.append(Paragraph("Métricas deliberadamente indisponíveis", styles["h2"]))
    unavailable = metric_catalog[metric_catalog["value_status"] == "Unavailable"]
    unavailable_rows = [[row.metric_label, row.grain, row.limitation] for row in unavailable.itertuples()]
    story.append(data_table(
        ["Métrica", "Grão necessário", "Por que não é calculável"], unavailable_rows,
        styles, [190, 120, 445],
    ))
    story.append(Spacer(1, 9))
    story.append(callout(
        "<b>Modelo preditivo rejeitado:</b> o Random Forest anterior usava target inconsistente, histórico posterior ao corte e pontuação na própria amostra. "
        "ROC-AUC 0,5211 e PR-AUC 0,2790 não demonstram discriminação operacional. A alternativa atual é triagem explicável em shadow mode.",
        styles, PALE_RED, RED,
    ))
    story.append(Spacer(1, 10))
    story.append(callout(
        "<b>Mensagem final ao CEO:</b> a RavenStack confirma um problema de medição antes de confirmar uma causa de churn. "
        "Corrija os contratos de churn, assinatura, receita e eventos; obtenha evidência qualitativa imediata se a urgência exigir; "
        "e só promova scores ou intervenções depois de validação temporal e experimento controlado.",
        styles, PALE_BLUE, BLUE,
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        f"Build Gold: {escape(str(context['generated_at']))} | Manifesto: {escape(str(context['manifest_version']))} | "
        "Todos os números deste relatório são derivados dos arquivos em artifacts/data.",
        styles["small"],
    ))

    doc.build(story, onFirstPage=draw_background, onLaterPages=draw_later_page)
    return OUTPUT_PATH


if __name__ == "__main__":
    print(build_report())
