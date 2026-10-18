# MEMÓRIA DO PROJETO: Desafio G4 · data-001 · Diagnóstico de churn da RavenStack

*Arquivo para retomar o trabalho sem perder o contexto. Última atualização: 17/10/2026 (sábado, noite), escrita com Claude (IA). Inclui o Enterprise (DADOS_ENTERPRISE) e o estudo uso × eventos × tickets (DADOS_FEATURE_EVENTS_11_12_2024).*

---

## 0. Regras de trabalho (do usuário). Valem sempre.

1. **NUNCA criar nem editar nada sem autorização explícita.**
2. **NUNCA rodar nenhum comando git sem autorização.** `ai-master-challenge` é um repositório git; não mexer nele.
3. **NUNCA alterar os dados originais** (`G4_DESAFIO\dados\*.csv`) nem as planilhas de `DADOS_ORIGINAIS`. Verificações e análises vão sempre em **planilhas apartadas**.
4. Trabalhar **passo a passo**: propor o próximo passo e esperar o "pode seguir".
5. Textos para o usuário e para o CEO: **linguagem simples, sem termos técnicos/estatísticos**. Em vez de "p-valor", usar "diferença confiável?" (Sim / Não, pode ser coincidência / Poucos casos para concluir).
6. Quando o usuário pedir, analisar **primeiro em quantidade** e só depois trazer **US$**.
7. Excel com **fórmulas** (verificáveis), não números colados. Sempre recalcular, conferir os números e testar o script no computador do usuário.
8. Os diagnósticos em .md **ainda não são a resposta final** do desafio.

---

## 1. O desafio

- As instruções estão em `ai-master-challenge\challenges\data-001-churn\README.md`.
- O CEO quer saber:
  1. a causa raiz do churn;
  2. os segmentos em risco, com contas específicas;
  3. ações priorizadas, com impacto.
- O desafio pede cruzar as 5 tabelas, distinguir correlação de causalidade, ter números verificáveis e um texto legível para um CEO.
- Também exige um *process log* do uso de IA. Os scripts salvos servem de evidência.
- Os dados (base fictícia, Kaggle "RavenStack") estão em `G4_DESAFIO\dados`: accounts (500), subscriptions (5.000), feature_usage (25.000), support_tickets (2.000), churn_events (600).

---

## 2. Estrutura de pastas (`G4_DESAFIO\analise`)

```
analise\
├─ MEMORIA_DO_PROJETO.md               ← este arquivo
├─ DADOS_ORIGINAIS\                    ← primeira visão "como os dados vêm". NÃO ALTERAR.
│   ├─ RavenStack_Analise_Churn.xlsx   (painéis mês a mês, segmentos, features, comparativo; filtros)
│   └─ scripts\ 01_bases · 02_excel · 03_dados_dashboard · 04_diagnostico_consistencia (+ LEIA-ME.txt)
├─ DADOS_RECONCILIA\                   ← qualidade da base e escolha da fonte confiável
│   ├─ 01_Evidencias_Consistencia.xlsx (28 regras testadas linha a linha; exemplos)
│   ├─ 02_Triangulacao.xlsx            (22 fatores × 3 definições de churn; tempo)
│   ├─ 03_Coortes_2024S2.xlsx          (o que mudou no 2º sem/24; dezembro; subconjunto limpo)
│   ├─ DIAGNOSTICO_RECONCILIACAO.md
│   └─ scripts\ 01..03
├─ DADOS_2024_NOV_DEZ\                 ← foco no churn de nov/dez/24 (e mês a mês)
│   ├─ 01_Churn_NovDez_Padroes.xlsx            (perfil → reclamação → feature → cancelamento rápido)
│   ├─ 02_Cobranca_Plano_Pais_Seats.xlsx       (hipóteses de seats e anual × plano × país)
│   ├─ 03_Casos_21_Contas.xlsx                 (caso a caso; linha do tempo)
│   ├─ 04_Tipos_de_Cancelamento.xlsx           (migração / redução / saída; janelas 3-7-14 dias)
│   ├─ 05_Upgrade_Downgrade_e_Rajadas.xlsx     (flags × plano/seats; compras em rajada)
│   ├─ 06_Valores_por_Tipo.xlsx                (US$ nov/dez: bruto × perda real)
│   ├─ 07_Grafico_Mensal_Clientes.xlsx         (jan/23–dez/24: ingressantes, normais, migrados, redução, cancelados; qtd e US$; REFERÊNCIA de valores)
│   ├─ 08_Plano_Features_Reducao_Enterprise.xlsx (plano × features; Enterprise por segmento)
│   ├─ DIAGNOSTICO_NOV_DEZ_2024.md
│   └─ scripts\ 01..08
├─ DADOS_ENTERPRISE\                   ← Enterprise em 4 períodos (2023 · jan–jun/24 · jul–out/24 · nov–dez/24)
│   ├─ 01_Enterprise_por_Periodo.xlsx  (preço/seats, reduções no tempo, regressão de plano, features, reclamações, perfil, lista das 89 reduções)
│   ├─ DIAGNOSTICO_ENTERPRISE.md       (inclui as consultas das 79 reduções, gêmeas, grupos A/B/C e janelas de rajada — essas partes NÃO estão em planilha)
│   └─ scripts\ 01_enterprise_por_periodo.py
├─ DADOS_FEATURE_EVENTS_11_12_2024\    ← parte de USO + EVENTOS (não das assinaturas); tickets churneados × não churneados
│   ├─ 01_Uso_Eventos_Tickets.xlsx     (uso nov/dez; antes/depois do evento; motivo × uso; prova da data de uso; perfil base inteira; features por grupo; tickets por grupo)
│   ├─ DIAGNOSTICO_FEATURE_EVENTS.md
│   └─ scripts\ 01_uso_eventos_tickets.py
├─ DADOS_CONSOLIDA_V1\                 ← consolidação: contas prioritárias, perda real por trimestre, ritmo de compra, evento × cancelamento real
│   ├─ 01_Contas_Enterprise_Prioritarias.xlsx · 02_Perda_Real_por_Trimestre.xlsx · 03_Ritmo_de_Compra_Segmentos.xlsx · 04_Eventos_x_Cancelamento_Real.xlsx
│   ├─ DIAGNOSTICO_CONSOLIDA_V1.md
│   └─ scripts\ comum.py (regras compartilhadas) + 01..04
└─ ENTREGA\                            ← relatório final sugerido (relatorio.md)
```

- **Dashboard interativo** com a visão original, publicado como artifact privado "RavenStack Churn": https://claude.ai/artifact/87CYnz8u7bSRxWfBzc73jV
- **Scripts:** cada um regenera sua planilha a partir dos CSVs originais. Rodar com `python <script>.py`, que acha a pasta `dados` sozinho; requer pandas e openpyxl. No PC do usuário há Python 3.10, pandas 2.3, openpyxl 3.1 e **não há scipy** (os testes foram escritos sem ele).
- Os scripts de `DADOS_ORIGINAIS` foram ajustados para o novo caminho (`parents[3]`). Rodar `02_excel.py` **regrava** o Excel original.

---

## 3. Qualidade da base (`DADOS_RECONCILIA`)

- **Assinaturas (subscriptions):** a ÚNICA tabela coerente. 100% nas regras:
  - **MRR = seats × preço fixo do plano** (Basic US$ 19, Pro US$ 49, Enterprise US$ 199 por seat);
  - ARR = 12 × MRR;
  - churn_flag = end_date preenchido;
  - trial = MRR zero.
  - Exceção: 23 assinaturas com upgrade e downgrade ao mesmo tempo.
- **Accounts:**
  - churn_flag bate com os eventos de churn ao nível do acaso;
  - nenhuma das 110 contas marcadas está sem assinatura ativa;
  - plan_tier/seats "iniciais" não batem com a 1ª assinatura.
- **Churn_events:**
  - 9 em 10 eventos acontecem com a conta ainda ativa;
  - só 8% coincidem com o fim de uma assinatura;
  - motivo × comentário sem relação;
  - reativação e preceding_* não batem.
- **Feature_usage:** 77% dos registros antes do início da assinatura (53% antes do cadastro). Quantidades servem; **datas não**.
  - Reforço (DADOS_FEATURE_EVENTS): **~1.000 registros por mês o tempo todo** (jan/23–dez/24) enquanto as assinaturas ativas vão de 3 a 4.707; **toda assinatura tem ~5 registros**, não importa quando começou nem quanto durou. As datas parecem sorteadas → filtrar uso por mês é amostra aleatória. "O uso cresceu" (time de produto) não se sustenta nesta tabela.
  - Uso é registrado por assinatura; para ligar a eventos/contas é preciso a tabela de assinaturas só como mapa assinatura → conta.
- **Support_tickets:**
  - os dados internos batem;
  - 54% dos tickets são anteriores ao cadastro da conta;
  - **satisfação só tem notas 3, 4 e 5** (nenhum 1 ou 2), com cerca de 41% sem nota;
  - **não há assunto, categoria nem texto da reclamação** (só prioridade, tempos, escalação, nota): não dá para saber O QUE foi reclamado.
- **Marcações de upgrade/downgrade:** não refletem mudança real de plano ou seats (59% contra 54% sem marcação); 73 marcações na 1ª assinatura da conta.
- **is_beta_feature:** cerca de 10% dos registros de **todas** as features (aleatório). Não identifica uma "feature nova".
- **Nenhuma conta termina 2024 sem assinatura ativa.**
- **Decisão:** a tabela de **assinaturas** é a base. Eventos e churn_flag só servem para confirmação.

---

## 4. Definições usadas

- **Rápida:** assinatura encerrada com **menos de 30 dias** de vida. **Conta nova:** menos de 30 dias de cadastro.
- **Tipo de encerramento** (janela de **7 dias**, olhando a mesma conta):
  - **Saída do cliente**: ficou sem nenhuma assinatura ativa e não abriu outra em até 7 dias;
  - **Migração (troca/ajuste)**: abriu outra assinatura até 7 dias antes ou depois. **Não é perda**;
  - **Redução**: seguiu cliente, sem compra nova perto. Perda de receita.
- **MRR reposto:** MRR da assinatura nova mais próxima de cada migração. Cada nova é contada **uma vez só**, em ordem de data, no período todo.
- **Perda real** = redução + saídas + (MRR encerrado em migrações − MRR reposto).
- **Rajada:** 3 ou mais assinaturas da mesma conta (qualquer plano, inclusive trial) iniciadas dentro de 7 dias corridos (dia da compra + 6), sem olhar o mês.
  - Testadas janelas de 7, 10, 14, 20, 21, 28 e 30 dias: não há ponto de corte natural. **10 dias** é a que melhor separa antes/depois (2023: 3% × nov–dez/24: 42% das Enterprise novas). Usuário decidiu NÃO refazer a planilha 05 com 10 dias.
- **Redução Enterprise "seguiu com outra Enterprise" / "ficou só com Basic/Pro" / "ficou sem assinatura":** outras assinaturas ativas da conta no dia do fim.
- **Gêmea:** outra Enterprise ativa da mesma conta com exatamente os mesmos seats.
- **Grupos das reduções Enterprise (consulta, não está em planilha):**
  - **A. Compra extra desfeita:** a conta já tinha Enterprise mais antiga e cancelou a nova com até 30 dias de vida;
  - **B.** cancelou um pacote antigo tendo Enterprise mais nova na conta;
  - **C.** cancelou sem ter Enterprise mais nova.
- **Grupos de contas (DADOS_FEATURE_EVENTS):** 1 = evento de churn em nov/dez/24 (141); 2 = evento só em outro mês (211); 3 = nunca teve evento, "não churneado" (148).
- **"Diferença confiável?":** teste exato (Fisher) para proporções; para comparar duas taxas por exposição (ex.: reduções por assinatura-mês), teste exato binomial condicional; para médias, embaralhamento dos rótulos (4.000 vezes). p < 0,05 = "Sim". Com menos de 10 casos: "Poucos casos para concluir".
- **Taxa por período:** "a cada 100 assinaturas ativas por mês" (assinaturas-mês), porque os períodos têm tamanhos diferentes.

---

## 5. Principais achados até agora

1. **Fatores fixos:** nenhum dos 22 testados (segmento, plano, uso, suporte…) explica o churn de forma robusta nas 3 definições.
2. **O sinal é de tempo:** os primeiros 30 dias concentram o risco (cerca de 5×). O 2º semestre de 2024 piora: o cancelamento em 30 dias vai de cerca de 0,7% para 4,2% **em todos os perfis**. Dezembro é atípico, com 61 encerramentos entre 29 e 31/12 a confirmar com a área.
3. **Satisfação, tempos de atendimento, uso e erros ficam estáveis** enquanto o churn sobe. Por isso o CS e o produto "não veem" o problema.
4. **Nov/dez:**
   - 266 assinaturas encerradas: 156 migrações, 110 reduções, **0 saídas**;
   - o cancelamento rápido é silencioso (87% sem ticket antes) e ligado a **compras em rajada** de contas novas (81% rápidas e 90% migração dentro da rajada);
   - as 21 contas "limpas" seguem todas clientes.
5. **Em US$:**

   | | Nov/dez | 24 meses |
   |---|---|---|
   | "Churn" de hoje | US$ 761.755 | US$ 1.179.139 |
   | Perda real | ≈ US$ 482 mil | US$ 718.359 |
   | … redução | US$ 339.472 | US$ 580.593 |
   | … cancelamento real | — | US$ 23.406 (4 casos, que voltaram) |
   | … saldo das migrações | — | US$ 114.360 |
   | Reposto nas migrações | — | US$ 460.780 (só US$ 40 mil já estão em "Ingressantes") |

6. **Enterprise (planilha 08 de DADOS_2024_NOV_DEZ + DADOS_ENTERPRISE):**
   - responde por **US$ 458 mil dos US$ 581 mil de redução (78%)** em 24 meses;
   - **sem aumento de preço**: US$ 199/seat em todas as assinaturas e períodos (mensal ou anual); só os seats médios variam (27–32), sem tendência;
   - reduções a cada 100 assinaturas por mês: 0,54 (2023) · 0,85 · 0,66 · **1,66 (nov–dez/24)**; a alta é de todos os planos (Pro também "Sim"); Enterprise nunca difere de Basic+Pro;
   - perda por mês: US$ 2 mil · 10 mil · 21 mil · **142 mil**; nov–dez ≈ 7× jul–out (dobro de reduções/mês e assinaturas maiores, ≈ US$ 6,5 mil × 3,8 mil); 33 das 44 em dezembro, 12 entre 29 e 31/12;
   - **não regrediram de plano**: 79 das 89 seguiram com outra Enterprise (11 eram trial); 10 ficaram só com Basic/Pro (US$ 27 mil); 0 ficaram sem assinatura;
   - **cada assinatura tem seats fixos**: "redução" = desligar um pacote inteiro. Típico: 25 seats, ≈ US$ 5 mil/mês, ≈ 1/4 do valor da conta; 8 contas perderam mais da metade;
   - **as 79 (68 pagas, US$ 431 mil/mês):**

     | Grupo | Com gêmea | Sem gêmea | Total | US$/mês | Leitura |
     |---|---|---|---|---|---|
     | A. Compra extra desfeita (≤ 30 dias) | 6 | 15 | 21 | 147 mil | quase não é perda; 13 das 15 sem gêmea em nov–dez/24 |
     | B. Pacote antigo desligado, havendo Enterprise mais nova | 14 | 26 | 40 | 226 mil | redução real, com dúvida |
     | C. Sem Enterprise mais nova | 9 | 9 | 18 | 58 mil | redução real |

     - tempo da gêmea/última Enterprise até o cancelamento: 9 a 379 dias (típico 64–77); **sem prazo fixo**;
     - referência da base: 78% das Enterprise ativas têm Enterprise mais nova na conta e 48% têm gêmea → ter pacote mais novo é normal, **não** prova de troca;
     - exemplos: A-d4e0d4 (117 seats duplicada e cancelada em 3 dias, US$ 23 mil), A-ce550d (109 seats aberta e cancelada em 31/12), A-e1b9cd (40+40 seats; cancelou uma, 25% da conta);
   - features: as 40 existem desde 2023; erro ≈ 30% estável; feature_10 e feature_24 com mais erro depois de 2023 (sinal fraco);
   - tickets estáveis (urgentes um pouco maiores em nov–dez: 30% × ~23%); quem reduz não abre mais tickets;
   - perfil: nenhum segmento confiável; EUA 48/89 reduções e US$ 238 mil; único "Sim" fraco: França em nov–dez (5 casos).
7. **Rajada (consultas):** 262 Enterprise em rajada (116 contas), 1ª em 05/06/2023; vira padrão em ago–set/24 e explode em dez/24 (41%). Só 5 das 89 reduções Enterprise estavam em rajada. O que mudou de fato foi o **ritmo de compra**: intervalo típico entre compras da mesma conta 30 dias (2023) → 17 (jul–out/24) → **8 (nov–dez/24)**; assinaturas novas/mês 56 → 193 → 403 → 782 com ~410 contas comprando. Pergunta em aberto para a empresa: o que mudou em jul–ago/24 (campanha, processo de contratação, forma de registrar)?
8. **Uso × eventos × tickets (DADOS_FEATURE_EVENTS_11_12_2024):**
   - em nov/dez, contas com e sem evento usam igual (registros, features, erro ≈ 29%);
   - o uso não muda em volta do evento: mesmo ritmo antes e depois; **61% dos eventos têm uso depois do "churn"**; só 18% coincidem (±7 dias) com fim de assinatura;
   - motivo registrado não muda uso/erro e não acompanha o comentário do cliente;
   - base inteira, 3 grupos: perfil de uso idêntico; por feature, só feature_10 (mais usada pelo grupo 1: 75% × 62%) e feature_29 (menos: 61% × 74%) — **feature_10 é sinal fraco que se repete** (também no Enterprise);
   - tickets: mesma quantidade, tempos e satisfação; única diferença confiável: mais "alta" (28% × 23%) e menos "urgente" (23% × 28%) no grupo 1, soma igual (~51%) → muda o rótulo, não a gravidade.
9. **Consolidação V1 (DADOS_CONSOLIDA_V1):**
   - nova classificação de cada assinatura encerrada: Troca (±7 dias) · **Compra extra desfeita** (≤ 30 dias, havia outra mais antiga do MESMO PLANO ativa — vale para todos os planos) · Redução real · Saída;
   - **perda real 24 meses = US$ 537.914 (46% do "churn" de hoje, US$ 1.179.139)**; 4º tri/24: US$ 331.314 de US$ 871.812 (38%); perda real sobre o MRR do início do trimestre: 5,5% no 4º tri/24 (o "churn" de hoje daria 14,4%);
   - 8 contas Enterprise com > 50% de perda: 4 não recuperaram (A-13466a, A-f44180, A-8ae05d, A-69fad4); 3 recuperaram; 1 compra desfeita;
   - ritmo de compra: todos os segmentos 1,7–3,2×; EUA, Cybersecurity e orgânico ganharam participação; cadastros +26% × compras +174%; piora simultânea em todos; rajada maior no orgânico e DevTools; Alemanha exceção;
   - datas de tickets/uso aleatórias, irrecuperáveis; evento de churn perto de um fim de assinatura = acaso (7,8% × 7,6%); proposta de churn oficial pela tabela de assinaturas.
10. **Pendência menor:** a planilha 06 mostra perda real de nov/dez de US$ 474 mil, contra US$ 482 mil na 07 (diferença de pareamento). A 07 é a referência; foi oferecido alinhar a 06.

---

## 6. ENTERPRISE — pedido original (CONCLUÍDO em 17/10/2026; resultado na seção 5, itens 6 e 7)

**Criar `analise\DADOS_ENTERPRISE`** e investigar o **Enterprise como centro**, por ser onde está a maior perda em valor (US$ 458 mil dos US$ 580.593 de redução, 78%).

**Separar a análise em 4 períodos:**
1. 2023;
2. jan–jun/2024;
3. jul–out/2024;
4. nov–dez/2024.

**Perguntas para cada período:**
- **Preço:** houve aumento? Estimar o preço por seat: MRR ÷ seats, ou ARR ÷ 12 ÷ seats para anual. Também o preço médio por assinatura e por conta.
- **Seats:** a quantidade por assinatura e por conta mudou?
- **Features:** alguma feature passou a aparecer no Enterprise só a partir de um período, como se tivesse sido "lançada" ali, e coincide com as reduções?
- **Reclamações:** volume, prioridade, escalação e satisfação por período.
- **Perfil de quem reduziu:** indústria, canal e país que mais participaram das reduções em cada período.

**Alertas já conhecidos para esse passo** (dizer ao usuário antes de começar):
- **Preço por seat:** nesta base ele é **fixo** em todas as assinaturas (Enterprise US$ 199, teste S03 = 100%), e ARR = 12 × MRR. Portanto a conta "valor ÷ seats" deve mostrar **nenhum aumento de preço**. Se houver mudança de valor, virá de seats ou do mix de planos, não do preço.
- **Features no tempo:** as datas de uso não são confiáveis. Para ver se uma feature "surgiu" num período, usar a **data de início da assinatura** a que o uso está ligado, não a data do uso. Deixar isso explícito.
- **Feature nova:** is_beta_feature é aleatória e não marca uma feature nova.
- **Tickets por período:** usar a data do ticket com cautela (54% são anteriores ao cadastro da conta).
- **Períodos de tamanhos diferentes:** comparar sempre "a cada 100 assinaturas" ou "por mês", não totais.
- **Base de comparação:** reduções Enterprise contra Enterprise que não reduziram no mesmo período; e Enterprise contra Basic/Pro.

**Entregáveis sugeridos:** uma planilha por pergunta (ou uma com abas por período), com fórmulas, "diferença confiável?" e LEIA-ME em linguagem simples, mais um diagnóstico curto em .md. Seguir as mesmas regras da seção 0.

---

## 7. Próximo passo

- **Em andamento:** relatório final sugerido em `analise\ENTREGA\relatorio.md` (foco em Diagnóstico + Formato do README; usuário pediu para NÃO sugerir adicionais ainda — diferencial, process log etc. ficam para depois).
- Opções antigas, sem compromisso:
  - colocar em planilha (DADOS_ENTERPRISE) as consultas das 79 reduções (grupos A/B/C, gêmeas) e das janelas de rajada — só com autorização;
  - alinhar a planilha 06 com a 07.

## 8. Depois (ideias registradas, sem compromisso)

- Juntar tudo numa resposta final para o CEO: causa raiz, segmentos e contas em risco, ações priorizadas com impacto em US$, e process log.
- Recomendações que já aparecem:
  - corrigir a régua de churn (separar migração, redução e saída);
  - revisar o processo de contratação (rajadas e cancelamentos em poucos dias, inclusive anuais);
  - acompanhar os primeiros 30 dias das assinaturas novas;
  - proteger contas Enterprise antes de reduções (lista das 89 na aba 7 de DADOS_ENTERPRISE; priorizar as 8 que perderam mais da metade);
  - não contar compra extra desfeita em até 30 dias como perda (≈ US$ 147 mil/mês das reduções Enterprise);
  - investigar com a empresa a mudança no ritmo de compra a partir de jul–ago/24;
  - registrar assunto dos tickets, data real de uso e amarrar o evento de churn ao cancelamento real;
  - consertar a pesquisa de satisfação (escala sem notas baixas, 41% sem resposta);
  - confirmar o pico de 29–31/12.
