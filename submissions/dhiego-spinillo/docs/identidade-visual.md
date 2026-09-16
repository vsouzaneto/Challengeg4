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
