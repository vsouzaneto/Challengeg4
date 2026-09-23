# Harness: eu estava certo?

> Código: [`harness.py`](harness.py). Resultados brutos: [`outputs/harness_resultados.json`](outputs/harness_resultados.json) e [`outputs/harness_forense.csv`](outputs/harness_forense.csv).
> Para rodar: `python harness.py --data ../data/support_tickets.csv --data2 ../data/it_tickets.csv` (≈ 30 s).

## A ideia

Um diagnóstico que diz "o dado não tem sinal" pode estar certo, ou pode estar usando **testes fracos demais para ver o sinal**. Um diagnóstico que escolhe entre 3 opções pode ter escolhido pelo motivo errado. O harness existe para **tentar derrubar** cada conclusão.

Todos os testes seguem o mesmo roteiro:

1. **Controle positivo.** Planto um efeito conhecido e confirmo que o método o encontra.
2. **Tentativa de contradição.** Procuro a evidência que provaria que eu estava errado.
3. **Critério definido antes de rodar.** O teste passa ou falha por uma regra escrita no código, não pela minha interpretação depois de ver o resultado.

## Resultado: 10/10

| # | Pergunta | Como tentei derrubar | Resultado | Decisão que sustenta |
|---|---|---|---|---|
| H1 | Os números do documento batem com o código? | Recalculei 15 números citados e procurei cada um no texto | 15/15 idênticos | Todas |
| H2 | "Não há gargalo por prioridade" é real ou teste fraco? | Plantei um efeito "Critical X h mais rápido" em dados embaralhados, 200× para cada tamanho de efeito | Diferenças **≥ 1,5 h** seriam detectadas em ≥ 80% das vezes | 1.1 (tempo inválido) |
| H3 | "Nada explica o CSAT" é real ou teste fraco? | Plantei "+X pontos no Chat" e um CSAT dependente do canal no Random Forest | Efeitos **≥ 0,24 ponto** seriam detectados; o Random Forest sai de 20% para **62%** quando há sinal | 2 (declarar nulo) |
| H4 | O "pior gargalo" (Chat × Low × Technical) é estável? | 1.000 reamostragens (bootstrap) + comparação do ranking entre duas metades do dado | **51 combinações** diferentes já foram "a pior"; a mais frequente em só 23%; metades concordam com ρ = **0,01** | 1.1 (rejeitar o ranking) |
| H5 | A triagem é mesmo indistinguível de um sorteio? | 300 permutações do tipo + controle positivo com 80% de tipos corretos | Real: 65,4%, dentro da faixa do sorteio (65,0% a 66,5%). Com 80% corretos, a métrica cai para 13,1%: **a régua funciona** | 1.4 (IA na triagem) |
| H6 | "Retriagem é o maior desperdício" depende das premissas? | Monte Carlo com 20.000 combinações de premissas (distribuição triangular) | Retriagem é o maior item em **100%** dos cenários. Total P10–P90: **3.158 a 4.686 h, R$ 109 mil a 194 mil** | 3 (onde atacar) |
| H7 | A incoerência depende do meu mapa de coerência? | 300 mapas perturbados (adicionei e removi tipos aceitos) | O **nível** varia de 57% a 73%, mas fica sempre a ≤ 1,5 p.p. do sorteio. A conclusão não depende do mapa | 1.4 |
| H8 | O problema é humano ou de ferramenta? | 10 assinaturas forenses (tabela abaixo) | **0 assinaturas humanas**; falhas de sistema; o workflow de status funciona | Causa raiz |
| H9 | A triagem por IA é viável com dado real? | Dataset 2: treino 28.701, validação 9.568, teste 9.568 tickets. Limiar escolhido na **validação**, medido no **teste** | IA decide sozinha **73,2%** com **95,1%** de acerto; abaixo do limiar acertaria 60,2%, então vai para humano | 1.4, P2 |
| H10 | O Quality Gate funciona? | Controle positivo (export sintético limpo) + 12 mutações, uma por defeito | Dado limpo: **12/12 regras OK**. Defeitos: **12/12 pegos pela regra certa** | P9 (governança) |

### H8: humano ou ferramenta, em detalhe

| Sinal | Se fosse humano… | Observado | Atribuição |
|---|---|---|---|
| Segundos nos horários | Digitado → :00 | 1,8% com :00 (acaso 1,7%); uniforme (p = 0,97) | 🔧 Sistema |
| Resolução × 1ª resposta | Eventos independentes → segundos diferentes | **100%** dos pares com os mesmos segundos → campo **calculado** | 🔧 Sistema |
| Troca AM/PM | Pico em ±12 h | 3,9% (acaso 4,2%) | ✖ Não é digitação |
| Hora do dia | Vale de madrugada | Madrugada ÷ horário comercial = 1,04 | 🔧 Sistema (fraco) |
| Placeholders | Agente não escreve `{…}` | 100% | 🔧 Template |
| Texto da resolução | Vocabulário de suporte; lixo repetido | 100% únicos; 0,8% vocabulário de suporte (18,7% nas descrições) | 🔧 Texto gerado |
| E-mail | Mesmo e-mail = mesma pessoa | 139 e-mails, todos com nomes diferentes | 🔧 Modelagem |
| Triagem por canal | Equipes erram diferente, acima do acaso | 17,0% a 19,8% (p = 0,70); acaso 18,3% | ✖ Não é julgamento |
| Colunas desalinhadas | Pico em algum deslocamento | Melhor: 20,8% (acaso 18,3%), sem pico | ✖ Descartado |
| Máquina de estados | Status incoerentes | 100% coerente | ✅ Workflow ok |

---

## O harness me pegou errando (e o que mudei)

Um harness que só confirma o que eu já pensava não serve para nada. Estas foram as correções que ele forçou:

| # | Erro | Como apareceu | Correção |
|---|---|---|---|
| 1 | **Teste de poder inflado.** A primeira versão do H2/H3 dizia que efeitos de 0,5 h e 0,08 ponto seriam detectados | Desconfiei do 10/10 na primeira rodada. Eu plantava o efeito **em cima** da vantagem que Critical e Chat já tinham por acaso | Embaralhar antes de plantar. O efeito mínimo detectável honesto é de **1,5 h** e **0,24 ponto**, 3× maior. A conclusão se mantém, com o número certo |
| 2 | **Faixa de desperdício enganosa.** O diagnóstico dizia "1.700 a 7.100 h" | O Monte Carlo (H6) mostrou que essa faixa exige **todas** as premissas no extremo ao mesmo tempo | O resumo passou a usar a faixa **P10–P90 de 3.200 a 4.700 h**, mantendo o baixo–alto como pior caso |
| 3 | **Número errado no texto.** "1,2% dos horários com :00" | O H8 recalculou: o denominador antigo incluía as linhas vazias | Corrigido para 1,8% (acaso 1,7%) |
| 4 | **Bug no teste de desalinhamento.** Listas vazias contavam como erro e davam 9,8% (parecia **abaixo** do acaso) | Um número abaixo do acaso não faz sentido para esse teste | Filtro corrigido: 20,8%, sem pico. A conclusão (não é join deslocado) se mantém |
| 5 | **Hipótese fraca virou evidência.** O diagnóstico dizia "hipótese compatível: fila por ordem de chegada, sem critério" | O H8 mostrou que a resolução é *calculada* e a triagem é *acaso exato*: dá para afirmar mais | O texto passou a citar a evidência forense em vez da hipótese |
| 6 | **Duas fontes para o mesmo número.** O H9 e o `triagem_ia.py` usavam divisões diferentes (86,7% contra 85,8%) | Divergência entre documentos | O H9 passou a chamar o mesmo código da solução: uma fonte só |

## O que o harness **não** consegue verificar

- **Premissas de minutos e custo.** O Monte Carlo mede a *sensibilidade*, não o valor verdadeiro. Só o dado real da operação resolve isso.
- **Precisão dos sinais de texto** (regex de recontato, urgência e severidade). Não existe rótulo verdadeiro para medir.
- **Acurácia de LLM sem treino na taxonomia desta operação.** Não foi medida; é o critério de aprovação da P2 (≥ 90% em 500 tickets rotulados por humanos).
- **Capacidade (P4).** Sem horário de abertura e sem tempo médio de atendimento, a pergunta "faltam pessoas?" não tem resposta.

---

## Aderência ao desafio: a entrega responde o que foi pedido?

### Requisitos da Entrega 1 (diagnóstico)

| Pedido no README do desafio | Status | Onde |
|---|---|---|
| Onde o fluxo trava: gargalos por **canal, prioridade, tipo** | ✅ Respondido: não há diferença (com teste de poder); o gargalo é a triagem e a 1ª resposta | DIAGNOSTICO 1.2–1.3 · H2 |
| **Quais combinações** geram os piores tempos | ✅ Respondido com a lista **e** a prova de que o ranking é ruído | DIAGNOSTICO 1.1 · H4 |
| Quais variáveis influenciam o **CSAT** | ✅ Nenhuma, com efeito mínimo detectável declarado; coleta enviesada identificada | DIAGNOSTICO 2 · H3 |
| Desperdício em **horas** | ✅ 3.400 h (P10–P90: 3.200 a 4.700) | DIAGNOSTICO 3 · H6 |
| Estimativa de **custo** | ✅ R$ 119 mil (P10–P90: R$ 109 mil a 194 mil) | DIAGNOSTICO 3 · H6 |
| **Maior desperdício recuperável** | ✅ Retriagem (48%), recuperação medida de 1.345 h/ano | DIAGNOSTICO 3 · H9 |

### Critérios de qualidade do desafio

| Critério | Status | Evidência |
|---|---|---|
| Usou **ambos** os datasets? | ✅ | Dataset 1 no diagnóstico; Dataset 2 prova a solução (H9) |
| Números concretos, não genéricos? | ✅ | Cada número tem teste, arquivo e código |
| Automação **realista** (100% é red flag) | ✅ | A IA decide 73%, humano 27%; backlog 49% para humano |
| Sabe onde IA ajuda e onde o humano é insubstituível? | ✅ | Limiar de confiança; "Administrative rights" fica com humano; decisão de contratar fica com gente |
| Protótipo funciona com dados reais? | ✅ | Quality Gate e triagem rodam nos 8.469 e nos 47.837 tickets reais, não em exemplos escolhidos |

### O risco que o avaliador pode ver, e a resposta

> *"O candidato só disse que o dado está ruim."*

A resposta está na [causa raiz](CAUSA_RAIZ_E_SOLUCAO.md): cada falha tem **causa** (humano, ferramenta ou processo, com evidência), **3 opções**, **a escolhida**, **um dono** e **uma regra que verifica**. Duas partes da solução **já rodam**: o Quality Gate e a triagem com a fila do backlog repriorizada. O ROI da principal foi **medido**, não suposto.

### O que ainda falta no desafio completo (fora desta entrega)

| Item | Obrigatório? | Situação |
|---|---|---|
| Entrega 2: proposta de automação (o que automatizar e o que não, fluxo) | Sim | **Adiantado** (P2, P3 e "o que não automatizar" na causa raiz); falta o fluxo ponta a ponta |
| Entrega 3: protótipo funcional | Diferencial | **Base pronta** (`triagem_ia.py`); falta a interface "rodando" para o Diretor |
| Entrega 4: process log | **Sim, sem ele a submissão é desclassificada** | **Não iniciado**. As tabelas "o harness me pegou errando" e "registro de decisões" já servem de matéria-prima |
| README da submissão no template | Sim | Não iniciado |

### Além do que foi pedido

1. **Harness de falsificação**, com controle positivo e mutação: o desafio não pede verificação, e é o que separa análise de opinião.
2. **Forense humano × ferramenta**: tira a culpa do agente com evidência e aponta o conserto certo.
3. **Quality Gate**: um contrato de dados executável que roda no ETL amanhã.
4. **ROI medido**, não suposto, para a principal alavanca.
5. **Fila do backlog repriorizada**: um contorno operacional para a semana 1.
