# Missões

queue.ts contém contratos de dia/vendedor, elegibilidade, lotes congelados, seleção, transições idempotentes, retornos após desfazer, totais, sequência e validação estrutural. Integração/persistência em ../../state/useDailyQueue.ts.

Seleção não conclui; adiamento não cumpre meta. Desfazer em lote anterior retorna por fila explícita. Dias e vendedores ficam isolados. Calendário operacional real é separado do scoring histórico.
