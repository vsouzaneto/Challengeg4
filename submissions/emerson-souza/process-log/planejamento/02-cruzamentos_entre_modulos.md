# Cruzamentos entre módulos (o "cooperativo")

Cada linha responde: **se eu tenho os dados do módulo A, o que o módulo B consegue fazer com eles?** O selo segue a regra de honestidade do [`01-NUCLEO_DO_SISTEMA.md`](01-NUCLEO_DO_SISTEMA.md).

> 🟢 dado real ligado · 🟡 proxy calculado · 🔵 hipótese configurável pelo usuário

---

## Partindo dos dados de CHURN (RavenStack: contas, assinaturas, uso, tickets, cancelamentos)

| Para | O que faz | Selo | Por quê / limite |
|---|---|---|---|
| **Suporte** ⭐ | Pega as contas em risco com sinal de suporte (ticket escalado, resposta lenta, satisfação baixa) e roda o diagnóstico de suporte **só nos tickets delas**: gargalo por prioridade, tempo de 1ª resposta, resolução, escalonamento, satisfação, horas desperdiçadas. Propõe a régua de atendimento para esse grupo. | 🟢 | `support_tickets` tem `account_id`. **Limite:** esses tickets **não têm texto**, então o classificador de texto do 002 não se aplica aqui, só a parte operacional. |
| **Leads (valor da conta)** | Responde *"vale a pena manter este cliente?"*: score de **valor** (MRR, assentos, plano, upgrades, tempo de casa) × score de **risco** → matriz *Salvar agora / Nutrir / Monitorar / Deixar ir*, com explicação, usando a mesma lógica explicável do 003. | 🟢 | Tudo sai das tabelas da RavenStack. |
| **Mídia** | Entrega o **perfil dos segmentos** (indústria, canal de aquisição, país, plano) que mais cancelam e dos que mais ficam, para o módulo de mídia usar como público de campanha de retenção/aquisição e para apontar canais de aquisição que trazem cliente errado. | 🔵 | O dataset de social **não tem** as contas da RavenStack; o que passa é um **perfil de público**, não uma lista de pessoas. |

## Partindo dos dados de SUPORTE (002: tickets com métricas + texto)

| Para | O que faz | Selo | Por quê / limite |
|---|---|---|---|
| **Churn** | **Risco de churn por experiência de suporte**: clientes com satisfação baixa, tickets repetidos, resolução longa, ticket aberto/pendente → lista de clientes para retenção. | 🟡 | Não existe cancelamento nesses dados. É um sinal indireto, mostrado como tal. |
| **Leads** | Tickets do tipo **Product inquiry** (pergunta sobre produto) viram **oportunidades para vendas**, priorizadas por produto e canal. | 🟡 | O ticket é real; tratar como lead é regra de negócio. |
| **Mídia** | Canal "Social media" como canal de atendimento: volume, tempo e satisfação versus outros canais → pauta para o time de social. | 🟡 | Métrica real, uso como pauta é interpretação. |

## Partindo dos dados de LEADS (003: contas, produtos, vendedores, pipeline)

| Para | O que faz | Selo | Por quê / limite |
|---|---|---|---|
| **Churn** | **Carteira pós-venda**: contas com deals ganhos (valor, produto, setor) viram a base que o módulo de churn monitoraria. Mostra concentração de receita e dependência de poucas contas. | 🟡 | Não há cancelamento no CRM, então não dá para medir churn, só preparar a base e o risco de concentração. |
| **Suporte** | Deals ganhos recentes → lista de **onboarding** prioritário para o suporte/CS (maiores valores primeiro). | 🟡 | Regra de negócio sobre dado real. |
| **Mídia** | **Setores e produtos que mais fecham** → onde concentrar conteúdo e patrocínio. | 🔵 | Setor do CRM ↔ categoria de conteúdo é um mapeamento que o usuário define. |

## Partindo dos dados de MÍDIA (004: posts, criadores, patrocínio, audiência)

| Para | O que faz | Selo | Por quê / limite |
|---|---|---|---|
| **Leads** | **Perfil de audiência que mais engaja** (idade, gênero, local, plataforma, categoria) → critério extra para priorizar contas/segmentos no lead scorer ("onde podemos atacar"). | 🔵 | Não há leads individuais no social; passa um perfil. |
| **Churn** | Perfis que engajam pouco com o conteúdo da marca → hipótese de segmentos com baixa afinidade. | 🔵 | Hipótese fraca: usar com cuidado, e dizer isso. |

---

## Prioridade de construção dos cruzamentos

1. ⭐ **Churn → Suporte** (🟢, é o exemplo-âncora do Emerson e é 100% real)
2. **Churn → Leads (vale a pena manter?)** (🟢)
3. **Suporte → Churn (risco por experiência)** (🟡)
4. **Suporte → Leads (product inquiry vira oportunidade)** (🟡)
5. **Leads → Mídia** e **Mídia → Leads** (🔵, com o mapeamento editável na tela)
6. Demais

## Como o cruzamento aparece para o usuário

No fim de cada análise: bloco **"Usar este resultado em outra ferramenta"** → botões só dos módulos compatíveis, cada um com o selo e **uma frase explicando o que vai acontecer** e o limite. Clicar abre uma **sub-sessão** ligada à original.
