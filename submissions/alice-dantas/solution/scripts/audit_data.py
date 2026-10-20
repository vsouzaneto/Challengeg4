#!/usr/bin/env python3
"""Auditoria reproduzivel dos dados do Challenge 003 (Lead Scorer).

Le os CSVs em solution/data/raw/ (somente leitura), calcula as verificacoes do
plano de validacao do discovery (V1..V14) e grava:

  solution/data/processed/audit_results.json   resultados estruturados
  solution/data/processed/audit_log.txt        mesmo texto impresso no terminal

Nao implementa scoring nem escolhe arquitetura. Os modelos da secao 16 sao
sondas de viabilidade (o que um baseline simples alcanca), nao candidatos.

Uso (a partir de solution/):
  .venv/bin/python scripts/audit_data.py
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import brier_score_loss, log_loss
    HAS_SKLEARN = True
except Exception:  # pragma: no cover - ambiente sem sklearn
    HAS_SKLEARN = False

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"

TABLES = ["accounts", "products", "sales_teams", "sales_pipeline", "metadata"]
SENTINELS = {"na", "n/a", "null", "none", "nan", "unknown", "-", "?", "#n/a", "undefined", "missing"}
OPEN_STAGES = ["Prospecting", "Engaging"]
CLOSED_STAGES = ["Won", "Lost"]
SEED = 20260101
MIN_CELL = 30  # amostra minima por celula para interpretar uma taxa
BACKTEST_CUTS = ["2017-05-31", "2017-06-30", "2017-07-31", "2017-08-31", "2017-09-30"]
SMOOTH_M = 20  # forca do encolhimento para a taxa global nos baselines por categoria

LOG: list[str] = []
R: dict = {}  # resultados estruturados


# ----------------------------------------------------------------------------
# utilidades
# ----------------------------------------------------------------------------
def say(text: str = "") -> None:
    print(text)
    LOG.append(text)


def section(num: int, title: str) -> None:
    say()
    say("=" * 100)
    say(f"{num}. {title}")
    say("=" * 100)


def show(df: pd.DataFrame, **kw) -> None:
    say(df.to_string(**kw))


def wilson(k: float, n: float, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def auc_score(y, s) -> float:
    """AUC por soma de postos (Mann-Whitney); empates contam 0,5."""
    y = np.asarray(y).astype(int)
    s = np.asarray(s, dtype=float)
    n1 = int(y.sum())
    n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return float("nan")
    r = stats.rankdata(s)
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def boot_auc_ci(y, s, n_boot: int = 300, seed: int = SEED) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    y = np.asarray(y)
    s = np.asarray(s, dtype=float)
    vals = []
    for _ in range(n_boot):
        i = rng.integers(0, len(y), len(y))
        v = auc_score(y[i], s[i])
        if not np.isnan(v):
            vals.append(v)
    return (float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5)))


def sanitize(o):
    if isinstance(o, dict):
        return {str(k): sanitize(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [sanitize(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating, float)):
        return None if (isinstance(o, float) and np.isnan(o)) or (isinstance(o, np.floating) and np.isnan(o)) else float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, (pd.Timestamp,)):
        return o.strftime("%Y-%m-%d")
    if isinstance(o, pd.Period):
        return str(o)
    if isinstance(o, pd.DataFrame):
        return sanitize(o.reset_index().to_dict(orient="records"))
    if isinstance(o, pd.Series):
        return sanitize(o.to_dict())
    return o


def fmt_p(p: float) -> str:
    return "<1e-300" if p == 0 else f"{p:.3g}"


def canon(s) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def month_of_quarter(dt: pd.Series) -> pd.Series:
    return ((dt.dt.month - 1) % 3) + 1


def rate_table(df: pd.DataFrame, col: str, y: str = "won") -> pd.DataFrame:
    g = df.groupby(col, dropna=False)[y].agg(wins="sum", n="count")
    g["win_rate"] = g["wins"] / g["n"]
    ci = [wilson(w, n) for w, n in zip(g["wins"], g["n"])]
    g["ci_low"] = [c[0] for c in ci]
    g["ci_high"] = [c[1] for c in ci]
    g["n_ge_min"] = g["n"] >= MIN_CELL
    return g.sort_values("n", ascending=False)


def eta_sq(df: pd.DataFrame, col: str, y: str = "won") -> dict:
    d = df[[col, y]].dropna()
    n = len(d)
    k = d[col].nunique()
    yb = d[y].mean()
    sst = ((d[y] - yb) ** 2).sum()
    g = d.groupby(col)[y].agg(["mean", "count"])
    ssb = (g["count"] * (g["mean"] - yb) ** 2).sum()
    eta = ssb / sst if sst > 0 else np.nan
    eps = 1 - (1 - eta) * (n - 1) / (n - k) if n > k else np.nan
    ct = pd.crosstab(d[col], d[y])
    chi2, p, dof, exp = stats.chi2_contingency(ct)
    v = np.sqrt(chi2 / (n * (min(ct.shape) - 1))) if min(ct.shape) > 1 else np.nan
    return {
        "factor": col, "levels": int(k), "n": int(n), "eta2": float(eta), "eps2_adj": float(eps),
        "cramers_v": float(v), "chi2_p": float(p), "pct_cells_expected_lt5": float((exp < 5).mean()),
    }


def r2_dummies(df: pd.DataFrame, cols: list[str], y: str = "won") -> dict:
    d = df[cols + [y]].dropna()
    X = pd.get_dummies(d[cols].astype(str), drop_first=True).astype(float).values
    X = np.column_stack([np.ones(len(d)), X])
    yv = d[y].values.astype(float)
    beta, *_ = np.linalg.lstsq(X, yv, rcond=None)
    res = yv - X @ beta
    sst = ((yv - yv.mean()) ** 2).sum()
    r2 = 1 - (res ** 2).sum() / sst
    n, p = X.shape
    adj = 1 - (1 - r2) * (n - 1) / (n - p) if n > p else np.nan
    return {"cols": cols, "n": int(n), "n_params": int(p), "r2": float(r2), "r2_adj": float(adj)}


# ----------------------------------------------------------------------------
# 0. carga e hashes
# ----------------------------------------------------------------------------
def load_raw() -> dict[str, pd.DataFrame]:
    raw = {}
    for t in TABLES:
        raw[t] = pd.read_csv(RAW / f"{t}.csv", dtype=str, keep_default_na=False)
    return raw


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


# ----------------------------------------------------------------------------
# 1. inventario
# ----------------------------------------------------------------------------
def infer_type(s: pd.Series) -> str:
    v = s[s != ""]
    if v.empty:
        return "vazio"
    num = pd.to_numeric(v, errors="coerce")
    if num.notna().all():
        return "inteiro" if (num % 1 == 0).all() else "decimal"
    dt = pd.to_datetime(v, format="%Y-%m-%d", errors="coerce")
    if dt.notna().all():
        return "data (AAAA-MM-DD)"
    return "texto"


def inventory(raw: dict[str, pd.DataFrame]) -> list[dict]:
    rows = []
    for t, df in raw.items():
        for c in df.columns:
            s = df[c]
            empty = int((s == "").sum())
            typ = infer_type(s)
            nonempty = s[s != ""]
            sentinel = int(nonempty.str.strip().str.lower().isin(SENTINELS).sum())
            ws = int((nonempty != nonempty.str.strip()).sum())
            lo = hi = None
            if typ in ("inteiro", "decimal"):
                num = pd.to_numeric(nonempty)
                lo, hi = format(float(num.min()), ".10g"), format(float(num.max()), ".10g")
            elif typ.startswith("data"):
                dt = pd.to_datetime(nonempty, format="%Y-%m-%d")
                lo, hi = dt.min().strftime("%Y-%m-%d"), dt.max().strftime("%Y-%m-%d")
            rows.append({
                "table": t, "column": c, "n_rows": len(df), "type": typ, "n_empty": empty,
                "pct_empty": round(100 * empty / len(df), 2), "n_unique": int(nonempty.nunique()),
                "min": lo, "max": hi, "sentinel_tokens": sentinel, "leading_trailing_ws": ws,
            })
    return rows


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    pd.set_option("display.width", 230)
    pd.set_option("display.max_columns", 40)
    pd.set_option("display.max_rows", 300)
    pd.set_option("display.float_format", lambda x: f"{x:,.0f}" if float(x).is_integer() else f"{x:,.4f}")

    say("AUDITORIA DE DADOS - Challenge 003 Lead Scorer")
    say(f"python {sys.version.split()[0]} | pandas {pd.__version__} | numpy {np.__version__} | "
        f"scipy {__import__('scipy').__version__} | sklearn {'ok' if HAS_SKLEARN else 'ausente'}")
    say(f"raw: {RAW.relative_to(ROOT)}")

    # ------------------------------------------------------------------ 0
    section(0, "Integridade dos arquivos de entrada (SHA-256, somente leitura)")
    hashes = {t: sha256(RAW / f"{t}.csv") for t in TABLES}
    for t, h in hashes.items():
        say(f"  {t}.csv  {h}")
    R["input_sha256"] = hashes

    raw = load_raw()

    # ------------------------------------------------------------------ 1
    section(1, "Inventario: arquivos, colunas, tipos, linhas, periodos, ausentes")
    inv = inventory(raw)
    R["inventory"] = inv
    show(pd.DataFrame(inv), index=False)

    meta = raw["metadata"]
    declared = set(zip(meta["Table"].str.strip(), meta["Field"].str.strip()))
    actual = {(t, c) for t in TABLES if t != "metadata" for c in raw[t].columns}
    say()
    say(f"metadata.csv declara {len(declared)} campos; {len(actual)} colunas reais nas 4 tabelas.")
    say(f"  declarados e ausentes nos dados: {sorted(declared - actual)}")
    say(f"  presentes nos dados e nao declarados: {sorted(actual - declared)}")
    R["metadata_check"] = {"declared_not_in_data": sorted(declared - actual),
                           "in_data_not_declared": sorted(actual - declared)}

    # tipagem explicita
    acc = raw["accounts"].replace("", np.nan).copy()
    for c in ["year_established", "revenue", "employees"]:
        acc[c] = pd.to_numeric(acc[c])
    prod = raw["products"].copy()
    prod["sales_price"] = pd.to_numeric(prod["sales_price"])
    teams = raw["sales_teams"].copy()
    pipe = raw["sales_pipeline"].replace("", np.nan).copy()
    pipe["engage"] = pd.to_datetime(pipe["engage_date"], format="%Y-%m-%d", errors="coerce")
    pipe["close"] = pd.to_datetime(pipe["close_date"], format="%Y-%m-%d", errors="coerce")
    pipe["value"] = pd.to_numeric(pipe["close_value"], errors="coerce")
    pipe["row_pos"] = np.arange(len(pipe))
    n_pipe = len(pipe)

    # ------------------------------------------------------------------ 2
    section(2, "Granularidade, chaves e cardinalidade")
    keys = {}
    for name, df, key in [("accounts", acc, "account"), ("products", prod, "product"),
                          ("sales_teams", teams, "sales_agent"), ("sales_pipeline", pipe, "opportunity_id")]:
        dup = int(df[key].duplicated().sum())
        nul = int(df[key].isna().sum())
        keys[name] = {"key": key, "rows": len(df), "distinct": int(df[key].nunique()), "duplicates": dup, "nulls": nul}
        say(f"  {name:15s} chave={key:15s} linhas={len(df):5d} distintas={df[key].nunique():5d} duplicadas={dup} nulas={nul}")
    R["keys"] = keys

    say()
    say("Cardinalidade (linhas do pipeline por pai):")
    card = {}
    for child, parent_key, parent_df, pk in [("sales_agent", "sales_agent", teams, "sales_agent"),
                                              ("account", "account", acc, "account"),
                                              ("product", "product", prod, "product")]:
        vc = pipe[child].value_counts()
        unused = sorted(set(parent_df[pk]) - set(vc.index))
        card[child] = {"distinct_in_pipeline": int(vc.size), "parents_in_table": int(parent_df[pk].nunique()),
                       "rows_per_parent_min": int(vc.min()), "rows_per_parent_median": float(vc.median()),
                       "rows_per_parent_max": int(vc.max()), "parents_without_pipeline_rows": unused}
        say(f"  {child:12s}: {vc.size} distintos no pipeline de {parent_df[pk].nunique()} na tabela-pai | "
            f"linhas/pai min={vc.min()} mediana={vc.median():.0f} max={vc.max()} | pais sem linhas: {unused}")
    R["cardinality"] = card
    t_mgr = teams.groupby("sales_agent")["manager"].nunique().max()
    say(f"  agente -> manager distintos (max): {t_mgr} | managers: {teams['manager'].nunique()} | "
        f"escritorios: {teams['regional_office'].value_counts().to_dict()}")
    sub_missing = sorted(set(acc["subsidiary_of"].dropna()) - set(acc["account"]))
    say(f"  accounts.subsidiary_of preenchido: {int(acc['subsidiary_of'].notna().sum())}; "
        f"referencias inexistentes em accounts: {sub_missing}")
    R["subsidiary_orphans"] = sub_missing

    # ------------------------------------------------------------------ 3
    section(3, "Integridade de joins e risco de multiplicacao de linhas")
    pcanon: dict[str, str] = {}
    for p_ in prod["product"]:
        pcanon.setdefault(canon(p_), p_)
    say(f"  chaves canonicas unicas em products: {len(pcanon) == len(prod)}")
    exact = set(prod["product"])
    labels = pipe["product"].value_counts()
    mapping = {}
    for lab in labels.index:
        mapping[lab] = lab if lab in exact else pcanon.get(canon(lab))
    unmatched_exact = {k: int(labels[k]) for k in labels.index if k not in exact}
    unresolved = [k for k, v in mapping.items() if v is None]
    say(f"  rotulos de produto no pipeline: {len(labels)} | sem match exato em products: {unmatched_exact}")
    say(f"  rotulos sem match nem por forma canonica: {unresolved}")
    pipe["product_std"] = pipe["product"].map(mapping)

    # evidencia empirica do mapeamento: razao close_value/preco nos Won
    won_ev = pipe[(pipe["deal_stage"] == "Won")].merge(
        prod.rename(columns={"product": "cand"}), how="cross")
    ev = (won_ev.assign(ratio=won_ev["value"] / won_ev["sales_price"])
          .groupby(["product", "cand"])["ratio"].median().reset_index())
    ev["dist"] = (np.log(ev["ratio"])).abs()
    best = ev.sort_values("dist").groupby("product").head(1).set_index("product")[["cand", "ratio"]]
    best["canon_match"] = best.index.map(mapping)
    say("  rotulo -> preco de catalogo mais proximo (mediana close_value/preco nos Won) vs mapeamento canonico:")
    show(best.rename(columns={"cand": "best_price_match", "ratio": "median_ratio"}))
    R["product_mapping"] = {"mapping": mapping, "unmatched_exact": unmatched_exact,
                            "price_evidence": best.reset_index().to_dict(orient="records")}

    say()
    say(f"  linhas do pipeline (base): {n_pipe}")
    j1 = pipe.merge(prod, on="product", how="left", validate="m:1")
    j1_inner = pipe.merge(prod, on="product", how="inner", validate="m:1")
    say(f"  join por nome EXATO do produto: left={len(j1)} (sales_price nulo: {int(j1['sales_price'].isna().sum())}) | "
        f"inner={len(j1_inner)} (perde {n_pipe - len(j1_inner)} linhas = {100 * (n_pipe - len(j1_inner)) / n_pipe:.1f}%)")
    j2 = pipe.merge(prod.rename(columns={"product": "product_std"}), on="product_std", how="left", validate="m:1")
    say(f"  join por produto NORMALIZADO: left={len(j2)} (sales_price nulo: {int(j2['sales_price'].isna().sum())})")
    j3 = j2.merge(teams, on="sales_agent", how="left", validate="m:1")
    say(f"  + sales_teams por sales_agent: linhas={len(j3)} (manager nulo: {int(j3['manager'].isna().sum())})")
    j4 = j3.merge(acc, on="account", how="left", validate="m:1", suffixes=("", "_acc"))
    say(f"  + accounts por account: linhas={len(j4)} (sector nulo: {int(j4['sector'].isna().sum())}; "
        f"account nula no pipeline: {int(pipe['account'].isna().sum())})")
    inner_all = j3.merge(acc, on="account", how="inner")
    say(f"  inner join com accounts perderia {len(j3) - len(inner_all)} linhas "
        f"({100 * (len(j3) - len(inner_all)) / len(j3):.1f}%) - todas com account nula")
    R["joins"] = {
        "base_rows": n_pipe, "left_exact_product_null_price": int(j1["sales_price"].isna().sum()),
        "inner_exact_product_rows": len(j1_inner), "left_normalized_null_price": int(j2["sales_price"].isna().sum()),
        "after_teams_rows": len(j3), "after_accounts_rows": len(j4),
        "inner_accounts_rows_lost": len(j3) - len(inner_all),
    }
    # multiplicacao: uma auto-juncao por conta (ex.: "historico da conta") explode as linhas
    vc = pipe["account"].dropna().value_counts()
    selfjoin = int((vc ** 2).sum())
    say(f"  RISCO: auto-juncao do pipeline por account geraria {selfjoin} pares a partir de "
        f"{int(vc.sum())} linhas com conta ({selfjoin / vc.sum():.1f}x).")
    R["joins"]["selfjoin_by_account_pairs"] = selfjoin
    R["joins"]["selfjoin_by_account_multiplier"] = selfjoin / float(vc.sum())

    # frame analitico (apenas para a auditoria)
    df = j4.copy()
    df["won"] = (df["deal_stage"] == "Won").astype(int)
    df["is_closed"] = df["deal_stage"].isin(CLOSED_STAGES)
    df["cycle_days"] = (df["close"] - df["engage"]).dt.days

    # ------------------------------------------------------------------ 4
    section(4, "Duplicatas, valores invalidos, anomalias e inconsistencias")
    exact_dups = int(pipe.drop(columns=["row_pos"]).duplicated().sum())
    cols_wo_id = ["sales_agent", "product", "account", "deal_stage", "engage_date", "close_date", "close_value"]
    dgrp = pipe[pipe.duplicated(cols_wo_id, keep=False)]
    sizes = dgrp.groupby(cols_wo_id, dropna=False).size()
    say(f"  linhas 100% duplicadas (incluindo ID): {exact_dups}")
    say(f"  linhas identicas em tudo exceto opportunity_id: {len(dgrp)} em {len(sizes)} grupos "
        f"(maior grupo: {int(sizes.max())})")
    say(f"    por estagio: {dgrp['deal_stage'].value_counts().to_dict()}")
    say(f"    com account nula: {int(dgrp['account'].isna().sum())} de {len(dgrp)}")
    say(f"    Prospecting sem nenhuma data: {int(((dgrp['deal_stage'] == 'Prospecting') & dgrp['engage'].isna()).sum())}")
    R["duplicates"] = {
        "exact_rows": exact_dups, "same_except_id_rows": len(dgrp), "groups": len(sizes),
        "largest_group": int(sizes.max()), "by_stage": dgrp["deal_stage"].value_counts().to_dict(),
        "with_null_account": int(dgrp["account"].isna().sum()),
        "group_size_distribution": sizes.value_counts().sort_index().to_dict(),
    }

    say()
    say("  Valores distintos de categorias (revisao de grafia):")
    for tname, d, col in [("accounts", acc, "sector"), ("accounts", acc, "office_location"),
                          ("products", prod, "series"), ("sales_teams", teams, "regional_office"),
                          ("sales_pipeline", pipe, "deal_stage")]:
        vals = sorted(d[col].dropna().unique())
        say(f"    {tname}.{col} ({len(vals)}): {vals}")
    R["sector_values"] = sorted(acc["sector"].unique())

    say()
    say("  Regras estruturais por estagio (violacoes):")
    rules = []
    for stage in ["Prospecting", "Engaging", "Won", "Lost"]:
        g = pipe[pipe["deal_stage"] == stage]
        rules.append({
            "stage": stage, "n": len(g),
            "engage_null": int(g["engage"].isna().sum()), "close_null": int(g["close"].isna().sum()),
            "value_null": int(g["value"].isna().sum()), "account_null": int(g["account"].isna().sum()),
            "close_before_engage": int((g["close"] < g["engage"]).sum()),
            "value_le_0": int((g["value"] <= 0).sum()), "value_gt_0": int((g["value"] > 0).sum()),
        })
    show(pd.DataFrame(rules), index=False)
    R["stage_rules"] = rules
    bad_dates = int((pipe["engage_date"].notna() & pipe["engage"].isna()).sum() +
                    (pipe["close_date"].notna() & pipe["close"].isna()).sum())
    bad_value = int((pipe["close_value"].notna() & pipe["value"].isna()).sum())
    say(f"  datas nao parseaveis: {bad_dates} | close_value nao numerico: {bad_value}")
    R["unparseable"] = {"dates": bad_dates, "close_value": bad_value}

    say()
    say("  Outliers numericos (regra 1,5xIQR):")
    out_rows = []
    for tname, series in [("accounts.revenue", acc["revenue"]), ("accounts.employees", acc["employees"]),
                          ("accounts.year_established", acc["year_established"]),
                          ("pipeline.close_value (Won)", pipe.loc[pipe["deal_stage"] == "Won", "value"])]:
        q1, q3 = series.quantile([0.25, 0.75])
        iqr = q3 - q1
        n_out = int(((series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)).sum())
        out_rows.append({"series": tname, "n": int(series.notna().sum()), "min": series.min(), "p50": series.median(),
                         "max": series.max(), "n_outliers_iqr": n_out})
    show(pd.DataFrame(out_rows), index=False)
    R["numeric_outliers"] = out_rows
    rpe = (acc["revenue"] * 1e6 / acc["employees"])
    say(f"  receita por funcionario (US$): min={rpe.min():,.0f} mediana={rpe.median():,.0f} max={rpe.max():,.0f}")

    # ------------------------------------------------------------------ 5
    section(5, "Completude condicionada ao estagio (nulo estrutural x falha)")
    comp = (pipe.groupby("deal_stage")[["sales_agent", "product", "account", "engage_date", "close_date", "close_value"]]
            .apply(lambda g: g.isna().mean() * 100).loc[["Prospecting", "Engaging", "Won", "Lost"]])
    say("  % nulo por estagio:")
    show(comp.round(1))
    R["completeness_by_stage_pct"] = comp.round(2)
    op = pipe[pipe["deal_stage"].isin(OPEN_STAGES)]
    cl = pipe[pipe["deal_stage"].isin(CLOSED_STAGES)]
    say(f"  account nula: abertos={op['account'].isna().mean():.1%} ({int(op['account'].isna().sum())}/{len(op)}) | "
        f"fechados={cl['account'].isna().mean():.1%} ({int(cl['account'].isna().sum())}/{len(cl)})")
    chi_acc = stats.chi2_contingency(pd.crosstab(pipe["deal_stage"], pipe["account"].isna()))
    say(f"  teste qui-quadrado estagio x account-nula: p={fmt_p(chi_acc[1])}")
    nullshare = op.assign(n=op["account"].isna()).groupby("sales_agent")["n"].mean()
    say(f"  % account nula entre abertos por vendedor: min={nullshare.min():.0%} max={nullshare.max():.0%}")
    R["account_missing"] = {"open_pct": float(op["account"].isna().mean()), "closed_pct": float(cl["account"].isna().mean()),
                            "open_n_null": int(op["account"].isna().sum()), "open_n": len(op),
                            "by_agent_min": float(nullshare.min()), "by_agent_max": float(nullshare.max())}

    # ------------------------------------------------------------------ 6
    section(6, "Datas, periodo coberto, ciclo e padroes de calendario (V3, V4)")
    cut_close = pipe["close"].max()
    cut_engage = pipe["engage"].max()
    CUT = cut_close
    say(f"  engage_date: {pipe['engage'].min().date()} a {cut_engage.date()} | "
        f"close_date: {pipe['close'].min().date()} a {cut_close.date()}")
    say(f"  data de corte ADOTADA (premissa, nao fornecida): {CUT.date()} (= maior close_date)")
    R["dates"] = {"engage_min": pipe["engage"].min(), "engage_max": cut_engage,
                  "close_min": pipe["close"].min(), "close_max": cut_close, "cutoff_assumed": CUT}
    say(f"  nenhum deal fechado antes de {pipe['close'].min().date()}, embora engajamentos comecem em "
        f"{pipe['engage'].min().date()}")
    em = df.groupby(df["engage"].dt.to_period("M")).agg(n_engaged=("opportunity_id", "size"),
                                                         n_closed=("is_closed", "sum"),
                                                         win_rate_closed=("won", lambda s: np.nan))
    clm = df[df["is_closed"]]
    em["win_rate_closed"] = clm.groupby(clm["engage"].dt.to_period("M"))["won"].mean()
    em["min_cycle_closed"] = clm.groupby(clm["engage"].dt.to_period("M"))["cycle_days"].min()
    say("  por mes de engage_date (deals com data):")
    show(em)
    R["by_engage_month"] = em
    cm = clm.groupby(clm["close"].dt.to_period("M")).agg(n_closed=("won", "size"), win_rate=("won", "mean"))
    say("  por mes de close_date:")
    show(cm)
    R["by_close_month"] = cm

    clm = clm.assign(moq_close=month_of_quarter(clm["close"]))
    moq = clm.groupby("moq_close").agg(n=("won", "size"), win_rate=("won", "mean"))
    say("  taxa de ganho por mes-do-trimestre do FECHAMENTO (1=jan/abr/jul/out, 2=fev/mai/ago/nov, 3=mar/jun/set/dez):")
    show(moq)
    R["win_by_close_month_of_quarter"] = moq

    say("  ciclo (close - engage, dias) dos fechados por resultado:")
    cyc = clm.groupby("deal_stage")["cycle_days"].describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9])
    show(cyc)
    R["cycle_by_outcome"] = cyc
    bins = [0, 7, 14, 28, 56, 84, 112, 140]
    hist = (pd.crosstab(pd.cut(clm["cycle_days"], bins=bins), clm["deal_stage"]))
    say("  histograma do ciclo por faixa de dias:")
    show(hist)
    R["cycle_hist"] = hist

    say("  calendario do fechamento (V4: limpeza em lote?):")
    dow = clm["close"].dt.dayofweek.value_counts().sort_index()
    wk_end = float(((clm["close"].dt.dayofweek >= 5)).mean())
    me = clm.groupby("deal_stage")["close"].apply(lambda s: s.dt.is_month_end.mean())
    perday = clm.groupby("close").size()
    say(f"    dia da semana (0=seg): {dow.to_dict()} | fechamentos em fim de semana: {wk_end:.1%}")
    say(f"    fechamento no ultimo dia do mes: {me.round(4).to_dict()} (esperado se uniforme ~ {1/30:.1%})")
    say(f"    fechamentos por dia: media={perday.mean():.1f} max={perday.max()} ({perday.idxmax().date()}) "
        f"dias distintos={perday.size}")
    disp = float(perday.var() / perday.mean())
    say(f"    indice de dispersao (variancia/media) dos fechamentos por dia: {disp:.2f} (~1 se chegassem de forma independente)")
    top_days = perday.sort_values(ascending=False).head(5)
    say(f"    5 dias com mais fechamentos: {{{', '.join(f'{k.date()}: {v}' for k, v in top_days.items())}}}")
    R["close_calendar"] = {"dow": dow.to_dict(), "weekend_share": wk_end, "month_end_share": me.to_dict(),
                           "per_day_mean": float(perday.mean()), "per_day_max": int(perday.max()),
                           "per_day_dispersion_index": disp}

    # ------------------------------------------------------------------ 7
    section(7, "Distribuicoes de estagio, resultado e valor")
    st = pipe["deal_stage"].value_counts()
    say("  estagios:")
    show(pd.DataFrame({"n": st, "pct": (100 * st / len(pipe)).round(2)}))
    R["stages"] = st.to_dict()
    won = df[df["deal_stage"] == "Won"]
    say(f"  close_value dos Won: n={len(won)} soma={won['value'].sum():,.0f} media={won['value'].mean():,.1f} "
        f"mediana={won['value'].median():,.1f} max={won['value'].max():,.0f}")
    say("  valores por produto (Won): n, mediana close_value e preco de catalogo")
    pv = won.groupby("product_std").agg(n=("value", "size"), median_value=("value", "median"),
                                        list_price=("sales_price", "first"))
    show(pv)
    R["won_value_by_product"] = pv
    say("  deals por produto x estagio (produto normalizado):")
    pxs = pd.crosstab(df["product_std"], df["deal_stage"])[["Prospecting", "Engaging", "Won", "Lost"]]
    pxs["total"] = pxs.sum(axis=1)
    show(pxs)
    R["product_by_stage"] = pxs
    say("  deals por vendedor (30 com deals; total historico):")
    apd = df.groupby("sales_agent").agg(total=("opportunity_id", "size"), closed=("is_closed", "sum"),
                                        open=("is_closed", lambda s: int((~s).sum())),
                                        win_rate_closed=("won", lambda s: np.nan))
    apd["win_rate_closed"] = df[df["is_closed"]].groupby("sales_agent")["won"].mean()
    say(f"    vendedores com deals: {len(apd)} | total/vendedor: min={apd['total'].min()} "
        f"mediana={apd['total'].median():.0f} max={apd['total'].max()}")
    say(f"    abertos/vendedor: min={apd['open'].min()} mediana={apd['open'].median():.0f} max={apd['open'].max()}")
    R["deals_per_agent"] = apd
    comp_ac = df[df["account"].notna()].groupby("account").size().sort_values(ascending=False)
    top5 = comp_ac.head(5).sum() / comp_ac.sum()
    top10 = comp_ac.head(10).sum() / comp_ac.sum()
    won_acc = won.groupby("account")["value"].sum().sort_values(ascending=False)
    say(f"  concentracao por conta (so deals com conta): top-5={top5:.1%} top-10={top10:.1%} das linhas; "
        f"top-5 contas = {won_acc.head(5).sum() / won_acc.sum():.1%} do valor Won")
    say(f"    contas com >=1 deal: {comp_ac.size}; mediana de deals/conta: {comp_ac.median():.0f}")
    R["account_concentration"] = {"top5_rows": float(top5), "top10_rows": float(top10),
                                  "top5_won_value": float(won_acc.head(5).sum() / won_acc.sum()),
                                  "top_accounts": comp_ac.head(10)}

    # ------------------------------------------------------------------ 8
    section(8, "Variavel-alvo candidata (Won x Lost) e disponibilidade")
    closed = df[df["is_closed"]].copy()
    n_closed = len(closed)
    n_won = int(closed["won"].sum())
    lo, hi = wilson(n_won, n_closed)
    say(f"  alvo: won = 1 se deal_stage == 'Won'; 0 se 'Lost'; indefinido para Prospecting/Engaging")
    say(f"  rotulados: {n_closed} de {len(df)} ({n_closed / len(df):.1%}) | Won={n_won} Lost={n_closed - n_won} | "
        f"taxa de ganho={n_won / n_closed:.4f} IC95% [{lo:.4f}, {hi:.4f}]")
    say(f"  nao rotulados (abertos): {len(df) - n_closed} = Engaging {int((df['deal_stage'] == 'Engaging').sum())} "
        f"+ Prospecting {int((df['deal_stage'] == 'Prospecting').sum())}")
    price_w = closed["sales_price"]
    vw = (closed["won"] * price_w).sum() / price_w.sum()
    say(f"  taxa de ganho ponderada por preco de catalogo (proxy de valor): {vw:.4f}")
    R["target"] = {"closed": n_closed, "won": n_won, "lost": n_closed - n_won, "win_rate": n_won / n_closed,
                   "ci95": [lo, hi], "open": len(df) - n_closed, "win_rate_price_weighted": float(vw)}

    # ------------------------------------------------------------------ 9
    section(9, "Treino x inferencia: o que existe em cada momento (matriz de disponibilidade)")
    avail = []

    def cov(col, stage):
        g = df[df["deal_stage"].isin(stage)]
        return round(100 * g[col].notna().mean(), 1)

    spec = [
        ("opportunity_id", "identificador", "nao e feature (sem informacao esperada)"),
        ("sales_agent", "atributo do deal", "ok na criacao"),
        ("product_std", "atributo do deal", "ok na criacao (exige normalizar 'GTXPro')"),
        ("account", "atributo do deal", "ok quando preenchido; nulo em 68% dos abertos"),
        ("sales_price", "derivado do produto", "ok (catalogo)"),
        ("manager", "derivado do vendedor", "ok (atribuicao atual, nao historica)"),
        ("regional_office", "derivado do vendedor", "ok (atribuicao atual, nao historica)"),
        ("sector", "derivado da conta", "ok se houver conta; foto atual da conta"),
        ("revenue", "derivado da conta", "ok se houver conta; foto atual da conta"),
        ("engage", "data do deal", "ok a partir de Engaging; ausente em Prospecting"),
        ("deal_stage", "estagio atual", "e o filtro (aberto x fechado), nao feature de resultado"),
        ("close", "VAZAMENTO", "so existe apos o desfecho"),
        ("value", "VAZAMENTO", "so existe apos o desfecho (Lost = 0 por definicao)"),
        ("cycle_days", "VAZAMENTO", "close - engage; so existe apos o desfecho"),
    ]
    for col, kind, note in spec:
        avail.append({"field": col, "class": kind,
                      "pct_filled_Prospecting": cov(col, ["Prospecting"]),
                      "pct_filled_Engaging": cov(col, ["Engaging"]),
                      "pct_filled_Won": cov(col, ["Won"]), "pct_filled_Lost": cov(col, ["Lost"]),
                      "note": note})
    show(pd.DataFrame(avail), index=False)
    R["availability"] = avail
    n_eng_acc = int(((df["deal_stage"] == "Engaging") & df["account"].notna()).sum())
    n_pro_acc = int(((df["deal_stage"] == "Prospecting") & df["account"].notna()).sum())
    say(f"  abertos pontuaveis com todas as features estaticas (conta presente): Engaging {n_eng_acc}, Prospecting {n_pro_acc}")
    R["open_with_account"] = {"Engaging": n_eng_acc, "Prospecting": n_pro_acc}

    # ------------------------------------------------------------------ 10
    section(10, "Vazamento: sondas empiricas (AUC de uma unica variavel, Won=1, fechados)")
    closed["moq_close"] = month_of_quarter(closed["close"])
    closed["moq_engage"] = month_of_quarter(closed["engage"])
    closed["engage_ord"] = closed["engage"].map(pd.Timestamp.toordinal)
    closed["close_ord"] = closed["close"].map(pd.Timestamp.toordinal)
    closed["id_rank"] = closed["opportunity_id"].rank(method="first")
    probes = [
        ("cycle_days (close-engage)", closed["cycle_days"], "VAZAMENTO: so conhecido apos o desfecho"),
        ("close_date (ordinal)", closed["close_ord"], "VAZAMENTO: so conhecido apos o desfecho"),
        ("close no 3o mes do trimestre (Mar/Jun/Set/Dez) (0/1)", (closed["moq_close"] == 3).astype(int), "VAZAMENTO: derivado de close_date"),
        ("close_value > 0 (0/1)", (closed["value"] > 0).astype(int), "VAZAMENTO: e o proprio rotulo"),
        ("engage_date (ordinal)", closed["engage_ord"], "legitimo na inferencia (Engaging)"),
        ("engage month-of-quarter", closed["moq_engage"], "legitimo na inferencia (Engaging)"),
        ("sales_price", closed["sales_price"], "legitimo"),
        ("posicao da linha no CSV", closed["row_pos"], "artefato de ordenacao do arquivo; nao usar"),
        ("ordem alfabetica de opportunity_id", closed["id_rank"], "esperado ~0,5 se o ID nao carrega informacao"),
    ]
    prow = []
    for name, s, note in probes:
        a = auc_score(closed["won"], s)
        prow.append({"probe": name, "auc": a, "auc_sym": max(a, 1 - a), "note": note})
    show(pd.DataFrame(prow), index=False)
    R["leakage_probes"] = prow
    dated = df[df["engage"].notna()].sort_values("row_pos")
    mono = bool(dated["engage"].is_monotonic_increasing)
    first_pro = int(df.loc[df["deal_stage"] == "Prospecting", "row_pos"].min())
    last_dated = int(dated["row_pos"].max())
    say(f"  linhas com engage_date estao em ordem nao decrescente no arquivo: {mono}; "
        f"Prospecting comeca na linha {first_pro} (ultima linha com data: {last_dated})")
    R["row_order"] = {"engage_monotonic": mono, "first_prospecting_row": first_pro, "last_dated_row": last_dated}

    # ------------------------------------------------------------------ 11
    section(11, "Sinal por segmento: taxa de ganho com IC95% (V7)")
    seg_results = {}
    closed["series"] = closed["product_std"].map(prod.set_index("product")["series"])
    for col in ["product_std", "series", "regional_office", "manager", "sector", "office_location"]:
        t = rate_table(closed, col)
        seg_results[col] = t
        say(f"  --- {col} (n minimo para interpretar: {MIN_CELL}) ---")
        show(t.round(4))
    t = rate_table(closed, "sales_agent")
    seg_results["sales_agent"] = t
    say(f"  --- sales_agent: {len(t)} vendedores; taxa min={t['win_rate'].min():.3f} max={t['win_rate'].max():.3f}; "
        f"celulas com n<{MIN_CELL}: {int((~t['n_ge_min']).sum())} ---")
    show(t.round(4))
    ta = rate_table(closed.dropna(subset=["account"]), "account")
    seg_results["account"] = ta
    say(f"  --- account: {len(ta)} contas; celulas com n<{MIN_CELL}: {int((~ta['n_ge_min']).sum())}; "
        f"taxa min={ta['win_rate'].min():.3f} max={ta['win_rate'].max():.3f} ---")
    R["segments"] = {k: v for k, v in seg_results.items()}

    # ------------------------------------------------------------------ 12
    section(12, "O vendedor domina a variancia? Decomposicao simples (V8)")
    cl2 = closed.copy()
    cl2["engage_month"] = cl2["engage"].dt.to_period("M").astype(str)
    cl2["close_month"] = cl2["close"].dt.to_period("M").astype(str)
    cl2["moq_close_s"] = cl2["moq_close"].astype(str)
    cl2["moq_engage_s"] = cl2["moq_engage"].astype(str)
    eta_rows = [eta_sq(cl2, c) for c in ["product_std", "sales_agent", "manager", "regional_office", "sector",
                                          "account", "engage_month", "moq_engage_s", "close_month", "moq_close_s"]]
    show(pd.DataFrame(eta_rows), index=False)
    R["eta_squared"] = eta_rows
    say("  modelo linear de probabilidade (R2 ajustado) - quanto cada bloco explica de Won x Lost:")
    r2_rows = [
        r2_dummies(cl2, ["product_std"]), r2_dummies(cl2, ["sales_agent"]),
        r2_dummies(cl2, ["product_std", "sales_agent"]), r2_dummies(cl2, ["product_std", "sales_agent", "regional_office"]),
        r2_dummies(cl2.dropna(subset=["account"]), ["account"]),
        r2_dummies(cl2, ["moq_engage_s"]), r2_dummies(cl2, ["moq_close_s"]),
        r2_dummies(cl2, ["close_month"]),
    ]
    show(pd.DataFrame(r2_rows), index=False)
    R["r2_blocks"] = r2_rows

    # ------------------------------------------------------------------ 13
    section(13, "Ciclo por produto e resultado (V5) e deals abertos fora do ciclo (V6)")
    cyc_prod = closed.groupby(["product_std", "deal_stage"])["cycle_days"].describe(percentiles=[0.5, 0.9])[
        ["count", "mean", "50%", "90%", "max"]].round(1)
    show(cyc_prod)
    R["cycle_by_product_outcome"] = cyc_prod
    p90_all_won = float(closed.loc[closed["won"] == 1, "cycle_days"].quantile(0.9))
    max_closed_cycle = int(closed["cycle_days"].max())
    say(f"  P90 do ciclo dos Won (geral): {p90_all_won:.0f} dias | maior ciclo entre fechados: {max_closed_cycle} dias")
    eng = df[df["deal_stage"] == "Engaging"].copy()
    zom = []
    for label, cutd in [("max close_date", cut_close), ("max engage_date", cut_engage)]:
        age = (cutd - eng["engage"]).dt.days
        p90 = eng["product_std"].map(closed[closed["won"] == 1].groupby("product_std")["cycle_days"].quantile(0.9))
        zom.append({"cutoff": label, "date": cutd.date(), "n_engaging": len(eng),
                    "age_median": float(age.median()), "age_max": int(age.max()),
                    "n_older_than_max_closed_cycle": int((age > max_closed_cycle).sum()),
                    "pct_older_than_max_closed_cycle": float((age > max_closed_cycle).mean()),
                    "n_older_than_product_P90_won": int((age > p90).sum()),
                    "pct_older_than_product_P90_won": float((age > p90).mean()),
                    "price_value_older_than_max_cycle": float(eng.loc[age > max_closed_cycle, "sales_price"].sum()),
                    "price_value_all_engaging": float(eng["sales_price"].sum())})
    show(pd.DataFrame(zom), index=False)
    R["aged_engaging"] = zom
    age_bins = pd.cut((cut_close - eng["engage"]).dt.days, bins=[0, 30, 60, 90, 138, 200, 300, 450])
    say("  idade dos Engaging (dias ate max close_date):")
    show(age_bins.value_counts().sort_index().to_frame("n"))

    # ------------------------------------------------------------------ 14
    section(14, "Preco de catalogo como proxy do valor (V9) e concentracao/repeticao de contas (V10)")
    w = df[df["deal_stage"] == "Won"].copy()
    w["ratio"] = w["value"] / w["sales_price"]
    say(f"  close_value / preco (Won): n={len(w)} media={w['ratio'].mean():.3f} mediana={w['ratio'].median():.3f} "
        f"dp={w['ratio'].std():.3f} p5={w['ratio'].quantile(.05):.3f} p95={w['ratio'].quantile(.95):.3f}")
    say(f"    dentro de +-20% do preco: {((w['ratio'] - 1).abs() <= .2).mean():.1%} | "
        f"correlacao de Pearson close_value x preco: {w['value'].corr(w['sales_price']):.4f}")
    byp = w.groupby("product_std")["ratio"].agg(["count", "mean", "median", "std", "min", "max"])
    show(byp.round(3))
    R["price_proxy"] = {"ratio_mean": float(w["ratio"].mean()), "ratio_median": float(w["ratio"].median()),
                        "ratio_sd": float(w["ratio"].std()), "within_20pct": float(((w["ratio"] - 1).abs() <= .2).mean()),
                        "pearson": float(w["value"].corr(w["sales_price"])), "by_product": byp}
    say("  (price proxy: preco de tabela; nao ha desconto/margem/valor anual no dataset)")

    # ------------------------------------------------------------------ 15
    section(15, "Carga aberta por vendedor x desfecho (V11)")
    d_ = df[df["engage"].notna()].copy()
    load = pd.Series(0.0, index=d_.index)
    for agent, g in d_.groupby("sales_agent"):
        eng_sorted = np.sort(g["engage"].values)
        clo_sorted = np.sort(g["close"].dropna().values)
        t_ = g["engage"].values
        n_eng_le = np.searchsorted(eng_sorted, t_, side="right")
        n_clo_le = np.searchsorted(clo_sorted, t_, side="right")
        load.loc[g.index] = n_eng_le - n_clo_le - 1  # exclui o proprio deal
    d_["load_at_engage"] = load
    say(f"  carga SEM RESTRICAO (deals com engage_date abertos do vendedor na data do engage; exclui Prospecting): "
        f"media={d_['load_at_engage'].mean():.1f} p50={d_['load_at_engage'].median():.0f} max={d_['load_at_engage'].max():.0f}")
    dc = d_[d_["is_closed"]].copy()
    dc["load_q"] = pd.qcut(dc["load_at_engage"], 4, duplicates="drop")
    lq = dc.groupby("load_q", observed=True).agg(n=("won", "size"), win_rate=("won", "mean"),
                                               cycle_median=("cycle_days", "median"))
    show(lq)
    rho_pooled = stats.spearmanr(dc["load_at_engage"], dc["won"])
    dc["load_dm"] = dc["load_at_engage"] - dc.groupby("sales_agent")["load_at_engage"].transform("mean")
    rho_within = stats.spearmanr(dc["load_dm"], dc["won"])
    say(f"  Spearman carga x ganho: agregado rho={rho_pooled.correlation:.3f} (p={fmt_p(rho_pooled.pvalue)}); "
        f"dentro do vendedor rho={rho_within.correlation:.3f} (p={fmt_p(rho_within.pvalue)})")
    dw = dc[dc["won"] == 1]
    rho_cyc = stats.spearmanr(dw["load_dm"], dw["cycle_days"])
    say(f"  Spearman carga (dentro do vendedor) x ciclo dos Won: rho={rho_cyc.correlation:.3f} (p={fmt_p(rho_cyc.pvalue)})")
    w0, w1 = pipe["close"].min(), pd.Timestamp("2017-08-15")
    dr = dc[(dc["engage"] >= w0) & (dc["engage"] <= w1)].copy()
    dr["load_dm"] = dr["load_at_engage"] - dr.groupby("sales_agent")["load_at_engage"].transform("mean")
    rr = stats.spearmanr(dr["load_dm"], dr["won"])
    dwr = dr[dr["won"] == 1]
    rrc = stats.spearmanr(dwr["load_dm"], dwr["cycle_days"])
    dr["load_q"] = pd.qcut(dr["load_at_engage"], 4, duplicates="drop")
    lqr = dr.groupby("load_q", observed=True).agg(n=("won", "size"), win_rate=("won", "mean"),
                                                cycle_median=("cycle_days", "median"))
    say(f"  VERSAO RESTRITA (engage entre {w0.date()} e {w1.date()}: fora do truncamento inicial e com >=138 dias para fechar):")
    show(lqr)
    say(f"    Spearman carga (dentro do vendedor) x ganho: rho={rr.correlation:.3f} (p={fmt_p(rr.pvalue)}), n={len(dr)}")
    say(f"    Spearman carga (dentro do vendedor) x ciclo dos Won: rho={rrc.correlation:.3f} (p={fmt_p(rrc.pvalue)})")
    dr["engage_month_s"] = dr["engage"].dt.to_period("M").astype(str)
    dr["load_dm_am"] = dr["load_at_engage"] - dr.groupby(["sales_agent", "engage_month_s"])["load_at_engage"].transform("mean")
    r_am = stats.spearmanr(dr["load_dm_am"], dr["won"])
    say(f"    controlando vendedor E mes do engage (carga centrada por vendedor x mes): rho={r_am.correlation:.3f} "
        f"(p={fmt_p(r_am.pvalue)})")
    say("    LEITURA: a carga cresce com o tempo no dataset (comeca vazio em 2016-10); sem a restricao ela se confunde")
    say("    com o truncamento inicial. Mesmo restrita, a correlacao e observacional e nao prova causalidade.")
    R["load_restricted"] = {"window": [w0, w1], "n": len(dr), "by_quartile": lqr,
                            "spearman_within_agent_win": float(rr.correlation), "p": float(rr.pvalue),
                            "spearman_within_agent_cycle_won": float(rrc.correlation),
                            "spearman_within_agent_month_win": float(r_am.correlation), "p_agent_month": float(r_am.pvalue)}
    R["load"] = {"mean": float(d_["load_at_engage"].mean()), "p50": float(d_["load_at_engage"].median()),
                 "max": float(d_["load_at_engage"].max()), "by_quartile": lq,
                 "spearman_pooled": float(rho_pooled.correlation), "p_pooled": float(rho_pooled.pvalue),
                 "spearman_within_agent": float(rho_within.correlation), "p_within": float(rho_within.pvalue),
                 "spearman_vs_cycle_won_within": float(rho_cyc.correlation)}

    # ------------------------------------------------------------------ 16
    section(16, "Viabilidade de baselines e modelos: backtest temporal (V12) - SONDA, nao solucao")
    say("  Desenho: corte T. Treino = fechados com close_date <= T. Teste = deals ja engajados em T e fechados depois de T")
    say("  (isto e, deals que estavam abertos em T e depois tiveram desfecho). Features congeladas em T: produto, vendedor,")
    say("  conta/setor (quando existe), mes-do-trimestre do engage. Sem close_date, close_value ou ciclo.")
    say(f"  Encolhimento das taxas por categoria: m={SMOOTH_M}. IC95% do AUC por bootstrap (300 reamostras, seed {SEED}).")
    say("  AVISO: nos fechados a conta nunca e nula, mas em 68% dos abertos e; as linhas '+conta' superestimam o que")
    say("  seria alcancavel na inferencia real.")

    def smoothed_rate(train, test, col, m=SMOOTH_M):
        p0 = train["won"].mean()
        g = train.groupby(col)["won"].agg(["sum", "count"])
        enc = (g["sum"] + m * p0) / (g["count"] + m)
        return test[col].map(enc).fillna(p0).values

    def metrics(y, p):
        eps = 1e-6
        p = np.clip(np.asarray(p, float), eps, 1 - eps)
        return {"auc": auc_score(y, p), "brier": float(np.mean((p - y) ** 2)),
                "logloss": float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))}

    bt_rows = []
    for T in BACKTEST_CUTS:
        Tt = pd.Timestamp(T)
        tr = closed[closed["close"] <= Tt]
        te = closed[(closed["engage"] <= Tt) & (closed["close"] > Tt)].copy()
        if len(te) < 100 or te["won"].nunique() < 2:
            continue
        y = te["won"].values
        p0 = tr["won"].mean()
        te["age_at_T"] = (Tt - te["engage"]).dt.days
        te["moq_engage_s"] = te["moq_engage"].astype(str)
        tr = tr.assign(moq_engage_s=tr["moq_engage"].astype(str))
        base = {"cut": T, "n_train": len(tr), "n_test": len(te), "train_win_rate": float(p0),
                "test_win_rate": float(y.mean()),
                "test_accounts_seen_in_train": float(te["account"].isin(set(tr["account"])).mean())}
        cands = {
            "B0 taxa global": np.full(len(te), p0),
            "B1 produto": smoothed_rate(tr, te, "product_std"),
            "B2 vendedor": smoothed_rate(tr, te, "sales_agent"),
            "B3 escritorio": smoothed_rate(tr, te, "regional_office"),
            "B4 setor da conta": smoothed_rate(tr, te, "sector"),
            "B5 mes-do-trimestre do engage": smoothed_rate(tr, te, "moq_engage_s"),
        }
        if HAS_SKLEARN:
            for name, cols in [("LR produto+vendedor+mes-trim.", ["product_std", "sales_agent", "moq_engage_s"]),
                               ("LR +conta(setor)", ["product_std", "sales_agent", "moq_engage_s", "sector"])]:
                both = pd.concat([tr[cols], te[cols]], keys=["tr", "te"]).astype(str)
                X = pd.get_dummies(both).astype(float)
                lr = LogisticRegression(C=1.0, max_iter=2000)
                lr.fit(X.loc["tr"].values, tr["won"].values)
                cands[name] = lr.predict_proba(X.loc["te"].values)[:, 1]
        row_models = []
        for name, p in cands.items():
            m_ = metrics(y, p)
            lo_, hi_ = boot_auc_ci(y, p) if name != "B0 taxa global" else (0.5, 0.5)
            row_models.append({"cut": T, "model": name, **m_, "auc_ci_low": lo_, "auc_ci_high": hi_})
        # idade em T (sinal legitimo na inferencia; sem treino)
        a_age = auc_score(y, te["age_at_T"])
        lo_a, hi_a = boot_auc_ci(y, te["age_at_T"].values)
        row_models.append({"cut": T, "model": "idade em T (dias desde engage; AUC bruto, sem treino)", "auc": a_age,
                           "brier": np.nan, "logloss": np.nan, "auc_ci_low": lo_a, "auc_ci_high": hi_a})
        # vazamento (so para demonstracao)
        a_leak = auc_score(y, te["cycle_days"])
        row_models.append({"cut": T, "model": "[VAZAMENTO] ciclo real (close-engage)", "auc": a_leak,
                           "brier": np.nan, "logloss": np.nan, "auc_ci_low": np.nan, "auc_ci_high": np.nan})
        a_leak2 = auc_score(y, (te["moq_close"] == 3).astype(int))
        row_models.append({"cut": T, "model": "[VAZAMENTO] fechou no 3o mes do trimestre", "auc": a_leak2,
                           "brier": np.nan, "logloss": np.nan, "auc_ci_low": np.nan, "auc_ci_high": np.nan})
        bt_rows.append({"summary": base, "models": row_models})
        say(f"\n  T={T}: treino={base['n_train']} (ganho {base['train_win_rate']:.3f}) | teste={base['n_test']} "
            f"(ganho {base['test_win_rate']:.3f}) | contas do teste vistas no treino: {base['test_accounts_seen_in_train']:.0%}")
        show(pd.DataFrame(row_models).drop(columns=["cut"]), index=False)
    R["backtest"] = bt_rows

    # tabela-resumo: AUC por modelo e corte
    if bt_rows:
        wide = pd.DataFrame([{**{"model": m["model"]}, **{r["summary"]["cut"]: m["auc"]}}
                             for r in bt_rows for m in r["models"]])
        wide = wide.groupby("model", sort=False).first()
        merged = {}
        for r in bt_rows:
            for m in r["models"]:
                merged.setdefault(m["model"], {})[r["summary"]["cut"]] = m["auc"]
        wide = pd.DataFrame(merged).T
        say("\n  Resumo: AUC no teste por modelo e corte")
        show(wide.round(3))
        R["backtest_auc_wide"] = wide

    # ------------------------------------------------------------------ 17
    section(17, "Estabilidade temporal (V14) e assinatura de truncamento")
    cut_rows = []
    for q, g in closed.groupby(closed["close"].dt.to_period("Q")):
        cut_rows.append({"close_quarter": str(q), "n": len(g), "win_rate": g["won"].mean(),
                         "cycle_median": g["cycle_days"].median()})
    show(pd.DataFrame(cut_rows), index=False)
    R["stability_by_close_quarter"] = cut_rows
    chi_m = stats.chi2_contingency(pd.crosstab(closed["close"].dt.to_period("M"), closed["won"]))
    say(f"  taxa de ganho por mes de fechamento: qui-quadrado p={fmt_p(chi_m[1])} (homogeneidade rejeitada se p pequeno)")
    first_close = pipe["close"].min()
    left_trunc = closed[closed["engage"] < first_close - pd.Timedelta(days=1)]
    say(f"  deals fechados com engage_date anterior a {first_close.date()}: {len(left_trunc)}; "
        f"ciclo minimo nesse grupo={left_trunc['cycle_days'].min()} dias vs. ciclo minimo geral={closed['cycle_days'].min()}")
    say("  Se deals que fecharam antes de 2017-03-01 foram excluidos do extrato, os engajados antes dessa data so")
    say("  aparecem se tiveram ciclo longo (truncamento a esquerda) - isso e uma hipotese; o dataset nao contem a regra de extracao.")
    sig = []
    for per, g in closed[closed["engage"] < first_close].groupby(closed["engage"].dt.to_period("M")):
        sig.append({"engage_month": str(per), "n_closed": len(g),
                    "days_from_last_engage_in_month_to_first_close": int((first_close - g["engage"].max()).days),
                    "min_cycle_observed": int(g["cycle_days"].min())})
    say("  assinatura do truncamento (engajados antes da primeira data de fechamento):")
    show(pd.DataFrame(sig), index=False)
    R["left_truncation_signature"] = sig
    R["left_truncation"] = {"closed_engaged_before_first_close": len(left_trunc),
                            "min_cycle_there": int(left_trunc["cycle_days"].min()),
                            "min_cycle_overall": int(closed["cycle_days"].min())}

    # ------------------------------------------------------------------ fim
    section(18, "Verificacao final: arquivos de entrada nao foram alterados")
    hashes_after = {t: sha256(RAW / f"{t}.csv") for t in TABLES}
    same = hashes_after == hashes
    say(f"  hashes antes == depois: {same}")
    R["input_unchanged"] = same

    (OUT / "audit_results.json").write_text(
        json.dumps(sanitize(R), indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    (OUT / "audit_log.txt").write_text("\n".join(LOG) + "\n", encoding="utf-8")
    say()
    say(f"Gravado: {OUT / 'audit_results.json'}")
    say(f"Gravado: {OUT / 'audit_log.txt'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
