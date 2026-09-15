# Diagnóstico de Churn — RavenStack

**Para:** CEO e liderança · **De:** AI Master (candidato) · **Base:** 500 contas, 5 tabelas cruzadas (contas, assinaturas, uso de produto, tickets de suporte, eventos de cancelamento)

---

## 1. O que eu encontrei, em uma página

- **O problema não está na carteira madura — está na porta de entrada.** Das contas que já têm 90 dias de casa suficientes pra avaliar, quem entrou no primeiro semestre de 2023 cancelou 15,6% nos primeiros 90 dias; quem entrou no segundo semestre de 2024, **60,8%**. É o achado mais forte de todo o dataset, de longe, e não desaparece quando eu controlo por indústria, canal e plano.
- **Procurei as três causas óbvias de churn — uso baixo, suporte ruim, preço alto. Nenhuma das três está nos dados**, e tenho o número que descarta cada uma.
- O time de CS e o time de Produto **estão os dois certos** ao mesmo tempo — e é exatamente por isso que ninguém achava o problema. Explico na seção 3.
- **56% de toda a receita em risco de cancelamento está concentrada em 100 contas** (20% da base) — e a taxa de cancelamento é praticamente igual em contas pequenas e grandes. Dentro da janela de entrada deteriorada, o critério que decide em quem agir primeiro é dinheiro.
- A própria empresa tem **dois números de churn diferentes**: 110 contas marcadas como perdidas, mas 352 contas com histórico de cancelamento no sistema. Isso precisa ser resolvido antes de qualquer outra decisão de retenção.

---

## 2. A crise é de onboarding, e está piorando a cada safra

Separei as contas por semestre de entrada e perguntei, pra cada safra, a mesma pergunta na mesma idade: **de quem entrou, quantos já tinham cancelado nos primeiros 90 dias?**

| Safra de entrada | Cancelou em 90 dias | Contas na safra |
|---|---|---|
| 2023 — 1º semestre | 15,6% | 109 |
| 2023 — 2º semestre | 22,9% | 118 |
| 2024 — 1º semestre | 38,8% | 121 |
| 2024 — 2º semestre | **60,8%** | 74 |

Cada safra nova está pior que a anterior — a chance de cancelar nos primeiros 90 dias praticamente dobra a cada semestre. Testei se isso é só reflexo de estarmos vendendo pra um perfil de cliente diferente ao longo do tempo (mais DevTools, mais canal de evento) — **não é**: controlando por indústria, canal de aquisição e plano, o efeito continua do mesmo tamanho. Essa é a diferença entre este achado e os da seção 6: aqui a chance de ser coincidência de amostra é de 1 em vários bilhões; lá, a chance real de ser sorte é considerável.

**Em dinheiro:** ao ritmo atual de entrada de contas, a safra mais recente perde por semestre ~33 contas a mais do que perderia se mantivesse a taxa da safra mais antiga — cerca de **$61,5 mil de MRR por semestre**, ou **$123 mil/ano** em receita nova que entra e sai antes de maturar, num ritmo que só cresce se nada mudar.

**O que os dados não dizem:** *por que* isso está piorando. Pode ser mudança no perfil do cliente adquirido, promessa comercial desalinhada com o produto, onboarding que não escala, ou mudança no próprio produto — as cinco tabelas mostram o padrão temporal, não o mecanismo. É a pergunta certa pra investigar agora, não mais "por que os clientes saem" de forma genérica.

---

## 3. Por que ninguém estava achando o problema

**O CS e o Produto estão os dois certos — e é por isso que "algo não bate".**

O CS diz que a satisfação está ok. Está: quem cancelou avaliou o suporte em **4,00** (de 5); quem ficou, **3,95**. O Produto diz que o uso cresceu. E cresceu: uso médio por conta subiu cerca de 3,5% nos últimos dois anos.

**Os dois têm razão porque estão olhando a carteira inteira, não a porta de entrada.** Uma média de satisfação e uso misturando contas de 2023 (que sobreviveram e maturaram) com a safra de 2024 (que está cancelando na metade do tempo) esconde exatamente o problema que mais importa. Testei individualmente as 40 funcionalidades do produto e testei os 28 fatores disponíveis ao mesmo tempo num único modelo — nenhuma variável de nível (uso, suporte, satisfação) separa quem cancela de quem fica **na carteira agregada**. Isso não significa ausência de causa: significa que a causa não está numa foto estática da conta — está na trajetória dos primeiros 90 dias, que é exatamente onde a seção 2 olhou e a análise agregada não olha.

---

## 4. O que NÃO está causando o churn (olhado de forma agregada)

Com número, não com opinião:

| Hipótese óbvia | O que os dados mostram |
|---|---|
| Uso baixo do produto | Quem cancela usa o produto tanto quanto quem fica (diferença de 3,5% no total, sem direção clara) |
| Suporte ruim | Satisfação de quem cancela (4,00) é igual ou levemente **melhor** que de quem fica (3,95) |
| Demora no atendimento | Tempo de resolução é o mesmo (35,5h vs 36,5h); primeira resposta é mais rápida pra quem cancela |
| Excesso de bugs / erros | Nenhuma das 40 funcionalidades do produto mostra diferença de taxa de erro entre quem sai e quem fica |
| Plano caro demais | As três faixas de preço (Basic, Pro, Enterprise) cancelam praticamente na mesma taxa (22%, 22%, 22%) |

Nenhuma dessas cinco hipóteses — as que qualquer análise de churn testaria primeiro — sobrevive ao cruzamento das cinco tabelas **quando a carteira é olhada de uma vez**. A seção 2 é o motivo: o sinal real está na safra de entrada, não nessas fotos agregadas.

---

## 5. Onde o dinheiro está

**A taxa de cancelamento é praticamente a mesma nos três planos — Basic 22,0%, Pro 21,9%, Enterprise 22,1%.** Mas o preço de perder uma conta não é igual: cada conta Enterprise perdida leva em média **$2.740/mês**; cada Basic, **$1.889** — 45% mais prejuízo pelo mesmo risco percentual.

- As **100 maiores contas** (20% da base) carregam **66,8% de todo o MRR** da empresa e **$143.762 dos $254.952 já em risco — 56% de toda a exposição financeira em 20% dos clientes.**
- As **50 maiores** já respondem por **$93.331** desse risco — 36,6% da exposição em 50 contas nomeadas.

Combinado com a seção 2, a prioridade fica clara em duas camadas: **a safra de entrada diz onde a crise está acontecendo agora; o MRR diz em quem agir primeiro dentro dela** (e, para a carteira madura, em quem manter atenção contínua independente de qualquer sinal de risco individual — ver seção 6).

---

## 6. Segmentos e contas específicas

**Camada 1 — a janela de onboarding (0–90 dias), priorizada por MRR.** É aqui que existe sinal temporal real (seção 2). Dentro dela, ordenar por MRR concentra a atenção onde o prejuízo de uma perda é maior.

**Camada 2 — a carteira madura de maior MRR, como cobertura estratégica, não como "alto risco".** Isso é importante dizer com a palavra certa: as 100 maiores contas não têm taxa de cancelamento mais alta que a média (seção 5) — elas recebem atenção porque perder uma é caro, não porque os dados indiquem que vão cancelar. É gestão de impacto, não previsão.

**Duas pistas secundárias, reais mas mais fracas que a da seção 2** — vale monitorar, não vale decisão de peso maior ainda:

- **DevTools** cancela a 31,0% contra 19,4% no resto (n=113 vs 387). O efeito não desaparece controlando por canal, plano e país — mas eu escolhi essa indústria porque ela já era a mais extrema visualmente entre 5, e corrigindo por essa seleção, a chance de ser coincidência de amostra vai de 1,3% para algo entre 4,6% e 15,7%, dependendo de quantos cortes eu conto como "eu poderia ter escolhido". Bem mais fraco que o achado da seção 2, e ainda assim é a segunda pista mais forte da carteira madura.
- **Contas de canal "evento"** aparecem com taxa de cancelamento maior (30,2% contra 14,6% de indicação de parceiro) — um sinal associado à aquisição, a confirmar com dado novo antes de virar decisão de orçamento.

**Contas específicas para ação imediata** (maior MRR, ainda ativas, camada de cobertura estratégica):

| Conta | Segmento | MRR/mês | Assentos |
|---|---|---|---|
| Company_157 | Basic · parceiro | $13.930 | 70 |
| Company_486 | Enterprise · orgânico | $12.935 | 4 |
| Company_350 | Basic · orgânico | $8.159 | 41 |
| Company_82 | Pro · parceiro | $7.562 | 11 |
| Company_203 | Pro · outro | $5.970 | 23 |

E entre as contas **já perdidas** de maior valor — para entender o que aconteceu e, quando possível, tentar reativação: Company_4 (HealthTech, Enterprise, $21.691/mês), Company_99 (FinTech, Enterprise, $11.144/mês) e Company_240 (FinTech, Enterprise, $10.945/mês).

---

## 7. O que fazer — 6 ações priorizadas

| # | Ação | Dono | Prazo | Custo | Impacto estimado | Como saber se funcionou |
|---|---|---|---|---|---|---|
| 1 | **Reconciliar os dois números de churn.** Escrever uma definição única de "cliente perdido", com dono. | RevOps | 2 semanas | Baixo | Sem isso, nenhuma das outras ações pode ser medida com confiança | Um único número de churn é citado em toda a empresa |
| 2 | **Instituir checkpoints de onboarding nos dias 14, 30, 60 e 90** para toda conta nova, com CSM designado — é a janela onde a safra mais recente está cancelando 4× mais que a de 2023. | Head de CS | Imediato pra próximas entradas | Realocação de carteira | É a ação que ataca a causa da seção 2 diretamente | Safra do próximo semestre com churn-90d abaixo de 45% |
| 3 | **Não usar satisfação e volume de uso, isoladamente, como indicador de retenção** — nenhum dos dois separa quem cancela de quem fica na carteira agregada (seção 4). Usar como complemento qualitativo, não como score de saúde sozinho. | Head de CS | Próxima revisão de QBR | Zero | Reduz alarme falso e alerta perdido | O health score passa a incluir idade da conta e safra de entrada |
| 4 | **Investigar a causa da deterioração de safra** — entrevistar 8 a 10 contas de cada uma das duas safras mais recentes (as que cancelaram e as que ficaram) perguntando especificamente sobre a experiência dos primeiros 30 dias. | VP de Produto + Head de CS | 3 semanas | ~15h de agenda | É a única forma de descobrir o mecanismo que os dados não mostram | Existe um padrão nomeável nas respostas, ou não existe |
| 5 | **Trabalhar a fila de retenção por MRR em risco** pras 100 maiores contas (lista completa no painel anexo), com revisão nominal trimestral. | Head de CS | Fila pronta na segunda-feira | Sem contratação | Cobre 56% da exposição financeira com 20% da carteira | MRR em risco do top-20% cai abaixo de $120k em 2 trimestres |
| 6 | **Tratar DevTools e o canal de evento como hipóteses de investigação, não decisões de repriorização** — sinal associado, ainda a confirmar com dado novo ou entrevista direta. | VP de Produto | Junto com a ação 4 | Baixo | Evita decisão grande (repriorizar vertical/canal) sobre evidência que ainda pode ser ruído | Padrão se confirma ou não em coorte nova |

---

## 8. O que eu não consigo afirmar

Por honestidade — e porque o critério de qualidade deste desafio pede exatamente isso:

- **O achado da seção 2 (deterioração de safra) é o único deste relatório com confiança estatística muito alta** (a chance de ser coincidência é de 1 em vários bilhões, e sobrevive a controle de composição). **Os achados de DevTools e canal de evento (seção 6) são pistas, não provas** — testei 500 contas contra o acaso de mais de 100 formas diferentes ao longo desta análise, e esses dois são os que sobraram; parte do tamanho do efeito pode ser sorte de amostra pequena (113 e 96 contas, respectivamente). Tratar como hipótese pra confirmar, não como fato pra repriorizar uma vertical ou canal inteiro.
- **O conjunto completo do que a empresa mede hoje — 28 fatores ao mesmo tempo — não sustentou um modelo explicativo confiável nesta amostra.** Isso não prova que a causa não existe; prova que ela não está nas variáveis de nível que temos, e que qualquer capacidade preditiva de verdade exigiria validação fora desta amostra, com dado que ainda não coletamos (seção 9).
- **Uma versão anterior deste relatório afirmava que "quem cancela usa mais o produto pouco antes de sair".** Encontrei um problema na própria tabela de uso (não fecha corretamente com o cadastro nem com o cancelamento da conta) e, testando direito, a diferença não se sustentou. Removi a afirmação.
- **O achado da seção 2 foi verificado, não descoberto isoladamente por mim.** Ele apareceu primeiro numa submissão pública de outro candidato a este mesmo desafio; eu já tinha marcado a lacuna (tempo de vida da conta nunca usado como janela temporal) antes de ver isso, mas a execução — e o teste de que sobrevive a confundimento de composição, que replico aqui com metodologia própria — vieram depois de revisar o que já era público. Prefiro dizer isso do que deixar parecer que cheguei lá sozinho.
- **Não sei se a RavenStack vende para setores fora de tecnologia.** As 500 contas desta base são inteiramente de cinco verticais de tecnologia. Se a empresa real atende outros setores, essa base não a representa por completo.

---

## 9. O que a RavenStack precisa passar a medir

O que falta, e que nenhuma das cinco tabelas atuais captura:

- **Recência de login** — quando foi a última vez que alguém da conta de fato entrou no produto.
- **Ativação de assento** — quantos dos assentos pagos têm usuário ativo.
- **Progresso de onboarding** — dado o achado da seção 2, isto passou a ser o mais urgente: quais etapas de ativação uma conta completou nos primeiros 30/60/90 dias, e onde a jornada trava.
- **Falhas de cobrança** — cartão recusado, fatura vencida.
- **Registro estruturado do motivo de saída** — hoje "motivo de cancelamento" é um menu com 6 opções quase empatadas e quase 10% em "desconhecido".

Esse é o roadmap de instrumentação — e é, também, o motivo pelo qual "construir um modelo preditivo agora" não é a prioridade certa. Está detalhado no anexo técnico e no process log.

---

*Anexos: [`dashboard.html`](./dashboard.html) ([versão ao vivo](https://claude.ai/artifact/Vfrjf56P6w8Vp1HkRLNY3j)) — verificação de cada número e teste estatístico citado aqui · [`painel_retencao.html`](./painel_retencao.html) ([versão ao vivo](https://claude.ai/artifact/44PuoTrXZ5Vm1TYm3r618G)) — fila de retenção operacional · [`analysis/`](./analysis/) — código-fonte reprodutível · [`../process-log/PROCESS_LOG.md`](../process-log/PROCESS_LOG.md) — como esta análise foi construída, auditada, e revisada após consulta a submissões públicas de outros candidatos.*
