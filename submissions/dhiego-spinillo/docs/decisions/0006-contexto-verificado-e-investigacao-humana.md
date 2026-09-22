# ADR 0006 — Contexto verificado e investigação humana

**Estado: implementado, após a revisão de três casos por Dhiego.**

## Problema

A categoria isolada não define o próximo passo. Um pedido pode já estar atendido, ter contexto em outro ticket ou relatar um possível incidente dentro de um assunto comum. O recap avaliado acrescentou detalhes e inferências que não sustentam adoção operacional.

## Decisão

Preservar a classificação local avaliada e acrescentar uma ficha de investigação preenchida pelo atendente: conferência de outros tickets, estado no sistema e notas internas; resultado conhecido ou desconhecido; relato de possível incidente acompanhado de trecho literal. Uma regra explícita deriva a orientação, persistida junto à decisão e motivo.

A ordem padrão é conferir contexto antes de novo contato. Se o atendimento está resolvido, orientar confirmação de necessidade restante; se pendente, atualizar diagnóstico e evidências para escalonamento; se desconhecido, recuperar contexto sem presumir resolução ou pendência. Um relato de possível incidente destaca investigação do relato e eventual consulta a logs com Segurança/Engenharia, sem exigir primeiro completar conferências rotineiras nem definir automaticamente causa ou severidade.

## Fronteiras

- A ficha registra declarações do atendente; não consulta sistemas, tickets relacionados, notas ou logs. “Não verificado” e “indisponível” não significam “não existe”.
- O relato de incidente é marcado pelo humano e sustentado em trecho do ticket. Não é um detector automático avaliado. A citação comprova origem, não ocorrência do incidente.
- Não há fechamento, mensagem enviada, abertura de incidente externo ou concessão de acesso. A categoria não muda automaticamente por existir sinal de incidente.
- Regra de próximo passo é aplicada no servidor; o LLM não inventa a justificativa da decisão.
- Recap continua experimental e desligado por padrão. O prompt avaliado permanece preservado; esta alteração não melhora retroativamente suas métricas.
- A ficha é restrita ao próximo passo e não implementa o roadmap de flags, churn ou priorização geral.

## Validação

Testar caminhos resolvido/pendente/desconhecido, conferências incompletas/indisponíveis, incidente independente de categoria, origem literal do relato, persistência, exportação e preservação dos registros antigos. Testes funcionais demonstram o contrato; benefício operacional ainda exige comparar o atendimento com e sem assistência. Os três exemplos orientam desenvolvimento, não nova avaliação independente.

## Sugestão de resposta

Dhiego perguntou se a sugestão de resposta entra nesta etapa. Foram incluídos três modelos de texto por regra: confirmação de necessidade restante, atualização do diagnóstico e esclarecimento de relato de possível incidente. O texto fica editável para revisão/cópia; a versão editada é salva localmente junto à decisão. Não há envio automático.

Resultado desconhecido ou conferências rotineiras pendentes não liberam o rascunho de resolução/diagnóstico. Relato de incidente permite preparar esclarecimento sem esperar completar consultas rotineiras. Uma mensagem que afirma consulta realizada depende de declaração de conferência do atendente; o sistema não verifica o fato em uma integração externa.

A classificação continua sendo o componente de IA avaliado. A ficha, o próximo passo e os modelos de resposta são regras determinísticas. A qualidade do recap não foi reavaliada nem promovida por esta alteração.
