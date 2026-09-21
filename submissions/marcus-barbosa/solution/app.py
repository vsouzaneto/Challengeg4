"""Lead Scorer: o pipeline de segunda-feira do vendedor, do gerente e da Head de RevOps.

Rodar:  streamlit run app.py   (os 4 CSVs do Kaggle precisam estar em data/raw/)
Tudo que aparece aqui sai de leadscorer/ (funções puras, testadas) e da calibração por
painel de snapshots; nenhuma chave de API é necessária.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from leadscorer.brief import seller_brief
from leadscorer.calibration import AGE_BANDS, HORIZON_DAYS, MAX_SUPPORT_DAYS
from leadscorer.data import enrich, load_tables, reference_date
from leadscorer.manager import agent_table, manager_must_acts, revops_findings, team_table
from leadscorer.scoring import (CAT_ALIVE, CAT_CRITICAL, CAT_FOCUS, CAT_FOLLOW, CAT_QUALIFY, CATEGORY_ORDER, SUPPORT_OK, money,
                                score_pipeline, summarize_categories)

HERE = Path(__file__).resolve().parent
RAW = HERE / "data" / "raw"
DOCS = HERE.parent / "docs"

st.set_page_config(page_title="Lead Scorer · segunda de manhã", page_icon=None, layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Source+Serif+4:ital,opsz,wght@0,8..60,300;1,8..60,400&family=JetBrains+Mono:wght@400;500&display=swap');
:root { --g4-navy:#001F35; --g4-ink:#031A26; --g4-gold:#B9915B; --g4-gold-dark:#977342; --g4-gold-light:#C9A96E; --g4-cream:#F5F4F3;
        --g4-white:#FFFFFF; --g4-warm-gray:#EDECEA; --g4-blue:#184560; --g4-brick:#842E20; --g4-muted:#64748B; --g4-border:rgba(0,31,53,0.09); }
html, body, [data-testid="stAppViewContainer"], .stMarkdown, p, li, td, th, label { font-family:'Manrope','Segoe UI',Arial,sans-serif; color:var(--g4-ink); line-height:1.4; }
[data-testid="stAppViewContainer"] { background:var(--g4-cream); }
[data-testid="stHeader"] { background:transparent; }
h1,h2,h3 { font-family:'Manrope',sans-serif; font-weight:800; color:var(--g4-navy); line-height:1.2; letter-spacing:-0.01em; }
h1{font-size:31px} h2{font-size:24px} h3{font-size:18px}
.g4-display { font-family:'Source Serif 4','Libre Baskerville',Georgia,serif; font-weight:300; font-size:44px; line-height:1.2; color:var(--g4-navy); margin:0 0 4px 0; }
.g4-display em { font-style:italic; font-weight:400; }
.g4-eyebrow { font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.08em; color:var(--g4-gold); margin-bottom:2px; }
.g4-rule { border:0; border-bottom:2px solid var(--g4-gold); margin:8px 0 20px 0; }
.g4-label { font-family:'JetBrains Mono',Consolas,monospace; font-size:11px; letter-spacing:0.06em; color:var(--g4-muted); text-transform:uppercase; }
[data-testid="stSidebar"] { background:var(--g4-navy); }
[data-testid="stSidebar"] * { color:var(--g4-cream); }
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 { color:var(--g4-gold); }
[data-testid="stMetric"] { background:var(--g4-white); border:1px solid var(--g4-border); border-radius:10px; padding:14px 18px; }
[data-testid="stMetricLabel"] { font-size:12px; color:var(--g4-muted); text-transform:uppercase; letter-spacing:0.06em; }
[data-testid="stMetricValue"] { font-weight:800; font-size:28px; color:var(--g4-navy); }
[data-testid="stDataFrame"] { border:1px solid var(--g4-border); border-radius:10px; overflow:hidden; }
.g4-card { background:var(--g4-white); border:1px solid var(--g4-border); border-radius:10px; padding:16px 20px; margin-bottom:12px; }
.g4-badge { display:inline-block; font-size:12px; font-weight:700; letter-spacing:0.04em; padding:3px 10px; border-radius:8px; margin-right:8px; }
.g4-badge--focar { background:var(--g4-navy); color:var(--g4-gold); }
.g4-badge--duas { background:var(--g4-brick); color:var(--g4-cream); }
.g4-badge--manter { background:var(--g4-gold); color:var(--g4-navy); }
.g4-badge--vivo { background:var(--g4-warm-gray); color:var(--g4-muted); }
.g4-badge--conta { background:var(--g4-blue); color:var(--g4-cream); }
.g4-badge--qualificar { background:var(--g4-white); color:var(--g4-navy); border:1px solid var(--g4-border); }
.g4-score { font-family:'JetBrains Mono',monospace; font-weight:500; font-size:22px; color:var(--g4-navy); }
.g4-why { color:var(--g4-ink); margin:6px 0 4px 0; }
.g4-next { color:var(--g4-blue); font-weight:600; }
#MainMenu, footer { visibility:hidden; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

BADGE = {CAT_FOCUS: "focar", "Focar agora": "focar", CAT_CRITICAL: "duas", "Primeiras duas semanas": "duas", CAT_FOLLOW: "manter", "Manter follow-up": "manter",
         CAT_ALIVE: "vivo", "Confirmar se está vivo": "vivo", "Cadastrar conta": "conta", CAT_QUALIFY: "qualificar"}


@st.cache_data(show_spinner=False)
def _load():
    t = load_tables(RAW)
    return enrich(t), reference_date(t.pipeline)


@st.cache_data(show_spinner=False)
def _score(as_of: str):
    e, _ = _load()
    scored, cal = score_pipeline(e, pd.Timestamp(as_of))
    return scored, cal


def badge(cat: str) -> str:
    return f'<span class="g4-badge g4-badge--{BADGE.get(cat, "manter")}">{cat}</span>'


def card(item: dict) -> str:
    score = "sem score" if item["score"] is None else f'score {item["score"]}'
    idade = "" if item["idade"] is None else f' · {item["idade"]} dias'
    return (f'<div class="g4-card">{badge(item["tipo"])}<span class="g4-label">{item["deal"]} · {item["produto"]} · {money(item["valor"])}{idade}</span>'
            f'<div><span class="g4-score">{score}</span> &nbsp; <b>{item["conta"]}</b></div>'
            f'<div class="g4-why">{item["porque"]}</div><div class="g4-next">Próximo passo: {item["acao"]}</div></div>')


# ----------------------------------------------------------------------------- dados
if not (RAW / "sales_pipeline.csv").exists():
    st.markdown('<p class="g4-eyebrow">Lead Scorer</p><p class="g4-display">Faltam os <em>dados</em></p><hr class="g4-rule">', unsafe_allow_html=True)
    st.write("Coloque os 4 CSVs do dataset Kaggle em `solution/data/raw/` ou rode `python download_data.py`. Nada é inventado: sem os dados reais, o app não pontua.")
    st.stop()

enriched, ref_date = _load()

# ----------------------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown("### Lead Scorer")
    st.caption("Priorização do pipeline com o que a história dos 8.800 deals sustenta. Nada de vendedor, produto ou setor no score: nos dados, nenhum separa ganho de perda além do acaso.")
    papel = st.radio("Quem está olhando", ["Vendedor", "Gerente", "RevOps"], index=0)
    as_of = st.date_input("Segunda-feira de referência", value=ref_date.date(), min_value=pd.Timestamp("2017-06-30").date(), max_value=ref_date.date(),
                          help="O pipeline é reconstruído como estava nessa data e a chance é calibrada só com o que já tinha fechado até ela.")
    scored_all, cal = _score(str(as_of))
    agents_all = agent_table(scored_all, enriched, pd.Timestamp(as_of))
    regioes = sorted(agents_all["regional_office"].dropna().unique())
    regiao = st.selectbox("Região", ["Todas"] + regioes)
    managers = sorted(agents_all.loc[agents_all["regional_office"] == regiao, "manager"].dropna().unique()) if regiao != "Todas" else sorted(agents_all["manager"].dropna().unique())
    manager = st.selectbox("Gerente", ["Todos"] + managers)
    pool = agents_all
    if regiao != "Todas":
        pool = pool[pool["regional_office"] == regiao]
    if manager != "Todos":
        pool = pool[pool["manager"] == manager]
    vendedores = sorted(pool.index)
    vendedor = st.selectbox("Vendedor", (["Todos"] if papel != "Vendedor" else []) + vendedores)
    st.markdown(f'<p class="g4-label">calibração: {cal.mode} · {len(cal.snapshots)} datas · horizonte {HORIZON_DAYS} d</p>', unsafe_allow_html=True)

scored = scored_all[scored_all["sales_agent"].isin(vendedores)]
if vendedor != "Todos":
    scored = scored[scored["sales_agent"] == vendedor]
agents = agents_all.loc[agents_all.index.isin(vendedores)]

# ----------------------------------------------------------------------------- cabeçalho
titulo = {"Vendedor": "Onde <em>focar</em> esta semana", "Gerente": "O que o time precisa de <em>você</em>", "RevOps": "O pipeline que a história <em>sustenta</em>"}[papel]
quem = vendedor if papel == "Vendedor" else (manager if manager != "Todos" else (regiao if regiao != "Todas" else "todo o time"))
st.markdown(f'<p class="g4-eyebrow">Lead Scorer · {pd.Timestamp(as_of).strftime("%d/%m/%Y")} · {quem}</p><p class="g4-display">{titulo}</p><hr class="g4-rule">', unsafe_allow_html=True)

# ----------------------------------------------------------------------------- vendedor
if papel == "Vendedor":
    b = seller_brief(scored)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Deals abertos", b["resumo"]["abertos"])
    c2.metric("Com chance estimável", b["resumo"]["acionaveis"])
    c3.metric("Focar agora", b["resumo"]["focar"])
    c4.metric("Confirmar se está vivo", b["resumo"]["confirmar_vivo"])
    c5.metric("Valor esperado 90 d", money(b["resumo"]["valor_esperado"]))
    st.write(b["abertura"])
    st.markdown("### A pauta de hoje")
    for item in b["itens"]:
        st.markdown(card(item), unsafe_allow_html=True)

    st.markdown("### Todo o seu pipeline")
    cats = st.multiselect("Blocos", CATEGORY_ORDER, default=CATEGORY_ORDER)
    view = scored[scored["category"].isin(cats)]
    cols = ["opportunity_id", "category", "score", "account", "product", "list_value", "age_days", "p_win", "expected_value", "needs_account", "next_step"]
    st.dataframe(view[cols].rename(columns={"opportunity_id": "deal", "category": "bloco", "account": "conta", "product": "produto", "list_value": "valor de lista",
                                            "age_days": "dias engajado", "p_win": "chance 90 d", "expected_value": "valor esperado", "needs_account": "sem conta", "next_step": "próximo passo"}),
                 hide_index=True, use_container_width=True, height=420,
                 column_config={"score": st.column_config.ProgressColumn("score", min_value=0, max_value=100, format="%d"),
                                "chance 90 d": st.column_config.NumberColumn(format="%.0%"), "valor de lista": st.column_config.NumberColumn(format="US$ %d"),
                                "valor esperado": st.column_config.NumberColumn(format="US$ %d")})
    deal_id = st.selectbox("Ver o porquê de um deal", [""] + list(view["opportunity_id"]))
    if deal_id:
        r = scored.set_index("opportunity_id").loc[deal_id]
        st.markdown(card({"tipo": r["category"], "deal": deal_id, "conta": r["account"] if isinstance(r["account"], str) else "(sem conta)", "produto": r["product"],
                          "valor": r["list_value"], "score": None if pd.isna(r["score"]) else int(r["score"]), "idade": None if pd.isna(r["age_days"]) else int(r["age_days"]),
                          "porque": r["explanation"], "acao": r["next_step"]}), unsafe_allow_html=True)
        if r["support"] == SUPPORT_OK:
            st.markdown(f'<p class="g4-label">como o score é calculado</p>', unsafe_allow_html=True)
            st.table(pd.DataFrame({"passo": ["chance de ganhar em 90 d (faixa de idade " + str(r["age_band"]) + ", deals com conta, n=" + str(cal.n_for(r["age_days"])) + ")",
                                            "valor de lista", "valor esperado = chance × valor", "posição entre os deals acionáveis"],
                                   "valor": [f"{r['p_win']:.0%} (IC {cal.ci_by_band[r['age_band']][0]:.0%} a {cal.ci_by_band[r['age_band']][1]:.0%})", money(r["list_value"]), money(r["expected_value"]), f"maior que {int(r['score'])}% → score {int(r['score'])}"]}))

# ----------------------------------------------------------------------------- gerente
elif papel == "Gerente":
    f = revops_findings(scored, agents)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Vendedores", len(agents))
    c2.metric("Deals abertos", f["deals_abertos"])
    c3.metric("Focar agora no time", int((scored["category"] == CAT_FOCUS).sum()))
    c4.metric("Além de 138 dias", f["deals_alem_138"], help="Nenhum deal na história fechou depois de 138 dias.")
    c5.metric("Valor esperado 90 d", money(f["valor_esperado_acionavel"]))
    st.markdown("### O que fazer na segunda")
    for a in manager_must_acts(agents, scored):
        st.markdown(f'<div class="g4-card"><span class="g4-badge g4-badge--focar">{a["tipo"]}</span><b>{a["quem"]}</b><div class="g4-why">{a["porque"]}</div><div class="g4-next">{a["acao"]}</div></div>', unsafe_allow_html=True)
    st.markdown("### Por vendedor")
    st.caption("A taxa histórica é contexto, não nota: entre vendedores, a variação é compatível com o acaso (χ² p=0,26). Sobrecarga = deals abertos acima do P75 do time.")
    show = agents[["manager", "regional_office", "abertos", "acionaveis", "focar", "duas_semanas", "confirmar_vivo", "fora_do_padrao_pct", "sem_conta_pct", "valor_esperado", "hist_win_rate", "hist_n", "sobrecarga"]]
    st.dataframe(show.rename(columns={"manager": "gerente", "regional_office": "região", "duas_semanas": "2 semanas", "confirmar_vivo": "confirmar vivo", "fora_do_padrao_pct": "% além de 138 d",
                                      "sem_conta_pct": "% sem conta", "valor_esperado": "valor esperado", "hist_win_rate": "taxa histórica %", "hist_n": "n fechados"}),
                 use_container_width=True, height=520, column_config={"valor esperado": st.column_config.NumberColumn(format="US$ %d")})
    st.markdown("### Por gerente e região")
    st.dataframe(team_table(agents).rename(columns={"valor_lista": "valor de lista", "valor_esperado": "valor esperado", "sem_conta_pct": "% sem conta", "confirmar_vivo": "confirmar vivo"}), use_container_width=True,
                 column_config={"valor de lista": st.column_config.NumberColumn(format="US$ %d"), "valor esperado": st.column_config.NumberColumn(format="US$ %d")})

# ----------------------------------------------------------------------------- revops
else:
    f = revops_findings(scored, agents)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pipeline nominal", money(f["valor_lista_total"]), help="Soma do preço de lista de todos os deals abertos.")
    c2.metric("Além de 138 dias", f"{f['pct_valor_alem_138']}%", help=f"{f['deals_alem_138']} deals, {money(f['valor_alem_138'])}. Nenhum deal na história fechou depois de 138 dias.")
    c3.metric("Pipeline acionável", money(f["valor_lista_acionavel"]), help=f"{f['deals_acionaveis']} deals em Engaging até 138 dias.")
    c4.metric("Valor esperado 90 d", money(f["valor_esperado_acionavel"]))
    st.markdown("### O que os dados sustentam")
    st.write(f"Dos {f['deals_abertos']} deals abertos, {f['deals_alem_138']} ({f['pct_valor_alem_138']}% do valor nominal) estão além do maior ciclo já concluído. "
             f"{f['deals_sem_conta']} ({f['pct_sem_conta']}%) não têm conta cadastrada, e nos dados nenhum deal fechou sem conta. "
             f"{f['prospecting']} estão em prospecção sem data de engajamento. O que sobra para trabalhar com chance estimável vale {money(f['valor_lista_acionavel'])} de lista e {money(f['valor_esperado_acionavel'])} esperados em 90 dias.")
    st.markdown("### Blocos de ação")
    summ = summarize_categories(scored).rename(columns={"valor_lista": "valor de lista", "valor_esperado": "valor esperado", "sem_conta": "sem conta"})
    st.dataframe(summ, use_container_width=True, column_config={"valor de lista": st.column_config.NumberColumn(format="US$ %d"), "valor esperado": st.column_config.NumberColumn(format="US$ %d")})
    st.markdown("### Chance de ganhar em 90 dias, por idade do deal")
    st.caption(f"Calibração por painel de snapshots ({', '.join(cal.snapshots) or cal.mode}), só deals com conta cadastrada, só com o passado. Intervalo de confiança de 95% (Wilson).")
    calib = pd.DataFrame({"faixa (dias)": [b for _, _, b in AGE_BANDS], "chance": [cal.p_by_band[b] for _, _, b in AGE_BANDS],
                          "IC 95%": [f"{cal.ci_by_band[b][0]:.0%} a {cal.ci_by_band[b][1]:.0%}" for _, _, b in AGE_BANDS], "n (deal × data)": [cal.n_by_band[b] for _, _, b in AGE_BANDS],
                          "incluindo deals sem conta": [cal.p_all_deals_by_band.get(b) for _, _, b in AGE_BANDS]})
    st.dataframe(calib, hide_index=True, use_container_width=True, column_config={"chance": st.column_config.NumberColumn(format="%.0%"), "incluindo deals sem conta": st.column_config.NumberColumn(format="%.0%")})
    st.markdown("### O que não entra no score, e por quê")
    st.write("Vendedor (χ² p=0,26), vendedor × produto (gap igual ao acaso, p=0,89), produto (spread 4,8 pp, p=0,37), setor (p=0,97), porte da conta (p=0,50), subsidiária (p=0,74), desconto (valor fechado = 0,998 × preço). "
             "Cada teste está em docs/exploration_results.md com o código em solution/02_explore.py.")
    bt = DOCS / "backtest.json"
    if bt.exists():
        st.markdown("### Backtest walk-forward")
        res = json.loads(bt.read_text(encoding="utf-8"))
        rows = []
        for r in res:
            a = r["alive_check"]; w = r["with_account"]
            rows.append({"data": r["as_of"], "abertos": r["open_at_t"], "além de 138 d": a["n"], "desses, fecharam depois": a["won_later_any_time"] + a["lost_later_any_time"],
                         "2 semanas: win 90 d": w.get("critical_window", {}).get("win_rate"), "mais de 14 d: win 90 d": w.get("critical_window", {}).get("win_rate_older"),
                         "top-100 score: % do valor ganho": w.get("value_capture", {}).get("100", {}).get("score"), "top-100 só preço: %": w.get("value_capture", {}).get("100", {}).get("list_price_all_open")})
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True,
                     column_config={c: st.column_config.NumberColumn(format="%.0%") for c in ["2 semanas: win 90 d", "mais de 14 d: win 90 d", "top-100 score: % do valor ganho", "top-100 só preço: %"]})
        st.caption("Na captura de valor, o score empata com ordenar por preço: a chance é quase plana entre 15 e 120 dias. O que o método faz é tirar do topo o que a história diz que não fecha e dizer o que fazer com cada bloco. Detalhes em docs/backtest.md.")
