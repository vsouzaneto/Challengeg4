# Prompt para explorar o design do Foco no Replit

Crie um protótipo web responsivo e navegável para **Foco**, ferramenta de priorização de oportunidades comerciais do desafio público G4 Lead Scorer 003. O público é um vendedor que abre o pipeline e precisa decidir sua próxima conversa em menos de um minuto. Gere uma interface utilizável com dados fictícios coerentes; não conecte a serviços, contas ou projetos pessoais.

## Comportamento real a preservar

- Há 2.089 oportunidades abertas no conjunto do case, distribuídas em três filas: **Avançar**, **Revisar** e **Qualificar**. Avançar reúne negócios engajados há até 90 dias; Revisar, os demais negócios engajados; Qualificar, os que estão em prospecção.
- Dentro de cada fila, um índice operacional de 0 a 100 ajuda a ordenar a atenção. Ele considera somente sinais observáveis: conta identificada, preço de catálogo como aproximação de impacto e tempo desde o engajamento. **Não é probabilidade de fechamento nem previsão de receita.**
- Cada oportunidade mostra conta ou “Conta não informada”, produto, vendedor, região, etapa, motivo da posição na fila e **próxima ação sugerida**. A ausência de conta nunca esconde a oportunidade.
- Há busca por conta, produto ou ID e filtros por vendedor, gerente e região. Mostre filtros ativos, total filtrado e um botão “Limpar filtros”.
- Os dados são históricos e fictícios; a interface deve deixar clara a data de referência de 31/12/2017. Não simule atualização em tempo real.

## Explore três propostas dentro do mesmo protótipo

1. **Fila de decisão (preferida):** lista priorizada com detalhes ao lado no desktop. O motivo e a próxima ação devem dominar o painel de detalhe.
2. **Mesa comercial:** tabela compacta, legível e ordenável com painel de detalhe ao selecionar uma linha. Priorize comparação rápida entre oportunidades.
3. **Visão por filas:** três áreas Avançar, Revisar e Qualificar, com contagens e indicação clara de ordem. Não crie arrastar e soltar: o usuário não altera a fila manualmente neste protótipo.

Inclua um seletor discreto para alternar as três propostas e uma nota curta, dentro do protótipo, sobre o benefício e o custo de cada uma. Não faça três skins da mesma tela: cada proposta deve testar uma hierarquia de informação diferente.

## Sistema visual e interações

- Estilo de produto de trabalho: azul e ardósia, tipografia muito legível, superfícies calmas e sinalização sem excesso de cartões. Evite verde como cor dominante, gradientes decorativos, gráficos sem função e aparência genérica de dashboard.
- Temas **Automático, Claro e Escuro**, com preferência persistida. Use tokens de cor, contraste de texto de pelo menos 4,5:1, foco de teclado visível e estados de hover/seleção que não dependam só de cor.
- No desktop, navegação lateral enxuta e área de trabalho ampla. No celular, lista e detalhe são telas separadas: tocar uma oportunidade abre o detalhe com botão **Voltar**, sem obrigar a rolar uma lista longa para encontrar a explicação.
- Os filtros devem funcionar de verdade no protótipo. Inclua estados de lista vazia, busca sem resultado e erro de carregamento demonstrável, com ação de recuperação. Botões sem função devem ser removidos.
- Use texto claro em português do Brasil: “Gerente”, “Próxima ação”, “Por que aparece aqui?”, “Dados históricos”. Evite transformar o índice em selo “quente” ou “ganho provável”.

## Entrega

Entregue um protótipo interativo para desktop e celular, sem backend obrigatório, com dados fictícios locais e código simples de revisar. Ao final, explique qual das três propostas melhor responde à decisão do vendedor, o que muda no celular e quais partes são somente visualização. Não inclua sistemas internos, arquivos pessoais, nomes reais, segredos ou informação que não pertença ao case público.
