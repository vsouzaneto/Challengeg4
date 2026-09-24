# Acessibilidade — Lead Scorer · Vendas

Meta: **WCAG 2.2 AA**. Contraste está provado em `design-tokens.md` §2; este documento cobre teclado, foco, semântica e independência de cor.

## 1. Regras de independência de cor

1. **Direção de razão** = ícone + texto + cor. `▲`/`▼`/`ℹ` são caracteres reais no DOM com `aria-hidden="true"`, acompanhados de `<span class="sr-only">` com "Aumenta o score" / "Reduz o score" / "Informativo". O sinal do peso (`+9`, `−2`) reforça.
2. **Tier** = letra sempre visível dentro do badge; `aria-label="Tier A — quente: agir esta semana"`.
3. **Confiança** = ícone ●/◐/○ + palavra ("Confiança alta"); nunca só o ícone.
4. **Zumbi/risco** = ícone ⏳ + "121 dias" + texto da razão; a cor burgundy é redundante.
5. **Estado de ação** (Contatado hoje) = texto no selo; cor apenas decorativa.
6. Gráficos da tela Qualidade: barras rotuladas com o valor **dentro/ao lado** (`7,4 de 10`), e tabela equivalente acessível (`<table>` visualmente oculta ou toggle "ver como tabela"). Intervalo de confiança descrito em texto (`[6,8–8,0]`), não só como barra cinza.
7. Nenhum link identificado só por cor: links dentro de texto têm sublinhado.

## 2. Estrutura semântica (landmarks)

```
<header>            wordmark (h1 visual só na home? não — wordmark é <p>; cada tela tem UM <h1>)
  <nav aria-label="Seções">  Fila · Time · Qualidade  (aria-current="page")
<aside aria-label="Filtros e referência">   sidebar
<main>              conteúdo da tela; <h1> = título da tela
<footer>            referência as-of · modelo
<aside role="dialog" aria-modal="true" aria-labelledby="deal-title">  drawer (montado no fim do body)
```

- Um único `<h1>` por tela ("Sua fila de hoje"); wordmark no header é `<p>` com `aria-label="Lead Scorer · Vendas"`.
- Ordem de heading sem saltos: h1 tela → h2 seções ("Por que este score", "Por vendedor") → h3 nos tiles.

## 3. Fila do vendedor (home)

### 3.1 Semântica
- Lista de deals: `<ol aria-label="Deals por prioridade">` com `<li>` → `<article aria-labelledby="deal-{id}-title">`. `<ol>` porque a ordem **é** a informação.
- Dentro do `article`: o título é um `<button>` (ou `<a href="?deal=…">`) que abre o drawer; o restante da linha é clicável por JS **mas** o alvo acessível é esse botão. `aria-describedby` aponta para score, valor e motivo.
- CTA "Registrar conta" é `<button>` separado, com `aria-label="Registrar conta de {product} no CRM"`; `stopPropagation` para não abrir o drawer por engano.
- Tiles: `<a>` com texto completo ("4 deals quentes para agir esta semana — ver deals").
- Aviso de ordenação secundária: `role="status"`.

### 3.2 Ordem de foco (Tab)
1. Skip link "Ir para a fila" (visível ao focar) → `#main`.
2. Nav: Fila → Time → Qualidade.
3. Pílula de status da API (não focável; `role="status"`).
4. Sidebar: Região → Manager → Vendedor → chips ativos (cada × é botão) → Limpar filtros → Dados até.
5. Conteúdo: Top N → Ordenação → tiles (3) → linha 1 (botão-título → CTA conta, se houver) → linha 2 → … → "Ver mais 10".
6. Rodapé (não focável).

Em telas < 1024 px, o botão "Filtros (3)" entra antes do Top N e abre o painel como `dialog` com focus trap.

### 3.3 Teclado
| Tecla | Onde | Efeito |
|---|---|---|
| `Enter` / `Space` | botão-título da linha | abre drawer |
| `↓` / `↑` | dentro da lista (roving tabindex opcional) | move foco entre linhas; Tab sai da lista |
| `Esc` | drawer / painel de filtros | fecha e devolve foco |
| `Home` / `End` | lista | primeira / última linha |
| `Delete` | linha focada | **não** descarta (ação destrutiva exige o botão no drawer) |

Selects nativos (`<select>`) para filtros: teclado e leitor de tela gratuitos; sem combobox customizado no MVP.

## 4. Drawer de detalhe

- `role="dialog" aria-modal="true" aria-labelledby="deal-title" aria-describedby="deal-summary"`.
- Ao abrir: foco vai para o `<h2 id="deal-title" tabindex="-1">`; `body` recebe `overflow:hidden`; conteúdo atrás recebe `inert` (ou `aria-hidden="true"` no `#root` principal).
- **Focus trap**: Tab no último elemento volta ao primeiro (botão ×); Shift+Tab no primeiro vai ao último.
- Ordem interna: × Fechar → (conteúdo rolável, não focável) → link "Registrar conta" (se houver) → Contatado → Reunião marcada → Proposta enviada → Descartar → Conta corrigida → "desfazer" (quando existir).
- Ao fechar (×, `Esc`, clique no scrim, Voltar do navegador): foco retorna ao botão-título da linha de origem; se a linha foi descartada, foco vai para a linha seguinte (ou para o h1 se não houver).
- Lista de razões: `<ul aria-label="Razões do score">`; cada `<li>`: `<span class="sr-only">Aumenta o score, 9 pontos.</span> Você fecha 74%…`.
- Botões de ação: `role="group" aria-label="Registrar o que você fez"`; botão ativo com `aria-pressed="true"`. Confirmação de Descartar: aparece inline com `role="alertdialog"` leve (texto + Confirmar/Cancelar), foco no Cancelar.
- Estado otimista anunciado: `<div role="status" aria-live="polite">Registrado "Contatado" às 08:14</div>`. Erro: `role="alert"`.
- Rolagem interna: o container tem `tabindex="0"` apenas se a altura exceder a viewport (para rolar por teclado).

## 5. Visão do manager

- Tiles: `<a>`; tabela por vendedor: `<table>` real com `<caption>` "Por vendedor, ordenado por valor em risco", `<th scope="col">`, `<th scope="row">` no nome. Linha inteira clicável via `<a>` na célula do nome (não `onClick` no `tr`).
- Coluna Carga: ícone ●●●○ com `aria-label="carga alta (61 deals; mediana do time 52)"`.
- Barra de tiers: `role="img" aria-label="Distribuição de tiers: A 22 %, B 27 %, C 26 %, D 25 %"` + legenda textual visível.
- Lista de zumbis: mesma semântica da fila (`<ol>`).

## 6. Visão da Head / qualidade

- Cada bloco é `<section aria-labelledby>` com h2-pergunta.
- Gráfico de barras: SVG com `role="img"` e `aria-label` resumindo ("Lead Scorer 7,4 de 10; mais novo primeiro 6,5…") **e** botão "Ver como tabela" que alterna para `<table>`. Valores impressos ao lado das barras.
- Calibração já é `<table>`.
- Frase-conclusão gerada (`quality.wins`/`quality.ties`) é `<p>` normal, lida antes do gráfico na ordem do DOM.

## 7. Estados

- Carregando: container `aria-busy="true"`; skeleton `aria-hidden="true"`; texto `sr-only` "Carregando sua fila…".
- Vazio / artefatos ausentes: `role="status"`; bloco de código `<pre><code>` + botão "Copiar comando" que anuncia "Copiado" via `aria-live`.
- Erro da API: `role="alert"`, botão "Tentar de novo" recebe foco quando o erro substitui conteúdo inteiro (não quando é faixa sobre dados antigos).
- Toasts: `role="status"` (sucesso) / `role="alert"` (erro); permanecem ≥ 6 s; pausam no hover/foco; sempre com botão de fechar.

## 8. Movimento, zoom, alvo

- `prefers-reduced-motion`: sem `animate-pulse`, sem transição do drawer.
- Layout funciona a 200 % de zoom e a 320 px de largura (cards em uma coluna; drawer 100 %).
- Alvos ≥ 40×40 px; × do chip 24×24 com `padding` para 40 px de área clicável (WCAG 2.5.8 mínimo 24).
- Sem limite de tempo; feedback otimista não expira sem confirmação.
- `lang="pt-BR"` no `<html>` (já existe). Números com `Intl` pt-BR.

## 9. Checagem automatizada sugerida

- `vitest` + `@testing-library/jest-dom` + `axe-core` (`vitest-axe`) em: home com dados, drawer aberto, estado vazio, artefatos ausentes.
- Lighthouse Accessibility ≥ 95 nas três telas.
- Teste manual: navegar toda a home só com Tab/Enter/Esc; VoiceOver no macOS lendo uma linha inteira ("Tier A, Prioridade 82 de 100, Konex GTX Pro, R$ 3.412 esperados, Confiança alta, Aumenta o score: Você fecha 74%…, Próxima ação: Ligar esta semana…").
