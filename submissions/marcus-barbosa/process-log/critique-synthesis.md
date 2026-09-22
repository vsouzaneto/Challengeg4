# Auditoria adversarial: o que caiu e o que foi corrigido

## Como foi feita

Cinco agentes independentes, sem acesso às conclusões do autor, receberam o repositório e uma lente cada: vazamento e corte temporal, estatística, produto (vendedor e gerente), reprodutibilidade e higiene, e o avaliador do G4. Instrução: refutar achados, reproduzir números a partir dos CSVs, apontar arquivo e linha. Resultado: 46 achados. Uma segunda rodada de agentes verificou cada achado sobre o código já corrigido: 45 verificações concluídas antes de a rodada ser interrompida por limite de uso (31 resolvidos, 12 parciais, 2 persistentes). A tabela abaixo foi consolidada pelo autor a partir dessa rodada e das correções commitadas (`git log`), com checagem pontual; os dois persistentes eram o LinkedIn no README (preenchido depois) e os arquivos de evidência ainda não criados (este documento, o export do transcript e a banca).

## Achados de método (mudaram o motor)

| # | Achado | Estado | O que mudou |
|---|---|---|---|
| 35 | O painel de calibração não aplicava a janela limpa: 1.196 linhas de deals engajados em 2016 entravam no snapshot de março | resolvido | `open_engaging_at` exige `engage_date >= 2017-03-01`; teste `test_panel_respects_window_start_and_horizon`; erro da IA #5 |
| 11, 34 | A calibração filtrava por "tem conta" no estado final do campo (look-ahead) e inflava a chance em cerca de 1,6× | resolvido | chance principal com todos os deals abertos; "com conta hoje" virou coluna de sensibilidade rotulada como otimista; decisão 18; erro #6 |
| 12, 38 | Faixa pequena herdava a taxa da faixa mais jovem (57% para deals de 91 a 138 dias com 0% observado) | resolvido | agrupamento só com faixas mais velhas; sem amostra, o deal fica sem score (`SUPPORT_THIN`); teste `test_small_band_pools_with_older_bands_never_younger`; erro #7 |
| 13 | O mesmo deal em até 5 snapshots; intervalo de Wilson por linha era estreito demais | resolvido | intervalo por bootstrap de deals (200 reamostras); n reportado como deals únicos e observações; decisão 20 |
| 14 | Horizontes do backtest sobrepostos; 779 dos 1.403 ganhos apareciam em mais de uma data | resolvido | datas principais 30/06 e 30/09; 31/07 e 31/08 como estabilidade; contagem de repetição no documento; decisão 22 |
| 15 | A fatia Prospecting do backtest era selecionada pelo futuro | resolvido | backtest só com Engaging (`include_prospecting=False`); o documento diz que a prospecção não é reconstruível em datas passadas |
| 36 | "Zero fechamentos após 138 dias" apresentado como validação, quando é consequência da definição | resolvido | bloco descrito como propriedade da base no backtest, na metodologia e no README; a régua de 138 dias declarada como recalibrável |
| 37 | "Chance quase plana" contradita pelo próprio painel; H10 condicionava a fechar | resolvido | textos reescritos com as quatro faixas (37 / 40 / 18 / 1%); H10/H10b descritas como "entre deals que fecharam" |
| 16 | Teste de vazamento só com calibração fixa | resolvido | `test_calibration_and_score_do_not_see_the_future` trunca a base na data e exige calibração e scores idênticos |
| 39 | H2b chamado de permutação; é Monte Carlo sob nulo binomial | resolvido | renomeado no código, na tabela de hipóteses, na metodologia e no painel de arquitetura; a conclusão se mantém |
| 2 | O score era, na prática, o preço; a interface dizia que produto não entrava | resolvido | textos dizem que o produto pesa pelo preço e que dentro de cada faixa o score ordena como o preço; correlação 0,74 publicada |

## Achados de produto e interface

| # | Achado | Estado | O que mudou |
|---|---|---|---|
| 1, 7 | Topo da pauta com deals sem conta e conselho contraditório; item "Cadastrar conta" herdava ação errada | resolvido | próximo passo prefixado com "Cadastrar a conta no CRM hoje; depois, ..."; item de cadastro com ação própria; deals já escolhidos não repetem; decisão 21 |
| 3 | Deals de 121 a 138 dias recebiam "follow-up sem urgência" | resolvido | categoria Última janela (91 a 138 dias) com ação própria |
| 4 | Ações do gerente sem alvo ("os 0 deals", cadastro para quem tem 0 acionáveis) | resolvido | ações só com alvo concreto; ação de qualificação para quem tem 20+ prospects; sobrecarga calculada sobre deals abertos e dita na legenda (parcial: não exclui prospecção do cálculo) |
| 5, 6 | Rótulos e unidades diferentes entre telas; formatação de número inconsistente | resolvido em parte | um nome por bloco, "% do valor além de 138 d", dinheiro com ponto de milhar nas tabelas, percentual com vírgula; contagens em tabelas ainda usam o separador do Streamlit |
| 8 | Frase genérica repetida em todos os cards; "em 1 datas" | resolvido | frase só na barra lateral; singular e plural tratados |
| 9 | "Segunda-feira de referência" aceitava qualquer dia | resolvido | "Data de referência", formato DD/MM/YYYY |
| 10 | "Nenhum deal fechou sem conta" virava ordem sem dizer o limite | resolvido | "todo deal fechado, ganho ou perdido, tem conta; cadastre para o deal ser acompanhado" |

## Achados de documentação e consistência

| # | Achado | Estado | O que mudou |
|---|---|---|---|
| 17, 42 | README marcava evidências inexistentes (chat export, auditoria, banca) | resolvido nesta rodada | este arquivo, `process-log/chat-exports/` e `docs/banca-final.md` criados antes do PR; `05_check_repo.py` confere caminhos citados |
| 18, 46 | Placeholder do LinkedIn | resolvido | URL preenchida |
| 19 | Origem "MB?" no código contra "IA" nos documentos | resolvido | `02_explore.py` com origem IA; documentos regerados |
| 20, 40 | "8 confirmadas" contra 14 no JSON; H2 e H12 contraditórias | resolvido | metodologia e tabela de hipóteses com 14 confirmadas, 2 derrubadas por robustez, e coluna "entra no score?" |
| 21 | Exemplo numérico do backtest com a visão errada | resolvido | metodologia regerada com os números atuais e sem o exemplo antigo |
| 22 | Hashes SHA-256 prometidos e ausentes | resolvido | `01_audit.py` grava bytes, linhas e SHA-256 no relatório |
| 23 | Rubrica de diferenciação e marcos nunca fechados | resolvido | coluna de status por item na rubrica; `docs/marcos.md` com estado final |
| 24 | process-log/README desatualizado | resolvido | reescrito |
| 25 | Número sem script ("83% a 90% fecham em 138 dias") | resolvido | substituído pela taxa "fecha em 90 d" que a calibração calcula (`p_close_by_band`) e publica |
| 27 | Decisão 8 contradizia o código | resolvido | decisão 8 anotada como implementada no painel após a auditoria |
| 28 | Recomendação 4 com dois cortes numéricos incompatíveis | resolvido | "7 vendedores acima do P75 do time (88 deals abertos ou mais)" |
| 29 | Artefatos citados fora da submissão | resolvido | `docs/rubrica-do-avaliador.md` dentro da pasta; decisão 24 |
| 31 | "Focar agora = score ≥ 70" sem a precedência da idade | resolvido | precedência documentada: Focar agora só entre 15 e 90 dias |
| 33 | Uma única captura de sessão; frase sobre outros candidatos | resolvido em parte | segunda captura da sessão; frase reescrita ("o gap que parece fit vendedor × produto é ruído") |

## Achados de reprodutibilidade e higiene

| # | Achado | Estado | O que mudou |
|---|---|---|---|
| 26, 41 | `02_explore.py` quebrava em console Windows sem UTF-8 | resolvido | `sys.stdout.reconfigure(encoding="utf-8")` nos scripts de linha de comando; sinal de menos ASCII |
| 30, 44 | Comandos só com `py -3.12`; playwright fora do requirements | resolvido | README com `python` e nota para Windows; `requirements-dev.txt` com playwright e pillow |
| 43 | `.gitignore` da raiz ignora `submissions/` | resolvido | `05_check_repo.py` lista o que existe e não está no git; passo documentado |
| 45 | `99_clean_env_check.ps1` não verificava exit codes | resolvido, com um erro no caminho | checagem de `$LASTEXITCODE` por passo; o primeiro conserto usou `$args` (variável automática do PowerShell) e passou sem executar nada (erro #8); corrigido e log gravado em `docs/clean_env_check.log` |
| 32 | Trailer Co-Authored-By em todos os commits | mantido por decisão | decisão 23: transparência sobre a IA; a autoria é do candidato |

## Descartados ou aceitos como limite

- 36 (parte): a régua de 138 dias é artefato do gerador da base. Aceito como limite declarado; a régua fica porque é o que esta base sustenta e o texto diz que precisa ser recalibrada em um CRM real.
- 4 (parte): calcular sobrecarga só sobre deals engajados. Não alterado; a legenda do app diz como a sobrecarga é calculada.
- 16 (parte): avisar quando um deal aberto tem `close_date` preenchida. Não ocorre nesta base (0 casos na auditoria); não implementado.

## O que a auditoria mudou

A janela limpa passou do ledger para o código. A chance deixou de depender de um campo que só existe no futuro. Faixas sem amostra deixaram de herdar taxa e o deal fica sem score em vez de receber número inventado. O backtest deixou de somar o mesmo ganho em quatro datas. E o bloco de 138 dias passou a ser descrito como o que é: uma propriedade desta base, não uma prova do método.
