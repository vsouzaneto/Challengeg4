# Submissão — Dhiego Spinillo — Challenge 002

**Protótipo em revisão com o candidato. Ainda não submetido.**

## Sobre mim

- **Nome:** Dhiego Spinillo.
- **Challenge escolhido:** 002 — Redesign de Suporte.

## Executive Summary

Auditei os dados antes de propor automação: o D1 não permite localizar perdas de tempo com segurança, pois não registra abertura e 49,3% dos pares temporais disponíveis estão invertidos. No D2, de suporte interno de TI, um classificador local acertou 86% de 800 tickets reservados, contra 45,25% do Jev na configuração testada. O protótipo executa classificação sobre texto novo, exige confirmação humana e registra correções; o limiar de confiança não cumpriu a meta de qualidade no teste. Um recap com LLM foi integrado e avaliado, mas permanece experimental por evidência insuficiente de fidelidade. A recomendação é validar utilidade operacional e instrumentar o atendimento antes de prometer economia ou ampliar a intervenção.

## Solução

### Abordagem

Entender as perguntas do diretor → auditar dados por finalidade → confrontar hipóteses → comparar sistemas → construir um fluxo executável → avaliar limites e revisar com o candidato.

### Resultados / Findings

| Pergunta do diretor | O que esta entrega sustenta |
|---|---|
| Onde perdemos tempo? | Não é possível quantificar pela duração do D1. Há 2.881 pendentes e sinais textuais para investigação; espera pelo cliente não equivale automaticamente a desperdício. |
| O que automatizar com IA? | Geração de uma sugestão de categoria no domínio avaliado. A confirmação segue humana; categoria não define urgência nem autoriza ações de acesso. |
| Funciona? | Classificação executável com 86% de acerto no teste, registro da decisão e exportação. Isso demonstra funcionamento técnico, sem provar economia ou redução de sobrecarga. |

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
4. Confirme ou corrija a categoria, informe o motivo e registre.
5. Exporte as decisões em CSV.

Os exemplos visíveis vêm do treino e não medem desempenho. A exportação omite o texto original; o banco local conserva o original para rastrear decisões. O volume Docker persiste os registros. Não há envio de resposta ou alteração em sistemas de atendimento.

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

Resultado verificado: **122 testes passam**. Cobrem contratos, política, falhas de recap, persistência, exportação e acesso a arquivos. [Reprodução das análises](solution/REPRODUZIR.md).

### Recomendações

1. Registrar abertura, primeira resposta, mudanças de status com motivo, equipe/atendente, transferências e prazo real de urgência. Esses dados permitem separar fila, execução e dependência do cliente.
2. Comparar o fluxo assistido com o atual em tickets do mesmo domínio: acerto do encaminhamento, trabalho ativo total incluindo revisão/correção e retrabalho. Definir com a operação o ganho mínimo que justifica implantação e manutenção.
3. Manter confirmação humana. A seleção pelo limiar teve 6,69% de erro no teste, acima da meta de 5%; não é autorização para roteamento automático.
4. Revisar semanticamente os recaps com referência humana antes de considerar adoção.

### Limitações

O D1 e o D2 têm domínios distintos; não foram unidos nem tratados como uma mesma operação. O contexto de cerca de 30 mil tickets/ano não informa elegibilidade ou minutos poupados. Não foram medidos redução de churn, recuperação de horas ou benefício financeiro. A calculadora ilustrativa foi retirada após Dhiego questionar as premissas de 500 tickets × 1 minuto: mesmo rotulada como hipótese, ela dava destaque a um ganho sem justificativa operacional.

O protótipo é local e não possui autenticação para publicação externa. Recap é experimental, desligado por padrão e sujeito a interpretações erradas mesmo quando contém citações literais. A utilidade operacional do recorte permanece em revisão.

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
5. O protótipo foi testado e está sendo revisado pelo candidato, inclusive quanto à relevância do benefício proposto.

### Onde a IA errou e como corrigi

O plano inicial sugeria métricas temporais que a auditoria não sustenta. A integração de recap inicialmente rejeitou um JSON válido envolto em Markdown; corrigimos o parser, preservamos a primeira rodada e repetimos as chamadas com o mesmo prompt. O julgamento posterior mostrou que passar no contrato não garante fidelidade. Dhiego também corrigiu o foco excessivo no resultado técnico e na economia simulada: a calculadora foi retirada e o benefício operacional voltou a ser uma hipótese a validar.

### O que eu adicionei que a IA sozinha não faria

Registro das intervenções reais do candidato: exigir distinção entre urgência e criticidade, entre espera necessária e retrabalho, entre regras e inferência; evitar autorresposta; manter evoluções dependentes de dados fora do núcleo; questionar se o ganho proposto merece investimento. Essas intervenções alteraram análise, escopo e interface; não são uma alegação de exclusividade das ideias.

## Evidências

- [Process log cronológico](process-log/README.md).
- [Intervenções selecionadas do candidato](process-log/evidencias/trechos-da-conversa.md).
- [Pareceres e decisões multimodelo](process-log/revisao-2026-09-21/decisoes.md).
- [Capturas da análise visual](process-log/evidencias/visual-v1/README.md).
- [Capturas do protótipo em revisão](process-log/evidencias/prototipo-v1/README.md).
- [Roadmap](ROADMAP.md) e [estado atual](STATUS.md).

**Submissão enviada em:** ainda não enviada. Histórico de commits local.
