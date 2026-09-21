"""Backtest walk-forward por snapshot: o score é útil quando aplicado no passado sem enxergar o futuro?

Para cada data t:
1. calibra a chance só com snapshots cujo horizonte terminou antes de t (calibration.py);
2. reconstrói o pipeline em Engaging aberto em t e pontua. A fatia Prospecting não é
   reconstruível em datas passadas (não há data de criação) e fica fora;
3. observa os 90 dias seguintes: ganhou, perdeu ou continuou aberto.

Datas principais espaçadas pelo horizonte (30/06 e 30/09), para que os desfechos não se
sobreponham; 31/07 e 31/08 entram como leitura de estabilidade, e o documento diz quantos
ganhos se repetem entre datas.

Métricas:
- win rate por faixa de score;
- captura do valor ganho pelo top-N: score vs. só preço no mesmo conjunto vs. só preço no
  pipeline inteiro (inclui deals além de 138 dias) vs. proporção aleatória;
- chance prevista vs. observada por faixa de idade, com as faixas agrupadas ou sem suporte
  declaradas por data;
- categorias: primeiras duas semanas vs. mais velhos; Focar agora; última janela;
- bloco "Confirmar se está vivo": nesta base, por construção, nenhum deal aberto com mais de
  138 dias fecha depois (nenhum ciclo concluído passa de 138). A tabela mostra quantos deals
  estavam nessa situação em cada data; isso descreve a base, não valida o método.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .calibration import AGE_BANDS, HORIZON_DAYS, calibrate
from .scoring import CAT_ALIVE, CAT_CRITICAL, CAT_FOCUS, CAT_LAST, SUPPORT_OK, SUPPORT_THIN, score_pipeline

PRIMARY_SNAPSHOTS = ("2017-06-30", "2017-09-30")
STABILITY_SNAPSHOTS = ("2017-07-31", "2017-08-31")
DEFAULT_SNAPSHOTS = ("2017-06-30", "2017-07-31", "2017-08-31", "2017-09-30")


def _capture(ok: pd.DataFrame, full: pd.DataFrame) -> dict:
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


def _by_score_band(ok: pd.DataFrame) -> dict:
    b = pd.cut(ok["score"], bins=[-1, 20, 40, 60, 80, 100], labels=["0-20", "21-40", "41-60", "61-80", "81-100"])
    g = ok.groupby(b, observed=True).agg(n=("won_h", "size"), win_rate=("won_h", "mean"), won_value=("won_value_h", "sum"))
    return {str(k): {"n": int(r["n"]), "win_rate": round(float(r["win_rate"]), 3), "won_value": round(float(r["won_value"]))} for k, r in g.iterrows()}


def snapshot(enriched: pd.DataFrame, t: pd.Timestamp, horizon_days: int = HORIZON_DAYS) -> dict:
    cal = calibrate(enriched, t, horizon_days)
    scored, _ = score_pipeline(enriched, t, cal, include_prospecting=False)
    end = t + pd.Timedelta(days=horizon_days)
    s = scored.assign(won_h=(scored["deal_stage"] == "Won") & (scored["close_date"] <= end),
                      closed_h=scored["deal_stage"].isin(("Won", "Lost")) & (scored["close_date"] <= end))
    s["won_value_h"] = np.where(s["won_h"], s["close_value"].fillna(0.0), 0.0)
    ok = s[s["support"] == SUPPORT_OK].copy()
    res: dict = {
        "as_of": str(t.date()), "horizon_days": horizon_days, "primary": str(t.date()) in PRIMARY_SNAPSHOTS,
        "calibration_mode": cal.mode, "calibration_snapshots": list(cal.snapshots), "calibration_deals": cal.n_deals, "calibration_obs": cal.n_obs,
        "p_by_band": {k: (None if v is None else round(v, 3)) for k, v in cal.p_by_band.items()},
        "pooled_bands": dict(cal.pooled_from), "unsupported_bands": [k for k, v in cal.p_by_band.items() if v is None],
        "open_engaging_at_t": int(len(s)), "scoreable": int(len(ok)), "thin": int((s["support"] == SUPPORT_THIN).sum()),
        "won_in_horizon": int(s["won_h"].sum()), "won_value_in_horizon": float(s["won_value_h"].sum()),
        "won_ids": sorted(s.loc[s["won_h"], "opportunity_id"].tolist()),
    }
    if len(ok):
        res["win_rate_scoreable"] = round(float(ok["won_h"].mean()), 3)
        res["by_score_band"] = _by_score_band(ok)
        res["value_capture"] = _capture(ok, s)
        g = ok.groupby("age_band", observed=True).agg(n=("won_h", "size"), predicted=("p_win", "mean"), observed=("won_h", "mean"), observed_close=("closed_h", "mean"))
        res["calibration_check"] = {str(k): {"n": int(r["n"]), "predicted": round(float(r["predicted"]), 3), "observed": round(float(r["observed"]), 3), "observed_close": round(float(r["observed_close"]), 3)} for k, r in g.iterrows()}
        crit = ok[ok["category"] == CAT_CRITICAL]; older = ok[(ok["age_days"] > 14) & (ok["age_days"] <= 90)]; last = s[s["category"] == CAT_LAST]
        res["categories"] = {
            "critical": {"n": int(len(crit)), "win_rate": round(float(crit["won_h"].mean()), 3) if len(crit) else None},
            "days_15_90": {"n": int(len(older)), "win_rate": round(float(older["won_h"].mean()), 3) if len(older) else None},
            "last_window": {"n": int(len(last)), "win_rate": round(float(last["won_h"].mean()), 3) if len(last) else None, "close_rate": round(float(last["closed_h"].mean()), 3) if len(last) else None},
        }
        focus = ok[ok["category"] == CAT_FOCUS]; total = float(s["won_value_h"].sum())
        res["categories"]["focus"] = {"n": int(len(focus)), "share_of_deals": round(len(focus) / len(ok), 3), "win_rate": round(float(focus["won_h"].mean()), 3) if len(focus) else None,
                                      "share_of_won_value": round(float(focus["won_value_h"].sum() / total), 3) if total else None}
    alive = s[s["category"] == CAT_ALIVE]
    res["alive_block"] = {"n": int(len(alive)), "list_value": float(alive["list_value"].sum()), "won_later": int((alive["deal_stage"] == "Won").sum()),
                          "lost_later": int((alive["deal_stage"] == "Lost").sum()), "still_open_at_end": int(alive["deal_stage"].isin(("Prospecting", "Engaging")).sum())}
    return res


def run_backtest(enriched: pd.DataFrame, dates=DEFAULT_SNAPSHOTS, horizon_days: int = HORIZON_DAYS) -> dict:
    results = [snapshot(enriched, pd.Timestamp(d), horizon_days) for d in dates]
    all_ids = [i for r in results for i in r["won_ids"]]
    overlap = {"won_counted_total": len(all_ids), "won_unique": len(set(all_ids)), "won_in_2_or_more_dates": int(sum(1 for c in pd.Series(all_ids).value_counts() if c >= 2))}
    for r in results:
        r.pop("won_ids", None)
    return {"results": results, "overlap": overlap, "primary_dates": list(PRIMARY_SNAPSHOTS), "stability_dates": list(STABILITY_SNAPSHOTS)}


def _pct(x) -> str:
    return "-" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.0%}"


def to_markdown(bt: dict) -> str:
    results = bt["results"]; ov = bt["overlap"]
    L = ["# Backtest walk-forward por snapshot", "",
         "Em cada data, a chance é calibrada só com snapshots cujo horizonte de 90 dias terminou antes da data; o pipeline em Engaging aberto naquele dia é pontuado e observam-se os 90 dias seguintes. "
         f"Datas principais, sem sobreposição de desfechos: {', '.join(bt['primary_dates'])}. Datas de estabilidade: {', '.join(bt['stability_dates'])}. "
         f"Nas quatro datas juntas, {ov['won_counted_total']} ganhos contados correspondem a {ov['won_unique']} deals únicos; {ov['won_in_2_or_more_dates']} aparecem em duas ou mais datas. "
         "A fatia Prospecting não é reconstruível em datas passadas e fica fora.", ""]
    L += ["| Data | Tipo | Snapshots de calibração | Deals / observações | Faixas agrupadas | Sem suporte | Engaging em t | Com score | Ganhos em 90 d | Valor ganho |", "|---|---|---|---|---|---|---:|---:|---:|---:|"]
    for r in results:
        L.append(f"| {r['as_of']} | {'principal' if r['primary'] else 'estabilidade'} | {', '.join(r['calibration_snapshots']) or r['calibration_mode']} | {r['calibration_deals']:,} / {r['calibration_obs']:,} | "
                 f"{', '.join(f'{k}→{v}' for k, v in r['pooled_bands'].items()) or 'nenhuma'} | {', '.join(r['unsupported_bands']) or 'nenhuma'} | {r['open_engaging_at_t']:,} | {r['scoreable']:,} | {r['won_in_horizon']:,} | {r['won_value_in_horizon']:,.0f} |")
    L += ["", "## Win rate em 90 dias por faixa de score", "", "| Data | Com score | 0-20 | 21-40 | 41-60 | 61-80 | 81-100 |", "|---|---:|---|---|---|---|---|"]
    for r in results:
        b = r.get("by_score_band", {})
        cell = lambda k: f"{b[k]['win_rate']:.0%} (n={b[k]['n']})" if k in b else "-"
        L.append(f"| {r['as_of']} | {r['scoreable']} | {cell('0-20')} | {cell('21-40')} | {cell('41-60')} | {cell('61-80')} | {cell('81-100')} |")
    L += ["", "## Captura do valor ganho em 90 dias pelo top-N (denominador: todo o Engaging aberto em t, inclusive além de 138 dias)", "",
          "| Data | N | Score | Só preço, no mesmo conjunto do score | Só preço, no pipeline inteiro | Aleatório |", "|---|---:|---:|---:|---:|---:|"]
    for r in results:
        for n, v in r.get("value_capture", {}).items():
            L.append(f"| {r['as_of']} | {n} | {_pct(v['score'])} | {_pct(v['list_price_scoreable'])} | {_pct(v['list_price_all_open'])} | {_pct(v['random_expectation'])} |")
    L += ["", "## Chance prevista vs. observada por faixa de idade (ganhar em 90 d; fechar em 90 d)", "", "| Data | Faixa | n | Prevista | Observada | Fechou (ganho ou perda) |", "|---|---|---:|---:|---:|---:|"]
    for r in results:
        for _lo, _hi, name in AGE_BANDS:
            v = r.get("calibration_check", {}).get(name)
            if v:
                L.append(f"| {r['as_of']} | {name} | {v['n']} | {_pct(v['predicted'])} | {_pct(v['observed'])} | {_pct(v['observed_close'])} |")
    L += ["", "## Categorias", "", "| Data | Primeiras 2 semanas: n / win 90 d | 15-90 dias: n / win 90 d | Última janela (91-138): n / win 90 d / fechou | Focar agora: n (% dos com score) / win 90 d / % do valor ganho |", "|---|---|---|---|---|"]
    for r in results:
        c = r.get("categories", {})
        cr, o, lw, f = c.get("critical", {}), c.get("days_15_90", {}), c.get("last_window", {}), c.get("focus", {})
        L.append(f"| {r['as_of']} | {cr.get('n', 0)} / {_pct(cr.get('win_rate'))} | {o.get('n', 0)} / {_pct(o.get('win_rate'))} | {lw.get('n', 0)} / {_pct(lw.get('win_rate'))} / {_pct(lw.get('close_rate'))} | {f.get('n', 0)} ({_pct(f.get('share_of_deals'))}) / {_pct(f.get('win_rate'))} / {_pct(f.get('share_of_won_value'))} |")
    L += ["", "## Bloco \"Confirmar se está vivo\" (mais de 138 dias em t)", "",
          "Nesta base nenhum ciclo concluído passa de 138 dias, então um deal aberto há mais de 138 dias não pode ter fechado depois: a coluna de fechamentos é zero por construção. O que a tabela informa é o tamanho do bloco em cada data.", "",
          "| Data | n | Valor de lista | Ganhou depois | Perdeu depois | Ainda aberto no fim da base |", "|---|---:|---:|---:|---:|---:|"]
    for r in results:
        a = r["alive_block"]
        L.append(f"| {r['as_of']} | {a['n']} | {a['list_value']:,.0f} | {a['won_later']} | {a['lost_later']} | {a['still_open_at_end']} |")
    return "\n".join(L) + "\n"
