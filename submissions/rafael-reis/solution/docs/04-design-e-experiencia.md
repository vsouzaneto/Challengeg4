# Design e experiência compartilhada

Status: especificação de implementação. Este documento define a experiência única das seis lentes e a rota de onboarding; os checkboxes de aceite continuam sendo a fonte da evidência.

## 1. Fontes e decisões

- [G4 Design System](../G4_Design_System.pdf), revisão 2026.1: identidade p. 2; cores p. 3; tipografia p. 4; componentes p. 5; mapa técnico p. 6. Inspeção textual e visual das seis páginas realizada na preparação desta documentação.
- [Resumo da submissão](../../README.md): diagnóstico, automação, protótipo funcional e process log; demonstração com ambos os datasets e limitações explícitas.
- [Guia de submissão](../../../../submission-guide.md): narrativa verificável, evidências de uso de IA e instruções para executar a solução.
- Requisitos do produto: seis lentes com estado, métricas, filtros, IDs, drill-down e contexto compartilhados.

Os tokens abaixo vêm do PDF. Layout, densidade, comportamento responsivo e regras de interação são decisões deste produto, não diretrizes atribuídas ao PDF. O exemplo Tailwind da p. 6 é um mapeamento de referência; usar os mesmos valores em CSS no shell Vite + TypeScript, sem introduzir Tailwind apenas para reproduzi-lo.

## 2. Tokens e ativos

| Token do produto | Valor da referência | Uso no sistema | Página |
|---|---|---|---|
| `--g4-navy` | `#001F35` | Fundo principal e shell | 3, 6 |
| `--g4-obsidian` | `#031A26` | Superfícies de cards e painéis | 3, 6 |
| `--g4-gold` | `#B9915B` | Ação principal, foco, seleção e acento | 3, 6 |
| `--g4-sand` | `#F5F4F3` | Texto e ícones em superfícies escuras | 3, 6 |
| `--g4-ocean` | `#184560` | Superfície intermediária, nunca indicador exclusivo | 3, 6 |
| `--g4-gold-light` | `#C9A96E` | Acento secundário | 3 |
| `--g4-wine` | `#842E20` | Fundo de erro/alerta com texto claro e ícone | 3, 6 |
| `--radius-control` | `8px` | Botões, inputs, select | 5, 6 |
| `--radius-card` | `16px` | Cards, painéis, modal | 5, 6 |
| `--radius-pill` | `999px` | Origem, filtros e estados | 5, 6 |
| `--space-section` | `20px` | Intervalo entre blocos | 5 |

A cor `#25D366` é denominada WhatsApp Direct na p. 3. Sua presença na marca não a transforma em sinal universal de sucesso nem justifica integração com WhatsApp. Novas cores para séries analíticas devem ser documentadas como extensão do produto, acompanhadas por rótulos e verificadas quanto à distinção perceptual.

Tipografia: Manrope para interface, corpo e números; Libre Baskerville apenas para destaques editoriais ocasionais. Usar `Manrope, system-ui, sans-serif` e `"Libre Baskerville", Georgia, serif`. Os arquivos de fonte não constam entre os assets locais auditados; o sistema deve funcionar com fallback, sem depender de download durante a demo.

| Escala de referência | Peso / entrelinha | Aplicação proposta |
|---|---|---|
| `61px` | 800 / 1,1 | Capa de apresentação, dispensável no cockpit |
| `49px` | 700 / 1,15 | Título amplo, quando houver espaço |
| `39px` | 600 / 1,25 | Título da lente em desktop |
| `31px` | 600 / 1,3 | KPI e subtítulo de destaque |
| `20px` | 600 / 1,4 | Títulos de painéis |
| `16px` | 400 / 1,6 | Corpo, controles e tabela |

Essa escala vem da p. 4. Ajustar títulos em telas estreitas com CSS responsivo, mantendo corpo legível. Valores tabulares usam numerais alinhados; nomes longos quebram linha e nunca desaparecem sem alternativa acessível.

Ativos existentes:

| Arquivo | Característica verificada | Aplicação |
|---|---|---|
| `logo-g4-branca.svg` | `viewBox 0 0 101 40`, areia + ouro | Marca preferida sobre o shell escuro |
| `logo-g4-escura.svg` | `viewBox 0 0 81 32`, marinho + ouro | Eventual superfície clara |
| `logo-g4-valley.svg` | `viewBox 0 0 949 179`, areia + ouro | Referência de evento, fora do shell principal |
| `logo-g4-valley-full.svg` | `viewBox 0 0 642 121`, areia + ouro | Alternativa de evento |
| `logo-g4-valley-dark-text.svg` | `viewBox 0 0 949 179`, texto escuro + ouro | Evento em fundo claro |
| `logo-g4-valley-transparent.png`, `logo-g4-valley-dark-text.png` | PNG RGBA, 1898 × 358 | Alternativas raster já existentes |
| `logo-g4-valley.png` | PNG RGB, 1000 × 300 | Alternativa raster existente |
| `logo_g4-educacao_Co6Tcc.png` | PNG RGBA, 400 × 400 | Acervo existente; não redefinir a marca principal |

Preservar proporção e arquivos originais. Se a marca tiver texto adjacente redundante, usar alternativa vazia na imagem; se for o único conteúdo do link inicial, o nome acessível será “Support Intelligence - início”.

## 3. Shell único

A estrutura persistente contém marca, nome Support Intelligence, navegação com **O Início** e as seis lentes, contexto dos dados, status da sessão e área principal. A lente ativa deve ser indicada por texto/semântica e acento visual. Cada lente mantém uma URL própria dentro do mesmo aplicativo.

| Lente | Pergunta que orienta a tela | Ação principal |
|---|---|---|
| Operational Diagnosis | Onde estamos perdendo tempo? | Abrir evidências do recorte |
| AI Automation Strategy | O que podemos automatizar com IA? | Investigar oportunidade e condição humana |
| AI Ticket Lab | A IA entende um novo ticket? | Analisar texto e abrir vizinhos |
| AI Copilot | A IA ajuda a resolver o ticket? | Revisar sugestão com fontes |
| Support Intelligence Graph | Que relações explicam este problema? | Investigar cluster/ticket |
| Support Command Center | O que ocorre na operação e na IA agora? | Controlar sessão e investigar alertas |

Os nomes oficiais das lentes permanecem reconhecíveis; descrições, ajuda, status e mensagens serão em Português BR. Texto original dos tickets mantém o idioma da fonte.

Contexto compartilhado: `dataset_id`, `source`, `space_id`, `session_id`, `ticket_id` e `model_version`, conforme [arquitetura](01-arquitetura-compartilhada.md). O shell mostra nomes legíveis; IDs técnicos ficam nos detalhes/auditoria. Filtros compatíveis atravessam as rotas. Valores inválidos para o destino não são convertidos silenciosamente.

Regras de navegação:

1. Navegar não reinicia replay, não recalcula modelo e não cria nova sessão.
2. Abrir ticket/cluster conserva origem, dataset, espaço semântico e versão necessários para recuperar a evidência correta.
3. Voltar/avançar do navegador restaura lente, filtros e seleção serializáveis; campos livres com dados do usuário não entram na URL.
4. Trocar dataset invalida apenas os filtros incompatíveis e informa quais foram removidos. Dataset 2 não ganha canal, CSAT ou resolução inexistentes.
5. Clicar um KPI abre seu denominador, fórmula, cobertura e registros aplicáveis. Se não houver drill-down, oferecer “Ver metodologia”, sem simular um link inoperante.
6. Filtros ativos aparecem em chips removíveis, com contador de registros e ação “Limpar filtros”. Filtros globais e controles próprios da lente ficam visualmente separados.
7. A ação “Ver na rede semântica” seleciona o ticket real e seus vizinhos; não abre uma rede genérica.

## 4. Origem e integridade visual

Cada bloco de métrica identifica sua origem e população. Rótulos visuais:

| Valor de `source` | Rótulo | Limite explícito |
|---|---|---|
| `historical` | Histórico | Registros do CSV, cobertura e filtros |
| `simulation` | Live Replay · Simulação | Conteúdo histórico; chegada e ordem simuladas |
| `user_created` | Ticket criado na sessão | Texto manual; sem resultado operacional observado |
| `model_evaluation` | Avaliação do modelo | Partição de avaliação, versão e tamanho |

“Observado nos dados”, “Hipótese / simulação” e “Estimativa parametrizada” devem acompanhar os resultados correspondentes. Valores indisponíveis usam “Indisponível” ou “Não se aplica”, com motivo; não usar zero como substituto de dado ausente. TTR não validado, falta de data de criação ou amostra insuficiente impedem uma conclusão, mesmo que o layout comporte um gráfico.

Toda métrica mostra unidade e denominador; taxas mostram contagem e total. Tooltips detalham metodologia, mas origem, status de simulação e limitações críticas permanecem visíveis sem hover. Números ilustrativos do briefing nunca são usados como estado inicial real.

## 5. Componentes e estados

Reutilizar o mesmo card de métrica, tabela de tickets, detalhe de ticket, badge de origem, aviso de cobertura, bloco de evidência, controle de replay e feedback em todas as lentes. Usar elementos HTML nativos antes de criar componentes customizados.

| Estado | Comportamento verificável |
|---|---|
| Carregando | Mensagem e indicador com dimensão estável; não mostrar números fictícios |
| Vazio | Distinguir “sem dados no recorte”, “nenhuma sessão” e “ainda não processado”; ação útil |
| Parcial | Mostrar cobertura, campos ausentes e resultados ainda válidos |
| Erro de API | Preservar texto/filtros e resultados anteriores identificados; permitir tentar novamente |
| Modelo indisponível | Informar a dependência; diagnóstico e documentação continuam acessíveis |
| LLM indisponível | Copilot mantém fontes recuperadas e fallback claramente identificado |
| Replay parado/pausado/concluído | Estado textual persistente; contadores coerentes; sem falsa atividade |
| Conexão interrompida | Indicar última atualização e preservar snapshot; não afirmar “ao vivo” |
| Seleção ausente | Explicar ticket/cluster não disponível nesta sessão/versão; voltar ao recorte |
| Salvando feedback | Desabilitar reenvio até resposta; confirmação somente após persistência |

Erros não apagam texto digitado nem feedback salvo. Reset do replay cria uma nova sessão ou reinicia uma execução conforme contrato; não significa excluir dados, histórico ou auditoria. Exclusões não fazem parte da experiência inicial.

No Command Center, ordenar: condição crítica → indicadores operacionais → automação/modelo → alertas → tendências → decisões recentes. Limitar cards visíveis ao que cabe na narrativa e agrupar detalhes. Nada de seis dashboards repetidos dentro do cockpit.

## 6. Graph como evidência

Legenda sempre visível para: nó, aresta, peso, cor, tamanho e seleção. A posição é uma projeção do espaço de embeddings, não distância física nem prova de causa. Similaridade vem do índice real e permanece consultável numericamente. Não denominar a visualização “rede neural do modelo”.

Progressão: visão de clusters → subgrupo quando existir no artefato → tickets. A interface informa quantos registros representa e quantos desenha. A ausência de subclusters calculados não autoriza inventar hierarquia.

O modo “Tabela / Lista” deve permitir as mesmas investigações essenciais sem canvas: cluster, tamanho, categoria dominante, métricas disponíveis, revisão necessária e ação para abrir tickets. No detalhe de ticket: vizinho, similaridade, rótulo observado, predição e origem. Busca, filtros, seleção e links funcionam por teclado nessa alternativa.

Movimento de entrada usa coordenadas/vizinhos calculados; não altera relações para ficar visualmente atraente. O Graph usa Sigma/Graphology para os dados e camadas SVG discretas de traços animados nas arestas reais e halos nos nós pequenos. Cada nó se move individualmente de forma sutil. Ao clicar, o nó e seus vizinhos ficam acesos e o restante é suavizado; um novo clique no mesmo nó ou no fundo restaura tudo. O arraste reposiciona apenas o nó escolhido e preserva sua posição local durante o polling. O pulso é somente uma affordance visual de atividade, nunca uma narrativa de aprendizado. A entrada e a saída do workspace usam CSS e View Transitions quando disponíveis. Em `prefers-reduced-motion: reduce`, inserir diretamente na posição final, desativar o pulso e atualizar rótulos. Pausar animação não pausa o processamento, salvo controle de replay separado.

Alertas dependem de regras documentadas e mostram grupo, quantidade, janela simulada, critério e registros. “Possível incidente” não vira incidente confirmado por receber brilho. Nenhuma informação existe exclusivamente em cor, tamanho, movimento, tooltip ou posição.

## 7. Acessibilidade e responsividade

Meta do produto: contraste de texto normal de pelo menos 4,5:1; texto grande e elementos gráficos essenciais de pelo menos 3:1, com verificação no contexto final. A tabela WCAG do PDF não substitui medir as combinações usadas.

Verificação numérica dos hexadecimais opacos, pela luminância relativa sRGB, na preparação da documentação:

| Combinação | Contraste calculado | Uso |
|---|---:|---|
| Areia sobre navy | 15,33:1 | Texto principal |
| Areia sobre obsidian | 16,21:1 | Texto de cards |
| Navy sobre gold | 5,82:1 | Botão primário |
| Branco sobre wine | 8,78:1 | Alerta textual |
| Areia sobre gold | 2,63:1 | Não usar para texto de botão |
| Ocean contra navy | 1,65:1 | Não usar como única borda/seleção essencial |

Há diferenças frente aos valores impressos na p. 3. Validar novamente estados hover, disabled, foco, transparência e sobreposições na implementação. O gold deve acompanhar texto navy no botão primário. Bordas decorativas podem ser suaves; foco e limites necessários para identificar controles devem ser discerníveis.

- Link “Pular para conteúdo”; landmarks `header`, `nav`, `main`; um título principal por lente.
- Links reais para navegar; botões para ações; labels associados a inputs e mensagens de erro.
- Foco visível, ordem previsível, retorno ao acionador após fechar painel/modal, sem armadilha de teclado.
- Tabelas com cabeçalhos; ordenação anunciada; gráfico com descrição e tabela de dados.
- Resultado de análise e feedback anunciado em região de status; replay anuncia resumos controlados, não cada evento.
- Alertas urgentes sem flashes; `prefers-reduced-motion` em transições, câmera e entrada de nós.
- Zoom 200% e largura de 320 CSS px sem perda de ações; rolagem horizontal apenas na região da tabela/gráfico, com alternativa textual.
- Em tela estreita: navegação compacta acessível, cards em uma coluna e detalhe abaixo da lista; sem depender de arrastar ou hover.
- Alvos de interação confortáveis; adotar 44 × 44 CSS px como decisão de produto para botões de ícone e controles primários.

## 8. Demonstração executiva

Preparar roteiro reproduzível com IDs reais e uma sessão identificada. O cenário de concentração semântica seleciona tickets reais, mas assume explicitamente ordem e chegada simuladas. A demo não se baseia em resultados escolhidos para esconder erros; manter exemplos de baixa confiança, falta de evidência e revisão humana.

| Passo | Lente e ação | Evidência que o público verá |
|---|---|---|
| 1 | Diagnóstico: selecionar recorte | Gargalo sustentado pelos dados ou limitação que impede medir TTR |
| 2 | Estratégia: abrir oportunidade | Observação, hipótese, intervenção humana e parâmetros do ROI |
| 3 | Command Center: iniciar Live Replay | Sessão, origem histórica, ordem/tempo simulados |
| 4 | Acompanhar processamento | Contadores e decisões reais do pipeline |
| 5 | Graph: abrir sessão | Nós/vizinhos compatíveis com o processamento |
| 6 | Cenário simulado de concentração | Critério e evidência do possível incidente |
| 7 | Clicar alerta no Command Center | Mesmo cluster e mesmos tickets selecionados no Graph |
| 8 | Ticket Lab: digitar texto novo | Inferência real, identificada como entrada manual |
| 9 | Examinar resultado | Categoria, score, revisão, rota e vizinhos com versão |
| 10 | “Ver na rede semântica” | Novo ticket no espaço correto, posição/arestas reais |
| 11 | Copilot: revisar sugestão | Resoluções históricas, qualidade da evidência e feedback persistido |
| 12 | Voltar ao Command Center | Mesma sessão; operação, IA e estimativas com origens separadas |

Se LLM falhar, manter recuperação/extrativo. Se replay falhar, usar os demais módulos e o último snapshot identificado. Se não houver resolução suficiente para o ticket demonstrado, a resposta correta é explicar a insuficiência e exigir revisão. Não introduzir dado fictício para cumprir o roteiro.

Registrar no process log decisões, limitações dos dados, erros encontrados, correções, ferramentas usadas e evidências de execução. O README de execução deve permitir repetir a apresentação, preservando os CSVs originais.

## 9. Checkpoints de aceite visual e integrado

- [ ] DES-01: seis lentes usam o mesmo shell, tokens, IDs e origem; navegação não reinicia a sessão.
- [ ] DES-02: logo correto, proporção preservada, fontes com fallback e contraste medido nos estados reais.
- [ ] DES-03: filtros e voltar/avançar restauram contexto compatível; transição entre datasets não inventa campos.
- [ ] DES-04: KPI relevante abre registros/metodologia; estado indisponível tem motivo e não aparece como zero.
- [ ] DES-05: simulação e hipóteses são visíveis antes da interação, inclusive em gráficos e screenshots.
- [ ] DES-06: Lab → Graph, alerta → cluster e ticket → Copilot preservam origem, seleção e versão.
- [ ] DES-07: investigações essenciais do Graph estão disponíveis por lista/tabela e teclado.
- [ ] DES-08: replay e animações respeitam movimento reduzido, sem perder fatos nem saturar leitor de tela.
- [ ] DES-09: estados vazio, erro, parcial, indisponível e feedback salvo foram exercitados.
- [ ] DES-10: layout utilizável a 320 CSS px e zoom 200%, com foco sempre visível.
- [ ] DES-11: roteiro completo de 12 passos é repetível e seu fallback funciona sem LLM.
- [ ] DES-12: process log registra execução real; números de exemplo do briefing não aparecem como medidos.
- [x] DES-13: O Início explica corpus, estados, limites, raciocínio técnico e execução local; o Graph tem pulso/nós neon baseado nos dados reais, seleção tipo Obsidian, arraste individual e tabela equivalente.
