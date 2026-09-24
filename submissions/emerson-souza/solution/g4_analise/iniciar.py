"""
G4 Analise - comando unico de inicio.

    python iniciar.py              -> prepara o ambiente (so na 1a vez) e abre o sistema
    python iniciar.py --so-instalar -> so prepara o ambiente, sem abrir
    python iniciar.py --g4os       -> prepara o ambiente e cadastra o G4 Analise no G4 OS (fonte MCP + skill)

O que faz, em ordem:
  1. Confere se a versao do Python e suportada (3.11 a 3.14).
  2. Cria o ambiente isolado (.venv) dentro desta pasta, se ainda nao existir.
  3. Instala as dependencias de requirements.txt no .venv
     (so quando o arquivo mudou desde a ultima instalacao).
  4. Abre o sistema usando o Python do .venv.

Nao precisa de administrador e nao mexe no Python do computador.
Este arquivo usa so a biblioteca padrao do Python, para rodar antes de qualquer instalacao.
"""

import hashlib
import os
import subprocess
import sys

VERSAO_MIN = (3, 11)
VERSAO_MAX = (3, 14)

PASTA = os.path.dirname(os.path.abspath(__file__))
VENV = os.path.join(PASTA, ".venv")
REQUISITOS = os.path.join(PASTA, "requirements.txt")
MARCA = os.path.join(VENV, ".requisitos_instalados")
APP = os.path.join(PASTA, "app", "principal.py")


def aviso(texto):
    print(f"[G4 Analise] {texto}", flush=True)


def conferir_versao():
    atual = sys.version_info[:2]
    if VERSAO_MIN <= atual <= VERSAO_MAX:
        aviso(f"Python {sys.version.split()[0]} - OK")
        return
    faixa = f"{VERSAO_MIN[0]}.{VERSAO_MIN[1]} a {VERSAO_MAX[0]}.{VERSAO_MAX[1]}"
    aviso(f"Este sistema precisa do Python {faixa}. Voce esta usando o {sys.version.split()[0]}.")
    aviso("Baixe uma versao compativel em https://www.python.org/downloads/ (recomendado: 3.12).")
    if sys.platform.startswith("win"):
        aviso("Se voce ja tem outra versao instalada, rode por ela, por exemplo:  py -3.12 iniciar.py")
    sys.exit(1)


def python_do_venv():
    if sys.platform.startswith("win"):
        return os.path.join(VENV, "Scripts", "python.exe")
    return os.path.join(VENV, "bin", "python")


def criar_venv():
    if os.path.exists(python_do_venv()):
        return
    aviso("Criando o ambiente isolado (.venv) - so acontece na primeira vez...")
    subprocess.run([sys.executable, "-m", "venv", VENV], check=True)


def hash_requisitos():
    with open(REQUISITOS, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def instalar_dependencias():
    atual = hash_requisitos()
    if os.path.exists(MARCA):
        with open(MARCA, encoding="utf-8") as f:
            if f.read().strip() == atual:
                aviso("Dependencias ja instaladas - OK")
                return
    aviso("Instalando as dependencias (pode levar alguns minutos na primeira vez)...")
    py = python_do_venv()
    subprocess.run([py, "-m", "pip", "install", "--upgrade", "pip", "-q"], check=True)
    subprocess.run([py, "-m", "pip", "install", "-r", REQUISITOS], check=True)
    with open(MARCA, "w", encoding="utf-8") as f:
        f.write(atual)
    aviso("Dependencias instaladas - OK")


def abrir_sistema():
    if not os.path.exists(APP):
        aviso("Ambiente pronto. (O sistema ainda esta em construcao: app/principal.py nao existe.)")
        return
    aviso("Abrindo o G4 Analise...")
    resultado = subprocess.run([python_do_venv(), APP] + sys.argv[1:], cwd=PASTA)
    sys.exit(resultado.returncode)


def main():
    conferir_versao()
    try:
        criar_venv()
        instalar_dependencias()
    except subprocess.CalledProcessError:
        aviso("A instalacao falhou (veja a mensagem acima). Confira a internet e rode de novo.")
        sys.exit(1)
    if "--so-instalar" in sys.argv:
        aviso("Ambiente pronto.")
        return
    if "--g4os" in sys.argv:
        r = subprocess.run([python_do_venv(), os.path.join(PASTA, "integracao_g4os", "instalar_no_g4os.py")], cwd=PASTA)
        sys.exit(r.returncode)
    abrir_sistema()


if __name__ == "__main__":
    main()
