# 02 — Estratégia: como decidir sobre conteúdo e patrocínio quando o dado não responde

O Head pediu três coisas: o que gera engajamento, se vale patrocinar, e qual a estratégia. Com o dataset atual, as duas primeiras não têm resposta honesta (ver documento 01). A terceira tem — e começa por **mudar a pergunta de "o que os dados dizem" para "como fazer os dados dizerem algo em 30 dias"**.

Escrevo isso com a experiência de quem gerencia as redes de um grupo de franquias de alimentação em Belo Horizonte, com várias lojas, parcerias com criadores locais e um time enxuto. Lá, a métrica que importa não é like: é cliente na loja e pedido no delivery. Essa lente guia tudo abaixo.

## O que fazer na segunda-feira (prioridade decrescente)

### 1. Congelar decisões baseadas neste dataset — e dizer isso por escrito
Nenhuma realocação de verba, nenhum "vamos focar em TikTok", nenhum corte de plataforma pode citar esta base. Custo: zero. Risco evitado: gastar meses otimizando para ruído. Entregável: um parágrafo no report semanal explicando o porquê (os cinco testes do documento 01 cabem em meia página).

### 2. Consertar a instrumentação (semanas 1–2)
O problema real do time não é falta de estratégia, é falta de dado que conecte post → resultado. Esquema mínimo por post, exportado das APIs nativas (Meta, TikTok, YouTube) e consolidado em uma planilha ou tabela:

| Campo | Por quê |
|---|---|
| `creator_id` estável + followers **na data do post** | Para faixa de influenciador fazer sentido |
| formato, duração, pilar de conteúdo, gancho dos 3 primeiros segundos | São as variáveis que o time controla |
| reach, impressões, **saves**, watch time / retenção, cliques no link | Engagement rate sem reach e saves é vaidade |
| `is_sponsored`, **custo** (cachê + mídia paga), tipo de disclosure | Sem custo não existe "vale a pena" |
| conversão atribuível (cupom, UTM, pedido, visita) | É o que o negócio paga |
| posts com engajamento zero e posts excluídos | Contra viés de sobrevivência |

Isso é o que o dataset do challenge finge ter e não tem. Quick win: automatizar o export semanal (Meta Business Suite e TikTok exportam CSV; um script de 50 linhas consolida).

### 3. Política de patrocínio por experimento, não por benchmark (semanas 2–4)
"Vale a pena patrocinar?" só se responde controlando o que a comparação ingênua ignora: plataforma, faixa de creator, categoria e **custo**. Desenho mínimo que cabe em um mês:

- **Mesmo briefing** de conteúdo entregue a 3 faixas de creator (micro <50K, médio 50–250K, macro >250K), 2 por faixa, na plataforma principal da marca.
- **Grupo de controle**: o mesmo conteúdo publicado organicamente no perfil da marca na mesma semana.
- **Métrica pré-registrada** (decidida antes de rodar): custo por engajamento qualificado (saves + comentários + cliques) e custo por conversão atribuível. Não "engagement rate".
- **Regra de decisão escrita antes**: um creator continua se o custo por conversão ficar abaixo do custo da mídia paga equivalente. Threshold de followers não é critério de entrada; custo por resultado é.

Na minha experiência com food service local, micro-criadores de bairro com audiência geograficamente coincidente com a loja costumam converter melhor por real investido do que perfis grandes com audiência dispersa — mas isso é hipótese a testar na empresa do Head, não resposta. O desenho acima é o que separa hipótese de política.

### 4. Ferramenta de acompanhamento com portão de sinal (entregue, `dashboard/index.html`)
O pedido "me dá uma ferramenta pra acompanhar no dia a dia" foi atendido com uma condição: a ferramenta **se recusa a mostrar ranking de segmentos quando o dado não sustenta**. Ela recebe o CSV do export, roda quatro verificações (teste de permutação por dimensão, replicação split-half do ranking, dispersão de views, consistência de creator) e só libera o painel de performance se passar. Em dados reais com sinal, libera e mostra médias com intervalo de confiança por plataforma × patrocínio, tipo, categoria e faixa de creator. Foi testada nos dois cenários (screenshots na pasta).

Isso resolve o problema recorrente de time de social: alguém abre o dashboard, vê "TikTok 20,1% vs Instagram 19,9%" e muda a pauta. O portão transforma a conversa de "qual número é maior" para "esse número é confiável".

### 5. O que parar de fazer
- Parar de reportar engagement rate médio por plataforma como KPI de decisão. Reportar custo por resultado e reach por pilar de conteúdo.
- Parar de contratar influenciador por faixa de seguidores. Contratar por teste pequeno com métrica de conversão.
- Parar de postar "em 5 plataformas igualmente" sem evidência (o único dado real do dataset é que o esforço está pulverizado 20/20/20/20/20). Concentrar onde a audiência da marca está, medir, expandir.

## Cadência depois dos 30 dias
Mensal: rodar o portão de sinal no export do mês. Trimestral: ranking de segmentos só vira estratégia se se repetir em dois trimestres seguidos. Semestral: revisar a política de patrocínio com os testes acumulados.

## Riscos e limitações desta recomendação
- Não tenho os dados reais da empresa, o custo dos patrocínios nem o objetivo de negócio (awareness, lead, venda). O plano é um método, calibrado com experiência de outro setor; os thresholds precisam ser definidos com o Head.
- O portão de sinal foi calibrado com o dataset do challenge (ruído) e com um CSV sintético com sinal plantado. Em dados reais, os limiares (r > 0,5; CV > 30%) devem ser revisados após o primeiro mês.
- Benchmarks públicos de engajamento por plataforma existem, mas deliberadamente não os usei como base: seriam "opinião de terceiros" substituindo "dado da empresa", exatamente o que o Head disse não querer.
