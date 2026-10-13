# Submissão — Gabriel Mata — Challenge 004

## Sobre mim

- **Nome:** Gabriel Mata
- **LinkedIn:** [linkedin.com/in/gabriel-mata-b51b42210](https://www.linkedin.com/in/gabriel-mata-b51b42210/)
- **Challenge escolhido:** 004 — Estratégia Social Media

**Atalhos:**
- 📄 [Relatório executivo (Head de Marketing)](solution/report/relatorio_executivo.md) · [PDF](solution/report/relatorio_executivo.pdf)
- 🔬 [Relatório técnico (avaliador)](solution/report/relatorio_tecnico.md) · [PDF completo](solution/report/relatorio_completo.pdf)
- 🧭 [Ferramenta "Decisor de Campanha" online](https://gabriellmata7.github.io/ai-master-challenge/submissions/gabriel-mata/solution/tool/decisor.html) · [arquivo](solution/tool/decisor.html)
- 🗂️ [Process log](process-log/process-log.md)

---

## Executive Summary

Analisei os 52 mil posts para responder às três perguntas do Head de Marketing. Nenhuma escolha que a empresa controla (plataforma, formato, categoria, tamanho do influenciador, patrocínio, horário, hashtags) nem o perfil de público altera o engajamento ou o alcance. **Isso está provado, não suposto:** o maior efeito possível de qualquer variável é de 0,4% (2,6 interações por post, de ~2.010), e o método detectou 74 de 74 efeitos artificiais inseridos de propósito para testá-lo.

A consequência central: **cada real pago em patrocínio compra zero engajamento adicional**. A recomendação é ter o orgânico como base da estratégia, o patrocínio como exceção (só com objetivo de venda ou nova audiência, sempre medido) e um plano de 8 semanas para gerar com dados reais as respostas que esta base não dá. Para o dia a dia, entrego o **Decisor de Campanha**: uma ferramenta que recebe o histórico de posts da empresa, aplica o mesmo método e devolve, em linguagem simples, um resumo para a próxima campanha.

---

## Solução

### Abordagem

1. **Desconfiar antes de analisar.** O planejamento previu que datasets de redes sociais do Kaggle costumam ser sintéticos. Por isso, o primeiro passo foi um teste de sinal, com dois cenários definidos de antemão: há sinal, ou é ruído.
2. **Regra de decisão fixada antes de ver os resultados.** Um segmento só "funciona" com diferença de pelo menos ±10% vs. a média da plataforma, IC 95% (bootstrap) excluindo 1, repetição em duas metades da base e n ≥ 100. Também foi feita uma análise de sensibilidade com cortes de 3%, 5% e 10%.
3. **Do isolado ao combinado.** Variáveis isoladas, combinações de até 4 variáveis (693 segmentos), 126 personas de público, patrocínio comparado dentro de grupos iguais, regressão com controles e modelo preditivo testando todas as interações ao mesmo tempo.
4. **Provar o nulo, não só deixar de encontrar efeito:**
   - teste de equivalência (limite máximo do efeito);
   - menor efeito detectável;
   - **controle positivo** (injetar efeitos falsos e conferir que o método os encontra);
   - caudas da distribuição;
   - tendência no tempo.
5. **Comparar métodos com um baseline.** O brief e o CSV foram enviados a um chat do Claude sem contexto, num único envio. A conclusão coincidiu, o que reforça a lógica. A diferença está no embasamento (ver o [relatório técnico](solution/report/relatorio_tecnico.md#9-comparação-com-o-baseline)).

### Resultados / Findings

| Pergunta do Head | Resposta | Evidência principal |
|---|---|---|
| O que gera engajamento? | **Nada que a empresa controla** | 693 segmentos entre −1,7% e +1,8%, todos dentro do acaso; modelo preditivo pior que prever a média |
| Patrocínio funciona? | **Não muda engajamento nem alcance** | Patrocinado ÷ orgânico = 0,9999 (IC 0,9994–1,0004); 42,7% dos posts são patrocinados e geram 42,7% do engajamento |
| Qual público engaja mais? | **Nenhum** | 126 personas e 68 combinações formato × público, todas dentro do acaso |
| O que não funciona? | **Práticas de decisão**, não conteúdos | Engajamento ÷ seguidores (artefato de 29x), "top segmentos" (não se repetem), pagar por seguidores |
| Quão seguro é isso? | **Muito** | 105 de 105 segmentos equivalentes a ±1%; o método detecta efeitos a partir de 0,06–0,40% |

![Patrocinado e orgânico entregam o mesmo engajamento](solution/outputs/os05/grafico_01_engajamento_por_faixa.png)

**Diagnóstico da base:** os dados se comportam como simulados (views quase constantes, variância ÷ média ≈ 1, nenhum post fracassado ou viral, creator sem identidade estável). A pergunta passou a ser "o que estes dados permitem afirmar, e com que segurança?".

### Recomendações (priorizadas)

1. **Orgânico como base da estratégia.** Entrega o mesmo engajamento e o mesmo alcance que o patrocinado.
2. **Patrocínio só com objetivo de venda ou nova audiência**, definido antes e medido com UTM e cupom. Preço pelo desempenho comprovado, nunca por seguidores, e nunca acima do que a mídia paga custaria para o mesmo objetivo.
3. **Trocar o indicador** para interações por post (ou por visualização). Abolir a divisão por seguidores.
4. **Parar** de otimizar horário, dia e hashtags, e de decidir a partir de "top posts".
5. **Plano de 8 semanas com dados reais:**
   - teste orgânico com versões muito diferentes;
   - teste de cadência orgânica;
   - teste de patrocínio por custo por venda;
   - decisão em três níveis: funciona / não faz diferença / ainda não dá para saber.

Quick wins da semana e política completa: [relatório executivo](solution/report/relatorio_executivo.md).

### A ferramenta: Decisor de Campanha

**[Abrir online](https://gabriellmata7.github.io/ai-master-challenge/submissions/gabriel-mata/solution/tool/decisor.html)** ou abrir `solution/tool/decisor.html` no navegador. Não precisa instalar nada.

- **Uso:** a pessoa vai lançar uma campanha, sobe o histórico de posts e descobre em que se basear.
- **Diagnóstico:**
  - resumo para a próxima campanha;
  - "Vale a pena pagar influenciador?";
  - o que funcionou melhor e pior;
  - para quem falar;
  - "Dá para confiar nestes dados?".
- **Planejar campanha:** testar uma ideia antes de colocar no ar, e um simulador do mês que compara "seu plano × se todos os posts fossem sem pagar", mostrando em reais o que se economiza.
- **Feita para quem não é técnico:** vereditos em linguagem simples ("Funcionou melhor", "Não faz diferença", "Ainda não dá para saber"), sem jargão na tela principal, tema claro e escuro.
- **Não inventa vencedor:** todo resultado passa pelo mesmo método estatístico da análise, com correção para muitas comparações. "Nenhum público comprovado" é uma resposta válida.
- **Validada:** o motor foi conferido contra o Python e contra uma base com efeito conhecido (ver "Onde a IA errou").

### Limitações

- **Dados simulados:** as conclusões valem para esta base. As recomendações marcadas como teste precisam ser validadas com dados reais.
- **Sem custo, conversão, saves ou tempo de exibição:** ROI não é calculável (a ferramenta já aceita essas colunas).
- **Frequência não mensurável**, porque o creator é inconsistente entre posts. A cadência entra como teste.
- **Audiência com um único rótulo por post**, não a distribuição percentual.
- **Faixas de seguidores desbalanceadas:** cerca de 2,6 mil posts abaixo de 100K, contra 26 mil entre 500K e 1M.

---

## Process Log — Como usei IA

### Ferramentas usadas

| Ferramenta | Para que usou |
|---|---|
| **Claude (Claude.ai, chat)** | Planejamento, desenho do método, interpretação dos resultados, estratégia, relatórios, revisão crítica de cada entrega (inclusive testando a ferramenta num navegador automatizado) e escrita das Ordens de Serviço |
| **Claude Code** | Executor: rodou cada análise a partir de uma Ordem de Serviço curta, sem contexto estratégico, gerou scripts, outputs, gráficos, PDFs e a ferramenta, e validou os próprios números |
| **Claude (chat separado, sem contexto)** | Baseline: o brief e o CSV num único envio, para comparar métodos |

### Workflow

1. **Planejamento no chat:** leitura do repositório, escolha do desafio, identificação do risco de dado sintético, dois cenários previstos e regras de trabalho ("todo número sai de código").
2. **Separação de papéis:** o raciocínio fica no chat; a execução fica no Claude Code, por **Ordens de Serviço** (OS) com regras contra a "espiral de erros" (no máximo 2 tentativas, sem mudar escopo, sem interpretar). Todas as OS estão na [seção 5 do process log](process-log/process-log.md#5-ordens-de-serviço).
3. **Ciclo por OS:** o chat escreve a OS → o Code executa e devolve um resumo → o chat interpreta, critica e decide a próxima. Foram **14 OS**, de OS-01 a OS-11, mais 03b, 03c e 07b.
4. **Análise:**
   - base amostral (OS-01);
   - benchmark (OS-02);
   - patrocínio e validação (OS-03);
   - fit e audiência (OS-03b);
   - robustez (OS-03c);
   - complementos (OS-04);
   - lacunas do brief (OS-06).
5. **Baseline** e confronto: as afirmações do baseline foram verificadas no CSV e as boas práticas foram incorporadas com crédito.
6. **Relatórios:** executivo, com duas partes espelhando o brief, e técnico, com gráficos gerados por código (OS-05) e PDFs (OS-07/07b).
7. **Ferramenta:**
   - núcleo (OS-08);
   - correção do motor + abas + design (OS-09);
   - linguagem para usuário não técnico + tema escuro (OS-10).
8. **Fechamento:** `run_all.py`, organização da pasta, commits e PR (OS-11).

Registro completo no [process log](process-log/process-log.md): [decisões, o porquê](process-log/process-log.md#3-registro-de-decisões-o-porquê) e [execução, o como](process-log/process-log.md#4-log-de-execução-do-claude-code-o-como).

### Onde a IA errou e como corrigi

| Erro | Como foi detectado | Correção |
|---|---|---|
| A regressão "mostrou" +73 shares para vídeo e +67 para patrocínio (p < 0,0001) | Coeficientes grandes demais → checagem de colinearidade (número de condição de 1e16) | Modelo limpo: ~1 share de efeito, R² ≈ 0 |
| A IA criou faixas de "duração de vídeo" sobre `content_length` | A OS-01 mostrou a mesma distribuição para texto e imagem | Análise de duração eliminada; o exemplo do brief ("vídeos de 30–60s") depende de um campo que a base não tem |
| A IA estimou "no máximo ~8 interações a mais por post" | A regra "todo número sai de código" (OS-04) | O valor correto é 2,6 interações. A IA tinha aplicado o pior efeito de comentários ao engajamento total |
| Duas rodadas da mesma OS (dois modelos) na mesma pasta | Números idênticos até no bootstrap | O segundo modelo tinha reaproveitado o script do primeiro. Regra: um modelo por OS |
| 88 de 315 testes de cauda "anormais" | O Claude Code desconfiou do próprio resultado | 86 eram empates em métricas inteiras; corrigido, sobram 6 (abaixo do acaso) |
| **A ferramenta escondia vencedores** | Teste com **efeito conhecido** (vídeo com +30% de likes): a ferramenta mostrou +7,7% e "nenhuma opção melhor" | O segmento passou a ser comparado com o resto, não com a média que o inclui. A ferramenta passou a mostrar +19,6% e "Funcionou melhor" |
| A ferramenta recomendava "1 post por versão" e usava jargão (IC, recorte, segmento) | Revisão da tela lendo como o usuário final | Mínimo de 30 posts, linguagem simples, lista de palavras proibidas verificada por script |

### O que eu adicionei que a IA sozinha não faria

- **"Ainda é cedo para concluir."** Quando a IA já declarava "os dados são ruído", exigi um modelo completo com todas as colunas antes de qualquer conclusão.
- **"Análises isoladas não se somam."** Levantei que "TikTok é melhor + 19–25 é melhor" não garante que "TikTok para 19–25" seja melhor. Isso gerou a etapa de consolidação (preditivo + regressão com controles).
- **A hipótese de fit:** propus que patrocinador alinhado ao conteúdo poderia engajar mais. Foi testada com rigor e não se sustentou. Registro como hipótese rejeitada, não escondida.
- **"Quero 100% de certeza."** Isso levou à OS de robustez (equivalência, poder de detecção, controle positivo), que é o principal diferencial técnico da entrega.
- **O objetivo do baseline:** comparar métodos, não provar que a IA erra. A conclusão coincidir reforça a lógica; o que diferencia é a prova.
- **A ênfase no orgânico**, com a mensagem "cada real pago em patrocínio compra zero engajamento adicional", e a decisão de tirar o custo do time da análise.
- **A ferramenta pensada para o usuário real:** alguém que vai lançar uma campanha, sobe o histórico e precisa de linguagem simples, não de estatística.
- **Separar raciocínio e execução** em dois ambientes, com o Claude Code recebendo só ordens curtas, para evitar desvio de contexto e espiral de erros.

---

## Evidências

- [x] **Process log em um documento único:** [`process-log/process-log.md`](process-log/process-log.md), com a linha do tempo, as decisões, o log de execução do Claude Code, as 15 Ordens de Serviço na íntegra e a exploração inicial
- [x] Chat export: [conversa completa com o Claude (chat)](https://claude.ai/share/8fe74758-e8bc-4805-b801-e5ad447b62c8), em link público
- [x] Baseline original: [`process-log/baseline/`](process-log/baseline/)
- [x] Git history: commits por etapa nesta branch
- [x] Capturas de tela da ferramenta: [`solution/outputs/os08/`](solution/outputs/os08/), [`os09/`](solution/outputs/os09/), [`os10/`](solution/outputs/os10/)

---

## Como rodar

```bash
# na raiz do repositório
pip install -r submissions/gabriel-mata/requirements.txt
# coloque o CSV do Kaggle em: submissions/gabriel-mata/datasets/social_media_dataset.csv
# (ou aponte a variável DATA_PATH para ele)
python submissions/gabriel-mata/solution/analysis/run_all.py
```

Isso reproduz todas as análises (OS-01 a OS-06), os gráficos, a ferramenta e as validações do motor (exige Node.js). Os PDFs são gerados à parte, por `python submissions/gabriel-mata/solution/analysis/os07_pdf.py`, o que exige o Google Chrome.

---

_Submissão enviada em: 13/10/2026_
