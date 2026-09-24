"""Tela do modulo Midia: resumo, o que gera engajamento, patrocinio, audiencia, estrategia, painel, sanidade, relatorio."""

import json
import os
from dataclasses import asdict

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import servicos
from nucleo import leitura, sessoes, visual
from nucleo.exportar import botao_salvar
from nucleo.visual import cores, selo, selo_evidencia
from nucleo.carregar import tabelas_da_sessao
from . import relatorio
from .analise import Premissas, analisar, recomendar_post
from .textos import dec, explicacao_metodo, md, num, pct, resumo_executivo

AZUL, VERMELHO, LARANJA, CINZA, VERDE = "#2E86AB", "#D1495B", "#F2A541", "#9AA5B1", "#3BB273"


@st.cache_resource(show_spinner="Analisando os posts (≈30 s, só na primeira vez)...", max_entries=12)
def _analisar(sessao_id, versoes, premissas_json):
    """Resultado guardado no disco (servicos.analisar_com_cache) e na memoria: trocar de aba nao recalcula nada."""
    return servicos.analisar_com_cache(sessoes.obter(sessao_id), json.loads(premissas_json))


def premissas_na_tela(chave):
    p = Premissas()
    with st.expander("Premissas da análise (mude e tudo é recalculado)", icon=":material/tune:"):
        c1, c2, c3 = st.columns(3)
        ef = c1.slider("Diferença mínima para dizer que 'funciona' (%)", 1.0, 30.0, p.efeito_minimo_pct, 1.0, key=f"{chave}_ef")
        cm = c2.number_input("Custo do patrocínio: US$ por 1.000 seguidores", 0.5, 500.0, p.custo_mil_seguidores, 0.5, key=f"{chave}_cm",
                             help="O dataset não tem custo. Use o valor que a empresa paga.")
        mn = c2.number_input("Mínimo de posts por combinação", 50, 5000, p.min_posts_grupo, 50, key=f"{chave}_mn")
        san = c3.slider("Efeito injetado no teste de sanidade (%)", 1.0, 30.0, p.efeito_sanidade_pct, 1.0, key=f"{chave}_san")
    return Premissas(efeito_minimo_pct=ef, custo_mil_seguidores=cm, min_posts_grupo=int(mn), efeito_sanidade_pct=san)


def render(sessao):
    p = premissas_na_tela(sessao["id"])
    versoes = tuple(os.path.getmtime(c) for c in sessao["arquivos"].values())
    try:
        r = _analisar(sessao["id"], versoes, json.dumps(asdict(p), sort_keys=True, default=list))
    except (KeyError, ValueError) as erro:
        st.error(f"Falta um campo obrigatório nos dados para esta análise: {erro}. Confira o De/Para na aba Dados.")
        return None
    abas = st.tabs(visual.abas(["Resumo executivo", "O que gera engajamento", "Patrocínio", "Audiência", "Estratégia",
                    "Painel semanal", "Recomendar post", "Sanidade e método", "Qualidade dos dados", "Relatório",
                    "Como ler"]))
    with abas[0]:
        aba_resumo(r)
    with abas[1]:
        aba_drivers(r)
    with abas[2]:
        aba_patrocinio(r)
    with abas[3]:
        aba_audiencia(r)
    with abas[4]:
        aba_estrategia(r)
    with abas[5]:
        aba_painel(r)
    with abas[6]:
        aba_recomendar(r, p, sessao["id"])
    with abas[7]:
        aba_sanidade(r)
    with abas[8]:
        for q in r["qualidade"]:
            st.write("• " + md(q))
    with abas[9]:
        aba_relatorio(r, sessao)
    with abas[10]:
        aba_como_ler()
    return r


def _barras_ic(t, titulo_y="engajamento (%)", media=None, altura=340):
    fig = go.Figure(go.Bar(x=t.grupo.astype(str), y=t.media, marker_color=cores(len(t)),
                           error_y=dict(type="data", symmetric=False, array=t.ic_max - t.media, arrayminus=t.media - t.ic_min),
                           customdata=t.posts, hovertemplate="%{x}: %{y:.2f}% (n=%{customdata})<extra></extra>"))
    if media is not None:
        fig.add_hline(y=media, line_dash="dot", annotation_text="média")
    lo, hi = float(t.ic_min.min()), float(t.ic_max.max())
    folga = max(hi - lo, 0.05)
    fig.update_layout(height=altura, yaxis_title=titulo_y, yaxis_range=[lo - folga, hi + folga], margin=dict(t=10, b=10))
    return fig


# ------------------------------------------------------------------ abas

def aba_resumo(r):
    n = r["numeros"]
    c = st.columns(4)
    c[0].metric("Posts", num(n["posts"]))
    c[1].metric("Criadores", num(n.get("criadores", 0)))
    c[2].metric("Engajamento médio", f"{dec(n['eng_medio_%'], 1)}%", help="(curtidas + compartilhamentos + comentários) ÷ views")
    c[3].metric("Patrocinados", pct(n.get("patrocinados_%", 0)))
    st.subheader("O que está acontecendo")
    for linha in resumo_executivo(r):
        st.markdown("• " + md(linha))
    drv = r["drivers"]
    t = [{"dimensão": v["rotulo"], "diferença entre o melhor e o pior grupo (%)": round(v["efeito_%"], 2),
          "p": round(v["p_valor"], 3), "veredito": v["veredito"]} for v in drv.values()]
    st.subheader("Cada dimensão testada")
    st.dataframe(t, hide_index=True, width="stretch")
    st.caption(f"'Funciona' exige p < 0,05 **e** diferença ≥ {dec(r['premissas'].efeito_minimo_pct, 0)}% (premissa).")


def aba_drivers(r):
    drv = r["drivers"]
    st.subheader("Engajamento por dimensão (com intervalo de 95%)")
    esc = st.selectbox("Dimensão", list(drv), format_func=lambda k: drv[k]["rotulo"])
    d = drv[esc]
    st.plotly_chart(_barras_ic(d["tabela"], media=r["numeros"]["eng_medio_%"]), width="stretch")
    st.caption(f"p = {dec(d['p_valor'], 3)} · diferença máxima {dec(d['efeito_%'], 2)}% → **{d['veredito']}**. O eixo está "
               "ampliado: se as barrinhas se cruzam, os grupos são iguais na prática.")
    st.dataframe(d["tabela"].round(3), hide_index=True, width="stretch")
    cb = r["combinacoes"]
    if cb:
        st.subheader("Combinações específicas (ex.: 'imagem de lifestyle no RedNote')")
        st.write(f"{cb['testadas']} combinações com ≥ {r['premissas'].min_posts_grupo} posts. **{cb['p_brutos_abaixo_005']}** parecem "
                 f"melhores num teste comum (p < 0,05), mas **{cb['aprovadas']}** passam quando se corrige para o número de testes "
                 f"(p < {dec(cb['limite_p'], 4)}). Esse é o erro de 'achar o vencedor' por acaso.")
        st.dataframe(cb["tabela"].round(4), hide_index=True, width="stretch")
    h = r["hashtags"]
    if h:
        st.subheader("Hashtags")
        st.write(f"{num(h['distintas'])} hashtags diferentes; {pct(h['sem_hashtag_%'])} dos posts sem hashtag. As mais usadas:")
        st.dataframe(h["tabela"].round(3), hide_index=True, width="stretch")
        if h["pares_testados"]:
            st.write("Pares de hashtags usados juntos (≥ 30 posts):")
            st.dataframe(h["pares_melhores"].round(3), hide_index=True, width="stretch")
        else:
            st.caption("Nenhum par de hashtags aparece junto em 30 posts ou mais: não há combinação com amostra para testar.")


def aba_patrocinio(r):
    pat = r["patrocinio"]
    if not pat:
        st.info("A base não informa quais posts são patrocinados.")
        return
    st.subheader("Patrocinado × orgânico, comparação justa")
    c = st.columns(3)
    for i, (k, rot) in enumerate((("engajamento", "Engajamento"), ("alcance", "Views"), ("compartilhamentos", "Compartilhamentos"))):
        x = pat.get(k)
        if x:
            c[i].metric(rot, f"{dec(x['diferenca_%'], 2)}%", help="Diferença patrocinado − orgânico dentro do mesmo grupo")
            c[i].caption(f"p = {dec(x['p_valor'], 2)}")
    e = pat["engajamento"]
    st.write(f"Comparação dentro de **{e['estratos']} grupos** de mesma plataforma, categoria e faixa de seguidores "
             f"({num(e['n_patrocinado'])} patrocinados × {num(e['n_organico'])} orgânicos). Veredito: **{pat['veredito']}**.")
    if len(pat["por_faixa"]):
        st.subheader("Em que condições? Por tamanho de criador")
        pf = pat["por_faixa"]
        fig = px.bar(pf, x="faixa", y="diferenca_%", color_discrete_sequence=[AZUL], text=pf["diferenca_%"].map(lambda v: f"{v:+.2f}%".replace(".", ",")))
        fig.add_hline(y=0, line_color=CINZA)
        fig.update_layout(height=300, yaxis_title="patrocinado − orgânico (%)", margin=dict(t=10, b=10))
        st.plotly_chart(fig, width="stretch")
        st.dataframe(pf.round(3), hide_index=True, width="stretch")
    if "custo" in pat:
        st.subheader("Custo implícito (premissa editável)")
        cu = pat["custo"]
        c1, c2 = st.columns(2)
        fig = px.bar(cu, x="faixa_seguidores", y="views_medias", color="faixa_seguidores", color_discrete_sequence=cores(len(cu)))
        fig.update_layout(height=280, title="Views médias por faixa: iguais", yaxis_range=[0, cu.views_medias.max() * 1.15], margin=dict(t=40, b=10))
        c1.plotly_chart(fig, width="stretch")
        fig = px.bar(cu, x="faixa_seguidores", y="custo_por_interacao", color_discrete_sequence=[VERMELHO])
        fig.update_layout(height=280, title="Custo por interação (US$): sobe com o tamanho", margin=dict(t=40, b=10))
        c2.plotly_chart(fig, width="stretch")
        st.dataframe(cu.round(3), hide_index=True, width="stretch")
        st.markdown(md(f"**Política de patrocínio:** pagar por resultado (views/interações entregues), com teto no preço médio de um "
                       f"criador de 10K–50K (US$ {num(pat['custo_referencia'])} por post pela premissa). Mínimo de seguidores: não há "
                       "ganho em exigir mais; o critério mínimo é o criador entregar engajamento dentro do intervalo normal da "
                       f"plataforma. Economia estimada: ~{pct(pat['economia_%'])} do gasto atual."))


def aba_audiencia(r):
    a = r["audiencia"]
    st.subheader("Qual audiência engaja mais, por plataforma")
    if a is None:
        st.info("Sem dados de audiência.")
        return
    st.dataframe(a.round(3), hide_index=True, width="stretch")
    st.caption("Com p > 0,05 o 'melhor' e o 'pior' grupo são iguais na prática: nenhuma audiência engaja mais nesta base.")
    cl = r.get("clusters")
    if cl:
        st.subheader("Grupos de criadores pelo perfil da audiência (clustering)")
        st.dataframe(cl["tabela"].round(3), hide_index=True, width="stretch")
        st.caption(f"{cl['k']} grupos formados automaticamente pela mistura de idade, gênero e local da audiência de cada criador "
                   f"(k-means). Diferença de engajamento entre os grupos: p = {dec(cl['p_valor'], 2)} → "
                   + ("existe diferença." if cl["p_valor"] < 0.05 else "nenhum perfil de audiência engaja mais."))
    drv = r["drivers"]
    for k in ("audiencia_idade", "audiencia_genero", "audiencia_local"):
        if k in drv:
            d = drv[k]
            st.write(f"**{d['rotulo']}** — p = {dec(d['p_valor'], 3)} · {d['veredito']}")
            st.plotly_chart(_barras_ic(d["tabela"], media=r["numeros"]["eng_medio_%"], altura=260), width="stretch")


def aba_recomendar(r, p, chave):
    st.subheader("Vou publicar um post: o que esperar e o que mudar?")
    st.caption("Escolha como é o post. O sistema procura posts parecidos no histórico e mostra o engajamento esperado e se "
               "alguma troca (formato ou plataforma) daria mais resultado.")
    c = r["posts"]
    campos = [(k, rot) for k, rot in (("plataforma", "Plataforma"), ("tipo", "Formato"), ("categoria", "Categoria"),
                                      ("faixa_seguidores", "Tamanho do criador"), ("patrocinado_txt", "Patrocínio")) if k in c]
    cols = st.columns(len(campos))
    escolhas = {}
    for col, (k, rot) in zip(cols, campos):
        opcoes = ["(qualquer)"] + sorted(c[k].dropna().astype(str).unique())
        v = col.selectbox(rot, opcoes, key=f"{chave}_rec_{k}")
        escolhas[k] = None if v == "(qualquer)" else v
    rec = recomendar_post(c, p, **escolhas)
    if "eng_%" not in rec:
        st.warning(f"Só {rec['n']} posts parecidos no histórico: pouco para estimar. Deixe algum campo como '(qualquer)'.")
        return
    k = st.columns(3)
    k[0].metric("Engajamento esperado", f"{dec(rec['eng_%'], 2)}%", help=f"Média de {num(rec['n'])} posts parecidos")
    k[1].metric("Faixa normal (80% dos posts)", f"{dec(rec['faixa_normal'][0], 1)}% a {dec(rec['faixa_normal'][1], 1)}%")
    k[2].metric("Views esperadas", num(rec["views"]))
    st.caption(f"Baseado em {num(rec['n'])} posts parecidos. Intervalo de 95% da média: {dec(rec['ic'][0], 2)}% a {dec(rec['ic'][1], 2)}%.")
    st.markdown("**Recomendação**")
    if not rec["alternativas"]:
        st.write("• Sem alternativas com amostra suficiente para comparar.")
    for a in rec["alternativas"]:
        nome = "formato" if a["campo"] == "tipo" else "plataforma"
        if a["p_valor"] < 0.05 and a["ganho_%"] >= p.efeito_minimo_pct:
            st.write(f"• Trocar o {nome} para **{a['melhor']}** deve render ~{dec(a['ganho_%'], 1)}% a mais (p = {dec(a['p_valor'], 3)}).")
        else:
            st.write(f"• Trocar o {nome} não muda o resultado (o melhor, {a['melhor']}, fica só {dec(a['ganho_%'], 2)}% acima; "
                     f"p = {dec(a['p_valor'], 2)}). Escolha o {nome} mais barato e rápido de produzir.")
    if escolhas.get("patrocinado_txt") == "patrocinado":
        pat = r["patrocinio"]
        if pat and "custo_referencia" in pat:
            st.write(md(f"• Patrocinado: pague por resultado, com teto de US$ {num(pat['custo_referencia'])} por post "
                        "(preço de um criador de 10K–50K pela premissa); criador maior não entrega mais."))
    st.caption("Use o post publicado para conferir no Painel semanal: se ficar fora da faixa normal, vale investigar.")


def aba_estrategia(r):
    st.subheader("Estratégia priorizada — o quê, para quem, quando e com que evidência")
    for a in r["estrategia"].itertuples():
        cor = selo_evidencia(a.evidencia)
        with st.container(border=True):
            st.markdown(f"**{a.prioridade}. {a.acao}** {cor}")
            st.write(md(a.o_que))
            st.caption(md(f"Para quem: {a.para_quem} · Quando: {a.quando} · Por quê: {a.por_que}"))
    st.caption("Selo verde = fato nos dados · azul = decisão por custo (o resultado é igual, então vence o mais barato) · cinza = sem evidência: testar.")
    st.subheader("Quick wins desta semana")
    for i, q in enumerate(r["quick_wins"], 1):
        st.markdown(f"{i}. {md(q)}")
    st.subheader("O que NÃO funciona (parar de fazer)")
    for v in r["drivers"].values():
        if v["veredito"].startswith("sem"):
            melhor = v["tabela"].iloc[0]
            st.markdown(f"• Escolher **{v['rotulo'].lower()}** esperando mais engajamento: o 'melhor' ({melhor.grupo}) fica só "
                        f"{dec(melhor['vs_media_%'], 2)}% acima da média (p = {dec(v['p_valor'], 2)}).")


def aba_painel(r):
    s = r["painel"]
    st.subheader("Painel semanal para acompanhar o dia a dia")
    if s is None or not len(s):
        st.info("Sem datas nos posts.")
        return
    plats = sorted(s.plataforma.unique()) if "plataforma" in s else []
    esc = st.multiselect("Plataformas", plats, default=plats, placeholder="Todas") if plats else []
    v = s[s.plataforma.isin(esc)] if esc else s
    geral = v.groupby("semana").apply(lambda x: (x.eng * x.posts).sum() / x.posts.sum(), include_groups=False).rename("eng").reset_index()
    m, dp = geral.eng.mean(), geral.eng.std()
    fig = go.Figure()
    fig.add_hrect(y0=m - 2 * dp, y1=m + 2 * dp, fillcolor=CINZA, opacity=0.15, line_width=0, annotation_text="faixa normal")
    for plat in (esc or plats):
        x = v[v.plataforma == plat]
        fig.add_trace(go.Scatter(x=x.semana, y=x.eng, mode="lines", name=plat, opacity=0.6))
    fig.add_trace(go.Scatter(x=geral.semana, y=geral.eng, mode="lines", name="todas", line=dict(color="black", width=3)))
    fig.update_layout(height=380, yaxis_title="engajamento semanal (%)", margin=dict(t=10, b=10))
    st.plotly_chart(fig, width="stretch")
    fora = geral[(geral.eng < m - 2 * dp) | (geral.eng > m + 2 * dp)]
    st.caption(f"Faixa normal = média ± 2 desvios das semanas. Semana fora da faixa merece olhar; dentro dela, é oscilação comum. "
               f"Semanas fora: {len(fora)} de {len(geral)}.")
    ult = geral.tail(4).eng.mean() - geral.iloc[-8:-4].eng.mean() if len(geral) >= 8 else float("nan")
    if ult == ult:
        st.metric("Últimas 4 semanas × 4 anteriores", f"{ult:+.2f} p.p.")


def aba_sanidade(r):
    st.subheader("Teste de sanidade: a ferramenta enxerga um efeito quando ele existe?")
    st.caption("Feito numa CÓPIA dos dados: os dados reais não são alterados.")
    for k, v in r["sanidade"].items():
        rot = "Patrocínio" if k == "patrocinio" else f"Formato '{v['grupo']}'"
        c = st.columns(4)
        c[0].markdown(f"**{rot}**")
        c[1].metric("Efeito injetado", f"+{dec(v['injetado_%'], 0)}%")
        c[2].metric("Efeito encontrado", f"{dec(v['encontrado_%'], 1)}%")
        c[3].metric("Resultado", "Encontrou" if v["achou"] else "Não encontrou")
    m = r["modelo"]
    if m:
        st.subheader("Modelo preditivo de engajamento (diferencial)")
        c = st.columns(2)
        c[0].metric("Regressão linear (R²)", f"{dec(m['r2_lr'][0], 3)}")
        c[1].metric("Floresta aleatória (R²)", f"{dec(m['r2_rf'][0], 3)}")
        st.caption(f"Validação cruzada em 5 partes com {m['variaveis']} variáveis e {num(m['amostra'])} posts. R² perto de 0 = as "
                   "características do post não preveem o engajamento nesta base.")
    st.subheader("Como os números foram calculados")
    for x in explicacao_metodo(r):
        st.markdown("• " + md(x))


def aba_relatorio(r, sessao):
    st.write("Relatório para o Head de Marketing: resumo, estratégia priorizada, quick wins, patrocínio, sanidade e limitações.")
    md_txt = relatorio.markdown(r, sessao["nome"])
    c1, c2 = st.columns(2)
    botao_salvar(c1, "Salvar PDF", lambda: relatorio.pdf(r, sessao["nome"]), "estrategia_social.pdf", key=f"pdf_{sessao['id']}")
    botao_salvar(c2, "Salvar Markdown", md_txt, "estrategia_social.md", key=f"md_{sessao['id']}")
    with st.expander("Pré-visualizar"):
        st.markdown(md_txt)


def aba_como_ler():
    st.markdown("""
**Resumo executivo** — a história em 5 minutos, com os números.

**O que gera engajamento** — cada dimensão (plataforma, formato, tamanho do criador…) com a barrinha do intervalo de 95%.
O eixo é ampliado de propósito: se as barrinhas se cruzam, os grupos são iguais. As **combinações** mostram por que uma
frase como "imagem de lifestyle no RedNote engaja mais" pode ser só acaso.

**Patrocínio** — patrocinado × orgânico comparados dentro do mesmo grupo (plataforma, categoria e tamanho do criador),
o custo por interação por faixa de criador e a política de patrocínio.

**Estratégia** — o que fazer, para quem, quando e com que evidência, na ordem; quick wins; o que parar de fazer.

**Painel semanal** — para acompanhar toda segunda-feira. A faixa cinza é o "normal": fora dela, vale investigar.

**Recomendar post** — descreva o post que vai publicar e veja o engajamento esperado e se alguma troca renderia mais.

**Sanidade e método** — a prova de que a ferramenta encontra efeito quando ele existe, e como cada número foi calculado.

**Premissas** (no topo) — diferença mínima que importa, custo do patrocínio e o efeito do teste de sanidade.
""")
