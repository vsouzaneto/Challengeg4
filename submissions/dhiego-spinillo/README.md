# Submissão — Dhiego Spinillo — Challenge 002

**Três caminhos executáveis em demonstração local: autosserviço, preparação e investigação. Ainda não submetido.**

## Comece por aqui

| Ordem | Material | O que responde |
|---|---|---|
| 1 · 2 minutos | [One-pager executivo](docs/resumo-executivo.md) · [visual no aplicativo](http://127.0.0.1:8766/resumo) | Problema, achados, recomendação, limites e próximo investimento. |
| 2 · 5 minutos | [Análise visual](solution/visual/index.html) · [abrir no aplicativo](http://127.0.0.1:8766/diagnostico) | Qualidade dos dados, urgência, espera, satisfação e contexto. |
| 3 · Demonstração | [Três fluxos executáveis](http://127.0.0.1:8766/fluxos) · [classificador](http://127.0.0.1:8766/classificador) | Autosserviço com conclusão, tentativa frustrada com contexto e investigação; sistemas fictícios explícitos. |
| 4 · Cenários | [Valor por processo](docs/valor-por-processo.md) · [calculadora](http://127.0.0.1:8766/valor) | Capacidade recuperada, despesa evitada e condições de retorno. |
| 5 · Evolução | [Três caminhos de atendimento](docs/tres-velocidades.md) | Fronteira entre execução demonstrada e integrações futuras. |
| Como decidimos | [Onde entra IA — e onde não entra](docs/onde-entra-ia.md) | Papel do LLM, modelo local, regras, fontes e revisão humana. |
| Fechamento | [Roteiro e matriz da entrega](docs/entrega.md) · [classificação dos 47.837 tickets](solution/reports/full-population/report.md) | O que demonstrar, o que foi avaliado e quais conclusões evitar. |
| Aprofundamento | [Comparação](solution/comparacao.md), [piloto](docs/piloto-operacional.md), [process log](process-log/README.md) | Como foi avaliado, o que falta medir e como as decisões evoluíram. |

Os tempos acima são sugestões de leitura/demonstração, não esforço de execução do case. Links em `127.0.0.1` funcionam após iniciar o aplicativo conforme o setup abaixo.

## Sobre mim

- **Nome:** Dhiego Spinillo.
- **Challenge escolhido:** 002 — Redesign de Suporte.

## Executive Summary

Auditei os dados antes de propor automação: o D1 não permite localizar perdas de tempo com segurança, pois não registra abertura e 49,3% dos pares temporais disponíveis estão invertidos. No D2, o classificador local acertou 86% de 800 tickets reservados, contra 45,25% do Jev na configuração testada. Após revisar casos e criticar o valor de uma ficha manual, implementei três caminhos: autosserviço com conclusão e tratamento de falha, atendimento preparado por consultas automáticas e investigação humana. IA interpreta texto com citações; modelo local sugere categoria; regras e fontes controlam procedimentos; humano assume exceções e aprova respostas. Sistemas e contas são fictícios, explicitamente identificados. A principal hipótese de valor é reduzir busca e preparação, com economics por processo e validação operacional ainda necessária. A comparação e o recap experimental anteriores foram preservados.

## Solução

### Abordagem

Entender as perguntas do diretor → auditar dados por finalidade → confrontar hipóteses → comparar sistemas → construir um fluxo executável → avaliar limites e revisar com o candidato.

### Resultados / Findings

| Pergunta do diretor | O que esta entrega sustenta |
|---|---|
| Onde perdemos tempo? | Não é possível quantificar pela duração do D1. Há 2.881 pendentes e sinais textuais para investigação; espera pelo cliente não equivale automaticamente a desperdício. |
| O que automatizar com IA? | IA para extração de intenção/tentativas/sinais; regras e consultas de contexto para executar procedimentos elegíveis ou preparar atendimento. Três caminhos demonstrados com sistemas fictícios. |
| Funciona? | Classificação avaliada; recuperação concluída em provedor simulado, falha com histórico e investigação aberta; 216 testes locais. Extração restrita exercitada em cenários conhecidos. Impacto operacional não medido. |

- [Diagnóstico visual](solution/visual/index.html): análise da base, fontes e limites; contém leituras de contexto preparadas durante a fase inicial.
- [Comparação local × Jev](solution/comparacao.md): separação de treino/validação/teste, remoção de vizinhos próximos e sensibilidade. O modelo local foi treinado com rótulos; Jev recebeu definições sem treino específico.
- [Rodada integral](solution/reports/full-population/report.md): 47.837 registros, 1.114 divergências com os rótulos, 305 delas acima do limiar. Rastreabilidade por linha e partição, sem novo treino. Concordância global inclui treino; a avaliação original continua sendo 86% no teste de 800.
- [Avaliação do recap](solution/avaliacao-recap.md): 15/16 saídas passaram pelo contrato estrutural/citações; Grok aprovou fidelidade em 6/15. Revisão automatizada exploratória, sem referência humana.
- [Política do classificador](docs/decisions/0004-classificador-local-e-confirmacao-humana.md) e [decisão de arquitetura/recap](docs/decisions/0005-prototipo-local-e-recap-experimental.md).

### Rodar o protótipo

Na pasta `submissions/dhiego-spinillo/`, com Docker e Compose disponíveis:

```bash
docker compose up --build
```

Abra **http://127.0.0.1:8766**. A página inicial apresenta os três caminhos. O modelo está incluído; a demo por regras e a classificação funcionam sem chave externa e sem baixar os datasets. A primeira construção baixa a imagem Python e as dependências.

1. Escolha **Recuperar acesso sem atendente** e processe. Observe as três fontes fictícias consultadas e a política aplicada.
2. Solicite a recuperação e conclua no provedor simulado. Confira o estado e a trilha de eventos: nenhuma conta real foi alterada.
3. Informe falha. O atendimento passa à preparação com o histórico preservado. Edite/aprove o rascunho; o texto é registrado, sem envio externo.
4. Processe o cenário de possível incidente. Receba para investigação: o caso permanece aberto e não executa reset.
5. Consulte `/valor`: examine preparação e autosserviço separadamente, incluindo custo de falha e cenários negativos. Consulte `/resumo` e `/diagnostico` para a análise.

Os sete cenários contêm textos reais do D2 e **contas, notas e estados fictícios**. Foram usados no desenvolvimento, não constituem uma avaliação independente. O volume Docker persiste os registros da demonstração.

**IA opcional:** copie `.env.example` para `.env` apenas se ainda não existir e configure `OPENROUTER_API_KEY`. Execute novamente `docker compose up --build` para aplicar a configuração. Em `/fluxos`, a opção de IA envia o texto ao OpenRouter para extrair intenção, tentativas e sinais com citações. Consome créditos. Sem chave, a interface identifica o uso de regras lexicais. Em `/classificador`, a mesma chave habilita o recap experimental, desligado por padrão. `TYPESAFE_API_KEY` é usada apenas nos experimentos Jev.

**Classificação e ficha anterior:** em `/classificador`, escolha/cole um texto em inglês, confirme o domínio de TI e analise a categoria. Confirme/corrija, registre conferências de outros tickets/sistema/notas e prepare a orientação. Nessa tela as conferências são declarações do atendente. Registre o motivo e exporte o CSV, que omite original, trecho do incidente e rascunho; o banco local conserva esses campos. Os três primeiros exemplos vieram do teste encerrado e foram discutidos com o candidato; os demais vieram do treino.

Execução alternativa com Python 3.10, a partir da mesma pasta:

```bash
python3.10 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m uvicorn app:app --app-dir solution --host 127.0.0.1 --port 8766
```

Testes, sem chamadas pagas:

```bash
.venv/bin/python -m pytest solution/tests -q
# Ou, com o serviço Docker iniciado:
docker compose exec suporte python -m pytest solution/tests -q
```

Resultado verificado: **216 testes passam localmente e no Docker** (204 do aplicativo/cálculos e 12 do lote integral). Cobrem contratos, política, falhas de recap, caminhos condicionais, persistência, exportação, procedimentos, estados, economics, separação das partições e reprodução da avaliação histórica. [Reprodução das análises](solution/REPRODUZIR.md).

### Recomendações

1. Registrar abertura, primeira resposta, mudanças de status com motivo, equipe/atendente, transferências e prazo real de urgência. Esses dados permitem separar fila, execução e dependência do cliente.
2. Comparar o fluxo assistido com o atual em tickets do mesmo domínio: acerto do encaminhamento, trabalho ativo total incluindo revisão/correção e retrabalho. Definir com a operação o ganho mínimo que justifica implantação e manutenção.
3. Manter confirmação humana da categoria. A seleção pelo limiar teve 6,69% de erro no teste, acima da meta de 5%; não é autorização para roteamento automático. O autosserviço demonstrado tem política própria por procedimento, contexto e confirmação do cliente.
4. Revisar semanticamente os recaps com referência humana antes de considerar adoção.

### Limitações

O D1 e o D2 têm domínios distintos; não foram unidos nem tratados como uma mesma operação. O contexto de cerca de 30 mil tickets/ano não informa elegibilidade ou minutos poupados. Não foram medidos redução de churn, recuperação de horas ou benefício financeiro. A primeira calculadora foi retirada após crítica do candidato; `/valor` apresenta hipóteses por processo, custos e condição de equilíbrio, ainda sem benefício medido.

O protótipo é local e não possui autenticação para publicação externa. Recap é experimental, desligado por padrão e sujeito a interpretações erradas mesmo com citações literais. A extração restrita dos três caminhos também requer avaliação semântica em amostra nova. Não há classificador de sentimento validado, envio automático de resposta, alteração cadastral real nem integração de produção. O piloto deve verificar se a preparação compensa seu custo de revisão.

## Process Log — Como usei IA

### Ferramentas usadas

| Ferramenta | Uso efetivo |
|---|---|
| Claude | Plano inicial fornecido pelo candidato; Sonnet 5 via OpenRouter para parecer, recap experimental e extração restrita nos três caminhos. |
| Codex | Crítica, scripts de auditoria/comparação, implementação, testes e organização dos registros. |
| Grok 4.7 via OpenRouter | Parecer independente sobre o mesmo briefing e julgamento exploratório de recaps. |
| Jev / TypeSafe | Classificação por definições no experimento comparativo. |

### Workflow

1. Dhiego trouxe experiência de CX e questionou urgência, pendências, reincidência, qualidade de resposta e uso indiscriminado de IA.
2. Codex auditou os arquivos e explicitou quais perguntas não podem ser respondidas com essas bases.
3. A revisão inspirada no [Oráculo Flow](process-log/revisao-2026-09-21/decisoes.md) confrontou pareceres reais; os revisores por API não executaram os CSVs.
4. Sistemas foram avaliados separadamente da política; resultados orientaram escolha local e confirmação humana.
5. Dhiego revisou três exemplos e definiu conferir registros antes de novo contato, investigar pendências a partir de evidências e separar categoria de possível incidente. Essas decisões orientaram a ficha e as regras de resposta.
6. A crítica de valor levou a consultas automáticas em fontes fictícias e três caminhos executáveis. A rodada completa classificou o D2 com o modelo congelado, mantendo desempenho de teste separado de ajuste ao treino.

### Onde a IA errou e como corrigi

O plano inicial sugeria métricas temporais que a auditoria não sustenta. A integração de recap inicialmente rejeitou um JSON válido envolto em Markdown; corrigimos o parser, preservamos a primeira rodada e repetimos as chamadas com o mesmo prompt. O julgamento posterior mostrou que passar no contrato não garante fidelidade. Dhiego também corrigiu o foco excessivo no resultado técnico e na economia simulada: a calculadora foi retirada e o benefício operacional voltou a ser uma hipótese a validar.

### O que eu adicionei que a IA sozinha não faria

Registro das intervenções reais do candidato: exigir distinção entre urgência e criticidade, entre espera necessária e retrabalho, entre regras e inferência; evitar autorresposta; manter evoluções dependentes de dados fora do núcleo; questionar se o ganho proposto merece investimento. Essas intervenções alteraram análise, escopo e interface; não são uma alegação de exclusividade das ideias.

## Evidências

- [Execução final local: sete capturas e roteiro](process-log/evidencias/entrega-local-2026-09-22/README.md). Sem hospedagem em VPS; esta rodada usa regras e classificador local. As evidências anteriores de IA real estão preservadas abaixo.
- [Process log cronológico](process-log/README.md).
- [Intervenções selecionadas do candidato](process-log/evidencias/trechos-da-conversa.md).
- [Pareceres e decisões multimodelo](process-log/revisao-2026-09-21/decisoes.md).
- [Capturas da análise visual](process-log/evidencias/visual-v1/README.md).
- [Capturas iniciais do protótipo](process-log/evidencias/prototipo-v1/README.md).
- [Fluxo vigente: três caminhos e valor por processo](process-log/evidencias/fluxos-v1/README.md).
- [Etapa anterior: ficha de investigação e rascunhos](process-log/evidencias/investigacao-v2/README.md).
- [Revisão de três casos pelo candidato](docs/revisao-guiada-tres-tickets.md) e [decisão do fluxo](docs/decisions/0006-contexto-verificado-e-investigacao-humana.md).
- [Plano de validação operacional](docs/piloto-operacional.md).
- [Roadmap](ROADMAP.md) e [estado atual](STATUS.md).

**Submissão enviada em:** ainda não enviada. Histórico de commits local.

## Evolução após a crítica de valor

O protótipo agora consulta três fontes locais fictícias e executa uma máquina de estados para autosserviço, preparação e investigação. A IA extrai sinais com citações; regras controlam procedimentos, contexto e ações. [ADR 0008](docs/decisions/0008-fluxos-executaveis-e-valor-por-processo.md). O fluxo antigo e suas avaliações foram preservados. Não há autenticação/integradores de produção ou saving medido.

O novo economics decompõe trabalho anterior, residual, falhas e revisão; reset isolado tem baixa contribuição no cenário. A hipótese principal de valor é retirar busca e reconstrução de contexto do atendente. [Memória e condição de equilíbrio](docs/valor-por-processo.md).
