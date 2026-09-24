# Checklist de auto-revisão — application-engineer → product-designer

Marque cada item antes de pedir revisão. Referências: `ux-spec.md`, `design-tokens.md`, `accessibility.md`.

## Decisão antes de dados
- [ ] A home abre na fila do vendedor com top 10 já ordenado por `priority_score` (sem reordenar no cliente).
- [ ] Cada linha mostra, nesta ordem: tier · score · conta/produto · valor esperado · confiança · motivo principal · próxima ação · dias.
- [ ] `next_action` visível em todas as larguras (nunca truncado por completo).
- [ ] Exatamente 3 tiles na home; nenhum gráfico na home.
- [ ] Deal sem conta aparece com "Conta não informada" + CTA; nunca é ocultado.

## Contrato e dados
- [ ] Tipos vêm de `src/api/schema.d.ts` gerado (`make gen-api`); nenhum campo inventado.
- [ ] Nenhuma lógica de score/tier/urgência no web (só formatação e agregações de contagem/soma para tiles do manager, se o endpoint `summary` não existir).
- [ ] Datas e idades vêm do payload (`as_of`, `days_in_engaging`); nada usa `new Date()` para calcular idade de deal.
- [ ] Moeda `R$` sem centavos via `Intl.NumberFormat('pt-BR')`; percentuais inteiros.

## Estado e navegação
- [ ] `as_of`, `region`, `manager`, `agent`, `n`, `sort`, `deal` na URL; recarregar a página reproduz a tela.
- [ ] Mudar região limpa manager/vendedor; mudar manager limpa vendedor.
- [ ] Voltar do navegador fecha o drawer.
- [ ] Ação no drawer é otimista; falha reverte e mostra toast com "Tentar de novo"; `Descartar` pede confirmação inline e oferece "desfazer".

## Estados
- [ ] Carregando (skeleton), vazio (filtro), vazio (tudo descartado), artefatos ausentes (com `cd solution && make pipeline` copiável), erro da API (faixa + retry), métricas ausentes: todos implementados e testados com Vitest.
- [ ] Rodapé/faixa de referência "Dados até … · modelo …" visível em todas as telas.

## Design system
- [ ] Nenhuma cor hex fora de `tailwind.config.ts`; nenhuma cor nova sem linha de contraste em `design-tokens.md` §2.
- [ ] Dourado `#B9915B` nunca como texto sobre fundo claro; badge tier A com texto navy.
- [ ] Tiers C e D com fundo tinta (`Cbg/Ctext`, `Dbg/Dtext`), não texto branco sobre sólido.
- [ ] Texto secundário usa `g4-muted`, não `signal-neutral`.
- [ ] Serif só em h1 e wordmark; raio 10 px (20 px só no cartão de estado); grid de 8 px.
- [ ] Sem logo/imagem do G4; wordmark textual "Lead Scorer · Vendas".
- [ ] Toda string de UI vem de `src/i18n/pt-BR.ts`; nada hardcoded em pt-BR nos componentes.

## Acessibilidade
- [ ] Um `<h1>` por tela; landmarks `header/nav/aside/main/footer`.
- [ ] Toda a home operável só com Tab/Enter/Esc; ordem de foco = `accessibility.md` §3.2.
- [ ] Drawer: `role=dialog aria-modal`, foco inicial no título, focus trap, `Esc` fecha, foco retorna à linha.
- [ ] Direção de razão com ícone + texto `sr-only` + cor; tier com letra; confiança com palavra.
- [ ] `:focus-visible` com anel navy 2 px em todos os controles.
- [ ] `prefers-reduced-motion` respeitado.
- [ ] `axe` sem violações em: home com dados, drawer aberto, vazio, artefatos ausentes.
- [ ] Lighthouse Accessibility ≥ 95.

## Manager e Head
- [ ] Tabela por vendedor ordenada por valor em risco; sem coluna de posição/ranking; cada linha linka para a fila do vendedor.
- [ ] Definições de "em risco", "zumbi" e "conta informada" no rodapé da tela.
- [ ] Tela Qualidade: 4 blocos-pergunta, nada além; números lidos de `metrics.json`/endpoint, nenhum calculado no cliente; frase de conclusão usa `wins`/`ties` conforme o IC.
- [ ] Gráfico de barras com valores impressos e alternativa em tabela.

## Entrega
- [ ] `npm run lint`, `npm run typecheck`, `npm run test` verdes; `npm audit` limpo ou justificado.
- [ ] Screenshots das 4 telas + 3 estados em `process-log/screenshots/` para revisão visual do Bernardo (itens V1–V4 do `ux-spec.md` §11).
