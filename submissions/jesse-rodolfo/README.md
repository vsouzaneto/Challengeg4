# Submissão: Jessé Rodolfo Machado, Challenge 002 (Redesign de Suporte)

## Sobre mim

- **Nome:** Jessé Rodolfo Machado
- **LinkedIn:** linkedin.com/in/jesserodolfo
- **Challenge escolhido:** 002, Redesign de Suporte

---

## Executive Summary

O dataset 1 tem 8.469 tickets (não 30 mil) e é sintético: os campos de tempo são carimbos de hora de uma janela de 27 horas, e a nota do cliente não é explicada por nenhuma variável. O que os dados sustentam é a fila: 67% dos tickets não estão fechados (33% abertos e 34% esperando o cliente). O desperdício, calculado por premissa sobre os 30 mil tickets do brief, vai de 1.042 a 11.400 horas por ano (base 3.950, 2,5 agentes), e o maior item recuperável é cobrar o cliente parado (1.700 h). Recomendação 1: padronizar a entrada e registrar cinco campos antes de automatizar; o piloto é o lembrete de cliente parado, só em e-mail. O protótipo classifica os tickets do dataset 2 com 85,69% de acerto no held-out, e 57,3% seguem automáticos com 96,5% de acerto depois do limiar e dos portões.

---

## Solução

### Abordagem

Método: mapear o processo, eliminar o que não precisa existir, padronizar, automatizar, medir. IA entra por último. Hipóteses antes de abrir os dados, auditoria antes do diagnóstico, faixas com premissas declaradas, piloto pequeno. Os datasets são duas organizações diferentes e não foram misturados: o dataset 1 é a operação diagnosticada; o dataset 2 prova que classificar por texto funciona.

### Resultados / Findings

#### Onde estamos perdendo tempo?

**Na espera: 67% dos tickets não estão fechados (33% abertos e 34% esperando o cliente), o que em horas dá de 1.042 a 11.400 por ano, base 3.950.**

O que o dataset 1 não permite concluir (prova em `docs/auditoria-dados.md`):

- Horários em janela de 27 horas, sem hora de abertura: tempo de resposta e de resolução não são calculáveis. 49% dos fechados (1.365 de 2.769) resolvem antes da primeira resposta.
- Nota não explicada por nenhuma variável: um modelo com todas acerta 20,0%, contra 20,9% de chutar a mais comum.
- Descrições com `{product_purchased}` sem substituir em 100% e só 16 frases de abertura distintas.

Mesmo assim, o desperdício em faixa sobre os 30 mil tickets do brief (premissas e origem de cada número em `solution/01-diagnostico.md`):

| Desperdício (h/ano) | Baixo | Base | Alto | Etiqueta |
|---|---|---|---|---|
| Cobrar o cliente parado | 375 | 1.700 | 5.400 | Recuperável por automação |
| Repasse entre filas | 250 | 1.000 | 2.250 | Recuperável por automação |
| Triagem manual | 167 | 250 | 1.500 | Recuperável por automação |
| Reabertura | 250 | 1.000 | 2.250 | Não recuperável até medir a causa |
| **Total** | **1.042** | **3.950** | **11.400** | |
| Agentes em tempo integral | 0,7 | 2,5 | 7,1 | |
| Custo/ano | R$ 31 mil | R$ 198 mil | R$ 798 mil | |

Duas premissas são minhas: triagem cronometrada em mim (5 tickets, média 19,9 s) e custo da hora da minha operação (R$ 30, 50 e 70; era de venda, não de suporte). As que mais mexem no total são as do ciclo de cobrança, e nenhuma é medida hoje.

#### O que pode ser automatizado com IA?

**Primeiro o lembrete de cliente parado (fase 1), depois triagem e roteamento (fase 2); nada que decida dinheiro, alçada, crítico ou cliente já insatisfeito.**

**Regra mestra:** a IA só responde o que existe no banco de respostas validadas. O que não bate com nada do banco vai para um humano, que valida uma vez; a resposta entra no banco e da próxima vez sai automática. A IA nunca inventa. Desenho do meu produto, não resultado medido em escala.

**Fluxo:** entrada estruturada (menu de tipo e 2 ou 3 campos obrigatórios) e classificador conferem; o banco validado responde; portão e desconhecido vão para o humano. Lembrete de cliente parado; aprendizado pela nota (4 ou 5 vira resposta sugerida, 1 ou 2 vai para revisão).

**Portões de autoridade.** Ficam com humano mesmo com resposta no banco, por falta de alçada da IA e não por falta de resposta:

| Portão | Exemplo no dataset 1 | Tickets |
|---|---|---|
| Reembolso | Refund request | 1.752 |
| Dúvida ou disputa de fatura | Billing inquiry e assunto Payment issue | 1.634 e 526 |
| Cancelamento | Cancellation request | 1.695 |
| Crítico (por regra operacional: serviço fora, pagamento bloqueado, perda de dados confirmada) | Priority Critical | 2.129 |
| Cliente já insatisfeito | Nota 1 ou 2 entre os fechados | 1.102 de 2.769 |

Financeiro ou Critical somam 75,3% dos tickets: efeito do sorteio uniforme do dataset; o piloto mede a proporção real. Acesso à conta e perda de dados não são portão, são os tipos mais padronizáveis.

**Piloto da fase 1, "Lembrete de cliente parado":**

- Só e-mail. Pendente de chat é cliente que saiu do site: pede régua de inatividade em minutos, onda posterior.
- Lembretes em 2 e 5 dias úteis; encerramento em 7, avisando que responder reabre. Portões nunca fecham sozinhos.
- Contadores: lembretes enviados, encerrados automaticamente, reabertos depois. 8 semanas; reabertura acima de 20% suspende o encerramento.
- Volume pequeno (cerca de 34 encerramentos): mostra direção, não taxa.

**Fase 2** (triagem e roteamento) só depois dos campos instrumentados, da entrada estruturada e do limiar calibrado com tickets reais. Pausa se menos de 60% passarem do limiar ou se humanos corrigirem mais de 15%.

**ROI da fase 1.** Substituição da cobrança, fechamento por prazo e reabertura são premissas da IA, não medidas; a implantação (20 a 40 h) é minha:

| | Conservador | Base | Otimista |
|---|---|---|---|
| Líquido h/ano, todos os canais | 97 | 1.161 | 4.855 |
| Líquido R$/ano, só e-mail (piloto) | R$ 0,7 mil | R$ 14,7 mil | R$ 86 mil |
| Implantação | R$ 1,2 mil | R$ 1,5 mil | R$ 1,4 mil |
| Retorno da implantação, só o piloto | 19,6 meses | 1,2 mês | 0,2 mês |

O piloto se justifica como instrumentação, não só pelas horas: é a primeira medição real dos campos, e o retorno maior está na fase 2, que depende deles.

#### Mostre que funciona

**No dataset 2, o classificador acerta 85,69% no held-out, contra 28,47% de chutar sempre Hardware; depois do limiar de 0,7 e dos portões, 57,3% seguem automáticos com 96,5% de acerto. Não transfere para o dataset 1.**

- **O que é:** TF-IDF (1 a 2 gramas, `min_df=3`) com regressão logística, sem o resíduo de assinatura. Roteia cada texto para "automático" ou "humano".
- **Como medi:** separei 20% (9.568 tickets) antes de treinar, estratificado, seed 42; treinei nos 38.269 restantes e comparei com a marcação.

| Limiar | Cobertura (acima do limiar) | Acerto nos aceitos |
|---|---|---|
| 0,5 | 82,7% | 92,1% |
| 0,6 | 73,1% | 94,6% |
| **0,7** | **62,9%** | **96,7%** |
| 0,8 | 52,0% | 98,0% |
| 0,9 | 38,7% | 99,3% |

- **Escolha de 0,7:** categoria errada vira resposta validada errada; um erro em 30 nos aceitos é o máximo que aceito, e 0,9 cobre só 38,7%. Os portões `Purchase` e `Administrative rights` tiram 5,6%, e sobram 57,3% automáticos com 96,5% de acerto. Limiar e portões: propostos pela IA, confirmados por mim.
- **Testes:** 5 de 5 passam (modelo carrega; vazio, confiança baixa e portão vão para humano; texto claro de `Purchase` acerta). Protegem a regra de roteamento, não a acurácia.
- **Limites:** o texto do dataset 2 já vem limpo e a cobertura pode cair com texto real; Miscellaneous é categoria genérica (recall de 82,2%, e 138 dos 1.412 vão para Hardware); o modelo não transfere para o dataset 1. Administrative rights com recall de 61,4%: 4 em 10 pedidos de direito administrativo saem como outra categoria e, com confiança alta, escapam do portão. No held-out, 30 dos 352 (8,5%) chegam a "automático". Na fase 2 o portão não pode depender só do classificador: palavra-chave (admin, rights, permission) como segunda trava, e ticket cuja segunda categoria mais provável é portão vai para o humano.

**Como rodar** (da raiz da submissão; `download.sh` exige `pip install kaggle` e `~/.kaggle/kaggle.json`):

```
bash solution/data/download.sh
python -m venv .venv && .venv/bin/pip install -r requirements.txt
for s in 01_auditoria 02_diagnostico 03_proposta; do .venv/bin/python -I solution/analise/$s.py; done
.venv/bin/python -I solution/prototipo/treinar.py
.venv/bin/python -I solution/prototipo/rotear.py "texto do ticket"
.venv/bin/python -m pytest solution/prototipo -q
```

### Recomendações

1. **Padronizar a entrada e registrar cinco campos antes de automatizar:** abertura, mudança de status, reabertura, histórico de fila e responsável, e resolução aplicada ligada à nota. Sem eles, nenhuma automação tem antes e depois.
2. **Piloto "Lembrete de cliente parado"** em e-mail por 8 semanas, medindo a cobrança na primeira semana.
3. **Só então a fase 2**, com limiar calibrado em tickets reais, regras de parada e segunda trava do portão.

### Limitações

- O dataset 1 é sintético e tem 28% do volume do brief: tempo, nota e retrabalho não são medidos, e o desperdício é estimativa por premissa.
- Repasse, cobrança e reabertura são premissas não medidas; três da ROI são da IA. O piloto tem volume pequeno: indica direção, não taxa.
- A acurácia é contra o rótulo do dataset 2, que tem ruído: a triagem humana sem ajuda acertou 1 de 5 contra ele.
- Limiar e portões não foram calibrados com tickets reais; a cobertura de 62,9% está perto da parada de 60% da fase 2, e a regra não muda depois de ver o número.
- Portão de Administrative rights frágil (recall de 61,4%), detalhado nos limites do protótipo.
- Sem interface gráfica, por decisão minha: linha de comando com testes já prova o fluxo.

---

## Process Log: Como usei IA

> Log completo, com horários e decisões, em `process-log/PROCESS-LOG.md`.

### Ferramentas usadas

| Ferramenta | Para que usou |
|------------|--------------|
| Claude Code com Opus 5.5 | Blocos 0 a 3: auditoria, diagnóstico e proposta |
| Claude Code com Sonnet 5.5 | Blocos 4 e 5: protótipo e fechamento (troca por limite de uso do Opus) |
| App Claude com Fable 5.1 | Revisor nos checkpoints de bloco |
| Python, pandas, scikit-learn, scipy, pytest | Análise, classificador e testes |
| Git, `commit.sh` | Commit por bloco, sem subir dados brutos |
| Claude Code com Opus 5.5 | Revisão final de consistência, só leitura, com Opus 5.5 |

Nenhuma decisão foi delegada: a IA propôs, eu confirmei ou rejeitei, e o log registra cada caso.

### Workflow

Um bloco por vez, horários na tabela de tempo: hipóteses minhas antes dos dados (0); a IA audita e eu decido tratar o dataset 1 como sintético (1); a IA monta as faixas e eu troco premissas por dados meus (2); a IA propõe fluxo, portões e ROI e eu fecho regra mestra, entrada estruturada e piloto (3); a IA escreve o protótipo e eu escolho limiar e portões (4); README e fechamento (5).

### Onde a IA errou e como corrigi

| Erro | Correção |
|---|---|
| Script da auditoria usou a coluna `Product`; o nome é `Product Purchased` | Quebrou antes de calcular; corrigi e rodei de novo |
| Propôs triagem de 1,5 a 5 minutos por ticket, sem medir | Cronometrei: média 19,9 s. Triagem base caiu de 1.500 para 250 h/ano; total de 5.200 para 3.950 h |
| Deu 78,8% dos tickets em portão, contando acesso e perda de dados | Os dois saíram dos portões; ficou 75,3% |
| Apresentou 62,9% como automático com 96,7% de acerto | É o número de passar do limiar; automático é 57,3% com 96,5% |
| O log dizia que a IA propôs juntar e-mail e chat | A IA ofereceu dois canais, sem nomear chat; corrigi o log e fiquei só com e-mail |

### O que eu adicionei que a IA sozinha não faria, e o que fiz diferente do baseline

O G4 rodou o brief em Claude, GPT e Gemini. O que veio do meu julgamento:

- **Desconfiar do dado antes de diagnosticar:** a auditoria veio antes de qualquer média, por instrução do meu `CLAUDE.md`.
- **Regra mestra e portões por autoridade:** a IA propôs uma lista de sete itens para "não automatizar"; troquei por uma regra mestra do meu produto, em que dinheiro e crítico ficam com humano por falta de alçada da IA, não de resposta.
- **Entrada estruturada:** o texto do ticket é algo a padronizar antes da ferramenta, não entrada fixa a classificar. Vem de empresas em que vi funcionar e da minha triagem errando por assinatura.
- **Dados da minha operação onde faltava medição:** custo da hora, tempo de implantação, e a triagem cronometrada em mim mesmo.
- **Cortes de escopo:** acesso e perda de dados fora dos portões, piloto só em e-mail, fase 2 separada, sensibilidade mantida sem ajustar premissa ao resultado esperado.

### Tempo

Orçamento do G4: 4 a 6 horas. Líquido = decorrido menos pausas (2 min de bloqueio do macOS e 15 de café, 17 no total). Intervalos entre blocos contam como trabalho.

Véspera (13/10, até 19:33): estrutura da pasta, kit de sessão (CLAUDE.md, commit.sh, guia de git), script de download e download dos CSVs. Nenhum dado aberto ou analisado; não conta no tempo.

| Período | Minutos | O que foi feito |
|---|---|---|
| Bloco 0 (07:30 a 07:55) | 25 | |
| Bloco 1 (07:58 a 08:15) | 17 | 2 de pausa por permissão do macOS |
| Bloco 2 (08:18 a 09:12) | 54 | |
| Bloco 3 (09:58 a 11:00) | 62 | |
| Bloco 4 (11:05 a 11:15) | 10 | |
| Intervalos curtos (07:55, 08:15, 11:00) | 11 | Checkpoints com o revisor, campos do log e commits |
| 09:12 a 09:58 | 46 | 15 de café; 31 de glossário do diagnóstico, dúvida sobre declarar dois modelos e rascunho do README |
| 11:15 a 11:35 | 20 | Campos do log do Bloco 4, correção do 62,9%, segundo commit |
| **Decorrido até 11:35** | **245** | **Líquido: 228 min (3 h 48)** |
| Bloco 5 (11:35 a 12:30) | 55 | README e fechamento |
| **Total (07:30 a 12:30)** | **300** | **Líquido: 283 min (4 h 43), 17 de pausa** |

---

## Evidências

- [x] Screenshots das conversas com IA: 4 prints em `process-log/screenshots/`
- [ ] Screen recording do workflow
- [x] Chat exports: `process-log/chat-exports/claude-code-sessao-2026-10-14.md`
- [x] Git history: um commit por bloco; o `bloco4: prototipo` tem dois commits, o segundo corrige 62,9% para 57,3%
- [x] Process log, código e testes: `process-log/PROCESS-LOG.md`, `solution/`

---

_Submissão enviada em: 14/10/2026, PR aberto às 12:35_
