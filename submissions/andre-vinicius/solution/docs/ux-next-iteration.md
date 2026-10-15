# Foco — próxima iteração de experiência

## Problema observado

O protótipo já ordena oportunidades e explica sua regra, mas uma pessoa que chega pela primeira vez precisa ler a documentação para entender onde começar. No celular, a visão por filas concentra filtros, cartões e detalhes demais na mesma tela. Esta é uma proposta de evolução; as funções abaixo ainda não estão implementadas.

## Primeiro contato com o produto

A entrada deve responder três perguntas em ordem: **o que merece minha atenção**, **qual ação tomar** e **por que essa oportunidade entrou na fila**. Um painel inicial resume Avançar, Revisar e Qualificar, mostra sinais de atenção com contagens e leva à carteira já filtrada. O vendedor vê seu recorte; a visão de gerente pode percorrer equipe e regiões quando houver autorização por perfil. No protótipo público, sem autenticação, os controles são filtros de demonstração e não permissões reais.

No celular, abrir uma fila por vez. Cada cartão mostra conta, motivo principal, índice e próxima ação; o restante fica no detalhe. Busca e filtros adicionais ficam acessíveis sem ocupar a primeira dobra. A opção de quadro continua somente leitura: trocar de coluna visual não muda etapa, proprietário ou prioridade.

## Região e rota

Um seletor visual de regiões deve abrir um resumo: quantidade por fila, sinais de tempo, vendedores da região e oportunidades para contato. O CSV informa `regional_office`, mas não coordenadas, endereços nem trajetos. Portanto, a primeira versão pode usar cartões ou um mapa esquemático, claramente rotulado como agrupamento regional. Traçar rotas reais exige localização confiável e outra fonte de dados; não deve ser inferido a partir do nome da região.

Preço de catálogo, clima e fatos externos podem aparecer numa camada futura de contexto. Uma fonte externa precisa mostrar data e origem. Nenhum desses sinais entra silenciosamente no índice atual; preço de catálogo já tem um bônus explícito de 10 pontos e não representa receita prevista.

## Índice em duas camadas

**Leitura do usuário:** “Revisar: 112 dias desde o engajamento, acima do limite de 90 dias. Próxima ação: confirmar interesse e registrar uma data para o próximo passo. Índice 70/100 nesta fila.” A frase deve usar os dados reais da oportunidade; o exemplo é apenas ilustrativo. O índice ordena atenção dentro da fila, sem representar chance de fechamento nem desempenho do vendedor.

**Como foi calculado:** mostrar, sob demanda, a composição verificável do `scoring.py`: base da fila (Avançar 65, Revisar 50, Qualificar 35); +10 por conta identificada; +10 por preço de catálogo de pelo menos USD 4.000; +10 por até 30 dias na fila Avançar ou +10 por 180 dias ou mais na fila Revisar, limitado a 100. Explicar também a escolha do limite de 90 dias e as limitações. A interface deve gerar esta explicação a partir dos mesmos campos usados pelo cálculo, evitando texto que divirja do índice.

O atual título “Por que aparece aqui?” deve virar algo ligado à decisão, por exemplo **“Por que está em Revisar?”**. As razões precisam distinguir **entrada na fila**, **posição pelo índice** e **ação recomendada**. A página “Como funciona a prioridade” serve ao usuário; “Método de construção e validação” registra arquitetura, decisões, dados, testes e limites do desenvolvimento para quem quiser auditar o case.

## Sinais de atenção

Os sinais comparam o tempo desde a última data de engajamento registrada com a ação sugerida pela fila: até 90 dias em Engaging → Avançar; acima de 90 → Revisar; Prospecting → Qualificar. Acima de 180 dias pode receber destaque adicional, coerente com o bônus atual. Quando não há data, dizer “sem data de engajamento registrada” em vez de presumir ausência de contato.

Os dados do desafio formam um retrato histórico com referência em **31/12/2017**. A tela deve chamar esses itens de sinais no conjunto histórico, nunca alertas em tempo real. Não há data de próximo contato no CSV; logo, não é possível afirmar que alguém descumpriu uma ação agendada.

## Validação antes de expandir

Prototipar a entrada, o resumo regional e a carteira móvel em desktop e celular. Testar com uma pessoa sem leitura prévia dos documentos:

1. Identificar uma oportunidade para agir e explicar a ação sugerida.
2. Explicar a fila e o índice dessa oportunidade sem confundir o índice com probabilidade de venda.
3. Escolher uma região e um vendedor, chegar à carteira filtrada e voltar ao resumo sem perder o contexto.

Registrar passos, resultado esperado, resultado observado e capturas reais. Só então recortar as páginas extras de vendedor, gerente, preço e região. Notas, arrastar cartões e status manuais continuam dependentes de persistência, autoria e integração com CRM.
