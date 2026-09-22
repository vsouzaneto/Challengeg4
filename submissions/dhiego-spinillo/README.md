# Submissão — Dhiego Spinillo — Challenge 002

**Protótipo implementado; pacote preparado para revisão final. Ainda não submetido.**

## Comece por aqui

| Ordem | Material | O que responde |
|---|---|---|
| 1 · 2 minutos | [One-pager executivo](docs/resumo-executivo.md) · [visual no aplicativo](http://127.0.0.1:8766/resumo) | Problema, achados, recomendação, limites e próximo investimento. |
| 2 · 5 minutos | [Análise visual](solution/visual/index.html) · [abrir no aplicativo](http://127.0.0.1:8766/diagnostico) | Qualidade dos dados, urgência, espera, satisfação e contexto. |
| 3 · 3 minutos | [Protótipo local](http://127.0.0.1:8766) | Classificação e lógica de preparação do atendimento em execução. |
| 4 · Cenários | [Economics e premissas](docs/economics.md) · [calculadora](http://127.0.0.1:8766/economia) | Capacidade recuperada, despesa evitada e condições de retorno. |
| 5 · Evolução | [Três caminhos de atendimento](docs/tres-velocidades.md) | Autosserviço, trabalho preparado e investigação humana; implementação atual versus proposta. |
| Aprofundamento | [Comparação](solution/comparacao.md), [piloto](docs/piloto-operacional.md), [process log](process-log/README.md) | Como foi avaliado, o que falta medir e como as decisões evoluíram. |

Os tempos acima são sugestões de leitura/demonstração, não esforço de execução do case. Links em `127.0.0.1` funcionam após iniciar o aplicativo conforme o setup abaixo.

## Sobre mim

- **Nome:** Dhiego Spinillo.
- **Challenge escolhido:** 002 — Redesign de Suporte.

## Executive Summary

Auditei os dados antes de propor automação: o D1 não permite localizar perdas de tempo com segurança, pois não registra abertura e 49,3% dos pares temporais disponíveis estão invertidos. No D2, de suporte interno de TI, um classificador local acertou 86% de 800 tickets reservados, contra 45,25% do Jev na configuração testada. O protótipo executa classificação sobre texto novo e organiza o próximo passo e um rascunho de resposta a partir de conferências registradas pelo atendente; o limiar de confiança não cumpriu a meta de qualidade no teste. Um recap com LLM foi integrado e avaliado, mas permanece experimental por evidência insuficiente de fidelidade. A recomendação é validar utilidade operacional e instrumentar o atendimento antes de prometer economia ou ampliar a intervenção.

## Solução

### Abordagem

Entender as perguntas do diretor → auditar dados por finalidade → confrontar hipóteses → comparar sistemas → construir um fluxo executável → avaliar limites e revisar com o candidato.

### Resultados / Findings

| Pergunta do diretor | O que esta entrega sustenta |
|---|---|
| Onde perdemos tempo? | Não é possível quantificar pela duração do D1. Há 2.881 pendentes e sinais textuais para investigação; espera pelo cliente não equivale automaticamente a desperdício. |
| O que automatizar com IA? | Hoje: sugestão de categoria e preparação por regras. Proposta: autosserviço de recuperação de senha, contexto consultado automaticamente e investigação humana para exceções; ver mapa dos três caminhos. |
| Funciona? | Classificação executável com 86% de concordância com os rótulos do teste, ficha de investigação, orientação e rascunhos por regra. Demonstra funcionamento técnico; impacto operacional não medido. |

- [Diagnóstico visual](solution/visual/index.html): análise da base, fontes e limites; contém leituras de contexto preparadas durante a fase inicial.
- [Comparação local × Jev](solution/comparacao.md): separação de treino/validação/teste, remoção de vizinhos próximos e sensibilidade. O modelo local foi treinado com rótulos; Jev recebeu definições sem treino específico.
- [Avaliação do recap](solution/avaliacao-recap.md): 15/16 saídas passaram pelo contrato estrutural/citações; Grok aprovou fidelidade em 6/15. Revisão automatizada exploratória, sem referência humana.
- [Política do classificador](docs/decisions/0004-classificador-local-e-confirmacao-humana.md) e [decisão de arquitetura/recap](docs/decisions/0005-prototipo-local-e-recap-experimental.md).

### Rodar o protótipo

Na pasta `submissions/dhiego-spinillo/`, com Docker e Compose disponíveis:

```bash
docker compose up --build
```

Abra **http://127.0.0.1:8766**. O modelo está incluído; classificação e registro funcionam sem chave externa e sem baixar os datasets. A primeira construção baixa a imagem Python e as dependências.

1. Escolha um ticket de demonstração ou cole texto em inglês.
2. Indique se pertence ao domínio de suporte interno de TI.
3. Analise, confira a categoria e a política.
4. Confirme ou corrija a categoria. Registre conferências de outros tickets, sistema e notas internas. O aplicativo não consulta essas fontes; os exemplos usam situações simuladas declaradas por quem demonstra.
5. Informe o resultado da consulta ao sistema. Se houver relato de possível incidente, marque-o e copie um trecho literal de origem.
6. Prepare a orientação. Conforme as informações registradas, revise e adapte o rascunho por regra; você pode copiá-lo, sem envio automático.
7. Informe o motivo, registre a decisão e exporte as conferências/orientação em CSV.

Os três primeiros exemplos vieram do teste já encerrado e foram discutidos com Dhiego; agora orientam desenvolvimento, sem constituir nova avaliação. Os demais vêm do treino. A exportação omite o texto original, o trecho do incidente e o rascunho; o banco local os conserva para rastrear decisões. O volume Docker persiste os registros. Não há envio de resposta ou alteração em sistemas de atendimento.

**Recap experimental opcional:** copie `.env.example` para `.env` se ainda não existir e configure `OPENROUTER_API_KEY`. Reinicie o serviço e marque a opção na interface. Essa ação envia o texto à API e pode consumir créditos. Sem chave, o classificador permanece disponível. `TYPESAFE_API_KEY` é usada apenas nos experimentos Jev, não no aplicativo.

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

Resultado verificado: **147 testes passam**. Cobrem contratos, política, falhas de recap, caminhos condicionais, origem do relato de incidente, persistência, registros antigos, exportação e acesso a arquivos. [Reprodução das análises](solution/REPRODUZIR.md).

### Recomendações

1. Registrar abertura, primeira resposta, mudanças de status com motivo, equipe/atendente, transferências e prazo real de urgência. Esses dados permitem separar fila, execução e dependência do cliente.
2. Comparar o fluxo assistido com o atual em tickets do mesmo domínio: acerto do encaminhamento, trabalho ativo total incluindo revisão/correção e retrabalho. Definir com a operação o ganho mínimo que justifica implantação e manutenção.
3. Manter confirmação humana. A seleção pelo limiar teve 6,69% de erro no teste, acima da meta de 5%; não é autorização para roteamento automático.
4. Revisar semanticamente os recaps com referência humana antes de considerar adoção.

### Limitações

O D1 e o D2 têm domínios distintos; não foram unidos nem tratados como uma mesma operação. O contexto de cerca de 30 mil tickets/ano não informa elegibilidade ou minutos poupados. Não foram medidos redução de churn, recuperação de horas ou benefício financeiro. A calculadora ilustrativa foi retirada após Dhiego questionar as premissas de 500 tickets × 1 minuto: mesmo rotulada como hipótese, ela dava destaque a um ganho sem justificativa operacional.

O protótipo é local e não possui autenticação para publicação externa. Recap é experimental, desligado por padrão e sujeito a interpretações erradas mesmo quando contém citações literais. A utilidade operacional ainda precisa de medição. A ficha pode acrescentar esforço; o piloto deve verificar se o contexto e a preparação compensam esse custo.

## Process Log — Como usei IA

### Ferramentas usadas

| Ferramenta | Uso efetivo |
|---|---|
| Claude | Plano inicial fornecido pelo candidato; Sonnet 5 via OpenRouter para parecer e geração de recap. |
| Codex | Crítica, scripts de auditoria/comparação, implementação, testes e organização dos registros. |
| Grok 4.7 via OpenRouter | Parecer independente sobre o mesmo briefing e julgamento exploratório de recaps. |
| Jev / TypeSafe | Classificação por definições no experimento comparativo. |

### Workflow

1. Dhiego trouxe experiência de CX e questionou urgência, pendências, reincidência, qualidade de resposta e uso indiscriminado de IA.
2. Codex auditou os arquivos e explicitou quais perguntas não podem ser respondidas com essas bases.
3. A revisão inspirada no [Oráculo Flow](process-log/revisao-2026-09-21/decisoes.md) confrontou pareceres reais; os revisores por API não executaram os CSVs.
4. Sistemas foram avaliados separadamente da política; resultados orientaram escolha local e confirmação humana.
5. Dhiego revisou três exemplos e definiu conferir registros antes de novo contato, investigar pendências a partir de evidências e separar categoria de possível incidente. Essas decisões orientaram a ficha e as regras de resposta.

### Onde a IA errou e como corrigi

O plano inicial sugeria métricas temporais que a auditoria não sustenta. A integração de recap inicialmente rejeitou um JSON válido envolto em Markdown; corrigimos o parser, preservamos a primeira rodada e repetimos as chamadas com o mesmo prompt. O julgamento posterior mostrou que passar no contrato não garante fidelidade. Dhiego também corrigiu o foco excessivo no resultado técnico e na economia simulada: a calculadora foi retirada e o benefício operacional voltou a ser uma hipótese a validar.

### O que eu adicionei que a IA sozinha não faria

Registro das intervenções reais do candidato: exigir distinção entre urgência e criticidade, entre espera necessária e retrabalho, entre regras e inferência; evitar autorresposta; manter evoluções dependentes de dados fora do núcleo; questionar se o ganho proposto merece investimento. Essas intervenções alteraram análise, escopo e interface; não são uma alegação de exclusividade das ideias.

## Evidências

- [Process log cronológico](process-log/README.md).
- [Intervenções selecionadas do candidato](process-log/evidencias/trechos-da-conversa.md).
- [Pareceres e decisões multimodelo](process-log/revisao-2026-09-21/decisoes.md).
- [Capturas da análise visual](process-log/evidencias/visual-v1/README.md).
- [Capturas iniciais do protótipo](process-log/evidencias/prototipo-v1/README.md).
- [Fluxo vigente: investigação e rascunhos](process-log/evidencias/investigacao-v2/README.md).
- [Revisão de três casos pelo candidato](docs/revisao-guiada-tres-tickets.md) e [decisão do fluxo](docs/decisions/0006-contexto-verificado-e-investigacao-humana.md).
- [Plano de validação operacional](docs/piloto-operacional.md).
- [Roadmap](ROADMAP.md) e [estado atual](STATUS.md).

**Submissão enviada em:** ainda não enviada. Histórico de commits local.
