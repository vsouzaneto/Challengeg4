"""Modelo de custo parametrizado da triagem de tickets (ler, classificar, encaminhar).

Só calcula e imprime. Toda premissa é uma variável nomeada abaixo, com a fonte no
comentário: "enunciado", "dataset", "premissa minha" ou "benchmark" com referência.
Saída em solution/02_modelo_custo.txt.
"""

import json
import sys
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "data"
SAIDA = AQUI / "02_modelo_custo.txt"
ARQ_COBERTURA = DADOS / "derived" / "cobertura.json"  # chaves esperadas: "acuracia", "cobertura"

# ----------------------------------------------------------------- premissas
CENARIOS = ["conservador", "base", "otimista"]

# enunciado: "algo em torno de 30 mil tickets por ano segundo a área"
VOLUME_ANUAL = 30_000

# dataset: distribuição de Topic_group em all_tickets_processed_improved_v3.csv (calculada abaixo)
ARQ_COMPOSICAO = DADOS / "all_tickets_processed_improved_v3.csv"

# premissa minha: minutos para ler, classificar e encaminhar um ticket, por cenário
MIN_TRIAGEM = {"conservador": 3, "base": 5, "otimista": 8}

# premissa minha: custo por hora de agente de suporte em reais, por cenário
CUSTO_HORA = {"conservador": 25.0, "base": 35.0, "otimista": 50.0}

# dataset: baseline TF-IDF + regressão logística do script 01 (01_auditoria_dados.txt, item 15),
# usado só se solution/data/derived/cobertura.json não existir
ACURACIA_FALLBACK = 0.858
COBERTURA_FALLBACK = 1.0

# premissa minha: minutos de retrabalho quando a triagem automática erra
MIN_RETRABALHO = 10

# premissa minha: horas produtivas de um FTE por ano
HORAS_FTE = 1_760


class Tee:
    def __init__(self, caminho):
        self.arq = open(caminho, "w", encoding="utf-8")
        self.term = sys.stdout

    def write(self, s):
        self.arq.write(s)
        self.term.write(s)

    def flush(self):
        self.arq.flush()
        self.term.flush()


sys.stdout = Tee(SAIDA)
pd.set_option("display.width", 200)

# --------------------------------------------------- carga de premissas de dado
composicao = pd.read_csv(ARQ_COMPOSICAO)["Topic_group"].value_counts(normalize=True)

if ARQ_COBERTURA.exists():
    cob = json.loads(ARQ_COBERTURA.read_text(encoding="utf-8"))
    ACURACIA, COBERTURA = float(cob["acuracia"]), float(cob["cobertura"])
    fonte_acuracia = f"dataset: {ARQ_COBERTURA.relative_to(AQUI.parent)}"
else:
    ACURACIA, COBERTURA = ACURACIA_FALLBACK, COBERTURA_FALLBACK
    fonte_acuracia = "dataset: baseline do script 01 (01_auditoria_dados.txt, item 15); cobertura.json ausente"

PREMISSAS = [
    ("volume anual de tickets", VOLUME_ANUAL, "enunciado"),
    ("composição por categoria", f"{len(composicao)} categorias de Topic_group",
     f"dataset: {ARQ_COMPOSICAO.relative_to(AQUI.parent)}"),
    ("minutos de triagem manual por ticket", MIN_TRIAGEM, "premissa minha"),
    ("custo por hora de agente (R$)", CUSTO_HORA, "premissa minha"),
    ("acurácia da triagem automática", ACURACIA, fonte_acuracia),
    ("cobertura da triagem automática", COBERTURA, fonte_acuracia),
    ("minutos de retrabalho por triagem errada", MIN_RETRABALHO, "premissa minha"),
    ("horas por FTE por ano", HORAS_FTE, "premissa minha"),
]

print("PREMISSAS USADAS")
for nome, valor, fonte in PREMISSAS:
    print(f"  {nome}: {valor}  [{fonte}]")
print(f"resultado depende de {len(PREMISSAS)} premissas empilhadas")

print("\nCOMPOSIÇÃO POR CATEGORIA (dataset) E VOLUME ANUAL DERIVADO")
comp = pd.DataFrame({
    "fração": composicao.round(4),
    "tickets/ano": (composicao * VOLUME_ANUAL).round(0).astype(int),
})
print(comp.to_string())


# ------------------------------------------------------------------ cálculo
def calcular(cenario):
    minutos = MIN_TRIAGEM[cenario]
    linhas = []
    for categoria, fracao in composicao.items():
        tickets = VOLUME_ANUAL * fracao
        horas_manual = tickets * minutos / 60
        tickets_auto = tickets * COBERTURA
        horas_absorvidas = tickets_auto * minutos / 60
        erros = tickets_auto * (1 - ACURACIA)
        horas_retrabalho = erros * MIN_RETRABALHO / 60
        linhas.append({
            "categoria": categoria,
            "tickets/ano": tickets,
            "h manual hoje": horas_manual,
            "h absorvidas": horas_absorvidas,
            "erros/ano": erros,
            "h retrabalho": horas_retrabalho,
            "h líquidas": horas_absorvidas - horas_retrabalho,
        })
    tab = pd.DataFrame(linhas).set_index("categoria")
    tab.loc["TOTAL"] = tab.sum()
    return tab


resultados = {}
for cenario in CENARIOS:
    tab = calcular(cenario)
    total = tab.loc["TOTAL"]
    resultados[cenario] = total
    por_mil = total / (VOLUME_ANUAL / 1000)
    print(f"\nCENÁRIO {cenario.upper()}: {MIN_TRIAGEM[cenario]} min/ticket, "
          f"R$ {CUSTO_HORA[cenario]:.2f}/h, acurácia {ACURACIA:.3f}, cobertura {COBERTURA:.2f}")
    print(tab.round(1).to_string())
    print(f"por mil tickets: h manual hoje {por_mil['h manual hoje']:.1f}, "
          f"h absorvidas {por_mil['h absorvidas']:.1f}, h retrabalho {por_mil['h retrabalho']:.1f}, "
          f"h líquidas {por_mil['h líquidas']:.1f}")
    print(f"horas líquidas economizadas por ano: {total['h líquidas']:.0f} h "
          f"= {total['h líquidas'] / HORAS_FTE:.2f} FTE")
    print(f"valor anual em reais: R$ {total['h líquidas'] * CUSTO_HORA[cenario]:,.0f}")

cons, otim = resultados["conservador"], resultados["otimista"]
print("\nRESULTADO PRINCIPAL (faixa conservador a otimista)")
print(f"horas de triagem manual hoje: {cons['h manual hoje']:.0f} a {otim['h manual hoje']:.0f} h/ano")
print(f"horas líquidas economizadas: {cons['h líquidas']:.0f} a {otim['h líquidas']:.0f} h/ano")
print(f"fração de FTE: {cons['h líquidas'] / HORAS_FTE:.2f} a {otim['h líquidas'] / HORAS_FTE:.2f} FTE")
print(f"por mil tickets: {cons['h líquidas'] / (VOLUME_ANUAL / 1000):.1f} a "
      f"{otim['h líquidas'] / (VOLUME_ANUAL / 1000):.1f} h líquidas")
print(f"\nsaída gravada em {SAIDA.relative_to(AQUI.parent)}")
