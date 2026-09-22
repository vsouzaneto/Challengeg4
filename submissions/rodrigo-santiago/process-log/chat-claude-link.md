# Chat com Claude — Construção do Webapp

**Link público da conversa:** https://claude.ai/share/39b2f071-95b1-429e-bf19-38c3c2d8912c

---

## Contexto

Esta conversa cobre a fase de construção do webapp "Deals Priorizados" (após o tratamento e enriquecimento dos dados feito com o Gemini, documentado em `chat-gemini-completo.md`).

Ferramenta usada: Claude, via projeto dedicado ao processo seletivo G4 com os CSVs originais e as instruções do desafio anexados.

## O que a conversa cobre

**Arquitetura da solução em Google Apps Script.** Discussão sobre estrutura de arquivos, escolha por 3 arquivos (`Code.gs` backend, `Prompts.gs` isolando os prompts para iteração, `Index.html` frontend completo com HTML+CSS+JS vanilla em um único arquivo).

**Iterações de código do webapp.** Escrita incremental de cada bloco (leitura da planilha, atualização de deals, integração Gemini, filtros multi-select, drag-and-drop no kanban, modal de análise IA, tela de login com credenciais pré-preenchidas, sidebar com breadcrumb estilo Garô).

**Definição da régua de prioridade ALTA/MÉDIA/BAIXA.** Discussão sobre o risco de "quando tudo é prioridade, nada é prioritário". Escrevi uma função de diagnóstico (`analisarPrioridades()`) e rodei na base para validar empiricamente que apenas 5% dos deals se qualificavam como quadrante A antes de adotar a régua.

**Refinamento dos prompts do Gemini para respostas curtas.** Primeira versão vinha longa demais. Iteramos para travar saída em 3 frases numeradas, máximo 80 palavras, tom consultivo executivo. Também trocamos do modelo `gemini-flash` para `gemini-flash-lite` e adicionamos `generationConfig` explícito (`maxOutputTokens: 250`, `temperature: 0.4`) para acelerar de 8-15s para 2-4s.

**Iterações de UX e design.** Primeira versão do layout foi rejeitada por parecer "genérica de consultoria". Redesign na direção "Attio/Pipedrive vibe": cards densos, tipografia forte, uso parcimonioso de cores. Reaproveitamento do design system da Garô Consultoria (paleta petróleo + laranja, tipografia Manrope, breadcrumb com separador rotacionado).

**Resolução de bug crítico.** Uma conta chamada "Gekko & Co" (existente no dataset) deixava a página inteira em branco porque o `&` no atributo `data-value` do dropdown de filtros era interpretado como início de entidade HTML mal-formada. Diagnóstico feito escrevendo função `checarNomes()` que varreu os 8.800 registros e retornou apenas 1 nome com caracteres especiais. Correção: escape explícito de `&`, `<`, `>`, `"`, `'` em toda concatenação de HTML.

**Deploy final.** Discussão sobre manter URL fixa entre deploys do Apps Script. Solução adotada: site simples no Netlify (`desafio-g4-003.netlify.app`) com HTML+iframe apontando para a URL do Apps Script. Assim a URL do Netlify permanece fixa, e atualizações do backend são feitas via "Manage deployments → New version" no Apps Script (mantendo a URL de deploy).

**Estruturação da submissão.** Discussão sobre como organizar os arquivos seguindo o template oficial do G4, o que colocar no README, no process log, e como abrir o Pull Request.

## Observação sobre imagens no chat

A conversa contém alguns screenshots que enviei para debug de bugs e para orientar sobre a interface do GitHub durante a submissão. Não contêm informação sensível — são apenas screens de tela do próprio GitHub e de erros do console do navegador.
