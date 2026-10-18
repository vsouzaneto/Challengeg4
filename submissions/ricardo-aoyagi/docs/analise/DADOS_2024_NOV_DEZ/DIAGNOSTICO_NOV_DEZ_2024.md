# Diagnóstico do churn de nov/dez de 2024: o que é perda de verdade

*Versão preliminar, baseada nas planilhas 01 a 08 desta pasta. Os CSVs originais não foram alterados. Usa como base a tabela de assinaturas, a única confiável (ver `DADOS_RECONCILIA`).*

---

## Resumo

1. **Nenhum cliente foi embora em nov/dez.** As 266 assinaturas encerradas no período aconteceram em contas que continuaram clientes. Na base inteira, nenhuma conta termina 2024 sem assinatura ativa.
2. **O "churn" de hoje mistura três coisas diferentes:**
   - **migração**: a conta encerra uma assinatura e abre outra em até 7 dias. Não é perda;
   - **redução**: a conta encerra uma assinatura sem repor. Há perda de receita, mas não do cliente;
   - **cancelamento real**: a conta fica sem nenhuma assinatura.
3. **Em dinheiro, a perda real de nov/dez é cerca de 2/3 do número de hoje:** US$ 482 mil por mês de MRR, contra US$ 762 mil no "churn" atual. Nos 24 meses, a perda real é de US$ 718 mil, contra US$ 1,18 milhão.
4. **O cancelamento "rápido" (menos de 30 dias) nasce na contratação, não na insatisfação.** Contas novas compram várias assinaturas de uma vez ("em rajada") e logo desfazem parte delas. Quase sempre é migração.
5. **A perda real está concentrada em reduções de assinaturas Enterprise.** Não é porque o Enterprise reduz mais: ele reduz na mesma frequência dos outros planos, mas cada assinatura vale muito mais.
6. **Reclamações, erros e satisfação não avisam o churn.** Quem cancela rápido quase nunca abriu ticket antes, erra tanto quanto quem fica, e a pesquisa de satisfação só registra notas 3, 4 e 5.

---

## 1. O que olhamos

| Fonte | O que é | Nov/dez 2024 |
|---|---|---|
| Assinaturas encerradas (confiável) | Assinatura com data de fim no período | 266 assinaturas (73 em nov, 193 em dez) |
| … rápidas | Menos de 30 dias de vida | 159 |
| … lentas | 30 dias ou mais | 107 |
| Eventos de churn (pouco confiável) | Registros com motivo e comentário | 185 eventos (49 de contas com menos de 30 dias) |

As duas fontes quase não se sobrepõem. Só **21 contas** aparecem nas duas como "churn rápido".

---

## 2. Passos que seguimos

| # | Pergunta | Planilha |
|---|---|---|
| 1 | Existe um caminho perfil → reclamação → feature com erro → cancelamento rápido? | `01_Churn_NovDez_Padroes.xlsx` |
| 2 | Seats, cobrança (anual/mensal), plano ou país mudam o cancelamento rápido? | `02_Cobranca_Plano_Pais_Seats.xlsx` |
| 3 | O que aconteceu, caso a caso, nas 21 contas em que as duas fontes concordam? | `03_Casos_21_Contas.xlsx` |
| 4 | Cada encerramento foi migração, redução ou saída do cliente? | `04_Tipos_de_Cancelamento.xlsx` |
| 5 | As marcações de upgrade/downgrade batem com o plano e os seats? Existe compra em rajada? Onde? | `05_Upgrade_Downgrade_e_Rajadas.xlsx` |
| 6 | Quanto de MRR saiu de fato em nov/dez? | `06_Valores_por_Tipo.xlsx` |
| 7 | Mês a mês (jan/23–dez/24): ingressantes, normais, migrados, reduções e cancelados, em quantidade e em US$ | `07_Grafico_Mensal_Clientes.xlsx` |
| 8 | Os planos usam features diferentes? O Enterprise reduz mais? Algum segmento do Enterprise reduz mais? | `08_Plano_Features_Reducao_Enterprise.xlsx` |

---

## 3. O que encontramos

### Não há trilha de reclamação ou erro antes do cancelamento rápido (planilha 01)
- **Ticket:** 87% das assinaturas rápidas (139 de 159) foram canceladas **sem nenhum ticket** nos 30 dias anteriores. A proporção de contas com ticket em nov/dez é igual entre quem cancela e quem fica (cerca de 3 em 10).
- **Erro:** quem cancela rápido erra tanto quanto quem fica. Cerca de 31% dos registros de uso têm erro nos dois grupos.
- **Perfil:** indústria, plano, cobrança, trial e país não diferenciam. O canal orgânico aparece um pouco acima, mas a outra fonte aponta outro canal.
- **Satisfação:** a pesquisa só tem notas 3, 4 e 5, e cerca de 41% dos tickets ficam sem nota. Do jeito que está, ela não consegue mostrar um cliente insatisfeito.

### Seats e cobrança não explicam (planilha 02)
- **Seats:** todas as faixas ficam entre 3 e 4,5 cancelamentos rápidos a cada 100 assinaturas.
- **Cobrança:** anual 3,8 contra mensal 2,9 a cada 100. É um indício fraco, pode ser coincidência, e os eventos de churn apontam o contrário.
- **Ponto de atenção:** 89 assinaturas **anuais** foram canceladas com menos de 30 dias, o que sugere arrependimento logo após a compra e possível reembolso.

### Os casos mais "limpos" não são saída de cliente (planilha 03)
- As 21 contas continuam clientes, com cerca de 8 assinaturas ativas cada.
- **Todas** as 27 assinaturas canceladas rápido nessas contas tiveram uma assinatura nova da mesma conta em até 7 dias.
- Dos 88 tickets dessas contas, 82 têm data **anterior à existência da conta**, o que é impossível.

### O "churn" de nov/dez é migração e redução, não saída (planilha 04)

| Tipo | Assinaturas | % |
|---|---|---|
| Migração (troca/ajuste) | 156 | 59% |
| Redução | 110 | 41% |
| Saída do cliente | 0 | 0% |

- Nas rápidas, 67% são migração.
- As trocas vão para os dois lados: plano acima, abaixo ou igual; seats e cobrança mudando nos dois sentidos.

### Marcações de upgrade/downgrade não são confiáveis; a rajada é coisa de período e de conta nova (planilha 05)
- **Upgrade/downgrade:** uma assinatura marcada como "upgrade" sobe de plano e/ou seats tanto quanto uma sem marcação (59% contra 54%). Há 73 marcações na **primeira** assinatura da conta.
- **Rajada (3 ou mais assinaturas em 7 dias):**
  - quase 3 em cada 10 assinaturas do 4º trimestre de 2024 entram em rajada, contra menos de 1 em 20 até junho;
  - acontece sobretudo em contas novas;
  - fica um pouco acima da média em DevTools e no canal orgânico, mas aparece em todos os segmentos.
- **Rajada e cancelamento:** das assinaturas compradas em rajada e encerradas em nov/dez, **81% foram canceladas rápido e 90% foram migração**.

### Em dinheiro (planilhas 06 e 07)

| | Nov/dez 2024 | Jan/23 – dez/24 |
|---|---|---|
| "Churn" de receita como contado hoje | US$ 761.755 | US$ 1.179.139 |
| Reposto em assinaturas novas nas migrações (não é perda) | ≈ US$ 280 mil | US$ 460.780 |
| **Perda real** | **≈ US$ 482 mil** | **US$ 718.359** |
| … redução | US$ 339.472 | US$ 580.593 |
| … cancelamento real | US$ 0 | US$ 23.406 (4 casos, todos voltaram depois) |
| … saldo das migrações (troca por assinatura mais barata) | ≈ US$ 142 mil | US$ 114.360 |

- Em nov/dez, a carteira cresceu de US$ 7,10 milhões para US$ 10,16 milhões de MRR ativo.
- Sobre o MRR de 01/11, o "churn" de hoje equivale a 10,7%; a perda real fica em torno de 6,7% a 6,8%.
- Nos 24 meses, só US$ 40 mil do reposto aparecem em "Ingressantes". O restante são assinaturas novas de clientes antigos, então não há dupla contagem.

### Onde está a perda: Enterprise (planilhas 06 e 08)
- As reduções de assinaturas **Enterprise** respondem por **US$ 458 mil dos US$ 581 mil** de redução em 24 meses (78%).
- O Enterprise **não reduz com mais frequência**. São cerca de 5 reduções a cada 100 assinaturas em todos os planos (Basic 4,9 · Pro 4,8 · Enterprise 5,2). A diferença é o valor de cada assinatura (US$ 199 por seat, contra 49 e 19).
- Os planos usam as **mesmas features** na mesma proporção e erram na mesma proporção. Não há feature "do Enterprise".
- Dentro do Enterprise, nenhuma feature, país, canal, indústria, cobrança ou faixa de seats reduz mais de forma confiável.
  - Só a feature_39 tem mais erro nas reduzidas, com apenas 10 casos.
  - Canadá e Índia aparecem abaixo da média, e Austrália, Alemanha, França e Reino Unido acima, sem segurança.

---

## 4. Exemplos

- **Conta A-0b0d6d (rajada):** cadastrou-se em 30/12/2024, abriu 13 assinaturas entre 30 e 31/12 e cancelou 2 delas no dia 31. Hoje isso entra como 2 "churns"; na prática, é ajuste de contratação.
- **Conta A-0354fe:** abriu 7 assinaturas em novembro e dezembro, todas com 34 seats, e cancelou uma Basic 4 dias depois de abrir. Segue cliente, com 6 assinaturas ativas.
- **Conta A-18793f:** abriu 11 assinaturas de 148 seats entre 19 e 30/12 e cancelou uma em 29/12, com 9 dias de vida. Registrou evento de churn com motivo "support", mas os 5 tickets da conta têm datas de 2023, antes de ela existir.

As linhas completas estão na aba *Linha_do_tempo* de `03_Casos_21_Contas.xlsx`.

---

## 5. O que isso significa (preliminar)

- **O aumento de churn que preocupa o CEO é, em boa parte, efeito de como o churn é contado.** Migrações e ajustes entram como perda.
- **A perda real existe e vem de reduções de contrato,** sobretudo em assinaturas Enterprise. Esse é o ponto a investigar a fundo.
- **O processo de contratação precisa de atenção.** Compras em rajada seguidas de cancelamento em poucos dias indicam pedidos duplicados, configuração errada ou teste de planos.
- **Os indicadores atuais não avisam o churn.** Tickets, erros e satisfação não se movem antes dos cancelamentos, e a pesquisa de satisfação não registra notas baixas.

---

## 6. Limites

- A base é **fictícia** (gerada por computador). Parte das incoerências pode vir do gerador.
- As regras de "migração" (até 7 dias) e "rajada" (3 ou mais assinaturas em 7 dias) são escolhas da análise. Parte das migrações pode ser compra independente; a sensibilidade está na planilha 04.
- As datas de uso e de tickets não são confiáveis, por isso o uso foi ligado à assinatura sem olhar a data.
- Os números de nov/dez podem variar alguns milhares de dólares entre as planilhas 06 e 07. A 07 conta cada assinatura nova uma única vez no período todo e é a referência.
