"""Textos da analise de suporte, montados a partir dos numeros."""

from modulos.churn.textos import dec, md, pct  # noqa: F401  (mesmos formatadores em todo o sistema)


def reais(v):
    return "R$ " + f"{v:,.0f}".replace(",", ".")


def num(v):
    return f"{v:,.0f}".replace(",", ".")


def resumo_executivo(r):
    L = []
    v, info = r["volume"], r["info"]
    if "em_aberto" in v:
        L.append(f"**{num(v['total'])} chamados, {pct(v['em_aberto_%'])} ainda sem resolução** ({num(v['em_aberto'])} abertos "
                 "ou aguardando o cliente). Esse acúmulo é o gargalo que os dados mostram com mais clareza, e ele é igual "
                 "em todos os canais, prioridades e tipos, ou seja, é um problema de capacidade, não de um canal específico.")
    g = r["gargalos"]["por_dimensao"]
    if "prioridade" in g and info["n_duracao_valida"]:
        t = g["prioridade"]["tabela"].set_index("prioridade")
        crit = next((k for k in t.index if str(k).lower() in ("critical", "urgent")), None)
        if crit is not None:
            L.append(f"**A prioridade não muda o tempo de atendimento:** chamados '{crit}' levam {dec(t.loc[crit, 'mediana_h'], 1)} h "
                     f"(mediana), o mesmo que os demais ({dec(t.mediana_h.min(), 1)}–{dec(t.mediana_h.max(), 1)} h; "
                     f"p = {dec(g['prioridade']['p_tempo'])}). Na prática a fila não respeita a urgência.")
        sig = [d for d in g.values() if d["p_tempo"] < 0.05]
        nomes = ", ".join(d["rotulo"].lower() for d in g.values())
        if sig:
            L.append("**Diferença de tempo comprovada por** " + ", ".join(f"{d['rotulo'].lower()} (p = {dec(d['p_tempo'])})" for d in sig)
                     + ": veja a aba 'Onde trava'.")
        else:
            L.append(f"**{nomes.capitalize()} não explica(m) diferenças de tempo** com segurança estatística: "
                     + ", ".join(f"{d['rotulo'].lower()} (p = {dec(d['p_tempo'])})" for d in g.values()) + ".")
    if "resposta_mediana_h" in v or "escalado_%" in v:
        partes = []
        if "resposta_mediana_h" in v:
            partes.append(f"1ª resposta em {dec(v['resposta_mediana_h'], 1)} h (mediana)")
        if "escalado_%" in v:
            partes.append(f"{pct(v['escalado_%'])} dos chamados escalados")
        L.append("**Atendimento:** " + "; ".join(partes) + ".")
    s = r["satisfacao"]
    if s:
        sig = s["tabela"][s["tabela"].p_valor < 0.05]
        if len(sig):
            L.append("**O que impacta a satisfação:** " + ", ".join(sig["variável"]) + ".")
        else:
            L.append(f"**Nada nos dados impacta a satisfação** (média {dec(s['media'], 2)} de 5, em {num(s['avaliados'])} avaliações): "
                     + ", ".join(x.lower() for x in s["tabela"]["variável"]) + " têm p > 0,05. "
                     "A satisfação aqui não serve como termômetro; precisa ser medida de outro jeito.")
    d = r["desperdicio"]
    if d:
        top = d["por_prioridade"].iloc[0]
        L.append(f"**Desperdício:** {pct(d['estouraram_%'])} dos chamados medidos passaram da meta de tempo, somando "
                 f"{num(d['horas_medidas'])} h acima da meta ({reais(d['custo_medido'])}) nos {num(d['chamados_medidos'])} chamados com "
                 f"tempo válido. O maior desperdício recuperável está em '{top['prioridade']}' ({num(top['horas_acima_meta'])} h).")
    c = r["classificador"]
    if c:
        L.append(f"**A classificação automática funciona:** treinada em {num(c['n_treino'])} tickets de TI e testada em "
                 f"{num(c['n_teste'])} que o modelo nunca viu, acerta {pct(100 * c['acuracia'], 1)} das 8 categorias.")
    a = r["automacao"]
    if a:
        f = a["faixas"].set_index("faixa")
        L.append(f"**Onde a IA entra e onde para:** com confiança ≥ {pct(100 * r['premissas'].confianca_auto)} o ticket vai direto "
                 f"({pct(f.loc['Automático', 'tickets_%'])} dos tickets, {pct(f.loc['Automático', 'acerto_%'], 1)} de acerto); na faixa "
                 f"intermediária a IA sugere e o humano confirma; abaixo de {pct(100 * r['premissas'].confianca_humano)} e em "
                 "cancelamento, reembolso, prioridade crítica e permissão de acesso, **sempre humano**.")
        L.append(f"**Retorno estimado:** {pct(a['automatizado_%'])} do volume sai automático, economizando cerca de "
                 f"{num(a['horas_mes'])} h/mês de triagem ({reais(a['reais_mes'])}/mês), com as premissas da tela. "
                 "É um ganho modesto e honesto: o maior ganho está em atacar o acúmulo e fazer a prioridade valer.")
    return L


def explicacao_metodo(r):
    p, info = r["premissas"], r["info"]
    return [
        f"**Tempo de atendimento:** {info['regra_duracao']}.",
        "**Onde trava:** mediana e percentil 90 do tempo por canal, prioridade e tipo (intervalo de 95% da mediana por "
        "reamostragem); combinações só com pelo menos 30 chamados; teste de Kruskal-Wallis entre os grupos.",
        "**Acúmulo:** % de chamados abertos ou aguardando o cliente por grupo (teste qui-quadrado).",
        "**Satisfação:** Kruskal-Wallis por variável e correlação de Spearman com o tempo. p < 0,05 = impacto comprovado.",
        "**Desperdício:** horas acima da meta de cada prioridade × custo/hora (" + reais(p.custo_hora) + "); metas: "
        + ", ".join(f"{k} {v} h" for k, v in p.sla_h.items()) + ".",
        "**Classificador:** TF-IDF + regressão logística treinada em 80% do Dataset 2 e avaliada nos 20% restantes (nunca vistos).",
        f"**Automação:** confiança ≥ {pct(100 * p.confianca_auto)} = automático; entre {pct(100 * p.confianca_humano)} e "
        f"{pct(100 * p.confianca_auto)} = IA sugere; abaixo = humano. Bloqueados sempre: tipos "
        f"{', '.join(p.nunca_automatizar_tipos)}; prioridades {', '.join(p.nunca_automatizar_prioridades)}; "
        f"categorias {', '.join(p.nunca_automatizar_categorias)}.",
        f"**Retorno:** tickets/mês × parte elegível × cobertura da faixa × {dec(p.minutos_triagem, 0)} min de triagem "
        "(a faixa 'sugere' economiza metade).",
    ]
