# Process Log

Registro de **como** cheguei na solução: o que eu decidi, o que a IA fez, onde ela errou e o que mudou por causa disso.

## Ferramentas

| Ferramenta | Papel |
|---|---|
| **ChatGPT** | Parceiro de brainstorm: transformei minha visão de produto em um PRD com regras de negócio ([prompt](chat-exports/01-chatgpt-prompt-inicial.md), [PRD](../docs/PRD.md)) |
| **Claude Code (Opus)** | Par de programação e análise: auditoria de dados, estatística, ML, app Next.js, evals, debugging e documentação |
| **Groq / Llama 3.x** (opcional) | Tier LLM da cascata, desligado por padrão (custo zero sem chave) |

---

## Linha do tempo

### 1. Entender o problema antes de promptar
- Li o README do challenge e escolhi o **002**, porque mistura diagnóstico, processo e build.
- Escrevi **minha** visão de produto antes de pedir qualquer coisa à IA: Zendesk + Botpress, LLM barata, CSAT, dashboards por período, KB que aprende com perguntas não respondidas, HITL upstream/downstream, guardrails, evals e MCP. Ver o [prompt original](chat-exports/01-chatgpt-prompt-inicial.md).
- Iterei com o ChatGPT até ele gerar um PRD com regras de negócio, li o PRD inteiro e o usei como norte, não como verdade.

### 2. Decisões de arquitetura (minhas, contra o PRD quando fez sentido)

| PRD sugeria | Decidi | Por quê |
|---|---|---|
| Python/FastAPI + Streamlit | **Next.js + TypeScript** na Vercel | Quero algo *produtizável*, com login/cadastro e deploy público. O Python fica só para análise offline e treino |
| FAISS/Chroma + embeddings | **TF-IDF × cobertura** (KB) e **TF-IDF + LogReg** (classificador) | Custo zero, ~1 ms, explicável, sem infraestrutura; dá para trocar depois mantendo a interface |
| LLM em todas as etapas | **Cascata**: tier local → LLM barata → LLM forte → humano | A maior parte dos tickets não precisa de LLM; o PRD já pedia model routing |
| Banco qualquer | **SQLite** (libsql), compatível com **Turso** | Requisito meu: hospedar na Vercel com cadastro |

### 3. Auditar os dados antes de analisar (o achado mais importante)
Pedi ao Claude Code para baixar os datasets reais do Kaggle e **perfilar antes de responder às perguntas do Diretor**. Vieram estes sinais vermelhos:
- **8.469** tickets, e não ~30k como diz o brief.
- `First Response Time` e `Time to Resolution` são **carimbos de data**, todos numa janela de 27h, sem timestamp de criação.
- **49,3%** dos fechados "resolvidos antes da primeira resposta".
- CSAT, canal, tipo e prioridade com distribuição **uniforme**; resoluções em **lorem ipsum** ("Offer investment fish.").

Então testei formalmente:
- Tipo × assunto: Cramér's V = 0,03.
- Texto → tipo: 20,3% de acurácia contra 20% do acaso.
- Drivers de CSAT: o Random Forest fica **abaixo do baseline**.

**Decisão:** em vez de forçar uma narrativa ("Chat tem o melhor CSAT!"), o diagnóstico separa o que os dados sustentam (backlog sem resposta, prioridade inflacionada, mix de assuntos) do que não sustentam (drivers de tempo e CSAT). A recomendação vira instrumentar a operação. É aqui que o baseline de "colar o brief na IA" falharia.

### 4. Diagnóstico estatístico
`solution/analysis/diagnostico.py`: Kruskal-Wallis por dimensão, Mann-Whitney (Critical vs Low), teste de permutação para a "pior combinação" (p=0,13, ou seja, não significativa), Spearman e RF com CV 5-fold.

**Julgamento humano:** a Opportunity Matrix (complexidade/risco/modo por assunto) é minha, não derivada do dataset; o racional está na tabela do app.

### 5. Classificador (Dataset 2)
`solution/analysis/train_classifier.py`, com split 70/15/15 estratificado:

| Modelo | Val acc | Val macro-F1 |
|---|---|---|
| TF-IDF + LogReg | 86,05% | 86,23% |
| TF-IDF + Complement NB | 81,73% | 81,23% |
| TF-IDF + LinearSVC (calibrado) | 86,62% | 86,88% |
| TF-IDF unigramas + LogReg | 85,42% | 85,88% |

- **Escolhi a LogReg**, mesmo o SVM sendo 0,6 p.p. melhor: ela tem probabilidades nativas (o gate depende delas), é trivial de portar e explicável.
- **Calibração do gate no conjunto de validação:** ≥0,85 → 97,3% de acurácia em 60% dos tickets; <0,60 → 56% (vai para humano). Os thresholds do PRD foram **confirmados com dados**.
- **Teste:** 86,64% de acurácia e macro-F1 de 86,56%. "Administrative rights" tem **70% de recall**, um problema que a acurácia sozinha escondia.
- **Exportei para JSON** e reimplementei a inferência em TS. Paridade: **480/480 predições idênticas** ao sklearn.

### 6. Pipeline e calibração: cinco iterações guiadas por resultado

| # | Sintoma observado | Causa | Correção |
|---|---|---|---|
| 1 | Perguntas sem artigo (ex.: "endereço de cobrança na nota emitida") recebiam resposta AUTOMÁTICA do artigo "Formas de pagamento" (score 0,36–0,59) | Busca lexical premia termos comuns ("cobrança", "nota") | Score = similaridade × √cobertura dos termos raros (IDF). Sem resposta: ≤0,14; com resposta: ≥0,45 |
| 2 | 100% dos tickets do D1 iam para HUMANO | Texto sintético sem sinal; descrições longas derrubam a cobertura | Assunto do formulário como sinal estruturado com **peso 0,8** (nunca gera AUTO sozinho); tipo declarado (Refund/Cancellation) como sinal de risco |
| 3 | 74–90% dos tickets "Frustrated" | Descrever problema ≠ estar irritado; e **bug**: "sue" casava dentro de "is**sue**" | Peso limitado para termos de problema; matching com word boundary (Unicode) |
| 4 | Variações da mesma pergunta viravam gaps separados | Comparação só com a primeira pergunta do cluster; threshold 0,5 | Single-linkage com todas as variações e threshold 0,4 → 7 variações num único gap |
| 5 | "Funcionou, obrigado!" virava Knowledge Gap | Mensagem de agradecimento passava pelo pipeline como pergunta | Detecção de confirmação → resolve e pede CSAT; follow-ups não criam gap |

**Resultado:** o pipeline aplicado ao D1 manda **55,7%** para humano, e a Opportunity Matrix independente dava **54,8%**. Os dois métodos convergem.

### 7. Evals — onde o sistema provou que precisava deles
Escrevi um golden set comportamental (58 casos: segurança, escalonamento, RAG, gaps, prioridade) e o runner `npm run eval`, que também reexecuta 480 tickets de teste do D2.

```text
Eval v2 (antes)                         Eval v3 (depois)
Comportamental     56/58                58/58
Escalation recall  97,1%                100%
Automação insegura 1  ← "Quero meu dinheiro de volta" foi AUTO   0
Prioridade ±1      91,7%                100%
```

- **Erro 1:** o regex de risco de reembolso só conhecia "money back" (inglês).
- **Erro 2:** ameaça de Procon/advogado saía com prioridade Medium.
- Corrigi os dois. O histórico (v2 → v3) aparece na página **/evals**, e `npm run eval` falha (exit 1) se houver qualquer automação insegura.
- **Limitação assumida:** escrevi o golden set conhecendo as regras, então ele é otimista. O próximo passo é um set rotulado por agentes.

### 8. Construção e teste
- Telas: login/cadastro, dashboard, diagnóstico (com calculadora de ROI), Smart Inbox, portal do cliente, Knowledge Base, evals, "como funciona" e servidor MCP (testado via JSON-RPC: 7 tools listadas e `triage_ticket` retornando decisão).
- Paleta dos gráficos derivada das cores G4 e **validada** (contraste, separação para daltonismo) antes de usar.
- **Teste ponta a ponta:** abri no portal uma pergunta não coberta → HUMANO (30%) → agrupada no gap existente (7 ocorrências) → publiquei o artigo → a mesma pergunta e uma paráfrase passaram a 95% de confiança.
- Mais dois bugs encontrados no navegador e corrigidos: o FRT mediano mostrava 7.956 min (o seed não deslocava `first_response_at`) e o tokenizador transformava "address" em "addres".

### 9. Iterações de produto a partir do meu uso
- **Motivos de escalonamento duplicados** no dashboard ("pedido de reembolso" e "reembolso/chargeback" vinham de detectores diferentes). Criei uma taxonomia canônica: um ticket conta uma vez por motivo, e risco médio que escalou por baixa confiança aparece como tal.
- **Confiança da IA explícita e ajustável:** a fórmula do score, os thresholds e os pesos saíram do código e foram para uma página de governança. Ela simula o impacto antes de aplicar e roda o golden set; uma configuração que gere automação insegura é sinalizada.
- **Diagnóstico mais enxuto:** o primeiro desenho tinha informação demais numa tela só. Passou para 4 números de manchete + abas com uma mensagem por aba.
- **Text-to-SQL** para o gestor tirar insights rápidos, com guardrail de somente leitura.
- **Portal dentro do console** (simulador) em vez de um link solto no login.

---

## Onde a IA ajudou
- Velocidade: perfilamento dos dados, testes estatísticos, comparação de modelos, todo o app em TypeScript.
- Debugging rápido quando os números "pareciam errados" (ex.: 90% frustrados → achar o bug "sue"/"issue").

## Onde a IA errou (ou teria errado sem supervisão)
- Thresholds e regex escritos "de cabeça" deixaram passar uma automação insegura, só pega pelo eval.
- Busca lexical confiante em respostas erradas (iteração 1).
- A leitura ingênua do dataset (médias de CSAT por canal, feature importance in-sample) teria virado "insight".

## Onde houve julgamento humano
- **O que nunca automatizar** e a regra "cobrança = no máximo sugestão".
- **Rejeitar** conclusões estatisticamente vazias, mesmo que boas para um slide.
- **Trocar a stack do PRD** (Python/Streamlit → TS/Vercel) para entregar produto, não protótipo descartável.
- Exigir **paridade** TS × Python e **calibração** de thresholds antes de confiar no modelo.

## Evidências
- Prompt inicial: [`chat-exports/01-chatgpt-prompt-inicial.md`](chat-exports/01-chatgpt-prompt-inicial.md)
- PRD gerado com IA: [`../docs/PRD.md`](../docs/PRD.md)
- Screenshots: [`screenshots/`](screenshots/)
- Histórico de evals: página **/evals** do app + `solution/app/data/eval_history_seed.json`
- Git history da branch de submissão
