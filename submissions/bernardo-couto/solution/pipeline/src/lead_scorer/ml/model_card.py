"""Model card generator (pt-BR) from ``metrics.json`` + ``training_manifest.json`` content."""

from __future__ import annotations

from typing import Any


def _pct(x: Any) -> str:
    return "—" if x is None else f"{float(x) * 100:.0f}%"


def _num(x: Any, digits: int = 3) -> str:
    return "—" if x is None else f"{float(x):.{digits}f}".replace(".", ",")


def _ci(ci: Any) -> str:
    if not ci:
        return ""
    return f" [{_num(ci[0])}; {_num(ci[1])}]"


def _brl(x: Any) -> str:
    return "—" if x is None else "R$ " + f"{float(x):,.0f}".replace(",", ".")


_BASELINE_LABELS = {
    "random": "aleatório",
    "price": "maior preço primeiro",
    "price_alive": "maior preço primeiro, excluindo parados (> 138 d)",
    "newest": "mais novo primeiro",
    "oldest": "mais antigo primeiro",
    "base_rate": "taxa-base por produto",
}


def _backtest_table(metrics: dict[str, Any], cut: str) -> str:
    rows = [
        "| Critério | AUC-PR [IC95] | AUC-ROC | Brier | Lift top 10% | P@10/vendedor [IC95] | "
        "Receita top 20% [IC95] |",
        "|---|---|---|---|---|---|---|",
    ]

    def line(label: str, r: dict[str, Any]) -> str:
        return (
            f"| {label} | {_num(r['auc_pr'])}{_ci(r.get('auc_pr_ci'))} | {_num(r['auc_roc'])} | "
            f"{_num(r.get('brier'))} | {_num(r['lift_top_decile'], 2)} | "
            f"{_num(r['precision_at_10'])}{_ci(r.get('precision_at_10_ci'))} | "
            f"{_num(r['revenue_capture_top20'])}{_ci(r.get('revenue_capture_top20_ci'))} |"
        )

    for name, label in _BASELINE_LABELS.items():
        rows.append(line(label, metrics["baselines"][name][cut]))
    for signal, label in (
        ("p_win", "regras · p_win"),
        ("expected_value", "regras · valor esperado"),
        ("priority_score", "**regras · priority_score (o que o vendedor vê)**"),
    ):
        rows.append(line(label, metrics["by_signal"][signal][cut]))
    shadow = metrics.get("shadow_model", {}).get(cut)
    if shadow:
        rows.append(line("modelo sombra · LR calibrada (peso 0 no score)", shadow))
    return "\n".join(rows)


def _horizon_table(metrics: dict[str, Any], cut: str) -> str:
    rows = [
        "| Critério | R$ 14 d · top 20% (share) | R$ 14 d · top 10/vendedor (share) | "
        "R$ 30 d · top 20% (share) | R$ 30 d · top 10/vendedor (share) |",
        "|---|---|---|---|---|",
    ]

    def cell(r: dict[str, Any], key: str) -> str:
        if key not in r:
            return "—"
        return f"{_brl(r[key])} ({_pct(r.get(key + '_share'))})"

    def line(label: str, r: dict[str, Any]) -> str:
        return (
            f"| {label} | {cell(r, 'revenue_14d_top20')} | {cell(r, 'revenue_14d_top10_agent')} | "
            f"{cell(r, 'revenue_30d_top20')} | {cell(r, 'revenue_30d_top10_agent')} |"
        )

    for name, label in _BASELINE_LABELS.items():
        rows.append(line(label, metrics["baselines"][name][cut]))
    rows.append(line("**regras · priority_score**", metrics["by_signal"]["priority_score"][cut]))
    shadow = metrics.get("shadow_model", {}).get(cut)
    if shadow:
        rows.append(line("modelo sombra", shadow))
    return "\n".join(rows)


def _calibration_table(bins: list[dict[str, Any]]) -> str:
    rows = ["| Bin | n | p_win previsto | taxa real | gap |", "|---|---|---|---|---|"]
    for b in bins:
        rows.append(
            f"| {b['bin']} | {b['count']} | {_num(b['predicted'])} | {_num(b['actual'])} | "
            f"{_num(b['actual'] - b['predicted'])} |"
        )
    return "\n".join(rows)


def render_model_card(metrics: dict[str, Any], manifest: dict[str, Any]) -> str:
    version = metrics["model_version"]
    as_of = metrics["as_of"]
    summary = metrics["summary"]
    promo = metrics["promotion"]
    acceptance = metrics["acceptance"]
    w = manifest["weights"]
    cuts = metrics["cuts"]

    parts: list[str] = [
        f"# Model card — `{version}`",
        "",
        f"**Data de referência dos dados:** {as_of} · **Gerado pelo job** `train` "
        f"(git `{manifest.get('git_sha', '?')}`, Spark {manifest.get('spark_version', '?')}) · "
        f"**Duração:** {manifest.get('duration_seconds', '?')} s",
        "",
        "## 1. O que este artefato é",
        "",
        "Duas camadas. **Camada 1 (regras)** produz o score que o vendedor vê: "
        f"`priority_score = {w['w_p']:.0f}·p̂ + {w['w_v']:.0f}·valor + {w['w_u']:.0f}·urgência`, "
        "com `p_win` = taxa histórica de Won do produto (suavizada, prior "
        f"a={w['prior_a']:.0f}) × {w['zombie_p_factor']} se o deal passou de "
        f"{w['zombie_days']} dias em Engaging; valor = `log1p(preço × razão histórica)` "
        "normalizado; urgência = hazard empírico de Won nos próximos 14 dias dado a idade. "
        "**Camada 2 (modelo)** é uma regressão logística Spark ML treinada em frame temporal, "
        f"em **modo sombra**: peso `{promo['blend_model_weight']}` no blend. "
        + (
            "Ela foi promovida e ajusta o `p_win`."
            if promo["promoted"]
            else "Ela **não** altera nenhum score; suas métricas são registradas para decidir a "
            "promoção em versões futuras."
        ),
        "",
        "## 2. Dados e janela",
        "",
        f"- Fonte: CRM (snapshot {manifest['snapshot_date']}), tabelas gold "
        "`opportunity_features`, `history_stats` e `labels` particionadas por `as_of` "
        "(só informação conhecida em `as_of`).",
        "- Frame de treino do modelo sombra final: meses "
        f"{', '.join(manifest['frame']['months'])}; "
        f"{manifest['frame']['counts'].get('train_rows', 0):.0f} linhas de treino, "
        f"{manifest['frame']['counts'].get('calibration_rows', 0):.0f} no mês de calibração "
        f"({manifest['frame']['calibration_month']}); taxa de Won no treino "
        f"{_pct(manifest['frame']['counts'].get('train_positive_rate'))}.",
        f"- Cortes de backtest: {', '.join(cuts)} (walk-forward: histórico ≤ T, desfecho > T).",
        "- Nenhum `randomSplit`/`CrossValidator`; nenhum `close_value`/`close_date` fora de "
        "história e avaliação; nenhum relógio real.",
        "",
        "## 3. Features (lista fechada)",
        "",
        "Camada 2: `" + "`, `".join(manifest["features"]) + "`. "
        "Proibidas (e testadas): tudo da conta (`account_*`, setor, porte), `engage_month`, "
        "desfechos. Motivo: 100% dos deals fechados têm conta contra 32% dos abertos — "
        '`account_known` codifica "já fechou", não "vai fechar".',
        "",
        "Coeficientes padronizados da LR final (contribuição = coef × valor padronizado):",
        "",
        "| Feature | Coeficiente |",
        "|---|---|",
    ]
    for name, coef in manifest.get("coefficients", {}).items():
        parts.append(f"| `{name}` | {_num(coef)} |")

    parts += [
        "",
        "## 4. Resultado no snapshot",
        "",
        f"- {summary['coverage']} deals abertos pontuados ({summary['prospecting_count']} em "
        f"Prospecting); {summary['zombie_count']} acima de {w['zombie_days']} dias "
        f"({_brl(summary.get('zombie_nominal_value'))} nominais em preço de tabela, fora do "
        "forecast — mesma definição do resumo da API; multiplicando pela razão histórica "
        "close_value/preço do produto seriam "
        f"{_brl(summary.get('zombie_nominal_value_ratio_adjusted'))}).",
        f"- Concentração do top 5 de cada vendedor na faixa 120–138 dias: "
        f"{_pct(summary.get('top5_agent_share_120_138'))}. É efeito do hazard (a chance de "
        "desfecho em 14 dias é maior perto do fim do ciclo), não evidência de que deal velho "
        "fecha mais — fora do tempo, idade não previu fechamento.",
        f"- Conta conhecida em {_pct(summary['account_known_rate'])} dos deals.",
        "- Tiers: "
        + ", ".join(f"{k}={v}" for k, v in sorted(summary.get("tier_counts", {}).items()))
        + "; confiança: "
        + ", ".join(f"{k}={v}" for k, v in summary.get("confidence_counts", {}).items())
        + ".",
        f"- Spearman(priority_score, preço) = {_num(summary['spearman_score_price'], 2)} "
        '(limite do projeto: < 0,90 — não é "ordenar por preço").',
        "",
        "## 5. Backtest temporal vs. baselines",
        "",
        "Métricas probabilísticas (Brier, AUC-PR, calibração) usam `p_win`; métricas de "
        "ranking (P@10 por vendedor, receita capturada no top 20%) usam `priority_score`, que é "
        "o que o vendedor vê. Bootstrap pareado, 2.000 reamostras, semente fixa.",
        "",
    ]
    for cut in cuts:
        b = metrics["backtest"][cut]
        parts += [
            f"### Corte T = {cut}",
            "",
            f"Abertos em T: {b['n_open']} · com desfecho até o snapshot: {b['n_labeled']} "
            f"(taxa-base {_num(b['base_rate'])}) · censurados: {b['n_censored']} · "
            f"parados (> {w['zombie_days']} d) em T: {b['zombies_at_cut']}, dos quais "
            f"fecharam depois: **{b['zombies_closed_after']}** · "
            f"Spearman(score, preço) = {_num(b['spearman_score_price'], 2)}",
            "",
            _backtest_table(metrics, cut),
            "",
            "Receita realizada logo após o corte (Won fechados em 14 / 30 dias) capturada no "
            "top 20% e no top 10 de cada vendedor — o que o time colheria seguindo a lista:",
            "",
            _horizon_table(metrics, cut),
            "",
            f"Concentração do top 5 por vendedor em 120–138 dias neste corte: "
            f"{_pct(b.get('top5_agent_share_120_138'))} (efeito do hazard, ver §4).",
            "",
            f"Calibração de `p_win` (erro médio absoluto {_num(b['mean_calibration_error'])}):",
            "",
            _calibration_table(b["calibration_bins"]),
            "",
        ]

    parts += [
        "**Leitura honesta.** Nenhum critério — nem as regras, nem o modelo — acerta *quem* vai "
        "fechar melhor que o acaso (AUC-ROC ≈ 0,5, IC95 do AUC-PR sobreposto ao aleatório). O "
        "ganho está em **valor** (receita capturada no top 20% ≈ 1,7–1,8× o aleatório), em "
        "**momento** (hazard por idade) e na **limpeza** dos deals parados, que nunca fecharam.",
        "",
        'Sensibilidade pessimista (censurados tratados como Lost): "mais novo primeiro" sobe para '
        "AUC-ROC "
        + ", ".join(_num(metrics["pessimistic"][c]["newest"]["auc_roc"], 2) for c in cuts)
        + " **por causa dos zumbis** (deal antigo e ainda aberto = nunca fechou), não por prever "
        "fechamento.",
        "",
        "## 6. Modelo sombra e regra de promoção",
        "",
        f"Regra: {promo['rule']}.",
        "",
        "| Corte | AUC-PR modelo | AUC-PR taxa-base | Brier modelo | Brier taxa-base | Passou |",
        "|---|---|---|---|---|---|",
    ]
    for c in promo.get("criteria", []):
        parts.append(
            f"| {c['cut']} | {_num(c['auc_pr_model'])} | {_num(c['auc_pr_base'])} | "
            f"{_num(c['brier_model'])} | {_num(c['brier_base'])} | "
            f"{'sim' if c['passed'] else 'não'} |"
        )
    parts += [
        "",
        f"**Decisão:** {'promovido' if promo['promoted'] else 'mantido em sombra'} "
        f"(`blend_model_weight = {promo['blend_model_weight']}`).",
        "",
        "Viés conhecido do frame: meses recentes só têm deals que fecharam rápido, logo a taxa de "
        "Won do treino é maior que a fora do tempo; a calibração isotônica no último mês do frame "
        "corrige parte disso. Reponderação temporal fica como questão aberta.",
        "",
        "## 7. Aceite (spec §7)",
        "",
        "| Verificação | Corte | Valor | Passou |",
        "|---|---|---|---|",
    ]
    for cut, checks in acceptance["by_cut"].items():
        for c in checks:
            parts.append(
                f"| {c['check']} | {cut} | {c['value']} | {'sim' if c['passed'] else 'não'} |"
            )
    parts += [
        "",
        f"**Resultado:** {'todos os limiares atendidos' if acceptance['passed'] else 'FALHOU'}.",
        "",
        "## 8. Monitoramento",
        "",
        "- O job `score` grava no `_manifest.json` da partição o PSI de cada feature contra a "
        "distribuição do frame de treino (referência em `training_manifest.json`) e alerta se "
        "PSI > 0,2. Esperar alarme em `account_known` se alguém o incluir: é o sintoma do "
        "vazamento descrito em §3, não drift real.",
        "- Cobertura de conta (`account_known_rate`) e distribuição de tiers/confiança por lote.",
        "- Feedback do vendedor (`POST /api/v1/feedback`) alimenta `data/feedback/actions` para, "
        f"num ciclo futuro, calibrar o fator {w['zombie_p_factor']} dos deals parados.",
        "",
        "## 9. Limitações e uso pretendido",
        "",
        '- **Uso:** ordenar a fila semanal de um vendedor e separar a fila "confirmar ou '
        'encerrar". **Não** é previsão individual de fechamento, **não** avalia vendedores e '
        "**não** decide encerrar deal.",
        "- `p_win` é a taxa do produto (60–65%): igual para todo deal do mesmo produto; em deals "
        f"parados o fator {w['zombie_p_factor']} é convenção declarada, não estimativa.",
        "- 68% dos deals abertos não têm conta: setor, porte e histórico aparecem só como contexto "
        "(peso 0) e a confiança cai.",
        "- Toda idade é contada até `as_of` (snapshot 2017-12-31), nunca até hoje.",
        "- Dataset possivelmente sintético (Kaggle): padrões de calendário (fim de trimestre) "
        "foram avaliados e **não** entram no score.",
        "",
    ]
    return "\n".join(parts)


__all__ = ["render_model_card"]
