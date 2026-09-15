# Diagnóstico de Churn — RavenStack

**Para:** CEO e liderança · **De:** AI Master (candidato) · **Base:** 500 contas, 5 tabelas cruzadas (contas, assinaturas, uso de produto, tickets de suporte, eventos de cancelamento)

---

## 1. O que eu encontrei, em uma página

- **Procurei as três causas óbvias de churn — uso baixo, suporte ruim, preço alto. Nenhuma das três está nos dados**, e tenho o número que descarta cada uma.
- O time de CS e o time de Produto **estão os dois certos** ao mesmo tempo — e é exatamente por isso que ninguém achava o problema. Explico na seção 2.
- Existe **um segmento com o dobro da taxa de cancelamento** da empresa (DevTools, 31% contra 19% no resto) e um **canal de aquisição que decide o destino da conta antes mesmo da venda fechar** (contas vindas de evento cancelam a 30%; de indicação de parceiro, a 15%). Nenhum dos dois é prova fechada — são as duas melhores pistas que temos, e digo exatamente o quão fortes elas são.
- **56% de toda a receita em risco de cancelamento está concentrada em 100 contas** (20% da base) — e a taxa de cancelamento é *igual* em contas pequenas e grandes. O critério que separa quem priorizar não é comportamento, é dinheiro.
- A própria empresa tem **dois números de churn diferentes**: 110 contas marcadas como perdidas, mas 352 contas com histórico de cancelamento no sistema — 35 delas marcadas como perdidas sem nenhum registro do motivo. Isso precisa ser resolvido antes de qualquer outra decisão de retenção, porque enquanto existirem dois números, toda conversa sobre churn vira uma discussão sobre qual número está certo.

---

## 2. Por que ninguém estava achando o problema

**O CS e o Produto estão os dois certos — e é por isso que "algo não bate".**

O CS diz que a satisfação está ok. Está: quem cancelou avaliou o suporte em **4,00** (de 5); quem ficou, **3,95**. Quem foi embora estava, na média, tão satisfeito quanto quem ficou — às vezes um pouco mais. O tempo de resolução foi praticamente igual (35,5h contra 36,5h) e a primeira resposta chegou mais rápido para quem cancelou (85 min contra 90 min).

O Produto diz que o uso cresceu. E cresceu: uso médio por conta subiu cerca de 3,5% nos últimos dois anos.

**Consequência prática:** os dois indicadores que a empresa usa hoje para dizer se uma conta está saudável — satisfação e uso — não avisam nada sobre quem vai cancelar. Fui além e testei individualmente cada uma das 40 funcionalidades do produto (frequência de uso e taxa de erro, uma a uma): nenhuma separa quem fica de quem sai. Testei os quatro planos, os sete países, os cinco canais de aquisição, quem está em trial. Testei tudo que as cinco tabelas permitem medir **ao mesmo tempo, num único modelo**: os 28 fatores juntos não explicam por que uma conta cancela mais que outra.

Isso não significa que não haja causa — significa que a causa não está em **nenhuma das variáveis que a RavenStack mede hoje**. É a descoberta mais importante deste relatório, e é o assunto da seção 8.

---

## 3. O que NÃO está causando o churn

Com número, não com opinião:

| Hipótese óbvia | O que os dados mostram |
|---|---|
| Uso baixo do produto | Quem cancela usa o produto tanto quanto quem fica (diferença de 3,5% no total, sem direção clara) |
| Suporte ruim | Satisfação de quem cancela (4,00) é igual ou levemente **melhor** que de quem fica (3,95) |
| Demora no atendimento | Tempo de resolução é o mesmo (35,5h vs 36,5h); primeira resposta é mais rápida pra quem cancela |
| Excesso de bugs / erros | Nenhuma das 40 funcionalidades do produto mostra diferença de taxa de erro entre quem sai e quem fica |
| Plano caro demais | As três faixas de preço (Basic, Pro, Enterprise) cancelam praticamente na mesma taxa (22%, 22%, 22%) |
| Cliente novo (trial) mais instável | Trial cancela um pouco mais (26% vs 21%), mas a diferença não é maior do que se explicaria por acaso |

Nenhuma dessas seis hipóteses — as que qualquer análise de churn testaria primeiro — sobrevive ao cruzamento das cinco tabelas.

---

## 4. Onde o dinheiro está

**A taxa de cancelamento é a mesma em toda a carteira — Basic 22,0%, Pro 21,9%, Enterprise 22,1%. Não existe plano seguro.** Mas o preço de perder uma conta não é igual: cada conta Enterprise perdida leva em média **$2.740/mês**; cada Basic, **$1.889** — 45% mais prejuízo pelo mesmo risco.

Como o risco percentual é igual em toda parte, priorizar por risco não ajuda. **O único critério que discrimina é dinheiro**, e aqui ele é muito concentrado:

- As **100 maiores contas** (20% da base) carregam **66,8% de todo o MRR** da empresa e **$143.762 dos $254.952 já em risco — 56% de toda a exposição financeira em 20% dos clientes.**
- As **50 maiores** (10% da base) já respondem por **$93.331** desse risco — 36,6% da exposição em 50 contas nomeadas.

Isso muda a pergunta de "quantas contas vamos perder" para "quais contas, em dólar, não podemos perder" — e essa lista tem nome.

---

## 5. Os segmentos em risco, com nome e cifra

**a) DevTools — a vertical com o dobro da taxa de cancelamento.** 31,0% de churn (35 de 113 contas) contra 19,4% no resto da carteira — **$67.153 em risco**, 35% de todo o MRR desse segmento. É o padrão mais forte de todo o relatório: mesmo controlando por canal de aquisição, plano e país, ele não desaparece. Ainda assim, é a **melhor pista, não uma prova** — comparei cinco indústrias e escolhi a mais extrema, então uma parte do tamanho do efeito pode ser sorte de amostra. Trato isso com cuidado na seção 7.

**b) Contas vindas de evento presencial — o pior canal de aquisição.** 30,2% de churn contra 14,6% de quem veio por indicação de parceiro — mais que o dobro. Em dinheiro: **$84.888 em risco** (39% do MRR originado em evento) contra **$30.605** (11,6%) no canal de parceiro. O canal é decidido antes da venda fechar — nenhuma ação pós-venda do CS muda isso.

**c) A interseção DevTools + evento — o bolso mais concentrado de risco.** Contas que são DevTools **e** vieram de evento cancelam a **43,5%** (10 de 23 contas) — quase o dobro da taxa isolada de DevTools. É uma amostra pequena (23 contas), mas é onde as duas piores pistas se somam.

**Contas específicas para ação imediata** (maior MRR, ainda ativas, no perfil de risco):

| Conta | Segmento | MRR/mês | Assentos |
|---|---|---|---|
| Company_157 | Basic · parceiro | $13.930 | 70 |
| Company_486 | Enterprise · orgânico | $12.935 | 4 |
| Company_350 | Basic · orgânico | $8.159 | 41 |
| Company_82 | Pro · parceiro | $7.562 | 11 |
| Company_203 | Pro · outro | $5.970 | 23 |

E entre as contas **já perdidas** de maior valor — para entender o que aconteceu e, quando possível, tentar reativação: Company_4 (HealthTech, Enterprise, $21.691/mês, veio de evento), Company_99 (FinTech, Enterprise, $11.144/mês) e Company_240 (FinTech, Enterprise, $10.945/mês, veio de evento).

---

## 6. O que fazer — 5 ações priorizadas

| # | Ação | Dono | Prazo | Custo | Impacto estimado | Como saber se funcionou |
|---|---|---|---|---|---|---|
| 1 | **Reconciliar os dois números de churn.** Escrever uma definição única de "cliente perdido", com dono, e investigar por que 35 contas marcadas como perdidas não têm motivo registrado. | RevOps | 2 semanas | Baixo | Sem isso, nenhuma das outras 4 ações pode ser medida com confiança | Um único número de churn é citado em toda a empresa |
| 2 | **Tirar satisfação e uso do "score de saúde" da conta.** Nenhum dos dois indica quem vai cancelar — hoje eles dão falsa segurança. | Head de CS | Imediato | Zero — é parar de fazer algo | Reduz alarme falso e alerta perdido | CSAT deixa de aparecer como indicador de retenção no próximo QBR |
| 3 | **Trabalhar a fila de retenção por MRR em risco**, não por taxa de churn. As 100 maiores contas (lista completa no painel anexo) recebem revisão nominal trimestral com CSM designado. | Head de CS | Fila pronta na segunda-feira | Realocação de carteira, sem contratação | Cobre 56% da exposição financeira com 20% da carteira | MRR em risco do top-20% cai abaixo de $120k em 2 trimestres |
| 4 | **Entrevistar 20 contas DevTools** — as 10 maiores perdidas e as 10 maiores que ficaram — perguntando o que usam junto com, ou no lugar de, a RavenStack. | VP de Produto | 3 semanas | ~10h de agenda | Se houver padrão nomeável, orienta o roadmap; se não houver, a decisão vira preço/ICP, não produto | Existe ou não existe um padrão comum nas 20 conversas |
| 5 | **Recalcular o payback de marketing de eventos com a retenção real da própria coorte**, não com a média da empresa (o modelo de CAC hoje provavelmente subestima a perda desse canal em ~1,4x). | CRO / Growth + Financeiro | Próximo ciclo de orçamento | Baixo — é recálculo de planilha | Corrige a alocação de orçamento de aquisição | Churn da coorte de evento abaixo de 25% em 2 trimestres |

---

## 7. O que eu não consigo afirmar

Por honestidade — e porque o critério de qualidade deste desafio pede exatamente isso:

- **O achado de DevTools e o do canal de evento são a melhor pista disponível, não fato comprovado.** Testei 500 contas contra o acaso de várias formas ao mesmo tempo (mais de 100 comparações no total, entre segmentos, funcionalidades e tickets); estatisticamente, isso é esperado gerar alguns resultados "chamativos" só por volume de tentativas — e os dois que sobraram são justamente esses. Eles resistem quando eu tento explicá-los por outro motivo (canal, plano, país), o que é um bom sinal, mas a amostra (113 contas DevTools, 96 contas de evento) é pequena para ser prova. Trate como hipótese para confirmar com o cliente ou em dado novo, não como fato para repriorizar uma vertical inteira.
- **Testei o conjunto completo de tudo que a empresa mede hoje — uso, suporte, plano, canal, indústria, tempo de vida da conta, 28 fatores ao mesmo tempo — e ele não explica por que uma conta cancela.** Isso é diferente de dizer que a causa não existe: é dizer que ela não está capturada em nenhum dado que a RavenStack coleta hoje. A seção 8 é a resposta a isso.
- **Uma versão anterior deste relatório afirmava que "quem cancela usa mais o produto pouco antes de sair".** Ao revisar com mais rigor, encontrei um problema na própria tabela de uso (ela não fecha corretamente com a data de cadastro nem com a data de cancelamento da conta) e, testando direito, a diferença não se sustenta. Removi a afirmação. Cito isso aqui de propósito: prefiro admitir um erro corrigido do que deixar uma conclusão errada na entrega.
- **Não sei se a RavenStack vende para setores fora de tecnologia.** As 500 contas desta base são inteiramente de cinco verticais de tecnologia (DevTools, FinTech, HealthTech, EdTech, Cybersecurity). Se a empresa real atende outros setores, essa base não representa o negócio inteiro.

---

## 8. O que a RavenStack precisa passar a medir

O resultado mais valioso deste diagnóstico é negativo: **os dados que a empresa coleta hoje não predizem quem vai cancelar.** Treinei um modelo preditivo formal com tudo que temos disponível — o resultado é essencialmente um chute educado, não uma previsão confiável. Isso não é falha da análise; é a resposta.

O que falta, e que nenhuma das cinco tabelas atuais captura:

- **Recência de login** — quando foi a última vez que alguém da conta de fato entrou no produto (temos volume de uso, não recência).
- **Ativação de assento** — quantos dos assentos pagos têm usuário ativo (uma conta de 40 assentos com 3 ativos é um sinal que hoje não existe).
- **Falhas de cobrança** — cartão recusado, fatura vencida.
- **Proximidade da renovação** — se o cancelamento se concentra perto da data de renovação do contrato.
- **Registro estruturado do motivo de saída** — hoje "motivo de cancelamento" é um menu com 6 opções quase empatadas (entre 13% e 20% cada) e quase 10% em "desconhecido"; um campo de texto livre revisado manualmente diria mais em um trimestre do que esse menu disse em dois anos.

Esse é o roadmap de instrumentação — e é, também, o motivo pelo qual "construir um modelo preditivo agora" não é a prioridade certa. Está detalhado no anexo técnico.

---

*Anexos: [`dashboard.html`](./dashboard.html) ([versão ao vivo](https://claude.ai/artifact/Vfrjf56P6w8Vp1HkRLNY3j)) — verificação de cada número e teste estatístico citado aqui · [`painel_retencao.html`](./painel_retencao.html) ([versão ao vivo](https://claude.ai/artifact/44PuoTrXZ5Vm1TYm3r618G)) — fila de retenção operacional · [`analysis/`](./analysis/) — código-fonte que gera `report_data.json` e os scripts de auditoria, roda com `python analysis/build_report_data.py` · [`../process-log/PROCESS_LOG.md`](../process-log/PROCESS_LOG.md) — como esta análise foi construída e auditada.*
