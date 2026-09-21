# Recorte para discussão — triagem assistida

**21/09/2026. Proposta de Codex, ainda não escolhida por Dhiego.** Leitura da análise visual concluída pelo candidato; dúvidas, revisão multimodelo e escolha final permanecem abertas.

## Tese

Testar se é possível apoiar a compreensão e o encaminhamento inicial de tickets, mantendo regras e decisão humana explícitas. Os sinais do D1 motivam a investigação, mas não demonstram a frequência real de falhas de atendimento nem horas recuperáveis. O D2 permite avaliar classificação no seu próprio domínio e explorar sínteses dos textos disponíveis.

## Entrega recomendada

1. **Diagnóstico:** reutilizar a análise visual, com contagens, limites por pergunta e instrumentação necessária. Não afirmar gargalo temporal, causa da insatisfação ou horas perdidas sem evidência.
2. **Classificação mensurável:** receber texto do domínio do D2, prever uma das oito categorias e apresentar indicação de incerteza avaliada. Comparar uma abordagem simples com a classe majoritária; separar treino, validação e teste, revisar quase duplicatas e reportar erros por classe. Se houver regra de abstenção, escolher seu limiar na validação e medir cobertura e erros no teste.
3. **Recap assistido:** gerar pedido, tentativas relatadas, pontos em aberto e próximo passo sugerido, preservando incerteza e vinculando afirmações à origem. Não afirmar ordem/autoria de mensagens sem evidência. Avaliar separadamente da classificação.
4. **Uma tela de atendimento:** texto original ao lado da categoria e recap, com correção pelo atendente. Se exibido encaminhamento, usar mapa de filas demonstrativo e explícito; categoria não concede autorização para executar acesso, reembolso ou outras ações.

Classificação é o núcleo com avaliação disponível; recap é a hipótese de valor adicional ligada às provocações do candidato. Comparar esse conjunto com as alternativas menores: só classificação ou só recap. Não tratar a combinação como decisão já tomada.

## Como demonstrar valor

- **Classificação:** métricas no teste reservado, comparação com referência simples, desempenho por classe e exemplos de erro. A categoria do dataset é referência sujeita a ruído; não equivale a validação de toda a política de atendimento.
- **Recap:** critérios de fidelidade, cobertura dos pedidos, preservação de tentativas e incerteza; amostra com variedade de comprimento/assunto, revisada pelo candidato. Separar exemplos usados para ajustar o prompt daqueles usados para avaliação. Revisão de Codex sozinho não é validação independente.
- **Operação:** ganho permanece hipótese até comparação de trabalho humano com e sem auxílio. Fórmula possível: tickets elegíveis × diferença medida de tempo ativo / 60, descontando esforço adicional de revisão/correção. Antes dessa medição, apresentar apenas cenários identificados e premissas, sem economia observada.
- **Reprodução:** entrada editável, execução real, instruções, capturas e limites. Os cinco exemplos preparados na análise não bastam como avaliação do protótipo.

## Fora do primeiro recorte recomendado

Autorresposta, execução automática de ações, previsão de churn, jornada por email, SLA inferido dos timestamps atuais e uso de Resolution como base confiável de respostas. Sugestões de resposta, sentimento e flags avançadas continuam extensões a discutir. Jev/TypeSafe é candidato opcional de comparação, não dependência; não foi testado. Infraestrutura, banco e orquestração devem atender ao recorte escolhido.

## Próximo passo

Ouvir a leitura de Dhiego: qual problema considera prioritário e que conclusão contestaria? Em seguida, submeter diagnóstico e alternativas à revisão com Claude/Grok/Codex, permitindo que contestem esta proposta. Fechar escopo e critérios de aceite antes de construir. Nenhuma nova data de entrega foi combinada na retomada.
