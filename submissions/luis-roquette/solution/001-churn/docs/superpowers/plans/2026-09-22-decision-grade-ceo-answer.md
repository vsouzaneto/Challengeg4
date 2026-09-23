# Decision-Grade CEO Answer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** elevar a resposta central do Challenge 001 para nota mínima 9,5/10 em clareza, precisão, cobertura, calibração causal e utilidade decisória.

**Architecture:** manter `ceo_answer.json` como fonte única. Reutilizar as métricas canônicas já calculadas, corrigir seleção e linguagem executiva em `publish.py`, e fazer relatório/dashboard apenas renderizarem essa decisão. Nenhuma dependência ou motor analítico paralelo será criado.

**Tech Stack:** Python 3.12, pandas, NumPy, statsmodels, Streamlit, pytest, Ruff e artefatos JSON/CSV existentes.

**Spec:** `.specs/tasks/done/raise-ceo-answer-to-9-5.feature.md`

## Global Constraints

- Qualidade da resposta precede UI, integrações e LLM.
- Confiança na comunicação não pode ser confundida com certeza causal.
- `ceo_answer.json`, relatório e dashboard compartilham claims, valores e `analysis_id`.
- Sem API paga, nova dependência, contato externo ou edição manual de artefatos derivados.
- Gates pesados executam no Codespace via `codespace-manager`.
- O app permanece somente leitura e nunca recalcula análise.

## Review Focus

- Todos os mecanismos inconclusivos: a UI deve dizer “causa não demonstrada”, nunca escolher a primeira linha como vencedora.
- RR elegível próximo de 1: o bloco “onde” deve declarar ausência de concentração material.
- Satisfação com cobertura abaixo de 70%: não generalizar respondentes para clientes.
- MRR observado: nunca apresentar como receita recuperável ou somar estoques mensais.
- Headline curta: conter resposta, limite e decisão sem jargão interno ou promessa causal.

---

### Task 1: Fixar a rubrica e o contrato executivo

**Files:**
- Create: `docs/executive-answer-rubric.md`
- Modify: `tests/test_publish.py`

**Interfaces:**
- Consumes: `ceo_answer.json` schema v1 e os seis critérios da SPEC.
- Produces: função de teste `score_executive_answer_contract(answer) -> dict[str, float | list[str]]` somente em testes; a nota humana continua separada.

- [x] **Step 1: escrever o teste RED dos hard caps**

```python
def test_executive_answer_has_no_causal_overclaim(analysis_result) -> None:
    answer = _build_ceo_answer(analysis_result)
    executive_text = " ".join(
        [answer["headline"], *[block["summary"] for block in answer["blocks"]]]
    ).lower()
    assert "mecanismo mais forte" not in executive_text
    assert "plausible_hypothesis" not in executive_text
    assert "auto_renew_off" not in executive_text
    assert "causa ainda não demonstrada" in executive_text
```

- [x] **Step 2: confirmar RED**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_publish.py::test_executive_answer_has_no_causal_overclaim -q`

Expected: FAIL porque a resposta atual publica `auto_renew_off` como mecanismo mais forte.

- [x] **Step 3: documentar a rubrica sem automatizar julgamento subjetivo**

Criar a tabela de pesos da SPEC, exemplos de nota 7,0 e 9,5 e os hard caps. Não hardcodar uma nota de aprovação no produto.

- [x] **Step 4: revisar a rubrica contra CK-1–CK-12 e HR-1–HR-3**

Run: `rg -n "Resposta direta|Precisão quantitativa|Reconciliação|Calibração causal|Utilidade decisória|Consistência" docs/executive-answer-rubric.md`

Expected: seis dimensões presentes; soma dos pesos igual a 10,0.

- [x] **Step 5: checkpoint**

```bash
git add docs/executive-answer-rubric.md tests/test_publish.py
git commit -m "test(churn): define decision-grade answer rubric"
```

### Task 2: Construir o veredito executivo com fatos completos

**Files:**
- Modify: `src/ravenstack_churn/publish.py`
- Test: `tests/test_publish.py`

**Interfaces:**
- Consumes: `monthly_churn`, `claim_checks`, `segment_metrics`, `mechanism_scorecard` e `quality_report` de `AnalysisResult`.
- Produces: `_build_ceo_answer(result) -> dict[str, object]` com os mesmos cinco IDs de bloco e claims adicionais rastreáveis.

- [x] **Step 1: escrever testes RED para impacto e ausência de falsa concentração**

```python
def test_ceo_answer_quantifies_impact_and_denies_false_concentration(analysis_result) -> None:
    answer = _build_ceo_answer(analysis_result)
    claims = {claim["id"]: claim for block in answer["blocks"] for claim in block["claims"]}
    expected_mrr = (
        analysis_result.monthly_churn.query(
            "period == 'comparison_period' and segment_type == 'all' and segment_value == 'all'"
        )
        .sort_values("period_end")
        .iloc[-1]["mrr_lost"]
    )
    assert claims["C-churn-impact"]["unit"] == "monthly_recurring_revenue"
    assert claims["C-churn-impact"]["value"] == expected_mrr
    where = next(block for block in answer["blocks"] if block["id"] == "where")
    assert "não há concentração material demonstrada" in where["summary"].lower()
```

- [x] **Step 2: confirmar RED**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_publish.py -k "impact or false_concentration" -q`

Expected: FAIL porque o MRR não está no contrato executivo e o RR 1,08× ainda é apresentado como concentração.

- [x] **Step 3: implementar a menor composição possível**

Em `_build_ceo_answer`, reutilizar as linhas `comparison_period/all/all`, adicionar `C-churn-impact` com moeda/período/limitação e trocar o resumo de `where` por ausência de concentração quando nenhum recorte sustentar excesso relevante. Não criar novo cálculo em `publish.py`.

- [x] **Step 4: testar valores, referências e linguagem**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_publish.py -q`

Expected: PASS; cada claim resolve para uma linha e nenhuma frase transforma MRR observado em recuperação.

- [x] **Step 5: checkpoint**

```bash
git add src/ravenstack_churn/publish.py tests/test_publish.py
git commit -m "feat(churn): publish complete CEO verdict"
```

### Task 3: Substituir a falsa causa por uma matriz de evidência e ação

**Files:**
- Modify: `src/ravenstack_churn/publish.py`
- Test: `tests/test_publish.py`

**Interfaces:**
- Consumes: gates fechados de `mechanism_scorecard`.
- Produces: bloco `strongest_mechanism` compatível, com título executivo, `summary` abstencionista e claims traduzidos; três `Action` completas em `next_actions`.

- [x] **Step 1: escrever testes RED para abstenção e três ações**

```python
def test_inconclusive_mechanisms_create_validation_plan_not_winner(analysis_result) -> None:
    answer = _build_ceo_answer(analysis_result)
    mechanism = next(block for block in answer["blocks"] if block["id"] == "strongest_mechanism")
    actions = next(block for block in answer["blocks"] if block["id"] == "next_actions")["actions"]
    assert mechanism["title"] == "Causa ainda não demonstrada"
    assert len(actions) == 3
    assert {action["owner_role"] for action in actions} == {
        "Head de Dados", "Head de Produto", "Head de CS"
    }
    assert all(action["advance_if"] and action["stop_if"] for action in actions)
```

- [x] **Step 2: confirmar RED**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_publish.py -k "validation_plan_not_winner" -q`

Expected: FAIL porque existe uma única ação genérica e o primeiro mecanismo vira destaque arbitrário.

- [x] **Step 3: implementar seleção abstencionista**

Se `supported` estiver vazio, não eleger scorecard row. Publicar `M-none-supported` com contagem zero, listar hipóteses apenas na evidência detalhada e criar ações determinísticas para integridade, uso prospectivo e satisfação representativa.

- [x] **Step 4: validar estados supported/tied/inconclusive/unavailable**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_publish.py -k "supported or tied or inconclusive or unavailable" -q`

Expected: PASS nos quatro estados; intervenção continua proibida sem mecanismo sustentado.

- [x] **Step 5: checkpoint**

```bash
git add src/ravenstack_churn/publish.py tests/test_publish.py
git commit -m "fix(churn): calibrate causal answer and actions"
```

### Task 4: Renderizar leitura de 45 segundos no dashboard e relatório

**Files:**
- Modify: `app.py`
- Modify: `src/ravenstack_churn/publish.py`
- Test: `tests/test_app.py`
- Test: `tests/test_publish.py`

**Interfaces:**
- Consumes: `headline`, cinco blocos, claims e actions já validados.
- Produces: hero e blocos sem cálculo; relatório com a mesma ordem e linguagem.

- [x] **Step 1: escrever testes RED de legibilidade e confiança**

```python
def test_dashboard_exposes_verdict_limits_and_decision_before_tabs(generated_artifacts, monkeypatch):
    monkeypatch.setenv("RAVENSTACK_ARTIFACT_DIR", str(generated_artifacts))
    app = AppTest.from_file(SOLUTION_ROOT / "app.py").run(timeout=20)
    text = " ".join(element.value for element in app.markdown)
    assert "Causa ainda não demonstrada" in text
    assert "Alta confiança" in text
    assert "Baixa confiança" in text
    assert not app.exception
```

- [x] **Step 2: confirmar RED**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_app.py -k "verdict_limits" -q`

Expected: FAIL porque a UI não traduz níveis de evidência em confiança executiva.

- [x] **Step 3: reutilizar o renderer atual**

Mapear `confirmed_fact -> Alta confiança`, `supported_mechanism -> Moderada`, `plausible_hypothesis/inconclusive -> Baixa`; não criar componente, gráfico ou dependência nova. Remover snake_case da apresentação.

- [x] **Step 4: validar igualdade entre superfícies**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_publish.py tests/test_app.py -q`

Expected: PASS; headline, claims, ações e limitações iguais no JSON, relatório e dashboard.

- [x] **Step 5: checkpoint**

```bash
git add app.py src/ravenstack_churn/publish.py tests/test_app.py tests/test_publish.py
git commit -m "feat(churn): render decision-grade CEO answer"
```

### Task 5: Fechar a nota 9,5 com gate adversarial e reprodução

**Files:**
- Modify: `docs/executive-answer-rubric.md`
- Modify: `README.md`
- Modify: `../../../process-log/003-implementacao-feedback-looping.md`
- Regenerate: `artifacts/`

**Interfaces:**
- Consumes: branch completa e rubrica de 10 pontos.
- Produces: avaliação assinada por dimensão, artefatos finais e evidência do gate no mesmo SHA.

- [x] **Step 1: executar revisão adversarial sem editar código**

Pontuar as seis dimensões, copiar as frases que sustentam cada nota e registrar qualquer hard cap. Se a nota for menor que 9,5, voltar à task dona da lacuna; não arredondar.

- [x] **Step 2: executar gate direcionado local**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_publish.py tests/test_app.py -q`

Expected: PASS sem exceções, jargão executivo ou divergência entre superfícies.

- [x] **Step 3: executar gate integral no Codespace**

Run via `codespace-manager`: `make setup && make reproduce && make check`

Expected: Ruff, formato, suíte completa, reprodução dupla e `artifact_sets=equal` verdes no SHA exato.

- [x] **Step 4: inspecionar desktop e mobile**

Run: `make app`; verificar desktop e viewport 390×844. Em até 45 segundos, localizar mudança, impacto econômico, explicação do paradoxo, limite causal e três próximas ações.

- [x] **Step 5: registrar e entregar**

Atualizar rubrica, README e diário com nota por dimensão, comandos, SHA, resultado, limitações e contribuição humana. PR/merge somente após revisão de Luis.

**Resultado:** nota interna 9,9/10, sem hard cap. No SHA `e6cd568`, o gate integral terminou com `84 passed` em duas execuções, Ruff e formato verdes e `artifact_sets=equal`. Após a ordem de bypass, nenhum novo preflight foi iniciado: apenas a camada local de publicação foi atualizada a partir dos CSVs canônicos já validados. O dashboard final foi conferido em desktop e 390×844.

## Self-review

- Cobertura da SPEC: cinco tasks cobrem rubrica, fatos, causalidade, ação, superfícies e gates.
- Placeholders: nenhum `TBD`, `TODO` ou etapa sem comando/resultado esperado.
- Consistência: mantém os cinco IDs de bloco e o schema v1; novos claims/actions usam contratos existentes.
- Principal risco: perseguir nota subjetiva por copy. Mitigação: hard caps factuais, referências canônicas e revisão adversarial antes do gate.
