# Diagnóstico Enterprise: de onde vem a perda

*Versão preliminar, não é a resposta final. Baseada na planilha `01_Enterprise_por_Periodo.xlsx` desta pasta e em consultas feitas depois dela (seções 4 a 6, que ainda não estão em planilha). Os CSVs originais não foram alterados. A base é a tabela de assinaturas, a única confiável (ver `DADOS_RECONCILIA`).*

*Períodos usados: 2023 · jan–jun/24 · jul–out/24 · nov–dez/24.*

---

## Resumo

1. **Não houve aumento de preço.** O preço por seat é o mesmo em todas as assinaturas e períodos: Enterprise US$ 199, Pro US$ 49 e Basic US$ 19, mensal ou anual.
2. **As reduções subiram em nov–dez/24, mas em todos os planos.** O Enterprise não reduz mais que os outros planos. O que cresce é o valor perdido, porque cada assinatura Enterprise vale muito mais.
3. **Os clientes não "regrediram" de plano.** Em 79 das 89 reduções, a conta continuou com outra assinatura Enterprise. Ela desligou um pacote inteiro e manteve os outros.
4. **Cerca de 1/3 da perda dessas 79 é compra extra desfeita.** São 21 casos e US$ 147 mil por mês: a conta comprou uma Enterprise a mais e cancelou em até 30 dias. Quase tudo em nov–dez/24.
5. **Cerca de 2/3 (US$ 283 mil por mês) são pacotes antigos desligados.** É o núcleo da perda real. O motivo não está registrado nas tabelas.
6. **Features, erros, reclamações e perfil não explicam as reduções.** Nenhuma indústria, canal ou país se destaca com segurança.
7. **A "rajada" é o ritmo de compra que acelerou.** O intervalo típico entre compras da mesma conta caiu de cerca de 30 dias (2023) para 8 dias (nov–dez/24). A rajada explica as migrações, não as reduções.

---

## 1. Preço e seats (aba 1)

- O preço por seat não muda em nenhum período, para nenhum plano.
- O valor médio das assinaturas Enterprise varia só porque o número médio de seats varia (de 27 a 32), sem tendência.

| Enterprise pagas iniciadas | 2023 | jan–jun/24 | jul–out/24 | nov–dez/24 |
|---|---|---|---|---|
| Assinaturas | 173 | 336 | 485 | 456 |
| Seats por assinatura (média) | 27,5 | 30,6 | 27,1 | 31,6 |
| Valor mensal por assinatura (média) | US$ 5.479 | US$ 6.093 | US$ 5.392 | US$ 6.279 |

---

## 2. Reduções no tempo (aba 2)

| Enterprise | 2023 | jan–jun/24 | jul–out/24 | nov–dez/24 |
|---|---|---|---|---|
| Reduções | 4 | 19 | 22 | 44 |
| A cada 100 assinaturas ativas, por mês | 0,54 | 0,85 | 0,66 | **1,66** |
| Valor mensal perdido, por mês do período | US$ 2 mil | US$ 10 mil | US$ 21 mil | **US$ 142 mil** |

- **A alta de nov–dez também aparece no Pro**, e o Basic sobe aos poucos. Em nenhum período o Enterprise fica diferente dos outros planos (diferença confiável? Não).
- **De jul–out para nov–dez, a perda por mês fica cerca de 7 vezes maior**, por duas razões:
  - o dobro de reduções por mês;
  - assinaturas reduzidas maiores (≈ US$ 6,5 mil contra ≈ US$ 3,8 mil por mês cada).
- **Das 44 reduções de nov–dez, 33 foram em dezembro**, e 12 só entre 29 e 31/12.

---

## 3. O que acontece numa redução Enterprise (aba 3 e consultas)

**Como a base funciona:**
- Cada conta tem várias assinaturas ao mesmo tempo, em média umas 8.
- Cada assinatura é um pacote com plano e número de seats fixos do início ao fim. Nenhuma assinatura muda de tamanho.
- Uma "redução" é o encerramento de um pacote inteiro, com a conta mantendo os demais.

| Depois da redução | Casos | Valor mensal perdido |
|---|---|---|
| Seguiu com outra Enterprise | 79 (11 eram trials, de valor zero) | US$ 431 mil |
| Ficou só com Basic/Pro | 10 (3 trials) | US$ 27 mil |
| Ficou sem assinatura | 0 | — |

**Exemplo, conta A-e1b9cd (27/06/2024):**
- Tinha 7 assinaturas ativas, entre elas duas Enterprise de 40 seats.
- Encerrou uma das Enterprise e perdeu US$ 7.960 por mês, cerca de 25% do que pagava.
- Continua cliente, e continua Enterprise.

**Quanto cada conta perdeu do que pagava** (68 reduções pagas que seguiram com Enterprise):

| Parte perdida do valor da conta | Reduções |
|---|---|
| Até 10% | 6 |
| 10% a 20% | 20 |
| 20% a 30% | 21 |
| 30% a 50% | 13 |
| Mais da metade | 8 |

- **A redução típica corta 25 seats**, cerca de US$ 5 mil por mês, ou 1/4 do valor da conta.
- **As 8 contas que perderam mais da metade** são os casos mais graves.

---

## 4. As 79 reduções que seguiram com Enterprise, uma a uma (consulta)

Para cada redução, olhamos as outras assinaturas Enterprise da conta:
- **"Gêmea":** outra Enterprise ativa com exatamente os mesmos seats. Havia em 29 casos.
- **Ordem e tempo:** quem foi criada antes e quanto tempo passou até o cancelamento.

| Situação | Com gêmea | Sem gêmea | Total | Valor mensal | Leitura |
|---|---|---|---|---|---|
| **A.** A conta já tinha Enterprise, comprou mais uma e cancelou essa nova em até 30 dias | 6 | 15 | **21** | **US$ 147 mil** | Compra extra desfeita; quase não é perda de receita |
| **B.** Cancelou um pacote antigo, tendo pacotes Enterprise mais novos | 14 | 26 | **40** | **US$ 226 mil** | Redução real, com dúvida |
| **C.** Cancelou sem ter pacote Enterprise mais novo | 9 | 9 | **18** | **US$ 58 mil** | Redução real |
| Total | 29 | 50 | 79 | US$ 431 mil | |

**Tempo até o cancelamento:**
- Da criação da gêmea até o cancelamento: de 9 a 379 dias, caso típico 64 dias.
- Nas sem gêmea, da Enterprise mais recente até o cancelamento: de 12 a 355 dias, caso típico 77 dias.
- Não há prazo fixo.

**Por que o grupo B não conta como "troca":**
- Na base, 78% das Enterprise ativas já têm uma Enterprise mais nova na mesma conta.
- 48% têm uma gêmea idêntica.
- Ou seja, as contas acumulam pacotes o tempo todo. Ter um pacote mais novo é o normal, não sinal de substituição.

**Exemplos:**
- **A-d4e0d4 (A):** abriu 117 seats em 16/11/24, abriu outra de 117 em 30/11 e cancelou essa em 03/12. Sozinho, vale US$ 23 mil por mês.
- **A-ce550d (A):** abriu uma Enterprise de 109 seats e cancelou no mesmo dia, 31/12/24 (US$ 21,7 mil por mês).
- **A-8b0451 (B):** abriu uma de 41 seats em 22/12 e cancelou a anterior de 41 seats em 31/12.

**Depois do cancelamento:** metade das 50 sem gêmea abriu alguma assinatura nova em até 90 dias (normalmente uns 20 dias depois), e 14 delas voltaram a abrir Enterprise.

---

## 5. Features, reclamações e perfil (abas 4 a 7)

- **Features:**
  - As 40 features aparecem no Enterprise desde 2023. Nenhuma "surge" num período.
  - Cerca de 30% dos registros de uso têm erro, em todos os períodos.
  - Ponto a checar com produto: feature_10 e feature_24 passam de ~15% para ~40% de registros com erro depois de 2023. É um sinal fraco: entre 40 testes, 2 "Sim" podem ser acaso.
  - A marca "beta" é aleatória.
- **Reclamações:**
  - Tickets por conta, escalações e satisfação ficam estáveis. Os tickets urgentes sobem um pouco em nov–dez (30% contra ~23%).
  - Quem reduz abre tickets no mesmo ritmo das demais contas, ou menos.
- **Perfil:**
  - As reduções acompanham o tamanho de cada grupo. EUA: 48 das 89 reduções e US$ 238 mil dos US$ 458 mil.
  - Cybersecurity, DevTools e FinTech lideram em quantidade. Os canais ficam equilibrados.
  - Único destaque, fraco: França em nov–dez/24, com 5 reduções.

---

## 6. Compras em rajada (consulta)

**Regra usada:**
- 3 ou mais assinaturas da mesma conta (qualquer plano) iniciadas dentro de uma janela de dias corridos, contada a partir de cada compra e sem olhar o mês.
- A regra original usava 7 dias.

**Enterprise em rajada (janela de 7 dias):**
- 262 assinaturas em 116 contas.
- O primeiro caso é de 05/06/2023.
- Vira padrão a partir de ago–set/24: 9% e 17% das Enterprise novas.
- Explode em dez/24: 41%.
- Quase metade (120) foi comprada por contas com menos de 30 dias de cadastro.

**Testando outras janelas:**

| Janela | 2023 | jan–jun/24 | jul–out/24 | nov–dez/24 | Das 89 reduções |
|---|---|---|---|---|---|
| 7 dias | 3% | 4% | 12% | 32% | 5 |
| **10 dias** | **3%** | 6% | 18% | **42%** | 8 |
| 14 dias | 8% | 11% | 29% | 52% | 14 |
| 20 dias | 9% | 17% | 44% | 64% | 22 |
| 21 dias | 10% | 18% | 45% | 67% | 26 |
| 28 dias | 18% | 27% | 58% | 73% | 37 |
| 30 dias | 21% | 31% | 60% | 74% | 39 |

- **Não há ponto de corte natural.** O número cresce de forma contínua com a janela.
- **10 dias é a janela que melhor separa o "antes" do "depois"**, sem pegar o ritmo normal de compra.
- **A partir de 14 dias, a janela começa a pegar o ritmo normal de compra**: com 28–30 dias, 1 em cada 5 Enterprise de 2023 já seria "rajada".

**O que realmente mudou: o intervalo entre compras da mesma conta**

| Início da Enterprise | Intervalo típico desde a compra anterior | Até 3 dias | Até 7 dias |
|---|---|---|---|
| 2023 | 30 dias | 8% | 15% |
| jan–jun/24 | 28 dias | 7% | 15% |
| jul–out/24 | 17 dias | 15% | 28% |
| nov–dez/24 | **8 dias** | **32%** | 48% |

- O número de contas comprando ficou parecido (cerca de 410–420).
- O volume de assinaturas novas por mês foi de 56 (2023) para 193 (jan–jun/24), 403 (jul–out/24) e 782 (nov–dez/24).

**A rajada e as reduções:**
- Só 5 das 89 reduções Enterprise estavam em rajada.
- Das 172 Enterprise encerradas, 31 estavam em rajada, quase todas viraram migração.
- Mesmo com janela de 30 dias, a proporção de reduções em rajada (44%) fica abaixo da média do Enterprise (53%).

---

## 7. O que isso significa (preliminar)

- **A perda Enterprise não vem de preço, de feature nova, de erros, de reclamações nem de um perfil específico de cliente.**
- **Parte da perda é efeito de contagem.** Cerca de US$ 147 mil por mês são compras extras desfeitas em poucos dias, que hoje entram como perda. É o mesmo problema das migrações, só que fora da janela de 7 dias.
- **A perda real (cerca de US$ 283 mil por mês) vem de contas grandes desligando um pacote Enterprise que tinham havia meses.** As contas continuam clientes e continuam Enterprise. O motivo não está nas tabelas; é preciso ouvir essas contas (lista na aba 7).
- **Algo mudou por volta de jul–ago/2024 no jeito de comprar.** As mesmas contas passaram a abrir assinaturas muito mais rápido, até uma por semana em dezembro. Vale checar com a empresa se houve campanha, mudança no processo de contratação ou na forma de registrar as assinaturas.

---

## 8. Limites

- A base é **fictícia** (gerada por computador).
- **Poucas reduções por período** (4 a 44), por isso muitos cruzamentos dão "poucos casos" ou "pode ser coincidência".
- As regras de "redução" (sem reposição em até 7 dias), de "compra extra desfeita" (até 30 dias de vida) e de "rajada" são escolhas da análise, não regras da empresa.
- As datas de uso e de tickets não são confiáveis. O uso foi ligado à data de início da assinatura, e os tickets foram usados só como tendência.
- As seções 4 a 6 vêm de consultas e ainda não estão em planilha.

---

## Arquivos desta pasta

| Arquivo | Conteúdo |
|---|---|
| `01_Enterprise_por_Periodo.xlsx` | Preço e seats, reduções no tempo, regressão de plano, features, reclamações, perfil e lista das 89 reduções |
| `scripts/01_enterprise_por_periodo.py` | Programa que gera a planilha a partir dos CSVs originais |
