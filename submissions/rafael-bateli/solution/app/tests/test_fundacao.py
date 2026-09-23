import json
import os
import time

import pytest

from motor import config, logs
from motor.decisao import Decisao


def test_p5_imports_das_entregas_anteriores():
    import automacao  # noqa: F401  (solution/automacao/automacao.py)
    import modelo  # noqa: F401
    import triagem_ia  # noqa: F401
    assert config.SLA_HORAS["Critical"] == 1


def test_caminhos_trocam_por_variavel_de_ambiente(tmp_path, monkeypatch):
    monkeypatch.setenv("DADOS_DIR", str(tmp_path))
    assert config.csv_d1() == tmp_path / "support_tickets.csv"
    assert config.dados_faltando() == [tmp_path / "support_tickets.csv", tmp_path / "it_tickets.csv"]


def test_carregar_env_nao_sobrescreve(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("X_TESTE=do_arquivo\nY_TESTE='aspas'\n# comentario\n", encoding="utf-8")
    monkeypatch.setenv("X_TESTE", "do_ambiente")
    monkeypatch.delenv("Y_TESTE", raising=False)
    config.carregar_env(env)
    assert os.environ["X_TESTE"] == "do_ambiente"
    assert os.environ["Y_TESTE"] == "aspas"
    monkeypatch.delenv("Y_TESTE")


def test_decisao_registra_rastro():
    d = Decisao("d1", "7")
    d.registrar("qualidade", "ok", "texto utilizável", time.perf_counter())
    d.etapa("rota", "2", "rede", 0.5)
    assert [e.nome for e in d.rastro] == ["qualidade", "rota"]
    assert len(d.trace_id) == 12


def test_p10_log_json_sem_segredo_e_sem_texto(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk-SEGREDO-123")
    logs.registrar("WARNING", "llm", "rate_limit", provedor="groq", texto="não pode aparecer",
                   detalhe="eco da chave gsk-SEGREDO-123")
    conteudo = logs.caminho_log().read_text(encoding="utf-8")
    assert "gsk-SEGREDO-123" not in conteudo
    assert "não pode aparecer" not in conteudo
    reg = json.loads(conteudo.strip().splitlines()[-1])
    assert reg["categoria"] == "rate_limit" and reg["provedor"] == "groq"


def test_categoria_fora_da_lista_e_erro_de_programacao():
    with pytest.raises(ValueError):
        logs.registrar("ERROR", "x", "categoria_inventada")


def test_saude_resume_logs():
    regs = [
        {"etapa": "llm", "status": "ok", "provedor": "groq", "latencia_ms": 100},
        {"etapa": "llm", "status": "erro", "provedor": "groq", "categoria": "rate_limit", "nivel": "WARNING"},
        {"etapa": "llm", "status": "ok", "provedor": "gemini", "latencia_ms": 300},
        {"etapa": "llm_final", "provedor": "groq", "fallback": False},
        {"etapa": "llm_final", "provedor": "gemini", "fallback": True},
        {"etapa": "guardrail", "categoria": "guardrail_reprovou", "regra": "sem_promessa_financeira", "nivel": "WARNING"},
    ]
    s = logs.saude(regs)
    assert s["chamadas_ok_por_provedor"] == {"groq": 1, "gemini": 1}
    assert s["taxa_fallback"] == 0.5
    assert s["erros_por_categoria"]["rate_limit"] == 1
    assert s["bloqueios_guardrail"] == {"sem_promessa_financeira": 1}
    assert len(s["ultimas_falhas"]) == 2


def test_ticket_ref_nao_carrega_texto_inteiro():
    ref = logs.ticket_ref("42", "x" * 500)
    assert ref.startswith("42:") and len(ref) < 120
