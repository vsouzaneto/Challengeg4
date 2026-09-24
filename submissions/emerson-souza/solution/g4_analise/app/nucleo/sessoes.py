"""
Sessoes: cada analise e uma sessao salva (SQLite + uma pasta por sessao).

Sub-sessoes (cooperativo) guardam de qual sessao vieram (origem_id) e o selo de evidencia.
"""

import json
import os
import shutil
import sqlite3
import uuid
from datetime import datetime

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "sessoes")


def _pasta_base():
    pasta = os.environ.get("G4_SESSOES", BASE)
    os.makedirs(pasta, exist_ok=True)
    return pasta


def _conexao():
    con = sqlite3.connect(os.path.join(_pasta_base(), "g4analise.db"))
    con.row_factory = sqlite3.Row
    con.execute("""
        CREATE TABLE IF NOT EXISTS sessoes (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            modulo TEXT NOT NULL,
            fonte TEXT NOT NULL,          -- 'desafio' ou 'arquivos'
            mapeamento TEXT NOT NULL,     -- JSON {tabela: {campo: coluna}}
            arquivos TEXT NOT NULL,       -- JSON {tabela: caminho}
            origem_id TEXT,               -- sessao-mae (cooperativo)
            origem_descricao TEXT,
            selo TEXT,                    -- verde / amarelo / azul
            criada_em TEXT NOT NULL
        )""")
    return con


def pasta_da_sessao(sessao_id):
    return os.path.join(_pasta_base(), sessao_id)


def criar(nome, modulo, fonte, mapeamento, arquivos, origem_id=None, origem_descricao=None, selo=None):
    sessao_id = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + uuid.uuid4().hex[:6]
    os.makedirs(pasta_da_sessao(sessao_id), exist_ok=True)
    with _conexao() as con:
        con.execute(
            "INSERT INTO sessoes VALUES (?,?,?,?,?,?,?,?,?,?)",
            (sessao_id, nome, modulo, fonte, json.dumps(mapeamento), json.dumps(arquivos),
             origem_id, origem_descricao, selo, datetime.now().isoformat(timespec="seconds")),
        )
    return sessao_id


def _para_dict(linha):
    d = dict(linha)
    d["mapeamento"] = json.loads(d["mapeamento"])
    d["arquivos"] = json.loads(d["arquivos"])
    return d


def listar():
    with _conexao() as con:
        return [_para_dict(l) for l in con.execute("SELECT * FROM sessoes ORDER BY criada_em DESC")]


def obter(sessao_id):
    with _conexao() as con:
        l = con.execute("SELECT * FROM sessoes WHERE id=?", (sessao_id,)).fetchone()
    return _para_dict(l) if l else None


def filhas(sessao_id):
    return [s for s in listar() if s["origem_id"] == sessao_id]


def apagar(sessao_id):
    """Apaga a sessao, as sub-sessoes dela e as pastas."""
    for f in filhas(sessao_id):
        apagar(f["id"])
    with _conexao() as con:
        con.execute("DELETE FROM sessoes WHERE id=?", (sessao_id,))
    shutil.rmtree(pasta_da_sessao(sessao_id), ignore_errors=True)


def salvar_arquivo(sessao_id, nome_tabela, arquivo_enviado):
    """Copia um arquivo enviado pela tela para a pasta da sessao."""
    pasta = os.path.join(pasta_da_sessao(sessao_id), "entrada")
    os.makedirs(pasta, exist_ok=True)
    extensao = os.path.splitext(arquivo_enviado.name)[1].lower()
    destino = os.path.join(pasta, f"{nome_tabela}{extensao}")
    with open(destino, "wb") as f:
        f.write(arquivo_enviado.getbuffer())
    return destino


def atualizar_arquivos(sessao_id, arquivos):
    with _conexao() as con:
        con.execute("UPDATE sessoes SET arquivos=? WHERE id=?", (json.dumps(arquivos), sessao_id))
