# Protocolo do Agente Juiz

Toda conclusão relevante do projeto passa por um agente revisor independente antes de entrar na entrega final.

## Princípios
1. **Contexto limpo:** o juiz é um subagente novo. Ele não vê a conversa, o raciocínio nem o código que produziu a conclusão, só as afirmações e os dados brutos.
2. **Recalcular, não reler:** cada afirmação numérica é recomputada pelo juiz com código próprio, a partir dos CSVs originais.
3. **Postura adversarial:** o objetivo do juiz é encontrar erro, exagero ou explicação alternativa. Não é concordar.
4. **Veredito por afirmação:**
   - `CONFIRMADA`: o número e a interpretação batem.
   - `CONFIRMADA COM RESSALVA`: o número bate, mas a redação exagera ou omite um contexto relevante.
   - `REFUTADA`: o número ou a lógica estão errados.
   - `NÃO VERIFICÁVEL`: não há como checar com os dados disponíveis.
5. **Rastreabilidade:** o parecer fica salvo em `process-log/revisoes/`, e toda correção decorrente é registrada no PROCESS_LOG.

## O que o juiz sempre checa
- O número está correto?
- A interpretação decorre do número, ou existe outra explicação plausível?
- A redação é proporcional à evidência (nem mais forte, nem mais fraca)?
- Há confusão entre correlação e causalidade?
- Um executivo poderia tomar uma decisão errada lendo isso?
