"""O que a IA pode fazer em cada rota (regra em código, não no prompt) e checagem do texto gerado."""

from __future__ import annotations

from .decisao import Decisao


def aplicar_permissoes(d: Decisao) -> None:
    if d.operacao == "d2":
        d.permite_rascunho, d.permite_dossie = False, False
        d.motivo_permissao = "service desk: a IA classifica e roteia; a proposta não prevê rascunho aqui"
    elif "canal_publico" in d.marcacoes:
        d.permite_rascunho, d.permite_dossie = False, d.rota in ("1A", "1B")
        d.motivo_permissao = "canal público: só o template aprovado, que leva a conversa para o privado"
    elif d.rota == "1B":
        d.permite_rascunho, d.permite_dossie = False, True
        d.motivo_permissao = "risco no texto (perda de dados, segurança, dinheiro ou idioma): IA só monta o dossiê"
    elif d.rota == "1A":
        d.permite_rascunho, d.permite_dossie = True, True
        d.motivo_permissao = "risco na decisão (hardware, reparo, recontato): IA rascunha, humano decide"
    elif d.rota == "2":
        d.permite_rascunho, d.permite_dossie = True, False
        d.motivo_permissao = "IA rascunha a partir da base de conhecimento; agente aprova, edita ou descarta"
    else:
        d.permite_rascunho, d.permite_dossie = False, False
        d.motivo_permissao = "coleta por template fixo; o ticket volta à triagem quando o cliente responder"
