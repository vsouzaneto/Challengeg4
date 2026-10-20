"""Prediction service: turns a planned post into chances of being a top post, expected views/engagement and matching insights."""
from dataclasses import dataclass
from itertools import combinations

import numpy as np
import pandas as pd

from social_insights import audits, engagement_model, hit_probability, views_forecast
from social_insights.data import DAYPARTS, FOLLOWER_TIERS, LENGTH_BINS

METRICS = {"views": "views", "likes": "likes", "comments_count": "comentários"}
EVIDENCE_PLAIN = {"robusta (FDR)": "confirmado", "replicada (2 metades)": "se repetiu nos dois anos", "exploratória": "pista"}
MAX_POCKETS = 6
MAX_IMPROVEMENTS = 3
SEGMENT_FIELDS = ["platform", "content_category", "language"]  # the fields that define "similar posts"
CHANGEABLE = ["content_type", *SEGMENT_FIELDS]
MAX_CHANGES = 2


def market_check(frame: pd.DataFrame) -> dict:
    """Is the post in a language of its audience market, on a platform available there? (rules in audits.py)"""
    flags = audits.market_coherence_flags(frame).iloc[0]
    market = frame["audience_location"].iloc[0]
    return {"mercado": market, "idioma_ok": bool(flags["idioma do mercado"]), "plataforma_ok": bool(flags["plataforma disponível"]),
            "idiomas": sorted(audits.MARKET_LANGUAGES.get(market, set()))}


def _product(lists: list[list]) -> list[tuple]:
    out = [()]
    for values in lists:
        out = [prefix + (v,) for prefix in out for v in values]
    return out


def status(chance: dict) -> str:
    """Plain verdict for one metric: is the history of similar posts clearly above, clearly below or within normal?"""
    if chance["historico_min"] > chance["base"]:
        return "acima"
    if chance["historico_max"] < chance["base"]:
        return "abaixo"
    return "normal"


def _ratio(value: float) -> str:
    return f"{value:.1f}x".replace(".", ",")


def _bin(value: float, edges: dict) -> str:
    return next(label for label, edge in edges.items() if value < edge)


def build_row(post: dict, df: pd.DataFrame) -> dict:
    """Full feature row for one planned post: user inputs + derived bins + creator history (if a known creator is given)."""
    row = dict(post)
    row["daypart"] = _bin(post["hour"], DAYPARTS)
    row["follower_tier"] = _bin(post["follower_count"], FOLLOWER_TIERS)
    row["length_bin"] = _bin(post["content_length"], LENGTH_BINS)
    row["is_sponsored"] = str(post["is_sponsored"])
    row.update(views_forecast.creator_snapshot(df, post.get("creator_id") or ""))
    return row


def pocket_matches(pocket: dict, row: dict) -> bool:
    """Does a discovered pocket (conditions on pre-publication fields) apply to this post?"""
    if pocket["plataforma"] not in ("todas", row["platform"]) or not pocket["condicoes"]:
        return False
    for field, cond in pocket["condicoes"].items():
        if isinstance(cond, list):
            if not (cond[0] <= float(row.get(field, np.nan)) <= cond[1]):
                return False
        elif str(row.get(field)) != str(cond):
            return False
    return True


@dataclass
class PredictionService:
    df: pd.DataFrame
    hits: hit_probability.HitPredictor
    views: views_forecast.ViewsForecaster
    engagement: engagement_model.EngagementPredictor
    pockets: list[dict]

    def predict(self, post: dict, goal: str = "qualquer") -> dict:
        row = build_row(post, self.df)
        frame = pd.DataFrame([row])
        chances = self._chances(row)
        views = self.views.predict(frame).iloc[0]
        eng = self.engagement.predict(frame).iloc[0]
        matched = [p for p in self.pockets if p["lift"] and pocket_matches(p, row)]  # pockets without a lift carry no information
        matched.sort(key=lambda p: (p["evidencia"].startswith("explor"), -abs(np.log(p["lift"]))))
        return {"post": row, "chances": chances["atual"], "por_formato": chances["formatos"],
                "views": {"estimativa": views["views previstas"], "min": views["intervalo 90% inf"], "max": views["intervalo 90% sup"],
                          "modelo": views["modelo"], "melhor_que_media": self.views.beats_baseline},
                "engajamento": {"estimativa": eng["engajamento estimado"] * 100, "min": eng["intervalo 90% inf"] * 100,
                                "max": eng["intervalo 90% sup"] * 100, "modelo": eng["modelo"], "melhor_que_media": self.engagement.beats_baseline},
                "descobertas": [{**p, "evidencia_simples": EVIDENCE_PLAIN.get(p["evidencia"], p["evidencia"])} for p in matched[:MAX_POCKETS]],
                "descobertas_total": len(matched), "resumo": self._summary(row, chances["atual"], matched),
                "status": [{"metrica": c["metrica"], "status": status(c)} for c in chances["atual"]],
                "melhorias": self._improvements(row, chances), "sugestao": self.nearby_best(row, goal), "objetivo": goal,
                "mercado": market_check(frame)}

    def _metric_signals(self, row: dict) -> dict:
        return {m: self._signal(m, row["content_type"], row) for m in METRICS}

    def nearby_best(self, row: dict, goal: str = "qualquer") -> dict | None:
        """Closest better post: up to MAX_CHANGES changes (format, platform, theme, language) with the largest proven gain.

        A variant counts only if its history is clearly above normal (lower bound of the range above the base rate) for the
        target metric; ties prefer fewer changes. Returns None when no nearby variant is reliably better.
        """
        metrics = list(METRICS) if goal == "qualquer" else [goal]
        current = self._metric_signals(row)
        values = {f: [v for v in sorted(self.df[f].astype(str).unique()) if v != str(row[f])] for f in CHANGEABLE}
        best = None
        for n in range(1, MAX_CHANGES + 1):
            for fields in combinations(CHANGEABLE, n):
                for combo in _product([values[f] for f in fields]):
                    variant = {**row, **dict(zip(fields, combo))}
                    signals = self._metric_signals(variant)
                    for m in metrics:
                        alt, now = signals[m], current[m]
                        gain = alt["historico"] - now["historico"]
                        if alt["historico_min"] > alt["base"] and gain > 1 and (best is None or gain > best["ganho"] + 0.5):
                            best = {"mudancas": dict(zip(fields, combo)), "metrica": m, "de": now["historico"], "para": alt["historico"],
                                    "base": alt["base"], "para_min": alt["historico_min"], "para_max": alt["historico_max"], "ganho": gain,
                                    "evidencia": self._evidence({**row, **dict(zip(fields, combo))}, m)}
        return best

    def _evidence(self, variant: dict, metric: str) -> str:
        """Searching many variants finds some by luck: a suggestion is only 'confirmed' if a validated discovery backs it."""
        backing = [p["evidencia"] for p in self.pockets
                   if p["metrica"] == metric and (p["lift"] or 0) > 1 and not p["evidencia"].startswith("explor") and pocket_matches(p, variant)]
        if any(e.startswith("robusta") for e in backing):
            return "confirmado"
        return "se repetiu nos 2 anos" if backing else "pista"

    def _signal(self, metric: str, media: str, row: dict) -> dict:
        """History of similar posts (same platform · theme · language) for one metric and format."""
        seg = self.hits.segment_tables[(metric, media)]
        key = " · ".join(str(row[f]) for f in SEGMENT_FIELDS)
        low, high = seg.interval(key)
        return {"historico": seg.table_.get(key, seg.base_) * 100, "historico_min": low * 100, "historico_max": high * 100,
                "base": self.hits.base_rates[(metric, media)] * 100}

    def _improvements(self, row: dict, chances: dict) -> list[dict]:
        """Single changes (format, platform, theme or language) that raise a metric's chance clearly above normal."""
        current = {c["metrica"]: c for c in chances["atual"]}
        options = [("content_type", c["formato"], c["metrica"], c) for c in chances["formatos"] if c["formato"] != row["content_type"]]
        for field in SEGMENT_FIELDS:
            for value in sorted(self.df[field].astype(str).unique()):
                if value == str(row[field]):
                    continue
                for metric in METRICS:
                    options.append((field, value, metric, self._signal(metric, row["content_type"], {**row, field: value})))
        better = [{"campo": f, "valor": v, "metrica": m, "de": current[m]["historico"], "para": alt["historico"],
                   "ganho": alt["historico"] - current[m]["historico"]}
                  for f, v, m, alt in options if alt["historico_min"] > alt["base"] and alt["historico"] > current[m]["historico"] + 1]
        better.sort(key=lambda b: -b["ganho"])
        seen, out = set(), []
        for b in better:  # one suggestion per (field, value)
            if (b["campo"], b["valor"]) not in seen:
                seen.add((b["campo"], b["valor"]))
                out.append(b)
        return out[:MAX_IMPROVEMENTS]

    def _chances(self, row: dict) -> dict:
        """Chance of top 5% per metric for the chosen format and for every other format."""
        formats = sorted(self.df["content_type"].unique())
        frame = pd.DataFrame([{**row, "content_type": f} for f in formats])
        pred = self.hits.predict(frame)
        out = []
        for _, r in pred.iterrows():
            low, high = (float(x) for x in r["segmento IC90 (%)"].split("–"))
            out.append({"formato": r["formato"], "metrica": r["métrica"], "chance": r["chance top 5% (%)"], "base": r["base (%)"],
                        "modelo": r["modelo"], "historico": r["sinal do segmento (%)"], "historico_min": low, "historico_max": high,
                        "posts_parecidos": r["posts no segmento"]})
        return {"atual": [c for c in out if c["formato"] == row["content_type"]], "formatos": out}

    def _summary(self, row: dict, chances: list[dict], matched: list[dict]) -> list[str]:
        """Plain-language sentences for the result card."""
        lines = []
        for c in chances:
            ratio = c["historico"] / c["base"] if c["base"] else 1
            name = METRICS[c["metrica"]]
            if c["historico_min"] > c["base"]:
                lines.append(f"Posts parecidos com este ({c['posts_parecidos']} no histórico) entraram no top 5% de {name} "
                             f"{_ratio(ratio)} mais que o normal. Vale priorizar.")
            elif c["historico_max"] < c["base"]:
                lines.append(f"Posts parecidos com este ficaram abaixo do normal em {name} ({_ratio(ratio)}). Considere outro formato ou idioma.")
        if not lines:
            lines.append("Para este perfil de post, o histórico não mostra vantagem nem desvantagem: a chance de top 5% fica na média (~5%).")
        strong = [p for p in matched if not p["evidencia"].startswith("explor")]
        if strong:
            lines.append(f"{len(strong)} padrão(ões) que se repetiram nos dois anos se aplicam a este post. Veja abaixo.")
        return lines
