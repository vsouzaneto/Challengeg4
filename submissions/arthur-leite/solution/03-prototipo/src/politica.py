"""
Política do que NÃO automatizar.

Princípio: rotear ≠ executar ≠ responder. A IA pode decidir para qual fila um ticket vai, mas
algumas AÇÕES e algumas RESPOSTAS exigem humano, seja qual for a confiança do modelo.

Por que regras explícitas, e não a categoria prevista: no Dataset 2, os temas sensíveis
atravessam as categorias (ex.: menções a segurança caem 41% em Hardware, 19% em Administrative
rights e 17% em Access). Uma regra pela categoria deixaria passar a maior parte deles.
As regras são de alta sensibilidade de propósito: um falso alarme custa segundos de um humano;
um falso negativo (ex.: phishing tratado como rotina) custa caro.

Frequências medidas no Dataset 2 (47.837 tickets) estão em REGRAS[*]["freq_ds2"]. No total, 23,4% dos tickets
acionam ao menos uma regra (execução exige humano), 2,7% bloqueiam o rascunho por LLM e 8,1% são escalados.
v2 (auditoria de dados): regra de privilégio sem "administrator" solto (vinha da assinatura) e
"maternity leaver" fora de desligamento. Antes: 13,0% privilégio, 2,3% desligamento, 27,7% no total.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

REGRAS = {
    "seguranca": {
        "padrao": r"\b(phishing|virus|malware|hacked|suspicious|breach|ransomware|spam)\b",
        "acao": "Escalar imediatamente para Segurança da Informação. Nunca resolver ou fechar automaticamente.",
        "porque": "Um incidente de segurança tratado como rotina tem custo assimétrico.",
        "bloqueia_rascunho": True, "freq_ds2": "0,7% (339)",
    },
    "saude_afastamento": {
        "padrao": r"\b(sick|maternity|paternity|medical|absence|illness)\b",
        "acao": "Só humano do RH responde. A IA apenas roteia.",
        "porque": "Dado de saúde é dado pessoal sensível (LGPD, art. 11). Não deve ir para um LLM externo.",
        "bloqueia_rascunho": True, "freq_ds2": "2,0% (934)",
    },
    "desligamento": {
        "padrao": r"\b(termination|resignation|leaver|leavers|offboarding|dismissal)\b",
        "acao": "A revogação de acessos é executada por humano, com checklist.",
        "porque": "Erro aqui = ex-funcionário com acesso ou funcionário ativo bloqueado.",
        "bloqueia_rascunho": False, "freq_ds2": "2,0% (950)",
    },
    "aprovacao_financeira": {
        "padrao": r"\b(approve|approval|approver|po|purchase order|invoice|quote|budget)\b",
        "acao": "A IA roteia e prepara; a aprovação é sempre humana.",
        "porque": "Aprovar gasto é decisão com responsabilidade, não classificação.",
        "bloqueia_rascunho": False, "freq_ds2": "10,4% (4.987)",
    },
    "privilegio": {
        # v2 (auditoria de dados): a v1 usava "admin|administrator|rights" soltos e metade dos alertas vinha da
        # palavra "administrator" na ASSINATURA dos e-mails (13,0% dos tickets). Agora só pedidos de acesso/privilégio.
        "padrao": r"\b(admin rights|administrator rights|administrative rights|admin access|administrator access|"
                  r"local admin|elevated|privileges?|permissions?|grant access|access rights)\b",
        "acao": "Conceder privilégio exige aprovação do gestor e registro.",
        "porque": "Concessão de acesso é controle de segurança auditável.",
        "bloqueia_rascunho": False, "freq_ds2": "3,5% (1.656)",
    },
    "urgencia_incidente": {
        "padrao": r"\b(urgent|urgently|asap|critical|immediately|outage|down|blocked|cannot work)\b",
        "acao": "Sobe a prioridade e notifica o plantão. Não espera na fila comum.",
        "porque": "Impacto no negócio; o tempo de espera importa mais que a categoria.",
        "bloqueia_rascunho": False, "freq_ds2": "7,7% (3.682)",
    },
}
_COMPILADAS = {k: re.compile(v["padrao"]) for k, v in REGRAS.items()}

ROTULOS = {"seguranca": "Segurança", "saude_afastamento": "Saúde / afastamento", "desligamento": "Desligamento",
           "aprovacao_financeira": "Aprovação financeira", "privilegio": "Privilégio de acesso",
           "urgencia_incidente": "Urgência / indisponibilidade"}


@dataclass
class DecisaoPolitica:
    alertas: list[str]                 # chaves de REGRAS acionadas
    exige_humano_para_executar: bool
    pode_gerar_rascunho: bool
    escalar: bool

    def descrever(self) -> list[str]:
        return [f"**{ROTULOS[a]}**: {REGRAS[a]['acao']} _{REGRAS[a]['porque']}_" for a in self.alertas]


def avaliar(texto: str) -> DecisaoPolitica:
    t = texto.lower()
    alertas = [k for k, rx in _COMPILADAS.items() if rx.search(t)]
    # "maternity leaver form" é licença, não desligamento: já coberto por saúde/afastamento
    if "desligamento" in alertas and "maternity" in t:
        alertas.remove("desligamento")
    return DecisaoPolitica(
        alertas=alertas,
        exige_humano_para_executar=bool(alertas),
        pode_gerar_rascunho=not any(REGRAS[a]["bloqueia_rascunho"] for a in alertas),
        escalar=any(a in ("seguranca", "urgencia_incidente") for a in alertas),
    )
