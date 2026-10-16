"""Gera bundle JSON para Command Center React."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from analytics.account_investigation import build_investigation_index
from analytics.columns import EXPORT_RENAME, to_export_frame
from analytics.paths import DASH_PUBLIC, OUT


def _records(df: pd.DataFrame) -> list[dict]:
    out = df.replace({np.nan: None}).copy()
    for col in out.select_dtypes(include=["bool"]).columns:
        out[col] = out[col].astype(bool)
    return json.loads(out.to_json(orient="records", date_format="iso"))


def export_dashboard_bundle(
    acc: pd.DataFrame,
    summary: dict,
    tables: dict | None = None,
    qualidade_dados: dict | None = None,
) -> Path:
    DASH_PUBLIC.mkdir(parents=True, exist_ok=True)
    export = to_export_frame(acc)
    usage = pd.read_csv(OUT / "usage_by_industry_month.csv")
    segments = pd.read_csv(OUT / "segment_net_churn.csv")

    months = sorted(usage["month"].astype(str).unique().tolist())
    med_esc = float(acc["escalation_rate"].median()) if "escalation_rate" in acc else 0.0
    revolving = int(acc["revolving_active"].sum())
    mrr_rev = float(acc.loc[acc["revolving_active"], "mrr_amount"].sum())

    bundle = {
        "meta": {
            "produto": "RavenStack Intelligence",
            "versao": "3.0",
            "autor": "Felipe de Lima Santiago",
            "slug": "felipe",
            "design_ref": "G4 Gestão e Estratégia",
            "gerado_utc": summary.get("generated_at"),
        },
        "narrativa_executiva": {
            "headline": "O churn subiu nos eventos, não necessariamente na retenção líquida.",
            "bullets": [
                f"{revolving} contas ativas já cancelaram antes (US$ {mrr_rev:,.0f} MRR em revolving).",
                "Uso médio e CSAT não separam quem sai. Olhe status, escalação e segmento.",
                "DevTools e canal Event concentram pior churn líquido.",
            ],
        },
        "kpis_globais": {
            "contas": summary["accounts"],
            "churn_liquido": summary["net_churned"],
            "eventos_churn": summary["churn_events_total"],
            "revolving": summary["revolving_active"],
            "mrr_revolving_usd": summary["mrr_revolving"],
            "mrr_perdido_usd": summary["mrr_lost"],
            "auc_modelo": summary["model_auc"],
            "mediana_taxa_escalacao": med_esc,
        },
        "contas": _records(export),
        "uso_mensal_por_industria": _records(usage),
        "segmentos": _records(segments),
        "filtros_disponiveis": {
            "status_conta": sorted(export["status_conta"].dropna().unique().tolist()),
            "industria": sorted(export["industria"].dropna().unique().tolist()),
            "canal_aquisicao": sorted(export["canal_aquisicao"].dropna().unique().tolist()),
            "plano_atual": sorted(export["plano_atual"].dropna().unique().tolist()),
            "faixa_risco": sorted(
                [x for x in export["faixa_risco"].dropna().unique().tolist()],
                key=lambda x: str(x),
            ),
            "em_trial": ["Sim", "Não"],
            "periodo_meses": months,
            "periodo_min": months[0] if months else "",
            "periodo_max": months[-1] if months else "",
        },
        "colunas_glossario": {v: k for k, v in EXPORT_RENAME.items()},
    }

    rec_path = OUT / "recommendations_impact.csv"
    if rec_path.exists():
        top = pd.read_csv(rec_path).iloc[0]
        bundle["recomendacao_destaque"] = {
            "acao": str(top["acao"]),
            "impacto_mrr_usd": float(top["impacto_mrr_usd"]),
            "impacto_anual_arr_usd": float(top["impacto_anual_arr_usd"]),
            "confianca": str(top["confianca"]),
        }

    if qualidade_dados:
        bundle["qualidade_dados"] = qualidade_dados

    if tables is not None:
        bundle["investigacoes"] = build_investigation_index(tables, acc)

    path = DASH_PUBLIC / "bundle.json"
    path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "dashboard_bundle.json").write_text(
        json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return path
