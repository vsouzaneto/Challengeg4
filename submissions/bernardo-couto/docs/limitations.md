# Limitações — o que a ferramenta não faz, por quê, e o que faltaria para escalar

**Para:** Head de RevOps e avaliadores · **De:** tech-writer, consolidando `docs/revops-review.md`, `docs/scoring-logic.md`, `docs/ml-pipeline.md`, `docs/data-quality-report.md` e `docs/security-review.md` · **Data de referência dos dados:** 2017-12-31.

Cada número abaixo cita o arquivo que o produziu. Nada aqui foi estimado à mão.

## 1. O que a ferramenta não faz (e diz isso na tela)

Lista exibida na primeira abertura da fila e no rodapé da tela Qualidade (`docs/revops-review.md` §3d).

| # | Não faz | Por quê |
|---|---|---|
| 1 | **Não prevê se um deal vai fechar.** Ordena por valor esperado e momento do ciclo. | Nos dois cortes de backtest nenhum critério — agente, produto, setor, conta, idade, carga ou o modelo estatístico — acertou mais que o acaso (AUC-ROC 0,44–0,53; `solution/models/2017-12-31-rules-v1/model_card.md` §5). |
| 2 | **Não sabe nada fora do CRM**: e-mails, reuniões, propostas, concorrência, decisor. | O dataset tem uma só marca temporal por deal aberto (`engage_date`); não há data de última atividade (`docs/data-quality-report.md`, "Limitações do dado"). |
| 3 | **Não decide encerrar um deal.** Diz "nenhum deal fechou depois de 138 dias"; quem confirma e encerra é o vendedor, no CRM. | A ação `closed_in_crm` do feedback é registro local, sem integração (`solution/api/README.md`). |
| 4 | **Não avalia vendedores.** Taxa de fechamento aparece como contexto, sem peso e sem ranking. | Diferença de 55–70% entre vendedores não se repetiu fora do período medido (AUC-ROC 0,493 fora do tempo; `solution/pipeline/analysis/00_hypotheses.md`, H2). |
| 5 | **Não usa `close_value` nem `close_date`** dos deals abertos. | Só existem depois do desfecho: seria leakage. O hook `guard_leakage.py` bloqueia em código. Valor esperado vem do preço de tabela × razão histórica × taxa do produto. |
| 6 | **Não muda o score com base na conta** (setor, porte, histórico). | 68,2% dos abertos não têm conta (`docs/data-quality-report.md`) e, quando têm, isso não previu fechamento (H7, H10 refutadas). |
| 7 | **Não usa fim de trimestre por deal.** | O padrão observado é de registro de Lost, não de fechamento; possível artefato do dataset (`docs/revops-review.md` §3b). `QUARTER_END_WINDOW` não existe no enum. |
| 8 | **Não funciona com dados de hoje.** Toda idade é contada até `as_of` (31/12/2017). | Snapshot único; nenhum código usa relógio real (hook bloqueia `today()`/`current_date()`). |

## 2. Limites do dado

| Limite | Evidência | Efeito na ferramenta |
|---|---|---|
| **Prospecting sem data alguma** (500 deals) | `docs/data-quality-report.md`, "Estágios, datas e nulos" | Urgência "desconhecida" (0,5); score vem só do valor; barrados do tier A sem conta; fora do backtest. Concentrados em poucos vendedores (máximo 111 num só; `docs/revops-review.md` §4, lacuna 6) — provável lista importada. |
| **68% sem conta é artefato temporal, não atraso de preenchimento** | Fração com conta ≈ 0,3 em todo mês de engajamento (0,21–0,54, sem tendência); 100% dos deals fechados têm conta vs 32% dos abertos (`docs/data-quality-report.md`, "`account_known` é um artefato temporal") | `account_*` proibido como feature: prevê "já fechou", não "vai fechar". Conta entra só em `confidence` e nos reason codes. |
| **Sem dados de atividade** | Nenhuma coluna de contato, reunião ou proposta | "Parado há 150 dias" e "falei ontem" são indistinguíveis. É a lacuna que mais limita o score (`docs/revops-review.md` §4, lacuna 1). |
| **Snapshot único de 2017** | `close_date` de 2017-03-01 a 2017-12-31; `engage_date` desde 2016-10-20 | Deals rápidos engajados antes de março/2017 não existem no dado (truncamento); conta e estágio em cortes passados são anacrônicos; não há como validar o efeito de calendário. |
| **81% do pipeline Engaging passou do ciclo máximo histórico** | 1.291 de 1.589 acima de 138 dias; R$ 3.185.048 nominais vs R$ 692.670 dos 298 vivos (`solution/data/gold/scores/as_of=2017-12-31/_manifest.json`) | A primeira quinzena de uso é limpeza de CRM, não venda. Marcar os 1.291 como Lost derruba o win rate acumulado de 63% para 53% (`docs/revops-review.md` §7). |
| **Base pequena em alguns cruzamentos** | GTK 500: 25 deals fechados; 17 pares agente×produto com menos de 10 (`docs/data-quality-report.md`) | Suavização bayesiana (a = 20); textos avisam "amostra pequena" abaixo de 30. |
| **Dataset possivelmente sintético** (Kaggle, CC0) | Uniformidade do dia de fechamento dentro do mês; Lost quase ausente em mês de fim de trimestre (`docs/revops-review.md` §3b) | Padrões de calendário foram avaliados e ficaram fora do score. |

## 3. Limites do modelo

| Limite | Evidência | Consequência |
|---|---|---|
| **Camada 2 (regressão logística) não promovida** | AUC-PR 0,628 / 0,582 vs 0,661 / 0,600 da taxa-base; Brier 0,273 / 0,276 vs 0,235 / 0,243 (`solution/models/2017-12-31-rules-v1/metrics.json`, `promotion`) | `blend_model_weight = 0`. O score é só regras. O modelo é treinado e versionado a cada `train` para provar, a cada retreino, se isso continua verdade. |
| **Com `regParam = 0,1` a elastic-net zera todos os coeficientes** | `docs/ml-pipeline.md` §4 | Prova direta de que as features não carregam sinal. O pipeline usa 0,01 para o sombra não ser degenerado; a decisão de promoção não muda. |
| **Viés do frame temporal e da calibração isotônica** | Meses recentes só têm deals rápidos: taxa de Won no treino 0,66 vs 0,60–0,63 fora do tempo; isotônica no último mês piora o Brier (`docs/ml-pipeline.md` §8; model card §6) | Reponderação temporal é questão aberta. |
| **`p_win` é a taxa do produto (60–65%)**, igual para todo deal do mesmo produto | `docs/scoring-logic.md`, "Componentes e pesos" | A UI diz "Fecham {p}% dos {product}", nunca "probabilidade deste deal". |
| **Fator 0,5 para deals parados é convenção, não estimativa** | Nenhum deal fechou depois de 138 dias; n = 0 para calibrar (`docs/scoring-logic.md`, Limitações 7) | Em deals parados a UI mostra "sem histórico de fechamento nesta idade" em vez do número. |
| **Alertas de PSI são esperados no snapshot** | PSI > 0,2 em `log_days` (6,13), `survival_rate` (4,05), `product_rate` (3,71), `open_load` (0,58) (`_manifest.json`, `psi`) | Diferença de população (treino = deals que fecharam; lote = 81% parados + 500 Prospecting), não bug. Reforça o modo sombra. |
| **Receita capturada no top 20% fica abaixo de "ordenar por preço"** | 0,376 / 0,359 vs 0,497 / 0,489 (model card §5) | Custo assumido de dizer *quando* agir e de demover parados. Peso 25/50/25 daria Spearman 0,93 com preço — lista de preços (`docs/revops-review.md` §3a). |
| **Métricas do protótipo pandas e do pipeline Spark diferem na 2ª–3ª casa** | `docs/ml-pipeline.md` §8 | Ordem das linhas muda a semente efetiva do bootstrap e o desempate. Os números oficiais são os de `metrics.json`. |

## 4. Segurança e risco de modelo (`docs/security-review.md`)

| Item | Estado | O que seria necessário em produção |
|---|---|---|
| **Sem autenticação nem autorização** (M1) | Aceito para o protótipo local; qualquer cliente lê o pipeline inteiro e grava feedback com `actor` autodeclarado | SSO (OIDC) na borda, `actor` derivado do token, filtro por papel (vendedor vê o próprio recorte; manager vê o time), rate limit em `POST /feedback`. |
| **Exposição do desempenho individual** | `/agents`, `/pipeline/summary`, reason codes `AGENT_*` com números | Score não é métrica de avaliação de pessoas nem insumo de remuneração; visão de manager ordenada por valor parado, sem coluna de posição; intervalos de confiança antes de qualquer comparação. |
| **Campos manipuláveis pelo vendedor** (`product`, `engage_date`, `deal_stage`, `account`, carteira, feedback) | Tabela de gaming em `docs/security-review.md`, "Gaming do score" | Monitorar troca de produto por deal, deals recriados em < 30 dias, taxa de `discard`; nenhuma ação do feedback vira label sem validação externa. |
| **LGPD** | Dados do challenge são públicos e sintéticos | Em CRM real: nomes de vendedores e managers são dados pessoais; base legal com teste de balanceamento; minimização na API; retenção do `actions.parquet`; access log sem query string; TLS. |
| **Dependências de desenvolvimento do web com CVEs** (M2/M3) | 7 findings em `npm audit`, todos em devDependencies (vite, vitest, esbuild); `react-router-dom` 6.30 com 2 CVEs moderados sem pré-condição de exploração na SPA | Bump para vite ≥ 6 / vitest ≥ 3.2.6 / react-router-dom v7 em commit isolado. `pip-audit`: 0 CVEs nos 4 projetos Python; `detect-secrets`: 0. |
| **Mermaid do site de docs carregado de CDN** (B3) | `unpkg.com`, sem pin por hash | Vendorizar o script para permitir CSP `script-src 'self'`. |
| **Portas em `0.0.0.0`** (I4) | Adequado para demo local | `127.0.0.1:` no Compose fora do laptop. |

## 5. O que faltaria para escalar

Prioridade definida em `docs/revops-review.md` §4 e `docs/ml-pipeline.md` §8.

| # | Lacuna | Por quê | Tipo |
|---|---|---|---|
| 1 | **Data de última atividade por deal** (contato, reunião, proposta) | É o dado que decide um deal e que não existe. Único item que pode fazer o score voltar a prever algo; "parado" vira regra de inatividade, não de idade. | campo / integração |
| 2 | **Escrita de volta no CRM** (confirmado, Lost com motivo, conta preenchida) | Hoje `POST /feedback` grava em parquet local. Sprint de limpeza sem escrita no CRM é trabalho dobrado. | integração |
| 3 | **Campo "confirmado em" e motivo de Lost em 4 categorias** | Deal confirmado volta à fila com marco novo; coorte de limpeza separada do win rate operacional. | campo |
| 4 | **Conta obrigatória ao criar oportunidade** | 68% sem conta é constante em toda idade; só regra de entrada corrige. | processo |
| 5 | **Snapshots periódicos do pipeline** | Sem histórico de estágio por data, nenhum backtest futuro é confiável e o PSI de `account_*` continua disparando. | dado |
| 6 | **Definição de Prospecting e data obrigatória** | 500 deals sem data; validar com o negócio se é pipeline ou lista importada. | campo / processo |
| 7 | **Ciclo de recalibração mensal** (fator dos parados, limiar 138, hazard) com o feedback | `ZOMBIE_P_FACTOR = 0,5` é convenção; depois do sprint haverá dado real. | processo |
| 8 | **Autenticação e visão por perfil** | Filtros livres na URL deixam um ranking implícito a um clique. | integração / segurança |
| 9 | **Validação com o negócio do padrão de fim de trimestre** | Se real, é problema de processo (Lost segurado); se artefato, sai da lista. | processo |
| 10 | **Forecast oficial só com deals vivos** | Evita somar R$ 3,19 mi parados ou R$ 998 mil "esperados" de zumbis ao forecast (`_manifest.json`, `values`). | processo |
| — | Reponderação temporal do frame de treino; GBT só se a LR sombra mostrar sinal; retreino agendado (`docs/ml-pipeline.md` §6 e §8) | Mais features de ML **não** estão na lista: não há sinal nos dados atuais (`docs/figures/20_model_candidates.md`). A lacuna 1 vem antes de qualquer modelo. | ML |

## 6. Sobre a palavra "IA" nesta solução

Nenhum LLM participa do cálculo do score nem da redação dos reason codes (ADR 0005). "IA" aqui significa: um modelo estatístico treinado nos dados do próprio CRM (em modo sombra) e engenharia assistida por IA (Claude Code com agentes, skills e hooks — `process-log/`). Os textos que o vendedor lê são templates determinísticos alimentados pelos números de cada deal.
