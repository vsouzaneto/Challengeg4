# Lead Scorer

Aplicação web que mostra ao vendedor o pipeline ordenado por **receita esperada** (chance de ganhar × valor), explica o porquê de cada score e reaprende o modelo sempre que a base do CRM é atualizada.

## Setup

Requisitos: Node.js 20 ou superior.

```bash
npm install
npm run dev        # desenvolvimento: http://localhost:3000
```

Produção:

```bash
npm run build
npm start          # http://localhost:3000
```

Testes do motor de score (sem dependências extras):

```bash
npm test
```

A base do challenge já vem em `data/` e o app abre pronto para uso.

### Plugar a base do CRM

Duas formas, sem mexer em código:

1. **Pela tela:** *Modelo e base → Atualizar a base*. Envie `sales_pipeline.csv`, `sales_teams.csv`, `products.csv` e `accounts.csv` no mesmo formato. A base é validada antes de substituir a atual; se tiver erro, nada muda e a mensagem diz o que corrigir.
2. **Por pasta:** aponte `LEAD_SCORER_DATA_DIR` para a pasta onde o CRM exporta os quatro CSVs.

| Variável | Padrão | Para quê |
|---|---|---|
| `LEAD_SCORER_DATA_DIR` | `./data` | Base padrão (CSVs do CRM) |
| `LEAD_SCORER_STORAGE_DIR` | `./storage` | Base enviada por upload e histórico de versões do modelo |
| `LEAD_SCORER_ADMIN_TOKEN` | vazio | Se definido, exige o token para trocar a base |

O servidor precisa de disco gravável em `LEAD_SCORER_STORAGE_DIR` para guardar uploads e versões (VM, container ou serviço Node com volume). Em hospedagens com disco somente leitura, o app funciona com a base padrão e mantém o histórico de versões só em memória.

## Como usar

- **Pipeline:** raias com os nomes dos estágios do CRM (`Prospecting`, `Engaging`, `Won`, `Lost`).
  - O card **#1** fica destacado ("Comece por este") e a raia dele recebe o selo **Comece aqui**. Dentro de cada raia, os cards seguem a ordem de receita esperada.
  - Passe o mouse no score para ver o resumo. Clique no card para ver o cálculo passo a passo.
  - Filtre por região, manager ou vendedor. Os filtros ficam na URL, então dá para compartilhar a visão de um vendedor. O ranking (#) é recalculado dentro do filtro; o score continua sendo o da empresa inteira.
  - `Won` e `Lost` ficam recolhidas como histórico.
  - Deals abertos há mais tempo do que 99% dos ganhos da base vão para o bloco **Revalidar** no fim da raia.
- **Modelo e base:** versão vigente, teste em datas passadas, o que o modelo aprendeu, qualidade da base, upload e histórico de versões.

## Lógica do score

Detalhes e justificativas estatísticas em [`../docs/analise-lead-scorer.md`](../docs/analise-lead-scorer.md), seção 6.

```text
receita esperada R = p × v
score (0–100)      = percentil de R entre as oportunidades abertas com estimativa (empresa inteira)
```

1. **Chance pela idade, `p_base(a)`.** Modelo de sobrevivência semanal com dois desfechos (ganho e perda). Deals ainda abertos entram como observação sem desfecho, não como perda. Resultados recentes pesam mais (meia-vida escolhida no backtest).
2. **Ajustes por grupo:** série, produto, região, manager, vendedor, região × produto, vendedor × produto e mês do trimestre de entrada.
   - Cada grupo recebe peso `w = n / (n + k)`, com `k` aprendido pelo método dos momentos.
   - Se o grupo não varia mais do que o acaso, `k = ∞` e o peso é zero.
   - Nenhum nome está no código: vendedor, produto ou região novos começam com peso zero e herdam o nível acima.
3. **Calibração (Platt).** Ajuste aprendido no backtest para que "30%" signifique 30%.
4. **Valor se ganhar:** `v = preço de tabela × razão histórica valor fechado / preço`, encolhida por produto → série → geral.
5. **Estados pela idade.** Os percentis do ciclo dos ganhos são fixos por política (75/95/99); os dias são reaprendidos a cada base.
   - **Início:** antes da mediana do ciclo das perdas.
   - **Em andamento:** até o percentil 75 dos ganhos.
   - **Esfriando:** entre os percentis 75 e 95.
   - **Tardio:** entre os percentis 95 e 99.
   - **Revalidar:** acima do percentil 99. Sem score.
6. **Aprendizado contínuo.** A cada base nova:
   - todos os parâmetros são reestimados;
   - 16 configurações (recência × curva × grupos) disputam um backtest com cortes mensais;
   - a candidata só substitui a configuração vigente se for melhor em erro de probabilidade **e** em receita capturada no topo da lista;
   - a versão fica registrada.

Resultado na base do challenge (backtest de mar a ago/2017):

| | Erro de probabilidade (Brier) | Receita ganha no top 20% da lista |
|---|---|---|
| Sem modelo: taxa histórica e ordenação por preço | 0,314 | 46,7% |
| Modelo v1, antes da calibração | 0,231 | 55,6% |
| Modelo v1, calibrado (validação deixando cada mês de fora) | 0,221 | — |

Na base atual, produto, região e vendedor não melhoraram a previsão; a versão vigente usa só o tempo. Se isso mudar com resultados novos, a configuração muda sozinha.

## Estrutura

```
data/                       base do challenge (CSV, CC0)
src/lib/scoring/            motor puro em TypeScript, sem dependência do Next
  csv.ts, dataset.ts        leitura, normalização e validação da base
  model.ts                  curva, encolhimento, valor, estados, calibração, score
  backtest.ts               cortes mensais, seleção e promoção da configuração
  model.test.ts             testes (conferem o motor contra a análise em Python)
src/lib/server/             estado do app: versões, cache, upload; DTOs da interface
src/lib/explain.ts          textos e formatação derivados do cálculo
src/components/pipeline/    raias, card, tooltip, painel de detalhamento, filtros
src/app/(app)/page.tsx      Pipeline
src/app/(app)/modelo/       Modelo e base (+ Server Actions de upload)
src/app/api/oportunidades/  detalhamento de uma oportunidade (JSON)
```

Base: `intento-product-starter` (Next.js 16, TypeScript, Tailwind v4, shadcn/ui sobre Base UI).

## Limitações

- **Prospecting não tem data de entrada.** A chance usa a de um deal recém-engajado vezes a conversão Prospecting → Engaging (`c`). A base não tem essa conversão, então `c = 1`: é uma estimativa otimista, sinalizada no card. Com o histórico de estágios, `c` passa a ser aprendido.
- **Sem histórico de atividades.** Sem dados de ligações, reuniões ou próximo passo, o modelo só enxerga tempo e valor. Qualquer campo novo entra como um grupo a mais e ganha peso só se o backtest aprovar.
- **Foto única da base.** O CRM exporta o estado atual, não as mudanças de estágio. O backtest reconstrói o passado a partir das datas de entrada e fechamento.
- **Sem autenticação por usuário.** O filtro por vendedor não é uma permissão. Para produção: SSO do G4 e visão restrita por vendedor/manager.
- **Efeito da própria ferramenta.** Deals bem pontuados recebem mais atenção, o que contamina o aprendizado futuro. Para medir o impacto e evitar esse ciclo: registrar score exibido e ação tomada, e reservar parte da lista para deals incertos.
- **Escala.** O motor processa ~9 mil oportunidades em menos de 1 s. Para centenas de milhares, mover o treino para um job agendado e guardar os scores em banco.
