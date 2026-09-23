# Process log — Entrega 3: protótipo funcional

**Ferramenta:** Claude Code (app desktop, modelo Claude Opus), em worktree git próprio, alinhado à branch `submission/rafael-bateli`. Skills usadas: *brainstorming* → *writing-plans* → *executing-plans* (TDD).
**Iterações:** 5 decisões com 3 opções cada → spec (1 revisão) → plano de 11 tarefas (6 erros achados na revisão, antes de escrever código) → 11 tarefas com teste antes do código → 4 correções depois do teste de fumaça com as APIs reais → medição da LLM em 3 execuções (1ª presa em 429; 2ª até a cota diária do `gpt-oss-120b` acabar; 3ª com o `gpt-oss-20b`, interrompida em 75/80 do M4). O checkpoint guardou tudo: o resultado final foi consolidado dele, sem refazer chamadas. Por fim, corte de escopo para o que o desafio pede.

---

## 1. O que pedi

1. Construir o protótipo que o desafio pede, **sem entregar nada a menos** e entregando a mais onde fizer sentido.
2. **Antes de escolher ferramenta, me perguntar**, sempre com 3 opções e os prós e contras de cada uma para esta situação.
3. Pensar mais na **proposta de valor** que no código.
4. Manter os critérios de qualidade: os dois datasets, números concretos, automação realista, onde a IA para e **dados reais, não 3 exemplos escolhidos a dedo**.
5. Ênfase explícita em **guardrails, fallbacks e logs de erro**.

## 2. Como decompus o problema antes de construir

A primeira pergunta não foi "qual ferramenta", foi **"o que o protótipo precisa provar, e para quem"**:

| Quem | Pergunta | Resposta no protótipo |
|---|---|---|
| Diretor | "Funciona? Quanto devolve?" | Replay dos 8.469 tickets + ROI da Entrega 2, sem fórmula nova |
| Agente | "O que muda na minha manhã?" | A fila já triada: não abre o que não descreve nada, não refaz triagem, trabalha pelo risco real |
| Supervisor | "Como sei que não está errando?" | Auditoria sorteada, devoluções, medição da LLM, saúde do sistema |

Daí saiu o conceito: **a fila de amanhã de manhã**, em vez de 4 demos soltas para os 4 exemplos do desafio.

## 3. Decisões (3 opções cada)

| Decisão | Opções apresentadas | Escolha | Por quê |
|---|---|---|---|
| Conceito | Mesa do agente + painel · motor + avaliação em CLI · só painel do Diretor | **Mesa + painel** | Cobre os 4 exemplos do desafio e mostra o agente e o ROI |
| Interface | FastAPI + HTML · Streamlit · link publicado + motor | **Streamlit** (minha escolha; a IA recomendava FastAPI) | Reusa o Python das Entregas 1–2 num processo só; os contras foram mitigados com `st.fragment`, cache e `AppTest` |
| LLM | Híbrido · Claude pago · só template | **Pedi Groq e Gemini gratuitos**, e depois **os dois com fallback quando a cota de um acabar** | Custo zero para o protótipo. A IA trouxe o contraponto que entrou na spec: o free tier do Gemini treina com o conteúdo, aceitável com dado público e vetado com ticket real (LGPD) |
| Taxonomia | Duas filas + painel cruzado · só D1 · modelo do D2 aplicado ao D1 | **Duas filas** | Aplicar o modelo do D2 ao D1 seria fora de domínio: "confiante e errado" (harness A6) |
| Acesso | Local + Hugging Face · local + Streamlit Cloud · só local | **"Siga o challenge, não fuja dele"** → só local | O guia de submissão pede código-fonte + instruções de setup, dentro da pasta |

## 4. Onde a IA errou e como foi corrigido

| # | Erro | Como percebi | Correção |
|---|---|---|---|
| 1 | Guardrail com **"no" na lista de negação**: "cancel with **no** charge" passaria como frase negada | Revisão do plano contra os casos de teste, antes do código | "no" saiu da lista; o caso virou teste |
| 2 | **Regex do reembolso em português** não casava "Aprovamos o seu reembolso" | Mesma revisão | Regex corrigida; o caso virou teste |
| 3 | **Artigo de recontato escrito para o agente**, mas usado como rascunho para o cliente | Mesma revisão | Reescrito para o cliente |
| 4 | **Duas contagens de testes erradas** no plano e uma categoria de log (`rede`) fora da lista da spec | Autorrevisão do plano | Corrigidas |
| 5 | **Pulei o passo "ver o teste falhar"** na tarefa da cadeia de LLM (código e teste gravados juntos) | Percebi ao registrar o resultado | Os testes passaram; o desvio fica registrado aqui. Nas tarefas seguintes voltei à ordem |
| 6 | **Gatilho de admin por palavra** (`permission\|administrator`): a spec previa, a IA implementou | O painel mostrou que 14% do D2 saía da automação. Medido: a regex tirava 728 tickets para salvar 3 | **Removido por decisão minha**, coerente com a Entrega 2 (B4: proteger a ação, não o rótulo). Roteamento automático: 62,5% → 70,0%, acerto mantido em 95,1% |
| 7 | **Modelo do Gemini da spec (`gemini-2.5-flash`) não existe mais** para contas novas | Teste de fumaça com a API real: HTTP 404 | Padrão trocado para `gemini-3.6-flash`, configurável |
| 8 | **Nome da chave**: o código só lia `GEMINI_API_KEY`; a chave foi criada como `GOOGLE_API_KEY` | Ao configurar o `.env` | Os dois nomes são aceitos, com teste |
| 9 | **Medição presa**: 15 min, 53 respostas 429 do Groq, nunca acionou o Gemini. Um 429 com espera curta era repetido sem limite, a pausa de 10 s ignorava o limite de 8K tokens/min, e não havia checkpoint | Log de erros (a ferramenta que o próprio protótipo criou) + sondagem de 1 lote: 2.252 tokens por lote | Ritmo pelo orçamento de tokens, troca de provedor na 3ª falha seguida, espera em 503 e checkpoint por lote. Teste que reproduz o laço infinito. **Critérios M1–M4 inalterados** (conferido por diff contra o commit de pré-registro) |
| 10 | **Diagnóstico errado de um 429**: tratei como pico de limite por minuto porque uma chamada pequena passou logo depois | Uma sondagem com um lote do tamanho real devolveu o motivo: **cota diária** do `gpt-oss-120b` (199.819 de 200.000 tokens), com o M1 em 340/500 | M1 fechado com n = 340, o que já decide (IC95% da diferença de −52 a −41 p.p.). M2–M4 seguem com o `gpt-oss-20b`, que tem cota própria (**decisão minha**, entre 3 opções), com cada número reportado por modelo. O M3 foi ajustado para comparar o mesmo modelo, e o `retry-after` passou a ir para o log |
| 11 | **Tela com número antigo**: o painel mostrava "14,0% com gatilho sensível" depois da correção 6 | Captura de tela para este log | O servidor guardava o resultado antigo em cache; reiniciado. Valor atual: 4,4% |
| 12 | **Captura de tela vazia**: o Chrome headless fotografava antes de o Streamlit desenhar | Conferência visual das imagens | Captura via DevTools, esperando o texto final aparecer na tela |

## 5. O que eu adicionei que a IA sozinha não faria

- **Groq + Gemini com fallback quando a cota acabar.** A IA ofereceu um provedor padrão; pedi os dois encadeados. Foi isso que expôs o erro 9: sem fallback de verdade, a medição ficaria presa.
- **"Siga o challenge, não fuja dele"**: cortou a publicação em nuvem, que parecia um diferencial, mas saía do formato pedido.
- **Ênfase em guardrails, fallbacks e logs de erro**: virou uma seção inteira da spec, 3 critérios de aceite (P8–P10) e a tela de saúde do sistema. Os logs foram o que diagnosticou o erro 9.
- **Remover o gatilho de admin por palavra** (erro 6): a IA seguiu a spec; eu decidi pela evidência.
- **Cortar escopo**: com o protótipo pronto, perguntei o que ainda faltava segundo o README do desafio e mandei cortar o que ele não pede. Saíram da submissão a especificação e os dois planos (4.011 linhas, dois terços de todo o texto; ficam no histórico do git) e o M5 (avaliação humana de 20 rascunhos), que vira limitação declarada.

## 6. Decisões que tomei sobre o que a IA propôs

- **Desconfiar do resultado bom demais para a tese**: antes de aceitar "LLM 39% × supervisionado 86%", olhei a matriz de confusão para descartar defeito de interpretação ou de nome de classe. Só 2 de 340 respostas não foram interpretadas. Os erros são de significado: no D2, "expenses for team report" está rotulado como *Hardware*, e a LLM zero-shot só conhece o nome da classe.
- **Ler o caso que derrubou o critério antes de aceitar a conclusão**: o M4 caiu pela regra automática com 1 rascunho. Lido por inteiro, o rascunho estava certo: a LLM recusou ensinar o reset e avisou que ele apaga dados. O erro era do guardrail (falso positivo). Publiquei as duas leituras e não ajustei o critério.
- **Critério antes do número**: o script de medição foi commitado antes da 1ª execução. Quando precisei corrigir a mecânica, o diff contra aquele commit provou que os critérios não mudaram.
- **Publicar o que saiu, inclusive amostra ruim**: o sorteio da semente 7 deu 8 de 9 decisões automáticas certas, e está na tela como saiu.
- **Mudanças em relação à spec ficam registradas** (PROTOTIPO.md, seção 7), com a evidência, em vez de reescrever a spec como se tivesse sido sempre assim.
