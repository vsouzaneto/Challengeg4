# Harness da Entrega 2: a proposta de automação estava certa?

> Código: [`harness_automacao.py`](harness_automacao.py). Resultados brutos: [`outputs/harness_automacao.json`](outputs/harness_automacao.json).
> Para rodar: `python harness_automacao.py --data2 ../data/it_tickets.csv` (≈ 4 min; roda depois de `automacao.py` e `aprendizado.py`).
> Mesmo método do [harness da Entrega 1](../diagnostico/HARNESS.md): **o critério de cada teste é escrito no código antes de rodar**, e cada teste procura a evidência que provaria que eu estava errado.

---

## Resultado: 9 decisões se sustentaram, 4 caíram

| # | Pergunta | Como tentei derrubar | Resultado | Veredito | O que mudou |
|---|---|---|---|---|---|
| A1 | Os números dos documentos batem com o código? | 11 números-chave da proposta e do documento de economia, procurados no texto como o código os calcula | 11/11 | ✅ Sustentou | (ver erro 8 abaixo) |
| A2 | As regras de palavra-chave foram um espantalho? | Regras **mais fortes**: exigindo margem de 1 a 5 palavras entre a 1ª e a 2ª classe, com 10, 20 e 50 palavras por classe | Com margem, regras **chegam** a 95% de acerto, mas cobrindo no máximo **15,7%** dos tickets; o modelo cobre **73,2%** | ✅ Sustentou a decisão | A frase "regras param em 80%" estava **errada** e foi corrigida |
| A3 | Outro modelo ganha com folga? | 5 modelos: regressão logística com 200 mil e 50 mil variáveis, Naive Bayes, SVM linear calibrado, gradiente estocástico | O melhor (SVM calibrado) cobre 74,5% contra 73,2%, dentro da variação entre divisões (A4) | ✅ Sustentou | **Economia:** 50 mil variáveis dão o mesmo resultado com metade do treino; o SVM treina 5× mais rápido |
| A4 | O limiar é estável? | 5 divisões diferentes de treino, validação e teste | Cobertura 71,3%–74,4%; acerto 95,0%–95,4% | ✅ Sustentou | — |
| A5 | A confiança é calibrada? | Erro de calibração (ECE) em 10 faixas | **0,036** (critério < 0,05) | ✅ Sustentou | — |
| A6 | O limiar protege contra uma **categoria nova**? | Treinei o modelo **sem** uma categoria, 4 vezes, e vi para onde vão os tickets dela | **Não protege.** 34,9% a 60,5% saem classificados errado com confiança alta. Um detector por ticket (similaridade) também falha: AUC 0,51–0,72 | ❌ **Derrubou** | **Monitor de devoluções** (população, não ticket): detecta 5% de novidade em 4 semanas, 100% das vezes ([B2](ECONOMIA_E_APRENDIZADO.md)) |
| A7 | 3.000 rótulos entregam os 73%? | Curva de aprendizado: 500 a 28.701 rótulos | Com 3.000: **49,8%**, não 73% | ❌ **Derrubou** | ROI do ano 1: **1.298 h**, não 1.345 h; o caminho até 71% é o ciclo de aprendizado ([B1](ECONOMIA_E_APRENDIZADO.md)) |
| A8 | Rotular os mais incertos acelera? | Aprendizado ativo (os 500 mais incertos por rodada) contra sorteio, até 3.000 rótulos | Sorteio **51,3%**, incertos **48,1%** | ❌ **Derrubou** | Gold set **sorteado**; auditoria inclui acertos, não só dúvidas |
| A9 | A quase-duplicata ajuda a classificar? | Acerto copiando a classe da duplicata × acerto do modelo **nos mesmos tickets** (controle: acaso) | 96,1% contra 95,6% (acaso: 18,6%) | ❌ **Derrubou** | A duplicata serve para **vincular** ao ticket anterior, não para classificar |
| A10 | Os 33% de humano dependem de um gatilho só? | Removi um gatilho de risco por vez | Nenhum passa de 6,6 p.p. do total | ✅ Sustentou | **Economia:** 1.267 tickets da rota 1 só têm gatilhos em que o risco é a decisão → a IA rascunha (rota 1A, 224 h/ano) |
| A11 | O custo de LLM pode passar do ganho? | Monte Carlo com 20 mil cenários: tokens ×0,5–10, preço ×0,5–3, volume ×0,8–1,5, câmbio R$ 4,50–6,50 | Passa do ganho em **0,04%** dos cenários. Até uma LLM classificando os 30 mil tickets custaria ≈ US$ 16/ano | ✅ Sustentou | Confirma: o token não decide nada |
| A12 | "Regras fixas primeiro" resiste às premissas? | Monte Carlo: horas nas faixas da Entrega 1, esforço ×0,5–2 | As duas regras fixas são as melhores em horas por semana de esforço em **88,1%** dos cenários | ✅ Sustentou | — |
| A13 | A proposta cobre o que o desafio pede? | 12 requisitos do README do desafio, procurados no documento | 12/12 | ✅ Sustentou | (ver erro 7 abaixo) |

---

## O harness me pegou errando (e o que mudei)

| # | Erro na proposta | Como apareceu | Correção |
|---|---|---|---|
| 1 | **"O limiar manda para humano o que o modelo não conhece."** Falso para categorias novas | A6: até 60,5% dos tickets de uma categoria nunca vista saem classificados errado, **com confiança** | Monitor semanal de **devoluções da fila errada**. Testei três monitores; só esse funciona (0,3% de alarme falso) |
| 2 | **ROI do ano 1 superestimado.** A proposta supunha 73% de cobertura desde o dia 1 | A7: 3.000 rótulos dão 49,8% | Ano 1 = 1.298 h (−3,4%). A diferença é pequena porque **o ganho vem de acertar, não de automatizar mais**, e isso virou um princípio (não baixar o limiar para cobrir mais) |
| 3 | **Estratégia de rótulo não definida**, e a intuição ("rotular os difíceis") está errada | A8: sorteio ganha de incerteza | Gold set sorteado e estratificado; auditoria sorteada |
| 4 | **"A duplicata sugere a classe quase de graça."** | A9: o modelo já acerta aqueles tickets | O papel da duplicata virou **vínculo** (histórico, resolução, recontato) |
| 5 | **"Regras param em 80% de acerto."** | A2: com margem, regras chegam a 95%, só que em 16% dos tickets | Frase e gráfico 07 corrigidos; a decisão se mantém |
| 6 | **Auditoria de 2%** dos automáticos | B5: com 2%, uma queda de 95% para 90% passa despercebida metade das vezes | **10%**: 88% de chance de ver a queda no mês, por 1,5 h/mês |
| 7 | **"Administrative rights: a IA acerta só 80%"**, lido como "a IA erra quando diz permissão" | B4: quando o modelo diz "permissão", acerta 96,7%. O risco é o contrário: o pedido de permissão que vai para Hardware | Proteção **na ação** (nenhuma concessão de acesso sem aprovação humana), não no rótulo; gatilho de palavra testado e descartado |
| 8 | **Falta de ROI em horas/mês e da acurácia geral sem limiar**, pedidos implícitos do desafio | A13, escrito a partir das dicas do README | Coluna h/mês (≈ 290 h/mês) e acurácia sem limiar (85,8%) na proposta |

**E o harness também errou:**

| # | Erro do harness | Como apareceu | Correção |
|---|---|---|---|
| 9 | **A1 aprovou por coincidência:** procurava "60%" e achou a meta "≥ 60%" do copiloto, não o número da categoria nova | Conferência manual: o documento dizia "61%" e o código arredondava para "60%" | Números com uma casa decimal ("60,5%"), que não colidem com metas redondas |
| 10 | **Regex sem efeito:** o gatilho de palavra do B4 deu 0% | Divergia do teste avulso (41,5%) | Um `\b` virou caractere de controle ao gravar o arquivo (o mesmo tipo de erro da Entrega 1). Corrigido, e agora os 4 scripts são varridos em busca de caracteres de controle |

---

## O que o harness **não** consegue verificar

- **Acurácia da LLM.** Não houve chamada de API. Por isso toda LLM começa com humano aprovando, e as métricas do copiloto são um plano de medição com gatilho de volta ([seção 2.4](ECONOMIA_E_APRENDIZADO.md)).
- **Recall dos gatilhos de risco em texto livre.** No Dataset 1, os gatilhos reconhecem frases de template; em produção, o falso negativo de risco é medido na operação (meta: zero; revisão em 48 h).
- **Premissas de minutos** (rascunho, revisão, rótulo). Faixas explícitas no código; só a operação mede o valor real.
- **Comportamento humano.** A simulação supõe que o agente devolve 80% dos tickets errados e que a triagem humana está certa. Na prática, a auditoria usa um revisor diferente de quem triou.

---

## Aderência ao desafio: a Entrega 2 responde o que foi pedido?

### Requisitos da Entrega 2 (README do desafio)

| Pedido | Status | Onde |
|---|---|---|
| Proposta **com base em ambos os datasets** | ✅ Dataset 1: rotas, exemplos e gatilhos. Dataset 2: classificação, duplicata, limiar, aprendizado | Proposta, seções 1–3 |
| **O que automatizar:** classificação automática | ✅ 3 opções; modelo supervisionado com limiar; medido e testado (A2–A5) | Proposta 1.1 |
| Roteamento inteligente | ✅ 3 opções; tabela classe → fila | Proposta 1.2 |
| Respostas sugeridas | ✅ 3 opções; LLM + base curada + aprovação; plano de medição | Proposta 1.3; Economia 2.4–2.5 |
| Triagem de prioridade | ✅ 3 opções; sinais + SLA; exemplo #7971 | Proposta 1.4 |
| Detecção de duplicatas | ✅ 3 opções; papel corrigido pelo A9 | Proposta 1.5 |
| **O que NÃO automatizar**, com exemplos dos dados | ✅ 33% dos tickets, 9 exemplos com ID, mais Dataset 2 (permissão, RH) | Proposta 2 |
| **Como funcionaria na prática:** entra → etapas → IA → humano | ✅ Fluxograma, tabela "onde o humano entra", 3 tickets atravessando o fluxo | Proposta 3 |

### Critérios de qualidade do desafio

| Critério | Status | Evidência |
|---|---|---|
| Usou ambos os datasets? | ✅ | Acima |
| Números concretos? | ✅ | Todo número vem de script; 11 conferidos pelo A1 |
| Automação realista (100% é red flag)? | ✅ | 33% direto para humano; a IA não decide nada de risco; o harness **reduziu** promessas (A6, A7) em vez de inflá-las |
| Sabe onde a IA ajuda e onde o humano é insubstituível? | ✅ | Rotas 1A/1B; proteção na ação (permissão); critério de promoção de nível |
| "Automação X economiza Y horas/mês" (dica) | ✅ | Coluna h/mês; ano 1 × regime |
| "Pense no agente de suporte" (dica) | ✅ | Dossiê, rascunho na 1A, 3 sugestões na triagem, motivo de rejeição em 1 clique |
| "Os melhores sabem onde parar" (dica) | ✅ | Seção 1.3 da Economia: 4 coisas que **não** construir, com o número que as derrubou |

### O risco que o avaliador pode ver, e a resposta

> *"O candidato aponta erro, mas cadê a solução?"*

Cada decisão derrubada voltou **com a solução testada**, não só com o diagnóstico:

| Derrubado | Solução | Testada? |
|---|---|---|
| Limiar não protege contra novidade (A6) | Monitor de devoluções | ✅ 3 monitores comparados; poder e alarme falso medidos |
| 73% no dia 1 (A7) | Ciclo de aprendizado com 4 sinais | ✅ 4 estratégias, 11 meses simulados |
| Rotular os difíceis (A8) | Gold set sorteado + auditoria de acertos | ✅ |
| Duplicata classifica (A9) | Duplicata vincula | ✅ (a parte que não paga saiu do escopo) |
| Auditoria de 2% (B5) | 10% | ✅ poder calculado por tamanho |
| Risco de permissão lido errado (B4) | Proteção na ação | ✅ limiar e gatilho testados e descartados |

---

## Além do que foi pedido

1. **Harness de falsificação na proposta de automação**, não só no diagnóstico: 13 testes, 4 derrubadas, e os erros do próprio harness registrados.
2. **Ciclo de aprendizado simulado**: mostra, com dado real, que o modelo sai de 50% para 71% usando só o trabalho que o time já faz, e que o autotreino é uma armadilha.
3. **Monitor de categoria nova** que funciona, escolhido entre três por poder e alarme falso medidos.
4. **Economias sem perda** (≈ 480 h/ano a mais) e **onde não economizar** (auditoria, gold set, grupo de controle), com número.
5. **Plano de medição da LLM**: métricas com meta e gatilho de volta, motivos de rejeição em lista fechada, registro de evento e quatro canais de aprendizado sem re-treino.
