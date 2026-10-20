"""Textos da CLI (pt-BR), montados a partir dos códigos do payload (fases F4 e F5 do contrato).

A CLI é uma camada de apresentação, como a tela: recebe chaves, códigos e números e
decide como dizer. Segue as regras do catálogo da tela (`web/copy/pt-BR.ts`): só
cita valores recebidos e não afirma mais do que o código diz. Um código sem texto
aqui quebra `tests/test_cli_text.py`.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

import pandas as pd

from . import codes
from .fmt import fmt_date, fmt_int

Params = Dict[str, Any]

# Verbos no infinitivo: os moldes "Comece por {nome}" e "{nome} porque…" leem bem com todos.
GROUP_LABELS = {"focar": "Focar", "acompanhar": "Acompanhar", "revisar": "Confirmar", "qualificar": "Qualificar",
                "nao_pontuavel": "Completar"}

# Campo ausente → (motivo curto na linha, nome usado nas frases).
MISSING = {
    "product": ("sem produto", "o produto"),
    "sales_price": ("sem preço de tabela", "o preço de tabela"),
    "engage_date": ("sem data de engajamento", "a data de engajamento"),
}

NO_ACCOUNT = "sem cliente registrado"
NO_PRODUCT = "sem produto"
NO_BAND = "Sem valor de tabela"
OPEN = "abertas"
NOTE = "Nota"
NEXT_STEP = "O que verificar agora"
WHY_HERE = "Por que está aqui"
COLUMNS = ("ID", "Produto", "Cliente", "Preço", "Início da negociação", "Idade")
DATA_WARNING = ("Atenção: dados diferentes da versão auditada. Os números conferidos "
                "no PRD deixam de ser garantidos.")

# Ajuda dos comandos e rótulo de erro (a mensagem do erro vem do núcleo, para quem opera).
HELP = {
    "raw": "pasta com os CSVs",
    "check-data": "presença, hash e reconciliação dos dados",
    "list": 'lista "Onde focar" de um vendedor',
    "seller": 'nome exato, ex.: "Zane Levy"',
    "as-of": "data de referência AAAA-MM-DD (padrão: último fechamento)",
    "json": "imprime o payload da API",
    "explain": '"Por que está aqui" de uma oportunidade aberta',
    "id": "ex.: 01XZ9CRY",
}
ERROR = "Erro"

# `check-data`: diagnóstico dos CSVs, das junções e da reconciliação.
CHECK_DATA = {
    "folder": "Dados: {folder}",
    "hash": "Hash: {audited} de {total} arquivos iguais à versão auditada",
    "joins": "Junções (linhas após cada passo):",
    "unmatched": "  sem o mapa GTXPro → GTX Pro: {count} não casadas",
    "opportunities": "Oportunidades: {total} = {parts}",
    "open": "Abertas: {count}",
}
JOIN_STEPS = {"sales_pipeline": "sales_pipeline", "products": "+ products", "sales_teams": "+ sales_teams",
              "accounts": "+ accounts"}
JOIN_GAPS = {"null_price": "preço nulo", "null_manager": "manager nulo", "orphan_account": "conta sem cadastro"}


def iso_date(value: str) -> str:
    return fmt_date(pd.Timestamp(value))


def value_label(band: str) -> str:
    return f"valor de tabela {band}"


# Os limites aparecem como fato do histórico, nunca como prazo.
REASONS: Dict[str, Callable[[Params], str]] = {
    codes.AGE_WITHIN_WON_CYCLE: lambda p: (
        f"{GROUP_LABELS['focar']} porque está aberta há {p['age_days']} dias. Entre as vendas ganhas, {p['percentile']}% "
        f"fecharam em até {p['won_cycle_limit_days']} dias."),
    codes.AGE_ABOVE_WON_CYCLE: lambda p: (
        f"{GROUP_LABELS['acompanhar']} porque está aberta há {p['age_days']} dias: mais do que {p['percentile']}% "
        f"das vendas ganhas levaram ({p['won_cycle_limit_days']} d), sem passar da venda mais longa já fechada "
        f"({p['cycle_limit_days']} d)."),
    codes.AGE_ABOVE_CYCLE_LIMIT: lambda p: (
        f"{GROUP_LABELS['revisar']} porque está aberta há {p['age_days']} dias, mais do que qualquer venda já "
        f"fechada aqui ({p['cycle_limit_days']} d)."),
    # A regra é o estágio, não a falta de data (o texto antigo dizia mais do que o código).
    codes.PROSPECTING_STAGE: lambda p: f"{GROUP_LABELS['qualificar']} porque ainda está em prospecção.",
    codes.MISSING_FIELD: lambda p: f"{GROUP_LABELS['nao_pontuavel']} porque falta {MISSING[p['field']][1]}.",
    codes.LIST_PRICE: lambda p: (
        f"Valor de tabela {fmt_int(p['sales_price'])} ({value_label(p['value_band'])}): preço de catálogo do "
        f"{p['product']}, não valor negociado."),
    codes.NO_PRODUCT: lambda p: "Sem valor de tabela: a oportunidade não tem produto.",
    codes.NO_LIST_PRICE: lambda p: f"Sem valor de tabela: o {p['product']} não tem preço no catálogo.",
}
# O que o sistema não vê: dito uma vez no "Por que está aqui", não como motivo.
LIMITS_NOTE = ("Como o pipeline só apresenta datas, produto e preço de tabela: não apresenta último contato, ligações, "
               "reuniões nem e-mails. A base não registra atividades, estágio nem contatos. Por isso o Rankio indica "
               "possibilidades para diferentes cenários de negociação, mas não uma certeza de próximo passo.")

# Sugestões de negociação: possibilidades para contextos que a base não registra, por grupo (as mesmas da tela).
# Não são derivadas dos dados da oportunidade nem preveem resultado.
SUGGESTIONS_TITLE = "Sugestões de negociação"
SUGGESTIONS_INTRO = ("O Rankio não sabe em que contexto a negociação está. Estas são possibilidades para diferentes "
                     "cenários: use as que fizerem sentido.")
SUGGESTIONS = {
    "focar": [
        ("já houve contato recente", "retome de onde parou e registre o avanço no CRM."),
        ("não há registro de contato", "consulte no CRM o último registro e avalie um novo contato para entender em "
                                       "que ponto a negociação está."),
        ("foi enviada uma proposta sem resposta", "avalie um novo contato para entender o que falta para a decisão."),
        ("o cliente pediu mais tempo", "combine uma data para retomar e registre no CRM."),
    ],
    "qualificar": [
        ("já houve conversa com a conta", "registre a data de início da negociação no CRM."),
        ("ainda não houve contato", "avalie um primeiro contato, pelo valor de tabela e pelo que você já conhece da "
                                    "conta."),
    ],
    "acompanhar": [
        ("o último registro é antigo", "avalie retomar o contato para entender se a negociação segue."),
        ("o cliente respondeu recentemente", "registre o avanço no CRM e combine o próximo passo com ele."),
        ("o contato mudou de função na empresa", "procure quem assumiu o assunto e registre o novo contato."),
        ("o cliente indicou que não vai seguir", "registre o desfecho no CRM."),
    ],
    "revisar": [
        ("a negociação continua ativa", "registre o avanço e a situação atual no CRM."),
        ("o cliente voltou a demonstrar interesse", "registre o novo engajamento no CRM."),
        ("não há registro recente", "confirme com quem atendeu a conta antes de decidir."),
        ("o cliente não responde mais", "considere registrar o desfecho no CRM e liberar espaço na carteira."),
    ],
    "nao_pontuavel": [
        ("o dado existe em outra fonte", "complete o campo no CRM."),
        ("ninguém sabe a informação", "pergunte a quem abriu a oportunidade."),
    ],
}
NO_ACCOUNT_SUGGESTION = ("a conta não está registrada", "consulte no CRM quem é a conta antes de contatar.")


def suggestions_for(entry: Dict[str, Any]) -> List[str]:
    """As possibilidades do grupo; a da conta ausente só entra quando a oportunidade não tem conta registrada."""
    pairs = list(SUGGESTIONS[entry["group"]])
    if entry["account"] is None and entry["group"] != "nao_pontuavel":
        pairs.append(NO_ACCOUNT_SUGGESTION)
    return [f"Se {when}: {then}" for when, then in pairs]

# O que verificar agora (ADR-008): uma verificação no CRM com base nos dados da linha, sem presumir atividade,
# intenção nem compromisso. Os três primeiros textos variam com a conta: registrada, ausente ou (no grupo) nenhuma.
ABOUT_STATUS = "o tempo aberta não prova que ela terminou"
ACCOUNT_ACTIONS: Dict[str, Dict[str, Callable[[str], str]]] = {
    codes.CHECK_STATUS: {
        "with": lambda account: f"Consulte no CRM o andamento da negociação com {account}.",
        "without": lambda account: "Consulte no CRM o andamento e a conta desta negociação.",
        "group": lambda account: "Consulte no CRM o andamento de cada negociação.",
    },
    codes.CHECK_PROGRESS: {
        "with": lambda account: f"Consulte no CRM o último registro da negociação com {account}.",
        "without": lambda account: "Consulte no CRM o último registro e a conta desta negociação.",
        "group": lambda account: "Consulte no CRM o último registro de cada negociação.",
    },
    codes.CONFIRM_STILL_ACTIVE: {
        "with": lambda account: f"Verifique no CRM se a negociação com {account} continua: {ABOUT_STATUS}.",
        "without": lambda account: f"Verifique no CRM se esta negociação continua e qual é a conta: {ABOUT_STATUS}.",
        "group": lambda account: f"Verifique no CRM se cada negociação continua: {ABOUT_STATUS}.",
    },
}
ACTIONS: Dict[str, Callable[[Params], str]] = {
    codes.CHECK_PROSPECTING: lambda p: (
        "Em prospecção, sem data de início: verifique no CRM se já houve engajamento e registre a data quando "
        "houver."),
    codes.FIX_MISSING_FIELD: lambda p: f"Corrija {MISSING[p['field']][1]} no CRM.",
    codes.FIX_MISSING_FIELDS: lambda p: "Corrija no CRM o campo indicado em cada oportunidade.",
}

# Ação de "comece por", em minúscula, no meio da frase de Focar vazio.
START_ACTIONS = {
    codes.CHECK_PROGRESS: "consulte no CRM o último registro de cada uma",
    codes.CONFIRM_STILL_ACTIVE: "verifique no CRM quais seguem ativas",
    codes.CHECK_PROSPECTING: "verifique no CRM se já houve engajamento e registre a data",
    codes.FIX_MISSING_FIELDS: "corrija o cadastro no CRM",
}

def _start_with(p: Params) -> str:
    """Focar vazio: cita só o limite que importa para o grupo indicado."""
    group = p["group"]
    if group == "acompanhar" or (group == "qualificar" and p["has_engaging"]):
        why = f"Nenhuma aberta há até {p['won_cycle_limit_days']} dias."
    elif group == "revisar":
        why = f"Todas as negociações em andamento estão abertas há mais de {p['cycle_limit_days']} dias."
    else:
        why = "Nenhuma negociação em andamento."
    return f"{why} Comece por {GROUP_LABELS[group]}: {START_ACTIONS[p['action']]}."


EMPTY: Dict[str, Callable[[Params], str]] = {
    codes.GROUP_EMPTY: lambda p: "Nenhuma oportunidade neste grupo.",
    codes.START_WITH_GROUP: _start_with,
    codes.NO_OPEN_FOR_SELLER: lambda p: "Nenhuma oportunidade aberta para este vendedor.",
    codes.NO_OPEN_FOR_FILTER: lambda p: "Nenhuma oportunidade aberta para este filtro.",
}


def reason_text(reason: Dict[str, Any]) -> str:
    return REASONS[reason["code"]](reason["params"])


def action_text(action: Dict[str, Any], account: Optional[str] = None) -> str:
    """O texto da ação. `account` é a conta da oportunidade; sem ela (ou na ação do grupo) a frase é genérica."""
    variants = ACCOUNT_ACTIONS.get(action["code"])
    if variants is None:
        return ACTIONS[action["code"]](action["params"])
    has_account = action["params"]["has_account"]
    if has_account is None:
        return variants["group"]("")
    return variants["with" if has_account and account else "without"](account or "")


def empty_text(empty: Dict[str, Any]) -> str:
    return EMPTY[empty["code"]](empty["params"])


# A legenda só descreve a ordem que conhece; uma ordem nova cai na versão curta.
KNOWN_WITHIN_GROUP = [codes.ORDER_VALUE_BAND, codes.ORDER_SALES_PRICE_DESC, codes.ORDER_OPPORTUNITY_ID]


def legend_text(ordering: Dict[str, Any]) -> str:
    groups = " → ".join(GROUP_LABELS[key] for key in ordering["group_order"])
    if ordering["within_group"] != KNOWN_WITHIN_GROUP:
        return f"Ordem: {groups}."
    age = "" if ordering["age_affects_order"] else " A idade aparece, mas não muda a ordem."
    return f"Ordem: {groups}. Em cada grupo, maior valor de tabela primeiro.{age}"


def data_label(meta: Dict[str, Any]) -> str:
    return f"Dados até {iso_date(meta['as_of'])}"


def summary_counts(payload: Dict[str, Any]) -> str:
    """Só os grupos com oportunidades; os zerados saem na linha de `empty_groups_text`."""
    return " + ".join(f"{payload['summary'][g['state']]} {GROUP_LABELS[g['state']]}"
                      for g in payload["groups"] if payload["summary"][g["state"]])


def empty_groups_text(payload: Dict[str, Any]) -> Optional[str]:
    """Os grupos sem oportunidades, ditos uma vez, para a ausência não passar por esquecimento."""
    empty = [GROUP_LABELS[g["state"]] for g in payload["groups"] if not payload["summary"][g["state"]]]
    if not empty:
        return None
    return f"Sem oportunidades em {' e '.join([', '.join(empty[:-1]), empty[-1]] if len(empty) > 1 else empty)}."


def account_warning(summary: Dict[str, Any]) -> str:
    return f"{summary['without_account']} de {summary['total']} {NO_ACCOUNT}"


# A conta ausente é um fato do cadastro: nenhum dado mostra que ela diga algo sobre a oportunidade.
ACCOUNT_NOTE = "A ausência do cliente é uma lacuna do cadastro e não diz nada sobre a qualidade da oportunidade."


def client_text(item: Dict[str, Any]) -> str:
    return item["account"] or NO_ACCOUNT


# Contexto histórico da idade (ADR-008): só descreve as vendas que fecharam, sem dizer o que fazer nem prever.
AGE_CONTEXT_TITLE = "Idade no contexto do histórico"
AGE_CONTEXT_NOTE = "Isso descreve as vendas que fecharam, mas não diz o que acontece com esta negociação."


def age_context(age_days: Optional[int], meta: Dict[str, Any]) -> Optional[str]:
    if age_days is None:
        return None
    return (f"Aberta há {age_days} dias. Nas vendas ganhas, metade fechou em até {meta['won_cycle_median_days']} dias, "
            f"{meta['cycle_percentile']}% em até {meta['won_cycle_limit_days']} dias e a mais longa levou "
            f"{meta['cycle_limit_days']}.")


def tie_note(entry: Dict[str, Any]) -> Optional[str]:
    """Na posição de uma oportunidade empatada: a ordem entre as empatadas é só pelo código."""
    if entry["tie_size"] < 2 or entry["sales_price"] is None:
        return None
    others = entry["tie_size"] - 1
    return (f"Empata com {others} {'outra' if others == 1 else 'outras'} do mesmo produto e valor de tabela. A "
            "ordem entre elas é só pelo código.")


def band_title(band: Optional[str]) -> str:
    return value_label(band).capitalize() if band else NO_BAND


def missing_short(field: str) -> str:
    return MISSING[field][0]


def tie_text(count: int, product: str, price: int) -> str:
    """Empate: mesmo grupo, produto e valor de tabela. A ordem dentro dele é só pelo código, sem significado."""
    return f"{count} oportunidades empatadas ({product}, {fmt_int(price)}): sem ordem entre si"
