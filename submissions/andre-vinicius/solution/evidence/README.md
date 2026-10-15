# Verificação visual dos painéis

Capturas feitas na prévia local com os CSVs originais do case (2.089 oportunidades abertas, 27 vendedores e três valores de `regional_office`). Os arquivos `gerente-*`, `vendedor-*` e `mapa-*` mostram as três subpáginas em 1440 × 900 e 390 × 844. `vendedor-card-ajuste.png` mostra os cartões revisados em tema escuro. No mapa com vendedor selecionado, Darcel Schlecht é da região Central; o mapa destaca essa região e lista as primeiras oportunidades dele.

A organização em gerente/equipe, ficha do vendedor, mapa por região e acesso às anotações aproveita a estrutura de uma referência visual fornecida para a tarefa. Cores, componentes e dados seguem o app deste case. As anotações continuam no detalhe da oportunidade; nenhum índice agregado de vendedor foi criado.

Os mesmos arquivos ficam em `docs/evidence/` e `static/evidence/` (servidos pelo leitor). Os exemplos comentados estão na seção 9 da especificação funcional. Esta pasta não tem capturas da Mesa comercial, da Fila de decisão nem do Kanban.

## Segundo redesign · 14/10/2026

Comparativo novo da versão anterior (`193a83f`) e da branch `codex/g4-003-redesign-02`, com os mesmos CSVs públicos. As capturas foram feitas em navegador Chromium, tema claro, página inteira, nas larguras 1440 × 900 (desktop) e 390 × 844 (celular). Os nomes `redesign-02-antes-*` mostram a versão anterior; `redesign-02-depois-*` mostram a versão revisada. Há pares para Oportunidades e Metodologia em ambas as larguras.

| Tela | Desktop | Celular |
| --- | --- | --- |
| Oportunidades, antes | [Captura](redesign-02-antes-oportunidades-desktop.png) | [Captura](redesign-02-antes-oportunidades-celular.png) |
| Oportunidades, depois | [Captura](redesign-02-depois-oportunidades-desktop.png) | [Captura](redesign-02-depois-oportunidades-celular.png) |
| Metodologia, antes | [Captura](redesign-02-antes-metodologia-desktop.png) | [Captura](redesign-02-antes-metodologia-celular.png) |
| Metodologia, depois | [Captura](redesign-02-depois-metodologia-desktop.png) | [Captura](redesign-02-depois-metodologia-celular.png) |

Na checagem visual, os quatro destinos principais ficaram legíveis no celular, a Metodologia exibiu filas, cálculo e limites, e não houve rolagem horizontal nas duas telas. Não foi um teste em aparelho físico.
