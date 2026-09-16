"""Avaliação do protótipo de triagem (script 06) como um usuário faria. Não altera nada.

Parte 1: seis tickets escritos à mão, cobrindo os três caminhos de decisão.
Parte 2: mil tickets do conjunto de teste (split_teste.csv), semente 7, pela função de triagem.
Só imprime; saída em solution/07_avaliacao_prototipo.txt. Nenhum CSV gravado.
"""

import importlib.util
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

SEED_AVALIACAO = 7   # diferente da semente 42 do script 04
N_LOTE = 1000
AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "data"
DERIVADOS = DADOS / "derived"
SAIDA = AQUI / "07_avaliacao_prototipo.txt"

# (texto, caminho esperado)
TICKETS_MANUAIS = [
    ("My mailbox is full and I cannot receive emails anymore, could you increase the mailbox size please", "automático"),
    ("I forgot my password for the timecard system and cannot submit my hours, please reset it", "automático"),
    ("New starter joining on Monday, she will need a laptop and a badge for the building", "pessoa por conteúdo"),
    ("Urgent: the projector in the main meeting room is not working and we have a client presentation in one hour", "pessoa por conteúdo"),
    ("Please approve the purchase order for 20 new monitors for the finance team", "pessoa por confiança baixa"),
    ("hello how are you", "pessoa por confiança baixa"),
]


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


def caminho(decisao):
    if decisao["regra"].startswith("conteúdo"):
        return "pessoa por conteúdo"
    if decisao["destino"] == "fila humana":
        return "pessoa por confiança baixa"
    return "automático"


def main():
    sys.stdout = Tee(SAIDA)
    pd.set_option("display.width", 200)

    spec = importlib.util.spec_from_file_location("triagem", AQUI / "06_triagem.py")
    triagem = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(triagem)
    limiar = triagem.carregar_limiar()
    modelo = triagem.carregar_modelo(limiar)

    print(f"=== PARTE 1: seis tickets escritos à mão (limiar {limiar}) ===")
    acertos = 0
    for texto, esperado in TICKETS_MANUAIS:
        d = triagem.triar(modelo, limiar, texto)
        obtido = caminho(d)
        acertos += obtido == esperado
        print(f"\n\"{texto}\"")
        print(f"  categoria: {d['categoria']}  confiança: {d['confianca']:.4f}  destino: {d['destino']}")
        print(f"  regra: {d['regra']}")
        print(f"  caminho esperado: {esperado}; obtido: {obtido}; {'confere' if obtido == esperado else 'DIFERE'}")
    print(f"\ncaminhos conforme o esperado: {acertos} de {len(TICKETS_MANUAIS)}")

    print(f"\n=== PARTE 2: {N_LOTE} tickets do teste, semente {SEED_AVALIACAO} ===")
    tk = pd.read_csv(DADOS / "all_tickets_processed_improved_v3.csv")
    idx_teste = pd.read_csv(DERIVADOS / "split_teste.csv")["indice_original"].values
    lote = tk.loc[idx_teste].sample(N_LOTE, random_state=SEED_AVALIACAO)
    decisoes = pd.DataFrame([triagem.triar(modelo, limiar, str(t)) for t in lote["Document"].fillna("")],
                            index=lote.index)
    decisoes["real"] = lote["Topic_group"]
    decisoes["caminho"] = [caminho(d) for _, d in decisoes.iterrows()]

    n = len(decisoes)
    humano = decisoes["destino"] == "fila humana"
    por_conteudo = decisoes["caminho"] == "pessoa por conteúdo"
    por_conf = decisoes["caminho"] == "pessoa por confiança baixa"
    auto = ~humano
    print(f"para pessoa: {humano.sum()} de {n} ({humano.mean():.4f}); "
          f"por regra de conteúdo: {por_conteudo.sum()} ({por_conteudo.mean():.4f}); "
          f"por confiança baixa: {por_conf.sum()} ({por_conf.mean():.4f})")
    print(f"decididos pela máquina: {auto.sum()} ({auto.mean():.4f})")
    conteudo_acima = por_conteudo & (decisoes["confianca"] >= limiar)
    print(f"barrados por conteúdo que teriam seguido automático pela confiança: {conteudo_acima.sum()}")

    dec = decisoes[auto]
    certo = dec["categoria"] == dec["real"]
    print(f"\nacurácia sobre os decididos pela máquina: {certo.mean():.4f} (n={len(dec)})")
    print("por classe real (n = decididos daquela classe; no lote = total da classe nos 1000):")
    tab = pd.DataFrame({
        "no lote": decisoes["real"].value_counts(),
        "n decididos": dec["real"].value_counts(),
        "acurácia": certo.groupby(dec["real"]).mean(),
    }).fillna(0)
    tab["n decididos"] = tab["n decididos"].astype(int)
    tab["fração automática"] = tab["n decididos"] / tab["no lote"]
    print(tab.round(4).to_string())

    erros = dec[~certo]
    print(f"\nerros automáticos: {len(erros)}; pares real → previsto mais comuns:")
    pares = Counter(zip(erros["real"], erros["categoria"]))
    for (real, prev), c in pares.most_common(10):
        print(f"  {real} → {prev}: {c}")

    print("\nregras de conteúdo que dispararam (grupo e termo):")
    disparos = decisoes.loc[por_conteudo, "regra"].str.removeprefix("conteúdo: ").value_counts()
    print(disparos.to_string() if len(disparos) else "  nenhuma")
    print("\nclasse real dos tickets barrados por conteúdo:")
    print(decisoes.loc[por_conteudo, "real"].value_counts().to_string())

    print(f"\nsaída gravada em {SAIDA.relative_to(AQUI.parent)}")


if __name__ == "__main__":
    main()
