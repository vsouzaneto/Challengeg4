"""Textos da analise de midia, montados a partir dos numeros."""

from modulos.churn.textos import dec, md, moeda, pct  # noqa: F401  (mesmos formatadores em todo o sistema)


def num(v):
    return f"{v:,.0f}".replace(",", ".")


def resumo_executivo(r):
    n, drv, pat, cb, san = r["numeros"], r["drivers"], r["patrocinio"], r["combinacoes"], r["sanidade"]
    L = [f"**{num(n['posts'])} posts** de {num(n.get('criadores', 0))} criadores, engajamento médio de **{dec(n['eng_medio_%'], 1)}%** "
         f"(interações ÷ views) e {num(n['views_mediana'])} views por post (mediana)."]
    iguais = [v["rotulo"].lower() for v in drv.values() if v["veredito"].startswith("sem")]
    reais = [v["rotulo"].lower() for v in drv.values() if v["veredito"].startswith("funciona")]
    if reais:
        L.append("**O que gera engajamento de verdade:** " + ", ".join(reais) + ".")
    L.append(f"**Nada do que a empresa controla muda o engajamento** nesta base: {len(iguais)} de {len(drv)} dimensões testadas "
             f"(plataforma, formato, categoria, tamanho do criador, duração, hashtags, dia, horário, idioma, audiência) ficam dentro "
             f"do ruído, com diferença máxima de {dec(max(v['efeito_%'] for v in drv.values()), 2)}% entre o melhor e o pior grupo. " + ("Combinações específicas também não: "
             f"das {cb['testadas']} testadas, {cb['p_brutos_abaixo_005']} parecem vencedoras num teste comum e **nenhuma** "
             "sobrevive à correção para muitos testes." if cb and cb["aprovadas"] == 0 else ""))
    if pat and pat["engajamento"]:
        e, a = pat["engajamento"], pat["alcance"]
        L.append(f"**Patrocínio não aumenta engajamento nem alcance** (comparação justa, dentro de {e['estratos']} grupos de mesma "
                 f"plataforma, categoria e tamanho de criador): engajamento {dec(e['diferenca_%'], 2)}% (p = {dec(e['p_valor'])}), "
                 f"views {dec(a['diferenca_%'], 2)}% (p = {dec(a['p_valor'])}). Vale para todas as faixas de criador.")
    if pat and "custo" in pat:
        L.append(f"**Criador grande custa mais e entrega o mesmo:** as views não crescem com os seguidores, então o custo por "
                 f"interação sobe junto com o tamanho. Pagando pelo preço de um criador de 10K–50K, o gasto com patrocínio cairia "
                 f"~{pct(pat['economia_%'])} (premissa de custo editável). **Política:** pagar por resultado entregue, com teto no "
                 "preço da faixa pequena, e patrocinar só com teste A/B.")
    if san:
        partes = []
        if "patrocinio" in san:
            partes.append(f"injetamos +{dec(san['patrocinio']['injetado_%'], 0)}% no engajamento dos patrocinados e a ferramenta "
                          f"achou +{dec(san['patrocinio']['encontrado_%'], 1)}%")
        if "tipo" in san:
            partes.append(f"injetamos +{dec(san['tipo']['injetado_%'], 0)}% em '{san['tipo']['grupo']}' e ela apontou esse formato "
                          "como o melhor")
        L.append("**Por que confiar no 'não há diferença':** num teste de sanidade (numa cópia dos dados), " + "; ".join(partes)
                 + ". Ou seja, quando existe efeito, a ferramenta encontra.")
    m = r["modelo"]
    if m:
        L.append(f"**Prever o engajamento antes de postar não é possível com estes dados:** o modelo explica "
                 f"{dec(100 * max(m['r2_rf'][0], 0), 1)}% da variação (validação cruzada).")
    L.append("**Segunda-feira:** " + " ".join(f"({i}) {q}" for i, q in enumerate(r["quick_wins"], 1)))
    return L


def explicacao_metodo(r):
    p = r["premissas"]
    return [
        "**Engajamento** = (curtidas + compartilhamentos + comentários) ÷ views, em %. Também olhamos views e compartilhamentos separados.",
        "**O que gera engajamento:** média por grupo com intervalo de 95% e teste de Kruskal-Wallis. Só 'funciona' se p < 0,05 "
        f"**e** a diferença entre o melhor e o pior grupo for ≥ {dec(p.efeito_minimo_pct, 0)}% (premissa).",
        f"**Combinações** (plataforma × formato × categoria × tamanho, grupos com ≥ {p.min_posts_grupo} posts): cada uma contra o "
        "resto, com correção de Bonferroni (quanto mais testes, mais 'achados' por acaso).",
        "**Patrocínio justo:** a diferença patrocinado − orgânico é calculada DENTRO de cada grupo de mesma plataforma, categoria e "
        "faixa de seguidores; depois testada (teste t). Assim tamanho, plataforma e categoria não confundem o resultado.",
        f"**Custo implícito:** premissa de US$ {dec(p.custo_mil_seguidores, 0)} por 1.000 seguidores por post patrocinado (o dataset "
        "não tem custo). Custo por interação = custo ÷ interações.",
        f"**Teste de sanidade:** numa cópia, soma +{dec(p.efeito_sanidade_pct, 0)}% ao engajamento de um grupo e roda a mesma análise.",
        "**Modelo preditivo:** regressão linear e floresta aleatória, avaliadas em validação cruzada (5 partes).",
        "**Faixas de seguidores:** <10K · 10K–50K · 50K–100K · 100K–500K · 500K+.",
    ]
