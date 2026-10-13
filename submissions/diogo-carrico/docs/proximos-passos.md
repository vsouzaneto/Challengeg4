# Próximos passos sugeridos

> **Nota.** Os itens abaixo foram planejados e em parte preparados, mas saíram do escopo final por decisão do Diogo (decisão D13 em `process-log/decisoes.md`). O desafio prevê de 4 a 6 horas, e o guia da G4 aponta "documento de 40 páginas onde 5 resolveriam" como sinal fraco. A entrega ficou com o que responde ao Diretor; estes itens ficam como sugestão para análise posterior, com o que já existe e como continuar.

## 1. Quanto do erro do classificador é rótulo errado (X1)

- **Por que importa.** Os classificadores das submissões públicas ficam entre 84% e 87%. Se parte do erro restante vier de rótulos errados, trocar de modelo não ajuda: o que melhora o resultado é revisar os rótulos.
- **O que já existe.** 105 grupos de textos quase iguais (617 tickets) têm rótulos diferentes. A lista está em `solution/outputs/classifier/near_duplicate_conflicts.csv`.
- **Como continuar.** Revisão cega de cerca de 150 casos: 120 erros do modelo e 30 quase-duplicatas. O revisor vê as duas opções (rótulo original e previsão do modelo) em ordem sorteada. A fração em que ele escolhe a previsão do modelo estima a parte do erro que é ruído de rótulo. A previsão P4 do Diogo é de cerca de 20%.
- **Esforço.** Cerca de 1 hora de revisão humana, mais a análise.

## 2. Rascunhos de resposta em pt-BR, avaliados (X2)

- **Por que importa.** Das 38 submissões públicas do Challenge 002, 25 dizem gerar rascunhos de resposta, e só uma mediu a qualidade de algo gerado. É também o uso de IA generativa que a vaga mais valoriza.
- **O que já existe.** A política de escalonamento (o que a IA nunca responde sozinha), na proposta de automação.
- **Como continuar.** Uma base de conhecimento curta, escrita pela empresa; um conjunto de 60 a 100 mensagens, incluindo casos difíceis de propósito (pedido de reembolso, ameaça de Procon, tentativa de manipular a IA); avaliação humana com rubrica (aprovado sem edição, aprovado com edição, rejeitado) e um LLM juiz como segunda opinião, medindo a concordância entre os dois. A previsão P8 do Diogo é de cerca de 65% aprovados sem edição.
- **Atenção aos dados.** Planos gratuitos que usam os dados para treino, como o do Google AI Studio, só servem para dados públicos ou escritos para o teste. Com dados de clientes, é preciso um plano pago com acordo de tratamento de dados (ver a seção de custos dos termos de referência).
- **Esforço.** Cerca de 1 dia.

## 3. Comparação com embeddings e LLM, e teste em português

- **Por que importa.** O protótipo usa só TF-IDF. Numa operação brasileira os tickets chegam em português, e o modelo atual aprendeu com tickets em inglês. Hoje o guarda de domínio manda esse texto para humanos, o que é seguro mas não automatiza nada.
- **Como continuar.** No mesmo conjunto de teste, comparar embeddings multilíngues rodando localmente (sem custo) e um LLM com poucos exemplos, com teste de McNemar, custo e tempo de resposta por 1.000 tickets. Medir a queda com uma amostra traduzida para português e com tickets escritos à mão. A previsão P6 do Diogo é de cerca de 40 pontos percentuais de queda sem adaptação. Ressalva: o texto do Dataset 2 vem pré-processado (sem pontuação, só minúsculas), o que tende a desfavorecer os LLMs.
- **Esforço.** Cerca de meio dia.

## 4. Antes de qualquer uso em produção

- Retreinar o classificador com tickets da própria operação: o modelo atual aprendeu com tickets de TI de outra organização.
- Instrumentar a operação (lista em `docs/diagnostico.md`, seção "O que medir numa operação real").
