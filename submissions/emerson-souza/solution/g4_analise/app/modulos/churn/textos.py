"""Textos da analise de churn, montados a partir dos numeros (nada escrito 'na mao')."""

import numpy as np


def moeda(v):
    return "US$ " + f"{v:,.0f}".replace(",", ".")


def valor(r, v, mes=False):
    """Dinheiro (US$) ou, se a base nao tem receita, contagem de clientes."""
    if r["base"].get("sem_receita"):
        return f"{v:,.0f} clientes".replace(",", ".")
    return moeda(v) + ("/mês" if mes else "")


def dec(v, casas=2):
    return f"{v:.{casas}f}".replace(".", ",")


def md(texto):
    """Escapa o cifrao para o Markdown do Streamlit/GitHub nao tratar US$ como formula."""
    return texto.replace("$", "\\$")


def pct(v, casas=0):
    return f"{v:.{casas}f}%".replace(".", ",")


def resumo_executivo(r):
    b, par = r["base"], r["paradoxo"]
    linhas = []
    linhas.append(
        f"**{b['canceladas']:,} de {b['clientes']:,} clientes cancelaram".replace(",", ".") + f" ({pct(100 * b['taxa_churn'], 1)})**, "
        f"com intervalo de confiança de 95% entre {pct(100 * b['ic_taxa'][0])} e {pct(100 * b['ic_taxa'][1])}. "
        + (f"A receita mensal perdida é de **{moeda(b['mrr_perdido'])}** (MRR da última assinatura de cada conta cancelada). "
           f"Ainda estão ativos {moeda(b['mrr_ativo'])} por mês." if not b.get("sem_receita") else
           "A base não tem receita: os valores abaixo são contagem de clientes."))

    # paradoxo do CEO
    frases = []
    if "variacao_uso_%" in par:
        v = par["variacao_uso_%"]
        frases.append(f"o uso total variou {pct(v, 1)} do primeiro ao último trimestre, ou seja, "
                      + ("praticamente estável" if abs(v) < 5 else "cresceu" if v > 0 else "caiu"))
    if "satisfacao" in par:
        sa = par["satisfacao"]
        frases.append(f"a satisfação média é {dec(sa['media_geral'], 1)} de 5, e quem cancelou deu nota "
                      f"{dec(sa['media_canceladas'], 1)} contra {dec(sa['media_ativas'], 1)} de quem ficou "
                      f"(sem diferença, p = {dec(sa['p_valor'])}); {pct(sa['sem_resposta_%'])} dos chamados ficaram sem avaliação")
    if frases:
        linhas.append("**O que o CEO ouviu está certo, mas não explica o churn:** " + "; ".join(frases) + ". "
                      "Nem o uso agregado nem a satisfação separam quem sai de quem fica.")

    s = r["sinais"]
    fortes = s[s.p_valor < 0.05] if len(s) else s
    if len(s):
        if len(fortes):
            linhas.append("**Sinais de comportamento com relação comprovada:** "
                          + ", ".join(f"{x.sinal} (+{x.diferenca_pp:.0f} p.p.)" for x in fortes.itertuples()) + ".")
        else:
            nomes = ", ".join(x.lower() for x in s.sinal)
            inicio = (f"**Nenhum dos {len(s)} sinais de comportamento testados** ({nomes}) **separa" if len(s) > 1
                      else f"**O único sinal de comportamento disponível** ({nomes}) **não separa")
            linhas.append(inicio + ", com segurança estatística, as contas que cancelaram das que ficaram.** "
                          "Qualquer recomendação baseada nele(s) é hipótese, não fato.")

    destaques = []
    for dim, seg in r["segmentos"].items():
        topo = seg["tabela"].iloc[0]
        if seg["p_valor"] < 0.10 and topo["taxa_%"] > seg["media_%"] + 5:
            destaques.append(f"{seg['rotulo'].lower()} **{topo['grupo']}** cancela {pct(topo['taxa_%'])} "
                             f"contra {pct(seg['media_%'])} da média (p = {dec(seg['p_valor'])})")
    if destaques:
        provado = any(seg["p_valor"] < 0.05 for seg in r["segmentos"].values()
                      if seg["tabela"].iloc[0]["taxa_%"] > seg["media_%"] + 5)
        linhas.append("**Onde o risco é maior (perfil, não comportamento):** " + "; ".join(destaques) + ". "
                      + ("Há diferença comprovada (p < 0,05) em pelo menos um perfil." if provado
                         else "É o sinal mais forte da base, mas ainda é indício (p entre 0,05 e 0,10), não prova."))

    mot = r["motivos"]
    if len(mot):
        declarados = mot[mot.motivo != "sem registro"]
        if len(declarados):
            topo = declarados.iloc[0]
            preco = declarados[declarados.motivo.isin(["budget", "pricing"])]["%"].sum()
            sem = mot.loc[mot.motivo == "sem registro", "%"].sum()
            linhas.append(f"**Motivos declarados:** o mais citado é '{topo['motivo']}' ({pct(topo['%'])})"
                          + (f"; orçamento + preço somam {pct(preco)}" if preco > 0 else "")
                          + (f". {pct(sem)} das canceladas não têm motivo registrado." if sem > 0 else "."))

    m = r["modelo"]
    if m:
        linhas.append(f"**Previsão:** um modelo de machine learning, avaliado com validação cruzada, acerta pouco acima do acaso "
                      f"(AUC {dec(m['auc_lr'][0])}; 0,50 = moeda jogada). Os dados não permitem prever com confiança quem vai cancelar; "
                      "por isso a priorização usa regra explicável + valor da conta.")

    a = r["acoes"]
    if len(a):
        p1 = a.iloc[0]
        linhas.append(f"**Primeira ação recomendada:** {p1['acao']} — {p1['contas']} contas, "
                      f"{valor(r, p1['mrr_em_jogo'], True)} em jogo, impacto estimado de {valor(r, p1['impacto_estimado_mrr'], True)} "
                      f"(premissa: recuperar {pct(r['premissas'].taxa_recuperacao_pct)}).")
    return linhas


def explicacao_metodo(r):
    p, ctx = r["premissas"], r["contexto"]
    lim = ctx["limite_resposta_min"]
    return [
        "**Cliente cancelado** = marcação oficial da conta. O motivo e a data vêm do último evento de cancelamento.",
        "**MRR perdido** = receita da última assinatura de cada conta cancelada (somar todas as assinaturas encerradas "
        "misturaria upgrade/downgrade com cancelamento e inflaria o número).",
        f"**Sinais** medidos só no período ANTES da data de referência (cancelada: data do cancelamento; ativa: "
        f"{ctx['fim_base']:%d/%m/%Y}), para não usar informação do futuro. Queda de uso: últimos {p.janela_dias} dias "
        f"contra os {p.janela_dias} anteriores, queda ≥ {pct(p.queda_pct)}. Demais sinais: últimos {2 * p.janela_dias} dias."
        + (f" Resposta lenta: média acima de {lim:.0f} min (percentil 75 da base)." if lim else ""),
        "**Teste de cada sinal:** taxa de churn de quem tem o sinal × quem não tem, com teste qui-quadrado (ou Fisher). "
        "p < 0,05 = evidência forte; 0,05–0,10 = indício; acima = sem evidência.",
        "**Score de risco (0–100):** " + ("com 'pesos pelos dados', só pontua o que mostrou diferença (p < 0,10); "
                                          if p.pesos_pelos_dados else "pesos de regra de negócio definidos na tela; ")
        + "cada conta mostra quais sinais somaram pontos.",
        "**Prioridade:** risco × valor. 'Salvar agora' = risco ≥ 50 e MRR acima da mediana; 'Acompanhar' = risco ≥ 50 "
        "ou (risco ≥ 30 e MRR alto); o resto, 'Monitorar'.",
        f"**Impacto estimado** = MRR das contas-alvo × taxa de recuperação ({pct(p.taxa_recuperacao_pct)}, premissa editável).",
        "**Ações ordenadas pela força da evidência primeiro**, depois pelo impacto: ação sem evidência não vira prioridade "
        "só porque mexe com muito dinheiro.",
    ]


def correlacao_causalidade():
    return ("Tudo aqui é **correlação**: mostra onde o churn é maior, não prova o porquê. Exemplo: um segmento cancelar mais "
            "pode ser pelo produto, pelo preço para esse público ou pela forma de venda. Para provar causa, o próximo passo "
            "é testar: aplicar a ação num grupo de clientes e comparar com um grupo parecido que não recebeu.")
