"""Backtest walk-forward por snapshot: o score é útil quando aplicado no passado sem enxergar o futuro?

Para cada data t:
1. calibra a chance só com snapshots cujo horizonte terminou antes de t (calibration.py);
2. reconstrói o pipeline aberto em t e pontua;
3. observa os 90 dias seguintes: ganhou, perdeu ou continuou aberto.

Métricas:
- win rate por faixa de score (o score ordena a chance?);
- captura de valor: quanto do valor ganho no horizonte estava no top-N do score, contra
  ordenar só por preço de lista e contra a proporção aleatória (o score ajuda a escolher?);
- validação das categorias: "Confirmar se está vivo" fechou depois? primeiras duas semanas
  ganharam menos que os mais velhos?
Tudo é reportado em duas visões: todos os deals com chance estimável e só os com conta
cadastrada (a diferença mede o peso da higiene de cadastro).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .calibration import HORIZON_DAYS, calibrate
from .scoring import CAT_ALIVE, CAT_CRITICAL, CAT_FOCUS, SUPPORT_OK, score_pipeline

DEFAULT_SNAPSHOTS = ("2017-06-30", "2017-07-31", "2017-08-31", "2017-09-30")


def _capture(ok: pd.DataFrame, full: pd.DataFrame) -> dict:
    """Quanto do valor ganho em 90 d no pipeline aberto (full) o top-N captura.

    - score: top-N pelo score (só deals com chance estimável);
    - list_price_scoreable: top-N por preço dentro do mesmo conjunto do score (isola o efeito da chance);
    - list_price_all_open: top-N por preço no pipeline aberto inteiro, como um vendedor faria sem a
      ferramenta (inclui deals além de 138 dias e em prospecção);
    - random_expectation: proporção n / pipeline aberto.
    Denominador único: todo o valor ganho em 90 d no pipeline aberto em t.
    """
    total = float(full["won_value_h"].sum())
    out = {}
    for n in (10, 30, 50, 100):
        n_ok = min(n, len(ok)); n_full = min(n, len(full))
        out[str(n)] = {
            "score": round(float(ok.nlargest(n_ok, "score")["won_value_h"].sum() / total), 3) if total else None,
            "list_price_scoreable": round(float(ok.nlargest(n_ok, "list_value")["won_value_h"].sum() / total), 3) if total else None,
            "list_price_all_open": round(float(full.nlargest(n_full, "list_value")["won_value_h"].sum() / total), 3) if total else None,
            "random_expectation": round(n_full / len(full), 3) if len(full) else None,
        }
    return out


def _by_band(ok: pd.DataFrame) -> dict:
    b = pd.cut(ok["score"], bins=[-1, 20, 40, 60, 80, 100], labels=["0-20", "21-40", "41-60", "61-80", "81-100"])
    g = ok.groupby(b, observed=True).agg(n=("won_h", "size"), win_rate=("won_h", "mean"), won_value=("won_value_h", "sum"))
    return {str(k): {"n": int(r["n"]), "win_rate": round(float(r["win_rate"]), 3), "won_value": round(float(r["won_value"]))} for k, r in g.iterrows()}


def snapshot(enriched: pd.DataFrame, t: pd.Timestamp, horizon_days: int = HORIZON_DAYS) -> dict:
    cal = calibrate(enriched, t, horizon_days)
    scored, _ = score_pipeline(enriched, t, cal)
    end = t + pd.Timedelta(days=horizon_days)
    s = scored.assign(won_h=(scored["deal_stage"] == "Won") & (scored["close_date"] <= end),
                      lost_h=(scored["deal_stage"] == "Lost") & (scored["close_date"] <= end))
    s["won_value_h"] = np.where(s["won_h"], s["close_value"].fillna(0.0), 0.0)
    res: dict = {"as_of": str(t.date()), "horizon_days": horizon_days, "calibration_mode": cal.mode, "calibration_snapshots": list(cal.snapshots),
                 "calibration_rows": cal.n_rows, "p_by_band": {k: round(v, 3) for k, v in cal.p_by_band.items()},
                 "open_at_t": int(len(s)), "won_in_horizon": int(s["won_h"].sum()), "won_value_in_horizon": float(s["won_value_h"].sum())}
    for label, sub, full in (("all", s[s["support"] == SUPPORT_OK], s), ("with_account", s[(s["support"] == SUPPORT_OK) & ~s["needs_account"]], s[~s["needs_account"]])):
        sub = sub.copy()
        block = {"n": int(len(sub)), "n_open": int(len(full)), "win_rate": round(float(sub["won_h"].mean()), 3) if len(sub) else None}
        if len(sub):
            block["by_score_band"] = _by_band(sub)
            block["value_capture"] = _capture(sub, full)
            crit = sub[sub["category"] == CAT_CRITICAL]; older = sub[sub["age_days"] > 14]
            block["critical_window"] = {"n": int(len(crit)), "win_rate": round(float(crit["won_h"].mean()), 3) if len(crit) else None,
                                        "n_older": int(len(older)), "win_rate_older": round(float(older["won_h"].mean()), 3) if len(older) else None}
            focus = sub[sub["category"] == CAT_FOCUS]; total = float(sub["won_value_h"].sum())
            block["focus"] = {"n": int(len(focus)), "win_rate": round(float(focus["won_h"].mean()), 3) if len(focus) else None,
                              "share_of_won_value": round(float(focus["won_value_h"].sum() / total), 3) if total else None,
                              "share_of_deals": round(len(focus) / len(sub), 3)}
            # calibração: chance prevista média vs. observada, por faixa de idade
            g = sub.groupby("age_band", observed=True).agg(n=("won_h", "size"), predicted=("p_win", "mean"), observed=("won_h", "mean"))
            block["calibration_check"] = {str(k): {"n": int(r["n"]), "predicted": round(float(r["predicted"]), 3), "observed": round(float(r["observed"]), 3)} for k, r in g.iterrows()}
        res[label] = block
    alive = s[s["category"] == CAT_ALIVE]
    res["alive_check"] = {"n": int(len(alive)), "won_later_any_time": int((alive["deal_stage"] == "Won").sum()), "lost_later_any_time": int((alive["deal_stage"] == "Lost").sum()),
                          "still_open_at_end": int(alive["deal_stage"].isin(("Prospecting", "Engaging")).sum())}
    return res


def run_backtest(enriched: pd.DataFrame, dates=DEFAULT_SNAPSHOTS, horizon_days: int = HORIZON_DAYS) -> list[dict]:
    return [snapshot(enriched, pd.Timestamp(d), horizon_days) for d in dates]


def _pct(x) -> str:
    return "-" if x is None else f"{x:.0%}"


def to_markdown(results: list[dict]) -> str:
    L = ["# Backtest walk-forward por snapshot", "",
         "Para cada data, a chance é calibrada só com snapshots cujo horizonte de 90 dias terminou antes da data; o pipeline aberto naquele dia é pontuado e observam-se os 90 dias seguintes. Duas visões: todos os deals com chance estimável e só os com conta cadastrada.", ""]
    L += ["| Data | Snapshots de calibração | Linhas | Abertos em t | Ganhos em 90 d | Valor ganho |", "|---|---|---:|---:|---:|---:|"]
    for r in results:
        L.append(f"| {r['as_of']} | {', '.join(r['calibration_snapshots']) or r['calibration_mode']} | {r['calibration_rows']:,} | {r['open_at_t']:,} | {r['won_in_horizon']:,} | {r['won_value_in_horizon']:,.0f} |")
    for label, title in (("with_account", "Deals com conta cadastrada"), ("all", "Todos os deals com chance estimável")):
        L += ["", f"## {title}", "", "### Win rate em 90 d por faixa de score", "", "| Data | n | 0-20 | 21-40 | 41-60 | 61-80 | 81-100 |", "|---|---:|---|---|---|---|---|"]
        for r in results:
            b = r[label].get("by_score_band", {})
            cell = lambda k: f"{b[k]['win_rate']:.0%} (n={b[k]['n']})" if k in b else "-"
            L.append(f"| {r['as_of']} | {r[label]['n']} | {cell('0-20')} | {cell('21-40')} | {cell('41-60')} | {cell('61-80')} | {cell('81-100')} |")
        L += ["", "### Captura do valor ganho em 90 d pelo top-N (denominador: todo o pipeline aberto em t)", "",
              "| Data | N | Score | Só preço, no mesmo conjunto do score | Só preço, no pipeline inteiro (sem a ferramenta) | Aleatório |", "|---|---:|---:|---:|---:|---:|"]
        for r in results:
            for n, v in r[label].get("value_capture", {}).items():
                L.append(f"| {r['as_of']} | {n} | {_pct(v['score'])} | {_pct(v['list_price_scoreable'])} | {_pct(v['list_price_all_open'])} | {_pct(v['random_expectation'])} |")
        L += ["", "### Chance prevista vs. observada por faixa de idade", "", "| Data | Faixa | n | Prevista | Observada |", "|---|---|---:|---:|---:|"]
        for r in results:
            for k, v in r[label].get("calibration_check", {}).items():
                L.append(f"| {r['as_of']} | {k} | {v['n']} | {_pct(v['predicted'])} | {_pct(v['observed'])} |")
        L += ["", "### Categorias", "", "| Data | Primeiras 2 semanas: n / win rate | Mais de 14 d: n / win rate | Focar agora: n (% dos deals) / win rate / % do valor ganho |", "|---|---|---|---|"]
        for r in results:
            c = r[label].get("critical_window", {}); f = r[label].get("focus", {})
            L.append(f"| {r['as_of']} | {c.get('n', 0)} / {_pct(c.get('win_rate'))} | {c.get('n_older', 0)} / {_pct(c.get('win_rate_older'))} | {f.get('n', 0)} ({_pct(f.get('share_of_deals'))}) / {_pct(f.get('win_rate'))} / {_pct(f.get('share_of_won_value'))} |")
    L += ["", "## Bloco \"Confirmar se está vivo\" (mais de 138 dias em t)", "", "| Data | n | Ganhou depois (qualquer data) | Perdeu depois | Ainda aberto no fim da base |", "|---|---:|---:|---:|---:|"]
    for r in results:
        a = r["alive_check"]
        L.append(f"| {r['as_of']} | {a['n']} | {a['won_later_any_time']} | {a['lost_later_any_time']} | {a['still_open_at_end']} |")
    return "\n".join(L) + "\n"
