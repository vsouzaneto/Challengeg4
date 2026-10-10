# Minha leitura do problema

_Bruno Mosconi, 09/10/2026. Escrito antes dos resultados da revisão inicial. Os números citados vêm do material de partida e ainda não foram conferidos._

**O problema de verdade.** A Head de RevOps não pediu um modelo. Ela pediu que 35 vendedores parem de priorizar "no feeling". Não falta dado; o que se perde é atenção. O vendedor gasta a segunda de manhã em negócios que já morreram e deixa esfriar os que ainda têm chance.

**A decisão que a ferramenta apoia.** É uma pergunta, toda segunda: "em quais negócios eu ponho energia esta semana, e por quê?". Se o vendedor não entende por que um negócio está no topo, não confia na lista, e ninguém segue uma lista em que não confia. Por isso, explicar vem antes de ganhar a última casa decimal de precisão.

**O que o score precisa medir.** Quanto o negócio vale considerando a chance de virar venda: o valor ponderado. Só o valor é o que o enunciado proíbe. Só a chance ignora o tamanho do prêmio.

**O que desconfio dos dados** (a confirmar na revisão):
- O funil parece inflado: boa parte do valor em andamento está em negócios parados há meses, que na história da base não viram venda.
- A taxa de ganho calculada só com os concluídos engana, porque esconde os negócios que nunca terminam. A chance precisa ser medida desde o início do negócio.
- Alguns campos parecem sinal, mas denunciam o desfecho. "Sem empresa", por exemplo, só aparece em negócio em andamento.
- Vendedor e produto talvez não mudem a taxa de ganho. Se for assim, ficam fora do score, por mais óbvios que pareçam.

**O que é sucesso:**
- O vendedor entende em 1 minuto onde focar e por quê.
- O gestor vê quanto do funil da equipe está parado.
- Testada no passado, a regra prioriza melhor do que ordenar por preço.

**O que decidi não fazer:**
- Machine learning só entra se ganhar com folga de uma regra que o vendedor entende.
- Não haverá LLM no app: a explicação sai do mesmo cálculo do número.
- Não haverá servidor nem banco: o volume não pede. A escala é mostrada com medição.

**Como vou saber se errei.** Todo número é recalculado antes de construir. A regra é comparada, no passado, com alternativas simples: preço e aleatório. Se não ganhar com clareza, a mensagem principal deixa de ser o ranking e passa a ser a limpeza do funil.