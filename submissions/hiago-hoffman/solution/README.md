# Lead Scorer

Aplicação web que mostra ao vendedor o pipeline ordenado por **uma nota de 0 a 100** (valor do deal × chance de ganhar na situação em que ele está × demais fatores aprendidos), explica a nota e reaprende o modelo sempre que a base do CRM é atualizada.

## Setup

### Pré-requisitos

- [Node.js](https://nodejs.org) 20 ou superior (`node -v` para conferir).
- Git.

### Rodar do zero

```bash
git clone https://github.com/gandahiago/ai-master-challenge.git
cd ai-master-challenge
git checkout submission/hiago-hoffman
cd submissions/hiago-hoffman/solution
npm install
npm run dev
```

Abra http://localhost:3000.

- A base do challenge já vem em `data/`; não é preciso baixar nada do Kaggle.
- No primeiro acesso em modo de desenvolvimento, o Next compila as páginas e o modelo é treinado: leva de 30 s a 1 min. Depois disso, cada página abre em menos de 1 s.

### Produção

```bash
npm run build
npm start          # http://localhost:3000
```

### Testes

```bash
npm test           # 14 testes do motor de score, sem dependências extras
```

### Problemas comuns

| Sintoma | Solução |
|---|---|
| Porta 3000 ocupada | `npm run dev -- -p 3001` e abra http://localhost:3001 |
| Primeira página demora | Normal no modo dev (compilação + treino do modelo); use `npm run build && npm start` para abrir rápido |
| `npm install` falha | Confira a versão do Node (`node -v`, precisa ser 20+) |

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
  - Passe o mouse na nota para ver, em linguagem direta, o valor, a chance e a situação do deal, e o que mais mexeu na nota.
  - Clique no card para ver a conta completa: só os fatores que de fato mudaram a posição daquele deal.
  - Ao escolher um vendedor, a região e o manager dele são preenchidos; ao escolher uma região ou um manager, as listas abaixo mostram só quem pertence a ela.
  - Filtre por região, manager ou vendedor. Os filtros ficam na URL, então dá para compartilhar a visão de um vendedor. O ranking (#) é recalculado dentro do filtro; o score continua sendo o da empresa inteira.
  - `Won` e `Lost` ficam recolhidas como histórico.
  - Todas as oportunidades abertas da raia, inclusive as em **Revalidar**, estão numa única lista ordenada pelo score.
- **Modelo e base:** versão vigente, teste em datas passadas, o que o modelo aprendeu, qualidade da base, upload e histórico de versões.

## Lógica do score

Detalhes e justificativas estatísticas em [`../docs/analise-lead-scorer.md`](../docs/analise-lead-scorer.md), seções 6.5 e 6.6.

Um score só, com a mesma fórmula para toda oportunidade aberta (Prospecting, Engaging e Revalidar):

```text
Prioridade = Valor × Situação × Afinidade × Relacionamento × Produto × Time × Calendário × Urgência
Score      = 100 × Prioridade / (Prioridade + K)     K = prioridade mediana dos deals vivos (score 50)
```

1. **Situação:** Prospecting (sem data de entrada), Início, Em andamento, Esfriando, Tardio ou Revalidar.
   - Os dias de cada faixa são percentis do ciclo dos ganhos, reaprendidos a cada base.
   - O fator é a chance de ganho dos deals da base que passaram por essa situação. É estimado pela curva de sobrevivência, com os deals abertos contados como sem desfecho; depois do histórico, pela cauda (ganhos + 1) ÷ (deals + 2).
   - Prospecting = fator de Início × conversão Prospecting → Engaging, aprendida comparando uploads sucessivos (50% sem observações).
2. **Afinidade, Relacionamento, Produto, Time e Calendário:** grupos com peso `n / (n + k)`, com `k` aprendido pelo método dos momentos.
   - Grupo sem sinal fica com ×1,00.
   - Cada grupo é testado sozinho no backtest e só entra se não reduzir a receita capturada.
   - Relacionamento = a conta já tinha uma compra fechada antes de o deal entrar em Engaging; conta não informada é neutra.
3. **Calibração isotônica:** "30% previsto" passa a valer 30% observado, sem inflar chances muito pequenas.
4. **Urgência:** 1 + força × queda prevista da chance na janela. Força (0,5 a 3) e janela (7 a 28 dias) são escolhidas no backtest; fica desligada se não aumentar a receita capturada.
5. **Aprendizado contínuo:** a cada base nova, todos os parâmetros são reestimados e as escolhas acima são refeitas no teste em datas passadas. A versão candidata só substitui a vigente se capturar pelo menos a mesma receita. As versões ficam registradas.

**Critério de todas as escolhas:** receita ganha capturada nos 20% do topo da lista, ponderada pelo valor (deals maiores pesam mais). O erro de probabilidade só desempata.

Resultado na base do challenge (backtest de mar a ago/2017):

| | Receita ganha no top 20% | Erro de probabilidade (Brier) |
|---|---|---|
| Sem modelo: taxa histórica e ordenação por preço | 46,7% | 0,314 |
| Situação sem grupos | 54,8% | 0,235 |
| Modelo em uso (v2) | 55,3% | 0,235 (0,222 calibrado) |

Nesta base, entram na fórmula produto, time, vendedor × produto (todos ×1,00, sem sinal) e o mês do trimestre de entrada. Região × produto e cliente com histórico foram testados e ficaram fora. A urgência ficou desligada.

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

- **Prospecting não tem data de entrada.** A conversão `c` só é aprendida a partir do segundo upload, comparando as bases; até lá vale 50%. Deals que continuam em Prospecting não entram na conta; se o CRM nunca encerrar Prospecting parados, `c` tende a ficar otimista.
- **Chance por situação é uma média da faixa.** Deals do mesmo produto na mesma situação empatam no score. Perto da chance semana a semana, a v2 captura 0,3 p.p. a menos de receita (55,3% contra 55,6%), em troca de uma fórmula explícita por situação.
- **Urgência e relacionamento não são validados causalmente.** Sem registro de ações, o teste mede se a lista aponta para receita que entrou, não se agir mudou o resultado.
- **Sem histórico de atividades.** Sem dados de ligações, reuniões ou próximo passo, o modelo só enxerga tempo e valor. Qualquer campo novo entra como um grupo a mais e ganha peso só se o backtest aprovar.
- **Foto única da base.** O CRM exporta o estado atual, não as mudanças de estágio. O backtest reconstrói o passado a partir das datas de entrada e fechamento.
- **Sem autenticação por usuário.** O filtro por vendedor não é uma permissão. Para produção: SSO do G4 e visão restrita por vendedor/manager.
- **Efeito da própria ferramenta.** Deals bem pontuados recebem mais atenção, o que contamina o aprendizado futuro. Para medir o impacto e evitar esse ciclo: registrar score exibido e ação tomada, e reservar parte da lista para deals incertos.
- **Escala.** O motor processa ~9 mil oportunidades em menos de 1 s. Para centenas de milhares, mover o treino para um job agendado e guardar os scores em banco.
