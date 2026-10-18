# Escopo: lista diária de acompanhamento Enterprise para CS

*Proposta de escopo, sem programação. Baseada no relatório de diagnóstico (`ENTREGA/relatorio.md`) e nos números da tabela de assinaturas.*

---

## 1. Objetivo

Toda manhã, o time de CS recebe uma lista curta e priorizada de **assinaturas Enterprise nos primeiros 30 dias**. Assim consegue agir **antes** de um encerramento e registrar o que ouviu do cliente.

A lista tem dois efeitos:
- **Evitar perda:** confirmar que a compra foi certa e que o cliente está usando o que comprou.
- **Evitar falso churn:** impedir compras duplicadas ou por engano, que hoje viram "compra extra desfeita" e inflam o churn.

## 2. O que os dados dizem sobre esse risco

Precisamos disso para dimensionar a automação.

| Assinaturas Enterprise iniciadas entre jul e nov/2024 (789) | % |
|---|---|
| Encerradas em até 30 dias | 3,5% |
| … das quais troca (nova assinatura em até 7 dias) | 2,1% |
| … das quais perda ou compra desfeita | 1,4% |

- **Volume é o maior desafio.** Em dez/2024 entraram cerca de **10 Enterprise novas por dia**. Em 31/12/2024 havia **317 assinaturas Enterprise** nos primeiros 30 dias, de 186 contas, somando US$ 1,6 milhão de MRR. Uma lista com "todas" seria grande demais para agir. Por isso a lista diária mostra **o que entrou ou mudou**, não o estoque inteiro.
- **O risco nos 30 primeiros dias é real, mas pequeno em quantidade de Enterprise.** O valor de cada caso é alto: em média cerca de US$ 5 mil por mês por assinatura.
- **A maior parte da perda Enterprise vem de pacotes antigos**, desligados meses depois da compra. A lista dos primeiros 30 dias resolve uma parte do problema. A outra parte entra na fase 2 (seção 10).

## 3. Quem usa e quando

- **Quem:** o time de CS, com o responsável de cada conta Enterprise.
- **Quando:** todos os dias úteis às 7h, com os dados do dia anterior.
- **Onde:** um e-mail ou mensagem com a lista e um link para a planilha ou painel com o histórico. O canal é decisão do time.

## 4. Fonte de dados

- **Usar:**
  - a tabela de **assinaturas** (início, fim, plano, licenças, valor, cobrança, trial);
  - a tabela de **contas** (cadastro, indústria, país, canal).
- **Não usar por enquanto:** datas de uso, datas de tickets, eventos de churn e satisfação. O relatório mostrou que hoje esses dados não são confiáveis. Eles entram depois da ação 6 do relatório (base coerente).

## 5. Quem entra na lista

Toda assinatura **Enterprise** com **0 a 30 dias de vida** entra na lista em três momentos:

| Momento | Quando | Por quê |
|---|---|---|
| **Entrada** | D+1 (dia seguinte à compra) | Confirmar a compra e evitar duplicidade ou erro |
| **Checkpoint** | D+20 | Saber se está em uso e se vai continuar, antes do fim do 1º mês |
| **Alerta imediato** | Quando a assinatura for encerrada dentro dos 30 dias | Registrar o motivo em até 48h |

Volume esperado: cerca de 10 entradas, 10 checkpoints e alguns alertas por dia.

## 6. Sinais de atenção e prioridade

Cada linha recebe sinais calculados das próprias assinaturas:

| Sinal | Regra | O que indica |
|---|---|---|
| **Possível duplicidade** | A conta já tem outra Enterprise ativa com **as mesmas licenças** | Compra repetida por engano |
| **Já tinha Enterprise** | A conta já tinha outra Enterprise ativa (tamanho diferente) | Compra a mais que pode ser desfeita |
| **Compra em rajada** | 3 ou mais assinaturas da conta em 7 dias | Processo de compra confuso |
| **Conta nova** | Conta com menos de 30 dias de cadastro | Precisa de onboarding |
| **Anual** | Cobrança anual | Cancelamento antecipado custa caro; confirmar contrato |
| **Trial** | Assinatura de teste (US$ 0) | Converter em pago |
| **Teste no lugar de pago** | A conta abriu uma Enterprise trial com o mesmo tamanho de uma Enterprise paga, até 30 dias antes ou depois | Pode estar trocando o pago pelo teste (caso da conta A-8ae05d) |

**Ordem da lista:**
1. Alertas de encerramento.
2. Assinaturas com o sinal "possível duplicidade" ou "teste no lugar de pago".
3. Valor mensal da assinatura, do maior para o menor.

Os sinais são **apoio à conversa, não previsão**. Na análise de jul–nov/2024 eles separam pouco quem encerra de quem fica. A rajada, por exemplo, tem 6,5% de encerramento em 30 dias contra 3,1% sem rajada, quase sempre por troca. Eles servem para orientar o tipo de contato.

## 7. Colunas da lista

- **Identificação:** conta, nome, indústria, país, canal, responsável de CS.
- **Assinatura:** código, licenças, valor mensal, cobrança, data de início, dias de vida, momento (entrada, checkpoint ou alerta).
- **Conta:** outras assinaturas ativas, valor total mensal da conta, % que esta assinatura representa da conta.
- **Sinais:** os sinais da seção 6 (Sim/Não) e a prioridade.
- **Histórico:** último contato e resultado (vem do registro do CS, seção 8).

## 8. O que o CS faz e o que registra

**Ação por momento:**

| Momento | Ação |
|---|---|
| **Entrada com duplicidade ou rajada** | Ligar ou escrever no mesmo dia para confirmar se a compra foi intencional. Se foi erro, corrigir a compra e marcar como "erro de compra". Isso não deve virar churn |
| **Entrada normal** | Boas-vindas e agendamento de onboarding das licenças |
| **Checkpoint D+20** | Verificar adoção (licenças em uso) e intenção de manter |
| **Alerta de encerramento** | Contato em até 48h para entender o motivo |

**Registro obrigatório de cada contato:**
- **Feito?:** Sim/Não.
- **Resultado:** mantém, reduz, cancela, foi erro de compra ou troca de plano.
- **Motivo:** de uma lista fechada, **nunca vazio e nunca "unknown"**. Opções: preço, orçamento cortado, funcionalidade que faltou (qual?), problema técnico, atendimento, foi para concorrente (qual?), projeto encerrado, compra duplicada ou por engano, troca de plano.
- **Comentário livre.**

Esse registro é o **feedback contínuo**. Ele alimenta a ação 5 do relatório (motivo claro) e é o que finalmente vai explicar por que contas Enterprise reduzem.

## 9. Como medir se está funcionando

Acompanhar mês a mês, comparando com o 2º semestre de 2024:

| Indicador | Ponto de partida |
|---|---|
| Enterprise encerradas em até 30 dias | 3,5% |
| Compras extras desfeitas Enterprise (valor mensal) | US$ 168 mil só no 4º tri/24 (todos os planos) |
| % de linhas da lista com contato feito em até 2 dias úteis | Meta: 90% |
| % de encerramentos com motivo registrado (sem vazio e sem "unknown") | Hoje 63% dos eventos têm algum motivo útil |
| Valor mensal mantido após contato (assinaturas que o cliente pensava encerrar) | Novo |

## 10. Fora do escopo agora (fase 2)

- **Pacotes Enterprise antigos.** É onde está a maior parte da perda real: por exemplo, a lista das 10 contas do relatório e as 4 prioritárias. A mesma automação pode ganhar um segundo bloco: contas Enterprise que reduziram nos últimos 90 dias e contratos anuais perto da renovação.
- **Modelo preditivo.** Só depois que uso, tickets e motivo de churn forem confiáveis (ações 5 e 6 do relatório).
- **Planos Basic e Pro.** O mesmo desenho vale, mas com outro limite de valor para não inundar o CS.

## 11. Dependências e riscos

- **Extração diária:** precisa de uma extração diária confiável da tabela de assinaturas, com contas e responsável de CS. Hoje a análise usou um retrato até 31/12/2024.
- **Ainda sem aviso prévio:** o encerramento só aparece quando a assinatura já terminou. Não existe na base um "pedido de cancelamento" com antecedência. Se o sistema de cobrança tiver essa data (aviso prévio, cancelamento agendado), ela deve entrar e vira o alerta mais valioso.
- **Excesso de alertas:** se a lista crescer demais, o time para de usar. Começar com Enterprise acima de um valor mínimo (a definir com CS) e ajustar.
