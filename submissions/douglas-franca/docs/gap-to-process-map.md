# Mapa: lacuna do dado → falha de processo (G2 → G4)

> **Tese:** o dataset é o fóssil da operação. O que não está registrado nele é o que a operação não mede. Cada linha abaixo liga um achado de qualidade (DQ) à etapa que deveria produzir o dado, e aponta o campo que resolveria a lacuna.
>
> Rótulos: **[evidência]** = a lacuna está comprovada no arquivo · **[hipótese]** = inferência sobre a operação, a validar com o time.

| Lacuna (DQ) | Etapa da operação | Falha provável | Rótulo | Consequência para o Head de Marketing | Dado/controle que resolve | FP (G4) |
|---|---|---|---|---|---|---|
| DQ-12 sem custo, fee, campaign_id | Contratação de creator/patrocínio | Contrato fechado fora do sistema; valor não vira dado | [evidência] ausência · [hipótese] causa | Impossível dizer se patrocínio paga a conta | `campaign_id`, custo total, fee, produção, mídia | FP-01 |
| DQ-12 sem cliques, conversão, receita | Mensuração de resultado | Só métricas de plataforma são coletadas; o funil de negócio não se conecta ao post | [evidência] ausência | Sucesso medido em vaidade (views/likes) | UTM/cupom por creator, conversões, margem, janela de atribuição | FP-02 |
| DQ-07 creator com vários nomes e tamanhos | Cadastro de creators | Não existe cadastro mestre; cada campanha recadastra | [evidência] | Impossível avaliar histórico de um creator antes de recontratar | Cadastro mestre com ID, handle por plataforma, seguidores datados, auditoria de audiência | FP-03 |
| DQ-04/DQ-05 sem cauda, sem fracasso | Coleta e registro | Posts que fracassam não são registrados, ou a extração normaliza os números | [evidência] padrão · [hipótese] causa | Estratégia construída só com sobreviventes | Extração completa via API, com posts zerados e removidos | FP-04 |
| DQ-06/DQ-15 colunas sem coerência | Integração de dados | Campos preenchidos por fontes diferentes sem chave comum | [evidência] padrão · [hipótese] causa | Cruzamentos (persona × canal) produzem ficção | Contrato de dados com chaves e validação na entrada | FP-04 |
| DQ-10 `content_length` sem unidade | Briefing e produção | Formato e duração não são especificados de forma padronizada | [evidência] | Impossível aprender qual duração funciona | `duration_seconds` (vídeo), `word_count` (texto), `slides` (carrossel) | FP-05 |
| DQ-11 hashtags e descrições sem semântica | Briefing e publicação | Texto não é registrado a partir do post publicado | [evidência] | Não há como aprender com mensagem, gancho ou CTA | Captura do texto publicado + taxonomia de tema, gancho e CTA | FP-05 |
| DQ-09 cadência fixa | Planejamento de pauta | Cadência não é uma variável planejada nem testada | [evidência] | "Postar mais" não tem base | Calendário com cadência planejada vs realizada | FP-06 |
| DQ-14 sem fuso, publicação 24h uniforme | Publicação | Horário não é registrado com fuso nem intencionalidade | [evidência] | Melhor horário é chute | `published_at` com fuso + horário planejado | FP-06 |
| DQ-13 audiência agregada por post | Pesquisa de audiência | Só o resumo da plataforma é guardado, e sem distribuição | [evidência] | Persona é inferida sem base | Distribuição de audiência (% por faixa) por post e por creator | FP-07 |
| Nenhuma hipótese registrada (todas as colunas) | Decisão e aprendizado | Decisões não ficam registradas antes do resultado | [hipótese] | Leitura oportunista: sempre há um "vencedor" | Pré-registro: hipótese, métrica primária, MDE, break-even, grupo de controle | FP-08 |
| Critério de escolha do patrocínio não registrado | Desenho de campanha | Não se documenta por que um post foi patrocinado nem qual é o comparador | [evidência] ausência do campo · [hipótese] causa. Obs.: no arquivo, patrocinados e orgânicos estão balanceados como num sorteio (seguidores médios 499.924 vs 499.855; V plataforma = 0,013), algo que uma operação real só teria com desenho deliberado | Sem saber o critério, qualquer comparação real fica confundida | Registro do critério de seleção + randomização ou rollout escalonado por creator elegível | FP-08 |

## Resumo para o G4
**8 pontos de falha** (FP-01 a FP-08) distribuídos pelo ciclo inteiro, da contratação à decisão. Todas as **lacunas** têm evidência direta no arquivo; as **causas** operacionais são hipóteses a validar com o time no G4.
