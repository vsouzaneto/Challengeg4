# Benchmark: como as ferramentas de mercado priorizam negócios

Pesquisa feita em 09/10/2026, em documentação oficial (centrais de ajuda, Trailhead, Microsoft Learn), com fontes ao lado de cada ponto.
"⚠" marca o que veio de fonte não oficial ou ficou incerto.
O objetivo não é copiar uma ferramenta. É adotar o que se repete entre elas e cabe nos nossos dados.

## 1. O que cada ferramenta mostra

| Ferramenta | Como o score aparece | Como explica | Negócio parado |
|---|---|---|---|
| Salesforce (Einstein Opportunity Scoring) | 1–99. No Pipeline Inspection, aparece em faixas (High 67–99, Med 34–66, Low 1–33), com seta quando muda de faixa ([Trailhead](https://trailhead.salesforce.com/content/learn/modules/sell-smarter-with-pipeline-inspection/understand-deal-health-with-insights-and-scores)) | Fatores positivos e negativos | Data de fechamento vencida pesa contra; mais de 3 meses vencida → score padrão 5 ([Help](https://help.salesforce.com/s/articleView?id=einstein_sales_opportunity_scoring_how_it_works.htm&language=en_US&type=5)) |
| HubSpot (Deal Score) | 0–100, "percentage probability" ([KB](https://knowledge.hubspot.com/records/use-deal-scores-beta)) | Até 5 "Key factors", com + ou − | "Stalled" quando o tempo na etapa passa 20% da média dos ganhos do responsável ([KB](https://knowledge.hubspot.com/properties/hubspots-default-deal-properties)); visões prontas "Stalled Deals" e "Stale Close Date" |
| Pipedrive | Probabilidade por etapa ou por negócio; "Valor total ponderado" no resumo do funil ([KB pt](https://support.pipedrive.com/pt/article/how-can-i-see-the-total-value-of-my-deals-by-stage-or-pipeline)) | — | "Recurso de estagnação", com ajuste "Estagnação em (dias)" por etapa; o negócio parado fica com "cor vermelha no cartão" ([KB pt](https://support.pipedrive.com/pt/article/the-rotting-feature)) |
| Microsoft Dynamics 365 Sales | 0–100 + nota A–D (verde, roxo, amarelo, vermelho) + tendência (Improving, Declining, Steady, "Not enough info") ([Learn](https://learn.microsoft.com/en-us/dynamics365/sales/work-predictive-opportunity-scoring)) | 5 razões positivas e negativas. O tooltip traz uma frase de coorte: "15% of opportunities with estimated revenue above 19900 are closed as won" | Tempo na etapa comparado ao dos negócios ganhos |
| Gong | 1–99 em faixas Low/Fair/High. É percentil e "neither signifies that the deal has an 80% chance of closing" ([help](https://help.gong.io/docs/explainer-about-deal-likelihood-scores)) | Sinais positivos e negativos | Avisos, entre eles "Stalled in stage" (dias por etapa) e "Overdue" ([help](https://help.gong.io/docs/using-deal-warnings)) |
| Outreach (Deal Health) | 0–100 em "On-track", "Needs review", "At-risk"; recalculado todo dia, com horário da última atualização ([support](https://support.outreach.io/support/solutions/articles/159000426278)) | Fatores + ações recomendadas a partir dos negativos | — |
| Salesloft Rhythm | Lista de ações com "the highest valued action listed first"; prospecção e fechamento em zonas separadas ([PDF](https://salesloft.com/wp-content/uploads/2023/06/Salesloft-Rhythm-for-Sellers-1.pdf)) | "Key Factors" atrás de um ícone | — |
| Agendor (BR) | — | — | "Tempo Limite na Etapa": negócio destacado em alerta, com contador de há quanto tempo está parado ([blog](https://www.agendor.com.br/blog/novidade-tempo-limite-etapa-crm/)) |
| RD Station CRM (BR) | — | — | Filtro de "negociações esfriando" ([blog](https://www.rdstation.com/blog/vendas/novidades-rd-station-crm-outubro-2024/)) |

## 2. Práticas que se repetem e o que adotamos

| # | Prática de mercado | Onde aparece | No nosso app |
|---|---|---|---|
| 1 | Score em 3–4 faixas com nome simples, ordenado pelo número de baixo | Salesforce, Gong, Outreach, Dynamics | Sem rótulo de faixa (alta, média, baixa): a chance aparece como histórico, "X de cada 10" (D28), e a lista é ordenada pelo valor ponderado |
| 2 | Chance e valor lado a lado | Dynamics (bolha), Clari (quadrante) | Cartão mostra chance, valor e valor ponderado |
| 3 | Dizer o que o número significa | HubSpot diz que é probabilidade; Gong diz que não é | O nosso é uma taxa histórica de verdade: "de cada 10 negócios com essa idade, X viraram venda" |
| 4 | Explicação curta, em frase de coorte | Dynamics, HubSpot | É a frase da D5. A Microsoft usa o mesmo formato |
| 5 | "Parado" medido contra quanto tempo os ganhos levam | HubSpot, Dynamics, Gong, Pipedrive | Esfriando a partir de 90 dias; parado depois de 138 (maior ciclo de um ganho) |
| 6 | Visões separadas para negócios com problema | HubSpot "Stalled Deals", avisos do Gong | Listas "Revisar ou encerrar" e "Inicie contato" |
| 7 | Cor sempre com texto ao lado | Pipedrive, Gong, Outreach | Nenhuma informação só por cor |
| 8 | Barra de números no topo, que segue os filtros | Salesforce, Pipedrive, Gong | Negócios em andamento, valor em funil, valor ponderado, esfriando, parados |
| 9 | Visão do gestor com consolidação por vendedor | Gong (Deals/Team), HubSpot | Alternar "Meus negócios" / "Equipe" |
| 10 | Mostrar a data dos dados | Outreach | "Dados de 31/12/2017", com seletor (D1) |
| 11 | Avisar quando há pouco histórico | Dynamics, Gong | Datas sem histórico suficiente bloqueadas, com explicação |
| 12 | Cada alerta com uma próxima ação | HubSpot, Outreach, Rhythm | Texto fixo, por exemplo "Retome o contato ou marque como perdido" |
| 13 | Prospecção separada do funil ativo | Rhythm | Lista "Inicie contato" (D4) |

**Ideia nossa, não vista nas ferramentas:** mostrar o prazo até a próxima mudança de situação: "Esfria em N dias" (90) e "Fica parado em N dias" (depois de 138). A primeira versão desta ideia ("a chance cai de 44% para 33%") foi recusada na D30: os saltos vêm dos limites das faixas, não de uma queda real dia a dia.

**O que não cabe nos nossos dados:**
- Sinais de atividade (e-mail, reunião, ligação, "ghosted").
- Contatos envolvidos.
- Data de fechamento prevista e "atrasada".
- Categorias de forecast (Commit, Best Case), que dependem do julgamento do vendedor.
- Meta e cobertura de funil.
- Histórico do score.

## 3. Vocabulário (pt-BR)

Fontes: centrais de ajuda em português do Pipedrive, HubSpot, Agendor, Ploomes, RD Station e Trailhead.

| Conceito | Rótulo no app | Evidência | Observação |
|---|---|---|---|
| Deal | Negócio | Pipedrive, Agendor, Ploomes, HubSpot | RD usa "negociação"; Salesforce, "oportunidade" |
| Pipeline | Funil | Pipedrive, Agendor, RD | "Pipeline" é aceito em texto de RevOps |
| Stage | Etapa | Pipedrive, Agendor, Ploomes | Não misturar com "fase" ou "estágio" |
| Open | Em andamento | Agendor, RD | |
| Won / Lost | Ganho / Perdido | Agendor, Pipedrive | |
| Won + lost | Concluídos | RD ("Negociações Concluídas") | Nunca "fechado": no HubSpot em português, "Negócio fechado" quer dizer ganho ([KB](https://knowledge.hubspot.com/pt/object-settings/set-up-and-customize-pipelines)) |
| Attention (90–138 d) | Esfriando | RD ("negociações esfriando") | |
| Stalled (> 138 d) | Parado há N dias | Agendor, Pipedrive | |
| Expected value | Valor ponderado | HubSpot, Pipedrive ("Valor total ponderado") | É exatamente valor × probabilidade. Adotado no lugar de "valor esperado" (D11) |
| Win rate | Taxa de ganho | Pipedrive ("taxa geral de ganho"), Agendor | "Taxa de conversão" pode ser confundida com conversão entre etapas |
| Avg. deal size | Ticket médio | Agendor | |
| Sales cycle | Ciclo de vendas | Agendor, Pipedrive | |
| Account | Empresa | Agendor, RD, Pipedrive ("Organizações") | |
| Rep / Manager | Vendedor(a) / Gestor(a) | Agendor, Meetime | Gerente comercial como cargo |
| Forecast | Previsão de vendas | Pipedrive, RD | "Forecast" aceito para gestores |

Ficam em inglês, como no mercado brasileiro: lead, follow-up, pipeline, forecast, SDR, closer, ICP ([Agendor](https://www.agendor.com.br/blog/termos-de-vendas/), [RD](https://www.rdstation.com/glossario/forecast-de-vendas/)).

## 4. Limites desta pesquisa

- Várias páginas da ajuda da Salesforce e da Clari não carregaram; os pontos dessas ferramentas vêm de Trailhead, blog ou comunidade (⚠).
- A ajuda em português da HubSpot é tradução automática.
- Pipedrive e Salesforce usam termos diferentes entre artigos ("etapa"/"estágio").
- Não vimos as telas ao vivo, só a documentação.
