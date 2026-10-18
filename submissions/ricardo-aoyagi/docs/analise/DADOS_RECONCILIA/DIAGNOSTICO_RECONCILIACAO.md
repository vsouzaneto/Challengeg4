# Diagnóstico de churn da RavenStack: o que a base permite afirmar

*Versão preliminar. Baseada nas planilhas desta pasta (01, 02 e 03). Os CSVs originais não foram alterados.*

---

## Resumo

1. **A base tem problemas sérios.** Três das cinco tabelas trazem informações que se contradizem. Só a tabela de **assinaturas** é coerente do começo ao fim, e por isso ela virou a referência.
2. **As três formas de marcar churn não conversam entre si.** Das 500 contas, só 100 têm as três marcações dizendo a mesma coisa.
3. **O churn não está concentrado em um tipo de cliente.** Indústria, país, canal, plano, tamanho, uso e suporte não explicam quem sai.
4. **O churn está concentrado no tempo.** As assinaturas novas cancelam muito mais nos primeiros 30 dias, e isso piorou a partir de **julho de 2024**, com pico em **dezembro de 2024**.
5. **Satisfação e uso não mudaram.** Por isso o CS ("satisfação ok") e o produto ("uso cresceu") não enxergaram o problema: os indicadores que eles acompanham não se movem junto com o churn.

---

## 1. Problemas encontrados na base

| Tabela | Situação | O que está errado |
|---|---|---|
| **Assinaturas** | ✅ Confiável | Tudo bate: valor mensal = número de usuários × preço do plano; data de fim preenchida = assinatura cancelada; nenhuma assinatura começa antes do cadastro da conta. Exceção pequena: 23 assinaturas (0,5%) marcadas com upgrade e downgrade ao mesmo tempo. |
| **Contas** | ❌ Não confiável | A marcação "churn" da conta acerta tanto quanto um sorteio. Das 110 contas marcadas como churn, **nenhuma** está sem assinatura ativa. O "plano inicial" bate com a primeira assinatura em só 1 a cada 3 contas. |
| **Eventos de churn** | ❌ Não confiável | Em **9 a cada 10** eventos a conta continua com assinatura ativa no dia do "churn". Só 8% dos eventos coincidem com o fim de alguma assinatura. O motivo registrado não tem relação com o comentário do cliente: um "concorrente" aparece com "caro demais" tanto quanto com "mudei para concorrente". As marcações de reativação e de upgrade/downgrade anterior também não batem com o histórico. |
| **Uso de features** | ⚠️ Parcial | **77%** dos registros de uso têm data anterior ao início da assinatura, e **53%** são anteriores até ao cadastro da conta. As quantidades servem; as datas não. |
| **Tickets de suporte** | ⚠️ Parcial | Os dados internos batem (tempo de resolução, notas de 1 a 5), mas **54%** dos tickets foram abertos antes de a conta existir. |

**As três marcações de churn** (conta marcada, evento registrado e assinatura cancelada) se comportam como se tivessem sido preenchidas de forma independente. Saber uma não ajuda a prever a outra.

| Combinação | Contas |
|---|---|
| As três dizem "saiu" | 50 |
| As três dizem "ficou" | 50 |
| Se contradizem | **400** |

---

## 2. Exemplos

| Conta | O que mostra |
|---|---|
| **A-0a282f** | Marcada como "não churn", mas tem 2 eventos de churn (06/10 e 31/12/2024). No mesmo dia do primeiro "churn" a conta **abre** uma assinatura nova e continua abrindo outras nos dias seguintes, incluindo uma Enterprise de US$ 5,8 mil/mês. |
| **A-038089** | Marcada como "churn", com 2 eventos de churn, mas tem 3 assinaturas ativas. Uma delas foi aberta em 30/12/2024, **depois** do último churn. |
| **A-10b8da** | Marcada como "churn", **sem nenhum** evento de churn e com 5 assinaturas ativas. |
| **Assinatura S-0896f4** | A conta foi cadastrada em 04/09/2024 e a assinatura começou em 08/12/2024, mas há uso registrado desde **08/02/2023**. |

As linhas completas estão na aba *Exemplos* de `01_Evidencias_Consistencia.xlsx`.

---

## 3. Passos que seguimos

1. **Conferimos a coerência de cada tabela** (`01_Evidencias_Consistencia.xlsx`). Testamos 28 regras simples, linha a linha, como "a data de fim vem depois da data de início?". Cada linha da planilha mostra OK ou FALHA.
2. **Escolhemos a tabela de assinaturas como referência**, porque foi a única que passou em todas as regras. As outras marcações de churn ficaram apenas como confirmação.
3. **Comparamos 22 possíveis causas usando as três marcações** (`02_Triangulacao.xlsx`). Para cada causa (indústria, plano, uso, suporte…), vimos se quem tem aquela característica cancela mais. Só aceitamos como causa o que aparecesse na tabela de referência e em pelo menos uma das outras, e que não pudesse ser explicado por acaso.
4. **Olhamos o churn ao longo do tempo** (mesma planilha, aba *Tempo*): por idade da assinatura, por mês e por mês de entrada.
5. **Investigamos o que mudou no 2º semestre de 2024 e em dezembro** (`03_Coortes_2024S2.xlsx`). Comparamos as assinaturas novas desse período com as anteriores, perfil por perfil.
6. **Repetimos a checagem nas 100 contas em que as três marcações concordam**, como prova dos nove.

---

## 4. O que os dados dizem sobre o churn

### Não é um tipo de cliente
Nenhuma das 22 características testadas explica o churn de forma consistente. Cancelam na mesma proporção:
- clientes de qualquer indústria, país ou canal;
- clientes de qualquer plano ou tamanho;
- clientes que usam muito ou pouco;
- clientes que abrem muitos ou poucos tickets;
- clientes satisfeitos ou insatisfeitos.

### É um problema de tempo
- **Primeiros 30 dias:** uma assinatura nova tem cerca de **5 vezes** mais chance de cancelar no primeiro mês do que depois de 6 meses.
- **Piorou a partir de julho de 2024:**

  | Assinaturas novas que cancelam em até 30 dias | % |
  |---|---|
  | Até junho de 2024 | ~0,7% |
  | A partir de julho de 2024 | ~4,2% (6 vezes mais) |
  | Novembro de 2024 | 8% |

  A piora atinge **todos os perfis ao mesmo tempo**: todos os planos, indústrias, países e canais. Não foi a entrada de um tipo diferente de cliente.
- **Dezembro de 2024 é atípico:**
  - 193 assinaturas encerradas (US$ 575 mil/mês), contra cerca de 75 esperadas;
  - 2 em cada 3 tinham até 30 dias de vida;
  - **61 encerramentos ficaram concentrados entre 29 e 31/12**, cerca de 20 por dia contra 5 por dia no resto do mês.

### O que não mudou
Satisfação (~4 de 5), tempo de atendimento, escalações, uso e erros ficaram estáveis o período todo. **Esses indicadores não avisam sobre o churn.**

---

## 5. O que isso significa (preliminar)

- **A causa provável é algo que mudou por volta de julho de 2024** e afeta quem acabou de assinar: produto, preço, cobrança, onboarding ou concorrência. Essas tabelas não registram esse tipo de mudança. É preciso cruzar as datas com o histórico da empresa (lançamentos, reajustes, campanhas).
- **Confirmar os encerramentos de 29 a 31/12** com a área responsável antes de tratá-los como perda de clientes. Pode ser fechamento de ano, renovação anual ou corte na extração dos dados.
- **Definir uma única regra oficial de churn** e fazer o motivo registrado bater com o que o cliente diz. Hoje cada área conta churn de um jeito, e as contagens não conversam.
- **Acompanhar de perto os primeiros 30 dias de cada assinatura nova**: é onde está o risco.

---

## 6. Limites

- A base é **fictícia** (gerada por computador, segundo o próprio autor). Parte das incoerências pode vir do gerador e não de um processo real da empresa.
- Ser coerente não é o mesmo que ser verdadeiro: a tabela de assinaturas é a mais confiável que temos, não uma garantia.
- Não achar efeito numa característica significa que **estes dados** não mostram efeito, não que ele não exista.

---

## Arquivos desta pasta

| Arquivo | Conteúdo |
|---|---|
| `01_Evidencias_Consistencia.xlsx` | 28 regras testadas linha a linha, resumo por tabela, cruzamentos e exemplos |
| `02_Triangulacao.xlsx` | 22 possíveis causas comparadas nas três marcações de churn; análise no tempo |
| `03_Coortes_2024S2.xlsx` | O que mudou no 2º semestre de 2024, dezembro, suporte/uso no tempo e as 100 contas "limpas" |
| `scripts/` | Programas que geram as planilhas a partir dos CSVs originais |
