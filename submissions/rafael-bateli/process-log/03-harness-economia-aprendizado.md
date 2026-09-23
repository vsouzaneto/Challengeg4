# Process log — Entrega 2, aprofundamento: harness, economia e aprendizado

**Ferramenta:** Claude Code (app desktop, modelo Claude Opus), em worktree git novo; os arquivos da Entrega 2 foram trazidos da worktree anterior.
**Iterações:** 5 rodadas de experimento exploratório → 2 scripts definitivos (`aprendizado.py`, `harness_automacao.py`) + módulo comum (`modelo.py`) → 3 rodadas completas até os números ficarem estáveis e conferidos contra os documentos.

---

## 1. O que pedi

1. Uma **análise mais profunda** e um **harness** para ver se as decisões da Entrega 2 estavam certas.
2. Checar se a entrega é **o que o desafio pede**, e o que dá para entregar **a mais**.
3. **Solução, não só o erro:** para cada coisa derrubada, voltar com a melhor solução, testada.
4. Duas perguntas: **onde economizar sem perder eficiência?** e **o que medir para a IA aprender com os erros e os acertos?**

## 2. Como o harness foi montado

Mesmo método da Entrega 1: **critério escrito no código antes de rodar**, controle quando cabe, e o teste procura a evidência contrária. Priorizei os testes que **mais podiam me desmentir**:
- regras **mais fortes** do que as que eu tinha usado (A2), para não vencer um espantalho;
- um tipo de ticket **que o modelo nunca viu** (A6), o cenário real que a proposta ignorava;
- o gold set **pequeno** (A7), porque o ROI tinha sido calculado com o modelo maduro;
- a intuição popular do **aprendizado ativo** (A8).

## 3. O que caiu e o que entrou no lugar

| Caiu | Evidência | Solução, testada |
|---|---|---|
| "O limiar manda para humano o que o modelo não conhece" | 34,9% a 60,5% da categoria nova sai errado com confiança | Monitor de **devoluções** (3 monitores comparados; só ele funciona) |
| ROI com 73% desde o dia 1 | 3.000 rótulos → 49,8% | Ciclo de aprendizado: 50% → 71% em 11 meses; ano 1 = 1.298 h |
| (implícito) rotular os tickets difíceis primeiro | Sorteio 51,3% × incertos 48,1% | Gold set sorteado; auditoria sorteada |
| "Duplicata sugere a classe" | Modelo já acerta 95,6% ali | Duplicata vincula ao ticket anterior |
| Auditoria de 2% | 49% de chance de ver uma queda de acerto | 10%, por 1,5 h/mês |
| "Permissão: a IA acerta só 80%" | Quando o modelo diz "permissão", acerta 96,7%; o risco é o pedido que vai para Hardware | Proteção **na ação** (aprovação no sistema de identidade); limiar próprio e gatilho de palavra testados e descartados |

## 4. Onde a IA errou (e o harness também)

| # | Erro | Como percebi | Correção |
|---|---|---|---|
| 1 | **Regex anulada por caractere de controle.** Ao gravar código via heredoc, `\b` virou backspace; o gatilho de palavra do B4 deu 0% | O resultado divergia do teste avulso (41,5%) | Reescrito com `chr()`; o A1 agora varre os scripts em busca de caractere de controle. **É a segunda vez** (Entrega 1, erro 7): a regra passou a ser não gravar código com barra invertida por heredoc |
| 2 | **A1 aprovou por coincidência:** "60%" encontrado na meta "≥ 60%" | Conferência manual; o documento dizia "61%" | Números com uma casa decimal |
| 3 | **Erro de sintaxe** introduzido ao trocar ponto por vírgula no meio de uma concatenação de strings | O harness não rodou | Variável intermediária |
| 4 | **Mensagem com vírgulas trocadas por ponto:** um `replace` aplicado à frase inteira | Leitura da saída ("volume. câmbio") | `replace` só no número |
| 5 | **Afirmação sem teste no documento:** "com 50% de devolução o monitor continua funcionando" | Revisão antes de publicar: não simulei esse valor | Frase trocada pelo que foi medido, e a limitação declarada |
| 6 | **Simulação e recomendação desalinhadas:** o ciclo usava auditoria de 5% e o B5 recomendava 10% | Revisão cruzada dos dois resultados | Ciclo re-simulado com 10% |

## 5. O que eu adicionei que a IA sozinha não faria

- **"Não adianta só falar que está errado":** cada decisão derrubada precisou voltar com uma alternativa **testada contra as outras**. Por exemplo, o monitor de devoluções só entrou depois de vencer dois concorrentes.
- **Economizar sem perder eficiência** como pergunta explícita: levou ao achado de que o ganho vem de **acertar**, não de automatizar mais. Isso mudou a recomendação: **não baixar o limiar**.
- **"O que medir para a LLM aprender"**: forçou separar erros (triagem, devolução) de acertos (auditoria sorteada) e mostrar, com simulação, que usar as próprias previsões é uma armadilha.

## 6. Decisões que tomei sobre o que a IA propôs

- Aceitei publicar **4 decisões derrubadas** em vez de ajustar os critérios até tudo passar. Um harness que só confirma não serve.
- Aceitei que a diferença entre "só triagem" e "completo" (≈ 1 p.p.) está **dentro do ruído**, e a escolha do completo se justifica pela **auditoria sem viés**, não pela cobertura.
- Mantive o SVM calibrado como **candidato** (+1,3 p.p., treino 5× mais rápido), sem trocar o modelo: a diferença está dentro da variação entre divisões (A4). Fica para a Entrega 3 decidir com o dado da taxonomia real.
