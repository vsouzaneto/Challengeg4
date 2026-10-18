# Diagnóstico consolidado V1

*Versão preliminar. Baseada nas planilhas 01 a 04 desta pasta. Os CSVs originais não foram alterados. A base é a tabela de assinaturas, a única coerente (ver `DADOS_RECONCILIA`).*

---

## Resumo

1. **A perda real de receita é menos da metade do "churn" contado hoje:** US$ 538 mil contra US$ 1,18 milhão de MRR em 24 meses (46%). No 4º trimestre de 2024 a diferença é maior: US$ 331 mil contra US$ 872 mil (38%).
2. **Das 8 contas Enterprise que perderam mais da metade do valor numa redução, só 4 seguem com a perda.** São elas as prioritárias: A-13466a, A-f44180, A-8ae05d e A-69fad4.
3. **A partir de jul/2024 todos os segmentos passaram a comprar 2 a 3 vezes mais por mês.** A piora (compra em rajada, cancelamento em até 30 dias) aparece em todos ao mesmo tempo. Não há um país, indústria ou canal "vendendo errado" sozinho.
4. **As datas de tickets e de uso estão espalhadas ao acaso e não dá para recuperá-las.** O evento de churn também não se liga ao cancelamento real: fica perto de um fim de assinatura na mesma proporção de uma data sorteada.

---

## 1. Contas Enterprise prioritárias (`01_Contas_Enterprise_Prioritarias.xlsx`)

**Como escolhemos:** entre as 68 reduções Enterprise pagas em que a conta seguiu com outra Enterprise, as 8 que cortaram mais de 50% do valor mensal da conta. Juntas, perderam US$ 68,9 mil por mês.

**As 4 que não recuperaram:**

| Conta | Indústria · País · Canal | O que aconteceu | MRR antes → 31/12/2024 |
|---|---|---|---|
| A-13466a | DevTools · AU · event | Cortou 40 seats e seguiu cortando | US$ 8.927 → US$ 171 |
| A-f44180 | Cybersecurity · UK · event | Anual de 89 seats encerrado com 213 dias | US$ 25.870 → US$ 9.286 |
| A-8ae05d | FinTech · IN · other | Anual de 86 seats encerrado com 31 dias; abriu Enterprise trial de 86 seats no mesmo mês | US$ 26.230 → US$ 9.116 |
| A-69fad4 | FinTech · UK · ads | Cortou 22 seats após 200 dias | US$ 8.056 → US$ 3.678 |

**As outras 4:**
- **Recuperaram e hoje pagam mais:** A-42e5e1, A-425e76 e A-bcf87c.
- **Compra a mais desfeita em 3 dias:** A-c45b23.

**Pontos comuns:**
- Três das 8 eram contratos **anuais** encerrados antes de 12 meses.
- Eventos de churn e tickets dessas contas não coincidem com a redução.
- Perfil: FinTech 4, DevTools 3; Reino Unido 4. Com 8 casos, nada disso é conclusivo.

---

## 2. Perda real por trimestre (`02_Perda_Real_por_Trimestre.xlsx`)

**Como cada assinatura encerrada foi classificada:**

| Situação | Regra | Conta como perda? |
|---|---|---|
| **Troca** | A conta abriu outra assinatura até 7 dias antes ou depois | Só a diferença de valor |
| **Compra extra desfeita** | Assinatura com até 30 dias, havendo outra mais antiga do mesmo plano ativa | Não |
| **Redução real** | A conta desligou uma assinatura e seguiu cliente | Sim |
| **Saída do cliente** | A conta ficou sem nenhuma assinatura | Sim |

| Trimestre | "Churn" de hoje (qtd) | Perda real (qtd) | "Churn" de hoje (US$) | Perda real (US$) | % perda real |
|---|---|---|---|---|---|
| 2023-T4 | 14 | 11 | 49.160 | 46.218 | 94% |
| 2024-T1 | 27 | 20 | 50.138 | 44.828 | 89% |
| 2024-T2 | 37 | 29 | 59.026 | 36.192 | 61% |
| 2024-T3 | 80 | 43 | 146.668 | 77.445 | 53% |
| 2024-T4 | 324 | 84 | 871.812 | 331.314 | 38% |
| **24 meses** | **486** | **189** | **1.179.139** | **537.914** | **46%** |

**O que não era perda em 24 meses:**
- 233 trocas, com US$ 460.780 repostos em assinaturas novas;
- 64 compras extras desfeitas, somando US$ 180.445.

**A perda real se divide em:**
- redução real: US$ 400.148;
- saída de cliente: US$ 23.406, em 4 casos, todos de contas que voltaram depois;
- diferença nas trocas: US$ 114.360.

Por plano, o Enterprise concentra US$ 332 mil dos US$ 424 mil de redução e saída.

---

## 3. Ritmo de compra a partir de jul/2024 (`03_Ritmo_de_Compra_Segmentos.xlsx`)

- **Todos cresceram:** de 1,7 a 3,2 vezes mais compras por mês, média de 2,7 vezes.
  - Ganharam participação: EUA, Cybersecurity e canal orgânico.
  - Perderam: Alemanha, HealthTech e canal partner.
- **O crescimento veio de clientes antigos:** os cadastros de contas novas subiram 26% (de 121 para 152), contra +174% nas compras.
- **A piora foi geral:**
  - compra em rajada: de ~3% para ~22%;
  - cancelamento em até 30 dias: de 0,7% para 6,1%;
  - intervalo típico entre compras da mesma conta: de 26 para 11 dias.
- **Nenhum segmento difere de forma confiável no cancelamento em 30 dias.** A rajada é mais comum no canal orgânico (30%) e em DevTools (27%); a Alemanha quase não tem.
- **Leitura:** é uma mudança de processo (como se compra ou registra uma assinatura), não um vendedor ou mercado específico. O canal orgânico, que não tem vendedor, é o que mais compra em rajada.

---

## 4. Datas e evento de churn (`04_Eventos_x_Cancelamento_Real.xlsx`)

- **Tickets:**
  - cerca de 250 por trimestre, sempre;
  - contas cadastradas no 2º semestre de 2024 têm metade dos tickets datados em 2023;
  - contas grandes abrem tantos tickets quanto as pequenas;
  - a data real não pode ser recuperada.
- **Uso:** cerca de 3.100 registros por trimestre, sempre, e 77% deles têm data anterior ao início da própria assinatura.
- **Eventos:**
  - só 47 dos 600 (8%) têm um fim de assinatura da conta a até 7 dias; uma data sorteada na vida da mesma conta dá 7,6%;
  - em 91% dos eventos, a conta estava ativa no dia;
  - 214 eventos são de contas que nunca encerraram nenhuma assinatura.
- **Do lado dos cancelamentos:**
  - só 6% das reduções reais têm evento perto;
  - das 110 contas marcadas como churn, só 43 tiveram perda real.
- **Proposta:**
  - o churn oficial passa a vir da tabela de assinaturas;
  - o evento de churn é gerado automaticamente no fim real da assinatura, com o motivo perguntado nesse momento;
  - tickets e uso passam a gravar a data real.

---

## 5. Limites

- Base fictícia.
- As janelas de 7 dias (troca), 30 dias (compra extra) e a regra de rajada são escolhas da análise.
- Os valores sorteados e as medianas aparecem como números calculados pelo programa, não como fórmulas.

---

## Arquivos desta pasta

| Arquivo | Conteúdo |
|---|---|
| `01_Contas_Enterprise_Prioritarias.xlsx` | As 8 contas, a linha do tempo de cada uma e o perfil |
| `02_Perda_Real_por_Trimestre.xlsx` | Resumo para o CEO com gráficos, quantidade, US$ e visão por plano |
| `03_Ritmo_de_Compra_Segmentos.xlsx` | Crescimento por segmento, sinais de venda errada, antes × depois e mês a mês por canal |
| `04_Eventos_x_Cancelamento_Real.xlsx` | Datas de tickets e uso, evento × cancelamento real e regra proposta |
| `scripts/` | `comum.py` (regras compartilhadas) e os programas 01 a 04 |
