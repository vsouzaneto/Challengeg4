# Foco — plano de testes e evidências

Este plano diz o que testar, como testar, o que está automatizado e qual foi o resultado real de cada execução. Resultado que não foi executado numa rodada aparece como não executado; nenhum número abaixo é estimado.

## 1. O que testar

| Camada | O que garantir | Como |
| --- | --- | --- |
| Dados | Contagens, chaves, vazios, datas, nomes divergentes | `audit.py` (saída para conferir) e testes de junção |
| Regra de prioridade | Fila, índice, desempate, fronteiras de 30, 90, 180 dias e US$ 4.000 | Testes Python (`test_rules.py`, `test_scoring.py`) |
| Isolamento do desfecho | `Won`/`Lost`, `close_value` e `close_date` não mudam a fila aberta | Testes Python (`test_scoring.py`, `test_sales.py`) |
| API e arquivos servidos | JSON ordenado, totais coerentes, páginas e scripts servidos | Teste HTTP real em `test_scoring.py` |
| Filtros e agrupamentos | Combinação de filtros, busca, agrupamentos, faixas, anotações | Testes Node |
| Interface | Leituras, detalhe, celular, tema, teclado, estados de erro | Roteiro manual com capturas |
| Documentação | Cópias servidas iguais aos documentos | `sync_docs.py --check` |
| Hipótese histórica | Resultado reproduzível e registrado | `evaluate.py` |

## 2. Como executar

Pré-requisitos: Python 3.10 ou superior, Node com `node --test` (18 ou superior) e os cinco CSVs em `data/` (`python download_data.py`). Sem `data/`, só `test_sales.py`, `test_rules.py` e os testes Node rodam.

```bash
python audit.py
python evaluate.py
python -m unittest discover -s tests -v
node --test tests/test_filters.cjs tests/test_business.cjs
node --check static/app.js
node --check static/panels.js
node --check static/mode.js
node --check static/theme.js
node --check static/reader.js
python sync_docs.py --check
```

Rode a partir da raiz do repositório, para que os imports `from app import …` e `from scoring import …` funcionem.

## 3. Inventário dos testes automatizados

### 3.1 `tests/test_scoring.py` — usa os CSVs reais (8 testes)

| Teste | O que verifica |
| --- | --- |
| `test_real_data_joins_and_alias` | 8.800 linhas lidas; `GTXPro` ligado a `GTX Pro` com preço maior que zero; existe conta vazia |
| `test_open_deals_only_and_deterministic_order` | Referência 2017-12-31; 2.089 oportunidades; IDs únicos; só `Prospecting`/`Engaging`; ordenadas por fila; duas execuções iguais |
| `test_closed_outcome_does_not_affect_open_priority` | Trocar `close_value` e `close_date` de uma linha não muda sua prioridade |
| `test_outcome_dates_do_not_change_snapshot_or_ranking` | Alterar fechamento de uma linha não muda a referência nem o ranking |
| `test_missing_engagement_date_and_stable_tie` | Sem data: `days_engaged` nulo e razão “sem data”; empate resolvido por ID |
| `test_missing_account_still_has_action_and_explanation` | Conta ausente continua em Qualificar com ação e razão “Conta ausente” |
| `test_payload_counts_match_lists` | Soma de `counts` igual ao número de oportunidades; `as_of` igual a 2017-12-31 |
| `test_http_serves_application_and_real_ranked_data` | Sobe o servidor numa porta livre e confere páginas, documentos, imagem, scripts e `/api/deals` com 2.089 itens e razões |

### 3.2 `tests/test_sales.py` — dados sintéticos (2 testes)

| Teste | O que verifica |
| --- | --- |
| `test_historical_sales_are_per_seller_and_only_wins_add_value` | Ganhas, perdidas e valor por vendedor; só `Won` soma valor |
| `test_closed_history_changes_context_without_changing_open_score` | Mudar `Won`/`Lost`, `close_value` e `close_date` altera `sales_by_agent`, mas não `deals`, `counts` nem `as_of` |

### 3.3 `tests/test_rules.py` — fronteiras da regra, dados sintéticos (11 testes)

| Teste | Fronteira |
| --- | --- |
| `test_ninety_day_limit_splits_advance_from_review` | 90 dias → Avançar 75; 91 → Revisar 60 |
| `test_recent_bonus_applies_up_to_thirty_days_in_advance_only` | 30 dias → 85; 31 → 75 |
| `test_old_bonus_applies_from_one_hundred_eighty_days_in_review_only` | 179 → 60; 180 → 70 |
| `test_catalog_price_bonus_starts_at_four_thousand` | 3.999,99 → 45; 4.000 → 55 (Qualificar) |
| `test_highest_index_per_queue_stays_below_the_cap` | Máximos 95, 80 e 55 |
| `test_prospecting_ignores_engagement_age` | Prospecting com 400 dias continua em Qualificar, índice 45 |
| `test_engaging_without_date_enters_advance_without_time_bonus` | Sem data → Avançar 75, sem bônus de tempo |
| `test_missing_account_loses_bonus_and_is_explained` | Sem conta → 65 e razão explícita |
| `test_queue_order_beats_index_order` | Avançar 65 aparece antes de Revisar 80 |
| `test_closed_deals_are_rejected_and_skipped` | `Won` levanta `ValueError`; `rank_open` ignora `Lost` |
| `test_catalog_alias_is_only_the_documented_one` | Só `GTXPro` é normalizado |

### 3.4 Node (7 testes)

| Arquivo | Teste | O que verifica |
| --- | --- | --- |
| `test_filters.cjs` | vendedor, gerente e região combinam sem alterar a ordem da fila | Combinação “e” e resultado vazio |
| `test_filters.cjs` | busca ignora maiúsculas, espaços e acentos preservados | Busca por ID, conta e produto |
| `test_business.cjs` | painéis agrupam a mesma carteira sem mudar ordem nem índice | `groupDeals` por vendedor, gerente e região |
| `test_business.cjs` | faixas de preço não perdem itens nas fronteiras | `priceBands` com 999, 1.000 e 4.000 |
| `test_business.cjs` | RG e mapa usam gerente, região e oportunidades do vendedor selecionado | `sellerProfile`, `regionSummary`, `avatarInitials` |
| `test_business.cjs` | status e anotação sobrevivem à releitura local, sem tocar no score | `saveAnnotation`/`readAnnotations` |
| `test_business.cjs` | armazenamento inválido não quebra a leitura | JSON inválido e erro de gravação |

## 4. Resultados reais

### 4.1 Esta rodada — 13/10/2026

Executados no ambiente da rodada de documentação (Node v24.21.0).

Comando:

```bash
node --test tests/test_filters.cjs tests/test_business.cjs
```

Saída:

```text
✔ painéis agrupam a mesma carteira sem mudar ordem nem índice (2.8677ms)
✔ faixas de preço não perdem itens nas fronteiras (0.436ms)
✔ RG e mapa usam gerente, região e oportunidades do vendedor selecionado (1.2895ms)
✔ status e anotação sobrevivem à releitura local, sem tocar no score (0.5701ms)
✔ armazenamento inválido não quebra a leitura (1.5329ms)
✔ vendedor, gerente e região combinam sem alterar a ordem da fila (2.3984ms)
✔ busca ignora maiúsculas, espaços e acentos preservados (0.4376ms)
ℹ tests 7
ℹ suites 0
ℹ pass 7
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 214.2795
```

**Não executados nesta rodada:** `download_data.py`, `audit.py`, `evaluate.py`, a suíte Python, `node --check` e `sync_docs.py --check`. O ambiente desta rodada exigiu aprovação para rodar Python e para baixar o dataset, e a rodada não pode pedir aprovação; sem os CSVs, os oito testes de `test_scoring.py` também não teriam dados. Em consequência:

- Os números do dataset citados nestes documentos (8.800 linhas, 2.089 abertas, 1.425 sem conta, AUC 0,4854) vêm das execuções registradas na seção 4.2, não de uma execução desta rodada.
- `tests/test_rules.py` foi escrito nesta rodada e **ainda não foi executado**. Os valores esperados foram calculados à mão a partir de `scoring.prioritize`. Rodar a suíte Python completa é o primeiro passo da próxima verificação.
- As cópias em `static/source/` foram atualizadas por cópia de arquivo e comparadas byte a byte com os originais (ver seção 5).

### 4.2 Execuções anteriores registradas

| Data | Quem | Resultado | Fonte |
| --- | --- | --- | --- |
| 09/10/2026 | Autor | Seis testes passaram (versão da época); páginas, scripts, CSS e API responderam HTTP 200 | Histórico deste arquivo (commit `2d15357`) |
| 10/10/2026 | Codex, tarefa G4-003-PAINEIS-01 | 10 testes Python, 6 Node, auditoria, avaliação histórica e verificação dos documentos passaram | Evidência da tarefa no quadro |
| 10/10/2026 | Claude Code, revisão da mesma tarefa | Node 6/6 reexecutado; Python não rodou (aprovação do ambiente e pasta `data/` ausente); `scoring.py` sem mudança | Evidência da tarefa |
| 10/10/2026 | Codex, tarefa G4-003-REDESIGN-01 | **10 testes Python com os CSVs reais** e 7 Node passaram | Evidência da tarefa |
| 10/10/2026 | Claude Code, revisão da mesma tarefa | Node 7/7 reexecutado; Python e dados reais não rodaram; totais por região 908 + 748 + 433 = 2.089 conferidos nas capturas | Evidência da tarefa |
| 13/10/2026 | Claude Code, esta rodada | Node 7/7; Python não executado | Seção 4.1 |

A última execução completa registrada (Python com os CSVs reais) é a de 10/10/2026, feita pelo Codex, **antes** dos testes de `test_rules.py` existirem. Os testes Python, portanto, somam 10 verificados em 10/10/2026 e 11 novos sem execução.

### 4.3 Resultados de `audit.py` e `evaluate.py` registrados

Estão em [auditoria dos dados](data-audit.md) (execução de 09/10/2026; a evidência da tarefa G4-003-PAINEIS-01 registra que ambos os scripts voltaram a rodar em 10/10/2026). Resumo: 8.800 negócios, 4.238 `Won`, 2.473 `Lost`, 1.589 `Engaging`, 500 `Prospecting`; 1.480 linhas com `GTXPro`; 1.425 abertas sem conta; AUC da afinidade 0,4854; quartil superior com 63,45% de `Won` contra 64,84% no teste.

### 4.4 Revisão Codex — 13/10/2026, rodada 202610131433-ae9e

Execução na cópia isolada da branch `claude-code/g4-003-docs-01`, após ler o diff `15bb5533533f..85c461d`. Nenhuma integração, push ou PR. As limitações da execução de Claude Code acima permanecem como registro histórico; os 11 testes novos foram agora executados.

| Comando / conferência | Resultado desta revisão |
| --- | --- |
| `python download_data.py` | Cinco CSVs públicos baixados; SHA-256 do ZIP igual ao esperado: `74d535826330b616758ebb6bb393abf701a5126364a72fbe71003cb6a7a87a9c` |
| `python -m unittest discover -s tests -v` | 21 testes passaram, incluindo os 11 novos e o servidor HTTP real |
| `node --test tests/test_filters.cjs tests/test_business.cjs` | 7 passaram; zero falhas |
| `python audit.py` | 8.800 linhas; 2.089 abertas; 1.425 abertas sem conta; zero IDs duplicados |
| `python evaluate.py` | AUC 0,4854; teste 0,6484; quartil superior 0,6345; corte 2017-11-03 |
| `node --check` em todos os scripts de `static/` | Sem erros de sintaxe |
| `python sync_docs.py --check` | 9 documentos conferidos antes das correções da revisão |
| `git diff --check 15bb5533533f..HEAD` | Sem erros de whitespace |
| Imagens e links locais | Sete arquivos copiados idênticos aos originais; links locais de `docs/` existentes; todas as sete imagens e a imagem de gerentes em tema escuro abertas e inspecionadas |

Trechos brutos das saídas executadas (rodapé das suítes, não a lista completa):

```text
----------------------------------------------------------------------
Ran 21 tests in 1.251s

OK
```

```text
ℹ tests 7
ℹ suites 0
ℹ pass 7
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 242.2866
```

A primeira tentativa da suíte Python passou os 13 testes sintéticos e falhou no `setUpClass` de `test_scoring.py` por ausência de `data/sales_pipeline.csv`. Depois do download, a suíte completa passou conforme acima. Não foi falha de implementação.

**Limite visual desta revisão:** a ferramenta de navegador informou `Browser is not available: iab`, e o inventário retornou zero navegadores. O leitor não foi aberto nem foram capturadas telas novas. As imagens existentes são do Foco; as legendas numéricas foram conferidas visualmente. As capturas históricas não certificam o layout atual. Mesa comercial, Fila de decisão, Kanban, detalhe do índice e índice da documentação continuam sem novas capturas nesta rodada. A leitura e aprovação do autor permanecem pendentes.

### 4.5 Fechamento visual e testes — 14/10/2026

Na cópia isolada `codex/g4-003-redesign-02`, executei `python -m unittest discover -s tests -v` com os CSVs públicos baixados pelo projeto: **21 testes passaram**. `node --test tests/test_filters.cjs tests/test_business.cjs` passou com **7 testes**. `python sync_docs.py --check` conferiu **9 documentos**. As capturas [`final-oportunidades-desktop.png`](../evidence/final-oportunidades-desktop.png) e [`final-oportunidades-celular.png`](../evidence/final-oportunidades-celular.png) mostram a navegação com ícones coloridos e os controles finais em 1440 px e 390 px. Não houve teste em aparelho físico nem piloto comercial.

## 5. Verificação dos documentos

`python sync_docs.py` copia os documentos listados em `SOURCES` para `static/source/`. Depois de editar qualquer um, rode `python sync_docs.py --check`; ele sai com erro se alguma cópia estiver ausente ou diferente. Quando Python não está disponível, a cópia pode ser feita com `cp` e conferida com `cmp`, que é o que a rodada de 13/10/2026 fez.

## 6. Lacunas conhecidas

| Lacuna | Risco | Como fechar |
| --- | --- | --- |
| `app.js`, `panels.js`, `reader.js`, `mode.js` e `theme.js` não têm teste automatizado | Regressão visual ou de comportamento só aparece na inspeção manual | Teste de navegador (por exemplo, automação do Chrome) sobre os cenários da seção 7 |
| Parâmetros de endereço (`/?agent=…`) e rotas `#…` dos painéis sem teste | Links entre painéis e fila podem quebrar sem aviso | Teste de navegador |
| Mapa com três formas fixas | Uma quarta região quebraria a página | Teste que falha com quatro regiões, ou forma gerada |
| `audit.py`, `evaluate.py` e `download_data.py` não têm asserções | Mudança de saída passa despercebida | Teste que compare contagens e AUC com valores esperados |
| Execução automática em integração contínua | Nenhum teste roda sem alguém executar | O repositório não tem pipeline; avaliar após definir o destino do PR |
| Legibilidade e navegação por teclado | Não verificadas | Roteiro da seção 7 |
| Efeito comercial | Não medido, nem mensurável neste dataset | Piloto com dados atuais |

## 7. Roteiro manual antes de uma entrega

Marcar cada item com captura ou observação e data.

| Cenário | Resultado esperado | Situação registrada |
| --- | --- | --- |
| Desktop, Mesa comercial | Tabela e detalhe legíveis; seleção atual indicada | Capturas de 10/10/2026 dos Painéis; Mesa comercial sem captura própria registrada |
| Fila de decisão e Kanban | Mesmo negócio, índice e próxima ação nas três leituras | Sem registro |
| Busca por ID e filtros por vendedor, gerente e região | Totais mudam; Limpar restaura a carteira | Filtros cobertos por teste Node; tela sem registro |
| Sem resultados | Mensagem clara e caminho para recuperar a lista | Sem registro |
| Claro, Escuro e Automático | Contraste legível; foco visível; escolha preservada | Captura em tema escuro dos cartões de vendedor (`evidence/vendedor-card-ajuste.png`); demais sem registro |
| Celular, seleção e Voltar | Detalhe abre sem ficar abaixo da lista; Voltar preserva o recorte | Ver seção 8; interação detalhada sem registro |
| Teclado | Tab alcança visões, filtros, linhas, detalhe e links; Escape fecha o detalhe móvel | Pendente |
| API indisponível | Erro visível e Tentar novamente funcional | Sem registro |
| Painéis em desktop e 390 × 844 | Gerente, Vendedor e Mapa legíveis | Capturas em `evidence/` (`gerente-*`, `vendedor-*`, `mapa-*`) |
| Totais por região | 908, 748 e 433 somam 2.089 | Conferido nas capturas de 10/10/2026 |

Capturas servidas pelo leitor: [gerentes no desktop](evidence/gerentes-desktop.png), [gerentes em largura reduzida](evidence/gerentes-largura-reduzida.png), [mapa geral](evidence/regioes-visao-geral.png), [região ampliada](evidence/regiao-ampliada.png). As capturas dos painéis em tema claro, em 1440 × 900 e 390 × 844, estão em `evidence/` com a descrição em `evidence/README.md`; os exemplos comentados estão na seção 9 da [especificação funcional](functional-spec.md).

## 8. Acesso pelo celular

Em 09/10/2026 uma instância temporária ligada apenas ao IP privado do computador (`--host`, porta 8844) recebeu, de um dispositivo da mesma rede, as requisições da página, CSS, scripts e API com HTTP 200, e o autor confirmou que abriu a página no celular. A conexão está validada; a legibilidade e a interação em um celular real continuam sem inspeção detalhada registrada. A instância padrão em `127.0.0.1` não é acessível por outro dispositivo.

## 9. Modelo de registro de uma execução

Ao rodar uma verificação, acrescente à seção 4.2 uma linha com data, quem executou, comando, resultado e fonte, e cole a saída bruta de cada comando na seção 4.1 (ou numa seção nova). Não resuma “passou” sem a contagem. Se algum comando não puder rodar, diga qual e por quê.

## 10. Limites de interpretação

Os testes provam que o código faz o que a regra descreve e que o desfecho não vaza para a prioridade. Não provam que a regra melhora a decisão comercial. O resultado da avaliação histórica é negativo, e não deve ser substituído por uma alegação de acurácia da heurística entregue. Um piloto exigiria observar uso, tempo até a ação e avanço de etapas em dados atuais. O [registro do processo](../PROCESS_LOG.md) identifica as etapas assistidas por IA e a evidência de cada uma.
