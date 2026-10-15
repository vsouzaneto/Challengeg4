# Proposta de automação com IA no Suporte

> **Em uma frase:** automatizar a **triagem** (para qual fila vai cada ticket) com um modelo treinado no histórico da própria operação, que decide sozinho só quando a precisão medida é de ≥ 95%. A IA **nunca** executa ações sensíveis e **nunca** redige sobre saúde ou segurança. E o primeiro investimento é medir a operação direito, porque hoje os dados não permitem diagnosticar onde o tempo se perde.

Os números deste documento vêm de scripts reproduzíveis. As fontes estão indicadas em cada seção.

**Como os dois datasets se cruzam.** O Dataset 1 (operação de suporte a clientes) não sustenta diagnóstico de tempos, mas dá duas coisas: a **estrutura** da operação (status, canais, prioridades, tipos), que molda o fluxo abaixo, e um conjunto de **8.469 tickets de outro domínio**, usado para testar e calibrar as travas que impedem a IA de decidir sobre o que não conhece. O Dataset 2 (48 mil tickets reais de TI, com rótulos coerentes) é onde a triagem é treinada e medida. **A abordagem foi validada em dados reais; nesta operação, ela começa retreinando no histórico próprio e rodando em modo sombra** (seção 4).

**Da prova à operação do Diretor.** As 8 categorias de TI do Dataset 2 são só a prova. Na operação real, as categorias do modelo passam a ser as filas dele: Billing, Refund, Technical issue, Product inquiry, Cancellation. O mesmo motor (classificador, faixas, travas e política) é retreinado no histórico rotulado dessas filas, e o que muda é só o arquivo de treino. A condição é que o histórico tenha rótulos com qualidade. No Dataset 1, o "Ticket Type" é independente do texto, então a semana 0 do piloto mede isso antes de treinar.

---

## 1. O que automatizar

### 1.1 Triagem e roteamento: automatizar, em 3 faixas de confiança

| Faixa | O que acontece | % dos tickets | Acerto medido |
|---|---|---|---|
| **Automático** | A IA roteia; o agente vê a categoria já atribuída | **65,5%** | **96,4%** (IC95% de 95,9 a 96,8%) |
| **Sugestão** | A IA mostra as 2 categorias mais prováveis; o agente escolhe com 1 clique | 23,3% | A certa está entre as 2 em 91,0% |
| **Humano** | O agente classifica do zero | 11,2% | — (ver a decomposição abaixo) |

_Fonte: `03-prototipo/benchmark/outputs/motor_final.md` (9.568 tickets reais de teste, nunca vistos no treino)._

- **Limiar por categoria:** o limiar global (71% de confiança) é calibrado na validação para ≥ 95% de acerto. As categorias que ficariam abaixo disso ganham limiar próprio: Hardware (78%) e Miscellaneous (75%). Na faixa automática, as 8 categorias ficam entre 95,1% e 99,0% (estimativas pontuais; ver os intervalos em `motor_final.md`).
- **Travas de domínio:** se o ticket não se parece com o histórico, vai para humano, mesmo que o modelo "tenha certeza". Isso acontece quando a similaridade com o caso mais próximo fica abaixo de 0,20 ou quando o modelo reconhece menos de 50% das palavras. Testado com os 8.469 tickets do Dataset 1 (outro domínio): **sem as travas, 34% iriam para a faixa automática; com elas, 11%**.
- **De onde vêm os 11,2% da faixa humana:** 1,5% por confiança baixa e **9,7% pela trava de domínio**. A trava também barra tickets normais, porém atípicos, que o modelo acertaria em 79% dos casos. O limiar da trava (0,20) foi escolhido por inspeção, e a sensibilidade está declarada: 0,15 barra 1,7% dos normais e 36% dos de outro domínio; 0,25 barra 24% e 96%. É o preço, assumido, de não deixar a IA decidir sobre o que não conhece. Depois do piloto, o limiar pode ser recalibrado com dados da própria operação.
- **Hardware está no limite:** 95,1%, com intervalo de 94,0% a 96,2%. É a 1ª categoria a monitorar no piloto.

### 1.2 Por que um modelo treinado no histórico, e não um LLM, para classificar

| Abordagem (mesma amostra de 400 tickets) | Acerto |
|---|---|
| **Classificador simples (TF-IDF + regressão logística) treinado no histórico** | **85,0%** (86,0% no teste completo) |
| Embeddings genéricos + regressão logística | 78,2% |
| Voto dos 5 tickets mais parecidos do histórico (sem LLM) | 76,0% |
| LLM Gemini flash-lite, só com o nome das categorias | 44,0% |
| LLM Gemini flash-lite com 3 exemplos por categoria | 48,0% |
| **LLM Gemini flash-lite com os 5 tickets mais parecidos do histórico no prompt (RAG)** | **76,9%** |
| LLM mais forte (Gemini 3.8 flash) com 3 exemplos por categoria (n = 200, limite de cota) | 53,5% |

Diferença pareada entre o modelo simples e o melhor LLM (RAG): significativa (McNemar, p = 0,0003). O LLM só se aproxima quando **recebe o histórico da empresa**, e aí fica praticamente empatado com o simples voto dos 5 vizinhos (76,9% × 76,0%): o que acerta é o histórico, não o LLM.

_Fonte: `03-prototipo/benchmark/outputs/benchmark.md`._

**O ativo é o histórico rotulado da empresa, não o modelo.** As categorias seguem convenções internas: os termos que mais pesam em "Administrative rights" são *outlook, upgrade, install, windows* (instalação de software), e "Miscellaneous" concentra *change, approval, groups*. Um modelo genérico não tem como saber isso. O modelo local também tem custo por ticket praticamente nulo, responde em milissegundos e não envia dados a terceiros. Os custos que existem são de manutenção e retreino. A diferença de acerto vale para esta configuração de LLM; um LLM mais forte, com definições das categorias, provavelmente reduziria a distância.

### 1.3 O agente na fila: copiloto, não piloto

Para cada ticket, o agente recebe:
- as **palavras que levaram à decisão**, para entender e contestar a IA;
- os **3 tickets mais parecidos** já resolvidos;
- um **rascunho de resposta**, redigido por LLM a partir do texto original e de casos parecidos. O agente revisa antes de enviar. Aqui o LLM é bom: redigir, não classificar.

---

## 2. O que NÃO automatizar

**Princípio: rotear ≠ executar ≠ responder.** A IA pode decidir a fila. A ação pedida e a resposta, em alguns casos, ficam sempre com humanos, seja qual for a confiança do modelo.

| Regra | Frequência* | O que acontece | Por quê |
|---|---|---|---|
| **Segurança** (phishing, malware, invasão) | 0,7% | Vai direto para Segurança da Informação, com escalonamento. **Sobrepõe o classificador** | Custo assimétrico: tratar um incidente como rotina é caro |
| **Saúde / afastamento** | 2,0% | Só o RH responde. **Sem rascunho por LLM** | Dado de saúde é dado pessoal sensível (LGPD, art. 11) |
| **Desligamento** | 2,0% | Revogação de acessos por humano, com checklist | Erro = ex-funcionário com acesso, ou ativo bloqueado |
| **Aprovação financeira** | 10,4% | A IA roteia e prepara; a aprovação é humana | Decisão com responsabilidade, não classificação |
| **Privilégio de acesso** | 3,5% | Concessão com aprovação do gestor e registro | Controle de segurança auditável |
| **Urgência / indisponibilidade** | 7,7% | Prioridade sobe e o plantão é notificado | O tempo de espera importa mais que a categoria |

\* Frequência nos 47.837 tickets do Dataset 2 (no conjunto de teste, o mesmo valor). No total, **23,4%** dos tickets têm uma ação que exige humano, mesmo quando o roteamento é automático. As regras foram revisadas pela auditoria de dados: a versão 1 contava a palavra "administrator" da assinatura dos e-mails como pedido de privilégio (13,0% → 3,5%).

**Exemplos reais do Dataset 2** (texto já pré-processado na origem; # = índice da linha no CSV, começando em 0, sem contar o cabeçalho):

| Ticket | Rótulo original | O que a política faz |
|---|---|---|
| #36521 *"suspicious sent monday … regarding multiple complains our users please block following domains …"* | Hardware | Pela categoria, iria para a fila de Hardware. A regra de **segurança** manda para Segurança da Informação, com escalonamento |
| #5461 *"leaver mobile phone … had mobile subscription plan available mobile number note mailbox receive messages"* | Hardware | Roteado para Hardware, mas é um **desligamento**: revogar linha e caixa de e-mail é com humano, com checklist |
| #31874 *"maternity leaver form … please find attached filled …"* | HR Support | **Saúde/afastamento**: só o RH responde, e o texto **não vai para o LLM** |
| #8682 *"new purchase po … please log allocation … mandatory receipts section order …"* | Purchase | Roteamento automático, mas a **aprovação da compra** é humana |

**Por que regras explícitas, e não a categoria prevista:** os temas sensíveis atravessam as categorias. As menções a segurança caem 41% em Hardware, 19% em Administrative rights e 17% em Access. Uma regra baseada na categoria deixaria passar a maioria. As regras são propositalmente sensíveis: um falso alarme custa segundos de um humano.

**Também não automatizamos:**
- **Fechar tickets.** Quem confirma a resolução é o cliente ou o agente.
- **Tickets fora do domínio** (outro idioma, assunto novo), que vão para a faixa humana pelas travas.
- **Respostas enviadas sem revisão.** Não há base nos dados para medir a qualidade de respostas automáticas: as "resoluções" do Dataset 1 são texto sintético sem sentido.

**Limitação conhecida da política:** as regras usam palavras-chave e não pegam todas as variações (ex.: "leaving", "last day", "remove his access" não acionam a regra de desligamento). No piloto, os casos que escaparem viram novas regras ou exemplos para um classificador de sensibilidade. A regra de privilégio cobre pedidos explícitos (*admin rights, permissions, grant access*); os tickets rotulados "Administrative rights" falam mais de instalação e upgrade e quase não usam esse vocabulário: a regra dispara em só 1,5% deles (27 de 1.760). No piloto, decidir com Segurança se a categoria inteira exige aprovação.

---

## 3. Como funciona na prática

```
TICKET ENTRA (e-mail, chat, telefone transcrito, redes)
 │
 ├─ 1. POLÍTICA ──────────── segurança? ──────────────► Fila Segurança + escalonamento  [humano]
 │                           urgência? ───────────────► prioridade ↑ + plantão          [humano notificado]
 │                           saúde? ──────────────────► sem rascunho por LLM
 │
 ├─ 2. TRAVAS DE DOMÍNIO ── não reconheço este ticket ─► Triagem humana (9,7%)          [humano]
 │
 ├─ 3. CLASSIFICADOR
 │      confiança ≥ limiar da categoria ─► roteado automaticamente (65,5%)  [IA]
 │      confiança média ─────────────────► 2 sugestões, agente escolhe (23,3%) [IA sugere, humano decide]
 │      confiança baixa ─────────────────► triagem humana (1,5%)            [humano]
 │
 └─ 4. NA FILA ── agente recebe: palavras-chave + 3 casos parecidos + rascunho (LLM)
                  ação sensível (aprovar, conceder, revogar) ──► sempre humano
                  agente corrige categoria? ──► vira dado de retreino (mensal)
```

**Onde o humano intervém:** em 100% das ações sensíveis, em 34,5% das decisões de roteamento (faixas de sugestão e humana) e na revisão de 100% das respostas.

---

## 4. Implantação: piloto antes de escala

| Semana | O que | Critério para avançar |
|---|---|---|
| 0 | **Instrumentar:** carimbos separados de criação, 1ª resposta e resolução; log de cada mudança de fila; categoria na abertura × na resolução. **Retreinar** o modelo no histórico rotulado da operação e medir a concordância desses rótulos | Dados chegando completos; rótulos históricos com qualidade suficiente |
| 1–2 | **Modo sombra:** a IA classifica, mas não roteia; mede-se a concordância com os agentes | Concordância ≥ 95% na faixa automática |
| 3–4 | **Faixa automática ligada** para as 3 categorias mais estáveis (Purchase, Access, Storage: 97,8–99,0%) | Reatribuições não aumentam |
| 5+ | Todas as categorias, sugestões e rascunho | Ganho de tempo medido ≥ cenário conservador |

Com a instrumentação ligada na semana 0, ao fim das 4 semanas de piloto a operação passa a ter, pela primeira vez, dados para um **diagnóstico real** de gargalos.

**Métricas do piloto** (substituem as premissas do ROI):
1. Minutos de triagem por ticket, antes × depois
2. % de tickets que mudam de fila
3. Tempo de espera em fila errada
4. Concordância do agente com a IA na faixa automática (detecta deriva do modelo)

---

## 5. Retorno esperado (premissas a validar no piloto)

Tempo de agente liberado na triagem: **552 a 2.106 h/ano, ou 46 a 175 h/mês** (0,3 a 1,2 pessoa). No cenário base, **≈ 1.218 h/ano ≈ 101 h/mês ≈ 0,7 pessoa ≈ R$ 47 mil/ano (≈ R$ 3,9 mil/mês)**.

**Maior desperdício recuperável:** entre o que se pode medir, é o **tempo de triagem manual**, de ~1.500 h/ano no cenário base, das quais a IA libera ~80%. O desperdício provavelmente maior, o tempo que o cliente espera com o ticket na fila errada, não é mensurável hoje. Medi-lo é o objetivo nº 1 da instrumentação. É tempo liberado bruto, não economia de caixa, e ainda não desconta implantação e manutenção. O resultado depende quase só de uma premissa de fonte fraca (minutos de triagem por ticket hoje), por isso ela é a 1ª métrica do piloto. Ficam fora, de propósito: o tempo de espera do cliente na fila errada (provavelmente o maior ganho), a redução de reroteamento (não demonstrada) e os ganhos de rascunho.

_Fonte: `01-diagnostico/outputs/modelo_desperdicio.md` e aba ROI do protótipo._

---

## 6. Operação contínua: o que acontece depois da entrega

| Frente | Como |
|---|---|
| **Monitoramento** | Painel semanal com: % automático, concordância do agente com a IA na faixa automática, reatribuições e alertas da política. **Gatilho:** se a concordância cair abaixo de 93% em qualquer categoria por 2 semanas, ela volta para a faixa de sugestão. (95% é a barra de **entrada** no piloto; 93% é o gatilho de **recuo** na operação, com folga para a variação semanal.) |
| **Kill switch** | Uma chave desliga o roteamento automático (tudo vira sugestão) sem parar a operação. Testada no modo sombra |
| **Retreino** | Mensal, com as correções dos agentes. Cada versão do modelo é comparada com a anterior no mesmo conjunto de teste antes de entrar |
| **Deriva** | A trava de domínio também mede deriva: um aumento de tickets "desconhecidos" indica produto, campanha ou incidente novo, e vira alerta para o gestor |
| **Dono** | 1 responsável pelo modelo (AI Master) + donos das regras de política (Segurança, RH, Financeiro), que revisam as regras a cada trimestre |
| **Adoção** | Treinamento de 1 h para os agentes (como ler a explicação, como corrigir a IA, quando ignorar) + canal de feedback. A barra de adoção é a concordância e as correções, não "uso do sistema" |

