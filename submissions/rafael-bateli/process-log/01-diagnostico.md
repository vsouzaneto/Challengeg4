# Process log — Entrega 1: Diagnóstico operacional

**Ferramenta:** Claude Code (app desktop, modelo Claude Opus), em sessões com worktree git isolado.
**Iterações:** 3 rodadas grandes (diagnóstico → harness e causa raiz → empacotamento), com dezenas de execuções de script entre elas.

---

## 1. Como decompus o problema antes de pedir à IA

Antes da análise, defini três regras para a IA seguir:

1. **Cada etapa com 3 opções**, prós e contras equivalentes, e a justificativa da escolhida. Objetivo: não aceitar a primeira resposta nem enviesar.
2. **Dado faltando ou quebrado é achado, não obstáculo.** A resposta vira "o fluxo trava porque o dado não é registrado corretamente", e é obrigatório mostrar **o erro e a resolução**.
3. **Contexto do Diretor:** onde perdemos tempo, o que automatizar, e "quero ver algo rodando".

## 2. Rodada 1: diagnóstico

- **Exploração:** a IA descobriu que o CSV tem **8.469 tickets, não ~30 mil**. `wc -l` dá 29.807 linhas porque as descrições ocupam várias linhas. Primeira armadilha evitada.
- **Achado central:** `First Response Time` e `Time to Resolution` são **horários, não durações**, e 49% dos fechados têm resolução antes da resposta.
- **Testes estatísticos** (Kruskal-Wallis, qui-quadrado, permutação, Random Forest com validação cruzada): nenhuma variável explica tempo ou CSAT.
- **Decisão registrada com 3 opções** em cada etapa (integridade, tempo, triagem, CSAT, desperdício).
- **Resultado:** [DIAGNOSTICO.md](../solution/diagnostico/DIAGNOSTICO.md), 5 gráficos, `diagnostico.py` reproduzível.

## 3. Rodada 2: "eu estava certo?"

Pedi quatro coisas: um **harness** para verificar as decisões, a **aderência ao desafio**, uma entrega **além do pedido na solução** e a pergunta **"é problema humano ou de ferramenta?"**.

- **Harness H1–H10:** controle positivo, efeito plantado, bootstrap, permutação, Monte Carlo, mapas perturbados, forense, validação da IA em dado real e teste de mutação do Quality Gate.
- **Forense humano × ferramenta:** antes de medir, escrevi o rastro que um erro humano deixaria; nenhum apareceu. A descoberta mais forte: **100% dos pares resolução/resposta têm os mesmos segundos**, ou seja, a resolução é *calculada* pelo sistema, não registrada.
- **Solução que roda:** `quality_gate.py` (contrato de dados) e `triagem_ia.py` (IA validada no Dataset 2, ROI medido, backlog repriorizado).
- **Resultado:** [HARNESS.md](../solution/diagnostico/HARNESS.md) e [CAUSA_RAIZ_E_SOLUCAO.md](../solution/diagnostico/CAUSA_RAIZ_E_SOLUCAO.md).

## 4. Onde a IA errou e como foi corrigido

| # | Erro da IA | Como percebi | Correção |
|---|---|---|---|
| 1 | **Teste de poder inflado.** Plantava o efeito em cima da vantagem que o grupo já tinha por acaso; o resultado dizia que efeitos 3× menores que o real seriam detectados | Um 10/10 na primeira rodada do harness é suspeito, então revisei cada teste | Embaralhar antes de plantar. Efeito mínimo honesto: 1,5 h e 0,24 ponto |
| 2 | **Faixa de desperdício exagerada** (1.700 a 7.100 h) apresentada como faixa típica | O Monte Carlo mostrou que ela exige todas as premissas no extremo ao mesmo tempo | Resumo passou a usar P10–P90 (3.200 a 4.700 h) |
| 3 | **Número com denominador errado** (1,2% dos horários com :00) | O recálculo do harness divergiu do texto | Corrigido para 1,8%: o cálculo antigo contava linhas vazias |
| 4 | **Bug no teste de desalinhamento de colunas** (9,8%, abaixo do acaso) | Um valor abaixo do acaso não faz sentido nesse teste | Filtro de listas vazias; 20,8%, sem pico |
| 5 | **Hipótese fraca como explicação** ("fila por ordem de chegada") | A forense trouxe evidência melhor | Texto passou a citar a evidência |
| 6 | **Duas fontes para o mesmo número** (86,7% contra 85,8% de acurácia) | Divergência entre documentos | O harness passou a chamar o mesmo código da solução |
| 7 | **Edição com regex corrompeu uma linha** (caracteres de controle no lugar de `\1,\2`) | A saída do teste forense saiu com números quebrados ("`,%`") | Linha reescrita via script; arquivo verificado sem caracteres de controle |

## 5. O que eu adicionei que a IA sozinha não faria

- **"Não adianta só falar que está errado":** exigi a melhor solução para cada erro, com dono e forma de verificação.
- **A pergunta humano × ferramenta:** mudou o destinatário do plano. O conserto é de TI e processo; treinar ou culpar agentes seria atacar o alvo errado.
- **3 opções por decisão, sem viés:** tornou visível o que foi descartado e por quê.
- **Desconfiar do próprio resultado:** pedir um harness que tentasse derrubar as conclusões, em vez de aceitá-las.

## 6. Decisões que tomei sobre o que a IA propôs

- Aceitei **não** publicar um ranking de "piores combinações" nem de "drivers de CSAT", mesmo sendo o que o desafio parece esperar. O harness provou que seriam ruído (H3, H4).
- Aceitei usar premissas explícitas para custo, com a condição de que fiquem trocáveis no código e com faixa de incerteza.
- A triagem por IA só vai para produção com critério de aprovação (≥ 90% em 500 tickets rotulados por humanos).
