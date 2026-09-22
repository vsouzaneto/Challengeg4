# Submissão — Robson Martello — Challenge 002

## Sobre mim

- **Nome:** Robson Martello
- **LinkedIn:** [Robson Martello](https://www.linkedin.com/in/rob-martello-65974757/)
- **Challenge escolhido:** 002 — Support Redesign

---

## Resumo executivo

Comecei tentando responder onde IA poderia melhorar a operação de suporte. A principal descoberta foi anterior à automação: os dados atuais não permitem observar com confiança o processo que queremos otimizar.

Testei oportunidades onde IA poderia agregar valor, incluindo classificação de tickets e uma camada probabilística de decisão. Em ambos os casos, alternativas mais simples foram superiores.

**Minha recomendação é não implementar IA operacional neste momento. Primeiro, instrumentar corretamente o processo; depois, medir os gargalos reais e só então qualificar onde IA supera uma referência mais simples.**

---

## Solução

### Abordagem

Não comecei escolhendo um modelo. Comecei pela decisão de negócio:

**Onde IA realmente melhoraria esta operação?**

Usei os dois conjuntos de dados para testar três hipóteses:

1. Os dados permitem identificar os gargalos operacionais?
2. IA generativa melhora o encaminhamento de chamados?
3. Um modelo de decisão pode determinar melhor onde automatizar?

A regra usada durante a análise foi simples:

**Nenhuma solução de IA seria recomendada sem superar uma alternativa mais simples e verificável.**

### Resultados

#### 1. O primeiro gargalo é observabilidade

O conjunto de dados operacional possui 8.469 tickets.

Apenas **1.404 (16,6%)** possuem intervalo temporal válido entre primeira resposta e resolução.

Dos 2.769 registros que possuem ambos os timestamps, **49,3% apresentam duração negativa**.

Além disso, não estão disponíveis informações fundamentais como:

- momento de criação do ticket;
- acordo de nível de serviço;
- tempo efetivo de trabalho do agente;
- transferências entre filas ou agentes;
- reaberturas;
- tempo em fila.

Todos os 1.404 intervalos válidos pertencem a tickets encerrados.

Portanto, consigo analisar uma pequena janela pós-primeira-resposta, mas não medir de forma confiável o ciclo completo do atendimento.

**Não é possível afirmar honestamente onde o processo trava nem quantificar horas desperdiçadas com os dados disponíveis.**

#### 2. Encaminhamento é automatizável — mas IA generativa não foi a melhor solução

O segundo conjunto de dados possui texto e categorias utilizáveis para classificação.

| Método | Acurácia |
| --- | ---: |
| Classe majoritária | 28,5% |
| Naive Bayes | 76,9% |
| TF-IDF + Logistic Regression | **86,6%** |

A confiança do modelo clássico também mostrou utilidade operacional.

Automatizando aproximadamente **60% dos casos de maior confiança**, a acurácia observada foi de aproximadamente **97,8%**, deixando os casos incertos para revisão humana.

Também testei um modelo de linguagem nos casos de menor confiança, onde havia maior possibilidade de ganho.

**O modelo de linguagem piorou o resultado.**

Conclusão:

**Há evidência para automação controlada de encaminhamento, mas não há evidência para justificar IA generativa nessa decisão.**

#### 3. Testei IA também para decidir onde usar IA

Minha última hipótese foi usar o Jev, um modelo probabilístico orientado a decisões, para avaliar se determinado processo estava pronto para automação.

Antes de executar o modelo, congelei 18 cenários e suas respostas esperadas.

| Método | Resultado |
| --- | ---: |
| Regras determinísticas | **18/18 — 100%** |
| Jev | **14/18 — 77,8%** |

O Jev foi consistente entre execuções e retornou a estrutura esperada, mas não adicionou capacidade decisória sobre a referência.

Em um dos erros, retornou uma decisão incorreta com **0,82 de confiança**.

**Decisão: não utilizar Jev.**

### Recomendações

#### 1. Não implementar IA para otimização da resolução ainda

O problema atual não é capacidade do modelo.

É **observabilidade do processo**.

Primeiro instrumentaria:

`criado_em → primeira_resposta_em → fila/transferências → tempo_de_trabalho_do_agente → resolvido_em → reaberto_em → acordo_de_nível_de_serviço`

Com esses eventos confiáveis, passaria a medir onde tempo e esforço realmente são consumidos.

#### 2. Se encaminhamento for prioridade, começar simples

Existe evidência para testar automação controlada de classificação.

Começaria com o modelo clássico já validado, automatizando apenas casos de alta confiança e enviando os demais para humanos.

IA generativa só entraria novamente se demonstrasse ganho sobre essa referência.

#### 3. Reavaliar IA depois da instrumentação

Após acumular dados operacionais confiáveis:

**medir → identificar gargalo → definir referência → testar intervenção → comparar IA → automatizar somente se houver ganho.**

### Limitações

Não estimei horas desperdiçadas ou impacto financeiro porque os dados não possuem informação suficiente para fazer essas estimativas sem assumir valores arbitrários.

Também não atribuí causalidade às diferenças observadas entre canais, prioridades ou tipos de ticket.

Essas ausências são parte da recomendação: antes de automatizar o processo, precisamos torná-lo observável.

---

## Registro do processo — Como usei IA

### Ferramentas usadas

| Ferramenta | Para que usei |
| --- | --- |
| ChatGPT / Codex | Decomposição do problema, formulação e crítica de hipóteses, exploração e validações |
| Modelo de linguagem | Experimento de classificação com encaminhamento alternativo |
| Jev | Experimento de decisão probabilística de prontidão |

### Fluxo de trabalho

1. Comecei procurando uma oportunidade de IA que melhorasse uma decisão real, não apenas uma métrica.
2. Auditei os dados antes de escolher qualquer modelo.
3. Descobri que o conjunto de dados operacional não permitia observar confiavelmente o processo de ponta a ponta.
4. No conjunto de dados textual, estabeleci referências simples antes de testar IA generativa.
5. Logistic Regression atingiu 86,6% e apresentou confiança útil para automação seletiva.
6. Testei o modelo de linguagem justamente nos casos difíceis; o resultado piorou.
7. Removi IA generativa dessa hipótese.
8. Testei então se um modelo probabilístico poderia melhorar a decisão de prontidão.
9. Congelei 18 casos antes do experimento.
10. Regras determinísticas acertaram 18/18; Jev, 14/18.
11. Removi também essa IA da solução.
12. Encerrei sem construir uma aplicação porque os experimentos não justificaram uma.

### Onde a IA errou e como corrigi

Durante o processo, a própria IA frequentemente tentou transformar resultados interessantes em produto.

Minha principal intervenção foi exigir uma pergunta anterior:

**Existe evidência de que deveríamos construir isso?**

Também houve uma tentativa de concluir que Jev não deveria ser usado antes de a API ter sido realmente executada. Mantive os casos congelados, forneci a credencial e exigi que o experimento fosse concluído antes da decisão.

O resultado final confirmou a hipótese contrária ao uso do modelo: referência 100%, Jev 77,8%.

### O que eu adicionei que a IA sozinha não faria

O principal julgamento não foi escolher um modelo.

Foi decidir quando **não usar um**.

Construir uma solução com IA seria simples. O problema mais difícil foi demonstrar que ela melhoraria a decisão existente.

Minha conclusão final foi:

> **O objetivo não era encontrar um lugar para a IA. Era descobrir se ela tinha conquistado um lugar no processo.**

Neste caso, ainda não ganhou esse lugar.

---

## Evidências

- [x] Narrativa escrita do processo e dos experimentos neste README
- [x] Resultados quantitativos reproduzidos no relatório
- [x] Histórico Git da submissão
- [ ] Screenshots ou export adicional de conversas

---

_Submissão enviada em: 21 de setembro de 2026_
