"""
Matriz de cruzamentos entre modulos (PLANEJAMENTO.md, secao 6).

Tipo A = outra ferramenta nos MESMOS dados. Tipo B = resultado vira perfil que filtra outra base.
Selos (badges de texto na tela): verde = dado real · laranja = proxy · azul = hipotese · cinza = nao da.
"""

SELOS = {
    "verde": ("green", "Dado real ligado"),
    "amarelo": ("orange", "Proxy (sinal indireto)"),
    "azul": ("blue", "Hipótese configurável"),
    "bloqueado": ("gray", "Não dá"),
}

# (origem, destino): (selo, tipo, o que faz)
MATRIZ = {
    ("churn", "suporte"): ("verde", "A", "Tickets das contas em risco → gargalos, satisfação e desperdício só desse grupo (sem classificador: os tickets não têm texto)."),
    ("churn", "leads"): ("amarelo", "A", "Contas ativas viram uma carteira de expansão: chance de a conta ficar (por plano, setor e porte) × MRR. Sem vendedor e sem datas na base."),
    ("churn", "midia"): ("azul", "B", "Países das contas que mais cancelam → que conteúdo usar com essa audiência (4 dos 7 países existem no social)."),
    ("suporte", "churn"): ("amarelo", "A", "Quem abriu 'pedido de cancelamento' vira 'cancelou' → o que diferencia esses clientes (produto, idade, gênero, satisfação). Sem receita: valores = contagem de clientes."),
    ("suporte", "leads"): ("amarelo", "lista", "Tickets de 'pergunta sobre produto' → lista de oportunidades para o CRM. Não vira sessão: a base de suporte não tem vendas ganhas/perdidas para o score aprender."),
    ("suporte", "midia"): ("azul", "B", "Idade e gênero de quem mais reclama → conteúdo para esse público."),
    ("leads", "churn"): ("bloqueado", "-", "O CRM não tem cancelamentos. Só dá para ver concentração de receita."),
    ("leads", "suporte"): ("bloqueado", "-", "O CRM não tem tickets. Só dá para montar a fila de onboarding dos deals ganhos."),
    ("leads", "midia"): ("azul", "B", "Países e setores onde mais ganhamos → onde concentrar conteúdo."),
    ("midia", "churn"): ("bloqueado", "-", "O social não tem clientes nem cancelamentos."),
    ("midia", "suporte"): ("bloqueado", "-", "O social não tem tickets."),
    ("midia", "leads"): ("azul", "B", "Perfil de audiência que mais engaja → fator extra (desligado por padrão) no score de leads."),
}


def destinos(origem):
    """Lista de (destino, selo, tipo, descricao) para uma sessao de origem."""
    return [(d, *MATRIZ[(o, d)]) for (o, d) in MATRIZ if o == origem]
