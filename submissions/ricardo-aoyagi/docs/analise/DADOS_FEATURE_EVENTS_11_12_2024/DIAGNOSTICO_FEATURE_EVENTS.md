# Diagnóstico: uso de features, eventos de churn e tickets

*Versão preliminar, não é a resposta final. Baseada em `01_Uso_Eventos_Tickets.xlsx` desta pasta. Os CSVs originais não foram alterados.*

*Este estudo parte das tabelas de **uso de features** e de **eventos de churn**, com foco em nov/dez de 2024. A tabela de assinaturas entra só para saber a qual conta pertence cada assinatura (o uso é registrado por assinatura, o evento por conta) e como prova na aba 4.*

---

## Resumo

1. **Em nov/dez, quem teve evento de churn usou o produto igual a quem não teve.** A quantidade de uso, as features e a proporção de erros são as mesmas.
2. **Nada muda em volta do evento.** O uso continua no mesmo ritmo depois do "churn": 6 em cada 10 contas seguem usando o produto.
3. **O motivo registrado não combina com o uso nem com o comentário do cliente.** Quem marcou "features" usa e erra igual a quem marcou "budget".
4. **A data de uso parece sorteada.** Cada assinatura tem cerca de 5 registros de uso, não importa quando começou nem quanto durou. Por isso, filtrar "uso de nov/dez" não mostra o que os clientes fizeram nesses meses.
5. **Na base inteira, sem olhar datas, o perfil de uso de quem teve churn é igual ao de quem nunca teve.** Sinal fraco que se repete: feature_10.
6. **Quem teve churn não reclama mais nem é atendido pior.** E a tabela de tickets não registra o assunto da reclamação, então não dá para saber *o que* foi reclamado.

---

## 1. Grupos comparados

| Grupo | Contas | O que é |
|---|---|---|
| **1. Evento em nov/dez** | 141 | Conta com evento de churn datado em nov/dez de 2024 (185 eventos) |
| **2. Evento só em outro mês** | 211 | Conta com evento de churn, mas nenhum em nov/dez |
| **3. Nunca teve evento** | 148 | Conta "não churneada" |

---

## 2. Passos que seguimos

| # | Pergunta | Aba |
|---|---|---|
| 1 | Em nov/dez, quem teve evento usou o produto de outro jeito? | `1_Uso_NovDez` |
| 2 | O uso muda nos 30 dias antes e depois de cada evento? | `2_Antes_e_depois_do_evento` |
| 3 | O motivo registrado combina com o uso e com o comentário? | `3_Motivo_x_Uso` |
| 4 | Por que o recorte por data de uso não mostra nada? | `4_Data_de_uso` |
| 5 | Sem olhar datas, o perfil de uso de cada conta difere entre os grupos? | `5_Perfil_de_uso_base_inteira` |
| 6 | Feature a feature, quem usa e quanto erra? | `6_Features_por_grupo` |
| 7 | Tickets: quem teve churn contra quem nunca teve | `7_Tickets_por_grupo` |

---

## 3. O que encontramos

### Uso em nov/dez (aba 1)

| Por conta, em nov/dez | Com evento | Sem evento | Diferença confiável? |
|---|---|---|---|
| Registros de uso | 4,2 | 4,4 | Não |
| Quantidade de usos | 42 | 44 | Não |
| Features diferentes | 4,0 | 4,1 | Não |
| % dos registros com erro | 29,5% | 28,7% | Não |
| % em feature beta | 8,9% | 10,0% | Não |

- Feature por feature, nenhuma é mais ou menos usada por quem teve evento.
- No erro, só 2 das 40 aparecem diferentes, com poucos registros (feature_18 e feature_31). É o esperado por acaso.

### Antes e depois do evento (aba 2)

| Medida | Valor |
|---|---|
| Registros de uso nos 30 dias antes, por evento | 1,96 |
| Registros de uso depois, a cada 30 dias | 1,96 (mesmo ritmo) |
| Eventos em que a conta **usou o produto depois** do "churn" | **61%** |
| % com erro nos 30 dias antes | 29% (média geral da base: 31%) |
| Eventos sem nenhum uso nos 30 dias antes | 15% |
| Contas sem evento, em datas sorteadas, sem uso nos 30 dias antes | 16% |
| Eventos com ticket nos 30 dias antes | 15% |
| Eventos que coincidem (±7 dias) com o fim de alguma assinatura | **18%** |

O evento de churn não marca uma saída real. A conta continua usando, e na maioria dos casos nenhuma assinatura termina perto da data do evento.

### Motivo registrado (aba 3)

- **O motivo não muda o uso.** Uso e erro antes do evento são parecidos em todos os motivos, de 23% a 33% de registros com erro, sem diferença confiável.
- **O comentário do cliente não acompanha o motivo.** Exemplos:
  - motivo "support": 12 comentários "too expensive";
  - motivo "features": 9 "too expensive", 9 "missing features" e 9 "switched to competitor".

### A data de uso não acompanha as assinaturas (aba 4)

**(A) O uso total fica parado.** Cerca de 1.000 registros por mês, de jan/23 a dez/24. Nesse tempo, as assinaturas ativas foram de 3 para 4.707.

**(B) Toda assinatura tem cerca de 5 registros de uso:**
- a média é 5,0 tanto nas iniciadas em 2023 quanto nas de nov–dez/24;
- vale para assinaturas que duraram 10 dias e para as que duraram 2 anos.

**(C) Datas fora da vida da assinatura.** Dos 2.067 registros com data em nov/dez:
- 17% são de **antes** de a própria assinatura começar;
- 5% são de **depois** de ela acabar.

**Consequência:**
- O recorte "uso de nov/dez" pega uma amostra quase aleatória, não o que os clientes fizeram nesses meses.
- A frase **"o uso cresceu"**, do time de produto, não se sustenta nesta tabela: o uso total ficou parado enquanto o número de assinaturas multiplicou.

### Perfil de uso na base inteira, sem datas (abas 5 e 6)

| Por conta | 1. Evento nov/dez | 2. Evento em outro mês | 3. Nunca |
|---|---|---|---|
| Assinaturas | 9,7 | 10,3 | 9,9 |
| Registros de uso | 48,8 | 51,2 | 49,4 |
| Horas de uso | 41,1 | 43,4 | 41,6 |
| Minutos por uso | 5,1 | 5,1 | 5,1 |
| Features diferentes (de 40) | 27,4 | 28,0 | 27,3 |
| % dos registros com erro | 31,3% | 30,6% | 31,0% |
| % em feature beta | 10,1% | 10,0% | 10,5% |

- Grupo 1 contra grupo 3: nenhuma diferença confiável.
- **Por feature (aba 6):** só 2 das 40 aparecem diferentes no uso, o esperado por acaso. Nenhuma tem diferença confiável no erro.
  - **feature_10:** usada por 75% das contas do grupo 1, contra 62% no grupo 3. Também com um pouco mais de erro (35% contra 26%), mas sem diferença confiável.
  - **feature_29:** usada por 61% contra 74%.
- **Sinal fraco que se repete:** a feature_10 também apareceu na análise Enterprise, com mais erro depois de 2023. Vale levar ao time de produto como pergunta, não como causa.

### Tickets: churneados contra não churneados (aba 7)

**Atenção:** a tabela de tickets não tem assunto, categoria nem texto da reclamação. Só registra prioridade, tempos, escalação e nota. Dá para comparar *como* foram os tickets, não *o que* foi reclamado.

| | 1. Evento nov/dez | 2. Evento em outro mês | 3. Nunca | 1 × 3 confiável? |
|---|---|---|---|---|
| Tickets por conta | 4,1 | 3,9 | 4,1 | Não |
| Contas com ao menos 1 ticket | 98% | 99% | 98% | Não |
| % urgentes | 23% | 26% | 28% | Não |
| % prioridade alta | 28% | 25% | 23% | **Sim** |
| % escalados | 4,5% | 5,5% | 4,0% | Não |
| Resolução (horas, média) | 36,1 | 35,5 | 36,1 | Não |
| 1ª resposta (minutos, média) | 89 | 88 | 88 | Não |
| Satisfação média (só notas 3 a 5) | 3,96 | 3,99 | 3,98 | Não |
| % sem nota | 41% | 42% | 41% | Não |

- A única diferença confiável é a prioridade "alta", maior no grupo 1.
- Mas o grupo 1 tem menos "urgentes", e a soma das duas prioridades é igual nos grupos (cerca de 51%). Muda o rótulo, não a gravidade.
- Olhando só os tickets abertos em nov/dez, o quadro é o mesmo.

---

## 4. O que isso significa (preliminar)

- **Uso de features, tickets e eventos de churn não conversam entre si nesta base.** Parecem preenchidos de forma independente. O evento de churn não marca uma saída real e o motivo registrado não bate com o comentário.
- **A causa do churn não está no uso nem no suporte.** Ela aparece no padrão de contratação e cancelamento de assinaturas: migrações, compras extras desfeitas e pacotes Enterprise desligados (ver `DADOS_2024_NOV_DEZ` e `DADOS_ENTERPRISE`).
- **Recomendações para a empresa:**
  - registrar o assunto de cada ticket;
  - registrar a data real de cada uso;
  - amarrar o evento de churn ao cancelamento real da assinatura;
  - abrir a escala de satisfação para notas 1 e 2.

---

## 5. Limites

- A base é **fictícia** (gerada por computador). Parte das incoerências pode vir do gerador.
- **"Diferença confiável?"** usa o teste de Fisher para proporções e o embaralhamento dos grupos para médias, com corte de 5%. Com menos de 10 casos, a resposta é "Poucos casos para concluir".
- **Datas de ticket pouco confiáveis:** 54% dos tickets são anteriores ao cadastro da conta.
- **Referência sorteada:** a referência "sem uso nos 30 dias antes" (aba 2) é calculada por sorteio fixo no programa, por isso aparece como valor e não como fórmula.

---

## Arquivos desta pasta

| Arquivo | Conteúdo |
|---|---|
| `01_Uso_Eventos_Tickets.xlsx` | 7 abas de análise e as bases usadas (contas, uso de nov/dez, eventos, conta × feature, uso por mês, assinaturas, tickets) |
| `scripts/01_uso_eventos_tickets.py` | Programa que gera a planilha a partir dos CSVs originais |
