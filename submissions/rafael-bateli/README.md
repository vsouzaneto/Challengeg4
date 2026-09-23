# Submissão — Rafael Bateli — Challenge 002

## Sobre mim

- **Nome:** Rafael Bateli
- **LinkedIn:** https://www.linkedin.com/in/rafael-bateli/
- **Challenge escolhido:** 002 — Redesign de Suporte

---

## Executive Summary

O fluxo de suporte trava porque **o dado não é registrado corretamente**, e isso é problema de **ferramenta e processo, não de pessoas**:
- A triagem (tipo, assunto e prioridade) acerta **18,3%**, exatamente o acaso.
- Não existe horário de abertura do ticket, e **49%** dos tickets fechados aparecem "resolvidos" antes da primeira resposta.
- **1 em cada 3 tickets nunca foi respondido**, e um *Critical* fica parado na mesma proporção que um *Low*.

O desperdício é de **≈ 3.400 h/ano (≈ R$ 119 mil)**, e o maior item recuperável é a **retriagem**. Uma triagem por IA validada em 48 mil tickets reais classifica **73% dos tickets sozinha com 95% de acerto** e devolve **≈ 1.345 h/ano**. Cada conclusão passou por um harness de 10 testes que tenta derrubá-la.

**Proposta de automação (Entrega 2):** o custo de token não decide nada; toda a LLM da proposta custa ≈ R$ 270/ano. Quem decide é o **custo do erro** e o **tipo de entrada**. **Três regras fixas, sem IA** (pendentes, coleta automática dos dados que faltam, prioridade por sinais) entregam **40% do ganho em 2 semanas**. A classificação usa **modelo supervisionado**, porque para acertar 95% as regras cobrem só 16% dos tickets e o modelo, 73%. A **LLM** só redige e resume, com humano aprovando. **Um terço dos tickets vai direto para humano** (perda de dados, segurança, dinheiro, recontato, hardware), com exemplos reais de cada caso. Total: **≈ 3.470 h/ano (≈ R$ 122 mil)**.

**Aprofundamento (harness + economia + aprendizado):** 13 testes tentaram derrubar a proposta; **4 decisões caíram e voltaram com a solução testada**. O limiar não protege contra um tipo de ticket novo (até 60,5% sai errado com confiança), e o **monitor de devoluções da fila errada** detecta a novidade. 3.000 rótulos dão 50% de cobertura, não 73%, e o **ciclo de aprendizado** com o trabalho que o time já faz leva a 71% em 11 meses. A auditoria de 2% era cega e passou a **10%**. Economias sem perda: **≈ 480 h/ano** a mais (a IA rascunha onde o risco é a decisão, rótulos grátis, triagem com 3 sugestões). O plano de medição da LLM tem métricas com meta, motivos de rejeição em lista fechada e registro de evento.

**Protótipo rodando (Entrega 3):** a proposta funcionando em Streamlit **nos dados reais inteiros**, sem exemplos escolhidos a dedo:
- **fila do agente**: os 2.819 tickets abertos do D1 em ordem de risco real, com rota, motivo e SLA, e os 9.568 tickets de teste do D2 classificados, 70% roteados sozinhos com 95,1% de acerto;
- **painel do Diretor**: replay dos 8.469 tickets, ROI e onde a IA para;
- **"Tente derrubar"**: casos adversários e sorteio de tickets reais.

O protótipo reproduz **100%** das rotas e prioridades das Entregas 1–2, e **141 testes** cobrem os 12 critérios de aceite, incluindo fallback, logs sem segredo e guardrails. A LLM (Groq → Gemini → template) só redige, com guardrail em código. **Medida pela primeira vez**, a LLM zero-shot acertou **39%** contra **86%** do modelo supervisionado nos mesmos tickets, o que confirma a decisão da Entrega 2. Em 75 rascunhos, 15 deles adversários, **não houve violação real**; o guardrail errou uma vez, para o lado seguro.

> **Status:** Entregas 1 (diagnóstico), 2 (proposta de automação) e 3 (protótipo) concluídas.

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
| [**PROPOSTA_AUTOMACAO.md**](solution/automacao/PROPOSTA_AUTOMACAO.md) | O que automatizar, o que NÃO automatizar e o fluxo na prática; determinístico × ML × LLM, custo e impacto × esforço |
| [**HARNESS_AUTOMACAO.md**](solution/automacao/HARNESS_AUTOMACAO.md) | 13 testes contra a proposta, 4 decisões derrubadas com a solução, erros do próprio harness e aderência ao desafio |
| [**ECONOMIA_E_APRENDIZADO.md**](solution/automacao/ECONOMIA_E_APRENDIZADO.md) | Onde economizar sem perder eficiência, onde não economizar, e o que medir para a IA aprender com erros e acertos |
| [**PROTOTIPO.md**](solution/app/PROTOTIPO.md) | **Entrega 3:** o protótipo rodando nos dados reais, os 12 critérios de aceite, a LLM medida, onde a IA para, fallbacks, logs e guardrails |

**Código que roda:**

| Script | O que faz |
|---|---|
| [`diagnostico.py`](solution/diagnostico/diagnostico.py) | Gera todos os números e gráficos do diagnóstico |
| [`harness.py`](solution/diagnostico/harness.py) | 10 testes de verificação (H1–H10) |
| [`solucao/quality_gate.py`](solution/diagnostico/solucao/quality_gate.py) | Contrato de dados: 12 regras; reprova o export atual (exit 1) |
| [`solucao/triagem_ia.py`](solution/diagnostico/solucao/triagem_ia.py) | Triagem por IA com limiar de confiança + ROI + fila do backlog repriorizada |
| [`automacao/automacao.py`](solution/automacao/automacao.py) | Rota de cada ticket, regras × modelo, duplicatas, custo de LLM, impacto × esforço + 5 verificações |
| [`automacao/aprendizado.py`](solution/automacao/aprendizado.py) | Ciclo de aprendizado (11 meses), monitor de categoria nova, tamanho da auditoria, economias |
| [`automacao/harness_automacao.py`](solution/automacao/harness_automacao.py) | 13 testes (A1–A13) que tentam derrubar a proposta |
| [`app/app.py`](solution/app/app.py) | **Protótipo (Streamlit):** fila do agente, painel do Diretor, "Tente derrubar" e qualidade da IA |
| [`app/motor/`](solution/app/motor/) | Motor sem tela: regras e modelo importados das Entregas 1–2, LLM com fallback, guardrails, logs, eventos |
| [`app/tests/`](solution/app/tests/) | 139 testes (P1–P12), sem rede |
| [`app/medir_llm.py`](solution/app/medir_llm.py) | Medição da LLM (M1–M4) com critérios pré-registrados |

### Recomendações

1. **Semanas 1–2:** Quality Gate no ETL, mutirão do backlog pela fila repriorizada, dono do dado nomeado e as regras fixas da Entrega 2 (política de pendentes, coleta automática dos dados que faltam, prioridade por sinais + SLA).
2. **Semanas 2–4:** consertar a captura (horário de abertura, horários vindos do log de eventos, template, resolução estruturada, CSAT em todo ticket, `customer_id`).
3. **Semanas 3–8:** triagem por IA (LLM sem treino → conjunto de referência → modelo supervisionado com limiar) e duplicata/recontato.
4. **Semanas 6–14:** copiloto de resposta e dossiê com LLM, sempre com humano aprovando, a partir de uma base de conhecimento curada.
5. **Mês 3:** rodar o diagnóstico de novo sobre o dado corrigido e decidir capacidade com números.

### Limitações

- O Dataset 1 é sintético; a distribuição uniforme vem da forma como foi gerado.
- Minutos por tarefa e custo/hora são premissas explícitas (Monte Carlo em H6); só o ganho da triagem por IA é medido.
- O Dataset 2 prova a técnica em texto real, mas em outra taxonomia. A acurácia na taxonomia desta operação exige o critério de aprovação descrito na causa raiz (P2).
- A acurácia da LLM foi medida na Entrega 3 com modelos gratuitos (`gpt-oss-120b` e `gpt-oss-20b`), não com o Claude da tabela de custo. Por isso toda LLM da proposta continua começando com humano aprovando.
- O protótipo roda localmente, com estado em arquivo. A avaliação humana dos rascunhos (M5) ficou fora do escopo e será medida em produção ([PROTOTIPO.md](solution/app/PROTOTIPO.md), seção 4).

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

cd ../automacao
python automacao.py                   # ≈ 1 min — proposta de automação; exit 0 = verificações OK
python aprendizado.py                 # ≈ 5 min — ciclo de aprendizado, monitor, economias
python harness_automacao.py           # ≈ 4 min — 13 testes contra a proposta

# Protótipo (Entrega 3)
cd ../app
pip install -r requirements.txt
streamlit run app.py                  # http://localhost:8501 — na 1ª vez treina o modelo (≈ 1 min)
python -m pytest -q                   # 139 testes, ≈ 40 s, sem rede
# Opcional: copie .env.exemplo para .env com GROQ_API_KEY e GEMINI_API_KEY; sem chave, os rascunhos vêm da base de conhecimento
```

---

## Process Log — Como usei IA

> Detalhado em [`process-log/`](process-log/).

### Ferramentas usadas

| Ferramenta | Para que usou |
|---|---|
| Claude Code (desktop, Claude Opus) | Exploração dos dados, análise estatística, harness, scripts da solução, protótipo (spec → plano → TDD) e redação dos documentos |
| Groq (`gpt-oss-120b`) e Gemini (`gemini-3.6-flash`), free tier | LLM **dentro do protótipo**: rascunho e dossiê, com fallback entre os dois, e a medição M1–M4 |

### Workflow

1. Contexto do desafio + duas regras minhas para a IA: **"sempre 3 opções por etapa, sem enviesar"** e **"se faltar dado, a resposta é: o fluxo trava porque o dado não é registrado corretamente, e é preciso achar o erro e trazer a solução"**.
2. Diagnóstico inicial (Entrega 1) → revisão crítica.
3. Pedi um harness para verificar se as decisões estavam certas, a aderência ao desafio e a pergunta **"é problema humano ou de ferramenta?"**.
4. O harness corrigiu 6 erros do próprio diagnóstico (ver process log).

### Onde a IA errou e como corrigi

Ver [`process-log/01-diagnostico.md`](process-log/01-diagnostico.md): teste de poder inflado, faixa de desperdício exagerada, número com denominador errado, bug no teste de desalinhamento, hipótese fraca apresentada como conclusão e duas fontes para o mesmo número.

Ver [`process-log/02-proposta-automacao.md`](process-log/02-proposta-automacao.md): rota errada para tickets genéricos, verificação com corte arbitrário, título de gráfico exagerado, soma tratada como união e exemplo com prioridade que a regra não sustentava.

Ver [`process-log/03-harness-economia-aprendizado.md`](process-log/03-harness-economia-aprendizado.md): 4 decisões derrubadas pelo harness, auditoria cega, risco de permissão lido ao contrário e dois erros do próprio harness (aprovação por coincidência e regex anulada por caractere de controle).

Ver [`process-log/04-prototipo.md`](process-log/04-prototipo.md): 11 erros da Fase 3, entre eles 3 guardrails errados achados na revisão do plano (antes do código), um gatilho que tirava 728 tickets da automação para salvar 3, e a medição presa em 53 respostas 429 sem acionar o fallback, diagnosticada pelos logs do próprio protótipo.

### O que eu adicionei que a IA sozinha não faria

- Recusar entregar "só o erro": exigir a solução com dono e verificação.
- A pergunta **humano × ferramenta**, que mudou o destinatário do plano (TI/processo, não o time de agentes).
- O formato de decisão com **3 opções e justificativa**, para não enviesar.
- Exigir um harness que tentasse derrubar as conclusões antes de aceitá-las.

---

## Evidências

- [x] Git history (commits desta branch)
- [x] Narrativa escrita: [`process-log/01-diagnostico.md`](process-log/01-diagnostico.md), [`process-log/02-proposta-automacao.md`](process-log/02-proposta-automacao.md), [`process-log/03-harness-economia-aprendizado.md`](process-log/03-harness-economia-aprendizado.md) e [`process-log/04-prototipo.md`](process-log/04-prototipo.md)
- [x] Screenshots do protótipo: [`process-log/screenshots/`](process-log/screenshots/)
- [x] Registro de decisões (DIAGNOSTICO.md) e de erros corrigidos (HARNESS.md)
- [ ] Chat export / screenshots das sessões _(adicionar em `process-log/chat-exports/`)_

---

_Submissão enviada em: 23/09/2026_
