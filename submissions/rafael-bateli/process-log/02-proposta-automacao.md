# Process log — Entrega 2: Proposta de automação com IA

**Ferramenta:** Claude Code (app desktop, modelo Claude Opus), em worktree git isolado a partir da branch da Entrega 1.
**Iterações:** 1 rodada de exploração dos dois datasets, 1 de construção do script e do documento, 1 de verificação dos números contra o dado.

---

## 1. Como enquadrei o pedido antes de pedir à IA

Retomei o contexto do Diretor e dei três instruções:

1. **Separar determinístico de probabilístico (LLM)**, e justificar cada decisão com o critério que decidiu: custo, horas, impacto × esforço ou outro.
2. **Dar exemplos dos dados**, como o desafio pede, e não exemplos genéricos.
3. **Usar a Entrega 1 só onde fosse necessário**, sem refazer o diagnóstico.

Mantive as regras da Entrega 1: 3 opções por decisão, número vindo de script, e verificação antes de afirmar.

## 2. O que a exploração dos dados mudou na proposta

| Achado | Onde | O que mudou |
|---|---|---|
| O texto do Dataset 1 é montado por **templates**: 15 aberturas de problema e ~25 frases de contexto; **69%** só dizem "estou com problema no {produto}" | Dataset 1 | A maior automação virou **coleta de dados determinística**, e não "IA resolve". Ninguém resolve o que não foi descrito |
| **34%** dos clientes já fizeram o troubleshooting básico; **186** dizem que a redefinição de senha não funciona | Dataset 1 | Macro fixa e link de redefinição, as automações "óbvias", foram rejeitadas com evidência |
| **139 e-mails repetidos, 100% de pessoas diferentes** (`asmith@example.com` = 4 pessoas) | Dataset 1 | Duplicata por e-mail foi descartada; a escolha foi `customer_id` + similaridade |
| Regras de palavra-chave, **no melhor caso**, param em **80%** de acerto; o modelo chega a **98%** na mesma cobertura | Dataset 2 | Justificativa quantitativa para classificação probabilística (supervisionada) em vez de regra |
| **149 alertas de máquina idênticos em 5 classes** | Dataset 2 | Exemplo de onde a IA **não** deve entrar: uma regra de assinatura resolve |
| Custo total de LLM ≈ **R$ 270/ano** | Preços da API | Custo de token saiu do critério de decisão; custo do erro entrou no lugar |

## 3. Onde a IA errou e como foi corrigido

| # | Erro | Como percebi | Correção |
|---|---|---|---|
| 1 | **Rota errada para tickets genéricos.** A primeira versão mandava para o copiloto todo ticket com "já tentei o básico", mesmo quando o problema não estava descrito. Resultado: 46% no copiloto | Um ticket que só diz "fiz reset de fábrica" continua sem o problema, e a LLM não teria o que redigir | "Já tentou o básico" e "incidente" viraram **marcações**, e não rotas. Copiloto caiu para 12%; coleta automática, 55% |
| 2 | **Verificação com corte arbitrário.** A V5 comparava o custo de LLM com "5% de 1.000 h", um número sem significado, e falhou | Um teste que falha por um limite inventado não prova nada | V5 passou a comparar o custo com **o ganho que a própria LLM gera** (horas do copiloto) |
| 3 | **Título de gráfico exagerado:** "regras fixas entregam metade do ganho" | Recalculei: 1.373 de 3.473 h = **40%** | O título passou a ser **calculado no código** |
| 4 | **Soma de motivos tratada como união:** "segurança e conta bloqueada (600)", "hardware (≈ 950)" | Conferência dos números citados contra o dado | Uniões medidas: **592** e **1.005**; o script passou a exportá-las |
| 5 | **Exemplo com prioridade que a regra da Entrega 1 não sustenta:** #1608 como *Critical* | A regra de urgência da Entrega 1 não reconhece "I rely heavily" | Troquei por **#7971**, que a fila da Entrega 1 já marca como *Critical* |
| 6 | **Número citado sem vir do script:** latência de 0,05 ms, medida só na exploração | Regra da entrega: todo número vem do script | Latência passou a ser medida e gravada em `automacao.json` |
| 7 | **Rótulos de gráfico sobrepostos e títulos cortados** | Inspeção visual dos PNGs | Posições e títulos ajustados; os três gráficos foram conferidos de novo |

## 4. O que eu adicionei que a IA sozinha não faria

- **Determinístico × probabilístico como eixo da proposta.** Sem isso, o default seria "LLM para tudo".
- **Exigir o critério de cada decisão** (custo, horas, impacto × esforço). Foi isso que expôs que o custo de token é irrelevante e que o critério real é o custo do erro.
- **Exemplos do dado, com ID do ticket.** Obriga cada "não automatizar" a apontar um caso concreto.

## 5. Decisões que tomei sobre o que a IA propôs

- Aceitei que **33% dos tickets vão direto para humano**, mesmo parecendo muito. O custo do erro é assimétrico, e o desafio avisa que automatizar 100% é red flag.
- Aceitei **não** medir a acurácia da LLM nesta entrega (sem chamada de API) e deixar isso explícito como limitação. Por isso toda LLM da proposta começa com humano aprovando.
- Aceitei manter a comparação de regras **no melhor caso** (palavras escolhidas olhando o treino), porque ela favorece a opção que perdeu e torna a conclusão mais forte.
