# Decisões

## 30/09/2026 — criação da base

- Seguir o Challenge 003 do plano, apesar do nome local da pasta. Preservar `Referencias/` e seus nomes originais para manter o arquivo indicado pelo usuário.
- Concentrar execução em `solution/` para permitir transporte para o fork oficial.
- Usar React, TypeScript, Vite, Tailwind e Vitest/Testing Library, com versões exatas e lockfile.
- Usar jsdom 26.1.0 para compatibilidade com o Node 22.14.0 disponível; a versão consultada 30.1.1 exigia Node 22.22.2+. Integrar Tailwind pelo plugin oficial do Vite.
- Exibir uma tela inicial de espera; oportunidades, scores, progresso e conquistas exigem dados e comportamento implementados.
- Definir contratos sem resultados futuros no candidato de scoring. Separar `activeOpportunityId` das ações e prever `returnQueue` para desfazer em lotes anteriores.
- Separar os dois relógios desde a base: histórico do scoring e calendário real em São Paulo.
- Preparar armazenamento versionado com fallback em sessão; validação de estado e integração na jornada serão próximas etapas.
- `prepare:data` começa como preflight de proveniência/hashes. Avaliação informa explicitamente que ainda não foi implementada.
- Nenhum download de dados, credencial, infraestrutura do CRM, remoto ou publicação é necessário para este marco.
