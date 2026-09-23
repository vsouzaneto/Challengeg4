# Causa raiz e solução: o problema é gente, ferramenta ou processo?

> Continuação do [DIAGNOSTICO.md](DIAGNOSTICO.md). Toda afirmação aqui é verificada no [HARNESS.md](HARNESS.md).
> A solução está em [`solucao/`](solucao/) e roda sobre os dados reais.

---

## Veredito em uma frase

**Não é problema de gente trabalhando mal.** Nenhuma falha tem assinatura de erro humano. As falhas são de **ferramenta**: o sistema grava valores errados. Somam-se falhas de **processo** (não existe regra para prioridade, pendência nem pesquisa) e uma de **governança**: ninguém é dono do dado, e por isso ninguém percebeu que 49% dos tempos eram impossíveis.

| Origem | Problemas | Quais |
|---|---|---|
| 👤 **Humano (agente)** | **0** | Nenhuma evidência |
| 🔧 **Ferramenta** | 5 | P1 relógio · P2 triagem · P3 roteamento · P7 texto · P8 identidade |
| 📋 **Processo** | 4 | P3 prioridade livre · P5 pendentes · P6 pesquisa CSAT · P7 resolução livre |
| 🏛️ **Governança (humano, gestão)** | 1 | P9 ninguém monitora o dado |
| ❓ **Indeterminado** | 1 | P4: faltam pessoas ou falta roteamento? Só dá para saber depois de corrigir P1 |

---

## Como separei humano de ferramenta

Erro humano e erro de sistema deixam **rastros diferentes** no dado. Para cada falha, escrevi antes de olhar o que veria **se** a causa fosse humana, e depois medi (harness H8):

| Sinal | Se fosse humano, veríamos… | Observado | Atribuição |
|---|---|---|---|
| Segundos nos horários | Horário digitado → segundos = :00 | 1,8% com :00 (acaso: 1,7%); segundos uniformes (p = 0,97) | 🔧 Gerado por sistema |
| Resolução × 1ª resposta | Dois eventos independentes → segundos diferentes | **100%** dos pares com os mesmos segundos: a resolução é **calculada** a partir da 1ª resposta (± N minutos) | 🔧 Campo calculado |
| Troca AM/PM | Erro clássico de digitação → pico em ±12 h | 3,9% em ±12 h (acaso: 4,2%) | ✖ Não é digitação |
| Hora do dia | Operação humana → vale de madrugada | Madrugada ≈ horário comercial | 🔧 Sem expediente (sinal fraco) |
| Placeholders | Agente não escreve `{chaves}` | 100% com `{product_purchased}` | 🔧 Template quebrado |
| Texto da resolução | Agente usa vocabulário de suporte; o lixo de quem só quer fechar o ticket se repete ("ok", ".") | 100% únicos; vocabulário de suporte em 0,8% das palavras (18,7% nas descrições) | 🔧 Texto gerado |
| Triagem por canal | Equipes diferentes → acertos diferentes, **acima** do acaso | Acerto de 17,0% a 19,8% nos 4 canais, igual ao acaso de 18,3% (p = 0,70) | ✖ Não é julgamento humano |
| Colunas desalinhadas | Join deslocado → pico de acerto em algum deslocamento | Nenhum pico entre −30 e +30 | ✖ Descartado |
| Prioridade × urgência | Agente com pressa ainda sobe a prioridade do "urgente!" | Urgentes em Critical/High: 52,5% (acaso ≈ 50%) | 🔧 Prioridade não usa o conteúdo |
| Máquina de estados | Sistema quebrado → status incoerentes | **100% coerente** | ✅ O workflow funciona |

**Leitura:** o sistema *sabe* em que estado cada ticket está (a última linha prova), mas grava **valores** errados nos campos. Isso é bom sinal: o conserto é no mapeamento, na integração e na configuração, não em trocar a ferramenta nem as pessoas.

---

## Os 9 problemas: causa, 3 opções e a escolha

Formato: **causa → evidência → opções A/B/C → escolha e por quê → dono → como verificar**.

### P1. O relógio não existe · 🔧 Ferramenta (export/ETL)

Não existe horário de abertura. A resolução é calculada como 1ª resposta ± minutos. Todos os horários caem numa janela de 27 h (carimbo de exportação).

| | Opção | A favor | Contra |
|---|---|---|---|
| A ✅ | **Corrigir o export: puxar os horários do log de eventos do sistema** | O sistema já registra as transições (a máquina de estados é coerente); o conserto é no ETL | Se o log não existir na origem, não resolve o histórico |
| B | Reconstruir os tempos a partir do histórico de e-mails e chats | Recupera o passado | Caro, lento, com cobertura parcial |
| C | Trocar a ferramenta de helpdesk | Resolve de vez | Não há evidência de que a ferramenta seja o problema; custo e risco altos |

**Escolha: A.** A causa está no caminho do dado, não na origem: o workflow grava estados corretamente. **B** só se justifica se a TI confirmar que o log não existe (vale um dia de checagem). **C** trata um sintoma com a solução mais cara.
**Dono:** TI/ETL. **Verificação:** regras R01 a R04 do [Quality Gate](solucao/quality_gate.py).

### P2. A triagem é um sorteio · 🔧 Ferramenta (+ processo)

Tipo, assunto e prioridade não têm relação com o texto: o acerto é de 18,31% contra 18,32% do acaso. O campo é preenchido sem olhar o conteúdo (valor padrão, menu genérico ou mapeamento de integração).

| | Opção | A favor | Contra |
|---|---|---|---|
| A | Regras de preenchimento + treinamento | Barato | Depende de disciplina manual, e o problema nem é humano |
| B ✅ | **IA na entrada com limiar de confiança; humano abaixo do limiar** | Medido em dado real: **73% dos tickets classificados sozinha, com 95,1% de acerto** | Exige construir, monitorar e recalibrar |
| C | Formulário estruturado para o cliente | Simples | O cliente escolhe errado e não funciona em telefone nem redes sociais |

**Escolha: B.** É a única que tira a classificação de "quem preenche" e a coloca no "que está escrito". A viabilidade foi medida no Dataset 2, com treino, validação e teste separados (harness H9).

**Subdecisão: com que rótulos treinar?** Os rótulos atuais são aleatórios (harness H5), e treinar neles **ensinaria o erro**.

| | Opção | A favor | Contra |
|---|---|---|---|
| A | Treinar com os rótulos atuais | Imediato | O modelo aprenderia o sorteio |
| B ✅ | **LLM classifica sem treino, com a taxonomia nova; humano valida uma amostra; isso vira um conjunto de referência (gold set) que treina um modelo supervisionado barato** | Começa no dia 1 e gera rótulos como subproduto; o estado final (supervisionado) foi comprovado no H9 | A acurácia do LLM **não foi medida aqui**, então precisa de um critério de aprovação |
| C | Rotular 2 a 3 mil tickets à mão antes de começar | Rótulo confiável | Semanas de trabalho de um time já sobrecarregado antes de qualquer ganho |

**Escolha: B, com critério:** o LLM precisa acertar **≥ 90% em 500 tickets rotulados por humanos** antes de entrar em produção. Se não atingir, cai para C.
**Dono:** Operações (taxonomia) + IA. **Verificação:** R07, R08 e H9.

### P3. A prioridade é decorativa · 🔧 Ferramenta + 📋 Processo

*Critical* fica sem resposta na mesma proporção que *Low* (32,5% contra 33,7%). Tickets com "urgente, está afetando meu trabalho" recebem prioridade alta em 52,5% dos casos, o mesmo que o acaso. A prioridade é escolhida livremente e a fila não a usa.

| | Opção | A favor | Contra |
|---|---|---|---|
| A | Configurar SLA por prioridade usando a prioridade **declarada** | Rápido | Aplica SLA a um campo aleatório, ou seja, prioriza o sorteio |
| B ✅ | **Prioridade calculada pelo conteúdo (severidade + urgência + recontato) + SLA na fila** | Liga a urgência real à ordem de atendimento | Depende de P2; enquanto isso, usa regras |
| C | Fila única por ordem de chegada com prazo máximo | Simples e justo | Um ticket de perda de dados espera atrás de uma dúvida de uso |

**Escolha: B.** A opção A fica pior do que parece porque formaliza um dado aleatório. **Contorno já pronto:** a fila do backlog repriorizada por regras transparentes ([`fila_backlog_reprocessada.csv`](outputs/fila_backlog_reprocessada.csv)). Pelo conteúdo, **259 tickets estão subpriorizados** (Low/Medium, mas com perda de dados, conta bloqueada ou urgência) e **457 estão superpriorizados**.
**Dono:** Operações + IA. **Verificação:** R09.

### P4. 1 em cada 3 tickets nunca foi respondido · ❓ Indeterminado (capacidade ou roteamento)

Se fosse **só** falta de gente com a priorização funcionando, os *Critical* seriam respondidos primeiro. Não são. Então existe **no mínimo** um problema de roteamento. Se também faltam pessoas, não dá para medir sem o horário de abertura e o tempo médio de atendimento (P1).

| | Opção | A favor | Contra |
|---|---|---|---|
| A | Contratar | Aumenta a capacidade | Decisão cara sem medição; se o gargalo for roteamento, os contratados herdam a mesma fila cega |
| B ✅ | **Mutirão de backlog com a fila repriorizada + resposta automática de recebimento que já pede os dados que faltam** | Ataca o risco (Critical e perda de dados primeiro) sem decisão irreversível | Esforço pontual; não resolve a causa |
| C | Fechar em massa os tickets antigos | Zera o número | Destrói o CSAT e esconde o problema |

**Escolha: B.** O backlog do dataset são 2.819 tickets × 12 min ≈ **564 h**, algo como 3 agentes por 2 semanas. Começa pelos **531 Critical/High segundo o conteúdo**; os 1.377 sem sinal claro no texto vão para leitura humana. A decisão de contratar fica para **depois** de P1: com o relógio funcionando, a capacidade vira uma conta, não um palpite.
**Dono:** Operações.

### P5. 34% dos tickets parados esperando o cliente · 📋 Processo

Não existe prazo nem cobrança automática. Custo estimado: ≈ 680 h/ano de cobrança manual.

| | Opção | A favor | Contra |
|---|---|---|---|
| A ✅ | **Política automática: 2 lembretes (D+2, D+5) e fechamento em D+7 com reabertura em 1 clique** | Imediata, não depende de dado novo, elimina a cobrança manual | Fecha alguns casos que voltariam |
| B | Agente continua cobrando manualmente | Toque pessoal | É o status quo que custa 680 h |
| C | IA pede os dados que faltam já na abertura, evitando a pendência | Ataca a causa | Exige saber *o que* costuma faltar, e hoje não existe campo de motivo |

**Escolha: A** agora. **C** vira evolução quando existir o campo "motivo da pendência".
**Dono:** Operações.

### P6. O CSAT não mede quem está insatisfeito · 📋 Processo + 🔧 Ferramenta

A pesquisa só é disparada no fechamento, o que cobre 32,7% dos tickets. Os abandonados nunca respondem.

| | Opção | A favor | Contra |
|---|---|---|---|
| A ✅ | **Pesquisa em todo ticket: no fechamento e aos 7 dias aberto; incluir motivo e CES** | Remove o viés de sobrevivência | Mais pesquisas enviadas |
| B | Trocar a pesquisa por análise de sentimento do texto | Sem esforço do cliente | Mede o humor na **entrada**, não a satisfação com o **atendimento** |
| C | Manter e corrigir estatisticamente (ponderação) | Sem mudar o processo | Não corrige dado ausente de forma não aleatória: os ausentes são justamente os insatisfeitos |

**Escolha: A.** **B** entra depois como complemento, não como substituto.
**Dono:** CX. **Verificação:** R11.

### P7. O texto não serve para nada · 🔧 Ferramenta + 📋 Processo

O template não é preenchido (`{product_purchased}`) e a resolução é ilegível. Isso **bloqueia** respostas sugeridas e base de conhecimento, os próximos passos de automação.

| | Opção | A favor | Contra |
|---|---|---|---|
| A ✅ | **Corrigir o template + resolução estruturada (código de solução em lista + texto livre)** | Cria a matéria-prima das respostas sugeridas | Um campo a mais para o agente |
| B | IA resume a resolução a partir da conversa | Zero esforço para o agente | Precisa da conversa gravada, que hoje não está no dataset |
| C | Deixar o campo livre e treinar os agentes | Barato | Não explica o texto gerado; o problema não é humano |

**Escolha: A.** **B** entra como ajuda ao agente quando existir o histórico da conversa.
**Dono:** TI + Operações. **Verificação:** R05 e R06.

### P8. Não existe cliente, só e-mail · 🔧 Ferramenta (modelagem)

139 e-mails aparecem com nomes diferentes. Recontato só pode ser medido pelo texto.

| | Opção | A favor | Contra |
|---|---|---|---|
| A ✅ | **`customer_id` do CRM em todo ticket** | Mede recontato, histórico e valor do cliente | Integração com o CRM |
| B | Deduplicar por e-mail | Imediato | Falha: o mesmo e-mail aparece com nomes diferentes |
| C | Casamento aproximado de nome + e-mail | Recupera o passado | Impreciso, sem garantia |

**Escolha: A.** **Dono:** TI/CRM. **Verificação:** R12.

### P9. Ninguém percebeu · 🏛️ Governança (a única causa humana, e é de gestão)

49% de tempos impossíveis, 100% de placeholders e uma triagem aleatória passaram despercebidos. O problema não é o agente, é a **ausência de um dono do dado**.

| | Opção | A favor | Contra |
|---|---|---|---|
| A ✅ | **Quality Gate diário no pipeline + dono nomeado (Ops Analytics) + alerta quando uma regra falha** | Automático, contínuo, barato; o gate já existe e foi testado (H10) | Exige nomear um dono |
| B | Auditoria manual trimestral | Nenhuma tecnologia | O erro vive até 3 meses sem ser visto |
| C | Treinar os gestores em leitura de dados | Melhora a cultura | Não detecta nada sozinho |

**Escolha: A.** **Dono:** Diretor de Operações nomeia o responsável.

---

## A solução completa, em ordem

O dado precisa ser consertado **antes** da IA: a IA treinada ou avaliada sobre dado ruim aprende o ruído.

```text
SEMANA 1      Parar o sangramento
              · Quality Gate no ETL em modo ALERTA            (pronto: solucao/quality_gate.py)
              · Mutirão do backlog pela fila repriorizada      (pronto: outputs/fila_backlog_reprocessada.csv)
              · Política automática de pendentes (P5)
              · Nomear o dono do dado (P9)

SEMANAS 2–4   Consertar a captura
              · created_at + horários do log de eventos (P1)   → R01–R04 passam
              · Template corrigido + resolução estruturada (P7) → R05–R06
              · CSAT em todo ticket + motivo + CES (P6)        → R11
              · customer_id do CRM (P8)                        → R12

SEMANAS 3–8   Triagem por IA
              · Taxonomia única; LLM rotula → humano valida 500 → gold set
              · Modelo supervisionado com limiar de confiança (padrão H9)
              · Prioridade pelo conteúdo + SLA na fila (P3)    → R07–R09

MÊS 3         Medir de novo
              · Gate em modo BLOQUEANTE
              · Rodar diagnostico.py sobre o dado bom → gargalos e drivers de CSAT reais
              · Decidir capacidade (P4) com números
```

### Metas de acompanhamento

| Indicador | Hoje | Meta no mês 3 |
|---|---|---|
| Regras do Quality Gate aprovadas | 1/12 | 12/12 |
| Triagem coerente com o conteúdo | 18% (acaso) | ≥ 90% |
| Tickets classificados pela IA sem humano | 0% | ~70% (com ≥ 95% de acerto) |
| *Critical* sem 1ª resposta | 32,5% | < 5% |
| Cobertura do CSAT | 32,7% | ≥ 60% |

### Quanto devolve

| Frente | Horas/ano | Base |
|---|---|---|
| Retriagem com IA (líquida, já descontada a revisão humana) | **≈ 1.345 h (≈ R$ 47 mil)** | Cobertura e acurácia **medidas** (H9); 82% da retriagem atual recuperada |
| Cobrança de pendentes automatizada | até ≈ 680 h | Premissas do diagnóstico |
| L1 repetitivo (senha, conta, passo a passo) | ≈ 430 h | Premissas do diagnóstico; é o foco da Entrega 2 |
| **Desperdício total mapeado** | **3.200 – 4.700 h (P10–P90)** | Monte Carlo com 20 mil cenários (H6) |

---

## O que **não** automatizar (já visível nos dados)

- **Tickets abaixo do limiar de confiança (~27%).** Neles a IA acerta 60%, e isso precisa de humano.
- **A classe mais difícil do Dataset 2 é "Administrative rights"**: só 62% dela passa pelo limiar, com 80% de acerto. Permissões administrativas pedem julgamento humano, e a IA erra justamente onde o erro é mais caro (acesso indevido).
- **49% do backlog não tem sinal claro no texto.** A regra manda para humano em vez de adivinhar.
- **Decisão de contratar (P4)** fica com gente e com números, não com modelo.
