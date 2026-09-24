"""
Cadastra o G4 Analise no G4 OS: uma FONTE MCP (stdio) e uma SKILL no(s) workspace(s) do G4 OS.

    python integracao_g4os/instalar_no_g4os.py            (normalmente via:  python iniciar.py --g4os)

- Acha os workspaces em ~/.g4os-public/workspaces e ~/.g4os/workspaces (ou G4OS_CONFIG_DIR).
- Cria/atualiza SO as pastas sources/g4-analise e skills/g4-analise. Nada mais e alterado.
- A fonte chama o Python do .venv deste projeto com app/servidor_mcp.py.
Depois, no G4 OS: abra Fontes, confira "G4 Analise" e (se pedir) clique em testar.
"""

import json
import os
import shutil
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
PROJETO = os.path.dirname(AQUI)


def python_do_venv(projeto=PROJETO, windows=None):
    windows = sys.platform.startswith("win") if windows is None else windows
    return os.path.join(projeto, ".venv", "Scripts", "python.exe") if windows else os.path.join(projeto, ".venv", "bin", "python")


def config_da_fonte(python, servidor, projeto):
    agora = int(time.time() * 1000)
    return {
        "id": f"g4-analise_{agora}",
        "name": "G4 Analise (Churn, Suporte, Leads, Mídia)",
        "slug": "g4-analise",
        "enabled": True,
        "provider": "custom-mcp",
        "type": "mcp",
        "icon": "📊",
        "tagline": "Análises de churn, suporte, leads e mídia social: resumo executivo, listas priorizadas, plano de ação "
                   "com evidência, cruzamentos entre áreas e relatórios. Mesmas sessões da janela do G4 Analise.",
        "mcp": {"transport": "stdio", "command": python, "args": [servidor], "cwd": projeto, "authType": "none"},
        "isAuthenticated": True,
        "connectionStatus": "untested",
        "createdAt": agora,
        "updatedAt": agora,
    }


def workspaces():
    raizes = [os.environ.get("G4OS_CONFIG_DIR")] if os.environ.get("G4OS_CONFIG_DIR") else []
    casa = os.path.expanduser("~")
    raizes += [os.path.join(casa, ".g4os-public"), os.path.join(casa, ".g4os")]
    achados = []
    for r in raizes:
        w = os.path.join(r, "workspaces")
        if os.path.isdir(w):
            achados += [os.path.join(w, d) for d in os.listdir(w) if os.path.isfile(os.path.join(w, d, "config.json"))]
    return achados


def instalar(workspace, python, servidor, projeto):
    fonte = os.path.join(workspace, "sources", "g4-analise")
    skill = os.path.join(workspace, "skills", "g4-analise")
    os.makedirs(fonte, exist_ok=True)
    os.makedirs(skill, exist_ok=True)
    antigo = os.path.join(fonte, "config.json")
    cfg = config_da_fonte(python, servidor, projeto)
    if os.path.exists(antigo):  # atualizacao: mantem id e data de criacao
        with open(antigo, encoding="utf-8") as f:
            velho = json.load(f)
        cfg["id"], cfg["createdAt"] = velho.get("id", cfg["id"]), velho.get("createdAt", cfg["createdAt"])
    with open(antigo, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    shutil.copyfile(os.path.join(AQUI, "guide.md"), os.path.join(fonte, "guide.md"))
    shutil.copyfile(os.path.join(AQUI, "permissions.json"), os.path.join(fonte, "permissions.json"))
    shutil.copyfile(os.path.join(AQUI, "SKILL.md"), os.path.join(skill, "SKILL.md"))
    return fonte, skill


def main():
    python = python_do_venv()
    servidor = os.path.join(PROJETO, "app", "servidor_mcp.py")
    if not os.path.exists(python):
        print("[G4 Analise] Rode antes:  python iniciar.py --so-instalar  (cria o .venv com as dependencias).")
        sys.exit(1)
    ws = workspaces()
    if not ws:
        print("[G4 Analise] Não achei o G4 OS neste computador (~/.g4os-public/workspaces). Abra o G4 OS uma vez e rode de novo.")
        sys.exit(1)
    for w in ws:
        fonte, skill = instalar(w, python, servidor, PROJETO)
        print(f"[G4 Analise] Instalado no workspace '{os.path.basename(w)}':\n  fonte: {fonte}\n  skill: {skill}")
    print("[G4 Analise] Pronto. No G4 OS, abra Fontes -> 'G4 Analise' (teste a conexão) e pergunte, por exemplo: "
          "'quais contas eu salvo esta semana?'")


if __name__ == "__main__":
    main()
