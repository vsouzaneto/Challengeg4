"""OS-11 - Roda a analise completa em sequencia e para no primeiro erro.

Ordem: os01 a os06 -> build_tool.py -> validadores no Node.
Nao gera PDFs: isso fica no os07_pdf.py, rodado a parte.
"""

import shutil
import subprocess
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SUB_ROOT = SCRIPT_DIR.parents[1]
TOOL_DIR = SUB_ROOT / "solution" / "tool"

ANALISES = [
    ("os01", "os01_base_amostral.py"),
    ("os02", "os02_benchmark.py"),
    ("os03", "os03_patrocinio_validacao.py"),
    ("os03b", "os03b_fit_audiencia.py"),
    ("os03c", "os03c_robustez.py"),
    ("os04", "os04_complementos.py"),
    ("os05", "os05_graficos.py"),
    ("os06", "os06_lacunas.py"),
]

VALIDADORES = ["validar_engine.mjs", "validar_os09.mjs"]

resultados = []


def rodar(etapa, comando, cwd):
    print(f"\n{'=' * 70}\n>>> {etapa}\n{'=' * 70}", flush=True)
    inicio = time.perf_counter()
    codigo = subprocess.run(comando, cwd=cwd).returncode
    gasto = time.perf_counter() - inicio
    resultados.append((etapa, gasto, "ok" if codigo == 0 else f"ERRO (codigo {codigo})"))
    return codigo == 0


def tabela():
    print(f"\n{'=' * 70}\nResumo\n{'=' * 70}")
    print(f"| {'etapa':<16} | {'tempo (s)':>9} | status")
    print(f"|{'-' * 18}|{'-' * 11}|{'-' * 24}")
    for etapa, gasto, status in resultados:
        tempo = "-" if gasto is None else f"{gasto:.1f}"
        print(f"| {etapa:<16} | {tempo:>9} | {status}")
    total = sum(d for _, d, _ in resultados if d is not None)
    print(f"\nTempo total: {total:.1f} s")


for etapa, script in ANALISES:
    if not rodar(etapa, [sys.executable, str(SCRIPT_DIR / script)], SCRIPT_DIR):
        tabela()
        sys.exit(1)

if not rodar("build_tool", [sys.executable, str(TOOL_DIR / "build_tool.py")], TOOL_DIR):
    tabela()
    sys.exit(1)

if shutil.which("node") is None:
    print("\nAVISO: Node.js nao encontrado. Os validadores do motor foram pulados.")
    for mjs in VALIDADORES:
        resultados.append((mjs.replace(".mjs", ""), None, "pulado (sem Node)"))
else:
    for mjs in VALIDADORES:
        if not rodar(mjs.replace(".mjs", ""), ["node", str(TOOL_DIR / mjs)], TOOL_DIR):
            tabela()
            sys.exit(1)

tabela()
