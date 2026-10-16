# G3 revisado: Lead Kanban e regra do prazo máximo

**Status:** implementado em 15/10/2026. Substitui a regra de pontos de atenção do [G3 original](08-g3-fila-comercial.md).

- Regra: [`solution/leadscore/priority.py`](../solution/leadscore/priority.py)
- Interface: [`solution/web/`](../solution/web/), com Pipeline, Dashboard e Procedimento
- Backtest: [`solution/evaluate_focus.py`](../solution/evaluate_focus.py), com resultados agregados em [`solution/experiments/g3-focus-backtest.json`](../solution/experiments/g3-focus-backtest.json)

## Por que revisar

A Head de RevOps descreveu dois sintomas: vendedores gastam tempo em **negócios que não vão fechar** e deixam **oportunidades boas esfriarem**. A regra original somava etapa, faixa de preço, tempo em `Engaging` e conta ausente. Como dava mais pontos aos negócios mais antigos, ela empurrava o vendedor para o primeiro sintoma:

- Nenhum dos **6.711** negócios concluídos levou mais de **138 dias** entre a entrada em `Engaging` e o fechamento (mediana de 45).
- **1.291 dos 1.589** negócios abertos em `Engaging` (81%) já passaram desse limite.
- **350 das 431** oportunidades de prioridade "Alta" e **45 das 50** primeiras da fila original estavam além do limite.

Os atributos fixos continuam sem sinal útil: a taxa de ganho por produto fica entre 60% e 65%, e por setor entre 61% e 65%. Isso explica o resultado do G2 (AUC 0,513). O sinal que existe é o **tempo**: perdas se decidem cedo (mediana de 14 dias, contra 57 dos ganhos) e nada fechou depois de 138 dias.

## Regra atual

O **prazo máximo** é o fechamento mais longo entre os negócios concluídos até a data de referência. Nenhum desfecho dos negócios avaliados entra na regra.

| Coluna | Critério | Ordem | Ação |
|---|---|---|---|
| **Negociar** | `Engaging` há até 138 dias | Valor potencial; no empate, o mais recente | Depende da fase (abaixo) |
| **Qualificar** | `Prospecting`, sem data de entrada | Valor potencial | Confirmar necessidade, decisor e prazo |
| **Confirmar ou encerrar** | `Engaging` há mais de 138 dias (prazo excedido) | Valor potencial; no empate, o mais antigo | Confirmar com o cliente e atualizar a etapa no CRM |

As fases da coluna Negociar orientam a ação, mas não mudam a ordem:

- **Início:** de 0 a 14 dias. É quando a maioria das perdas acontece; confirmar interesse e decisor.
- **Em andamento:** de 15 a 89 dias. Já passou do período de maior risco; definir o próximo marco.
- **Perto do limite:** de 90 a 138 dias. Faltam poucos dias para o prazo máximo, e negócios nesta fase costumam travar; buscar a decisão.

O **valor potencial** é o preço de catálogo do produto. Não inferimos moeda nem o tratamos como valor negociado ou probabilidade. A conta pendente gera uma tarefa de cadastro e não altera a coluna nem a ordem.

### Termos revisados

| Antes | Agora | Motivo |
|---|---|---|
| Foco da semana | Negociar | Verbo de ação, paralelo às outras colunas |
| Limpar pipeline | Confirmar ou encerrar | Descreve o que o vendedor faz |
| Valor em jogo | Valor potencial | Termo comum em vendas |
| Ciclo histórico | Prazo máximo | Diz o que é: o maior tempo até um fechamento |
| Fase de risco / Janela final / Fora do ciclo | Início / Perto do limite / Prazo excedido | Leitura direta, sem jargão |

## Interface

- **Barra superior fixa:** navegação entre Pipeline e Dashboard, filtros globais (regional, manager, vendedor e busca) e o botão **?**.
- **Pipeline:** as três colunas, cada uma com contagem, valor potencial e resumo. Os cartões mostram posição, valor, barra de prazo, fase e progresso das ações. O detalhe traz próximas ações, motivos, régua de prazo, conta e histórico. Há exportação em CSV.
- **Dashboard:** relatório de uma página para a gestão, organizado em blocos:
  - KPIs: valor em negociação no prazo, a qualificar e a confirmar ou encerrar, mais o **pipeline no prazo** (Negociar ÷ (Negociar + Confirmar ou encerrar), em valor, lido como "de cada 100 em negociação, X ainda estão no prazo");
  - composição por regional, manager ou vendedor;
  - quatro rankings por vendedor: maior valor em negociação, mais valor a confirmar ou encerrar, menor saúde e sem negociação no prazo;
  - a seção **"Por que a fila funciona assim"**, com 4 fatos: o prazo máximo, a parte do pipeline que já o excedeu, os ganhos por fase e a receita comparada às outras regras. Os histogramas completos ficam recolhidos;
  - uma tabela ordenável com histórico de ganho, exportável em CSV.
- **Procedimento (botão ? ou tecla ?):** regras, fluxo de classificação, régua de prazos, ações por situação, ordem, indicadores, funcionalidades, evidências, glossário e limites. As ações exibidas são lidas dos dados gerados pela regra em Python, para não haver duas versões.
- As cores das três colunas passaram no validador de paleta para daltonismo. Todo gráfico tem legenda, tooltip e valores em tabela.

## Backtest exploratório

Em cinco fins de mês de 2017, reconstruímos os negócios que estavam em `Engaging` naquela data. O prazo máximo foi calculado apenas com negócios fechados até o corte. Cada regra escolheu 5 negócios por vendedor (150 vagas por corte), e o desfecho foi observado até 31/12/2017. Os empates na vaga de corte foram divididos proporcionalmente, como no G2. `Prospecting` ficou de fora por não ter datas.

Cada célula mostra **ganhos esperados / receita ganha** nas 150 vagas.

| Corte | Em `Engaging` | Prazo excedido | Regra anterior | Só valor potencial, sem colunas | Colunas + valor × taxa por idade | **Regra atual** |
|---|---:|---:|---:|---:|---:|---:|
| 31/05/2017 | 1.535 | 81 | 62,83 / 331.079 | 71,97 / 501.904 | 77,95 / 524.888 | **72,83 / 526.251** |
| 30/06/2017 | 1.686 | 149 | 38,82 / 234.312 | 62,93 / 393.929 | 52,95 / 344.302 | **74,00 / 466.947** |
| 31/07/2017 | 2.257 | 275 | 42,30 / 258.698 | 56,62 / 373.898 | 57,04 / 383.947 | **64,00 / 426.524** |
| 31/08/2017 | 2.265 | 408 | 23,50 / 125.634 | 46,22 / 266.242 | 54,85 / 307.934 | **57,50 / 334.887** |
| 30/09/2017 | 2.409 | 530 | 12,70 / 67.683 | 37,53 / 227.005 | 32,08 / 195.494 | **58,00 / 335.186** |
| **Total** | | | **180 / 1,02 mi** | **275 / 1,76 mi** | **275 / 1,76 mi** | **326 / 2,09 mi** |

As vagas ocupadas por negócios com prazo excedido somaram **190** na regra anterior, **91** no baseline de valor e **zero** nas variantes com colunas.

**O que os números dizem:**

1. **A coluna Confirmar ou encerrar é a evidência mais forte.** Dos 1.443 casos que já tinham prazo excedido nas datas de corte, **nenhum fechou depois**, nem como ganho nem como perda.
2. **A regra anterior foi pior que ordenar só por valor.** Ela teve 180 ganhos esperados contra 275, porque reservava vagas para negócios travados.
3. **A regra atual superou o baseline de valor em receita em todos os cortes**, com cerca de 19% a mais de ganhos e de receita no total (IC 95% de +12% a +25%; ver "De onde vem o ganho").
4. **A ordem por idade vem deste número.** Os ganhos até o fim dos dados foram de **45%** na fase Início, **39%** em Em andamento, **19%** em Perto do limite e **0%** com prazo excedido. Por isso, no empate de valor, o mais recente vem primeiro, e acima do prazo máximo o negócio sai da negociação. O Dashboard mostra esse gráfico.
5. **A taxa de ganho por idade foi descartada.** Entre negócios concluídos, ela sobe com a idade (de 63% para 76% após 120 dias), mas ignora quem trava. Multiplicar o valor por essa taxa não melhorou a fila.

### Controles de robustez

Dois pontos da regra podiam ter sido ajustados aos dados. Por isso foram testados à parte (`robustness_summary` no JSON).

**1. O desempate, separando seleção e conferência.** O desempate foi escolhido depois de ver as 5 datas. Refazendo a escolha só com as 3 primeiras, o resultado seria o mesmo, e ele também vence nas 2 últimas. Não é uma validação independente, porque essas datas já tinham sido vistas, mas mostra que a vantagem não vem de uma data só. Cada célula mostra a receita ganha nas vagas do top 5.

| Desempate na coluna Negociar | Seleção (mai–jul) | Conferência (ago–set) |
|---|---:|---:|
| **Mais recente primeiro (regra atual)** | **1,42 mi** | **670 mil** |
| Mais antigo primeiro | 1,24 mi | 502 mil |
| Só valor, sem colunas | 1,27 mi | 493 mil |

**2. O prazo, comparando o máximo com percentis.** O prazo foi recalculado em cada data só com os fechamentos conhecidos até ela.

| Prazo | Dias (média das datas) | Receita no top 5 | Casos após o prazo | Desses, ganhos depois |
|---|---:|---:|---:|---:|
| **Máximo (regra atual)** | 138 | **2,09 mi** | 1.443 | **0** |
| Percentil 99 | ~128 | 2,10 mi | 1.637 | 9 |
| Percentil 95 | ~115 | 2,09 mi | 1.905 | 35 |
| Percentil 90 | ~104 | 2,10 mi | 2.202 | 86 |

O resultado da fila não depende do prazo exato: a receita varia menos de 1%. O que muda é o custo de errar. Um prazo menor mandaria para "Confirmar ou encerrar" vendas que ainda iam fechar. O máximo é a escolha conservadora: não marcou como parado nenhum negócio que viria a ser ganho.

### De onde vem o ganho

Para separar os dois usos da idade, o backtest inclui duas variantes intermediárias. Os totais são das 750 vagas do top 5, em 5 datas.

| Variante | Receita | Vagas com parados |
|---|---:|---:|
| Só valor potencial | 1,76 mi | 91 |
| Colunas e valor, sem desempate por idade | 1,90 mi | 0 |
| Valor e mais novo primeiro, sem colunas | 2,06 mi | 31 |
| **Regra atual** (colunas e mais novo primeiro) | **2,09 mi** | **0** |

- **Tirar os parados explica cerca de 40% do ganho; preferir os mais novos, o restante.** A explicação anterior ("não reservar vagas para parados") cobria só a primeira parte.
- **O desempate "mais antigo primeiro" não é neutro.** Ele escolhe os negócios perto do limite, que fecham menos. Por isso rende 1,74 mi, abaixo da variante sem desempate, e não serve como medida isolada do efeito de tirar os parados.
- **Bootstrap pareado** (150 pares vendedor × data, 5.000 reamostras, semente fixa):

  | Comparação | Ganho | IC 95% |
  |---|---:|---:|
  | Regra × só valor | +18,5% | +12,4% a +25,4% |
  | Regra × colunas sem desempate | +10,2% | +5,5% a +15,4% |
  | Regra × valor e idade sem colunas | +1,3% | +0,4% a +2,5% |

  O sinal é a idade. As colunas acrescentam pouco em receita sobre ordenar por valor e idade, mas tiram os 31 parados da agenda e dão a eles uma ação própria.

**Ressalva metodológica.** O backtest é **exploratório**:
- duas escolhas foram feitas depois de olhar os resultados: retirar a taxa por idade e desempatar pelo negócio mais recente. A segunda se mantém na conferência acima;
- o teste do G2 já tinha sido visto;
- os cortes se sobrepõem e o horizonte varia de 92 a 214 dias;
- o dataset parece sintético.

O backtest serve para descartar ideias ruins, não para prometer ganho em operação.

## Limites e próximos passos

- `engage_date` é a entrada na etapa, não o último contato. Com atividades datadas do CRM, "prazo excedido" poderia considerar dias sem interação.
- O prazo máximo deveria ser recalculado periodicamente, talvez por produto, e acompanhado de um percentil (o p90 é 104 dias).
- O sistema é somente leitura: recomenda ações, mas não altera o CRM. As ações marcadas ficam no navegador.
- Validação necessária: teste prospectivo com parte dos vendedores, medindo ciclo, taxa de resolução e receita, e revisão das ações com o time comercial.

## Reproduzir

A partir de `solution/`:

```powershell
python evaluate_focus.py --output experiments/g3-focus-backtest.json
python -m unittest discover -s tests -v
```
