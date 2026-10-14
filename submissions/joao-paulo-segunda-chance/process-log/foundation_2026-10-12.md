# Registro parcial — fundação de dados

Registro escrito da sessão; não se apresenta como export integral de conversa.

## Autorização

Aprovei avançar nas etapas da fundação, com Supabase dedicado e versionamento no fork. Mantida a orientação de não abrir PR ou pedir revisão antes da entrega estar pronta.

## TDD e desenvolvimento

1. Escrever nove testes de contratos antes de `domain/source_contracts.py`; a primeira execução falhou por módulo inexistente.
2. Implementar parser puro de tipos/obrigatoriedade; os nove testes passaram, totalizando 26 testes Python.
3. Escrever teste de existência/RLS antes de criar schemas; falhou no banco vazio.
4. Gerar e aplicar migrações; teste de schemas e privilégios passou.
5. Preservar arquivos e linhas, separando representação recebida e normalizada. Conferir contagens e SHA-256.
6. Escrever teste de imutabilidade com troca de parent IDs. O teste demonstrou que a primeira proteção conferia somente o parent novo; fortalecer para conferir ambos. O teste passou depois da correção.
7. Testar RLS com identidades sintéticas e rollback: leitor autorizado vê apenas seu workspace, não membro não vê dados, raw e importação privilegiada permanecem negados.
8. Um fixture de RLS tentou inserir snapshot num run já finalizado e foi corretamente rejeitado; corrigir ordem do fixture para construir antes de finalizar.
9. A primeira finalização excedeu o tempo de resposta. Inspecionar estado antes de retomar, sem presumir commit. Separar materialização da candidata e publicação, otimizar idempotência para não tentar inserir novamente registros já materializados.
10. Uma revisão automática bloqueou a materialização por interpretar a candidata vazia como risco de substituir dados ativos. Leituras de fontes verificadas e definição da função comprovaram que a origem era não vazia e que a função não mudava o ponteiro ativo. Nova execução foi aceita.
11. Publicar somente após conferências, reproduzir reconciliação via SQL e comparar com auditor.
12. Teste de referência futura foi escrito antes da proteção, falhou, e passou após bloquear datas além do período observado. Não equiparar maior data à completude da extração.
13. Testar falha de publicação: candidata incompleta não altera a versão ativa. Fixtures são revertidos.
14. A revisão automática rejeitou replay de uma fonte real verificada. Usar alternativa materialmente mais segura: replay em fonte sintética transacional com rollback. O teste comprovou zero novas linhas/chunks na reapresentação.
15. Security Advisors retornaram sem avisos. Resolver índices de FKs; índices novos ainda sem tráfego mantidos por sustentarem relações e consultas futuras.

## Limites e decisões

- Não inventar eventos ausentes, datas de mudança ou cobertura de telemetria.
- Não modificar arquivos originais nem eliminar conflitos silenciosamente.
- Não gerar risco preditivo ou probabilidade a partir de medidas sem cobertura.
- A receita é contratual, exclui trials e não equivale a perda prevista ou caixa.
- CSVs pequenos têm bytes preservados no banco privado no bootstrap; Storage/Excel e UI de preview pertencem ao adaptador web seguinte.
- Operações tem schema, mas decisões/ações no site ainda não estão implementadas.
- A carga foi executada pela conexão Supabase autorizada; o CLI REST não foi chamado com chave privilegiada nesta sessão.
- Fonte, payloads, resultados detalhados e segredos não são publicados no GitHub. Código e fixtures sintéticas são versionados sem PR.
