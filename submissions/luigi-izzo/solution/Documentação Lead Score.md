# 🎯 Regra de Negócio: Lead Scoring Model

## 1. Visão Geral e Arquitetura do Score

O **Lead Score** é calculado em uma escala de **0 a 100 pontos**, dividida em 4 pilares complementares que ponderam tanto o **perfil do cliente/produto** quanto o **comportamento e tempo do deal no pipeline**:

Score Final = Pilar 1 (Estágio) + Pilar 2 (Timing/Estagnação) + Pilar 3 (Perfil/Conta) + Pilar 4 (Produto/Ticket)

---

## 2. Tabelas de Pontuação por Pilar

### Pilar 1: Estágio Atual do Deal (`sales_pipeline`) — *Max: 25 pts*
Mede o nível de avanço da oportunidade no funil de vendas.

| Condição | Pontos | Justificativa de Vendas |
| :--- | :---: | :--- |
| `deal_stage = 'Engaging'` | **+25** | Deal em negociação ativa e contato direto com o cliente. |
| `deal_stage = 'Prospecting'` | **+10** | Oportunidade em fase inicial de qualificação. |

---

### Pilar 2: Tempo no Pipeline & Estagnação (`sales_pipeline`) — *Max: 30 pts*
Mede a recência do deal com base na mediana histórica de fechamento (57 dias) e no limite de estagnação (88 dias - P75).

| Idade do Deal (Dias em Aberto) | Pontos | Impacto / Explicabilidade |
| :--- | :---: | :--- |
| Menor ou igual a 30 dias | **+30** | Oportunidade Quente: Ritmo ideal de fechamento. |
| 31 a 60 dias | **+20** | Ritmo Normal: Dentro da mediana histórica (57 dias). |
| 61 a 90 dias | **+10** | Atenção: Próximo do limite saudável (88 dias). |
| Maior que 90 dias | **-15** | Alerta de Estagnação: Ultrapassou o P75 de ganho; alto risco de abandono. |

---

### Pilar 3: Fit de Perfil da Conta (`accounts`) — *Max: 25 pts*
Combina a taxa de conversão histórica do setor com o porte/capacidade financeira do cliente.

#### 3.1. Setor da Conta (`sector`) — *Max: 15 pts*
| Grupo de Setores | Pontos | Win Rate Histórico Médio |
| :--- | :---: | :---: |
| Top Performance (`Marketing`, `Entertainment`, `Software`) | **+15** | Maior que 63.9% |
| Performance Média (`Technology`, `Services`, `Retail`) | **+10** | 63.0% a 63.4% |
| Demais Setores (`Employment`, `Telecommunications`, `Medical`, `Finance`) | **+5** | Menor que 62.9% |

#### 3.2. Porte da Empresa (`revenue`) — *Max: 10 pts*
| Receita Anual da Conta (`revenue`) | Pontos | Justificativa |
| :--- | :---: | :--- |
| Maior que $1.000M | **+10** | Empresa Enterprise com grande orçamento disponível. |
| Menor ou igual a $1.000M | **+5** | Empresa de médio/pequeno porte. |

---

### Pilar 4: Atratividade do Produto & Ticket (`products`) — *Max: 20 pts*
Pondera a relevância financeira do produto ofertado.

| Faixa de Preço do Produto (`sales_price`) | Pontos | Exemplo de Produtos |
| :--- | :---: | :--- |
| Preço maior ou igual a $3.000 (High Ticket) | **+20** | `GTK 500`, `GTXPro`, `MG Advanced` |
| Preço menor que $3.000 (Standard Ticket) | **+10** | `GTX Basic`, `GTX Plus Basic`, `MG Special` |

---

## 3. Matriz de Categorização (Tiers de Prioridade)

Com base no Score Final calculado (0 a 100), cada oportunidade é classificada em 3 níveis de ação imediata para o vendedor:

| Faixa de Score | Tier | Indicador | Ação Recomendada para o Vendedor |
| :---: | :---: | :---: | :--- |
| **80 a 100** | **High Priority** | Alta | **Foco Imediato:** Entrar em contato nas próximas 24h. Oportunidade quente de alto valor/conversão. |
| **50 a 79** | **Medium Priority** | Média | **Manter Nutrição:** Acompanhar conforme o fluxo normal da semana. |
| **0 a 49** | **Low Priority** | Baixa | **Revisar / Arquivar:** Deal estagnado ou com perfil de baixa conversão. Priorizar apenas se houver agenda livre. |

---

## 4. Estrutura de Explicabilidade (Explainability Log)

Para atender à exigência de o vendedor entender o motivo da nota, o algoritmo gera 3 tags explicativas por oportunidade:

- **Ponto Forte (Prós):** ex.: `+15 pts: Setor de Marketing possui alta conversão histórica`
- **Alerta de Risco (Contras):** ex.: `-15 pts: Deal parado no pipeline há 105 dias (estagnado)`
- **Ação Sugerida:** ex.: `Agendar reunião de fechamento esta semana`