# Plano da Fase 3: protótipo funcional

> Ponto de partida para a Entrega 3. Escrito ao fechar a Entrega 2 (commit `a44c91e`), para a próxima sessão começar sem redescobrir nada.
> O protótipo vai morar nesta pasta (`solution/app/`); o `.gitignore` da submissão já ignora `solution/app/*.pkl` (modelo treinado).

---

## 1. O que o desafio pede

> *"Protótipo funcional (diferencial). Construa algo que demonstre que sua proposta funciona."*
> Critério: **"funciona com dados reais, não com 3 exemplos cherry-picked?"**
> Diretor: *"me mostre que funciona — não quero só um PowerPoint. Quero ver algo rodando."*

Exemplos citados no README do desafio: classificador que devolve categoria + confiança; respostas sugeridas; roteador que categoriza e prioriza; dashboard de gargalos.

**O que o nosso protótipo deve provar:** o **fluxo da proposta** (Entrega 2, seção 3) rodando ponta a ponta, **em ticket único e no dataset inteiro**, com as mesmas regras e o mesmo modelo que o harness verificou.

```text
ticket → Quality Gate → duplicata → classificação + confiança → gatilhos de risco
       → prioridade + SLA → rota (1A · 1B · 2 · 3) + motivo → rascunho/dossiê (LLM)
       → registro de evento → painel (gargalos + métricas de aprendizado)
```

---

## 2. O que já existe e roda (reusar, não reescrever)

| Peça do fluxo | Onde está | Estado | O que falta para o protótipo |
|---|---|---|---|
| Quality Gate (12 regras) | [`diagnostico/solucao/quality_gate.py`](../diagnostico/solucao/quality_gate.py) → `avaliar(df, c)` | Função pronta | Versão por ticket (hoje avalia o export inteiro) |
| Classificador + limiar | [`automacao/modelo.py`](../automacao/modelo.py) → `dividir`, `treinar`, `prever`, `escolher_limiar` | Pronto, testado (A3–A5) | Salvar o modelo treinado (`.pkl`) para não treinar a cada execução |
| Problemas e sinais de risco (Dataset 1) | [`automacao/automacao.py`](../automacao/automacao.py) → `PROBLEMAS`, `SINAIS`, `RISCO`, `TECNICO` | Pronto | **Extrair a função `rota()`**, hoje aninhada dentro de `parte_a`, para um módulo reutilizável |
| Prioridade por sinais | [`diagnostico/solucao/triagem_ia.py`](../diagnostico/solucao/triagem_ia.py) → `SINAIS`, `URGENCIA`, `RECONTATO`, `sugerir()` (aninhada em `parte_c`) | Pronto | Extrair `sugerir()` e unificar os dois dicionários de sinais (hoje há dois) |
| Rotas 1A/1B | Regra descrita em [PROPOSTA 3.2](../automacao/PROPOSTA_AUTOMACAO.md) e medida no harness A10 | Só documentada | Implementar a divisão (1A = só hardware/reparo/recontato) |
| Duplicata | Similaridade em `automacao.py` (parte B) | Medida no Dataset 2 | Índice do histórico + regra de assinatura de alerta |
| Monitor de devoluções, auditoria | [`automacao/aprendizado.py`](../automacao/aprendizado.py) (B2, B5) | Simulados | Métricas no painel a partir do registro de eventos |
| Resultados já calculados | `automacao/outputs/*.json`, `rotas_dataset1.csv`, `diagnostico/outputs/fila_backlog_reprocessada.csv` | Prontos | Fonte do painel e **gabarito** para os testes do protótipo |

**Números que o protótipo precisa reproduzir** (senão há duas verdades): rotas 33,0% / 12,4% / 54,6% em 8.469 tickets; 73,2% decididos sozinhos com 95,1% de acerto no Dataset 2; 0 ticket de risco fora da rota 1.

---

## 3. Decisões em aberto (3 opções cada; para decidir no início da Fase 3)

### D1. Interface

| | Opção | A favor | Contra |
|---|---|---|---|
| A | **Streamlit** (app Python local) | Reusa o código Python direto; dá para colar um ticket e ver a rota; gráficos nativos | Precisa de `pip install` e rodar local; o avaliador tem que executar |
| B | **API (FastAPI) + página HTML** | Separa motor e tela; parece produto; testável por `curl` | Mais código; dois processos para subir |
| C | **Página publicada (artifact) com dados pré-calculados + CLI local** | O Diretor abre um link e vê; o CLI prova que roda nos dados reais | A página não reclassifica texto novo sem backend (só o CLI faz isso) |

### D2. LLM (rascunho e dossiê)

| | Opção | A favor | Contra |
|---|---|---|---|
| A | **API real (Claude)** | Fecha a maior lacuna das Entregas 1–2: **acurácia da LLM nunca medida**. Dá para rodar o critério P2 (≥ 90% em 500 tickets) | Precisa de chave de API; custo (baixo: ≈ R$ 270/ano na operação inteira) |
| B | **Modo simulado:** templates da base de conhecimento, sem LLM | Roda em qualquer máquina, sem chave | Não prova nada sobre a LLM |
| C | **Híbrido:** API se houver chave; senão, template, com aviso na tela | Funciona para qualquer avaliador | Dois caminhos de código para manter |

### D3. Taxonomia exibida

| | Opção | A favor | Contra |
|---|---|---|---|
| A | **Dataset 2 (8 classes de TI)** para a classificação + **Dataset 1** para rotas e risco | Cada dataset faz o que sabe: o D2 tem rótulo real, o D1 tem os sinais de risco | Duas taxonomias na mesma tela; precisa explicar |
| B | Só Dataset 1, com os 15 problemas-padrão como classes | Uma taxonomia só | Os rótulos do D1 são aleatórios (Entrega 1); a "classificação" seria por regra de template, sem prova em texto livre |
| C | Taxonomia nova unificada | Mais próxima da operação real | Sem rótulo; exigiria o gold set, que é trabalho de semanas |

### D4. Escopo

| | Opção | Entrega |
|---|---|---|
| A | Mínimo | Roteador (ticket → rota + motivo + prioridade) em CLI, rodando nos 8.469 tickets, com testes |
| B | Recomendado | A + tela para colar ticket + painel de gargalos e métricas |
| C | Completo | B + LLM real medida (D2-A) + registro de eventos + monitor de devoluções alimentado por simulação |

---

## 4. Critérios de aceite (viram testes do protótipo, no mesmo estilo do harness)

| # | Critério | Como verificar |
|---|---|---|
| P1 | Roda nos **dados reais inteiros**, não em exemplos | Processar os 8.469 tickets do D1 e os 9.568 de teste do D2 |
| P2 | **Uma fonte da verdade** | Rotas do protótipo = `rotas_dataset1.csv` (100% iguais); cobertura/acerto = `harness_automacao.json` |
| P3 | **Nenhum ticket de risco sai automatizado** | Todos os tickets com gatilho de risco → rota 1 |
| P4 | Latência | < 1 s por ticket sem LLM |
| P5 | Setup curto | `pip install` + 1 comando, em < 5 min, descrito no README |
| P6 | Explica cada decisão | Toda rota mostra o motivo (gatilho, confiança, sinal) |
| P7 | Casos adversários | Ticket de categoria nunca vista, ticket vazio, ticket com `{placeholder}`, ticket só com "Please assist": comportamento esperado documentado |

---

## 5. Pendências da submissão (fora do protótipo, mas bloqueiam o PR)

| Item | Onde | Situação |
|---|---|---|
| LinkedIn | `README.md`, seção "Sobre mim" | `_(preencher)_` |
| Chat exports / screenshots das sessões | `process-log/chat-exports/` ou `process-log/screenshots/` | Não adicionados (o guia lista como evidência) |
| Process log da Fase 3 | `process-log/04-prototipo.md` | A escrever durante a fase |
| Data de envio | final do `README.md` | `(em andamento)` |
| **Fork + PR** | CONTRIBUTING | O `origin` local aponta para o repositório da organização, não para um fork. Para o PR: criar o fork no GitHub, `git remote add fork <url-do-fork>`, `git push fork submission/rafael-bateli` e abrir o PR para `main` com o título `[Submission] Rafael Bateli — Challenge 002` |
| Só arquivos dentro de `submissions/rafael-bateli/` | CONTRIBUTING | ✅ Todos os commits até aqui respeitam |
| Arquivos ignorados | `.gitignore` da raiz ignora `submissions/` | Sempre usar `git add -f` com caminho explícito, **nunca** a pasta inteira (os CSVs de `solution/data/` e a `.venv/` não podem entrar) |

---

## 6. Como retomar

```bash
cd submissions/rafael-bateli/solution
pip install -r diagnostico/requirements.txt
# Datasets (Kaggle, CC0) em solution/data/ — não versionados:
#   support_tickets.csv  (Customer Support Ticket Dataset, suraj520)
#   it_tickets.csv       (IT Service Ticket Classification, adisongoh)
cd automacao && python automacao.py && python aprendizado.py && python harness_automacao.py   # conferir: 9 sustentados, 4 derrubados
```

**Regras de trabalho mantidas desde a Entrega 1:** 3 opções por decisão, com a escolhida justificada; todo número vem de script; harness que tenta derrubar antes de afirmar; para cada erro apontado, a melhor solução, testada; e não gravar código com barra invertida (`\b`, `\n`) via heredoc no shell: usar o editor ou `chr()` (erro que aconteceu duas vezes).
