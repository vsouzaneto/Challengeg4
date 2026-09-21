"""Lead Scorer: o pipeline de segunda-feira do vendedor, do gerente e da Head de RevOps.

Rodar:  streamlit run app.py   (os 4 CSVs do Kaggle precisam estar em data/raw/)
Tudo que aparece aqui sai de leadscorer/ (funções puras, testadas) e da calibração por
painel de snapshots; nenhuma chave de API é necessária.
Presets por URL: ?papel=Gerente&regiao=Central  ·  ?papel=RevOps&data=2017-09-30  ·  ?papel=Vendedor&vendedor=Vicki%20Laflamme
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from leadscorer.brief import seller_brief
from leadscorer.calibration import AGE_BANDS, HORIZON_DAYS
from leadscorer.data import enrich, load_tables, reference_date
from leadscorer.manager import agent_table, manager_must_acts, revops_findings, team_table
from leadscorer.scoring import (CAT_ALIVE, CAT_CRITICAL, CAT_FOCUS, CAT_FOLLOW, CAT_LAST, CAT_QUALIFY, CATEGORY_ORDER, SUPPORT_OK, fmt_n, money,
                                score_pipeline, summarize_categories)

HERE = Path(__file__).resolve().parent
RAW = HERE / "data" / "raw"
DOCS = HERE.parent / "docs"

st.set_page_config(page_title="Lead Scorer · segunda de manhã", layout="wide")

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
[data-testid="stSidebar"] [data-baseweb="select"] > div, [data-testid="stSidebar"] [data-baseweb="input"] > div, [data-testid="stSidebar"] input {
  background:#0A2C47 !important; color:var(--g4-cream) !important; border-color:rgba(245,244,243,0.35) !important; }
[data-testid="stSidebar"] [data-baseweb="select"] span, [data-testid="stSidebar"] [data-baseweb="select"] div { color:var(--g4-cream) !important; }
[data-testid="stSidebar"] svg { fill:var(--g4-cream) !important; }
[data-testid="stSidebar"] [role="radiogroup"] label p { color:var(--g4-cream) !important; }
[data-testid="stMetric"] { background:var(--g4-white); border:1px solid var(--g4-border); border-radius:10px; padding:14px 18px; }
[data-testid="stMetricLabel"] { font-size:12px; color:var(--g4-muted); text-transform:uppercase; letter-spacing:0.06em; }
[data-testid="stMetricValue"] { font-weight:800; font-size:24px; color:var(--g4-navy); }
[data-testid="stMetricValue"] > div { overflow:visible; white-space:nowrap; }
[data-testid="stDataFrame"] { border:1px solid var(--g4-border); border-radius:10px; overflow:hidden; }
.g4-card { background:var(--g4-white); border:1px solid var(--g4-border); border-radius:10px; padding:16px 20px; margin-bottom:12px; }
.g4-badge { display:inline-block; font-size:12px; font-weight:700; letter-spacing:0.04em; padding:3px 10px; border-radius:8px; margin-right:8px; }
.g4-badge--focar { background:var(--g4-navy); color:var(--g4-gold); }
.g4-badge--duas { background:var(--g4-brick); color:var(--g4-cream); }
.g4-badge--ultima { background:var(--g4-gold-dark); color:var(--g4-cream); }
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

BADGE = {CAT_FOCUS: "focar", "Focar agora": "focar", CAT_CRITICAL: "duas", "Primeiras duas semanas": "duas", CAT_LAST: "ultima", "Última janela": "ultima",
         CAT_FOLLOW: "manter", "Manter follow-up": "manter", CAT_ALIVE: "vivo", "Confirmar se está vivo": "vivo", "Cadastrar conta": "conta", CAT_QUALIFY: "qualificar"}
NOMES = {"opportunity_id": "deal", "category": "bloco", "account": "conta", "product": "produto", "list_value": "valor de lista", "age_days": "dias engajado",
         "p_win": "chance 90 d", "expected_value": "valor esperado", "needs_account": "sem conta", "next_step": "próximo passo", "manager": "gerente",
         "regional_office": "região", "abertos": "abertos", "acionaveis": "acionáveis", "focar": "focar agora", "duas_semanas": "2 semanas", "ultima_janela": "última janela",
         "confirmar_vivo": "confirmar se está vivo", "qualificar": "qualificar ou descartar", "fora_do_padrao_pct": "% além de 138 d", "sem_conta_pct": "% sem conta",
         "valor_lista": "valor de lista", "valor_esperado": "valor esperado", "hist_win_rate": "taxa histórica %", "hist_n": "n fechados", "sobrecarga": "sobrecarga",
         "deals": "deals", "sem_conta": "sem conta"}
MONEY_COLS = {"valor de lista", "valor esperado"}


def md(text: str) -> str:
    """Escapa cifrões para o Markdown do Streamlit não ler 'US$ 1 ... US$ 2' como fórmula."""
    return text.replace("$", "\\$")


def badge(cat: str) -> str:
    return f'<span class="g4-badge g4-badge--{BADGE.get(cat, "manter")}">{cat}</span>'


def card(item: dict) -> str:
    score = "sem score" if item["score"] is None else f'score {item["score"]}'
    idade = "" if item["idade"] is None else f' · {item["idade"]} dias'
    return (f'<div class="g4-card">{badge(item["tipo"])}<span class="g4-label">{item["deal"]} · {item["produto"]} · {money(item["valor"])}{idade}</span>'
            f'<div><span class="g4-score">{score}</span> &nbsp; <b>{item["conta"]}</b></div>'
            f'<div class="g4-why">{item["porque"]}</div><div class="g4-next">Próximo passo: {item["acao"]}</div></div>')


def show_table(df: pd.DataFrame, height: int | None = None, index: bool = True, extra: dict | None = None) -> None:
    """Tabela com nomes em português e dinheiro formatado como no resto da tela (US$ 1.234)."""
    view = df.rename(columns=NOMES).copy()
    for c in view.columns:
        if c in MONEY_COLS:
            view[c] = view[c].map(lambda v: money(v) if pd.notna(v) else "")
    cfg = {"score": st.column_config.ProgressColumn("score", min_value=0, max_value=100, format="%d"), "chance 90 d": st.column_config.NumberColumn(format="%.0f%%")}
    if extra:
        cfg.update(extra)
    if "chance 90 d" in view.columns:
        view["chance 90 d"] = view["chance 90 d"] * 100
    st.dataframe(view, use_container_width=True, height=height, hide_index=not index, column_config=cfg)


# ----------------------------------------------------------------------------- dados
if not (RAW / "sales_pipeline.csv").exists():
    st.markdown('<p class="g4-eyebrow">Lead Scorer</p><p class="g4-display">Faltam os <em>dados</em></p><hr class="g4-rule">', unsafe_allow_html=True)
    st.write("Coloque os 4 CSVs do dataset Kaggle em `solution/data/raw/` ou rode `python download_data.py`. Nada é inventado: sem os dados reais, o app não pontua.")
    st.stop()


@st.cache_data(show_spinner=False)
def _load():
    t = load_tables(RAW)
    return enrich(t), reference_date(t.pipeline)


@st.cache_data(show_spinner=False)
def _score(as_of: str):
    e, _ = _load()
    scored, cal = score_pipeline(e, pd.Timestamp(as_of))
    return scored, cal


enriched, ref_date = _load()

# ----------------------------------------------------------------------------- sidebar
qp = st.query_params


def _idx(options: list, key: str, default: int = 0) -> int:
    v = qp.get(key)
    return options.index(v) if v in options else default


with st.sidebar:
    st.markdown("### Lead Scorer")
    st.caption("Priorização do pipeline com o que a história dos 8.800 deals sustenta. O score ordena por valor esperado: preço de lista × chance de ganhar em 90 dias, que depende da idade do deal. "
               "Produto pesa pelo preço, não por taxa de fechamento; vendedor e setor não entram, porque nos dados não separam ganho de perda além do acaso.")
    papeis = ["Vendedor", "Gerente", "RevOps"]
    papel = st.radio("Quem está olhando", papeis, index=_idx(papeis, "papel"))
    data_default = pd.Timestamp(qp.get("data")).date() if qp.get("data") else ref_date.date()
    as_of = st.date_input("Data de referência", value=data_default, min_value=pd.Timestamp("2017-06-30").date(), max_value=ref_date.date(), format="DD/MM/YYYY",
                          help="O pipeline é reconstruído como estava nessa data e a chance é calibrada só com o que já tinha fechado até ela.")
    scored_all, cal = _score(str(as_of))
    agents_all = agent_table(scored_all, enriched, pd.Timestamp(as_of))
    regioes = ["Todas"] + sorted(agents_all["regional_office"].dropna().unique())
    regiao = st.selectbox("Região", regioes, index=_idx(regioes, "regiao"))
    managers = ["Todos"] + (sorted(agents_all.loc[agents_all["regional_office"] == regiao, "manager"].dropna().unique()) if regiao != "Todas" else sorted(agents_all["manager"].dropna().unique()))
    manager = st.selectbox("Gerente", managers, index=_idx(managers, "gerente"))
    pool = agents_all
    if regiao != "Todas":
        pool = pool[pool["regional_office"] == regiao]
    if manager != "Todos":
        pool = pool[pool["manager"] == manager]
    vendedores = sorted(pool.index)
    opcoes_vendedor = (["Todos"] if papel != "Vendedor" else []) + vendedores
    vendedor = st.selectbox("Vendedor", opcoes_vendedor, index=_idx(opcoes_vendedor, "vendedor"))
    st.markdown(f'<p class="g4-label">calibração: {cal.mode.split(":")[0]} · {len(cal.snapshots)} fins de mês · {fmt_n(cal.n_deals)} deals · horizonte {HORIZON_DAYS} d</p>', unsafe_allow_html=True)

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
    c1.metric("Abertos", b["resumo"]["abertos"])
    c2.metric("Com chance", b["resumo"]["acionaveis"])
    c3.metric("Focar agora", b["resumo"]["focar"])
    c4.metric("Confirmar se está vivo", b["resumo"]["confirmar_vivo"])
    c5.metric("Esperado 90 d", money(b["resumo"]["valor_esperado"]))
    st.write(md(b["abertura"]))
    st.markdown("### A pauta de hoje")
    for item in b["itens"]:
        st.markdown(card(item), unsafe_allow_html=True)

    st.markdown("### Todo o seu pipeline")
    cats = st.multiselect("Blocos", CATEGORY_ORDER, default=CATEGORY_ORDER)
    view = scored[scored["category"].isin(cats)]
    show_table(view[["opportunity_id", "category", "score", "account", "product", "list_value", "age_days", "p_win", "expected_value", "needs_account", "next_step"]], height=420, index=False)
    deal_id = st.selectbox("Ver o porquê de um deal", [""] + list(view["opportunity_id"]))
    if deal_id:
        r = scored.set_index("opportunity_id").loc[deal_id]
        st.markdown(card({"tipo": r["category"], "deal": deal_id, "conta": r["account"] if isinstance(r["account"], str) else "(sem conta)", "produto": r["product"],
                          "valor": r["list_value"], "score": None if pd.isna(r["score"]) else int(r["score"]), "idade": None if pd.isna(r["age_days"]) else int(r["age_days"]),
                          "porque": r["explanation"], "acao": r["next_step"]}), unsafe_allow_html=True)
        if r["support"] == SUPPORT_OK:
            deals_n, obs_n = cal.n_for(r["age_days"]); lo, hi = cal.ci_by_band[r["age_band"]]
            st.markdown('<p class="g4-label">como o score é calculado</p>', unsafe_allow_html=True)
            st.table(pd.DataFrame({"passo": [f"chance de ganhar em 90 d (faixa {r['age_band']} dias; {fmt_n(deals_n)} deals em {fmt_n(obs_n)} observações)",
                                            "valor de lista", "valor esperado = chance × valor", "posição entre os deals acionáveis"],
                                   "valor": [f"{r['p_win']:.0%} (entre {lo:.0%} e {hi:.0%})", money(r["list_value"]), money(r["expected_value"]), f"maior que {int(r['score'])}%, score {int(r['score'])}"]}))

# ----------------------------------------------------------------------------- gerente
elif papel == "Gerente":
    f = revops_findings(scored, agents)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Vendedores", len(agents))
    c2.metric("Abertos", f["deals_abertos"])
    c3.metric("Focar agora", int((scored["category"] == CAT_FOCUS).sum()))
    c4.metric("Confirmar se está vivo", f["deals_alem_138"], help="Deals com mais de 138 dias. Nesta base nenhum deal fechou depois disso.")
    c5.metric("Esperado 90 d", money(f["valor_esperado_acionavel"]))
    st.markdown("### O que fazer na segunda")
    acts = manager_must_acts(agents, scored)
    if not acts:
        st.write("Nenhuma ação de gestão com alvo concreto nesta seleção.")
    for a in acts:
        st.markdown(f'<div class="g4-card"><span class="g4-badge g4-badge--focar">{a["tipo"]}</span><b>{a["quem"]}</b><div class="g4-why">{a["porque"]}</div><div class="g4-next">{a["acao"]}</div></div>', unsafe_allow_html=True)
    st.markdown("### Por vendedor")
    st.caption(f"A taxa histórica é contexto, não nota: entre vendedores, a variação é compatível com o acaso (χ² p=0,26). Sobrecarga = deals abertos acima do P75 do time ({f['p75_abertos']}).")
    show_table(agents[["manager", "regional_office", "abertos", "acionaveis", "focar", "duas_semanas", "ultima_janela", "confirmar_vivo", "qualificar", "fora_do_padrao_pct", "sem_conta_pct", "valor_esperado", "hist_win_rate", "hist_n", "sobrecarga"]], height=520)
    st.markdown("### Por gerente e região")
    show_table(team_table(agents))

# ----------------------------------------------------------------------------- revops
else:
    f = revops_findings(scored, agents)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pipeline nominal", money(f["valor_lista_total"]), help="Soma do preço de lista de todos os deals abertos.")
    c2.metric("% do valor além de 138 d", f"{f['pct_valor_alem_138']}%", help=f"{fmt_n(f['deals_alem_138'])} deals, {money(f['valor_alem_138'])}. Nesta base nenhum deal fechou depois de 138 dias.")
    c3.metric("Acionável (lista)", money(f["valor_lista_acionavel"]), help=f"{fmt_n(f['deals_acionaveis'])} deals em Engaging até 138 dias.")
    c4.metric("Esperado 90 d", money(f["valor_esperado_acionavel"]))
    st.markdown("### O que os dados sustentam")
    st.write(md(f"Dos {fmt_n(f['deals_abertos'])} deals abertos, {fmt_n(f['deals_alem_138'])} ({str(f['pct_valor_alem_138']).replace('.', ',')}% do valor nominal) estão além do maior ciclo já concluído nesta base. "
                f"{fmt_n(f['deals_sem_conta'])} ({str(f['pct_sem_conta']).replace('.', ',')}%) não têm conta no CRM, e todo deal fechado, ganho ou perdido, tem conta. "
                f"{fmt_n(f['prospecting'])} estão em prospecção sem data de engajamento e {fmt_n(f['ultima_janela'])} estão na última janela (91 a 138 dias). "
                f"O que sobra com chance estimável vale {money(f['valor_lista_acionavel'])} de lista e {money(f['valor_esperado_acionavel'])} esperados em 90 dias."))
    st.markdown("### Blocos de ação")
    summ = summarize_categories(scored); summ.index.name = "bloco"
    show_table(summ)
    st.markdown("### Por região")
    por_regiao = scored.groupby("regional_office")["category"].value_counts().unstack(fill_value=0).reindex(columns=[c for c in CATEGORY_ORDER if c in scored["category"].unique()], fill_value=0)
    por_regiao.index.name = "região"
    st.caption("Toda a prospecção sem data de engajamento está em uma única região.")
    show_table(por_regiao)
    st.markdown("### Chance de ganhar em 90 dias, por idade do deal")
    st.caption(f"Painel de fins de mês ({', '.join(cal.snapshots) or cal.mode}), todos os deals em Engaging abertos em cada data e engajados a partir de 01/03/2017, só com o passado. "
               "Intervalo de 95% por bootstrap de deals. A coluna 'com conta hoje' usa o estado final da conta e é um limite otimista, não uma chance.")
    calib = pd.DataFrame({"faixa (dias)": [b for _, _, b in AGE_BANDS],
                          "chance de ganhar": [cal.p_by_band[b] for _, _, b in AGE_BANDS],
                          "intervalo 95%": [("" if cal.p_by_band[b] is None else f"{cal.ci_by_band[b][0]:.0%} a {cal.ci_by_band[b][1]:.0%}") for _, _, b in AGE_BANDS],
                          "fecha (ganho ou perda)": [cal.p_close_by_band[b] for _, _, b in AGE_BANDS],
                          "deals únicos": [cal.n_deals_by_band[b] for _, _, b in AGE_BANDS], "observações": [cal.n_obs_by_band[b] for _, _, b in AGE_BANDS],
                          "com conta hoje (otimista)": [cal.p_with_account_by_band.get(b) for _, _, b in AGE_BANDS],
                          "faixas agrupadas": [cal.pooled_from.get(b, "") for _, _, b in AGE_BANDS]})
    for c in ("chance de ganhar", "fecha (ganho ou perda)", "com conta hoje (otimista)"):
        calib[c] = calib[c].map(lambda v: "" if v is None or pd.isna(v) else f"{v:.0%}")
    st.dataframe(calib, hide_index=True, use_container_width=True)
    st.markdown("### O que não entra no score, e por quê")
    st.write("Vendedor (χ² p=0,26), vendedor × produto (gap igual ao acaso, p=0,89), produto como taxa de fechamento (spread 4,8 pp, p=0,37; o produto pesa só pelo preço), setor (p=0,97), porte da conta (p=0,50), subsidiária (p=0,74), desconto (valor fechado = 0,998 × preço). "
             "Cada teste está em docs/exploration_results.md com o código em solution/02_explore.py.")
    bt = DOCS / "backtest.json"
    if bt.exists():
        st.markdown("### Backtest walk-forward")
        data = json.loads(bt.read_text(encoding="utf-8"))
        rows = []
        for r in data["results"]:
            a = r["alive_block"]; vc = r.get("value_capture", {}).get("100", {}); cats = r.get("categories", {})
            rows.append({"data": r["as_of"], "tipo": "principal" if r["primary"] else "estabilidade", "Engaging em t": r["open_engaging_at_t"], "com score": r["scoreable"],
                         "win 90 d, 2 semanas": cats.get("critical", {}).get("win_rate"), "win 90 d, 15-90 d": cats.get("days_15_90", {}).get("win_rate"),
                         "win 90 d, última janela": cats.get("last_window", {}).get("win_rate"), "além de 138 d": a["n"],
                         "top-100 score: % do valor ganho": vc.get("score"), "top-100 só preço: %": vc.get("list_price_all_open")})
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True,
                     column_config={c: st.column_config.NumberColumn(format="%.0%") for c in ["win 90 d, 2 semanas", "win 90 d, 15-90 d", "win 90 d, última janela", "top-100 score: % do valor ganho", "top-100 só preço: %"]})
        ov = data["overlap"]
        st.caption(f"Datas principais sem sobreposição de desfechos: {', '.join(data['primary_dates'])}; as outras são leitura de estabilidade ({ov['won_in_2_or_more_dates']} dos {ov['won_unique']} ganhos aparecem em mais de uma data). "
                   "Na captura de valor, o score empata com ordenar por preço: o score só varia entre quatro faixas de idade e, dentro de cada faixa, ordena como o preço. O que o método faz é tirar do topo o que a história diz que não fecha e dizer o que fazer com cada bloco. Detalhes em docs/backtest.md.")
