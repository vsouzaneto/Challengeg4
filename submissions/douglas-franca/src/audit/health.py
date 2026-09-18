"""Gate 0: o arquivo serve para decidir? Regras de docs/process/06-data-contract.md.

Funções puras, usadas pelo Decision Gate (app/) e pelos testes. O arquivo do challenge é
reprovado aqui por construção: as regras foram escritas a partir dos achados DQ do G2.
"""

from dataclasses import dataclass

import pandas as pd

ALIASES = {
    "views": ["views", "impressions", "plays"],
    "likes": ["likes", "reactions"],
    "shares": ["shares", "reposts"],
    "comments": ["comments", "comments_count"],
}
MIN_COMPLETENESS = 0.95
MIN_OVERDISPERSION = 10.0  # var/média das views; Poisson dá ~1 (DQ-05)
MIN_LIKES_VIEWS_CORR = 0.3  # DQ-06
MIN_TAIL_RATIO = 5.0  # views máx / mediana (DQ-04)
MAX_CREATORS_WITH_MANY_NAMES = 0.01  # DQ-07
MIN_ROWS_FOR_DISTRIBUTION_RULES = 500


@dataclass(frozen=True)
class Check:
    code: str
    name: str
    passed: bool
    detail: str
    why: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "passed", bool(self.passed))  # numpy.bool_ -> bool


def _resolve(df: pd.DataFrame) -> dict[str, str | None]:
    lower = {c.lower(): c for c in df.columns}
    return {key: next((lower[a] for a in options if a in lower), None) for key, options in ALIASES.items()}


def _sponsored_mask(df: pd.DataFrame) -> pd.Series | None:
    col = next((c for c in df.columns if c.lower() in ("is_sponsored", "sponsored", "patrocinado")), None)
    if col is None:
        return None
    return df[col].astype(str).str.lower().isin(["true", "1", "sim", "yes"])


def health_check(df: pd.DataFrame) -> list[Check]:
    checks: list[Check] = []
    cols = _resolve(df)
    missing = [k for k, v in cols.items() if v is None]
    checks.append(Check("H1", "Métricas básicas presentes", not missing,
                        "todas presentes" if not missing else f"ausentes: {', '.join(missing)}",
                        "sem views, likes, shares e comentários não há taxa de engajamento"))
    if missing:
        return checks

    views, likes = df[cols["views"]], df[cols["likes"]]
    metric_cols = list(cols.values())
    completeness = df[metric_cols].notna().mean().min()
    checks.append(Check("H2", "Completude das métricas ≥ 95%", completeness >= MIN_COMPLETENESS,
                        f"menor completude: {completeness:.1%}", "dado incompleto vai para quarentena (FP-04)"))

    origin = [c for c in ("source_system", "extracted_at") if c in df.columns]
    origin_ok = len(origin) == 2 and df[origin].notna().all().all()
    checks.append(Check("H3", "Origem documentada (source_system, extracted_at)", origin_ok,
                        "origem em todas as linhas" if origin_ok else "sem colunas de origem preenchidas",
                        "a primeira pergunta ao time: de onde vieram estes dados? (FP-04)"))

    enough = len(df) >= MIN_ROWS_FOR_DISTRIBUTION_RULES
    zeros = int((df[metric_cols] == 0).any(axis=1).sum())
    checks.append(Check("H4", "Posts sem resultado estão registrados", zeros > 0 or not enough,
                        f"{zeros:,} posts com alguma métrica zerada em {len(df):,}",
                        "sem fracassos no arquivo, a estratégia é construída só com sobreviventes (DQ-04)"))

    dispersion = views.var() / views.mean() if views.mean() else 0.0
    checks.append(Check("H5", f"Views com variação realista (var/média ≥ {MIN_OVERDISPERSION:g})",
                        dispersion >= MIN_OVERDISPERSION or not enough,
                        f"var/média = {dispersion:,.2f}",
                        "var/média ≈ 1 é a assinatura de um sorteio de Poisson com média fixa (DQ-05)"))

    corr = views.corr(likes)
    checks.append(Check("H6", f"Likes acompanham views (r ≥ {MIN_LIKES_VIEWS_CORR:g})",
                        bool(corr >= MIN_LIKES_VIEWS_CORR) or not enough, f"r = {corr:.3f}",
                        "se mais views não trazem mais likes, as colunas estão desacopladas (DQ-06)"))

    tail = views.max() / views.median() if views.median() else 0.0
    checks.append(Check("H7", f"Existe cauda (views máx. ≥ {MIN_TAIL_RATIO:g}× mediana)",
                        tail >= MIN_TAIL_RATIO or not enough, f"máx./mediana = {tail:.2f}×",
                        "redes reais têm posts que viralizam; sem cauda, não há top performer a estudar"))

    sponsored = _sponsored_mask(df)
    if sponsored is not None and sponsored.any():
        has_campaign = "campaign_id" in df.columns and df.loc[sponsored, "campaign_id"].notna().all()
        checks.append(Check("H8", "Todo post patrocinado tem campaign_id", bool(has_campaign),
                            "ok" if has_campaign else "campaign_id ausente nos patrocinados",
                            "sem campaign_id o custo do CRM não chega ao post (FP-01)"))
        cost_col = next((c for c in ("custo_total", "cost", "fee") if c in df.columns), None)
        has_cost = cost_col is not None and df.loc[sponsored, cost_col].notna().all()
        checks.append(Check("H9", "Todo post patrocinado tem custo", bool(has_cost),
                            "ok" if has_cost else "custo ausente nos patrocinados",
                            "sem custo não existe retorno a calcular (FP-01, DQ-12)"))

    if {"creator_id", "creator_name"} <= set(df.columns):
        many = (df.groupby("creator_id")["creator_name"].nunique() > 1).mean()
        checks.append(Check("H10", "Cada creator tem um único nome", many <= MAX_CREATORS_WITH_MANY_NAMES,
                            f"{many:.1%} dos creators com mais de um nome",
                            "sem cadastro mestre, não há histórico de creator (FP-03, DQ-07)"))

    time_col = next((c for c in ("published_at", "post_date") if c in df.columns), None)
    if time_col is not None:
        with_tz = df[time_col].astype(str).str.contains(r"(?:Z|[+-]\d{2}:?\d{2})$", regex=True).mean()
        checks.append(Check("H11", "Data de publicação com fuso horário", with_tz >= 0.99,
                            f"{with_tz:.0%} das datas com fuso (coluna {time_col})",
                            "sem fuso, 'melhor horário' é chute (FP-06, DQ-14)"))
    return checks


def verdict(checks: list[Check]) -> tuple[bool, str]:
    failed = [c for c in checks if not c.passed]
    if not failed:
        return True, "APTO: este arquivo pode sustentar uma decisão"
    return False, f"NÃO APTO: {len(failed)} de {len(checks)} regras falharam; não use este arquivo para decidir verba"
