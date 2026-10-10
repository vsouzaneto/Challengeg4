# Incremento 4: revisor, testador de uso e o que foi feito

Interface nova (D41–D44), em `solution/src/ui/`. O núcleo mudou só na chance exibida (D40: % inteira e "De cada 100…"). Um teste confere que o potencial exibido não inverte a ordem nas 6.016 linhas das datas disponíveis. Cada achado grave foi reproduzido antes da correção, como pede o `CLAUDE.md`.

## Comandos

| Comando | Resultado |
|---|---|
| `npm run check` | tipos ok; Biome sem erro (8 avisos: 2 `!important` no bloco de "reduzir movimento", 4 de ordem de especificidade no CSS, 2 em `e2e/`); Vitest com 66 testes passando |
| `npm run e2e` | 12 testes passando |
| `npm audit --omit=dev` | 0 vulnerabilidades |
| `npm run personas` | 12 testes passando; medições abaixo |
| `npm run prints` | 28 prints em WebP e 2 vídeos em VP9, 2,7 MB, em `screenshots/03-app/` |

## Revisor (1 rodada)

Veredito: "aprovar após correções".

| Achado | Reproduzido? | O que foi feito |
|---|---|---|
| MÉDIO 1. Na troca de data, o herói fica até 280 ms com os dados da data anterior, inclusive a empresa (fere a D34) | **Sim.** Com movimento ligado, logo depois de clicar em 30/09: `.hero .acct` = "The New York Inquirer", com o aviso de data passada já na tela | O herói antigo some na hora, os cartões mudam de lugar, e depois o herói novo aparece. A ordem pedida na D44 continua. Teste novo no e2e, com movimento ligado e sem espera |
| MÉDIO 2. Botões focáveis dentro de `role="img"` no termômetro | Sim (`Thermo.tsx`) | Com pontos clicáveis, o termômetro é `role="group"`. O e2e confere que nenhum `[role=img]` contém botão |
| LEVE 3. Clicar num ponto com o painel aberto fecha e reabre o painel | Por leitura do código | `data-open` nos pontos |
| LEVE 4. Nome da aba diferente do texto visível no celular (WCAG 2.5.3); tablist incompleto; folha "modal" sem trava de foco | Sim | O nome é o texto visível ("Frios 57"); abas e painel ligados por `id`; setas do teclado; a folha vai para o `body` e, no celular, deixa o resto da página inerte |
| LEVE 5. "da empresa" no score se confunde com Empresa (o cliente) | Sim | "de todos os vendedores" (D45) |
| LEVE 6. Estado vazio fala "você" quando quem vê é o gestor | Sim | Terceira pessoa quando vem da equipe ("Carl não tem negócio no CRM"), com teste |
| LEVE 7. A saudação conta a lista inteira, mas a frase sugere os 5 primeiros | Sim | **Não mudou.** O texto foi aprovado pelo Bruno na D42, e contar só os 5 esconderia negócios que esfriam esta semana. Vai ao Bruno |
| LEVE 8. "138" escrito à mão; funções copiadas; `SellerView.tsx` com 748 linhas | Sim | `STALE_AFTER` nos textos; `first` e `initials` em `format.ts`; `parts.tsx` (temperatura, empresa, score, o que fazer) e `DealPanel.tsx` separados |
| LEVE 9. Prints numa pasta diferente da documentada | Sim | `03-app/` é de propósito (preserva os prints do portão reprovado em `02-app/`); `AGENTS.md` §5 atualizado |
| LEVE 10. Se uma faixa arredondar para 0%, a frase e a conta não fecham | Caso latente (mínimo atual: 8,6%) | Teste novo: nenhuma faixa das datas disponíveis exibe 0% |

## Testador de uso (1 rodada; 3 personas, 1280 e 390 px, claro e escuro)

| Achado | Reproduzido? | O que foi feito |
|---|---|---|
| GRAVE. O nº 1 da Anna Snelling tem score 0 e potencial de US$ 5 | **Sim, e é o dado real.** A única prioridade dela em 31/12 é um MG Special de US$ 55 com 138 dias (chance de 8,6%). Versie Hillebrand, Lajuana Vencill e Niesha Huffines estão no mesmo caso | **Não mudou.** Pela regra, ele está certo em 1º (é o único). Esconder ou trocar o herói por um limite de score muda a regra: vai ao Bruno |
| GRAVE. "Ver o motivo" não aparece no print | Não no app. O roteiro de medição fotografava no meio da animação do painel. Os prints de `03-app/` e o e2e mostram o painel inteiro | O roteiro espera o painel assentar |
| GRAVE. Lista de frios sem critério; empresa truncada | Em parte. A ordem é a da D21 (preço, depois idade). A empresa aparecia cortada em 1280 ("Sem empresa n…") | Produto e empresa em duas linhas: nada é cortado; a frase diz "do mais caro para o mais barato". Botões "Dar perda" não entram: o app só lê dados |
| MÉDIO. A imagem do "Como funciona" empurra a tabela para baixo | Sim, em 1280 | Fica para o incremento 5. A imagem foi aprovada na D44; o testador citou o briefing antigo |
| MÉDIO. A lista vazia do gestor aparece só no fim | Sim | Linha "Sem prioridade nesta semana: Carl Lin." logo abaixo da frase da equipe, com link para a semana dele |
| MÉDIO. A barra de abas cobre o conteúdo no celular | Não. É efeito do print de página inteira: o conteúdo tem 120 px de folga embaixo, mais que a barra | — |
| LEVE. O seletor de data não tem rótulo | Sim | "Dados de" ao lado; o 30/06 já explica o bloqueio ao passar o mouse |
| LEVE. Pouco contraste no modo escuro | **Não.** Medido: texto secundário 8,16:1 (página) e 6,54:1 (cartão); aba escolhida 5,50:1; contagem da aba 4,90:1 | Descartado |

### Medições (`npm run personas`, depois das correções)

Tempo da máquina, do clique até a resposta estar na tela, com o movimento ligado. A primeira abertura leva cerca de 0,9 s porque inclui a animação de entrada. O "por que" inclui 0,4 s de espera pelo painel. A estimativa de leitura humana do testador, na rodada dele, foi de 3 a 5 s para achar o primeiro negócio e de 3 s para o gestor achar o valor frio.

| Persona | Pergunta | 1280 claro | 390 claro | 1280 escuro | 390 escuro | Sem rolar |
|---|---|---|---|---|---|---|
| Vendedora | qual negócio atacar primeiro | 899 ms | 884 ms | 898 ms | 899 ms | sim |
| Vendedora | por que está em primeiro | 428 ms | 444 ms | 424 ms | 445 ms | sim |
| Vendedora | o que fazer com os frios | 40 ms | 45 ms | 37 ms | 21 ms | sim |
| Gestor | quanto valor está frio | 106 ms | 108 ms | 102 ms | 104 ms | sim |
| Gestor | qual vendedor tem a lista vazia | na mesma tela | na mesma tela | na mesma tela | na mesma tela | sim |
| RevOps | como o score funciona | 58 ms | 60 ms | 58 ms | 57 ms | não |

Todas as respostas levam 1 clique a partir da tela anterior (a entrada, para a vendedora e o gestor).

O RevOps não cumpre as três tarefas em 2 minutos com o rascunho. Falta, segundo o testador:
- a fórmula com um exemplo real;
- por que vendedor e produto ficam fora, com os testes traduzidos;
- o backtest com a margem de erro.

Isso é o escopo do incremento 5.
