# Process log — como a IA foi usada

> **Antes desta etapa.** Houve uma preparação com o Claude (modo Cowork) como assistente. Ela deixou prontos:
> - uma análise inicial dos dados;
> - a configuração do Claude Code;
> - o plano.
>
> Essa preparação não faz parte do processo registrado aqui. O primeiro passo do Claude Code foi revisar todo esse material — regras, números, código e documentação — em `01-revisao-inicial.md`.

## O que o guia de submissão pede, e onde está

1. **Ferramentas de IA e por quê:** a seção "Ferramentas", logo abaixo, e "Ferramentas usadas" no `../README.md`.
2. **Como o problema foi decomposto antes de pedir algo à IA:**
   - `00-leitura-do-problema.md`, a leitura do Bruno, escrita antes dos resultados da revisão;
   - `01-revisao-inicial.md`, a revisão de todo o material antes de construir;
   - `../docs/plano-e-matriz.md`, com os critérios de aceite e o plano por incremento.
3. **Onde a IA errou e como foi corrigido:** `erros-da-ia.md` (34 erros: quem percebeu, a correção e a evidência).
4. **O que o Bruno acrescentou que a IA sozinha não faria:** "O que eu adicionei" no `../README.md` e as decisões marcadas "Bruno" em `decisoes.md`.
5. **Quantas iterações foram:** "Iterações" e "Linha do tempo", mais abaixo.

## Ferramentas

| Ferramenta | Modelo | Para quê |
|---|---|---|
| Claude Code (extensão no Cursor) | Opus 5.5 (orquestrador, `critico`, `revisor`), Sonnet 5.5 (`testador-de-uso`) | Revisão inicial, implementação, testes, revisões, testes de uso, deploy |
| Skills `frontend-design` e `dataviz` (Anthropic) | — | Direção visual da interface, com o briefing do `../CLAUDE.md`; validação da paleta |
| Claude (Cowork) | — | Consultor do Bruno: formatar os prompts e sugerir caminhos |
| Krea (MCP) | Nano Banana Pro | As duas imagens do app; prompts em `prototipos/rodada-3/README.md` |
| Playwright | — | Testes de navegador, prints, vídeos e medição das personas |

## Se tiver 5 minutos, leia

- **P-1** em `erros-da-ia.md`: o viés de sobrevivência que a revisão inicial achou na preparação. A chance parecia subir com a idade.
- **C-9** em `erros-da-ia.md`: a falta de empresa entregava o futuro nas datas passadas (D34).
- **D41** em `decisoes.md`: a interface reprovada por parecer painel genérico, e a direção nova.
- **C-22 a C-24** em `erros-da-ia.md`: o que o Bruno pegou no site publicado (D53 a D55).

## Como ler esta pasta

| Arquivo ou pasta | O que tem |
|---|---|
| `01-revisao-inicial.md` | Revisão completa do material de partida, feita pelo Claude Code no primeiro passo |
| `decisoes.md` | Decisões de partida e decisões tomadas durante a construção |
| `00-leitura-do-problema.md` | A leitura do problema pelo Bruno, escrita antes de ver os resultados da revisão |
| `erros-da-ia.md` | Erros da IA (da preparação e desta etapa): quem percebeu e como foi corrigido |
| `revisoes-incremento-4.md`, `revisoes-incremento-5.md` | Achados do `revisor` e do `testador-de-uso`, o que foi reproduzido e o que foi feito, com as medições das personas |
| `prototipos/` | As três rodadas de protótipo, com prints, vídeos e os prompts das imagens |
| `screenshots/` | Prints reais: `02-app/` (primeira versão, reprovada no portão visual) e `03-app/` (versão final, em 1280 e 390 px, claro e escuro, com vídeos) |
| `chat-exports/` | Exports das sessões do Claude Code (`/export`) |

## Linha do tempo

Pelos commits da branch `submission/bruno-mosconi` (datas de 09 e 10/10/2026), na ordem:

| Commit | Etapa | O que foi feito |
|---|---|---|
| `0d4f530` | Incremento 0 | Configuração do Claude Code (agentes, hook que bloqueia edições fora da pasta, script seguro de `git add`) e material de partida |
| `3684997` | Revisão inicial (C1) | Núcleo em TypeScript e recálculo independente de todos os números |
| `cc7c54d` | Revisão inicial (C2) | Correções dos achados do `critico` e do `revisor` |
| `a2fb335` | Leitura do problema | O texto do Bruno, escrito antes de ver os resultados da revisão e versionado depois deles, sem alteração (`01-revisao-inicial.md`, G1) |
| `13f16c0`, `cad53e8` | Portão G1 | Decisões do Bruno aplicadas: entrada tardia como regra final, chance como histórico, prazo sem previsão de queda |
| `6211796` | Incremento 4, primeira versão | Telas do vendedor e do gestor |
| `e64ec7d` | Portão visual | Primeira versão reprovada; direção de arte, protótipos da rodada 2 e score de 0 a 100 |
| `0274e4f` | Protótipos, rodada 3 | Aprovada (D44), com o briefing novo |
| `d4ddece` | Incremento 4 | Interface na direção aprovada |
| `a8981ae` | Incremento 5 | "Como funciona" com as três provas; herói de ação para score baixo |
| `81a3ceb`, `6b00278` | Escala e deploy | Bench, segundo adaptador de dados, documentos conferidos contra a auditoria, teste de que o app não faz chamada de rede |
| `5534e37`, `195823f` | Documentação | README no template; exports das sessões, limpos (D52) |
| `8cfa186` | Correções do site publicado | Entrada, Central, herói de ação e acabamento (D53 a D55) |
| `ef7a82f`, `6c71128` | Publicação | URL no README; caminho certo depois de clonar (teste de clone limpo) |
| `134894a` e seguintes | Fechamento | Lint sem avisos; achados da banca simulada (D56); seletor de equipe e tabela da prova 1 (D57); "Como escalar" com arquitetura alvo e gatilhos (D58); export final da sessão 3 |
| Depois do `7b82e3f` | Varredura final | Limpeza dos exports, varredura de segurança e conferência da entrega; texto da tela na língua do vendedor (D59). Detalhe abaixo |

### Varredura final

Feita depois do export final da sessão 3. Por isso não está em nenhum export: a evidência é este texto e os commits.

**O que foi verificado:**
- **Termos privados e e-mails:** os arquivos rastreados, o que entraria no próximo commit e o histórico da branch.
- **Caminhos absolutos, nome do usuário e da máquina, IDs de sessão e UUIDs:** os mesmos lugares.
- **Segredos:** prefixos de chave, palavras como token e Bearer, blocos de configuração de MCP e do Claude Code, e arquivos proibidos no `.gitignore` e nos commits.
- **Imagens:** as 94 de `screenshots/` e `prototipos/`, abertas uma a uma, em busca de e-mail, conta, abas, notificações e caminhos.
- **Histórico e escopo do PR:** `git log -p` da branch e a lista de arquivos do PR.
- **A entrega:** placeholders, as seções do template oficial, as entregas do enunciado e os cinco pontos do guia de submissão.

**O que foi achado e corrigido:**
- **Export da sessão 3:** a limpeza (`tools/limpar-exports.mjs`) fez 56 substituições:
  - 36 caminhos com o usuário local;
  - 7 caminhos temporários;
  - 6 da pasta do ai-memory;
  - 3 e-mails;
  - 3 termos privados;
  - 1 ID de sessão.

  Os exports das sessões 1 e 2 já estavam limpos.
- **Configuração pessoal:** um trecho citado na conversa virou `[configuração pessoal removida]`.
- **`.gitignore`:** ganhou dois padrões de arquivo de chave.
- **Nenhum segredo** com valor, nas imagens ou no histórico. Os 6 UUIDs que ficaram são IDs de job do Krea (exceção aprovada).
- **Escopo do PR:** só arquivos desta pasta.
- **A tela tinha um termo técnico fora de "Ver detalhes":** "margem de erro", na dica da data bloqueada. Foi reescrito na língua do vendedor (D59).
- **Placeholder:** havia um sem preencher em `erros-da-ia.md`, que o Bruno preencheu.
- **Guia de submissão:** os cinco pontos que ele pede passaram a ser apontados no topo deste arquivo.

**"O que eu adicionei", no `../README.md`:** o Claude Code conferiu as frases do Bruno contra este process log e achou duas inconsistências:
- **Os 9 erros da preparação**, que citavam um erro que não está entre eles. O Bruno corrigiu com as próprias palavras.
- **A "margem de erro", que aparecia na tela.** O erro era do app, não do texto, e foi corrigido no app (D59).

## Iterações

Contadas nos commits, nos exports e nos arquivos desta pasta:

- **Sessões do Claude Code:** 3 (exports em `chat-exports/`), com compactações de contexto na segunda e na terceira. O export final da terceira (`2026-10-10-claude-code-sessao-3.txt`) substitui o parcial versionado antes (`2026-10-09-claude-code-sessao-3-parcial.txt`), porque traz a sessão desde o início, inclusive tudo o que o parcial tinha.
- **Portões com o Bruno:**
  - G0: aprovação do plano;
  - G1: decisões da revisão;
  - portão visual: reprovado;
  - rodada 2 de protótipos: reprovada;
  - rodada 3: aprovada;
  - incremento 4: aprovado;
  - incremento 5: aprovado;
  - site publicado: correções pedidas pelo Bruno (D53 a D55).
- **Versões da interface:** 4. São a primeira versão do app (reprovada), a rodada 2 de protótipos (reprovada), a rodada 3 (aprovada) e o app final.
- **Rodadas de revisão dos agentes:**
  - revisão inicial: `critico` em 2 rodadas sobre o plano e 1 sobre a revisão, e `revisor` em 1;
  - plano do incremento 4: `critico`;
  - incrementos 4 e 5: `revisor` e `testador-de-uso`, 1 rodada cada;
  - site publicado: `testador-de-uso` contra a URL e banca simulada (`critico`), 1 rodada cada.
- **Decisões registradas:** D1 a D59, em `decisoes.md`.
- **Erros registrados:** 34, em `erros-da-ia.md`. São 9 da preparação, encontrados na revisão inicial, e 25 desta etapa, todos corrigidos ou com o motivo de não corrigir.
