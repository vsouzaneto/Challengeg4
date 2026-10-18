# Diagnóstico de Churn: RavenStack

*Relatório de diagnóstico. Período analisado: jan/2023 a dez/2024. As 5 tabelas foram cruzadas, e os dados originais não foram alterados. Os números podem ser conferidos nas planilhas indicadas em cada seção (pasta `analise`). Valores em US$ de receita mensal (MRR), salvo indicação.*

---

## Resumo para o CEO

> **O churn não subiu da forma que o número sugere.** Em 24 meses, nenhuma conta deixou de ser cliente de vez: as 500 contas terminam 2024 com assinatura ativa. O que subiu foi a quantidade de **assinaturas encerradas**. Mais da metade delas não é perda: são trocas de assinatura e compras feitas a mais e desfeitas em poucos dias.
>
> **A perda real existe e está concentrada.** Contas Enterprise grandes estão desligando pacotes de licenças e continuam clientes.

| | "Churn" de receita como é contado hoje | Perda real |
|---|---|---|
| 24 meses | US$ 1,18 milhão (486 assinaturas) | **US$ 538 mil (189 assinaturas)** |
| 4º trimestre de 2024 | US$ 872 mil, **14,4%** do MRR do início do trimestre | **US$ 331 mil, 5,5%** do MRR |

**As três respostas:**

1. **Causa do aumento.** A partir de jul/2024, os clientes passaram a comprar assinaturas num ritmo muito mais rápido: muitas de uma vez, trocadas ou desfeitas em poucos dias. Essas trocas e desfazimentos são contados como churn. **Causa da perda real:** contas Enterprise desligando pacotes de licenças. Preço, produto, suporte e perfil de cliente não explicam nenhuma das duas.
2. **Quem está em risco.** As contas Enterprise, que concentram 78% da perda por redução, e entre elas uma lista de 10 contas nomeadas. Também os contratos anuais encerrados antes de 12 meses e as assinaturas nos primeiros 30 dias.
3. **O que fazer.**
   - Corrigir a forma de contar o churn (imediato).
   - Proteger as contas Enterprise antes de elas desligarem pacotes (maior impacto em US$).
   - Descobrir e corrigir o que mudou no processo de compra em jul/2024.
   - Endurecer a regra de cancelamento de contratos anuais.
   - Tornar obrigatório e claro o motivo de cada cancelamento.
   - Alinhar os sistemas para que a base de dados passe a ser coerente.

**Por que "algo não batia":**
- **Satisfação "ok":** a pesquisa de satisfação só registra notas 3, 4 e 5, nunca 1 ou 2, e 41% dos tickets ficam sem nota. Ela não consegue mostrar um cliente insatisfeito.
- **"Uso cresceu":** a tabela de uso tem o mesmo volume todo mês, cerca de 1.000 registros, enquanto as assinaturas ativas multiplicaram. As datas de uso estão espalhadas ao acaso. Esses dados não sustentam a frase.

---

## O que está acontecendo de verdade

### O "churn" de hoje mistura quatro coisas diferentes

Hoje, toda assinatura encerrada conta como churn. Separamos cada uma em quatro situações, usando a tabela de assinaturas, a única coerente da base (ver "Como chegamos aqui"):

| Situação | O que é | É perda? | 24 meses (qtd) | 24 meses (US$) |
|---|---|---|---|---|
| **Troca** | A conta abriu outra assinatura até 7 dias antes ou depois | Só a diferença de valor | 233 | 575 mil encerrados, 461 mil repostos → **114 mil de perda** |
| **Compra extra desfeita** | Assinatura com até 30 dias de vida; a conta já tinha outra mais antiga do mesmo plano | **Não** | 64 | 180 mil |
| **Redução real** | A conta desligou uma assinatura e continuou cliente | **Sim** | 185 | **400 mil** |
| **Saída do cliente** | A conta ficou sem nenhuma assinatura | **Sim** | 4 | **23 mil** (as 4 contas voltaram depois) |

### Por trimestre

| Trimestre | "Churn" de hoje (qtd) | Perda real (qtd) | "Churn" de hoje (US$) | Perda real (US$) | % que era perda |
|---|---|---|---|---|---|
| 2023-T4 | 14 | 11 | 49.160 | 46.218 | 94% |
| 2024-T1 | 27 | 20 | 50.138 | 44.828 | 89% |
| 2024-T2 | 37 | 29 | 59.026 | 36.192 | 61% |
| 2024-T3 | 80 | 43 | 146.668 | 77.445 | 53% |
| **2024-T4** | **324** | **84** | **871.812** | **331.314** | **38%** |

- **Até o início de 2024:** quase todo churn contado era perda real, mas pequena.
- **No 4º trimestre de 2024:** o número explode, mas 240 dos 324 encerramentos foram trocas ou compras desfeitas.
- **Gráfico:** `DADOS_CONSOLIDA_V1/02_Perda_Real_por_Trimestre.xlsx`, aba `1_Resumo_CEO`.

---

## 1. O que está causando o churn? (causa raiz)

### 1.1 Causa do aumento: o jeito de comprar mudou a partir de jul/2024

| Assinaturas iniciadas | Até jun/2024 | Jul–dez/2024 |
|---|---|---|
| Intervalo típico entre duas compras da mesma conta | 26 dias | **11 dias** (8 dias em nov–dez) |
| Compradas "em rajada" (3 ou mais da mesma conta em 7 dias) | 3% | **22%** (41% das Enterprise de dezembro) |
| Canceladas em até 30 dias | 0,7% | **6,1%** |
| Assinaturas novas por mês | 193 (jan–jun/24) | **529** |
| Contas novas cadastradas | 121 (jan–jun/24) | 152 |

- **Quem comprou mais foram os clientes que já existiam:** as compras cresceram 174%, os cadastros só 26%.
- **Comprando mais rápido, compram mais vezes errado ou a mais**, e trocam ou desfazem em seguida. Cada troca ou desfazimento vira um "churn" no número de hoje.
- **A mudança aparece em todos os países, indústrias e canais ao mesmo tempo.** Nenhum segmento se diferencia de forma confiável no cancelamento em 30 dias.
- **A rajada é mais comum no canal orgânico (30%), que não tem vendedor**, e em DevTools (27%). A Alemanha é a exceção: quase não tem rajada e foi o país que menos cresceu.
- **Leitura:** a simultaneidade aponta para uma mudança de **processo** (como se compra ou registra uma assinatura), não para um mercado ou um time de vendas.
- **Detalhes:** `DADOS_CONSOLIDA_V1/03_Ritmo_de_Compra_Segmentos.xlsx` e `DADOS_2024_NOV_DEZ/05_Upgrade_Downgrade_e_Rajadas.xlsx`.

### 1.2 Causa da perda real: contas Enterprise desligando pacotes

- **Enterprise concentra 78% da perda por redução e saída:** US$ 332 mil dos US$ 424 mil em 24 meses. No 4º trimestre de 2024: US$ 190 mil.
- **Não é porque o Enterprise reduz mais vezes.** Reduz na mesma frequência dos outros planos, cerca de 5 a cada 100 assinaturas. Cada licença Enterprise custa US$ 199 por mês, contra US$ 49 do Pro e US$ 19 do Basic.
- **Não é troca de plano.** Em 79 das 89 reduções Enterprise, a conta continuou com outra Enterprise. Ela desligou um pacote inteiro (cada assinatura tem número fixo de licenças), em média 25 licenças, ou cerca de 1/4 do que pagava.
- **Parte disso é compra desfeita:** 21 dessas 79 reduções (US$ 147 mil) foram compras a mais desfeitas em até 30 dias, concentradas em nov–dez/2024. Na tabela "O que está acontecendo de verdade", elas já estão fora da perda real.
- **Detalhes:** `DADOS_ENTERPRISE/01_Enterprise_por_Periodo.xlsx` e `DADOS_ENTERPRISE/DIAGNOSTICO_ENTERPRISE.md`.

### 1.3 O que testamos e NÃO é causa (correlação × causalidade)

| Hipótese | Resultado | Onde ver |
|---|---|---|
| Aumento de preço | **Não houve.** Preço por licença idêntico em todas as assinaturas e períodos | `DADOS_ENTERPRISE`, aba 1 |
| Feature nova ou com defeito | **Não.** As 40 features existem desde 2023; a taxa de erro é a mesma (~30%) entre quem cancela e quem fica. Só a feature_10 mostra um sinal fraco de mais erro (13 de 26 registros), a verificar | `DADOS_FEATURE_EVENTS`, abas 5–6 |
| Suporte ruim / reclamações | **Não.** Quem teve churn abre a mesma quantidade de tickets, com a mesma gravidade, os mesmos tempos e a mesma nota | `DADOS_FEATURE_EVENTS`, aba 7 |
| Uso baixo antes de sair | **Não.** Quem tem evento de churn usa igual a quem nunca teve, e continua usando depois do "churn" | `DADOS_FEATURE_EVENTS`, abas 1–2 |
| Um tipo de cliente (indústria, país, canal, tamanho, cobrança) | **Não**, em nenhuma das 22 características testadas | `DADOS_RECONCILIA/02_Triangulacao.xlsx` |
| Motivo registrado no evento de churn | **Não é confiável.** O motivo não bate com o comentário do cliente, e a data do evento fica perto de um cancelamento real tanto quanto uma data sorteada (8% contra 7,6%) | `DADOS_CONSOLIDA_V1/04_Eventos_x_Cancelamento_Real.xlsx` |

**O que é fato e o que é hipótese:**
- **Fato:** as quantidades e valores desta seção e da anterior, tirados da tabela de assinaturas.
- **Hipótese forte, a confirmar com a empresa:** que uma mudança de processo em jul–ago/2024 causou o novo ritmo de compra. Os dados mostram **quando** e **em todos os lugares**, mas nenhuma tabela registra **o que** mudou.
- **Não sabemos:** **por que** as contas Enterprise desligam pacotes. Nenhuma tabela registra isso de forma confiável. A resposta exige conversar com essas contas.

---

## 2. Quais segmentos estão mais em risco?

### 2.1 Contas Enterprise com maior perda real (24 meses)

| Conta | Indústria · País · Canal | Perda real (US$/mês) | Paga hoje (US$/mês) | Último corte |
|---|---|---|---|---|
| A-5a215a | EdTech · FR · other | 34.626 | 69.687 | 30/12/2024 |
| A-f44180 | Cybersecurity · UK · event | 19.502 | 9.286 | 30/10/2024 |
| A-8ae05d | FinTech · IN · other | 17.114 | 9.116 | 28/12/2024 |
| A-180abf | DevTools · US · event | 12.736 | 24.576 | 06/11/2023 |
| A-65aeb5 | DevTools · US · partner | 12.708 | 19.893 | 03/12/2024 |
| A-dbc825 | EdTech · FR · partner | 11.306 | 25.702 | 17/12/2024 |
| A-4c56c9 | FinTech · US · partner | 10.633 | 16.256 | 03/11/2024 |
| A-faa28c | HealthTech · US · organic | 9.552 | 39.300 | 13/10/2024 |
| A-39b19f | FinTech · US · partner | 9.335 | 11.902 | 01/05/2024 |
| A-13466a | DevTools · AU · event | 8.794 | **171** | 31/12/2024 |

- Essas 10 contas respondem por US$ 146 mil dos US$ 424 mil de perda por redução e saída.
- Juntas, ainda pagam cerca de US$ 226 mil por mês. Nove das dez continuam com contratos grandes, então ainda há muito a proteger nelas.
- **Prioridade máxima:** as 4 contas que perderam mais da metade do que pagavam numa única redução e **não recuperaram**:
  - **A-13466a:** a conta encolheu de US$ 8.927 para US$ 171 por mês.
  - **A-f44180:** contrato anual de 89 licenças encerrado com 213 dias.
  - **A-8ae05d:** contrato anual de 86 licenças encerrado com 31 dias. No mesmo mês, a conta abriu uma Enterprise de teste grátis do mesmo tamanho.
  - **A-69fad4.**
- **Detalhes:** `DADOS_CONSOLIDA_V1/01_Contas_Enterprise_Prioritarias.xlsx`.

### 2.2 Outros grupos de risco

- **Contratos anuais encerrados antes de 12 meses:** 79 viraram perda real em 24 meses, somando US$ 164 mil. Outros 36 anuais foram comprados a mais e desfeitos em até 30 dias.
- **Assinaturas nos primeiros 30 dias:** é a fase de maior risco. Uma assinatura nova tem cerca de 5 vezes mais chance de ser encerrada no 1º mês do que depois de 6 meses. Desde jul/2024, 6,1% são encerradas em até 30 dias.
- **Clientes que compram em rajada** (canal orgânico, DevTools, EUA): é risco de processo (compras erradas e desfeitas), não de perda de cliente.
- **Não estão mais em risco:** nenhuma indústria, país ou canal reduz Enterprise com mais frequência de forma confiável. Em US$, os EUA pesam mais (US$ 238 mil de US$ 458 mil das reduções Enterprise) só por terem mais contas Enterprise.

---

## 3. O que a empresa deveria fazer?

Em ordem de prioridade. As ações 1 a 4 atacam a perda e o número de churn; as ações 5 e 6 corrigem as informações para que o problema possa ser medido e explicado daqui em diante. O impacto estimado usa os números de 2024. Os valores são de receita mensal, e cada US$ 1 mil de MRR mantido equivale a US$ 12 mil por ano.

| # | Ação | Como | Impacto estimado |
|---|---|---|---|
| **1** | **Trocar a régua de churn** (nesta semana) | Medir churn pela tabela de assinaturas: separar troca, compra desfeita, redução real e saída. Reportar "clientes perdidos" e "receita perdida" separados | O churn de receita do 4º trimestre de 2024 passa de 14,4% para 5,5% do MRR. Evita tratar como perda US$ 541 mil de MRR que não eram perda, só nesse trimestre, e foca o time no que de fato se perdeu |
| **2** | **Programa de proteção Enterprise** (este mês) | (a) Ligar para as 4 contas prioritárias e para a lista de 10 da seção 2.1. (b) Alerta automático quando uma assinatura Enterprise for encerrada, com contato do CS **antes** de desligar o pacote. (c) Registrar o motivo de cada redução | Perda Enterprise no 4º tri/24: US$ 190 mil de MRR. **Cada 10% evitado ≈ US$ 19 mil de MRR por trimestre (≈ US$ 228 mil por ano).** As 4 prioritárias deixaram de pagar US$ 47 mil por mês |
| **3** | **Descobrir o que mudou no processo de compra em jul/2024 e corrigir** (próximas 2–4 semanas) | Revisar com Produto, Vendas e Financeiro o que entrou em jul–ago/24 (checkout, autoatendimento, integração, campanha). Bloquear compras duplicadas e confirmar compras múltiplas em poucos dias. Começar pelo canal orgânico | No 4º tri/24, 240 de 324 encerramentos (74%) foram trocas ou compras desfeitas. Inclui US$ 168 mil de MRR comprados a mais e desfeitos (possíveis reembolsos) e US$ 103 mil perdidos em trocas por assinaturas mais baratas |
| **4** | **Regra para contratos anuais encerrados antes de 12 meses** (próximo ciclo comercial) | Prazo claro de arrependimento (por exemplo, 7 dias) e, depois dele, cumprimento do contrato ou multa. Conversa de retenção obrigatória antes de encerrar um anual | 79 anuais viraram perda real em 24 meses, somando US$ 164 mil de MRR. Parte dessa receita se mantém pelo prazo restante do contrato |
| **5** | **Motivo de cancelamento obrigatório e claro** (próximo mês) | Ao encerrar qualquer assinatura, o motivo e o comentário passam a ser **obrigatórios**: não podem ficar vazios nem como "unknown". Trocar a lista atual por motivos específicos (ex.: preço, orçamento cortado, funcionalidade que faltou — qual?, problema técnico, atendimento, foi para concorrente — qual?, projeto encerrado, compra duplicada ou por engano, troca de plano). Registrar também o assunto de cada ticket e abrir a pesquisa de satisfação para notas 1 e 2 | Hoje **221 dos 600 eventos de churn (37%) não explicam nada**: 148 sem comentário e 95 com motivo "unknown". Nos demais, o comentário contradiz o motivo. Sem isso, a pergunta "por que as contas Enterprise desligam pacotes?" (ação 2) continua sem resposta |
| **6** | **Tornar a base de dados coerente: alinhar sistemas e modelagem** (projeto do próximo trimestre) | A incoerência mostra que os sistemas (cobrança/assinaturas, cadastro de contas, produto/uso, suporte e registro de churn) não conversam. (a) Tornar a tabela de assinaturas a fonte única: a marcação de churn da conta e o evento de churn passam a ser **gerados a partir do fim real da assinatura**, não preenchidos à parte. (b) Vínculos obrigatórios: evento de churn ligado à assinatura encerrada; plano e licenças da conta calculados das assinaturas ativas; upgrade/downgrade calculados, não marcados à mão. (c) Datas validadas na entrada: nenhum ticket antes do cadastro da conta, nenhum uso fora da vida da assinatura. (d) Um dono para os dados e uma checagem automática mensal com as 28 regras já testadas neste diagnóstico | Hoje 400 das 500 contas têm marcações de churn que se contradizem, 54% dos tickets e 77% dos registros de uso têm datas impossíveis. Enquanto isso não mudar, nenhum indicador de CS ou de produto consegue avisar o churn, e cada análise futura começa reconciliando dados |

---

## Como chegamos aqui

### Qualidade dos dados: o primeiro achado

- **Só a tabela de assinaturas é coerente do começo ao fim.** Valor = licenças × preço do plano; data de fim preenchida = encerrada. Por isso ela é a base das contas deste relatório.
- **As três marcações de churn não concordam entre si.** A marcação na conta, o evento de churn e a assinatura encerrada só batem em 100 das 500 contas.
- **Os eventos de churn não marcam saída e não explicam o motivo:**
  - em 91% deles, a conta estava ativa no dia;
  - a proximidade com um cancelamento real é igual à de uma data sorteada;
  - das 110 contas marcadas como churn, só 43 tiveram perda real;
  - 37% dos eventos não têm motivo útil (comentário vazio ou motivo "unknown").
- **Datas de tickets e de uso estão espalhadas ao acaso:**
  - 54% dos tickets são anteriores ao cadastro da conta;
  - 77% dos registros de uso são anteriores ao início da própria assinatura;
  - o volume é o mesmo em todos os trimestres;
  - as **quantidades** servem; as **datas**, não.
- **A pesquisa de satisfação só tem notas 3 a 5.**

### Como as 5 tabelas foram cruzadas

| Tabelas | Pergunta |
|---|---|
| Assinaturas | Classificação de cada encerramento, perda real em quantidade e US$, ritmo de compra, contas em risco |
| Assinaturas + Contas | Indústria, país, canal e data de cadastro de quem reduz e de quem compra em rajada |
| Uso + Assinaturas + Eventos | Uso e erros de quem teve churn × quem não teve, antes e depois do evento |
| Tickets + Contas + Eventos | Reclamações de quem teve churn × quem não teve; datas dos tickets × cadastro |
| Eventos + Assinaturas | Se cada evento de churn corresponde a um cancelamento real |

### Regras usadas

- **Troca:** outra assinatura da mesma conta até 7 dias antes ou depois.
- **Compra extra desfeita:** até 30 dias de vida, havendo outra mais antiga do mesmo plano.
- **Rajada:** 3 ou mais assinaturas da mesma conta em 7 dias.
- **"Diferença confiável":** testada estatisticamente, com corte de 5% e no mínimo 10 casos. Abaixo disso, tratamos como "pode ser coincidência" ou "poucos casos".

### Limites

- A base é fictícia (gerada por computador). Parte das incoerências pode vir do gerador.
- As janelas de 7 e 30 dias são escolhas da análise. A sensibilidade a outras janelas está em `DADOS_2024_NOV_DEZ/04_Tipos_de_Cancelamento.xlsx`.
- Não encontrar efeito em uma característica significa que **estes dados** não mostram efeito.

---

## Onde conferir cada número

| Assunto | Arquivo (pasta `analise`) |
|---|---|
| Qualidade da base e escolha da fonte | `DADOS_RECONCILIA/01_Evidencias_Consistencia.xlsx`, `02_Triangulacao.xlsx` |
| Trocas, reduções e saídas em nov/dez; mês a mês em quantidade e US$ | `DADOS_2024_NOV_DEZ/04`, `06`, `07` |
| Compra em rajada | `DADOS_2024_NOV_DEZ/05`, `DADOS_CONSOLIDA_V1/03` |
| Enterprise: preço, licenças, features, reclamações, perfil | `DADOS_ENTERPRISE/01_Enterprise_por_Periodo.xlsx` |
| Uso, eventos e tickets: churn × não churn | `DADOS_FEATURE_EVENTS_11_12_2024/01_Uso_Eventos_Tickets.xlsx` |
| Perda real por trimestre (gráfico do CEO) | `DADOS_CONSOLIDA_V1/02_Perda_Real_por_Trimestre.xlsx` |
| Contas prioritárias | `DADOS_CONSOLIDA_V1/01_Contas_Enterprise_Prioritarias.xlsx` |
| Evento de churn × cancelamento real; datas de tickets e uso | `DADOS_CONSOLIDA_V1/04_Eventos_x_Cancelamento_Real.xlsx` |

*Cada planilha tem uma aba LEIA-ME e é gerada por um programa na subpasta `scripts`, que lê os dados originais sem alterá-los.*
