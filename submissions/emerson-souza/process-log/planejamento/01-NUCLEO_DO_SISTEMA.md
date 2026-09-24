# NÚCLEO DO SISTEMA: a regra principal da construção

> **Regra de ouro (definida pelo Emerson):** o sistema funciona **SOZINHO** e **COOPERATIVO** ao mesmo tempo.
> Todo o resto do projeto obedece a esta regra. Antes de construir qualquer peça, a pergunta é: *"isso funciona sozinho E conversa com os outros módulos?"*

---

## 1. O que é "SOZINHO"

O usuário abre o programa (**painel gráfico no computador, como um software**), cria uma **sessão** e escolhe o tipo de análise:

| Escolha na sessão | Dados que entram | O que o sistema entrega | Equivale ao |
|---|---|---|---|
| **Análise de Churn** | dados de clientes, assinaturas, uso, tickets, cancelamentos | diagnóstico de churn completo | Desafio 001 |
| **Análise de Suporte** | tickets (métricas + texto) | diagnóstico operacional + automação com IA | Desafio 002 |
| **Análise de Leads / Pipeline** | contas, produtos, vendedores, oportunidades | lead scorer com explicação do score | Desafio 003 |
| **Análise de Mídia / Social** | posts, métricas, patrocínio, audiência | análise de performance + estratégia | Desafio 004 |

Cada módulo, **sozinho**, tem que entregar **100% do que o desafio correspondente pede** (foco: os **obrigatórios** de `07-requisitos_obrigatorios.md` primeiro), com os mesmos critérios de qualidade. Nada de módulo "meia-boca" só para completar.

---

## 2. O que é "COOPERATIVO" (a grande sacada)

O **resultado** de uma análise pode virar a **entrada** de outra ferramenta, **com os mesmos dados**.

**Exemplo-âncora (o do Emerson):**
1. Rodo a **Análise de Churn** com os dados da RavenStack.
2. A análise recomenda: *"estas contas precisam de um suporte melhor"*.
3. Com um clique, **essas mesmas contas e os tickets delas** vão para a **ferramenta de Suporte**, que roda o diagnóstico de suporte só nesse grupo (gargalos, tempo de resposta, escalonamento, satisfação) e propõe a automação para ele.

**Outros cruzamentos desejados:**
- Churn → Leads: *"vale a pena manter este cliente?"* (valor da conta × risco).
- Churn → Mídia: *"esse tipo de cliente pode receber propaganda/campanha?"*
- Suporte sozinho → outras ferramentas, quando os dados permitirem.

O mapa completo de cada cruzamento, com o que é possível e com que evidência, está em [`02-cruzamentos_entre_modulos.md`](02-cruzamentos_entre_modulos.md).

---

## 3. Como o núcleo funciona (conceito, sem código)

```
                 ┌──────────────── SESSÃO ────────────────┐
 dados ──► [1. Leitura + perfil]──►[2. De/Para para o     │
 (CSV,      detecta colunas,        "contrato" do módulo] │
 Excel,     tipos, chaves              │                  │
 JSON)                                 ▼                  │
                               [3. Módulo escolhido]      │
                               Churn | Suporte | Leads | Mídia
                                       │                  │
                               [4. Resultado + Ações]     │
                                       │                  │
                               [5. "Enviar para…"] ───────┼──► abre SUB-SESSÃO em outro módulo
                                                          │    com os dados/entidades filtrados
                 └────────────────────────────────────────┘
```

1. **Leitura + perfil:** lê qualquer arquivo e mostra o que tem (colunas, tipos, nulos, chaves).
2. **De/Para:** cada módulo tem um **contrato** (lista de campos obrigatórios e opcionais). O usuário (ou a sugestão automática) liga as colunas dele aos campos do contrato. Com isso, o sistema aceita **dados de qualquer empresa**, não só os do desafio.
3. **Módulo:** roda a análise completa daquele desafio.
4. **Resultado + ações:** números, gráficos, listas de contas/tickets/deals/posts e recomendações.
5. **Enviar para…:** cada resultado mostra **quais outros módulos conseguem usá-lo**. O botão cria uma **sub-sessão ligada à original**, com rastreio de onde veio.

### Sessões
- Cada análise é uma sessão salva (histórico, reabrir, rodar de novo, apagar).
- Sub-sessões cooperativas ficam **penduradas na sessão-mãe** (ex.: "Churn RavenStack → Suporte das contas em risco").

---

## 4. Regra de honestidade dos cruzamentos (inegociável)

O desafio cobra **"insights verificáveis"** e avisa que *"a IA disse, o candidato acreditou"* é fraco. Por isso, todo cruzamento mostra na tela o **nível de evidência**:

| Selo | Significado | Exemplo |
|---|---|---|
| 🟢 **Dado real ligado** | As tabelas compartilham uma chave de verdade | Churn → Suporte na RavenStack (`account_id` existe em contas e tickets) |
| 🟡 **Proxy** | Sinal indireto calculado a partir dos dados, explicado | Suporte (002) → "risco de churn por experiência de suporte" (não existe cancelamento nesses dados) |
| 🔵 **Hipótese configurável** | Ligação por regra de negócio que o usuário define e pode editar | Setor do CRM ↔ categoria de conteúdo do social |

**Nunca** ligar duas bases sem chave em comum e apresentar isso como fato. Os 4 datasets do desafio são de **4 empresas diferentes**, e o sistema tem que deixar isso claro.

---

## 5. Checklist de qualquer peça nova

- [ ] Funciona **sozinha** com os dados do desafio correspondente?
- [ ] Funciona com **dados de outra empresa** (via De/Para)?
- [ ] O resultado declara **quem pode consumi-lo** (Enviar para…)?
- [ ] Todo cruzamento mostra o **selo de evidência**?
- [ ] Atende os **critérios de qualidade** do desafio (ver `desafios/`)?
- [ ] Foi **testada com os dados reais**, não com 3 exemplos?
- [ ] Ficou **registrada no process log**?
