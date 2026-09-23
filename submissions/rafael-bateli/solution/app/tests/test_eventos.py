import pytest

from motor import eventos, logs


def test_grava_le_e_calcula_metricas(tmp_path):
    r = eventos.Registro(tmp_path / "ev.jsonl")
    assert r.gravar("aprovar", ticket_id="1", origem="llm", provedor="groq")
    r.gravar("editar", ticket_id="2", origem="llm", provedor="gemini")
    r.gravar("aprovar", ticket_id="3", origem="template", provedor="template")
    r.gravar("descartar", ticket_id="4", origem="llm", provedor="groq")
    r.gravar("fila_errada", ticket_id="T1", classe_prevista="Hardware", classe_correta="Administrative rights")
    r.gravar("prioridade_alterada", ticket_id="5", de="Low", para="High")
    r.gravar("auditoria_certo", ticket_id="T2")
    r.gravar("auditoria_errado", ticket_id="T3")
    m = eventos.metricas(r.ler())
    assert m["revisados"] == 4
    assert m["aprovacao_sem_edicao"] == 0.5
    assert m["aprovacao_sem_edicao_llm"] == pytest.approx(1 / 3, abs=1e-3)
    assert m["descartes"] == 1
    assert m["devolucoes_por_classe"] == {"Hardware": 1}
    assert m["prioridades_alteradas"] == 1
    assert (m["auditoria_n"], m["auditoria_acerto"]) == (2, 0.5)


def test_tipo_desconhecido_e_erro():
    with pytest.raises(ValueError):
        eventos.Registro().gravar("inventado")


def test_falha_ao_gravar_guarda_na_sessao_e_loga(tmp_path):
    pasta = tmp_path / "e_uma_pasta"
    pasta.mkdir()
    r = eventos.Registro(pasta)  # abrir uma pasta como arquivo falha
    assert r.gravar("aprovar", ticket_id="1") is False
    assert len(r.pendentes) == 1
    assert any(x.get("categoria") == "falha_eventos" for x in logs.ler())
    r.caminho = tmp_path / "ok.jsonl"
    assert r.gravar("aprovar", ticket_id="2") is True
    assert len(r.ler()) == 2 and r.pendentes == []


def test_metricas_vazias():
    m = eventos.metricas([])
    assert m["revisados"] == 0 and m["aprovacao_sem_edicao"] is None
