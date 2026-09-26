# Plano de rastreamento

**Para que serve:** ter, para cada post, o que o arquivo do desafio não tem: custo, clique, venda, público real e o tamanho do creator de uma fonte confiável. Sem isso, nenhuma regra da [estratégia](../solution/03_estrategia.md) pode ser medida e nenhum teste pode ser lido.

- **Ferramentas:** GA4 no site e nas páginas de destino; uma planilha ou tabela para o registro de posts, contratos e auditorias; exportações ou APIs das plataformas para métricas, público e seguidores.
- **Atualizado em:** 25/09/2026.
- **Nomes de evento:** objeto_ação, em minúsculas com sublinhado. Nenhum dado pessoal nas propriedades: creators e patrocinadores entram por um código interno.

## Eventos

| Evento | O que registra | Propriedades | Quando dispara | Decisão que alimenta |
|---|---|---|---|---|
| `post_publicado` | Um post no ar | post_id, data_hora, plataforma, formato, categoria, creator_id, objetivo (alcance, conversa, compartilhamento ou venda), patrocinado, contrato_id, patrocinador_id, categoria_patrocinador, tem_fit, tipo_divulgacao, local_divulgacao, rotulo_parceria_paga, utm_campaign, cupom, teste_id, grupo_do_teste | Quando o post vai ao ar; preenchido pelo time de social | Todas: é a linha-base de cada post |
| `contrato_registrado` | Um acordo de patrocínio | contrato_id, patrocinador_id, creator_id, valor, modelo (fixo, híbrido ou por desempenho), posts_previstos, direito_de_uso_dias, exclusividade | Na assinatura | Custo por post e por venda; R4 (recorrência) |
| `metricas_post_coletadas` | Resultado de um post | post_id, janela (1, 7 ou 30 dias), views, alcance_unico, likes, comentarios, shares, salvamentos, cliques_no_link | Coleta automática 1, 7 e 30 dias depois da publicação | Engajamento, conversa e compartilhamento por objetivo |
| `publico_post_coletado` | Quem viu o post | post_id, parcela por faixa etária, parcela por gênero, parcela por país | Junto com a coleta de 7 dias | Pergunta "qual audiência engaja" (hoje é um rótulo por post) |
| `seguidores_creator_coletados` | Tamanho do creator | creator_id, plataforma, data, seguidores | Toda semana | Faixa do creator confiável; teste H3 |
| `landing_visitada` | Visita vinda de um post | utm_source, utm_medium, utm_campaign, utm_content, pagina | Page view no GA4 com UTM | Cliques por post |
| `compra_concluida` | Venda | pedido_id, valor, cupom, utm_campaign, utm_content | Página de confirmação do pedido | Vendas e custo por venda: métrica principal de H1, H2 e H3 |
| `pesquisa_pos_compra_respondida` | Como o cliente conheceu a marca | pedido_id, resposta (lista fechada, com "creator" e o nome do creator) | Depois da compra | Vendas que o cupom e o último clique não pegam |
| `divulgacao_auditada` | Checagem de um post patrocinado | post_id, data, divulgacao_ok, problema (implícita, só hashtag, sem rótulo, fora do vídeo) | Auditoria semanal | R2; ritual de segunda |

## Convenção de UTM

| Parâmetro | Valor | Exemplo |
|---|---|---|
| utm_source | plataforma | instagram, tiktok, youtube |
| utm_medium | tipo de post | creator_patrocinado, creator_organico |
| utm_campaign | contrato ou campanha | ct0412_skincare_q4 |
| utm_content | post | post_88213 |

Tudo em minúsculas, sem espaço. A lista de UTMs e cupons fica na mesma tabela do registro de posts.

## Conversões

| Conversão | Evento | Contagem |
|---|---|---|
| Venda | `compra_concluida` | Uma por pedido |
| Clique qualificado | `landing_visitada` com UTM de creator | Uma por sessão |

## Primeira semana (o mínimo)

1. Registro de `post_publicado` e `contrato_registrado` numa planilha compartilhada, com os campos acima.
2. UTM e cupom para cada post patrocinado novo; `compra_concluida` com cupom e UTM no GA4.
3. Coleta semanal de `seguidores_creator_coletados` e primeira `divulgacao_auditada` dos posts patrocinados que estão no ar.

Com isso, em duas semanas já dá para calcular custo por venda e a variação real das métricas que define o tamanho dos testes.

## O que cada evento corrige no arquivo do desafio

| Falta no arquivo | Evento que resolve |
|---|---|
| Nenhum custo | `contrato_registrado` |
| Nenhum clique nem venda | `landing_visitada`, `compra_concluida`, cupom |
| Seguidores mudam a cada post do mesmo creator | `seguidores_creator_coletados`, com data e fonte única |
| Público é um rótulo por post, não uma distribuição | `publico_post_coletado` |
| Divulgação sem conferência | `divulgacao_auditada` |

## Qualidade e privacidade

- Antes de valer, conferir cada evento no DebugView do GA4 e em um post de teste.
- Nada de nome, e-mail ou telefone nas propriedades; o pedido liga à venda pelo código.
- Seguir a política de consentimento do site para os eventos do GA4.
