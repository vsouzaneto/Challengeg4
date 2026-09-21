"""Relatório de saúde dos dados: tudo que o scoring assume, verificado com número.

Gera um Markdown com contagens, nulos, chaves órfãs, inconsistências de data e
distribuições básicas. É a etapa 0 do método: nenhum fator é definido antes deste
relatório existir.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

from .data import CLOSED_STAGES, OPEN_STAGES, Tables, enrich, reference_date


def _pct(n: int, d: int) -> str:
    return f"{(100.0 * n / d):.1f}%" if d else "n/a"


def file_manifest(raw_dir: Path) -> list[dict]:
    """Nome, bytes, linhas e SHA-256 de cada CSV usado: a procedência dos dados fica no relatório."""
    out = []
    for name in ("accounts.csv", "products.csv", "sales_teams.csv", "sales_pipeline.csv"):
        path = Path(raw_dir) / name
        if not path.exists():
            continue
        h = hashlib.sha256(path.read_bytes()).hexdigest()
        lines = sum(1 for _ in path.open("rb")) - 1
        out.append({"file": name, "bytes": path.stat().st_size, "rows": lines, "sha256": h})
    return out


def audit(tables: Tables, raw_dir: Path | None = None) -> tuple[str, dict]:
    """Retorna (markdown, métricas) para que testes e docs usem os mesmos números."""
    p = tables.pipeline
    m: dict = {}
    lines: list[str] = ["# Relatório de saúde dos dados", ""]
    if raw_dir is not None:
        m["manifest"] = file_manifest(raw_dir)
        lines += ["## Arquivos usados (procedência)", "", "| Arquivo | Bytes | Linhas | SHA-256 |", "|---|---:|---:|---|"]
        lines += [f"| {f['file']} | {f['bytes']:,} | {f['rows']:,} | `{f['sha256']}` |" for f in m["manifest"]]
        lines.append("")

    lines += ["## Tamanho das tabelas", "", "| Tabela | Linhas | Colunas |", "|---|---:|---:|"]
    for name, df in (("accounts", tables.accounts), ("products", tables.products),
                     ("sales_teams", tables.teams), ("sales_pipeline", p)):
        lines.append(f"| {name} | {len(df):,} | {df.shape[1]} |")
        m[f"rows_{name}"] = len(df)

    lines += ["", "## Estágios do pipeline", "", "| Estágio | Deals | % |", "|---|---:|---:|"]
    stage_counts = p["deal_stage"].value_counts()
    for stage, n in stage_counts.items():
        lines.append(f"| {stage} | {n:,} | {_pct(n, len(p))} |")
        m[f"stage_{stage}"] = int(n)
    unknown = sorted(set(stage_counts.index) - set(OPEN_STAGES) - set(CLOSED_STAGES))
    m["unknown_stages"] = unknown
    if unknown:
        lines.append(f"\nEstágios fora do esperado: {unknown}")

    lines += ["", "## Nulos por coluna do pipeline", "", "| Coluna | Nulos | % |", "|---|---:|---:|"]
    for col in p.columns:
        n = int(p[col].isna().sum())
        m[f"null_{col}"] = n
        lines.append(f"| {col} | {n:,} | {_pct(n, len(p))} |")

    lines += ["", "## Nulos por estágio (o que falta em cada fase)", ""]
    by_stage = p.groupby("deal_stage")[["account", "engage_date", "close_date", "close_value"]].apply(lambda g: g.isna().mean() * 100).round(1)
    lines.append(by_stage.to_markdown())
    for stage in by_stage.index:
        for col in by_stage.columns:
            m[f"nullpct_{stage}_{col}"] = float(by_stage.loc[stage, col])

    e = enrich(tables)
    lines += ["", "## Integridade das chaves (após normalização de produto)", ""]
    orphan_product = e.loc[e["sales_price"].isna(), "product"].value_counts()
    orphan_agent = e.loc[e["manager"].isna(), "sales_agent"].value_counts()
    orphan_account = int((e["account"].notna() & e["sector"].isna()).sum())
    m["orphan_product_rows"] = int(orphan_product.sum())
    m["orphan_agent_rows"] = int(orphan_agent.sum())
    m["orphan_account_rows"] = orphan_account
    m["rows_without_account"] = int(e["account"].isna().sum())
    m["open_rows_without_account"] = int((e["is_open"] & e["account"].isna()).sum())
    lines += [f"- Produtos do pipeline sem correspondência no catálogo: {m['orphan_product_rows']:,} linhas {dict(orphan_product)}",
              f"- Vendedores do pipeline sem correspondência em sales_teams: {m['orphan_agent_rows']:,} linhas {dict(orphan_agent)}",
              f"- Contas do pipeline sem correspondência em accounts: {orphan_account:,} linhas",
              f"- Oportunidades sem conta (campo vazio): {m['rows_without_account']:,} ({_pct(m['rows_without_account'], len(e))}); entre abertas: {m['open_rows_without_account']:,} ({_pct(m['open_rows_without_account'], int(e['is_open'].sum()))})"]

    raw_names = tables.pipeline["product"].unique()
    m["product_names_pipeline"] = sorted(map(str, raw_names))
    m["product_names_catalog"] = sorted(map(str, tables.products["product"].unique()))

    lines += ["", "## Datas", ""]
    ref = reference_date(p)
    m["reference_date"] = str(ref.date())
    closed = p[p["deal_stage"].isin(CLOSED_STAGES)]
    cycle = (closed["close_date"] - closed["engage_date"]).dt.days
    m["cycle_negative"] = int((cycle < 0).sum())
    m["cycle_median_days"] = float(cycle.median())
    m["engage_min"] = str(p["engage_date"].min().date()) if p["engage_date"].notna().any() else None
    m["engage_max"] = str(p["engage_date"].max().date()) if p["engage_date"].notna().any() else None
    m["close_min"] = str(closed["close_date"].min().date())
    m["close_max"] = str(closed["close_date"].max().date())
    m["open_with_close_date"] = int((p["deal_stage"].isin(OPEN_STAGES) & p["close_date"].notna()).sum())
    m["open_with_close_value"] = int((p["deal_stage"].isin(OPEN_STAGES) & p["close_value"].fillna(0).gt(0)).sum())
    m["lost_with_value"] = int(((p["deal_stage"] == "Lost") & p["close_value"].fillna(0).gt(0)).sum())
    m["won_zero_value"] = int(((p["deal_stage"] == "Won") & p["close_value"].fillna(0).le(0)).sum())
    lines += [f"- Data de referência (max close_date dos fechados): **{m['reference_date']}**",
              f"- engage_date: {m['engage_min']} → {m['engage_max']}; close_date: {m['close_min']} → {m['close_max']}",
              f"- Ciclo (close − engage) dos fechados: mediana {m['cycle_median_days']:.0f} dias; negativos: {m['cycle_negative']:,}",
              f"- Deals abertos com close_date preenchida: {m['open_with_close_date']:,}; com close_value > 0: {m['open_with_close_value']:,}",
              f"- Lost com close_value > 0: {m['lost_with_value']:,}; Won com close_value ≤ 0 ou vazio: {m['won_zero_value']:,}"]

    open_eng = e[(e["deal_stage"] == "Engaging") & e["engage_date"].notna()]
    age = (ref - open_eng["engage_date"]).dt.days
    if not age.empty:
        q = age.quantile([0.25, 0.5, 0.75, 0.9]).round(0)
        m["engaging_age_q"] = {str(k): float(v) for k, v in q.items()}
        m["engaging_age_over_cycle_median"] = int((age > m["cycle_median_days"]).sum())
        lines += ["", "## Idade dos deals em Engaging na data de referência", "",
                  f"- Quartis (dias): P25={q[0.25]:.0f}, P50={q[0.5]:.0f}, P75={q[0.75]:.0f}, P90={q[0.9]:.0f}",
                  f"- Engaging mais velhos que a mediana do ciclo dos fechados ({m['cycle_median_days']:.0f} d): {m['engaging_age_over_cycle_median']:,} de {len(age):,}"]

    lines += ["", "## Win rate global e por dimensão (apenas fechados: Won / (Won + Lost))", ""]
    won = closed["deal_stage"].eq("Won")
    m["win_rate_global"] = float(won.mean())
    lines.append(f"- Global: {m['win_rate_global']:.1%} em {len(closed):,} deals fechados")
    ce = e[e["is_closed"]].assign(won=lambda d: d["deal_stage"].eq("Won"))
    for dim in ("product", "sector", "regional_office", "manager", "sales_agent"):
        g = ce.groupby(dim)["won"].agg(["mean", "size"]).sort_values("mean")
        if len(g) == 0:
            continue
        spread = float(g["mean"].max() - g["mean"].min())
        m[f"wr_spread_{dim}"] = spread
        m[f"wr_n_{dim}"] = int(len(g))
        lines.append(f"- {dim}: {len(g)} grupos, win rate de {g['mean'].min():.1%} a {g['mean'].max():.1%} (spread {spread:.1%}), menor grupo n={int(g['size'].min())}")

    lines += ["", "## Valor", ""]
    wv = closed.loc[closed["deal_stage"] == "Won", "close_value"]
    m["won_value_median"] = float(wv.median())
    m["won_value_p90"] = float(wv.quantile(0.9))
    m["won_value_max"] = float(wv.max())
    lines.append(f"- close_value dos Won: mediana {m['won_value_median']:,.0f}, P90 {m['won_value_p90']:,.0f}, máximo {m['won_value_max']:,.0f}")
    price = tables.products.set_index("product")["sales_price"]
    m["price_ratio_max_min"] = float(price.max() / price.min()) if price.min() else None
    lines.append(f"- sales_price do catálogo: de {price.min():,.0f} a {price.max():,.0f} (razão {m['price_ratio_max_min']:.0f}x)")

    return "\n".join(lines) + "\n", m


def write_report(tables: Tables, out_path: Path | str, raw_dir: Path | None = None) -> dict:
    md, metrics = audit(tables, raw_dir)
    Path(out_path).write_text(md, encoding="utf-8")
    return metrics
