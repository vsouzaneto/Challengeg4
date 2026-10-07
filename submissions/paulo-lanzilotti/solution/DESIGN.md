# Design system

## Direction

Uma ferramenta de trabalho vista por um vendedor em uma manhã de escritório iluminado: a atenção vai para a fila e para o próximo passo. Tema claro, composição contida e uma única cor de ação.

## Tokens

- Background: `oklch(1 0 0)`
- Surface: `oklch(0.978 0.003 260)`
- Ink: `oklch(0.245 0.016 260)`
- Muted ink: `oklch(0.48 0.012 260)`
- Line: `oklch(0.91 0.006 260)`
- Primary: `oklch(0.42 0.161 260)`
- Primary hover: `oklch(0.35 0.145 260)`

Use uma estratégia de cor restrita. A cor primária aparece em seleção, foco e ação. Sem decoração em gradiente.

## Typography

Fonte de sistema sans-serif, com escala compacta para produto. Títulos de 25 a 30 px; corpo entre 14 e 16 px; metadados a 12 ou 13 px. Números com alinhamento tabular.

## Components

- Header do portfolio-lanzilotti: marca tipográfica pl., Mona Sans local, fundo cinza claro e navegação externa. Altura de 100 px no desktop, sem seletor de idioma nem controle de animação.
- Filtros como abas textuais, sem preenchimento pesado.
- Lista de oportunidades com uma divisória por linha.
- Painel de detalhe com hierarquia de título, próximo passo e contexto.
- Campos de busca e seleção com altura mínima de 42 px.
- Raios de 10 a 12 px para controles e superfícies; botões de filtro de segmento usam a mesma escala.

## Responsive

Em telas largas, lista e detalhe lado a lado. Abaixo de 900 px, detalhe vem após a lista e recebe foco visual quando uma linha é selecionada.
