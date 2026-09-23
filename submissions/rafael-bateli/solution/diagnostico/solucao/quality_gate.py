"""Quality Gate — contrato de dados para exports de tickets de suporte.

O diagnóstico mostrou que o fluxo trava porque o dado não é gravado corretamente.
Este script é a correção que roda amanhã: valida qualquer export contra o contrato
e BLOQUEIA (exit code 1) quando uma regra crítica falha. Cabe no ETL, num cron
diário ou no CI do time de dados.

Uso:
    python quality_gate.py --data ../../data/support_tickets.csv
    python quality_gate.py --data export.csv --colunas mapa.json   # nomes de coluna diferentes

Saída: ../outputs/quality_gate.md e ../outputs/quality_gate.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "outputs"

# Nomes de coluna do export. Troque aqui (ou via --colunas) para outro sistema.
COLUNAS = {
    "id": "Ticket ID", "email": "Customer Email", "nome": "Customer Name",
    "tipo": "Ticket Type", "assunto": "Ticket Subject", "descricao": "Ticket Description",
    "status": "Ticket Status", "resolucao": "Resolution", "prioridade": "Ticket Priority",
    "criado_em": "Created At",  # não existe no export atual: é a regra R01
    "primeira_resposta": "First Response Time", "resolvido_em": "Time to Resolution",
    "csat": "Customer Satisfaction Rating",
}
STATUS_ABERTO, STATUS_PENDENTE, STATUS_FECHADO = "Open", "Pending Customer Response", "Closed"

# Tipos aceitos para cada assunto (mesmo mapa generoso do diagnóstico).
TIPOS_POR_ASSUNTO = {
    "Refund request": {"Refund request"}, "Cancellation request": {"Cancellation request"},
    "Payment issue": {"Billing inquiry", "Refund request"}, "Product recommendation": {"Product inquiry"},
    "Delivery problem": {"Product inquiry", "Refund request", "Cancellation request"},
    "Account access": {"Technical issue", "Billing inquiry"},
    "Product compatibility": {"Technical issue", "Product inquiry"},
    "Peripheral compatibility": {"Technical issue", "Product inquiry"},
    "Installation support": {"Technical issue", "Product inquiry"},
    "Product setup": {"Technical issue", "Product inquiry"},
    "Hardware issue": {"Technical issue", "Refund request"}, "Display issue": {"Technical issue", "Refund request"},
    "Battery life": {"Technical issue", "Refund request"}, "Software bug": {"Technical issue"},
    "Network problem": {"Technical issue"}, "Data loss": {"Technical issue"},
}
TEMAS = {
    "Account access": r"account|log ?in|password|credential|locked",
    "Network problem": r"network|wi-?fi|internet|connect(?:ion)? ",
    "Data loss": r"data loss|deleted|files|recover",
    "Software bug": r"software bug|crash|glitch|freez",
    "Hardware issue": r"hardware|screen|noise|not turning on|flicker",
    "Battery life": r"battery",
    "Display issue": r"display|screen|flicker",
    "Payment issue": r"payment|charge|billing|refund|invoice",
}
URGENCIA = r"as soon as possible|affecting my work|urgent|immediately"
VOCAB_SUPORTE = {"issue", "product", "problem", "update", "reset", "account", "password", "replace", "refund",
                 "restart", "install", "software", "support", "device", "error", "settings", "network",
                 "battery", "troubleshoot", "resolve", "fixed", "solution", "reinstall", "firmware", "driver",
                 "replaced", "updated", "resolved", "cable", "charger", "screen", "access", "login"}


@dataclass
class Regra:
    id: str
    nome: str
    severidade: str  # BLOQUEANTE | ALERTA
    dono: str
    metrica: str
    limite: str
    status: str = ""
    valor: str = ""
    correcao: str = ""


def _ts(df, col):
    return pd.to_datetime(df[col], errors="coerce") if col in df else pd.Series(pd.NaT, index=df.index)


def avaliar(df: pd.DataFrame, c: dict) -> list[Regra]:
    regras: list[Regra] = []
    fechado = df[c["status"]] == STATUS_FECHADO
    fr, rs = _ts(df, c["primeira_resposta"]), _ts(df, c["resolvido_em"])

    def add(r: Regra, ok: bool, valor: str):
        r.status, r.valor = ("OK" if ok else "FALHA"), re.sub(r"(\d)\.(\d+)(?=[%×])", r"\1,\2", valor)
        regras.append(r)

    # R01 — sem horário de abertura não existe métrica de tempo.
    tem_criado = c["criado_em"] in df and df[c["criado_em"]].notna().mean() > 0.99
    add(Regra("R01", "Horário de abertura presente", "BLOQUEANTE", "TI / sistema de tickets",
              "% tickets com created_at", "≥ 99%",
              correcao="Gravar created_at pelo sistema na entrada do ticket (não editável)."),
        tem_criado, "coluna inexistente" if c["criado_em"] not in df else f"{df[c['criado_em']].notna().mean():.1%}")

    # R02 — ordem temporal.
    par = fechado & fr.notna() & rs.notna()
    invertidos = (rs[par] < fr[par]).mean() if par.any() else 0
    add(Regra("R02", "Resolução depois da 1ª resposta", "BLOQUEANTE", "TI / ETL",
              "% fechados com resolvido_em < primeira_resposta", "≤ 0,5%",
              correcao="Validar created_at ≤ first_response_at ≤ resolved_at na gravação; rejeitar o evento fora de ordem."),
        invertidos <= 0.005, f"{invertidos:.1%}")

    # R03 — campo calculado em vez de registrado (segundos idênticos nos dois horários).
    mesmos_seg = ((rs[par] - fr[par]).dt.total_seconds() % 60 == 0).mean() if par.any() else 0
    add(Regra("R03", "Horários registrados por evento (não calculados)", "BLOQUEANTE", "TI / ETL",
              "% pares com segundos idênticos", "≤ 5% (acaso ≈ 1,7%)",
              correcao="resolved_at deve vir do evento 'ticket resolvido', não de uma fórmula sobre first_response."),
        mesmos_seg <= 0.05, f"{mesmos_seg:.0%}")

    # R04 — janela temporal compatível com a operação.
    todos = pd.concat([fr, rs]).dropna()
    janela_h = (todos.max() - todos.min()).total_seconds() / 3600 if len(todos) else 0
    dias_esperados = max(1, len(df) / (30_000 / 365))  # volume ÷ ritmo diário informado
    add(Regra("R04", "Janela dos horários compatível com o volume", "BLOQUEANTE", "TI / ETL",
              "horas cobertas pelos horários", f"≥ {dias_esperados * 24 * 0.5:,.0f} h ({len(df):,} tickets a ~82/dia)".replace(",", "."),
              correcao="Horários concentrados em ~1 dia indicam carimbo de exportação. Exportar o horário do evento."),
        janela_h >= dias_esperados * 24 * 0.5, f"{janela_h:,.0f} h".replace(",", "."))

    # R05 — template com placeholder não substituído.
    placeholder = df[c["descricao"]].str.contains(r"\{[A-Za-z_]+\}", regex=True).mean()
    add(Regra("R05", "Descrição sem placeholder de template", "BLOQUEANTE", "TI / integração de formulários",
              "% descrições com {chave}", "≤ 0,5%",
              correcao="Corrigir o merge do template (product_purchased, error_message…); rejeitar texto com {…}."),
        placeholder <= 0.005, f"{placeholder:.1%}")

    # R06 — resolução legível (usa vocabulário de suporte).
    res = df.loc[fechado, c["resolucao"]].dropna().astype(str)
    legivel = res.map(lambda s: bool(VOCAB_SUPORTE & set(re.findall(r"[a-z]+", s.lower())))).mean() if len(res) else 0
    add(Regra("R06", "Resolução com conteúdo de suporte", "ALERTA", "Operações + TI",
              "% resoluções com vocabulário de suporte", "≥ 80%",
              correcao="Resolução estruturada: código de solução (lista) + texto livre; alimenta a base de conhecimento."),
        legivel >= 0.8, f"{legivel:.1%}")

    # R07 — tipo coerente com assunto.
    coerente = df.apply(lambda r: r[c["tipo"]] in TIPOS_POR_ASSUNTO.get(r[c["assunto"]], {r[c["tipo"]]}), axis=1).mean()
    add(Regra("R07", "Tipo coerente com o assunto", "BLOQUEANTE", "Operações (taxonomia) + IA de triagem",
              "% tickets com tipo aceito para o assunto", "≥ 90%",
              correcao="Taxonomia única (assunto determina o tipo) preenchida pela triagem por IA."),
        coerente >= 0.9, f"{coerente:.1%}")

    # R08 — assunto reflete o texto (lift sobre o acaso).
    texto = df[c["descricao"]].str.replace(r"I'm having an issue with the \{product_purchased\}\. Please assist\.", "", regex=True)
    temas = texto.map(lambda s: [k for k, p in TEMAS.items() if re.search(p, s, re.I)])
    base = (temas.str.len() > 0) & df[c["assunto"]].isin(TEMAS)
    acerto = pd.Series([a in t for a, t in zip(df.loc[base, c["assunto"]], temas[base])]).mean()
    acaso = temas[base].str.len().mean() / len(TEMAS)
    lift = acerto / acaso if acaso else 0
    add(Regra("R08", "Assunto bate com a descrição", "BLOQUEANTE", "IA de triagem",
              "acerto ÷ acaso (lift)", "≥ 3×",
              correcao="Assunto definido pelo conteúdo (IA), não por quem abre o ticket."),
        lift >= 3, f"{lift:.2f}× ({acerto:.1%} vs acaso {acaso:.1%})")

    # R09 — prioridade reflete urgência declarada.
    urg = df[c["descricao"]].str.contains(URGENCIA, case=False, regex=True)
    alta = df.loc[urg, c["prioridade"]].isin(["Critical", "High"]).mean() if urg.any() else 1
    add(Regra("R09", "Pedido urgente recebe prioridade alta", "ALERTA", "IA de triagem + Operações (SLA)",
              "% tickets com linguagem de urgência em Critical/High", "≥ 70%",
              correcao="Prioridade = f(severidade do conteúdo, impacto declarado, cliente); não escolha livre."),
        alta >= 0.7, f"{alta:.1%} (n={int(urg.sum())})")

    # R10 — máquina de estados coerente (esperado OK: o gate não reprova tudo).
    aberto, pend = df[c["status"]] == STATUS_ABERTO, df[c["status"]] == STATUS_PENDENTE
    estado_ok = (fr[aberto].isna().all() and fr[pend].notna().all() and rs[pend].isna().all()
                 and fr[fechado].notna().all() and rs[fechado].notna().all())
    add(Regra("R10", "Status coerente com os horários", "BLOQUEANTE", "TI / sistema de tickets",
              "Open sem resposta; Pending sem resolução; Closed completo", "100%",
              correcao="—"),
        estado_ok, "100% coerente" if estado_ok else "incoerente")

    # R11 — CSAT cobre além dos fechados.
    cobertura = df[c["csat"]].notna().mean()
    add(Regra("R11", "CSAT cobre toda a base", "ALERTA", "Operações / CX",
              "% tickets com CSAT", "≥ 60% (inclui abertos há > 7 dias)",
              correcao="Pesquisar também tickets abertos/pendentes há mais de 7 dias; incluir motivo + CES."),
        cobertura >= 0.6, f"{cobertura:.1%}")

    # R12 — identidade do cliente.
    dup = df[df[c["email"]].duplicated(keep=False)].groupby(c["email"])[c["nome"]].nunique()
    conflitos = int((dup > 1).sum())
    add(Regra("R12", "Um e-mail = um cliente", "ALERTA", "TI / CRM",
              "e-mails ligados a nomes diferentes", "0",
              correcao="customer_id do CRM em todo ticket; permite medir recontato de verdade."),
        conflitos == 0, f"{conflitos}")
    return regras


def relatorio_md(regras: list[Regra], arquivo: str) -> str:
    bloq = [r for r in regras if r.status == "FALHA" and r.severidade == "BLOQUEANTE"]
    linhas = [
        "# Quality Gate — resultado", "",
        f"Arquivo: `{arquivo}`  ",
        f"**Veredito: {'REPROVADO' if bloq else 'APROVADO'}**, "
        f"{sum(r.status == 'OK' for r in regras)}/{len(regras)} regras OK, {len(bloq)} bloqueantes em falha.", "",
        "| Regra | Verificação | Severidade | Medido | Limite | Status | Dono | Correção |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in regras:
        linhas.append(f"| {r.id} | {r.nome} | {r.severidade} | {r.valor} | {r.limite} | "
                      f"{'✅' if r.status == 'OK' else '❌'} {r.status} | {r.dono} | {r.correcao} |")
    return "\n".join(linhas) + "\n"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=HERE.parents[1] / "data" / "support_tickets.csv")
    ap.add_argument("--colunas", type=Path, help="JSON com o mapa de colunas, se o export usar outros nomes")
    args = ap.parse_args()
    c = dict(COLUNAS)
    if args.colunas:
        c.update(json.loads(args.colunas.read_text(encoding="utf-8")))

    df = pd.read_csv(args.data)
    regras = avaliar(df, c)
    OUT.mkdir(exist_ok=True)
    md = relatorio_md(regras, args.data.name)
    (OUT / "quality_gate.md").write_text(md, encoding="utf-8")
    (OUT / "quality_gate.json").write_text(json.dumps([asdict(r) for r in regras], ensure_ascii=False, indent=2), encoding="utf-8")
    print(md)
    return 1 if any(r.status == "FALHA" and r.severidade == "BLOQUEANTE" for r in regras) else 0


if __name__ == "__main__":
    raise SystemExit(main())
