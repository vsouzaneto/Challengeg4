"""O servidor MCP (para o agente do G4 OS) testado com um cliente MCP de verdade, pela entrada/saida padrao."""
import asyncio
import json
import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "app"))
from nucleo import leitura  # noqa: E402

pytestmark = pytest.mark.skipif(leitura.pasta_dados_desafio() is None, reason="dados do desafio ausentes")


async def _conversa(tmp, passos):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    env = {**os.environ, "G4_SESSOES": str(tmp / "s"), "G4_EXPORTAR": str(tmp / "e")}
    params = StdioServerParameters(command=sys.executable, args=[os.path.join(RAIZ, "app", "servidor_mcp.py")], env=env)
    async with stdio_client(params) as (ler, escrever):
        async with ClientSession(ler, escrever) as sessao:
            await sessao.initialize()
            return await passos(sessao)


def _json(res):
    assert not res.isError, res.content[0].text
    return json.loads(res.content[0].text) if len(res.content) == 1 else [json.loads(c.text) for c in res.content]


def test_agente_usa_o_g4_analise(tmp_path):
    async def passos(s):
        nomes = {t.name for t in (await s.list_tools()).tools}
        assert {"listar_sessoes", "criar_sessao", "obter_resumo", "consultar_lista", "obter_plano_de_acao",
                "enviar_para_outra_ferramenta", "exportar_sessao", "classificar_ticket", "recomendar_post"} <= nomes
        sid = _json(await s.call_tool("criar_sessao", {"nome": "Churn agente", "modulo": "churn"}))["sessao_id"]
        resumo = _json(await s.call_tool("obter_resumo", {"sessao_id": sid}))
        assert "110 de 500" in resumo["resumo_executivo"][0]
        lista = _json(await s.call_tool("consultar_lista", {"sessao_id": sid, "lista": "contas_priorizadas", "limite": 5}))
        assert len(lista["linhas"]) == 5 and "score_risco" in lista["colunas"]
        plano = _json(await s.call_tool("obter_plano_de_acao", {"sessao_id": sid}))
        assert plano and "acao" in (plano[0] if isinstance(plano, list) else plano)
        sub = _json(await s.call_tool("enviar_para_outra_ferramenta", {"sessao_id": sid, "destino": "suporte"}))
        assert sub["sub_sessao_id"]
        arq = _json(await s.call_tool("exportar_sessao", {"sessao_id": sid, "formato": "csv"}))
        assert os.path.exists(arq["arquivo_salvo"])
        sess = _json(await s.call_tool("listar_sessoes", {}))
        return sess
    sess = asyncio.run(_conversa(tmp_path, passos))
    sess = sess if isinstance(sess, list) and sess and isinstance(sess[0], dict) else sess
    assert len(sess) == 2  # a sessao criada + a sub-sessao (a janela ve as mesmas)


def test_agente_leads_e_erros_claros(tmp_path):
    async def passos(s):
        sid = _json(await s.call_tool("criar_sessao", {"nome": "Leads agente", "modulo": "leads"}))["sessao_id"]
        foco = _json(await s.call_tool("consultar_lista", {"sessao_id": sid, "lista": "foco", "filtros": {"regiao": "West"}, "limite": 3}))
        assert foco["linhas"] and all(x["regiao"] == "West" for x in foco["linhas"])
        erro = await s.call_tool("consultar_lista", {"sessao_id": sid, "lista": "nao_existe"})
        assert erro.isError and "Opções" in erro.content[0].text
    asyncio.run(_conversa(tmp_path, passos))


def test_instalador_cria_so_as_pastas_do_g4_analise(tmp_path, monkeypatch):
    import importlib.util
    ws = tmp_path / ".g4os-public" / "workspaces" / "meu"
    (ws / "sources" / "outra-fonte").mkdir(parents=True)
    (ws / "config.json").write_text("{}")
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.delenv("G4OS_CONFIG_DIR", raising=False)
    spec = importlib.util.spec_from_file_location("inst", os.path.join(RAIZ, "integracao_g4os", "instalar_no_g4os.py"))
    inst = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inst)
    assert inst.workspaces() == [str(ws)]
    inst.instalar(str(ws), "python", "servidor.py", "proj")
    cfg = json.loads((ws / "sources" / "g4-analise" / "config.json").read_text(encoding="utf-8"))
    assert cfg["mcp"]["transport"] == "stdio" and cfg["mcp"]["args"] == ["servidor.py"]
    assert (ws / "skills" / "g4-analise" / "SKILL.md").exists() and (ws / "sources" / "outra-fonte").exists()
