# Ficha de investigação e rascunhos — evidências

Capturas reais do protótipo local, com estados de conferência simulados explicitamente para QA. Nenhum sistema de férias, ticket relacionado, nota interna ou log foi consultado. Registros de QA têm motivo identificando Codex e a simulação.

- [Fluxo final em desktop](fluxo-final-desktop.png): situação pendente declarada, orientação e rascunho para atualizar diagnóstico. Após ajuste de altura da coluna de entrada.
- [Resposta após conferência declarada](resposta-conferencia.png): caminho de confirmação, antes do ajuste de altura da coluna de entrada.
- [Relato de incidente](incidente-desktop.png): categoria preservada e investigação baseada no trecho marcado pelo atendente. Antes do ajuste de altura da coluna de entrada.
- [Conferências no celular](conferencias-mobile.png) e [resposta no celular](resposta-mobile.png).

Inspeção em 1440×1000 e 390×844 sem transbordamento horizontal da página. Comparativo carregou, recap desmarcado não chama o provedor, rascunho fica ausente enquanto faltam conferências e decisão/rascunho são registrados sem envio. Os 147 testes verificam também persistência do rascunho editado, validação de evidência literal, fontes indisponíveis, compatibilidade de registros antigos e exportação sem texto original/trecho/rascunho. O botão de cópia tem fallback de seleção manual; nesta rodada não foi feita verificação do clipboard.

O detector visual encontrou estilos preexistentes e apontou cores claras sem considerar o fundo azul em alguns elementos. A inspeção considerou a renderização efetiva; não houve reformulação geral da identidade nesta etapa. Capturas e testes de contrato não medem benefício operacional.
