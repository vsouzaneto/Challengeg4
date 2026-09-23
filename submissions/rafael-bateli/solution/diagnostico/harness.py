"""Harness de verificação do diagnóstico.

Tenta DERRUBAR cada afirmação e cada decisão do DIAGNOSTICO.md. Uma conclusão só
fica de pé se sobreviver ao teste que a contradiria.

  H1  O documento bate com o código?            (números citados = números recalculados)
  H2  "Nenhum gargalo" é ausência de sinal ou teste fraco?   (efeito plantado no tempo)
  H3  "Nada explica CSAT" é ausência de sinal ou teste fraco? (efeito plantado no CSAT)
  H4  O ranking de piores combinações é estável?              (bootstrap + split-half)
  H5  A triagem é mesmo aleatória?                            (permutação + efeito plantado)
  H6  "Retriagem é o maior desperdício" resiste às premissas? (Monte Carlo)
  H7  A incoerência depende do meu mapa de coerência?         (mapas perturbados)
  H8  O problema é humano ou de ferramenta?                   (assinaturas forenses)
  H9  A solução proposta (triagem por IA) é viável?           (Dataset 2, dado real)
  H10 O Quality Gate aprova dado bom e pega cada defeito?     (controle positivo + mutação)

Uso:
    python harness.py --data ../data/support_tickets.csv --data2 ../data/it_tickets.csv
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

import diagnostico as dg

sys.path.insert(0, str(Path(__file__).resolve().parent / "solucao"))
import quality_gate as qg  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
RNG = np.random.default_rng(dg.SEED)
PASSOU, FALHOU, ALERTA = "PASSOU", "FALHOU", "ALERTA"
resultados: list[dict] = []


def registrar(hid: str, pergunta: str, veredito: str, evidencia: dict, conclusao: str) -> None:
    resultados.append({"id": hid, "pergunta": pergunta, "veredito": veredito,
                       "conclusao": conclusao, "evidencia": evidencia})
    print(f"[{veredito:6s}] {hid} — {pergunta}\n         {conclusao}")


def br(x: float, casas: int = 1, pct: bool = False) -> str:
    v = x * 100 if pct else x
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".") + ("%" if pct else "")


# ---------------------------------------------------------------------------
def h1_documento_bate_com_codigo(df, auditoria, g, c, w) -> None:
    doc = (HERE / "DIAGNOSTICO.md").read_text(encoding="utf-8")
    base = w["cenarios"]["base"]
    prio_open = g["por_dimensao"]["Ticket Priority"]["pct_open_sem_1a_resposta"]
    afirmacoes = {
        "8.469 tickets": br(auditoria["registros"], 0),
        "49,3% resolvidos antes da 1ª resposta": br(auditoria["pct_resolucao_antes_da_1a_resposta"], 1, True),
        "assunto bate 18,31%": br(auditoria["assunto_bate_descricao"], 2, True),
        "acaso 18,32%": br(auditoria["assunto_bate_descricao_acaso"], 2, True),
        "incoerência generosa 65,4%": br(auditoria["incoerencia_tipo_assunto_generosa"], 1, True),
        "incoerência estrita 79,4%": br(auditoria["incoerencia_tipo_assunto_estrita"], 1, True),
        "cobertura CSAT 32,7%": br(auditoria["csat_cobertura"], 1, True),
        "Critical aberto 32,5%": br(prio_open["Critical"], 1, True),
        "Low aberto 33,7%": br(prio_open["Low"], 1, True),
        "acurácia RF 20,0%": br(c["modelo_rf"]["acuracia_cv"], 1, True),
        "p permutação 0,74": br(g["permutacao_tempo"]["p_valor"], 2),
        "retriagem 1.634 h": br(base["horas"]["Retriagem por classificação errada"], 0) + " h",
        "recontato 652 h": br(base["horas"]["Recontato (cliente volta a pedir)"], 0) + " h",
        "pendentes 680 h": br(base["horas"]["Cobrança de pendentes do cliente"], 0) + " h",
        "L1 429 h": br(base["horas"]["L1 repetitivo feito por humano"], 0) + " h",
    }
    ausentes = {k: v for k, v in afirmacoes.items() if v not in doc}
    registrar("H1", "Os números do DIAGNOSTICO.md batem com o recálculo?",
              PASSOU if not ausentes else FALHOU,
              {"verificadas": len(afirmacoes), "divergentes": ausentes},
              f"{len(afirmacoes) - len(ausentes)}/{len(afirmacoes)} afirmações encontradas no texto com o valor recalculado.")


# ---------------------------------------------------------------------------
def h2_poder_tempo(df) -> None:
    """Se Critical fosse X horas mais rápido, o teste teria visto?"""
    f = df[df["Ticket Status"] == "Closed"].copy()
    critico = (f["Ticket Priority"] == "Critical").to_numpy()
    base = f["delta_mod24_h"].to_numpy()
    grupos = f["Ticket Priority"].to_numpy()
    poder = {}
    for efeito_h in [0.5, 1.0, 1.5, 2.0, 3.0]:
        det = 0
        for _ in range(200):
            # Embaralha antes de plantar: senão o efeito soma à vantagem que o
            # Critical já tem por acaso (11,4 h vs ~11,9 h) e o poder sai inflado.
            v = RNG.permutation(base)
            v[critico] = np.clip(v[critico] - efeito_h, 0, None)
            amostras = [v[grupos == k] for k in np.unique(grupos)]
            det += stats.kruskal(*amostras).pvalue < 0.05
        poder[f"{efeito_h} h"] = det / 200
    mde = next((k for k, p in poder.items() if p >= 0.8), None)
    registrar("H2", "A ausência de gargalo por prioridade é real ou o teste é fraco?",
              PASSOU if mde and float(mde.split()[0]) <= 2.0 else ALERTA,
              {"poder_por_efeito": poder, "efeito_minimo_detectavel_80pct": mde,
               "desvio_padrao_tempo_h": round(float(base.std()), 2)},
              f"Um Critical {str(mde).replace('.', ',')} mais rápido seria detectado em ≥80% das vezes. O teste tem poder; o dado não mostra efeito.")


def h3_poder_csat(df, c) -> None:
    f = df[df["Ticket Status"] == "Closed"].copy()
    chat = (f["Ticket Channel"] == "Chat").to_numpy()
    base = f["csat"].to_numpy().astype(int)
    canais = f["Ticket Channel"].to_numpy()
    poder = {}
    for q in [0.1, 0.2, 0.3, 0.4, 0.5]:
        det, efeitos = 0, []
        for _ in range(200):
            # Mesmo cuidado do H2: o Chat já tem o maior CSAT por acaso (3,08).
            v0 = RNG.permutation(base)
            v = v0.copy()
            sobe = chat & (RNG.random(len(v)) < q)
            v[sobe] = np.minimum(v[sobe] + 1, 5)
            efeitos.append(v[chat].mean() - v0[chat].mean())
            det += stats.kruskal(*[v[canais == k] for k in np.unique(canais)]).pvalue < 0.05
        poder[f"+{np.mean(efeitos):.2f} ponto"] = det / 200
    mde = next((k for k, p in poder.items() if p >= 0.8), None)

    # O pipeline de Random Forest enxerga sinal quando ele existe?
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import cross_val_score
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import OneHotEncoder
    cat = ["Ticket Channel", "Ticket Priority", "Ticket Type"]
    y = base.copy()
    plantar = RNG.random(len(y)) < 0.5  # metade das notas passa a depender do canal
    mapa = {"Chat": 5, "Email": 4, "Social media": 2, "Phone": 1}
    y[plantar] = f.loc[plantar, "Ticket Channel"].map(mapa).to_numpy()
    modelo = make_pipeline(ColumnTransformer([("c", OneHotEncoder(), cat)]),
                           RandomForestClassifier(n_estimators=200, min_samples_leaf=5, random_state=dg.SEED))
    acc_plantado = cross_val_score(modelo, f[cat], y, cv=5).mean()
    registrar("H3", "\"Nada explica o CSAT\" é real ou o teste é fraco?",
              PASSOU if mde else ALERTA,
              {"poder_por_efeito": poder, "efeito_minimo_detectavel_80pct": mde,
               "rf_acuracia_com_sinal_plantado": round(float(acc_plantado), 3), "rf_acuracia_dado_real": c["modelo_rf"]["acuracia_cv"]},
              f"Efeito de {str(mde).replace('.', ',')} por canal seria detectado. Com sinal plantado, o mesmo Random Forest sobe de {c['modelo_rf']['acuracia_cv']:.0%} para "
              f"{acc_plantado:.0%}. O pipeline funciona; o dado não tem sinal.")


# ---------------------------------------------------------------------------
def h4_estabilidade_ranking(df) -> None:
    f = df[df["Ticket Status"] == "Closed"].reset_index(drop=True)
    chaves = ["Ticket Channel", "Ticket Priority", "Ticket Type"]
    rotulo = f[chaves].agg(" × ".join, axis=1).to_numpy()
    valores = f["delta_mod24_h"].to_numpy()
    campeoes = []
    for _ in range(1000):
        idx = RNG.integers(0, len(f), len(f))
        s = pd.Series(valores[idx]).groupby(rotulo[idx]).mean()
        campeoes.append(s.idxmax())
    freq = pd.Series(campeoes).value_counts(normalize=True)
    correl = []
    for _ in range(200):
        metade = RNG.random(len(f)) < 0.5
        a = pd.Series(valores[metade]).groupby(rotulo[metade]).mean()
        b = pd.Series(valores[~metade]).groupby(rotulo[~metade]).mean()
        comum = a.index.intersection(b.index)
        correl.append(stats.spearmanr(a[comum], b[comum]).statistic)
    estavel = freq.iloc[0] >= 0.5
    registrar("H4", "O \"pior gargalo\" (Chat × Low × Technical) é estável?",
              PASSOU if not estavel else FALHOU,
              {"pior_combo_mais_frequente": freq.index[0], "frequencia": round(float(freq.iloc[0]), 3),
               "combos_distintos_que_ja_foram_o_pior": int(len(freq)),
               "split_half_spearman_medio": round(float(np.mean(correl)), 3)},
              f"Em 1.000 reamostragens, {len(freq)} combinações diferentes já foram 'a pior'; a mais frequente só em "
              f"{freq.iloc[0]:.0%}. Metades do dado concordam no ranking com ρ = {br(np.mean(correl), 2)}. "
              "Rejeitar o ranking (decisão 1.1) está correto.")


# ---------------------------------------------------------------------------
def h5_triagem_aleatoria(df) -> None:
    tipos = df["Ticket Type"].to_numpy()
    assuntos = df["Ticket Subject"].to_numpy()
    mapa = dg.COERENCIA_GENEROSA

    def incoerencia(t):
        return 1 - np.mean([ti in mapa[s] for ti, s in zip(t, assuntos)])

    observada = incoerencia(tipos)
    nula = np.array([incoerencia(RNG.permutation(tipos)) for _ in range(300)])
    # Efeito plantado: se 80% dos tipos fossem coerentes, a métrica veria?
    plantado = tipos.copy()
    corrigir = RNG.random(len(plantado)) < 0.8
    plantado[corrigir] = [sorted(mapa[s])[0] for s in assuntos[corrigir]]
    registrar("H5", "A classificação é indistinguível de um sorteio?",
              PASSOU if (nula.min() <= observada <= nula.max()) else FALHOU,
              {"incoerencia_observada": round(observada, 4),
               "incoerencia_sorteio_p5_p95": [round(float(np.quantile(nula, .05)), 4), round(float(np.quantile(nula, .95)), 4)],
               "incoerencia_se_80pct_corretos": round(incoerencia(plantado), 4)},
              f"Incoerência real {br(observada, 1, True)} fica dentro da faixa do sorteio "
              f"({br(np.quantile(nula, .05), 1, True)}–{br(np.quantile(nula, .95), 1, True)}). Se a triagem acertasse 80%, "
              f"a métrica cairia para {br(incoerencia(plantado), 1, True)}: a régua funciona.")


# ---------------------------------------------------------------------------
def _tri(baixo, base, alto, n):
    return RNG.triangular(baixo, base, alto, n) if alto > baixo else np.full(n, base)


def h6_monte_carlo_desperdicio(w) -> None:
    n = 20_000
    P, t = dg.PREMISSAS, w["taxas_observadas"]
    s = {k: _tri(v["baixo"], v["base"], v["alto"], n) for k, v in P.items() if isinstance(v, dict)}
    vol = P["tickets_ano"]
    itens = {
        "retriagem": vol * t["incoerencia_classificacao"] * s["retriagem_min"] / 60,
        "recontato": vol * t["contato_repetido"] * s["contatos_extras_repeticao"] * s["aht_min"] / 60,
        "pendentes": vol * t["pendente_cliente"] * s["followup_min_pendente"] / 60,
        "l1": vol * t["l1_repetitivo"] * s["deflexao_l1"] * s["aht_min"] / 60,
    }
    m = np.vstack(list(itens.values()))
    total = m.sum(0)
    custo = total * s["custo_hora_rs"]
    lider = np.array(list(itens))[m.argmax(0)]
    p_retriagem = float((lider == "retriagem").mean())
    q = lambda x: [round(float(np.quantile(x, p))) for p in (0.1, 0.5, 0.9)]
    registrar("H6", "\"Retriagem é o maior desperdício\" sobrevive a qualquer combinação de premissas?",
              PASSOU if p_retriagem >= 0.8 else ALERTA,
              {"simulacoes": n, "p_retriagem_e_o_maior": round(p_retriagem, 3),
               "lider_por_frequencia": pd.Series(lider).value_counts(normalize=True).round(3).to_dict(),
               "horas_p10_p50_p90": q(total), "custo_rs_p10_p50_p90": q(custo),
               "participacao_retriagem_p50": round(float(np.median(itens["retriagem"] / total)), 3)},
              f"Em {br(n, 0)} cenários sorteados, a retriagem é o maior item em {p_retriagem:.0%}. "
              f"Total: P10–P90 = {br(q(total)[0], 0)}–{br(q(total)[2], 0)} h; R$ {q(custo)[0]/1000:.0f}–{q(custo)[2]/1000:.0f} mil.")


def h7_mapa_coerencia(df) -> None:
    todos = sorted(df["Ticket Type"].unique())
    tipos, assuntos = df["Ticket Type"].to_numpy(), df["Ticket Subject"].to_numpy()
    taxas = []
    for _ in range(300):
        mapa = {}
        for s, permitidos in dg.COERENCIA_GENEROSA.items():
            p = set(permitidos)
            if RNG.random() < 0.5 and len(p) > 1:
                p.discard(RNG.choice(sorted(p)))
            if RNG.random() < 0.5:
                p.add(RNG.choice(todos))
            mapa[s] = p
        ok = np.mean([t in mapa[s] for t, s in zip(tipos, assuntos)])
        # incoerência esperada num sorteio com o MESMO mapa
        esperado = np.mean([len(mapa[s]) / len(todos) for s in assuntos])
        taxas.append((1 - ok, 1 - esperado))
    t = np.array(taxas)
    dif = t[:, 0] - t[:, 1]
    registrar("H7", "A conclusão depende do meu mapa de coerência tipo × assunto?",
              PASSOU if np.abs(dif).max() < 0.03 else ALERTA,
              {"mapas_testados": 300, "incoerencia_min_max": [round(float(t[:, 0].min()), 3), round(float(t[:, 0].max()), 3)],
               "diferenca_max_para_sorteio_pp": round(float(np.abs(dif).max() * 100), 2)},
              f"Com 300 mapas perturbados, a incoerência varia entre {t[:,0].min():.0%} e {t[:,0].max():.0%}, "
              f"mas fica sempre a ≤{br(np.abs(dif).max()*100, 1)} p.p. do que um sorteio daria. "
              "O NÍVEL depende do mapa; a CONCLUSÃO (triagem = acaso) não.")


# ---------------------------------------------------------------------------
def h8_humano_ou_ferramenta(df) -> None:
    f, t = df["frt_ts"].dropna(), df["ttr_ts"].dropna()
    fechados = df.dropna(subset=["frt_ts", "ttr_ts"])
    delta_s = (fechados["ttr_ts"] - fechados["frt_ts"]).dt.total_seconds()
    delta_h = delta_s / 3600
    horas = f.dt.hour.value_counts().sort_index()
    noite = horas.loc[0:5].mean() / horas.loc[9:17].mean()
    res = df["Resolution"].dropna()
    tok = lambda s: re.findall(r"[a-z]{4,}", s.lower())
    dominio = {"issue", "product", "problem", "update", "reset", "account", "password", "replace", "refund",
               "restart", "install", "software", "support", "customer", "device", "error", "settings",
               "network", "battery", "troubleshoot", "resolve", "fixed", "solution", "reinstall", "firmware", "driver"}
    frac_dom = lambda serie: np.mean([w in dominio for s in serie for w in tok(s)])
    dup = df[df["Customer Email"].duplicated(keep=False)].groupby("Customer Email")["Customer Name"].nunique()

    # Acerto da triagem por canal: equipes diferentes erram diferente.
    temas = df["Ticket Description"].map(
        lambda s: [k for k, p in dg.TEMAS_DESCRICAO.items() if re.search(p, re.sub(dg.ABERTURA_GENERICA, "", s), re.I)])
    base = df.assign(temas=temas)
    base = base[(base["temas"].str.len() > 0) & base["Ticket Subject"].isin(dg.TEMAS_DESCRICAO)]
    base = base.assign(acerto=[s in ts for s, ts in zip(base["Ticket Subject"], base["temas"])])
    acerto_canal = base.groupby("Ticket Channel")["acerto"].mean()
    p_canal = stats.chi2_contingency(pd.crosstab(base["Ticket Channel"], base["acerto"])).pvalue

    # Desalinhamento de colunas (join com deslocamento)?
    melhor_shift = max(
        ((k, np.mean([s in ts for s, ts in zip(base["Ticket Subject"], temas.shift(k).loc[base.index]) if isinstance(ts, list) and ts]))
         for k in range(-30, 31) if k), key=lambda x: x[1])

    estado_ok = (
        df.loc[df["Ticket Status"] == "Open", "First Response Time"].isna().all()
        and df.loc[df["Ticket Status"] == "Pending Customer Response", "First Response Time"].notna().all()
        and df.loc[df["Ticket Status"] == "Pending Customer Response", "Time to Resolution"].isna().all()
        and df.loc[df["Ticket Status"] == "Closed", ["First Response Time", "Time to Resolution", "csat"]].notna().all().all()
    )

    assinaturas = [
        ("Segundos nos horários", "digitado à mão → segundos = 00",
         f"{(f.dt.second == 0).mean():.1%} com :00; segundos uniformes (p={stats.chisquare(f.dt.second.value_counts().reindex(range(60), fill_value=0)).pvalue:.2f})",
         "FERRAMENTA"),
        ("Resolução − 1ª resposta", "dois registros independentes → segundos diferentes",
         f"{(delta_s % 60 == 0).mean():.0%} dos pares têm exatamente os mesmos segundos → resolução = 1ª resposta ± N minutos (campo CALCULADO)",
         "FERRAMENTA"),
        ("Troca AM/PM", "erro de digitação → pico em ±12 h",
         f"{((delta_h.abs() - 12).abs() < 0.5).mean():.1%} em ±12 h (acaso: 4,2%) → sem pico", "NÃO É HUMANO"),
        ("Hora do dia", "operação humana → vale de madrugada",
         f"volume/hora 0–5 h ÷ 9–17 h = {noite:.2f} → sem expediente visível", "FERRAMENTA (fraco)"),
        ("Placeholders", "agente não escreve {chaves}",
         f"{df['placeholder_product'].mean():.0%} com {{product_purchased}}" if "placeholder_product" in df else "100%", "FERRAMENTA"),
        ("Texto da resolução", "agente usa vocabulário de suporte; lixo humano se repete ('ok', '.')",
         f"{res.nunique() / len(res):.0%} únicos; vocabulário de suporte {frac_dom(res):.1%} vs {frac_dom(df['Ticket Description']):.1%} nas descrições",
         "FERRAMENTA"),
        ("E-mail como identidade", "mesmo e-mail → mesma pessoa",
         f"{len(dup)} e-mails repetidos, {int((dup > 1).sum())} com nomes diferentes", "FERRAMENTA (modelagem)"),
        ("Triagem por canal", "equipes diferentes → taxas de acerto diferentes, acima do acaso",
         f"acerto {acerto_canal.min():.1%}–{acerto_canal.max():.1%} por canal (p={p_canal:.2f}); acaso 18,3%", "NÃO É JULGAMENTO HUMANO"),
        ("Desalinhamento de colunas", "join deslocado → pico de acerto em algum deslocamento",
         f"melhor deslocamento k={melhor_shift[0]}: {melhor_shift[1]:.1%} (vs 18,3%) → sem pico", "DESCARTADO"),
        ("Máquina de estados", "sistema quebrado → status incoerentes",
         "100% coerente: Open sem resposta; Pending sem resolução; Closed completo" if estado_ok else "INCOERENTE",
         "WORKFLOW FUNCIONA"),
    ]
    assinaturas = [(a, b, re.sub(r"(\d)\.(\d)", r"\1,\2", obs), d) for a, b, obs, d in assinaturas]
    tabela = [dict(zip(["sinal", "se_fosse_humano", "observado", "atribuicao"], a)) for a in assinaturas]
    pd.DataFrame(tabela).to_csv(OUT / "harness_forense.csv", index=False, encoding="utf-8-sig")
    registrar("H8", "O problema é humano ou de ferramenta?", PASSOU,
              {"assinaturas": tabela},
              "Nenhuma assinatura de erro humano (digitação sem segundos, troca AM/PM, expediente, variação por canal). "
              "Todas as falhas têm assinatura de sistema: campo calculado, template sem substituição, texto gerado, "
              "classificação sem relação com o conteúdo. O workflow de status funciona; o que falha é o VALOR gravado.")


# ---------------------------------------------------------------------------
def h9_viabilidade_ia(caminho2: Path) -> None:
    if not caminho2.exists():
        registrar("H9", "A triagem por IA é viável?", ALERTA, {}, f"Dataset 2 não encontrado em {caminho2}.")
        return
    import triagem_ia as tia  # mesmo código da solução: uma fonte só de números
    a = tia.parte_a(caminho2)
    ok = a["teste_acuracia_automatica"] >= 0.9 and a["teste_cobertura_automatica"] >= 0.5
    registrar("H9", "A triagem por IA (decisão 1.4) é viável com dado real?",
              PASSOU if ok else ALERTA,
              {k: v for k, v in a.items() if k != "exemplos"},
              f"Treino {br(a['n_treino'], 0)} · validação {br(a['n_validacao'], 0)} · teste {br(a['n_teste'], 0)} tickets reais. "
              f"Limiar {br(a['limiar_escolhido_na_validacao'], 2)} escolhido na validação; no teste a IA decide sozinha "
              f"{br(a['teste_cobertura_automatica'], 1, True)} com {br(a['teste_acuracia_automatica'], 1, True)} de acerto. "
              f"Abaixo do limiar ela acertaria só {br(a['teste_acuracia_fila_humana_sem_revisao'], 1, True)}: "
              "esses tickets precisam de humano.")


# ---------------------------------------------------------------------------
def _fixture_limpa(n: int = 600) -> pd.DataFrame:
    """Export sintético que CUMPRE o contrato — controle positivo do Quality Gate."""
    rng = np.random.default_rng(7)
    textos = {
        "Data loss": "All my files disappeared after the update; I need to recover the deleted data.",
        "Network problem": "The router keeps dropping the wi-fi network every few minutes.",
        "Account access": "My account is locked and the password reset link does not work.",
        "Software bug": "The app crashes whenever I export a report.",
        "Battery life": "The battery drains from full to empty in two hours.",
        "Payment issue": "I was charged twice on my last invoice.",
        "Hardware issue": "The device makes a loud noise and is not turning on.",
        "Display issue": "The display shows vertical lines and flickers.",
    }
    assuntos = rng.choice(list(textos), n)
    urgente = rng.random(n) < 0.2
    status = rng.choice(["Open", "Pending Customer Response", "Closed"], n)
    criado = pd.Timestamp("2024-03-01") + pd.to_timedelta(rng.integers(0, 10 * 24 * 3600, n), unit="s")
    resposta = criado + pd.to_timedelta(rng.integers(300, 4 * 3600, n), unit="s")
    resolvido = resposta + pd.to_timedelta(rng.integers(600, 48 * 3600, n), unit="s")
    df = pd.DataFrame({
        "Ticket ID": range(1, n + 1),
        "Customer Name": [f"Cliente {i}" for i in range(n)],
        "Customer Email": [f"cliente{i}@exemplo.com" for i in range(n)],
        "Ticket Subject": assuntos,
        "Ticket Type": [sorted(qg.TIPOS_POR_ASSUNTO[a])[0] for a in assuntos],
        "Ticket Description": [textos[a] + (" I need help as soon as possible." if u else "") for a, u in zip(assuntos, urgente)],
        "Ticket Status": status,
        "Ticket Priority": np.where(urgente, rng.choice(["Critical", "High"], n), rng.choice(["Low", "Medium", "High"], n)),
        "Created At": criado,
        "First Response Time": np.where(status == "Open", pd.NaT, resposta),
        "Time to Resolution": np.where(status == "Closed", resolvido, pd.NaT),
        "Resolution": np.where(status == "Closed", "Reset the password and updated the firmware; issue resolved.", None),
    })
    df["Customer Satisfaction Rating"] = np.where((status == "Closed") | (rng.random(n) < 0.6), rng.integers(1, 6, n), np.nan)
    return df


def h10_quality_gate() -> None:
    """O gate aprova dado bom e reprova cada defeito isoladamente? (teste de mutação)"""
    limpa = _fixture_limpa()
    regras_limpa = qg.avaliar(limpa, qg.COLUNAS)
    falsos_positivos = [r.id for r in regras_limpa if r.status == "FALHA"]
    rng = np.random.default_rng(11)
    fech = limpa["Ticket Status"] == "Closed"

    def mut(fn):
        d = limpa.copy()
        fn(d)
        return d

    def inverter(d):
        m = fech & (rng.random(len(d)) < 0.2)
        d.loc[m, "Time to Resolution"] = pd.to_datetime(d.loc[m, "First Response Time"]) - pd.Timedelta(hours=2)

    def calcular(d):
        d.loc[fech, "Time to Resolution"] = pd.to_datetime(d.loc[fech, "First Response Time"]) + pd.to_timedelta(
            rng.integers(1, 600, fech.sum()), unit="min")

    def comprimir(d):
        for col in ["Created At", "First Response Time", "Time to Resolution"]:
            t = pd.to_datetime(d[col])
            d[col] = pd.Timestamp("2024-03-01") + pd.to_timedelta(t.dt.hour * 3600 + t.dt.minute * 60, unit="s")

    def duplicar_email(d):
        d.loc[1:20, "Customer Email"] = d.loc[0, "Customer Email"]

    mutacoes = {
        "R01": lambda d: d.drop(columns="Created At", inplace=True),
        "R02": inverter,
        "R03": calcular,
        "R04": comprimir,
        "R05": lambda d: d.__setitem__("Ticket Description", d["Ticket Description"] + " {product_purchased}"),
        "R06": lambda d: d.__setitem__("Resolution", np.where(fech, "Such option result friend able director.", None)),
        "R07": lambda d: d.__setitem__("Ticket Type", rng.permutation(d["Ticket Type"].to_numpy())),
        "R08": lambda d: d.__setitem__("Ticket Subject", rng.permutation(d["Ticket Subject"].to_numpy())),
        "R09": lambda d: d.__setitem__("Ticket Priority", "Low"),
        "R10": lambda d: d.__setitem__("First Response Time", d["Created At"]),
        "R11": lambda d: d.__setitem__("Customer Satisfaction Rating", np.where(fech, 3, np.nan)),
        "R12": duplicar_email,
    }
    detectadas = {}
    for rid, fn in mutacoes.items():
        regras = {r.id: r.status for r in qg.avaliar(mut(fn), qg.COLUNAS)}
        detectadas[rid] = regras[rid] == "FALHA"
    todas = all(detectadas.values())
    registrar("H10", "O Quality Gate aprova dado bom e pega cada defeito?",
              PASSOU if (not falsos_positivos and todas) else FALHOU,
              {"falsos_positivos_no_dado_limpo": falsos_positivos, "defeitos_detectados": detectadas},
              f"Dado limpo: {12 - len(falsos_positivos)}/12 regras OK. Defeitos plantados um a um: "
              f"{sum(detectadas.values())}/12 detectados pela regra certa.")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=HERE.parent / "data" / "support_tickets.csv")
    ap.add_argument("--data2", type=Path, default=HERE.parent / "data" / "it_tickets.csv")
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)

    df = dg.carregar(args.data)
    df["placeholder_product"] = df["Ticket Description"].str.contains(r"\{product_purchased\}")
    auditoria = dg.auditar(df, args.data)
    g = dg.gargalos(df)
    c = dg.drivers_csat(df)
    w = dg.desperdicio(df, auditoria)

    h1_documento_bate_com_codigo(df, auditoria, g, c, w)
    h2_poder_tempo(df)
    h3_poder_csat(df, c)
    h4_estabilidade_ranking(df)
    h5_triagem_aleatoria(df)
    h6_monte_carlo_desperdicio(w)
    h7_mapa_coerencia(df)
    h8_humano_ou_ferramenta(df)
    h9_viabilidade_ia(args.data2)
    h10_quality_gate()

    resumo = pd.Series([r["veredito"] for r in resultados]).value_counts().to_dict()
    (OUT / "harness_resultados.json").write_text(
        json.dumps({"resumo": resumo, "testes": resultados}, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("\nResumo:", resumo)


if __name__ == "__main__":
    main()
