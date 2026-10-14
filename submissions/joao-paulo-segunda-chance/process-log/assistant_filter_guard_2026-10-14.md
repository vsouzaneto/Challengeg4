# Conferência dos filtros explícitos do assistente — 14/10/2026

Autorizei a implementação após a revisão de prompt injection. Um modelo ainda poderia selecionar uma ferramenta tipada com setor ou país diferente do nome que escrevi; a evidência tornaria o recorte visível depois da resposta, mas o cálculo já teria ocorrido sobre o segmento errado.

## Implementação

No domínio canônico `web/domain/assistant.mjs`, o servidor extrai da pergunta atual nomes inteiros presentes no catálogo limitado de setor e país da versão. A comparação ignora maiúsculas/minúsculas e normaliza Unicode; nomes como `Tech` não coincidem com o trecho de `EdTech`. A consulta escolhida pelo modelo é normalizada e, antes do SQL, comparada aos nomes explícitos. Uma divergência, inclusive filtro nulo, retorna esclarecimento fixo sem consulta. Dois nomes de uma mesma dimensão também retornam esclarecimento para pedir um recorte por vez. A ambiguidade tem prioridade mesmo quando há outra divergência. Uma pergunta sem nome reconhecido segue o fluxo existente.

O modelo faz a mesma chamada única; não há nova chamada, migração, alteração no frontend nem mudança na versão de instruções `1.1.0`. Não foram alteradas permissões, contas ou fatos. A validação reconhece nomes exatos do catálogo seguro enviado ao modelo e presentes na pergunta atual. Não resolve sinônimos, abreviações ausentes do catálogo, correferência ao histórico nem manipulações sem nome explícito reconhecido; o recorte e a evidência continuam disponíveis ao usuário nos casos permitidos.

## Verificação e publicação

- 12 testes de domínio aprovados, incluindo divergência de setor/país, omissão de filtro, dois nomes, limites de palavra, acentos, caso e bloqueio da função de consulta.
- 47 testes de interface/adaptadores aprovados; `npm run check` e `node --check` sem erros. Pacote gerado pelo empacotador canônico, SHA256 local `2cc9e1715fbfc328aaab17e034b979e2bebac0c3098f194562a2ce7af736d464`.
- Edge `challenge-assistant` ACTIVE v8 com `verify_jwt=true`; conteúdo recuperado após publicação idêntico ao pacote local. Os guardas HTTP anônimos constam do teste separado.

Os testes da escolha do modelo e do SQL usam simulações; não foi feita uma nova pergunta autenticada ao provedor nessa rodada. A PR permanece não aberta por minha orientação.
