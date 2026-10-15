# Motor de triagem final: avaliação no conjunto de teste

_9.568 tickets reais do Dataset 2 que o modelo nunca viu. Gerado por `benchmark/avaliar_motor.py`._

## 1. Faixas de automação

| Faixa | % dos tickets | Acerto da 1ª opção | Certa entre as 2 primeiras |
|---|---|---|---|
| Automático | 65,5% | 96,4% | 99,4% |
| Sugestão (humano escolhe entre 2) | 23,3% | 63,4% | 91,0% |
| Humano | 11,2% | 72,4% | 90,2% |

**Por que um ticket vai para humano:**

| Motivo | % de todos os tickets | O modelo acertaria | Sem as travas, iria para |
|---|---|---|---|
| confiança baixa | 1,5% | 33,6% | humano 100,0% |
| trava de domínio | 9,7% | 78,6% | auto 55,7%, sugere 41,8%, humano 2,5% |

A trava de domínio troca cobertura por segurança: ela também barra tickets normais, porém atípicos (pouco parecidos com o histórico), que o modelo acertaria na maioria das vezes. É o custo de não deixar passar tickets de outro domínio (seção 3).

Intervalo de confiança de 95% (bootstrap) para o acerto da faixa automática: **95,9% a 96,8%**.

Para comparar: o modelo sem as travas acerta 86,0% no geral.

## 2. Faixa automática por categoria prevista

| Categoria | Limiar | Origem do limiar | Tickets automáticos | Acerto | IC95% (bootstrap) |
|---|---|---|---|---|---|
| Access | 0,71 | global (validação) | 1060 | 97,8% | 97,0% a 98,7% |
| Administrative rights | 0,71 | global (validação) | 174 | 96,0% | 92,5% a 98,9% |
| HR Support | 0,71 | global (validação) | 1569 | 95,8% | 94,8% a 96,7% |
| Hardware | 0,78 | próprio da categoria | 1563 | 95,1% | 94,0% a 96,2% |
| Internal Project | 0,71 | global (validação) | 281 | 96,4% | 94,3% a 98,6% |
| Miscellaneous | 0,75 | próprio da categoria | 810 | 96,0% | 94,7% a 97,3% |
| Purchase | 0,71 | global (validação) | 410 | 99,0% | 98,0% a 99,8% |
| Storage | 0,71 | global (validação) | 401 | 97,8% | 96,3% a 99,0% |

Só as categorias que ficariam abaixo de 95% com o limiar global (Hardware e Miscellaneous) ganharam limiar próprio. As demais usam o global; categorias com menos de 150 casos na validação usam o global por estabilidade. Os acertos por categoria são estimativas pontuais: Hardware, no limite, tem intervalo que passa abaixo de 95%.

**Principais erros automáticos (real → previsto):** Hardware → HR Support: 26; Administrative rights → Hardware: 22; HR Support → Hardware: 20; Miscellaneous → HR Support: 17; Hardware → Miscellaneous: 15

## 3. Teste fora do domínio (tickets de cliente do Dataset 1)

Um modelo de TI interna recebendo tickets de clientes de produto deveria perceber que não sabe.

| Faixa | % dos 8.469 tickets |
|---|---|
| auto | 10,8% |
| sugere | 8,7% |
| humano | 80,5% |

Sem as travas de domínio, **34,1%** desses tickets teriam ido para a faixa automática.

### Sensibilidade da trava de similaridade

O limiar 0,20 foi escolhido por inspeção das duas distribuições, e não por otimização. Como o Dataset 1 foi usado para escolhê-lo, o resultado fora do domínio é otimista. A tabela mostra a sensibilidade:

| Limiar | Tickets normais barrados (validação) | Tickets de outro domínio barrados (Dataset 1) |
|---|---|---|
| 0,15 | 1,7% | 36,4% |
| 0,20 | 10,4% | 80,1% |
| 0,25 | 24,0% | 95,7% |

## 4. Política no conjunto de teste

- 23,4% dos tickets têm uma ação que exige humano
- 2,7% bloqueiam o rascunho por LLM
- 7,9% são escalados

| Regra | Tickets |
|---|---|
| Aprovação financeira | 1009 |
| Urgência / indisponibilidade | 710 |
| Privilégio de acesso | 335 |
| Saúde / afastamento | 194 |
| Desligamento | 189 |
| Segurança | 70 |