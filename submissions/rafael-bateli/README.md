# Submissão — Rafael Bateli — Challenge 002

## Sobre mim

- **Nome:** Rafael Bateli
- **LinkedIn:** _(preencher)_
- **Challenge escolhido:** 002 — Redesign de Suporte

---

## Executive Summary

O fluxo de suporte trava porque **o dado não é registrado corretamente**, e isso é problema de **ferramenta e processo, não de pessoas**:
- A triagem (tipo, assunto e prioridade) acerta **18,3%**, exatamente o acaso.
- Não existe horário de abertura do ticket, e **49%** dos tickets fechados aparecem "resolvidos" antes da primeira resposta.
- **1 em cada 3 tickets nunca foi respondido**, e um *Critical* fica parado na mesma proporção que um *Low*.

O desperdício é de **≈ 3.400 h/ano (≈ R$ 119 mil)**, e o maior item recuperável é a **retriagem**. Uma triagem por IA validada em 48 mil tickets reais classifica **73% dos tickets sozinha com 95% de acerto** e devolve **≈ 1.345 h/ano**. Cada conclusão passou por um harness de 10 testes que tenta derrubá-la.

> **Status:** Entrega 1 (diagnóstico) concluída. Entregas 2 (proposta de automação) e 3 (protótipo) em andamento.

---

## Solução

### Abordagem

1. **Auditar o dado antes de analisar.** Cada coluna foi checada, e o que o dado não sustenta virou achado ("a captura está quebrada"), não gráfico.
2. **Decidir com 3 opções por etapa**, com prós e contras equivalentes, e registrar por que a escolhida vence.
3. **Tentar derrubar cada conclusão** com um harness: controle positivo, efeito plantado, permutação, Monte Carlo e forense humano × ferramenta.
4. **Trazer a solução, não só o erro:** causa raiz de cada problema, dono, regra de verificação e código que roda.

### Resultados / Findings

| Documento | Conteúdo |
|---|---|
| [**DIAGNOSTICO.md**](solution/diagnostico/DIAGNOSTICO.md) | Onde o fluxo trava, o que impacta o CSAT, quanto se desperdiça |
| [**CAUSA_RAIZ_E_SOLUCAO.md**](solution/diagnostico/CAUSA_RAIZ_E_SOLUCAO.md) | 9 causas (humano, ferramenta ou processo), 3 opções para cada, a solução e o plano |
| [**HARNESS.md**](solution/diagnostico/HARNESS.md) | 10 testes de verificação, o que eles me pegaram errando e a aderência ao desafio |

**Código que roda:**

| Script | O que faz |
|---|---|
| [`diagnostico.py`](solution/diagnostico/diagnostico.py) | Gera todos os números e gráficos do diagnóstico |
| [`harness.py`](solution/diagnostico/harness.py) | 10 testes de verificação (H1–H10) |
| [`solucao/quality_gate.py`](solution/diagnostico/solucao/quality_gate.py) | Contrato de dados: 12 regras; reprova o export atual (exit 1) |
| [`solucao/triagem_ia.py`](solution/diagnostico/solucao/triagem_ia.py) | Triagem por IA com limiar de confiança + ROI + fila do backlog repriorizada |

### Recomendações

1. **Semana 1:** Quality Gate no ETL, mutirão do backlog pela fila repriorizada, política automática de pendentes, dono do dado nomeado.
2. **Semanas 2–4:** consertar a captura (horário de abertura, horários vindos do log de eventos, template, resolução estruturada, CSAT em todo ticket, `customer_id`).
3. **Semanas 3–8:** triagem por IA (LLM sem treino → conjunto de referência → modelo supervisionado com limiar) e prioridade pelo conteúdo com SLA.
4. **Mês 3:** rodar o diagnóstico de novo sobre o dado corrigido e decidir capacidade com números.

### Limitações

- O Dataset 1 é sintético; a distribuição uniforme vem da forma como foi gerado.
- Minutos por tarefa e custo/hora são premissas explícitas (Monte Carlo em H6); só o ganho da triagem por IA é medido.
- O Dataset 2 prova a técnica em texto real, mas em outra taxonomia. A acurácia na taxonomia desta operação exige o critério de aprovação descrito na causa raiz (P2).

---

## Setup

```bash
pip install -r solution/diagnostico/requirements.txt

# Datasets (Kaggle, CC0) em solution/data/ — não versionados:
#   solution/data/support_tickets.csv  ← Customer Support Ticket Dataset (suraj520)
#   solution/data/it_tickets.csv       ← IT Service Ticket Classification (adisongoh)

cd solution/diagnostico
python diagnostico.py                 # ≈ 10 s — números e gráficos
python harness.py                     # ≈ 30 s — 10 testes
python solucao/quality_gate.py        # exit 1 = export reprovado
python solucao/triagem_ia.py          # IA de triagem + fila do backlog
```

---

## Process Log — Como usei IA

> Detalhado em [`process-log/`](process-log/).

### Ferramentas usadas

| Ferramenta | Para que usou |
|---|---|
| Claude Code (desktop, Claude Opus) | Exploração dos dados, análise estatística, harness, scripts da solução e redação dos documentos |

### Workflow

1. Contexto do desafio + duas regras minhas para a IA: **"sempre 3 opções por etapa, sem enviesar"** e **"se faltar dado, a resposta é: o fluxo trava porque o dado não é registrado corretamente, e é preciso achar o erro e trazer a solução"**.
2. Diagnóstico inicial (Entrega 1) → revisão crítica.
3. Pedi um harness para verificar se as decisões estavam certas, a aderência ao desafio e a pergunta **"é problema humano ou de ferramenta?"**.
4. O harness corrigiu 6 erros do próprio diagnóstico (ver process log).

### Onde a IA errou e como corrigi

Ver [`process-log/01-diagnostico.md`](process-log/01-diagnostico.md): teste de poder inflado, faixa de desperdício exagerada, número com denominador errado, bug no teste de desalinhamento, hipótese fraca apresentada como conclusão e duas fontes para o mesmo número.

### O que eu adicionei que a IA sozinha não faria

- Recusar entregar "só o erro": exigir a solução com dono e verificação.
- A pergunta **humano × ferramenta**, que mudou o destinatário do plano (TI/processo, não o time de agentes).
- O formato de decisão com **3 opções e justificativa**, para não enviesar.
- Exigir um harness que tentasse derrubar as conclusões antes de aceitá-las.

---

## Evidências

- [x] Git history (commits desta branch)
- [x] Narrativa escrita: [`process-log/01-diagnostico.md`](process-log/01-diagnostico.md)
- [x] Registro de decisões (DIAGNOSTICO.md) e de erros corrigidos (HARNESS.md)
- [ ] Chat export / screenshots das sessões _(adicionar em `process-log/chat-exports/`)_

---

_Submissão enviada em: (em andamento)_
