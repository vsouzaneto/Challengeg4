# Tempo de triagem: hoje × com IA

_Gerado por `02_modelo_desperdicio.py` (mesmo cálculo do app: `03-prototipo/src/roi.py`). Revisado por agente juiz: `process-log/revisoes/fase3_benchmark_roi_parecer.md`._

## Resposta curta

A triagem com IA libera entre **552 e 2.106 horas de agente por ano**, ou 46 a 175 h/mês (0,3 a 1,2 pessoa). No cenário base, são **1.218 h/ano ≈ 101 h/mês ≈ 0,7 pessoa ≈ R$ 46.563/ano**. É **tempo liberado bruto**, não economia de caixa, e ainda não desconta implantação e manutenção.

## O que é medido e o que é premissa

| Item | Valor | Tipo |
|---|---|---|
| Volume | 30.000 tickets/ano | Enunciado do case |
| Faixa automática | 65,5% dos tickets, 96,4% de acerto | **Medido** (9.568 tickets de teste, Dataset 2) |
| Faixa de sugestão (humano escolhe entre 2) | 23,3% | **Medido** |
| Faixa humana | 11,2% | **Medido** |
| Minutos para triar 1 ticket hoje | 1,5 / 3 / 5 (cenários) | **Premissa**, fonte fraca: blogs de fornecedores (3–8 min) × boa prática (< 2 min) |
| Tempo residual com IA | 10 s para conferir; 30 s para escolher entre 2 | **Premissa** de desenho, a validar no piloto |
| Custo da hora | R$ 38,24 | salario.com.br, CBO 2124-20, out/2026 (n = 64.048): R$ 6.959/mês com encargos, 42 h/semana |

## Cenários

| | Conservador | Base | Otimista |
|---|---|---|---|
| Minutos de triagem por ticket hoje | 1,5 | 3,0 | 5,0 |
| Horas de triagem hoje | 750 h | 1.500 h | 2.500 h |
| Horas com IA | 198 h | 282 h | 394 h |
| **Tempo liberado** | **552 h** | **1.218 h** | **2.106 h** |
| Pessoas (FTE de 1.747 h produtivas) | 0,3 | 0,7 | 1,2 |
| Valor do tempo (R$/ano) | R$ 21.105 | R$ 46.563 | R$ 80.508 |

## Leituras honestas

- **Sensibilidade:** o resultado é praticamente proporcional à premissa de minutos de triagem, a de fonte mais fraca. Por isso ela é o 1º item do piloto.
- **O que ficou de fora, de propósito:**
  - *Redução de roteamento errado.* O erro da IA foi medido contra o rótulo humano, e o erro humano atual não foi medido. A taxa de transferência de mercado (15–25%, MetricNet/ICMI) inclui escalonamentos legítimos e não equivale a erro de triagem. O app permite ligar essa hipótese com premissas próprias.
  - *Tempo de espera do cliente na fila errada.* É provavelmente o maior ganho para o cliente, mas não é mensurável com estes dados.
  - *Rascunho de resposta e autoatendimento.* São ganhos potenciais sem base para estimar.
- **Validade externa:** o desempenho foi medido em tickets internos de TI, em inglês. Uma operação de suporte ao cliente retreina com o próprio histórico e mede de novo.

## O piloto (4 semanas) mede, antes de qualquer decisão financeira

1. Minutos de triagem por ticket, antes × depois (substitui a premissa principal)
2. % de reatribuições de fila, antes × depois (decide se a hipótese de roteamento entra no ROI)
3. Tempo de espera em fila errada (o ganho para o cliente)
4. Concordância do agente com a IA na faixa automática (detecta deriva do modelo)