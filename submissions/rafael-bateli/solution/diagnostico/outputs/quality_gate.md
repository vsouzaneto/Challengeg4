# Quality Gate — resultado

Arquivo: `customer_support_tickets.csv`  
**Veredito: REPROVADO**, 1/12 regras OK, 7 bloqueantes em falha.

| Regra | Verificação | Severidade | Medido | Limite | Status | Dono | Correção |
|---|---|---|---|---|---|---|---|
| R01 | Horário de abertura presente | BLOQUEANTE | coluna inexistente | ≥ 99% | ❌ FALHA | TI / sistema de tickets | Gravar created_at pelo sistema na entrada do ticket (não editável). |
| R02 | Resolução depois da 1ª resposta | BLOQUEANTE | 49,3% | ≤ 0,5% | ❌ FALHA | TI / ETL | Validar created_at ≤ first_response_at ≤ resolved_at na gravação; rejeitar o evento fora de ordem. |
| R03 | Horários registrados por evento (não calculados) | BLOQUEANTE | 100% | ≤ 5% (acaso ≈ 1,7%) | ❌ FALHA | TI / ETL | resolved_at deve vir do evento 'ticket resolvido', não de uma fórmula sobre first_response. |
| R04 | Janela dos horários compatível com o volume | BLOQUEANTE | 27 h | ≥ 1.236 h (8.469 tickets a ~82/dia) | ❌ FALHA | TI / ETL | Horários concentrados em ~1 dia indicam carimbo de exportação. Exportar o horário do evento. |
| R05 | Descrição sem placeholder de template | BLOQUEANTE | 100,0% | ≤ 0,5% | ❌ FALHA | TI / integração de formulários | Corrigir o merge do template (product_purchased, error_message…); rejeitar texto com {…}. |
| R06 | Resolução com conteúdo de suporte | ALERTA | 3,0% | ≥ 80% | ❌ FALHA | Operações + TI | Resolução estruturada: código de solução (lista) + texto livre; alimenta a base de conhecimento. |
| R07 | Tipo coerente com o assunto | BLOQUEANTE | 34,6% | ≥ 90% | ❌ FALHA | Operações (taxonomia) + IA de triagem | Taxonomia única (assunto determina o tipo) preenchida pela triagem por IA. |
| R08 | Assunto bate com a descrição | BLOQUEANTE | 1,00× (18,3% vs acaso 18,3%) | ≥ 3× | ❌ FALHA | IA de triagem | Assunto definido pelo conteúdo (IA), não por quem abre o ticket. |
| R09 | Pedido urgente recebe prioridade alta | ALERTA | 52,5% (n=692) | ≥ 70% | ❌ FALHA | IA de triagem + Operações (SLA) | Prioridade = f(severidade do conteúdo, impacto declarado, cliente); não escolha livre. |
| R10 | Status coerente com os horários | BLOQUEANTE | 100% coerente | 100% | ✅ OK | TI / sistema de tickets | — |
| R11 | CSAT cobre toda a base | ALERTA | 32,7% | ≥ 60% (inclui abertos há > 7 dias) | ❌ FALHA | Operações / CX | Pesquisar também tickets abertos/pendentes há mais de 7 dias; incluir motivo + CES. |
| R12 | Um e-mail = um cliente | ALERTA | 139 | 0 | ❌ FALHA | TI / CRM | customer_id do CRM em todo ticket; permite medir recontato de verdade. |
