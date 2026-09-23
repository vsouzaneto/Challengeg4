# Support Decision Copilot

Aplicação local para diagnosticar a operação Customer Support, classificar tickets em
dois domínios independentes, aplicar um gate de risco e registrar decisões humanas sem
enviar mensagens externas. O estado atual é **seguro por padrão**: a recuperação não
produz rascunhos porque a execução real encontrou zero consultas elegíveis para a
validação humana opcional que habilitaria essa capacidade.

- [README oficial da submissão](../../README.md)
- [Pesquisa técnica](../../research/002-support.md)
- [Diário contemporâneo](../../process-log/002-support.md)
- [Challenge 002 oficial](../../../../challenges/process-002-support/README.md)
- [Demo pública](https://support-decision-copilot-luis.streamlit.app/)

## Resposta curta às três perguntas

1. **Onde perdemos tempo?** Em 8.469 linhas, 1.404 intervalos pós-primeira-resposta válidos
   mostram Chat (`6,52 h`), High (`7,12 h`) e Product inquiry (`6,98 h`) como maiores
   medianas; o proxy soma `4.047,83 h` acima das medianas de 20 grupos.
2. **O que automatizar?** Classificação e roteamento interno somente com modelo suportado,
   confiança calibrada e ausência de riscos. Resposta externa, caso crítico, sensível,
   ambíguo, inválido ou incerto permanece humano.
3. **Como funciona?** Streamlit abre em **Resposta ao Diretor**; fila, scorecard,
   Laboratório IT e evidências aprofundam a decisão. O fluxo registra ações em SQLite e
   exporta CSV sem enviar mensagens externas.

## Arquitetura mínima

```text
CSVs públicos → sanitização/splits → diagnóstico + modelos separados
                                      ↓
fila Customer → classificador → gate de risco → precedentes → decisão humana → SQLite/CSV
scorecard      ← evidências agregadas         Laboratório IT ← modelo/taxonomia IT
```

Customer Support usa o Dataset 1 para operação, diagnóstico e precedentes. IT usa o
Dataset 2 somente no laboratório de oito classes. Os domínios reutilizam código, mas não
linhas, rótulos, taxonomias ou métricas. A interface carrega artefatos validados; não
treina, não retuna thresholds e não aprende com uma decisão individual.

## Requisitos e setup

Requer Python 3.12, `make`, `curl` e `unzip`. O primeiro `make setup` precisa de rede ou de
um cache local completo para instalar as versões exatas de `requirements.lock`. Depois do
lock instalado, o pacote editable reutiliza o `setuptools` bloqueado, sem build isolation
nem resolução adicional.

```bash
make PYTHON=python3.12 data
make PYTHON=python3.12 setup
make PYTHON=python3.12 doctor
make PYTHON=python3.12 reproduce
.venv/bin/python -m support_copilot.retrieval prepare-review \
  --artifacts artifacts --split calibration
# Se o comando acima retornar eligible=0:
.venv/bin/python -m support_copilot.retrieval lock-review \
  --artifacts artifacts --split calibration --decision disabled
make PYTHON=python3.12 reproduce
make PYTHON=python3.12 app
```

Se `eligible` for maior que zero, não use `--decision disabled`: preencha a rubrica de
calibração e execute `lock-review --rubric CAMINHO_DA_RUBRICA.csv` antes da segunda
reprodução. Essa sequência libera a fila somente após uma decisão de recuperação
congelada; iniciar o app logo após a primeira reprodução mantém a fila indisponível.

`make data` exige rede para baixar as fontes; o primeiro `make setup` também exige rede ou
cache local completo para instalar o lock. Depois de preparar ambiente, CSVs e artefatos,
inferência, decisões, exportação e demonstração funcionam localmente sem API, credencial ou
serviço externo. `make demo` apenas valida o ambiente e inicia o Streamlit; não instala,
baixa ou treina.

## Fontes e retomada manual

| Domínio | Download público | Arquivo esperado |
|---|---|---|
| Customer | [Kaggle](https://www.kaggle.com/api/v1/datasets/download/suraj520/customer-support-ticket-dataset) | `customer_support_tickets.csv` |
| IT | [Kaggle](https://www.kaggle.com/api/v1/datasets/download/adisongoh/it-service-ticket-classification-dataset) | `all_tickets_processed_improved_v3.csv` |

Se `make data` falhar, baixe os dois ZIPs pelos links, extraia exatamente esses arquivos
para `data/raw/` e repita `make reproduce`. Não use CSV sintético como substituto. Dados
brutos, `.venv`, artefatos reproduzíveis, banco e exports runtime são ignorados pelo Git.

## Comandos

| Comando | Função |
|---|---|
| `make doctor` | Confere Python 3.12, lock, ferramentas, fontes e diretório gravável |
| `make setup` | Cria `.venv` e instala lock + pacote local |
| `make data` | Baixa os dois datasets públicos sem credenciais |
| `make reproduce` | Sanitiza, divide, analisa, treina e publica artefatos verificados |
| `make demo` | Executa `doctor` e abre a aplicação local |
| `make test` | Executa a suíte pytest |
| `make lint` | Executa Ruff |

O lock só deve ser criado por `make bootstrap-lock` em Python 3.12 quando ainda não
existir. Ele não deve ser regenerado para “consertar” uma falha de ambiente.

## Fluxo do agente

1. A fila Customer é ordenada por prioridade existente, quantidade de riscos e incerteza.
2. O detalhe mostra texto sanitizado, categoria, confiança, regras e decisão do gate.
3. Até três precedentes do treino podem aparecer com ID e similaridade.
4. O agente aprova, edita e aprova, rejeita ou escalona; as duas últimas exigem motivo.
5. A confirmação só aparece após escrita e releitura do `audit_id`; o CSV usa os bytes do
   arquivo persistido e neutraliza fórmulas de planilha.

Nenhuma ação envia mensagem, fecha ticket, retreina modelo ou altera threshold. Sem draft
validado, aprovação é bloqueada e a saída correta é revisão humana ou escalonamento.

## Evidência: observado, medido e projetado

### Histórico observado

- Dataset 1: a lane estruturada usa 8.469/8.469 linhas sem campos textuais ou PII; a lane
  textual conservadora mantém 1.389 linhas para classificação/recuperação.
- Dataset 2 lido: 47.837 linhas; 26.472 passaram pela mesma fronteira pública.
- O intervalo temporal disponível é pós-primeira-resposta, não resolução total.
- Há 1.404 intervalos válidos e 2.769 ratings. Chat tem mediana `6,52 h` (`355/2.073`),
  High `7,12 h` (`355/2.085`) e Product inquiry `6,98 h` (`257/1.641`).
- Grupos com `n≥30` formam o ranking suportado; grupos menores ficam separados como
  exploratórios com IC95%. Chat / Low / Technical issue (`13,23 h`, `n=15`) não sustenta
  sozinho uma prioridade operacional.
- O proxy de excesso soma `4.047,83 h` em 20 grupos; Refund request / High lidera com
  `274,17 h`. Excesso é oportunidade histórica, não economia realizada.
- Spearman entre intervalo e satisfação é `0,00264` em 1.404 pares. Ridge MAE `1,2026`
  ficou pior que o baseline `1,1867`: `no_reliable_signal`, sem alegação causal.

### Desempenho medido

- Modelos são escolhidos contra dummy e baselines textuais por CV somente no treino.
- Teste fica lacrado até modelos, calibração, regras e thresholds estarem congelados.
- No teste congelado, Customer obteve macro-F1 `0,1394`, log loss `1,6124` e ECE
  `0,0328` em 231 casos; IT obteve `0,8351`, `0,4578` e `0,0414` em 5.301 casos.
- Customer tem `0%` de cobertura segura. IT cobre `37,43%` no limiar travado de `0,55`,
  mas o risco seletivo de `10,64%` supera o teto; ambos permanecem sem autonomia de
  produção, e IT pode operar somente em shadow com revisão humana.
- Fixtures cobrem regressões; a evidência final abaixo usa fila, SQLite, export e
  navegador reais. O desempenho Customer baixo mantém sua automação desativada.

### Cenários projetados

O volume inicial de `30.000 tickets/ano` vem do briefing. Conservador, base e otimista
projetam, respectivamente, `150`, `625` e `1.600 h/ano`; fração, minutos e custo/hora são
editáveis. A fonte não contém custo, moeda ou salário: nenhum cenário é economia realizada.

### Piloto shadow e go/no-go

Duração de duas semanas, mínimo de `1.000` tickets estratificados e baseline do tempo
manual. Cada sugestão é comparada com a decisão humana, sem alterar helpdesk ou responder
ao cliente. Promoção exige todos: macro-F1 `≥75%`, recall por classe `≥65%`, ECE `≤5%`,
risco seletivo `≤10%` com cobertura `≥20%`, zero escape sensível/crítico e redução `≥20%`
do tempo mediano de triagem.

## Protocolo humano de recuperação

A fonte normativa completa é o docstring/ajuda de
`src/support_copilot/retrieval.py`. Resumo operacional:

```bash
.venv/bin/python -m support_copilot.retrieval prepare-review \
  --artifacts artifacts --split calibration

.venv/bin/python -m support_copilot.retrieval lock-review \
  --artifacts artifacts --split calibration \
  --rubric CAMINHO_DA_RUBRICA_PREENCHIDA.csv

.venv/bin/python -m support_copilot.retrieval prepare-review \
  --artifacts artifacts --split test

.venv/bin/python -m support_copilot.retrieval lock-review \
  --artifacts artifacts --split test \
  --rubric CAMINHO_DA_RUBRICA_FINAL.csv
```

Se houver população elegível, calibração e teste opcionais usam amostras seeded,
estratificadas e independentes de 30 consultas.
O avaliador preenche relevância, correção, segurança e esforço de edição de 1 a 5, além de
pseudônimo e timestamp. Menos de 30 consultas, formulário incompleto, nota de segurança
abaixo de 3 ou médias de correção/segurança abaixo de 4 mantêm drafts bloqueados. O teste
final nunca retuna o threshold. A execução real atual registrou `insufficient_evidence`
com zero consultas elegíveis; portanto, nenhuma rubrica foi fabricada. As 60 avaliações
de CK-12 são validação futura opcional, não gate do briefing; sua ausência bloqueia drafts,
não o diagnóstico, o roteamento seguro, a intervenção humana ou o protótipo real.

Para congelar explicitamente uma demonstração sem revisão suficiente:

```bash
.venv/bin/python -m support_copilot.retrieval lock-review \
  --artifacts artifacts --split calibration --decision disabled
```

## Privacidade, integridade e falhas

- Nome, email, telefone, URL, IP e identificadores são removidos antes de treino, UI,
  persistência e export. Texto suspeito inteiro entra em quarentena.
- Sanitização por regex é conservadora, não prova anonimização universal e pode reduzir
  cobertura. Toda amostra pública ainda exige revisão humana.
- Manifesto vincula fontes, lock, configuração, código, splits e artefatos por hashes.
- Artefato ausente, corrompido, incompatível ou stale bloqueia só a capacidade afetada,
  mostra caminho relativo, causa e `make reproduce` como correção.
- SQLite usa transação atômica e idempotência por UUID. Falha não apaga registros antigos
  nem anuncia sucesso.

## Acesso operacional

Diagnóstico, métricas e fila sanitizada permanecem públicos para avaliação. Decisões,
leitura do SQLite e export são **fail-closed**: exigem login OIDC e combinação exata de
`iss` + `sub` nas allowlists do servidor. Sem configuração de autenticação, nenhuma ação
sensível é habilitada e o banco nem sequer é criado pela página de evidências.

Copie apenas a estrutura de `.streamlit/secrets.example.toml` para o cofre de secrets do
Streamlit Cloud. Nunca versione `secrets.toml`. `client_secret` e `cookie_secret` ficam no
servidor; nenhum token é exposto ao frontend.

## Evidências finais

- [Screenshot sanitizado real](evidence/screenshot.png): Scorecard com o diagnóstico
  operacional; a imagem não prova persistência nem contém audit ID.
- [Export persistido](evidence/decisions-demo.csv): evidência pública exclusiva da
  persistência do `audit_id=1`, ação `escalate`, SHA-256 `5d832e99...357e5b` registrado em
  [metrics.json](evidence/metrics.json).
- Scorecard e texto livre IT foram observados no navegador. IT classificou
  `hardware device not starting` como Hardware, com confiança `0,9701` e `auto_route` no
  threshold `0,55`.
- Aprovação/edição permaneceram bloqueadas porque zero consultas eram elegíveis para a
  validação humana opcional. CK-12 fica como evolução futura; nenhum draft ou rating foi
  fabricado, e o escalonamento real persistido demonstra a intervenção humana canônica.
- Evidência técnica mais recente: 242 testes completos, 41 testes de workflow e 2 testes
  de documentação/evidência aprovados. O preflight terminal do SHA final foi pulado por
  instrução do owner e não é apresentado como verde.

Ausência de amostra suficiente mantém somente a resposta assistida desativada. Essa falha
segura é uma limitação explícita e não impede os entregáveis obrigatórios do challenge.

## Limitações e escopo excluído

- Sem timestamp de criação, primeira resposta e resolução total não são observáveis.
- Associação não é causalidade; custo é cenário, nunca fato histórico.
- Sanitização forte reduz amostra e pode enviesar as conclusões.
- Recuperação está desativada por evidência insuficiente; não há geração livre de fallback.
- Não existem helpdesk real, envio, autenticação, multiempresa, deploy obrigatório ou
  aprendizado online.

## Verificação

No paralelo da Phase 3, o step documental executou somente:

```bash
.venv/bin/pytest tests/test_workflow.py::test_delivery_documentation_contract -q
.venv/bin/ruff check tests/test_workflow.py
git diff --check
```

O step final executa a suíte consolidada, reprodução e demonstração real no estado
entregue. Resultado de outro SHA, fixture sintética ou teste S07 isolado não substitui
esse gate.
