# Identidade da análise visual v1

**15/09/2026 — requisito de Dhiego: seguir o branding do G4.**

## Fontes consultadas

- [Artigo oficial do rebranding](https://g4business.com/blog/rebranding-g4-por-que-mudamos), lido no site.
- [Vídeo oficial indicado](https://www.youtube.com/watch?v=SbEDu7LMXnY): descrição, transcrição disponível na interface do YouTube e referência visual. Não foi alegada uma auditoria quadro a quadro.
- [CSS global público do site](https://g4business.com/wp-content/uploads/elementor/css/post-7.css), conferido junto aos estilos renderizados.
- [Logo oficial público](https://g4business.com/wp-content/uploads/2026/01/logo-g4-completa-branca.svg), preservado sem redesenho.

O material comunica direção, método e permanência. A tradução para este estudo usa composição sóbria, hierarquia editorial e evidência explícita. Não foi fornecido um manual completo da marca; esta aplicação segue os recursos e estilos oficiais observados.

## Plano visual antes da implementação

- **Tema e tarefa:** leitura guiada da análise de atendimento por Dhiego, para discutir decisões antes do protótipo.
- **Paleta observada:** navy `#001F35`, mauá `#031A26`, gold `#B9915B`, silver `#F5F4F3`, azul de apoio `#184560`, vermelho de atenção `#842E20`.
- **Tipografia:** PPMuseum nos títulos, Manrope no corpo e dados tabulares. Referências remotas às fontes, com alternativas locais se indisponíveis. Fontes comerciais não são copiadas para o repositório.
- **Composição:** abertura institucional marinho/dourado; corpo claro e espaçoso; navegação horizontal; painéis de evidência e interpretação lado a lado.
- **Elemento central:** mudar a pergunta analítica altera o universo admissível e o limite de interpretação. No explorador de tickets, o texto de origem permanece visível ao lado da leitura de contexto.

```text
Logo G4 | estudo de Dhiego | navegação
Tese da análise + estado da investigação
Universos D1 / D2 e limites
Pergunta escolhida → dados admissíveis → decisão possível
Canais e sinais de atrito
Ticket selecionado | fonte + recap comentado
Código / IA / humano + propostas futuras
Fontes e método
```

**Revisão do plano:** evitar um dashboard genérico de KPIs. Os números contam uma pergunta específica e trazem denominador. O esquema editorial marinho/dourado deriva da identidade solicitada. As opções não simulam chamadas de IA: todo recap desta v1 é uma leitura exploratória fixa, identificada como tal.

## Fronteira funcional

Esta é uma análise visual interativa, gerada de relatórios JSON. Não é protótipo de inferência. Numa implementação futura, recap e rascunhos poderão ser gerados para a entrada selecionada; exemplos preparados servem como referências de discussão/avaliação, sem substituir geração e verificação. Regras, cálculos e envio humano permanecem separados.

## Protótipo funcional — plano visual de 21/09

Reutilizar os tokens oficiais e o logo, com tarefa central de atendimento: ler o texto, conferir a categoria e o contexto, registrar a decisão. Cabeçalho compacto e navegação entre atendimento, evidências e diagnóstico. A área principal coloca entrada e contexto lado a lado; os trechos que sustentam o recap têm acesso direto ao texto original. Resultados medidos ficam numa seção própria, com denominadores e limite.

```text
G4 / Suporte assistido       Atendimento · Evidências · Diagnóstico
Entenda o pedido. Confirme o próximo passo.
Ticket e exemplo editável  | Categoria sugerida e revisão obrigatória
Domínio confirmado        | Recap → pedidos / tentativas / pendências
Gerar análise             | Incertezas e próximo passo sugerido
                          | Sua decisão + motivo → registrar
Comparação medida / limites / cenário de esforço
```

Revisão do plano: o centro é o texto do cliente e sua interpretação; não usar métricas decorativas como painel principal. A confirmação registra apenas uma decisão demonstrativa. Novo texto invalida a análise anterior. Ausência de modelo ou recap deve oferecer próximo passo explícito. Layout em uma coluna no celular; indicadores visuais e textuais, foco visível e estados de carregamento acessíveis.


## Ajuste após revisão guiada

O fluxo vigente preserva entrada à esquerda e preparação do atendimento à direita. A ficha registra conferências humanas e relato de possível incidente, prepara orientação por regra e apresenta rascunho editável. Recap fica experimental e só ocupa a área de resultado quando solicitado ou quando falha. A calculadora de esforço foi retirada após a crítica do candidato. A coluna de entrada permanece acessível durante a leitura da ficha em desktop, com altura limitada e rolagem própria; celular usa uma coluna. Não foram adicionadas integrações simuladas.


## One-pager executivo

Superfície de leitura para o diretor, preservando azul-marinho #001F35, dourado #B9915B, branco/prata #F5F4F3 e as famílias já usadas na aplicação. Uma folha vertical com tese de decisão, tabela de evidências/implicações, experimento e protótipo lado a lado, seguida do próximo investimento. A distinção entre dado, capacidade técnica e hipótese de impacto organiza o conteúdo. Sem gráficos decorativos; projeções ficam identificadas como cenários e detalhadas na calculadora. O primeiro plano foi reduzido para três achados centrais; detalhes permanecem nos links. CSS de impressão em A4; HTML e Markdown incluídos.

## Capacidade e retorno — implementação de 21/09

Registro por leitura de `solution/templates/economia.html`, `solution/static/economia.css`, `solution/static/economia.js` e `solution/visual/resumo-executivo.html`; esta seção não declara inspeção visual no navegador.

A simulação ocupa uma página própria, acessível pelo resumo executivo. Herda do aplicativo o logo G4, cabeçalho marinho, fundo prata, corpo Manrope, controles de cantos discretos e foco dourado. A área de até 1200px coloca premissas à esquerda e resultado em painel marinho à direita, com números tabulares em dourado claro (`#e4c89f`). Abaixo de 800px, essas áreas ficam empilhadas; os campos mantêm duas colunas. O resumo conserva título Museum, folha de até 900px, tabela de evidências e impressão A4, acrescentando o link “Simular retorno”.

Dez entradas numéricas e três hipóteses de eficiência alimentam o cálculo. Alterar uma entrada oculta o resultado anterior e pede recálculo; selecionar uma hipótese recalcula automaticamente. Mensagens anunciam cálculo, conclusão e falha. Capacidade recuperada e despesa evitada aparecem em grupos separados, com premissas, limites e aviso de trabalho adicional. A referência salarial fica em conteúdo expansível. Esses valores são cenários: o resumo continua sem alegar ROI comprovado.

Correção após inspeção: o título de Economia usa explicitamente PPMuseum com ênfase em dourado escurecido (#87622f). Capturas finais do aplicativo mostram a composição em desktop e celular; a revisão da documentação acima foi feita separadamente por leitura de código.

## Fluxos operacionais e valor por processo — incremento de 21/09

Registro por leitura de `solution/templates/fluxos.html`, `solution/templates/valor.html`, `solution/static/fluxos.css`, `solution/static/fluxos.js` e `solution/static/valor.js`, com persistência conferida em `app.py` e `service_flow.py`. Não houve inspeção visual nesta etapa de documentação.

`/fluxos` herda logo, cabeçalho marinho, fundo prata, corpo Manrope e título PPMuseum com ênfase dourada. Uma faixa apresenta os três caminhos: autosserviço, atendimento preparado e investigação humana. Em até 1280px, pedido e cenário ficam à esquerda; decisão, contexto consultado, citações, próximo passo e trilha ficam à direita. A decisão usa fundo marinho e rótulo dourado claro. Abaixo de 800px, a faixa e o espaço de trabalho passam para uma coluna.

O aviso inicial distingue textos do D2 de contas, notas e registros fictícios. A opção de IA informa o envio do texto ao OpenRouter; sem configuração, os exemplos usam regras lexicais identificadas. Mudanças de entrada invalidam o resultado anterior. Os controles acompanham o estado: solicitar/concluir recuperação simulada, relatar falha, editar/aprovar resposta ou assumir investigação. A execução, as ações e o rascunho aprovado ficam registrados no SQLite local; a interface apresenta a trilha, sem retomar automaticamente a execução ao recarregar. Mensagens de andamento e erro usam região de anúncio, e controles são bloqueados durante chamadas. Não há envio externo de mensagens nem alteração de conta real.

`/valor` reutiliza a composição da calculadora: premissas à esquerda, resultados em marinho à direita e empilhamento no celular. Os campos agrupam volume/uso, autosserviço e preparação; salário e custos ficam em conteúdo expansível. A saída separa horas, conclusões e falhas por caminho antes de apresentar capacidade e resultado financeiro. Os volumes são exclusivos, falhas descontam esforço e investigação humana não recebe ganho presumido. Alterações ocultam resultados até o recálculo; grupos que excedem o total recebem explicação textual. Valores são hipóteses editáveis, formatados em português e reais, sem benefício operacional medido.
