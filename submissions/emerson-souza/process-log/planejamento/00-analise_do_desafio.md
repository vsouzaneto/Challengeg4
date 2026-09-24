# Visão geral: AI Master Challenge (G4), os 4 desafios num só sistema

*Planejamento. Nenhum código ainda. Atualizado em 23/09/2026.*

## Mapa desta pasta
| Arquivo | Conteúdo |
|---|---|
| `00-analise_do_desafio.md` | Este arquivo: regras gerais e decisões |
| **`01-NUCLEO_DO_SISTEMA.md`** | **A regra principal: sozinho + cooperativo** |
| `02-cruzamentos_entre_modulos.md` | O que cada módulo faz com os dados dos outros, com selo de evidência |
| `desafios/001-churn.md` … `004-social-media.md` | O que cada desafio pede, critérios, dicas e plano do módulo |
| `04-datasets.md` | Inventário dos dados, links, esquemas e status do download |
| `05-tecnologias_e_painel.md` | Stack e desenho do painel gráfico |
| `06-achados_iniciais_dos_dados.md` | O que os dados reais mostram (e o que NÃO mostram) |
| **`07-requisitos_obrigatorios.md`** | **Obrigatórios × diferenciais de cada desafio, com teste de aceite** |
| `08-contratos_de_dados.md` | Campos que cada módulo entende (De/Para) |
| `09-telas_do_painel.md` | Telas e abas de cada módulo |
| `10-entrega_github.md` | Anotações da entrega: estrutura, README, evidências a coletar |
| `11-o_que_falta_planejar.md` | Decisões em aberto, ordem de construção, riscos |
| `process-log/00-diario.md` | Registro do processo (obrigatório na entrega) |

## O repositório oficial, conferido arquivo por arquivo
Listagem completa via API do GitHub: o repositório tem **11 arquivos**, e todos foram lidos:
`README.md`, `CONTRIBUTING.md`, `submission-guide.md`, `templates/submission-template.md`, `challenges/README.md` e o `README.md` de cada um dos 4 desafios (`data-001-churn`, `process-002-support`, `build-003-lead-scorer`, `marketing-004-social`), além de `.gitignore` e `LICENSE`. Cada pasta de desafio contém **só o README**; os dados ficam no Kaggle.

## Regras gerais de entrega
| Tema | Regra |
|---|---|
| Canal | **Só Pull Request**: fork → branch `submission/seu-nome` → `submissions/seu-nome/` → PR para `main` |
| Estrutura | `README.md` (template) + `solution/` + `process-log/` (`screenshots/`, `chat-exports/`) + `docs/` |
| Título do PR | `[Submission] Nome — Challenge XXX` → no nosso caso: **`[Submission] Emerson Souza — Challenges 001, 002, 003 e 004`** |
| Um PR por pessoa | Atualizar = push na mesma branch |
| Fora da pasta | PR que mexe fora de `submissions/seu-nome/` é rejeitado |
| Process log | **Obrigatório** (senão, desclassificado): ferramentas, como decompôs o problema, onde a IA errou, o que você adicionou, quantas iterações |
| Setup | Se tem código, tem que ter instruções de setup |
| Baseline | Eles já rodaram cada desafio em Claude/GPT/Gemini. É preciso **superar substancialmente** a IA pura |
| Tempo | 4–6 h por desafio, sem pontos extras por horas a mais |
| Mais de um desafio | Permitido; eles preferem *"um bem feito a dois superficiais"* → **cada módulo tem que ser completo** |

## O que eles avaliam
Entendeu o problema antes de executar? Usou IA de forma inteligente? Resolve de verdade? Alguém consegue agir com o que foi entregue?

**Entrega forte:** entendeu o problema, IA usada de forma estratégica, resultado acionável, process log com iteração e julgamento, comunicação clara.
**Entrega fraca:** genérica, sem verificação, 1 prompt → 1 resposta, foco em parecer inteligente, documento de 40 páginas.

## Decisões tomadas (Emerson)
1. **Os 4 desafios**, num **sistema único** com painel gráfico no computador.
2. **Núcleo: sozinho + cooperativo** (ver `01-NUCLEO_DO_SISTEMA.md`).
3. Planejamento documentado em `.md` antes de qualquer código.
4. Painel em **janela própria, como software** (ideia do Emerson).
5. **Foco nos obrigatórios** de cada desafio; diferenciais depois.

## Próximos passos
Ver `11-o_que_falta_planejar.md`.
