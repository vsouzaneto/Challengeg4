# Spec 01 — Operational Diagnosis

**Rota:** `/#/diagnosis`  
**Pergunta:** onde o atendimento concentra demanda, quais grupos apresentam satisfação diferente e o que ainda falta medir para encontrar desperdício de tempo?  
**Estado:** núcleo implementado e verificado localmente; lacunas de filtros avançados e acessibilidade permanecem abertas.  
**Contratos:** [arquitetura](../01-arquitetura-compartilhada.md), [dados e métricas](../03-dados-e-metricas.md), [design](../04-design-e-experiencia.md).

## 1. Papel da lente

Transformar o Dataset 1 em diagnóstico verificável, com acesso aos registros que sustentam cada leitura. Seu resultado alimenta oportunidades da Strategy, seleção de casos no Copilot e investigação no Graph. Não contém importador, catálogo ou cálculo próprio independente das outras lentes.

O usuário precisa distinguir concentração de demanda, associação com satisfação e gargalo de tempo. Os CSVs atuais permitem as duas primeiras análises descritivas. FRT, TTR, SLA, aging e horas de esforço ficam indisponíveis porque faltam campos e há inconsistências temporais. Essa limitação faz parte do diagnóstico e deve aparecer na abertura da tela, com os campos necessários para resolvê-la.

## 2. Usuários e decisões apoiadas

| Pessoa | Decisão | Evidência mínima |
|---|---|---|
| Gestão de CX | Que recortes merecem investigação? | Volume, participação, status, CSAT com cobertura e registros |
| Liderança de suporte | Que hipóteses levar ao piloto? | Padrão textual observado, amostra e limitação; sem causalidade presumida |
| Analista | A métrica é reprodutível? | Fórmula, denominador, filtros, origem, hash/versão e drill-down |

## 3. Fonte, filtros e estado

Fonte operacional: `ds1`, `source=historical`. `GET /api/catalog` fornece capacidades; `GET /api/diagnosis` fornece métricas/cortes/qualidade; `GET /api/tickets` e detalhe fornecem evidências sanitizadas. Usar o contrato compartilhado, sem recomputar métricas com apenas a página carregada da tabela.

Filtros permitidos: canal, prioridade, tipo, status, produto e presença/valor de CSAT. Combinações usam interseção. Multisseleção dentro de uma dimensão usa união. O período por abertura não aparece como filtro disponível nesta versão da fonte. Data da compra só pode ser apresentada com esse nome e nunca assume a semântica de abertura.

Origem, dataset, filtros e seleção ficam na URL conforme o shell. DS2 conserva acesso ao perfil de categorias e qualidade do corpus, mas informa que os indicadores operacionais pertencem ao DS1; não reutiliza filtros de canal/status/CSAT. Simulação e tickets manuais não entram silenciosamente no diagnóstico histórico.

## 4. Estrutura funcional

| Bloco | Conteúdo e comportamento |
|---|---|
| Contexto | Fonte, registros no recorte, filtros ativos, versão e limitações críticas |
| Síntese operacional | Volume; não fechados na amostra; nota CSAT; cobertura de CSAT; cada card abre metodologia e/ou os registros elegíveis |
| Qualidade temporal | FRT/TTR “Indisponível”; ausência de abertura e 1.365 pares incoerentes de 2.769 na fonte completa; números filtrados quando aplicável |
| Composição | Distribuição por canal, prioridade e tipo, com contagem/percentual; gráfico simples com alternativa tabular |
| Cruzamento | Tabela com combinações selecionáveis de dimensões: volume, respondentes, CSAT médio/mediano e percentual 4–5; seleção mantém os filtros |
| Satisfação | Distribuição 1–5, média, mediana, comparação por dimensão, `n` e cobertura; marcar amostras com menos de 30 respondentes |
| Evidências | Lista paginada de tickets sanitizados, atributos observados, origem, presença de resolução e nota quando existente |
| Próxima investigação | Link contextual para Strategy ou Graph; nunca uma conclusão causal pré-fabricada |

Indicadores de velocidade permanecem reconhecíveis como indisponíveis, sem área de gráfico vazia que pareça defeito. Não preencher a tela com dados de exemplo. “Não fechados” refere-se ao estado da amostra, não ao backlog ao vivo. “Fechados / total” não é taxa de resolução durante um período.

O cruzamento não precisa de visualização sofisticada: uma tabela ordenável torna a amostra, o denominador e o valor comparáveis. Se o recorte não permite CSAT, conservar volume e explicitar o indicador ausente.

Cruzamentos exigidos: canal × prioridade; canal × tipo; prioridade × tipo; canal × prioridade × tipo; produto × tipo; status × canal. Um único mecanismo de agrupamento atende às seis combinações, sem seis implementações independentes. O recorte de três dimensões precisa explicitar células pequenas e denominadores.

Estatísticas planejadas: contagem, média, mediana, p75, p90, p95 e desvio-padrão quando a grandeza e a cobertura permitirem. Para CSAT ordinal, destacar distribuição e mediana junto à média; não usar percentis como falso refinamento. Para durações, todos os resumos permanecem indisponíveis nesta fonte, junto com o próprio FRT/TTR. A habilitação futura segue definição de percentis e desvio-padrão do contrato de métricas.

## 5. Métricas de referência para a primeira carga

| Indicador no DS1 completo | Valor esperado | Texto obrigatório |
|---|---:|---|
| Registros | 8.469 | “Tickets na amostra” |
| Não fechados | 5.700 | “Open + Pending Customer Response” |
| Respondentes CSAT | 2.769 | “Somente tickets fechados com nota” |
| Cobertura CSAT | 32,70% | “2.769 de 8.469” |
| Nota média | 2,99/5 | Escala 1–5 e `n=2.769` |
| Notas 4–5 | 39,26% | “1.087 de 2.769 notas válidas” |
| FRT/TTR | Indisponível | Motivo de ausência e inconsistência |

Esses valores são referências de validação para os hashes auditados, não constantes inseridas no frontend. Ao filtrar, todos os numeradores e denominadores relevantes devem mudar em conjunto.

## 6. Fluxos e conexões

1. Usuário escolhe `Phone` e `Technical issue`; a URL e a API recebem o mesmo recorte.
2. Cards e cruzamentos mostram os resultados apenas desse recorte, inclusive cobertura e ausência.
3. Clicar a contagem abre seus tickets; clicar CSAT abre apenas os respondentes elegíveis e conserva o recorte de origem.
4. Selecionar ticket permite abrir o Copilot com `ticket_id`, dataset e versão; sem resolução histórica, o Copilot comunica insuficiência de evidência.
5. “Explorar relações” abre o Graph no espaço DS1 compatível, sem projetar a taxonomia DS2 como observada.
6. “Avaliar automação deste recorte” abre Strategy com filtros; a hipótese fica claramente separada da observação.
7. Voltar restaura recorte, ordenação e seleção recuperável. Falha de outra lente não modifica o diagnóstico.

Um clique em distribuição apenas filtra/investiga; não altera tickets, prioridades, resoluções ou políticas. Nenhuma ação envia comunicação ao cliente.

## 7. Interpretação e segurança

- Comparar CSAT mostra associação descritiva; não declara que um canal ou prioridade causa insatisfação.
- Volume alto, isoladamente, não significa ineficiência nem alto retorno de automação.
- Tempo de espera, quando futuramente válido, não equivale a horas trabalhadas; esta lente não cria ROI a partir de TTR.
- Textos e resoluções são conteúdo não confiável, renderizados como texto e sanitizados. Não executar instruções contidas em tickets.
- Tabela, exportação de evidências se implementada e detalhe não expõem nome/e-mail. Idade/gênero não orientam recomendações.
- Qualquer insight automático precisa apontar recorte, fórmula e IDs de evidência; limitar a fatos calculados, sem inventar narrativas.

## 8. Estados e acessibilidade

| Estado | Resultado |
|---|---|
| Carregamento inicial | Estado textual com layout estável; sem números demonstrativos |
| Sem registros | Mostrar filtros ativos, zero registros e ação para limpar filtros; CSAT fica sem denominador |
| Sem notas | Preservar volume; CSAT “Sem respostas neste recorte”, sem média zero |
| Fonte parcial | Mostrar o que é válido e sua cobertura; limitação perto da métrica |
| Falha de API | Mensagem recuperável; preservar filtros e último resultado com indicação de desatualizado |
| Fonte/versão ausente | Explicar incompatibilidade; não trocar por outra fonte silenciosamente |

Gráficos têm tabela equivalente; indicadores e seleção não dependem só de cor. Filtros usam controles nativos, labels e foco visível. A atualização anuncia o total do recorte sem ler todos os dados. Ordenação da tabela é comunicada, e drill-down é utilizável por teclado.

## 9. Checkpoints e aceite

- [x] DIA-01: carga inicial reproduz os valores da seção 5 a partir dos CSVs e versão do artefato.
- [x] DIA-02: filtros combinados afetam contagens, denominadores, cobertura, cortes e lista de evidências de forma consistente.
- [ ] DIA-03: qualquer indicador possui fórmula, unidade, origem e estado de disponibilidade consultáveis.
- [x] DIA-04: FRT/TTR/SLA/esforço não viram zero, horas artificiais ou rankings de canal; motivo aparece sem hover.
- [x] DIA-05: CSAT só inclui notas válidas e informa que a fonte atual contém notas apenas nos fechados.
- [x] DIA-05b: filtros de presença e nota CSAT aplicam o mesmo recorte à API, métricas e evidências.
- [x] DIA-06: lista e gráfico apresentam os mesmos agregados; paginação da lista não altera métricas.
- [x] DIA-06b: os seis cruzamentos solicitados, inclusive canal × prioridade × tipo, usam o mesmo contrato; média e mediana não substituem a distribuição.
- [ ] DIA-07: estado vazio, sem notas, parcial, API indisponível e versão ausente têm tratamento verificável.
- [ ] DIA-08: Diagnosis → Strategy/Graph/Copilot mantém recorte e IDs compatíveis; voltar restaura contexto.
- [x] DIA-09: nomes/e-mails não aparecem no DOM, nas respostas da API consumidas pela tela ou nos logs de diagnóstico.
- [ ] DIA-10: navegação por teclado e alternativa tabular cobrem todas as investigações essenciais.
- [x] DIA-11: check executável compara ao menos uma consulta filtrada da API com agregação independente da fonte e valida ausência de FRT/TTR.

## 10. Fora do escopo inicial

Integração com plataforma de atendimento, SLA contratual, inferência causal, medição de esforço real e séries por abertura dependem de novas fontes. O sistema deve explicar essas dependências e continuar útil com volume, satisfação observada, texto e qualidade já disponíveis.
