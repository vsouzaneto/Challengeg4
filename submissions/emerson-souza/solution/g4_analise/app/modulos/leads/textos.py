"""Textos da analise de leads, montados a partir dos numeros."""

from modulos.churn.textos import dec, md, moeda, pct  # noqa: F401  (mesmos formatadores em todo o sistema)


def num(v):
    return f"{v:,.0f}".replace(",", ".")


def resumo_executivo(r):
    ab, hist, fat, curva, v = r["abertos"], r["historico"], r["fatores"], r["curva"], r["validacao"]
    L = []
    prosp = int((ab.lista == "Prospecção").sum())
    L.append(f"**{num(len(ab))} deals abertos** ({num(len(ab) - prosp)} em negociação e {num(prosp)} em prospecção), "
             f"somando {moeda(ab.valor.sum())} em valor e **{moeda(ab.valor_esperado.sum())} de valor esperado** "
             f"(preço × chance). No histórico, {pct(100 * hist.ganhou.mean())} dos deals fechados foram ganhos "
             f"({num(hist.ganhou.sum())} de {num(len(hist))}).")
    par = ab[ab.parado]
    if len(par):
        L.append(f"**{pct(100 * len(par) / len(ab))} do pipeline está parado:** {num(len(par))} deals abertos há mais de "
                 f"{r['cortes']['limite_parado']} dias, mais que o ciclo de QUALQUER deal já fechado na base "
                 f"({moeda(par.valor.sum())} em preço de tabela). São deals esquecidos ou que o CRM não atualizou. "
                 "O primeiro trabalho da semana é confirmar se eles existem.")
    if curva:
        L.append(f"**Deal perdido morre cedo:** a mediana de um deal perdido é {dec(curva['mediana_perdido'], 0)} dias, a de um ganho "
                 f"é {dec(curva['mediana_ganho'], 0)} dias. Quem passa das primeiras semanas ganha mais: por isso a idade do deal "
                 "entra no score, sempre comparada com os deals que chegaram à mesma idade (sem usar o futuro).")
    comp = [x for x in fat.values() if x["evidencia"] == "comprovado"]
    if comp:
        L.append("**Fatores com diferença comprovada:** " + ", ".join(f"{x['rotulo'].lower()} (p = {dec(x['p_valor'], 3)})" for x in comp) + ".")
    else:
        partes = [f"{x['rotulo'].lower()} {pct(x['tabela']['taxa_%'].min())}–{pct(x['tabela']['taxa_%'].max())} "
                  f"(p = {dec(x['p_valor'])})" for x in fat.values()]
        L.append("**Vendedor, produto, setor e porte mudam pouco a chance, e nenhum com comprovação estatística:** "
                 + "; ".join(partes) + ". Eles entram no score com peso reduzido e marcados como indício.")
    if v:
        L.append(f"**Teste honesto no passado:** numa foto de {v['data_foto']:%d/%m/%Y}, o score aprendeu só com o que já tinha "
                 f"fechado e pontuou {num(v['n_teste'])} deals abertos. Ele separou ganho de perda com AUC {dec(v['auc'])} "
                 "(0,50 = acaso). " + ("Ou seja, **esta base não permite prever quem vai ganhar**; a prioridade vem de "
                                       "**valor e de o deal estar vivo**, que são fatos, não previsões."
                                       if v["auc"] < 0.6 else "O score tem poder de previsão útil."))
    vivos = ab[ab.lista == "Foco"]
    if len(vivos):
        top = vivos.head(max(1, int(0.2 * len(vivos))))
        L.append(f"**Segunda-feira:** comece pelos {num(len(top))} deals vivos de maior valor esperado "
                 f"({moeda(top.valor_esperado.sum())})"
                 + ("; depois requalifique os parados" if ab.parado.any() else "")
                 + ("; por último, a prospecção" if (ab.lista == "Prospecção").any() else "") + ". "
                 "A lista 'Minha segunda-feira' já vem nessa ordem, com os 3 motivos de cada score e a próxima ação.")
    return L


def explicacao_metodo(r):
    p, c = r["premissas"], r["cortes"]
    tempo = [] if not r["curva"] else [
        "**Tempo aberto:** para um deal com N dias, a taxa de ganho dos deals do histórico que chegaram a N dias. "
        "A duração total do ciclo não entra (só se sabe depois de fechar).",
        f"**Parado:** aberto há mais que {c['limite_parado']} dias (o maior ciclo já fechado). Perde {dec(p.penalidade_parado, 0)} "
        "pontos (hipótese: não há deal fechado com essa idade para medir).",
    ]
    return [
        f"**Base:** taxa de ganho do histórico (deals ganhos ÷ ganhos + perdidos) = {pct(100 * c['base'])}.",
        f"**Fatores (vendedor, produto, setor, porte):** taxa de ganho de cada grupo no histórico, suavizada com "
        f"{p.suavizacao} deals 'virtuais' na média (grupo pequeno não pesa demais). Pontos = taxa suavizada − média. "
        "Teste qui-quadrado diz se a diferença é comprovada (p < 0,05), indício (p < 0,10) ou não comprovada.",
        "**Porte da conta:** número de funcionários em 4 faixas iguais (Pequena, Média, Grande, Muito grande).",
    ] + tempo + [
        "**Score** = base + pontos, de 1 a 99 = chance estimada de ganhar, em %.",
        f"**Faixas** (entre os deals vivos): Quente = {pct(p.quente_pct)} de maior score; Frio = {pct(p.frio_pct)} de menor; "
        "o resto é Morno. Deals parados ficam na faixa 'Parado'.",
        f"**Valor esperado** = chance × valor do deal ({r['info']['regra_valor']}). É a ordem da lista (não só o valor, não só a chance).",
        "**Validação:** foto do passado (70% dos fechamentos): aprende só com o que fechou até a data e mede, nos deals que "
        "estavam abertos nela, se o score separa ganho de perda (AUC).",
    ]
