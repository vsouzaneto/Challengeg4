# Process log

Como a solução foi construída, em ordem, com os pontos em que a IA errou e as decisões humanas que mudaram o rumo.

## Ferramentas

| Ferramenta | Uso |
|---|---|
| **Claude Code** (desktop, Claude Opus 5.5) | Fork e setup do repositório, download do dataset (conector Kaggle), análise exploratória em Python/pandas/scipy, desenho do modelo, implementação (Next.js + TypeScript), testes, validação no navegador integrado, documentação |
| **Segunda IA (revisão independente)** | Revisou criticamente a primeira análise. O documento dela está em [`revisao-externa-ia.md`](revisao-externa-ia.md) |
| **Skills da Intento** | `intento-product-design` (estrutura antes da estética, estados, validação), `shadcn` (componentes Base UI) |
| **Navegador integrado do Claude Code** | Validação das jornadas: filtros, tooltip, detalhamento, upload válido e inválido, mobile |

## Linha do tempo

### 1. Entender antes de construir

- Fork, leitura do README do challenge, do guia de submissão e do `CONTRIBUTING.md`.
- **Conferência das regras nos PRs reais do repositório.** Achado: o `.gitignore` da raiz ignora `submissions/`. Isso explica um PR concorrente com 13.923 arquivos (o `git add -f` levou o `node_modules` junto). Solução adotada: adicionar com `-f` filtrando os artefatos e conferir, a cada commit, que nada saiu da pasta.

### 2. Análise exploratória, antes de qualquer tela

Pedido explícito: "analise a base, olhe mês a mês, traga o que ela diz além do óbvio, não invente, marque o que é heurística". Resultado em [`../docs/analise-lead-scorer.md`](../docs/analise-lead-scorer.md).

- **Achado central:** nenhum atributo estático prevê ganho ou perda. Qui-quadrado com p > 0,26 em produto, setor, região, manager, vendedor e conta. O win rate por vendedor não persiste entre semestres (r = 0,15).
- **Efeitos que pareciam reais e eram calendário:** "último resultado prevê o próximo" e "carga do vendedor reduz conversão". Os dois somem quando se controla pelo mês de fechamento.
- **O que diferencia os deals:**
  - valor: o preço varia 500× entre produtos;
  - tempo: quem perde, perde rápido;
  - pipeline "zumbi": 81% dos deals em Engaging estão abertos há mais tempo do que qualquer deal já fechado.
- **Pergunta de negócio acrescentada no meio:** "qual o produto mais vendido, qual gera mais receita, quem é especialista?"

### 3. Revisão cruzada com outra IA (iteração decisiva)

A análise foi entregue a uma segunda IA para crítica. Eu (Claude) conferi cada afirmação dela contra a base:

- **Ela acertou e me corrigiu em três pontos:**
  1. Minha tabela "sobreviver aumenta a chance de ganhar" tinha viés de seleção, porque ignorava os deals abertos. Refeita com riscos competitivos (abertos como censurados), a conclusão se inverteu: a chance **cai** com a idade.
  2. O caso "Hayden × MG Advanced", que eu chamei de "único caso forte", não sobrevive à correção de Benjamini–Hochberg (q = 0,30).
  3. Eram 178 testes, não ~200.
- **Ela errou em dois pontos:**
  - criticou propostas que não estavam no documento (pesos 70/30, normalização pelo maior preço);
  - não percebeu que o próprio método dela zera a chance de 81% do pipeline.
- **Direção humana decisiva:** a regra de score não pode depender de nomes da base e não pode ser fixa; precisa aprender com os resultados e reajustar os pesos sozinha. Isso levou ao modelo v1: estrutura fixa, parâmetros reaprendidos, encolhimento hierárquico, backtest e promoção de versão.
- **Correção de conduta:** a IA passou a opinar sobre o que "cabia no challenge". Resposta humana: "Não é você que deve dizer o que cabe." A partir daí as decisões de escopo voltaram para o humano, e a IA passou a apresentar opções.

### 4. Decisões de produto (humanas, via perguntas objetivas)

- Uma aplicação web que o G4 possa plugar amanhã, baseada no `intento-product-starter`.
- Raias com os mesmos nomes da base; tooltip no score; detalhamento ao clicar; filtros por região e vendedor.
- Dados via CSV do CRM **e** upload pela tela.
- Won/Lost como histórico recolhido.
- Ordem do funil + ranking #1, #2… + selo "Comece aqui".

### 5. Implementação e verificação

| Commit | O quê |
|---|---|
| `8797aa5` | Setup: starter, dataset, análise e modelo v1 |
| `53f71f1` | Motor de score + pipeline |
| `ac12477` | Página Modelo e base + upload |

Verificações que mudaram o código:

- **Testes automáticos batendo o motor TypeScript com os números do Python** (`p_base(0) = 51,9%`, limiares 14/88/116/130). Passaram de primeira, o que confirma que a implementação é o modelo descrito.
- **Backtest revelou probabilidades otimistas** (previsto 78%, observado 47%). Foi adicionada calibração Platt, validada deixando cada mês de fora: Brier 0,231 → 0,221.
- **O backtest confirmou sozinho a análise:** produto, região e vendedor não melhoram a previsão, e o modelo em uso considera só o tempo.
- **Bugs pegos no navegador, não na leitura do código:**
  - hidratação quebrada porque o Node e o navegador formatam moeda compacta de jeitos diferentes;
  - Tailwind lendo o cache binário do Next, efeito colateral do `.gitignore` da raiz;
  - a página inteira rolando na horizontal;
  - ranking #3 aparecendo depois do #4 por desempate inconsistente;
  - `/modelo` sendo pré-renderizada no build e congelando o estado.
- **Upload testado de ponta a ponta:**
  - base inválida → recusada com mensagem clara, base vigente intacta;
  - base simulada "até 30/09/2017" → modelo v2 criado, configuração mantida, parâmetros reaprendidos;
  - restaurar a base padrão → volta ao v1.

## Onde a IA errou (resumo)

1. Viés de seleção na tabela de sobrevivência (corrigido após a revisão externa).
2. Afirmar significância sem corrigir para múltiplos testes.
3. Tentar decidir escopo no lugar do responsável pela entrega.
4. Probabilidades mal calibradas na primeira versão do motor (detectado pelo backtest).
5. Cinco bugs de interface detectados só ao rodar e usar o app.

## Evidências

- Histórico do git na branch `submission/hiago-hoffman`.
- Scripts de análise em [`analysis/`](analysis/).
- Revisão externa em [`revisao-externa-ia.md`](revisao-externa-ia.md).
- Testes em `solution/src/lib/scoring/model.test.ts`.
