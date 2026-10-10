# Revisão inicial do material de partida

Status: **concluída. G1 aprovado e aplicado (09/10/2026), com as duas escolhas finais respondidas pelo Bruno (fim do arquivo).**

## Plano

### 1. O que entendi

- Tudo nesta pasta é rascunho da preparação feita com IA. Isso vale para números, scripts, configuração e documentos. Nada vale até ser conferido.
- A revisão (AGENTS.md, seção 8) tem três partes. Primeiro, recalcular os números de forma independente. Depois, revisar a lógica do score e do backtest. Por fim, revisar código, configuração e documentação. A saída é este arquivo, com a tabela de afirmações e os achados com evidência.
- A crítica vai além dos erros: pergunta se D1–D19, o plano e o score se sustentam, e onde a entrega pode ficar parecida com o baseline.
- D19, a decisão nova, pede uma página que mostra a investigação que sustenta o score. Para cada achado, ela diz o que os dados mostraram, como o número foi conferido e que decisão ele mudou. Ela não pode ser descartável nem ter regra duplicada.
- O enunciado pede software funcionando, com score explicável: "o deliverable principal é software funcionando — não um documento". A banca premia verificação e julgamento e penaliza saída genérica e documento longo.
- O prazo é domingo, 11/10/2026, à noite. A orientação é de 4 a 6 horas, e excesso de escopo é risco real.

### 2. Inventário

Afirmações numéricas dos arquivos da seção 8. Cada ID vira uma linha da tabela da revisão. "dup" marca uma repetição de um número que já tem ID: ela é conferida junto e corrigida em todos os lugares.

| ID | Onde | Afirmação |
|---|---|---|
| N01 | AGENTS.md:48 | 35 vendedores; cerca de 8.800 oportunidades (o enunciado diz "~8.800") |
| N02 | AGENTS.md:49 | `close_value` = 0 em 2.473 de 2.473 perdidos; vazio nos abertos |
| N03 | AGENTS.md:169 | 8.800 negócios; 85 empresas; 7 produtos; 35 vendedores |
| N04 | AGENTS.md:170 | Won 4.238 · Lost 2.473 · Engaging 1.589 · Prospecting 500 |
| N05 | AGENTS.md:171 | "GTXPro" em 1.480 linhas |
| N06 | AGENTS.md:172 | Prospecting não tem nenhuma data |
| N07 | AGENTS.md:173 | 1.425 de 2.089 em andamento sem empresa; 0 concluídos sem empresa |
| N08 | AGENTS.md:175 | datas de 20/10/2016 a 31/12/2017; 1º concluído em 01/03/2017; maior ciclo de 138 dias |
| N09 | AGENTS.md:177 | 5 vendedores sem negócio (5 nomes) |
| N10 | AGENTS.md:178 | em 31/12/2017, 9 dos 30 sem negócio recente: 6 com só parados e prospecção, 3 sem nada aberto |
| N11 | AGENTS.md:186 | qui-quadrado p = 0,264 (vendedor) e 0,372 (produto); 36–38% dos sorteios |
| N12 | AGENTS.md:202–205 | coorte com `engage_date` ≤ T−138; faixas 49,8 · 46,4 · 44,0 · 32,9 · 21,2 · 9,1%; 5.991 negócios; iniciados até 15/08/2017 |
| N13 | AGENTS.md:206 | só concluídos: 68,7% aos 14 dias; 71,1% aos 90 |
| N14 | AGENTS.md:216 | dos 1.589 Engaging: 110 no prazo, 188 esfriando, 1.291 parados |
| N15 | AGENTS.md:217 | preço de lista US$ 3,89 mi, 82% parado; prospecção US$ 1,07 mi |
| N16 | AGENTS.md:218 | valor ponderado ≈ US$ 195 mil |
| N17 | AGENTS.md:224–229 | backtest: 44,41 · 43,35 · 40,10 · 36,17 · 32,23 · 15,40% |
| N18 | AGENTS.md:232 | ML 45,0% vs valor ponderado 44,6% (backtest exploratório) |
| N19 | analise-exploratoria.md:6 | dup N15/N16 (US$ 3,9 mi; US$ 195 mil) |
| N20 | analise-exploratoria.md:10–13 | US$ 227.651 · 465.914 · 3.198.664 ("82% dos negócios com data") · 1.073.986 |
| N21 | analise-exploratoria.md:15–16 | nenhum negócio concluído depois de 138 dias (dup N08) |
| N22 | analise-exploratoria.md:21, 25–31 | dup N12 |
| N23 | analise-exploratoria.md:33 | dup N13 |
| N24 | analise-exploratoria.md:38 | taxa de ganho entre concluídos 63,15%, IC 95% 62,0–64,3% |
| N25 | analise-exploratoria.md:39 | de cada 100 iniciados: 50 ganhos, 29 perdidos, 22 nunca concluídos |
| N26 | analise-exploratoria.md:45–50 | p-valores: vendedor 0,264 · gestor 0,786 · regional 0,604 · produto 0,372 · setor 0,971 · empresa 0,943 |
| N27 | analise-exploratoria.md:52 | melhor − pior vendedor = 15,4 p.p.; 36–38% dos sorteios |
| N28 | analise-exploratoria.md:53 | em valor: 23,5 p.p.; cerca de 41% dos sorteios |
| N29 | analise-exploratoria.md:54 | receita varia 9,3×; Spearman 0,62 (volume) e −0,21 (taxa) |
| N30 | analise-exploratoria.md:61–63 | mês do trimestre: 49,0 · 54,7 · 80,7% |
| N31 | analise-exploratoria.md:70–74 | dup N05, N07 (68%), N06, N09, N10 |
| N32 | analise-exploratoria.md:82–85 | 44,4 · 36,2 · 15,4 · 45,0% (mistura dois backtests, ver P4) |
| N33 | analise-exploratoria.md:87 | dup N18 |
| N34 | como-escalar.md:22, 33 | 8.800; 880 mil = 100×; marcador `medir` |
| N35 | como-escalar.md:55 | três marcadores `medir` (preenchidos no incremento do bench) |
| N36 | como-escalar.md:89 | ganho de 0,4 p.p. (dup N18) |
| N37 | como-escalar.md:105 | 68% dos abertos sem empresa (dup N07) |
| N38 | README.md:15 | 1.589; US$ 3,9 mi; ≈ US$ 195 mil; 82%; 138 dias (dup) |
| N39 | README.md:26 | backtest com seis métodos |
| N40 | solution/analysis/README.md:24, 41 | "21 consultas"; gerado com Python 3.13 e as versões fixadas |
| N41 | docs/plano-e-matriz.md:102 | hook com 10 testes. **Conferido:** `node --test` deu 10 aprovados e 0 falhas |

**Já visto na leitura**: anotado aqui, e só entra como achado depois de reproduzido.

| # | Observação | Evidência |
|---|---|---|
| P1 | O Node local é o 22.23.2; AGENTS §5, CA1 e o README pedem o Node 24 | `node --version` |
| P2 | A skill `frontend-design` não está instalada. O `/plugin` não existe na extensão do VS Code | `installed_plugins.json` sem a entrada; mensagem "/plugin isn't available in this environment" |
| P3 | O `SHA256SUMS` foi gerado na preparação. O `-c` passa, mas prova só que nada mudou desde então; a origem fica sem prova. **Resolvido em 09/10:** o Bruno baixou o zip do Kaggle (`archive.zip`, 145.926 bytes, SHA-256 `74d53582…7a87a9c`), com 5 arquivos datados de 14/04/2024. Extraído numa pasta vazia do scratchpad, `shasum -a 256 -c SHA256SUMS` deu OK nos 5, e `cmp` deu idêntico byte a byte nos 5. Os arquivos de `solution/data/` são os originais do Kaggle. Limite: o download foi feito pelo Bruno; não conferi a URL | `shasum`, `cmp` |
| P4 | A tabela da seção 7 da análise põe o 44,4% do backtest de referência ao lado do 45,0% do exploratório. No exploratório, o mesmo método deu 44,6% | analise-exploratoria.md:82–87 |
| P5 | "82% dos negócios com data": pela tabela, 82% parece ser fração do **valor**, não dos negócios | analise-exploratoria.md:12 |
| P6 | A D18 só existe em `decisoes.md`, porque o AGENTS §7 vai até a D17. A D12 tem redação diferente nos dois arquivos. A D19 ainda não está escrita em lugar nenhum | decisoes.md:24, 29; AGENTS.md:194 |
| P7 | O benchmark promete "chance em faixas (alta, média, baixa)", e nenhuma decisão prevê isso | benchmark-ux.md:25 |
| P8 | O setor "technolgy" está grafado errado em `accounts.csv` e não aparece na lista de qualidade | accounts.csv:2 |
| P9 | As saídas Python foram geradas no 3.13; o local é o 3.12.4, e os pacotes não estão instalados | `python3 --version` |
| P10 | O como-escalar §1 diz que descreve "o que existe e foi medido", mas cita como prova "o seletor de data mostra a curva mudando", que ainda não existe | como-escalar.md:9, 32 |
| P11 | Os CSVs de dados não têm aspas, o que dispensa biblioteca de CSV. Só o `metadata.csv` tem 2 linhas com aspas | `grep -c '"'` |
| P12 | O AGENTS §2.2 omite a dica "tamanho da conta" do enunciado, e nenhum documento testa `revenue` nem `employees` (achado do critico, conferido) | enunciado:96; AGENTS.md:66–71 |
| P13 | O AGENTS:231 e o CA7 mandam o TS "reproduzir" os números do Python, que são justamente o que esta revisão audita | AGENTS.md:231; plano-e-matriz.md:25, 45 |

### 3. Método por frente

**Independência.** O recálculo é a primeira versão do núcleo do app, em TypeScript (`solution/src/core/`). Ele é escrito a partir das definições pré-registradas abaixo e dos CSVs crus, com testes. Antes do commit C1, não abro nada de `solution/analysis/*.py` nem de `solution/analysis/saidas/`. Até agora não abri, e o critico também não. A ordem fica provada no git: o C1 vem antes de qualquer leitura do Python, e o export da sessão mostra a sequência.

Dois limites honestos:
1. O Python e as definições do AGENTS saíram da mesma preparação. A independência é de **implementação**, não de conceito. O conceito é conferido nas hipóteses H1–H11 e pelo critico.
2. O AGENTS.md é carregado em toda sessão, então os valores-alvo já estão no meu contexto. A proteção contra "ajustar até bater" é o pré-registro:
   - as definições são escritas antes do código;
   - a tabela da revisão guarda duas colunas: "recalculado (C1)", que nunca é editada depois do C1, e "reconciliado", em que cada mudança feita depois de ler o Python traz o motivo.

**Definições pré-registradas.** Quando o texto de partida é ambíguo, marco a escolha com ⚑ e calculo também a alternativa como sensibilidade.

| Item | Definição |
|---|---|
| Datas e idade | Dias corridos. Idade em T = T − `engage_date`. |
| Estado em T | Existe em T quem tem `engage_date` ≤ T. Concluído em T: `close_date` ≤ T, com desfecho Won ou Lost. Aberto em T: existe e não está concluído. Prospecting não tem datas: entra só em T = 31/12/2017, na lista "Inicie contato". |
| Duração observada em T | min(`close_date`, T) − `engage_date`. Nunca lê data posterior a T. Maior ciclo em T = maior duração entre os concluídos até T. |
| Coorte em T | Não-Prospecting com `engage_date` ≤ T − 138. Ganho = Won com `close_date` ≤ T. Quem não ganhou até T (perdido ou aberto) conta como "não ganhou". |
| Em risco na faixa b | Na coorte, ⚑ duração observada em T ≥ b. Alternativa: > b. |
| Corte de 138 | ⚑ Fixo em 138, como pede o AGENTS. Alternativa calculada: o maior ciclo observado em cada T (H2, H11). |
| Chance(b) | ganhos em risco em b ÷ em risco em b, com b ∈ {0, 30, 60, 90, 104, 120}. |
| Faixa do negócio | É a do maior b ≤ idade. Idade ≤ 138 → faixa 120–138 (138 ainda é "Esfriando"). Idade 139 ou mais → parado, chance 0. |
| "Só concluídos" (o cálculo errado) | ⚑ Entre os concluídos até T com ciclo ≥ b: Won ÷ (Won + Lost), para b = 14 e b = 90. |
| Valor | Preço de lista do produto, com "GTXPro" → "GTX Pro". Valor ponderado = chance(faixa) × preço. |
| Situação em 31/12 | No prazo: 0–89 dias. Esfriando: 90–138. Parado: mais de 138. "Sem negócio recente": nenhum aberto com idade ≤ 138. |
| Ordem das listas | "Foque agora": valor ponderado decrescente, depois `opportunity_id`. ⚑ "Revisar ou encerrar": preço decrescente, depois idade decrescente, depois `opportunity_id` (o AGENTS não define essa ordem; vai ao G1). "Inicie contato": preço decrescente, depois `opportunity_id`. |
| Backtest | Fotos em T ∈ {30/06, 31/07, 31/08, 30/09/2017}. Em cada T, a curva vem da coorte **de T**. Candidatos: abertos em T. Ranking por vendedor; os 10 primeiros, ou todos se houver menos de 10. Janela do desfecho: (T, T+90]. ⚑ Denominador: soma de `close_value` dos candidatos ganhos na janela, de todos os vendedores. Agregação: soma global sobre as 4 datas ÷ soma global dos denominadores. Desempate: score decrescente, depois `opportunity_id` crescente (ordem de texto). |
| Métodos | (1) Valor ponderado. (2) ⚑ "Faixas e preço": chance da faixa, decrescente, e depois preço. (3) "Preço sem parados": os não parados por preço; depois os parados, na ordem da lista "Revisar ou encerrar". (4) Só preço. (5) Chance "só concluídos" × preço. (6) Aleatório pela esperança exata: Σ min(1, 10/n)·receita, por vendedor e data. |
| Teste pareado | Entre dois métodos **do mesmo backtest**. Bootstrap por **vendedor**: 10.000 reamostragens com semente fixa; cada vendedor leva as 4 datas; em cada reamostra, a razão das somas é recalculada → IC 95% da diferença. Troca de sinais: inverte a diferença em US$ de cada vendedor (soma das 4 datas), com o denominador fixo → p-valor. |
| Qui-quadrado | Concluídos em 31/12; tabela grupo × (Won, Lost); g.l. = k − 1. Empresa: só negócios com empresa. Repetido também no desfecho da coorte (H5). |
| Embaralhamento | Permuta Won/Lost entre concluídos; estatística = maior − menor taxa por vendedor; % de sorteios ≥ observado; 10.000 sorteios, semente fixa. ⚑ "Em valor": Σ preço dos ganhos ÷ Σ preço dos concluídos, por vendedor. |
| Outros | IC da taxa de ganho por Wilson (⚑; a aproximação normal entra também). "De cada 100": divisão da coorte de 31/12 em ganho, perdido e aberto. Trimestre: concluídos pelo mês do `close_date` dentro do trimestre. ⚑ Receita por vendedor = Σ `close_value`; volume = nº de concluídos. |

| Frente | O que | Como | Quem | Saída | Pronto quando |
|---|---|---|---|---|---|
| **Regras** | AGENTS §2 contra os 5 arquivos oficiais | O critico compara. P12 já confirmado | critico | achados com trecho citado | todo item do §2 tem fonte, ou foi corrigido |
| **Dados** | Origem dos CSVs; N01–N10 | (a) origem: hash dos CSVs do zip do Kaggle (pergunta 1); (b) contagens e qualidade no núcleo, com testes; (c) aspas, colunas por linha, chaves sem par entre as tabelas, setor grafado errado | orquestrador | linhas N01–N10 | cada linha com valor recalculado e status |
| **Números** | N11–N38 | Funções do núcleo com testes. `npm run auditoria` imprime "declarado · recalculado" e grava a saída num arquivo versionado. Estatística escrita à mão: CDF do qui-quadrado testada contra valores tabelados (3,841 com 1 g.l. → p = 0,05), embaralhamento e bootstrap com semente fixa, Spearman, IC de Wilson | orquestrador | tabela; commit C1 | toda afirmação com "recalculado (C1)" |
| **Lógica** | coorte, faixas, 138, backtest, desempate, aleatório | Testes com dados pequenos calculados à mão: 138 e 139 dias; aberto em T conta como "não ganhou"; anti-vazamento (mudar o futuro não muda T); desempate; esperança do aleatório. Hipóteses H1–H11 | orquestrador, critico | achados de lógica | cada hipótese com resultado e evidência |
| **Comparação com o Python** | os 4 scripts e as saídas | Só depois do C1: rodar num `.venv` (pergunta 2), comparar número a número e procurar vazamento | orquestrador, revisor | coluna "reconciliado" | divergências explicadas ou registradas |
| **ML** | 45,0 vs 44,6 | Abaixo | orquestrador | nota com fonte Python | idem |
| **Código e configuração** | Python, hook e testes, `adicionar-ao-git.sh`, `settings.json`, agentes, `.gitignore` | Checklist do revisor, que começa **só depois do C1** | revisor | até 10 achados | cada um reproduzido, ou descartado com motivo |
| **Documentação** | todos os `.md` | Contradições, número sem fonte, vocabulário fora do §10, referência quebrada, dados pessoais ou corporativos; P4–P7, P10, P12, P13 | revisor | achados | idem |
| **Crítica** | D1–D19, plano, score, risco de baseline | O critico recebe o recálculo na revisão. Eu escrevo a crítica final, com recomendações em ordem de prioridade | critico, orquestrador | seção "Crítica" | cada recomendação diz o que mudar, por quê e a evidência |

**Hipóteses** (podem virar achado ou cair):
- **H1: viés de desenho.** As faixas e os cortes de 90 e 138 dias parecem escolhidos olhando todos os dados, inclusive o período do backtest. Teste: backtest com faixas fixadas antes (de 30 em 30 dias) e com chance por dia exato. Se der igual, as faixas não importam. Se cair, a tabela da seção 7 está otimista.
- **H2: o backtest é point-in-time?** Em cada foto, curva, coorte e corte usam só o que se sabia em T. Também mostro o maior ciclo observável em cada T, contra os 138 fixos.
- **H3: o ganho do valor ponderado é real?** Teste pareado contra "preço sem parados" e contra "faixas e preço". Se não for significativo, a mensagem principal vira **a triagem** (82% do valor está parado), e o valor ponderado fica pela explicação.
- **H4: a métrica dos 10 primeiros discrimina?** Distribuição de abertos por vendedor e data. Com 10 ou menos, todos os métodos empatam.
- **H5: o teste de vendedor e produto mede o desfecho certo?** Repetir no desfecho da coorte, onde aberto conta como "não ganhou".
- **H6: preço de lista vale como valor?** Comparar `close_value` dos ganhos com o preço de lista.
- **H7: os dados são sintéticos?** O ciclo máximo é o mesmo para ganhos e perdidos, nenhuma variável explica o desfecho, nada conclui depois de 138 dias. Se confirmar, isso entra nas limitações e muda o tom: vendemos o método que se recalibra, não a curva.
- **H8: a frase "de cada 10" é grossa demais?** Os 49,8% e os 46,4% viram os dois "5 de cada 10".
- **H9: o tamanho da conta importa?** Taxa de ganho por faixa de `revenue` e de `employees` (quartis), entre concluídos e na coorte, com qui-quadrado. Registrar também quantos negócios em andamento ficam sem esses campos (N07).
- **H11: a base está cortada no início?** Nenhum negócio conclui antes de 01/03/2017, mas 358 linhas têm `engage_date` em 2016 e 827 em jan–fev de 2017. Conferido com `grep -c`, a pedido do critico. Teste: maior ciclo e curva só com negócios iniciados a partir de 01/03/2017; backtest refeito sem as fotos de 30/06 e 31/07, cuja coorte vai até 12/02 e 15/03. Se o 138 ou a curva mudarem, isso entra nas limitações e na regra do CA6 sobre datas sem histórico suficiente.
- **H10: na prática, a "Foque agora" é a ordem por preço?** Em 31/12, por vendedor, comparar a sobreposição dos 10 primeiros por valor ponderado e por preço. Isso alimenta a crítica do produto: ordem de "Revisar ou encerrar", custo de esperar, % parada por vendedor na visão do gestor.

**ML (N18), proporcional à decisão.** A regra fica registrada antes de rodar: o ML só entra se o IC 95% excluir zero **e** o ganho for de pelo menos 2 p.p. O ganho declarado é de 0,4 p.p., então ele precisaria ser quase 5 vezes maior.
1. Ler `backtest_exploratorio.py` depois do C1 e procurar vazamento.
2. Rodar com 5 sementes e desempate pelo ID, para medir quanto ele varia sozinho.
3. Exportar num CSV, por (vendedor, data), a receita capturada pelo ML **e pelo valor ponderado do próprio exploratório**, com o denominador. Os dois backtests não são montados do mesmo jeito (44,41 contra 44,6), então o pareamento é só entre essas duas colunas, no mesmo teste pareado em TS da H3.

Resposta esperada: o p-valor e o IC, mesmo que a decisão não mude. Na página, o 45,0% aparece como nota, com fonte Python, fora do CA16.

**Origem dos dados.** O Kaggle exige login. Com o zip baixado pelo Bruno, comparo os hashes. Se forem diferentes, comparo o conteúdo linha a linha, porque fim de linha diferente basta para mudar o hash. Sem o zip, registro a origem como "não verificada".

### 4. Interface exploratória (D19)

**Onde fica.** No mesmo app (`solution/`), na página "Como funciona" (`#/como-funciona`). Proponho uma página só, em vez de uma exploratória separada da "Como funciona" do CA8:
- **Camada de cima**, que cabe numa tela, para o vendedor e para a Head de RevOps: a fórmula, a frase, as três listas e o que fica de fora.
- **Camada de baixo**, recolhida por padrão: a investigação.

**Código compartilhado.** A interface e o recálculo usam as mesmas funções de `src/core/`, e a UI só formata. A independência vem de comparar o núcleo TS com o Python e com dados pequenos calculados à mão, não de separar revisão e interface. Uma interface com código próprio seria uma terceira cópia da regra, livre para divergir do que foi verificado.

**Seções da investigação.** Cada uma traz: "O que os dados mostraram", "Como conferimos", "Que decisão mudou", gráfico e tabela.

| # | Seção | Mostra | Achado / decisão |
|---|---|---|---|
| S1 | Os dados | negócios por etapa; concluídos por mês; tabela de problemas, com a % sem empresa por etapa | período; 1º concluído em 01/03/2017; "sem empresa" vaza o desfecho; normalização de "GTXPro"; prospecção sem data → D13; vendedores sem negócio → estados vazios |
| S2 | A chance cai com a idade | linha com 2 séries (coorte × só concluídos) + tabela por faixa (em risco, ganhos, chance) | viés de sobrevivência evitado → D5, D2 |
| S3 | O que não muda a taxa de ganho | seletor de dimensão: vendedor, gestor, regional, produto, setor, empresa, receita e funcionários da empresa. Taxa por grupo com n, p do qui-quadrado e % do embaralhamento, calculado só para a dimensão escolhida. Um parágrafo sobre o mês do trimestre | D3; o calendário fica fora do score |
| S4 | Como validamos | receita capturada por método (total e por data), IC das diferenças e nota sobre o ML | D5 contra as alternativas; sem ML |

**Fica de fora:**
- o funil por situação, porque a barra de números do app já mostra;
- o funil por vendedor, que é tela do gestor;
- seletor de data na página;
- curva ao longo do tempo;
- filtros e exportação.

O `docs/analise-exploratoria.md` encolhe para um texto curto que aponta para a página e para a saída versionada de `npm run auditoria`, a única fonte dos números.

**Stack.** As versões são conferidas com `npm view` na instalação.

| Dependência | Por quê |
|---|---|
| react, react-dom | D8 |
| vite, @vitejs/plugin-react | D8. Site estático; o CSV entra no bundle por import `?raw`, então não há rede (CA9) |
| typescript | D8, modo estrito |
| vitest | testes do núcleo; usa a configuração do Vite |
| @biomejs/biome | lint e formatação (CA10) |
| @playwright/test | e2e e prints. Entra só quando a interface começar |

**Sem dependência para:**
- gráficos: barras em CSS dentro da tabela e uma linha em SVG;
- rotas: troca por `location.hash`;
- CSV: os dados não têm aspas, e um teste garante isso;
- estatística: escrita à mão, com testes;
- fonte: a do sistema.

Na execução, uso as skills `frontend-design` (briefing do CLAUDE.md) e `dataviz`.

**CA16, proposto para `docs/plano-e-matriz.md`:**

> Página "Como funciona" (D19): a camada de cima explica a regra numa tela; a de baixo traz S1–S4. Cada seção diz o que os dados mostraram, como foi conferido e que decisão mudou. Todo gráfico tem tabela. Todo número vem de função de `src/core` coberta por teste; `src/ui` não calcula. A exceção é a nota do ML, marcada como fonte Python. Sem rede. Legível em 1280 e em 390 px.

**Verificação:**
- Vitest nas funções;
- um e2e que confere se a página mostra os números que o núcleo devolve (5.991, as 6 chances, os 6 métodos);
- revisor: nenhum número literal nem conta em `src/ui`;
- testador-de-uso com a persona Head de RevOps, com prints em 1280 e 390 px em `process-log/screenshots/02-app/`.

### 5. Sequência, portões e commits

| Passo | O que | Commit |
|---|---|---|
| **G0** | Bruno aprova o plano. Registro a D19 em `decisoes.md` e o CA16 no plano | — |
| 1 | Estrutura mínima: `package.json`, TS, Vitest, Biome (instalação com aprovação) | — |
| 2 | Núcleo e recálculo, testes primeiro, sem abrir o Python. Critico em paralelo: regras e as decisões D1–D19 | **C1** `feat: núcleo e recálculo independente` |
| 3 | Abrir o Python e comparar; teste pareado (H3, ML). Revisor em paralelo | — |
| 4 | Reproduzir os achados, preencher este arquivo e `erros-da-ia.md`, corrigir os docs. AGENTS, CLAUDE e o CA7 ficam como proposta para o G1 | **C2** `fix: correções da revisão inicial` |
| **G1** | Resumo para o Bruno; ok nas mudanças de D1–D19 e do CA7 | — |
| 5 | Página "Como funciona" (D19), com limite: sábado ao meio-dia | — |
| 6 | Revisor e testador-de-uso com prints; correções | **C3** `feat: página Como funciona com a investigação (D19)` |
| **G2** | Ok do Bruno antes do incremento 4 (telas do vendedor e do gestor). Se ele aprovar o incremento 4 já no G1, o G2 vira só informativo, e o incremento 4 começa no sábado ao meio-dia de qualquer jeito | — |

Antes de cada commit: `npm run check` verde e `sh tools/adicionar-ao-git.sh`. O C1 é uma proposta minha além do pedido: ele prova no git que o recálculo veio antes da leitura do Python. Ele também leva a edição do LinkedIn que já está pendente no README.

### 6. Agenda e cortes

Os passos 1–2 absorvem o incremento 1 e a maior parte dos incrementos 2 e 3 (curva, valor ponderado, backtest em TS). A página D19 absorve o incremento 5.

| Dia | Plano original | Novo |
|---|---|---|
| Sex 09/10 | incrementos 0, 0b | G0 → passos 1–4 → G1 |
| Sáb 10/10 | incrementos 1–5 | passos 5–6 até o meio-dia → G2 → incremento 4 (listas, filtros, painel de motivo, estados vazios) |
| Dom 11/10 | incrementos 6–8 | fim do incremento 4, deploy, README, process log, banca, PR |

**Cortes:**
- **Já agora:** o seletor de data (D1) oferece só as 4 datas do backtest e 31/12/2017.
- **Se apertar, nesta ordem:**
  1. O segundo adaptador JSON vira um teste com dados de exemplo (muda o CA10).
  2. O `bench` e os números medidos do CA15. O documento continua, sem os números, porque o enunciado pede "o que precisaria pra escalar", não medição.
  3. Na S3, só vendedor, produto e tamanho da conta.
  4. No celular, o layout vira uma lista simples.

**Não pode ser cortado:**
- CA0–CA5, CA7, CA11–CA13;
- o texto do CA15;
- no CA16, as seções S2 e S4.

**Limite da D19:** se a página não chegar ao G2 no sábado ao meio-dia, ela fica como está, e o incremento 4 começa. O restante volta depois, se sobrar tempo.

### 7. Riscos

| Risco | Sinal precoce | Resposta |
|---|---|---|
| Ajustar a interpretação até bater com o Python | mudança de definição depois do C1 | definições pré-registradas; coluna C1 congelada; cada reconciliação com motivo |
| O recálculo vira um poço de tempo | as contagens ou a coorte divergem logo no passo 2 | uma tentativa de diagnóstico por divergência; depois, registrar "declarado · recalculado · causa provável" e seguir |
| A D19 empurra a tela principal | a página não fica pronta no sábado ao meio-dia | o limite da seção 6; a tela do vendedor é o entregável principal |
| A independência é contaminada | relato de agente citando conta do Python antes do C1 | revisor só depois do C1; o critico não abre o `.py` |
| Node 22 local contra Node 24 exigido | confirmado (P1) | pergunta 3 |
| A `frontend-design` não está instalada | confirmado (P2) | pergunta 4, antes do passo 5 |
| Aprovações de `npm` e `pip` travam o trabalho | um pedido de permissão parado | pergunta 2 |
| Dados da empresa em exports e prints (o contexto da sessão tem e-mail corporativo) | `grep` do domínio antes de versionar | o revisor checa; o Bruno decide |
| O `/export` pode não existir na extensão, como o `/plugin` | testar no fim desta sessão | converter o transcript JSONL de `~/.claude/projects/`, com cobertura de dados pessoais |
| O embaralhamento fica lento no navegador | a S3 demora mais de 300 ms | menos sorteios com semente fixa, ou um Web Worker |
| Os dados são sintéticos (H7) | indícios na H7 | dizer nas limitações; vender o método |
| A conversa é compactada e perde estado | — | este arquivo é atualizado a cada passo |

### 8. Parecer do critico e o que fiz com cada achado

Rodada 1. Veredito do critico: "ajustar e seguir". Ele confirmou que não abriu os `.py` nem as saídas.

| # | Achado | Decisão | O que mudou |
|---|---|---|---|
| 1 | [BLOQUEANTE] A D19 vem antes da tela do vendedor, que é o entregável principal | **Aceito em parte.** A ordem D19 → G2 → incremento 4 foi pedida pelo Bruno, e com o núcleo pronto no C1 a página é pequena. O risco é real, então ele vira limite e corte. A inversão fica como pergunta 5 | limite no sábado ao meio-dia; seletor de data cortado já; adaptador JSON e `bench` entram na lista de cortes |
| 2 | [IMPORTANTE] Não há definições pré-registradas, e os alvos já estão no contexto | **Aceito** | bloco "Definições pré-registradas" com ⚑ nas ambiguidades; colunas "recalculado (C1)" e "reconciliado" |
| 3 | [IMPORTANTE] "Tamanho da conta" sumiu do resumo e das hipóteses | **Aceito.** Reproduzido: enunciado:96 contra AGENTS.md:66–71 | P12, H9, `revenue` e `employees` na S3; a correção do AGENTS §2.2 vai ao G1 |
| 4 | [IMPORTANTE] O CA7 manda reproduzir o Python auditado | **Aceito** | P13; a proposta de mudar o CA7 e o AGENTS:231 para "tabela reconciliada" vai ao G1 |
| 5 | [IMPORTANTE] A regra de 2 p.p. já decide o ML; o IC na página quebra o CA16 | **Aceito em parte.** O Bruno perguntou se a diferença é significativa, então a pergunta ainda merece resposta, mas barata | o teste pareado é em TS (serve à H3); o Python só exporta a receita por vendedor e data, com 5 sementes; o ML aparece como nota com fonte Python |
| 6 | [IMPORTANTE] Sete seções contrariam "simples"; o doc vira uma segunda fonte | **Aceito** | 4 seções; a S5 sai; o trimestre vira parágrafo; a investigação fica recolhida; o doc aponta para a saída da `auditoria` |
| 7 | [IMPORTANTE] O process log não tem a leitura do Bruno; o erro da preparação fica invisível | **Aceito como pergunta.** Mexe na D17 e na autoria do Bruno, então a decisão é dele | perguntas 6 e 7 |
| 8 | [IMPORTANTE] Lacunas de produto podem deixar a entrega parecida com o baseline | **Aceito como entrada da crítica.** São do incremento 4, não desta revisão | H10; a ordem de "Revisar ou encerrar", o custo de esperar e a % parada por vendedor vão para a crítica e para o G1 |

Rodada 2, a última. Veredito do critico: "ajustar e seguir". Ele confirmou que as definições de estado em T, coorte, borda de 138, denominador, aleatório e desempate estão coerentes com o AGENTS §6–7.

| # | Achado | Decisão | O que mudou |
|---|---|---|---|
| 9 | [IMPORTANTE] A base pode estar cortada no início: nada conclui antes de 01/03/2017 | **Aceito.** Reproduzido: `grep -c` deu 358 linhas de 2016 e 827 de jan–fev de 2017 | H11; o corte de 138 ganha ⚑ e uma alternativa calculada |
| 10 | [IMPORTANTE] O teste pareado do ML misturava dois backtests | **Aceito** | o CSV do Python traz o ML e o valor ponderado do próprio exploratório |
| 11 | [IMPORTANTE] A ordem de "Revisar ou encerrar" e do método 3 não estava pré-registrada | **Aceito** | linha "Ordem das listas" com ⚑; a pergunta vai ao G1 |
| 12 | [IMPORTANTE] O pedido da ordem D19 → incremento 4 estava sem fonte; o G2 pode travar o sábado | **Aceito em parte.** A fonte existe: é a mensagem do Bruno nesta sessão, na parte "Sequência e portões", que o critico não vê. Ela vai citada em `decisoes.md` junto com a D19. O risco de trava é real | G2 informativo se o incremento 4 for aprovado no G1; o embaralhamento só calcula a dimensão escolhida |
| 13 | [SUGESTÃO] A definição de "em risco" lia o futuro | **Aceito** | "duração observada em T" |
| 14 | [SUGESTÃO] Perguntas bloqueantes mal classificadas | **Aceito** | só as perguntas 1 e 2 bloqueiam o início |

### 9. Decisões que preciso do Bruno

**Bloqueiam o início:**

| # | Pergunta | Recomendação |
|---|---|---|
| 1 | Aprova as instalações? `npm install` das dependências da seção 4 (o Playwright só no passo 5) e `pip install -r requirements.txt` num `.venv` em `solution/analysis/` (já ignorado pelo git) | **Sim, todas de uma vez** |
| 2 | Node 22 (o instalado) ou Node 24 (o que o AGENTS pede)? | **Node 22**, com `engines: ">=22"`, testado no 22. A Vercel aceita os dois. A mudança no AGENTS §5, no CA1 e no README vai no C2. Se preferir o 24, você o instala |

**Até o G1:**

| # | Pergunta | Recomendação |
|---|---|---|
| 3 | ~~Você baixa o zip do Kaggle?~~ **Resolvido em 09/10:** os 5 CSVs são idênticos byte a byte aos do zip (ver P3) | — |
| 4 | ~~Instalar a `frontend-design`~~ **Resolvido em 09/10:** o Bruno escolheu, pelo `/update-config`, habilitar o plugin em `~/.claude/settings.json` (`enabledPlugins`). Ele já está no marketplace oficial registrado. Vale a partir de uma sessão nova; confirmar com `/skills` antes do passo 5 | — |
| 5 | A ordem fica D19 → incremento 4, como você pediu, ou se inverte, como sugere o critico? | **Manter a sua ordem**, com o limite do sábado ao meio-dia e a pergunta 6 |
| 6 | Você aprova o incremento 4 já no G1, para ele começar no sábado ao meio-dia mesmo sem o G2? | **Sim.** Assim a tela principal não espera por aprovação |
| 7 | Qual a ordem da lista "Revisar ou encerrar"? | Preço decrescente, depois idade, depois ID (pré-registrado com ⚑) |
| 8 | Você escreve de 10 a 15 linhas com a sua leitura do problema, para o process log? | **Sim.** É a evidência de "entendeu antes de executar" com a sua voz |
| 9 | O viés de sobrevivência da preparação entra em `erros-da-ia.md`? Isso flexibiliza a D17 | **Sim**, como "erro da preparação, reproduzido na revisão". Eu reproduzo o número errado e o efeito dele no backtest; quem percebeu na preparação você preenche, porque eu não sei |

## Aprovação do plano (G0, 09/10/2026)

O Bruno aprovou o plano com ajustes. Eles estão registrados em `decisoes.md`, de D19 a D26. Os ajustes que mudam este plano:
- **Ordem:** revisão → G1 → incremento 4 (telas do vendedor e do gestor, já aprovado) → portão visual com prints → incremento 5, a página "Como funciona" (D19). A tela do vendedor não pode ser cortada; a página pode.
- **S3:** inclui o mês do trimestre, como "muda a taxa de ganho, mas não serve para o score".
- **D1:** o seletor de data fica com 31/12/2017 e as 4 datas do backtest.
- **CA7 (D22):** TypeScript e Python precisam concordar; se divergirem, a revisão decide qual está certo e registra o motivo.
- **D23:** cada função estatística escrita à mão é testada contra o scipy, com tolerância definida.
- **Node 22 ou superior (D20):** a mudança no AGENTS §5, no CA1 e no Setup do README vai no C2.
- **Ordem de "Revisar ou encerrar" (D21):** preço, depois idade (mais antigo primeiro), depois ID.
- **Erro da preparação (D24):** o viés de sobrevivência entra em `erros-da-ia.md`; quem percebeu, o Bruno preenche.
- **Leitura do problema:** fica em `00-leitura-do-problema.md`. É do Bruno, não é editado pelo agente e terá commit próprio.
- **Interface (ajuste da D12):** gráfico só em três lugares, validador de paleta da `dataviz` e portão visual antes de fechar o incremento 4.

## Recálculo independente (C1)

**Como.** O núcleo foi escrito em TypeScript (`solution/src/core/`) a partir das definições pré-registradas e dos CSVs crus. Até este commit, nenhum arquivo de `solution/analysis/*.py` nem de `solution/analysis/saidas/` (as saídas da preparação) foi aberto; a listagem da pasta mostrou só os nomes. `npm run auditoria` grava `solution/analysis/saidas/auditoria-ts.md`. A versão desse arquivo no commit C1 é a coluna **"recalculado (C1)"** e não é mais editada.

**Dependências instaladas.** Versões conferidas com `npm view` em 09/10/2026, só no projeto, como `devDependencies` exatas: typescript 7.0.2, vitest 5.0.3, @biomejs/biome 2.5.15 e @types/node 22.20.5. `npm install` reportou 0 vulnerabilidades. Do lado Python, foi criado o `.venv` (ignorado pelo git) com o `requirements.txt` da preparação: scipy 1.18.1, numpy 2.5.3, pandas 3.0.5, no Python 3.12.4.

**Testes.** `npm run check` passa: tipos, Biome e 30 testes. Eles cobrem:
- **casos pequenos calculados à mão:** coorte, "em risco", bordas de 89, 90, 138 e 139 dias, anti-vazamento (mudar o que acontece depois de T não muda nada em T), desempate, ordem das três listas, D13 e a esperança do aleatório;
- **dados:** SHA-256 dos 5 CSVs e ausência de aspas;
- **estatística contra o scipy 1.18.1 (D23):** a referência vem de `solution/analysis/referencia_scipy.py`. As tolerâncias foram definidas antes de rodar:
  - contas determinísticas, 1e-12 absoluto + 1e-9 relativo: cauda do qui-quadrado em 35 pontos, qui-quadrado nas 17 tabelas reais, Wilson e Spearman. Passaram todas;
  - Monte Carlo, com 10.000 sorteios de cada lado: fração do embaralhamento ±0,02 (nosso 0,3811 contra 0,3777 do scipy); limites do IC do bootstrap ±0,5 p.p. (maior distância: 0,24 p.p.); p da troca de sinais ±0,02.

Um erro meu apareceu no caminho. No teste das listas, a minha conta à mão esqueceu que os negócios parados também entram na coorte: escrevi 2/4 onde o certo era 2/7. Corrigi o caso antes de rodar; o código não precisou mudar.

**Resultado (C1).** De 40 linhas da auditoria, **32 conferem, 6 divergem e 2 estão pendentes**: N18 e N40 dependem de ler o Python. *Correção feita depois, achado 7 do revisor:* a auditoria do C1 aceitava ±US$ 5 mil no N16 sem regra pré-registrada, e a tabela abaixo já o marcava como divergente. Com a regra única (ver "Tolerâncias"), o C1 fica em **31 conferem, 7 divergem e 2 pendentes**. A tabela completa está em `solution/analysis/saidas/auditoria-ts.md`.

| ID | Declarado | Recalculado (C1) | Observação, antes de ler o Python |
|---|---|---|---|
| N12 | 49,8 · 46,4 · 44,0 · 32,9 · 21,2 · 9,1 | 49,8 · 46,4 · 44,2 · 33,6 · 22,1 · 9,9 | Com "em risco" = duração **>** b, que era a alternativa ⚑, os 6 valores batem exatamente |
| N13 | 68,7% · 71,1% | 68,6% · 71,3% | Com >, 68,66% · 71,13%: bate |
| N16 | ≈ US$ 195 mil | US$ 199.308 | Com >, US$ 195.380: bate |
| N17 | valor ponderado 44,41% | 44,25% | Com >, 44,41%: bate |
| N17 | faixas e preço 43,35% | 32,69% | A minha definição ⚑ (chance da faixa, depois preço) não é a da preparação. A definição certa só se sabe lendo o Python |
| N17 | chance só com concluídos 32,23% | 38,08% | Escolhi chance 0 para os parados nesse método, e talvez a preparação não tenha zerado. A confirmar no Python |
| N20 | "82% dos negócios com data" | 81,2% dos negócios; 82,2% do valor | Confirma o P5: os 82% são do **valor**, não dos negócios. Erro de redação |

**A minha definição pré-registrada (≥) estava errada, e a da preparação (>) está certa.** O motivo: um negócio aberto em T com idade *a* tem `close_date` > T = início + *a*, ou seja, duração **> a**. Quem concluiu exatamente no dia *b* já não é comparável a um negócio que, com idade *b*, ainda está aberto. Isso veio da divergência, mas a justificativa não depende do número. Na reconciliação (C2), o padrão passa a ser ">", com este motivo. A coluna C1 fica como está.

**Sinais para a revisão.** Ainda não são conclusões; serão conferidos no passo 3 e discutidos na crítica.
- **H3:** o ganho do valor ponderado é real. Contra "preço sem parados", ele ganha 4,15 p.p. (IC 95% de 1,97 a 6,82; p = 0,0006). Contra "só preço", ganha 8,08 p.p. (IC de 4,55 a 12,33).
- **H4:** a métrica discrimina. Em cada foto, todos os 30 vendedores têm entre 17 e 166 negócios abertos, e nenhum tem 10 ou menos.
- **H1:** as faixas importam pouco. Faixas de 30 dias dão 43,81%; chance por dia exato, 44,63%; as faixas do AGENTS, 44,25%.
- **H2:** o maior ciclo observado já é 138 nas 4 fotos, então o corte fixo não usa o futuro.
- **H11: a base está cortada no início.** Inícios por mês: 7 (out/16), 115, 236, 312, 515, depois cerca de 800/mês. Nenhuma conclusão antes de 01/03/2017. Ou seja, só aparecem negócios concluídos a partir de março ou ainda abertos. Entre os iniciados a partir de 01/03, o maior ciclo continua 138, mas a curva é mais baixa: 47,3 · 41,6 · 38,8 · 26,1 · 14,1 · 4,9%. A variante de backtest "curva só desde 01/03" (36,02%) **não vale como evidência**: nas fotos de 30/06 e 31/07, a coorte fica vazia, e a ordem cai no ID.
- **H5: vendedor, gestor e regional têm p < 0,01 no desfecho da coorte.** A diferença está na fração que fica aberta para sempre (de 0% a 31% por vendedor), não na taxa entre concluídos (de 55% a 71%). Um fator só do vendedor multiplica todos os negócios dele pelo mesmo número e não muda a ordem da lista que ele vê. Mudaria o nível do valor ponderado na visão do gestor. Isso muda o **argumento** da D3, que passa a ser "não muda a ordem do vendedor", não "não muda nada".
- **H9:** o tamanho da empresa dá p de 0,10 a 0,14 entre concluídos e de 0,035 a 0,056 na coorte. Mas fica vazio em 68% dos negócios em andamento.
- **H6:** o `close_value` dos ganhos fica entre 0,66 e 1,34 vezes o preço de lista, com média de 0,996.
- **H7:** ganhos e perdidos têm o mesmo ciclo máximo (138). Nenhum negócio Engaging tem data de conclusão.
- **H8:** "de cada 10" junta as faixas de 0 e 30 dias (as duas viram 5).
- **H10:** dos 10 primeiros por valor ponderado, em média 88,6% também são os 10 mais caros; em 9 dos 21 vendedores, a lista é idêntica.
- **P8:** o setor "technolgy" está grafado errado.

## Comparação com o Python e reconciliação (passo 3)

**Como.** Depois do C1, li os 4 scripts de `solution/analysis/` e as saídas deles. Rodei os scripts no `.venv` (Python 3.12.4, versões do `requirements.txt`). `backtest_referencia.py` e `efeito_trimestre.py` reproduzem as saídas salvas byte a byte. `auditoria_sql.py` muda só a ordem de linhas empatadas, porque as consultas não têm `ORDER BY` completo; restaurei o arquivo versionado. Para o N18, escrevi `solution/analysis/significancia_ml.py`: é o mesmo modelo do exploratório, agora com desempate pelo ID e 5 sementes, e exporta a receita capturada por vendedor e foto. O teste pareado roda no TypeScript (`npm run auditoria`).

**Decisões de reconciliação** (CA7, D22: se TS e Python divergem, a revisão decide qual está certo e por quê):

| # | Divergência | Causa | Quem está certo | Mudança no TS |
|---|---|---|---|---|
| R1 | Curva, N13, N16, valor ponderado do backtest | Pré-registrei "em risco" como duração ≥ b; o Python usa > b (`backtest_referencia.py:16`, `auditoria_sql.py:53`) | **Python.** Um negócio aberto em T com idade *a* tem conclusão depois de início + *a*, então só é comparável a quem durou mais de *a* | padrão `atRisk: ">"`; o ≥ fica como alternativa testada |
| R2 | "Faixas e preço" 43,35% × 32,69% | O método do Python é **situação** (no prazo > esfriando > parado), depois preço (`backtest_referencia.py:26`); eu tinha lido "chance da faixa, depois preço" | **Python, quanto ao método.** Mas o Python trata 90 dias como no prazo (`a<=90`), contra os 0–89 da D2: um erro de um dia | método `situationThenPrice` com a fronteira da D2: **43,16%**. Com a fronteira do Python, 43,35%, o que confirma a causa |
| R3 | "Chance só com concluídos" 32,23% × 38,08% | O Python usa chance por dia exato, com o último dia que tem pelo menos 30 casos, e **não zera os parados** (`backtest_referencia.py:18-21`); eu tinha zerado | **Python.** É o cálculo ingênuo como alguém o faria; zerar os parados emprestaria a ele um conhecimento que vem da coorte | `concludedOnlyByDay` |
| R4 | N18: ML 45,0 × 44,6 | O 44,6% do exploratório é a chance por **dia exato**, não as faixas da D5 (`backtest_exploratorio.py:23-29`) | os dois reproduzem: ML 45,03% (as 5 sementes iguais; com cerca de 2 mil linhas por foto não há parada antecipada) e valor ponderado por dia 44,65%, contra 44,6 do exploratório, que não desempata pelo ID | — |

**Vazamento.** Não encontrei. Nos dois backtests, a curva, a coorte e os ganhos usam `cl <= T`. Os candidatos são `eng <= T & (cl nulo | cl > T)`. O ML treina na foto T−90 com rótulo "ganho até T" (`backtest_exploratorio.py:31-32`). O corte fixo de 138 não usa o futuro: o maior ciclo observado já é 138 nas 4 fotos (H2).

**A pergunta do AGENTS sobre o ML (N18): a diferença não é significativa.**

| Comparação (unidade = vendedor, 4 fotos somadas, 10.000 reamostragens) | Diferença | IC 95% | p (troca de sinais) |
|---|---|---|---|
| ML − valor ponderado por dia exato (mesmo script) | +0,38 p.p. | −3,24 a +3,48 | 0,83 |
| ML − valor ponderado por faixas (D5) | +0,62 p.p. | −3,32 a +3,98 | 0,74 |

Pela regra fixada antes de rodar (IC sem o zero e ganho de pelo menos 2 p.p.), o ML não entra.

**H3 depois da reconciliação: o ganho do valor ponderado vem quase todo da situação, não da curva.**

| Comparação | Diferença | IC 95% | p |
|---|---|---|---|
| valor ponderado − situação e preço | +1,25 p.p. | −0,19 a +2,91 | 0,13 |
| valor ponderado − preço sem parados | +4,31 p.p. | +1,99 a +7,21 | 0,0006 |
| valor ponderado − só preço | +8,23 p.p. | +4,58 a +12,67 | 0,0001 |
| valor ponderado − chance só com concluídos | +12,17 p.p. | +6,65 a +18,59 | 0,0001 |

### Tabela da revisão (AGENTS §8)

"Recalculado (C1)" é o valor do commit `3684997`, que não é mais editado. "Reconciliado" é o valor atual de `npm run auditoria`, com R1–R4. Os detalhes de cada linha estão em `solution/analysis/saidas/auditoria-ts.md`.

| ID | Afirmação | Onde | Declarado | Recalculado (C1) | Reconciliado | Status | Ação |
|---|---|---|---|---|---|---|---|
| N01, N03 | negócios, empresas, produtos, vendedores | AGENTS:48, 169 | 8.800; 85; 7; 35 | igual | igual | confere | — |
| N02 | `close_value` 0 nos perdidos, vazio nos abertos | AGENTS:49 | 2.473 de 2.473 | igual; vazio em 2.089 de 2.089 | igual | confere | — |
| N04 | etapas | AGENTS:170 | 4.238 · 2.473 · 1.589 · 500 | igual | igual | confere | — |
| N05 | "GTXPro" | AGENTS:171 | 1.480 | igual | igual | confere | — |
| N06 | Prospecting sem data | AGENTS:172 | 0 com data | igual | igual | confere | — |
| N07, N37 | sem empresa | AGENTS:173; como-escalar:105 | 1.425 de 2.089 (68%); 0 concluídos | igual (68,2%) | igual | confere | — |
| N08, N21 | período; 1º concluído; maior ciclo | AGENTS:175; análise:15 | 20/10/2016–31/12/2017; 01/03/2017; 138 | igual (ganhos e perdidos: 138) | igual | confere | — |
| N09 | 5 vendedores sem negócio | AGENTS:177 | 5 nomes | os mesmos 5 | igual | confere | — |
| N10 | sem negócio recente | AGENTS:178 | 9 de 30: 6; 3 | igual | igual | confere | — |
| N11, N26 | p do qui-quadrado (6 dimensões) | AGENTS:186; análise:45–50 | 0,264 · 0,786 · 0,604 · 0,372 · 0,971 · 0,943 | iguais | iguais | confere | o argumento da D3 muda (H5), ver a crítica |
| N12, N22 | chance por faixa; coorte | AGENTS:202–205; análise:21–31 | 49,8 · 46,4 · 44,0 · 32,9 · 21,2 · 9,1; 5.991 | 49,8 · 46,4 · 44,2 · 33,6 · 22,1 · 9,9; 5.991 | igual ao declarado | confere após R1 | registrar a definição ">" no AGENTS |
| N13, N23 | só concluídos aos 14 e 90 dias | AGENTS:206; análise:33 | 68,7 · 71,1 | 68,6 · 71,3 | 68,7 · 71,1 | confere após R1 | — |
| N14 | no prazo · esfriando · parados | AGENTS:216 | 110 · 188 · 1.291 | igual | igual | confere | — |
| N15, N19, N38 | US$ 3,89 mi; 82% parado; prospecção US$ 1,07 mi | AGENTS:217; análise:6; README:15 | idem | igual (82,2% do valor) | igual | confere | — |
| N16 | valor ponderado | AGENTS:218 | ≈ US$ 195 mil | US$ 199.308 | US$ 195.380 | confere após R1 | — |
| N20 | US$ por situação | análise:10–13 | 227.651 · 465.914 · 3.198.664 · 1.073.986 | igual | igual | confere | — |
| N20 (P5) | "82% dos negócios com data" | análise:12 | 82% dos negócios | 81,2% dos negócios; 82,2% do valor | igual | **diverge (redação)** | trocar por "82% do valor" |
| N24 | taxa de ganho; IC 95% | análise:38 | 63,15%; 62,0–64,3 | igual (Wilson e normal) | igual | confere | — |
| N25 | de cada 100 iniciados | análise:39 | 50 · 29 · 22 | 49,8 · 28,5 · 21,7 | igual | confere | — |
| N27 | melhor − pior vendedor; sorteios | análise:52; AGENTS:186 | 15,4 p.p.; 36–38% | 15,4; 38,1% | igual | confere | — |
| N28 | em valor | análise:53 | 23,5 p.p.; ~41% | 23,5; 42,3% | igual | confere | — |
| N29 | receita 9,3×; Spearman | análise:54 | 9,3×; 0,62; −0,21 | igual | igual | confere | — |
| N30 | mês do trimestre | análise:61–63 | 49,0 · 54,7 · 80,7 | igual | igual | confere | — |
| N17, N32 | backtest: valor ponderado | AGENTS:224; análise:82 | 44,41% | 44,25% | 44,41% | confere após R1 | — |
| N17 | "faixas e preço" | AGENTS:225 | 43,35% | 32,69% | 43,16% (D2) | **diverge: erro de um dia no Python** | renomear para "situação e preço" e usar 43,16% |
| N17 | preço sem parados · só preço · aleatório | AGENTS:226–229 | 40,10 · 36,17 · 15,40 | iguais | iguais | confere | — |
| N17 | chance só com concluídos | AGENTS:228 | 32,23% | 38,08% | 32,23% | confere após R3 | — |
| N18, N33, N36 | ML × valor ponderado | AGENTS:232; análise:85–87; como-escalar:89 | 45,0 · 44,6 | pendente | 45,03 · 44,65; diferença não significativa (p = 0,74–0,83) | confere | escrever o resultado do teste no lugar de "a revisão verifica" |
| N32 (P4) | tabela da análise §7 | análise:82–85 | mistura 44,4 (referência) com 45,0 (exploratório) | — | — | **erro de comparação** | separar as duas tabelas, ou comparar o ML com 44,65 |
| N34, N35 | 880 mil; marcador `medir` | como-escalar:33, 55 | a medir | — | — | sem número ainda | preencher no incremento do `bench`, ou cortar (D25). **Preenchido em 09/10/2026 (D51, `bench.md`)** |
| N39 | seis métodos | README:26 | 6 | 6 | 6 | confere | — |
| N40 | "21 consultas"; Python 3.13 | analysis/README:24, 41 | 21; 3.13 | — | 21 (Q01–Q21, mais a Q12b); os scripts reproduzem no 3.12.4 | confere | registrar que reproduz no 3.12.4 |
| N41 | hook com 10 testes | plano:102 | 10 | 10 aprovados | — | confere | — |

**Tolerâncias.** Esta regra não estava no pré-registro; ficou explícita depois do achado 7 do revisor.
- Valores exatos e valores com "≈" ou "~" conferem quando batem **na precisão em que foram declarados**. "≈ US$ 195 mil" exige 195 mil.
- Valores de Monte Carlo (os sorteios dos N27 e N28) conferem dentro de **±3 erros-padrão**, ou seja, ±1,5 p.p. com 10.000 sorteios.

**Saldo:** 41 itens no inventário e 40 linhas na auditoria. No C1, com a regra única, **31 conferem, 7 divergem e 2 estão pendentes**. Depois da reconciliação, **38 conferem e 2 divergem**, as duas com causa conhecida: a redação do N20 e o erro de um dia do Python no N17. Os itens só de texto (P4, P6, P7, P10, P12, P13) vão para os achados de documentação.

## Achados de código, configuração e documentação (revisor, rodada 1)

O veredito do revisor foi "aprovar após correções". Cada achado foi reproduzido antes de ser corrigido.

| # | Achado | Reproduzido? | Decisão | Onde |
|---|---|---|---|---|
| V1 | O "faixas e preço" do TS não é o método da preparação | sim: o mesmo que R2 | **corrigido** (`situationThenPrice`), com teste à mão | C2 |
| V2 | O "só concluídos" do TS zerava os parados | sim: o mesmo que R3 | **corrigido** (`concludedOnlyByDay`), com teste à mão | C2 |
| V3 | As 5 sementes do ML não medem variação; a "falta de determinismo" do exploratório vem do empate sem ID | sim: as 5 sementes dão 45,03% | **aceito.** A variação real é medida pelo bootstrap por vendedor. O `analysis/README.md` passa a dizer a causa certa | C2 (doc) |
| V4 | Nenhum teste fixa os números reais, e um método que lê o futuro passaria | sim: o `grep` não acha nenhum teste com 5991, 4238, 1291 ou 44.41 | **corrigido.** `reference.test.ts` fixa as contagens, a coorte, a curva, o funil, o valor ponderado e os 6 métodos, com 2 casas. O teste anti-vazamento do backtest muda todos os desfechos depois de T e exige a mesma ordem em todos os métodos. **Teste do próprio teste:** um método que ordena pela receita futura muda a ordem e é pego | C2 |
| V5 | O script de git põe `00-leitura-do-problema.md` no índice | sim: aconteceu no C1 e foi tirado com `git restore --staged` | **aceito como procedimento.** Repetir em todo commit até o Bruno fazer o dele | — |
| V6 | `engines >=22` aceita um Node que não roda `.ts` sem flag | não reproduzido: não tenho Node 22.17. A fonte é a nota de versão do Node 22.18.0, em que a remoção de tipos passou a ser padrão | **aceito:** `>=22.18`, no `package.json` e nos documentos. É um ajuste da D20 | C2 |
| V7 | O N16 tinha dois status, e as tolerâncias não estavam pré-registradas | sim | **corrigido:** regra única (acima), aplicada no código, com a contagem do C1 refeita | C2 |
| V8 | Os documentos contradizem a H5 ("não há diferença por vendedor") | sim: como-escalar:88, análise:41 | **aceito.** O novo argumento depende do Bruno (G1, D3) | C2 depois do G1 |
| V9 | Referências quebradas: arquivos do plano que não existem, "D1–D17", `npm run backtest` inexistente, `critico.md` apontando para a seção 6, terceiro nome do método, `sha256sum` no macOS | sim, todas | **aceito.** Corrijo no C2; o `critico.md` está em `.claude/` e fica como proposta | C2; `.claude/` depende do Bruno |
| V10 | Coorte vazia vira chance 0 sem aviso | sim: a variante H11 em 30/06 | **aceito, para o incremento 4.** As 5 datas do seletor têm coorte, então hoje não há caso real. A guarda `hasEnoughHistory` entra junto com o seletor (CA6) | incremento 4 |

O revisor pediu também o e-mail dos commits: `git log --format='%ae'` mostra um endereço `@gmail.com` (pessoal) no C1. Ele não está escrito aqui.

## Parecer do critico sobre a revisão (rodada 1 deste gatilho)

Veredito: "ajustar e seguir". O ponto que bloqueia é decidir a coorte (H11) antes do incremento 4.

| # | Achado | Reproduzido? | Decisão |
|---|---|---|---|
| K1 | [BLOQUEANTE] A base cortada no início infla a curva, e a frase e o valor ponderado herdam isso | **sim, e piorou na checagem:** a taxa de ganho por mês de início em `efeito_trimestre.txt` é 1,0 (out/16), 0,72, 0,68 e 0,58 nos meses iniciais, contra 0,34 a 0,57 de abr a ago/17. A coorte limpa é vazia em 30/06 e tem 379 negócios em 31/07. A calibração está abaixo | aceito; vai ao G1 (pergunta 1) |
| K2 | A D3 testa o vendedor com o método que o projeto chama de errado para a curva | sim: p = 0,264 entre concluídos e p < 0,001 na coorte; a diferença está na fração que fica aberta (de 0% a 31%) | aceito; vai ao G1 (pergunta 3) |
| K3 | O ganho vem da triagem por idade, não da curva fina | sim: H3 +1,25 p.p. sobre "situação e preço", p = 0,13; H10 88,6% | aceito; vai ao G1 (pergunta 4) |
| K4 | A parte que diferencia a entrega é a que pode ser cortada | é leitura do plano; o fato confere (D19 e D25) | aceito como proposta; vai ao G1 (pergunta 5) |
| K5 | O AGENTS §2.2 omite trechos do enunciado: a frase da Head, "o deliverable principal é software", a dica completa das features óbvias, o exemplo "score 85" e o "setor de educação" | sim: enunciado:15, 17, 96, 98; README raiz:52 | aceito; muda o AGENTS, então vai ao G1 (pergunta 6) |
| K6 | A frase "de cada 10" é uma probabilidade sem validação | **sim:** em 31/08, a curva cheia prevê 51,7% e se realizam 34,3%; a limpa prevê 45,3% (`auditoria-ts.md`, Calibração; `reference.test.ts`) | aceito; `calibrationAt` entrou no núcleo, com teste; vai ao G1 (pergunta 2) |
| K7 | As reconciliações estão certas; os números de H3 e H11 citados eram os da versão com ≥ | sim | corrigido: os números com > estão abaixo. A seção C1 continua com os valores do C1, como registro |
| K8 | A S3 com seletor e embaralhamento no navegador é cara para uma página que pode ser cortada | — | **aceito no plano do incremento 5:** a S3 vira uma tabela estática com as 8 dimensões, os dois p-valores e o mês do trimestre; o embaralhamento fica só na auditoria |

Números reconciliados (">") que substituem os da seção C1:
- curva limpa em 31/12: 47,3 · 41,7 · 38,6 · 25,6 · 13,5 · 4,3%;
- H3: valor ponderado − preço sem parados = +4,31 p.p. (IC 1,99 a 7,21);
- H1: faixas de 30 em 30 dias dão 44,14%.

## Crítica

O que está fraco, o que eu mudaria e por quê, em ordem de prioridade. Cada item tem evidência em `solution/analysis/saidas/auditoria-ts.md`.

1. **A curva superestima a chance, e o motivo é conhecido.**
   - A base só contém negócios concluídos a partir de 01/03/2017 ou ainda abertos. Os iniciados antes disso entram só se sobreviveram até março (H11), e por isso ganham mais: 72% em nov/16 contra cerca de 45% em 2017.
   - Em 31/08, a curva cheia previa 51,7% de ganho para os abertos e se realizaram 34,3%. A curva limpa (iniciados a partir de 01/03/2017) previa 45,3%: ainda erra, mas menos.
   - A **ordem** não muda: com a curva limpa, o valor ponderado dá 43,10% nas fotos de 31/08 e 30/09, contra 42,97% com a cheia.
   - **Mudaria:** usar a coorte limpa; bloquear datas com coorte pequena (30/06 tem zero); e não vender a chance como previsão.
2. **A frase "de cada 10" e o valor ponderado são instrumentos de ordem, não previsões.**
   - Mesmo com a curva limpa, a chance prevista fica 11 p.p. acima da realizada em 31/08. Por faixa, o erro oscila muito (30 dias: 51% → 22%; 90 dias: 31% → 44%).
   - O calendário pesa, e muito (mês do trimestre: 49% · 55% · 81%), e não é conhecido para um negócio em andamento.
   - **Mudaria:** escrever a frase como fato histórico ("entre os negócios que chegaram a essa idade, X de cada 10 viraram venda"); mostrar a calibração no "Como funciona"; e não somar o valor ponderado como previsão de receita na visão do gestor.
3. **A D3 está certa, mas pelo motivo errado.**
   - Produto não muda nada: p = 0,37 entre concluídos e 0,72 na coorte.
   - O vendedor não muda a taxa entre concluídos (p = 0,26), mas muda muito a fração que fica parada: 0% para três vendedores, até 31% para outros (p < 0,001 na coorte). A própria auditoria SQL da preparação já mostrava isso (Q12).
   - Um fator do vendedor multiplica todos os negócios dele e **não muda a ordem da lista que ele vê**; esse é o argumento certo para deixá-lo fora.
   - **Mudaria:** reescrever a D3 e a análise com os dois testes, e levar o achado para a visão do gestor ("% parado por vendedor"), que é a informação mais acionável da base para quem gerencia.
4. **"Vai além de ordenar por valor" está frágil e precisa ser dito com precisão.**
   - Sobre "só preço", o valor ponderado ganha +8,23 p.p. (IC 4,58 a 12,67), e isso é sólido.
   - Sobre "situação e preço", ganha só +1,25 p.p. (p = 0,13).
   - Em 31/12, 88,6% dos 10 primeiros por valor ponderado também estão entre os 10 mais caros.
   - **Mudaria:** a mensagem passa a ser "a idade decide em que lista o negócio está e se ele esfria; o preço ordena dentro da lista; a chance explica". O CA3 passa a exigir o ganho sobre "só preço" com IC. O painel mostra o custo de esperar.
5. **O ML fica fora, agora com evidência.** +0,62 p.p. sobre o valor ponderado, IC −3,32 a +3,98, p = 0,74. A regra de decisão foi fixada antes (2 p.p. e IC sem o zero), e o resultado não chegou perto.
6. **Risco de parecer o baseline.**
   - O score usa idade e preço, justamente as features que o enunciado chama de óbvias.
   - O que diferencia a entrega é a evidência: viés de sobrevivência evitado, base cortada detectada, "sem empresa" que vaza o desfecho, backtest com IC, ML testado e descartado, calibração.
   - Essa evidência está na página que pode ser cortada.
   - **Mudaria:** um piso que não pode ser cortado, sem gráficos: três tabelas vindas de `src/core` (curva da coorte × só concluídos; backtest com IC; dimensões com os dois p-valores), mais uma linha no painel de motivo.
7. **Os dados parecem sintéticos ou recortados (H7):**
   - ciclo máximo idêntico (138) para ganhos e perdidos;
   - nenhum negócio concluído depois de 138 dias;
   - três vendedores com 0% de negócios parados;
   - corte no início e no fim, com só 121 inícios em dez/17;
   - um efeito de fim de trimestre enorme.
   **Mudaria:** dizer isso nas limitações, sem exagerar, e vender o método (point-in-time, coorte, backtest, calibração), que funcionaria numa base real, e não os números da curva.
8. **Pontos menores:**
   - o resumo de regras do AGENTS omite trechos do enunciado (K5);
   - o `critico.md` aponta para a seção 6 em vez da 7;
   - o benchmark promete faixas "alta, média, baixa" que nenhuma decisão prevê (P7): decidir no incremento 4;
   - "technolgy" está grafado errado no `accounts.csv` (P8): corrigir na exibição, sem mudar o arquivo.

## Decisões para o Bruno (G1)

| # | Decisão | Recomendação | Muda |
|---|---|---|---|
| 1 | Coorte limpa: só iniciados a partir da primeira conclusão observada (01/03/2017), mais um n mínimo de coorte para a data ficar disponível | **Sim, com n ≥ 1.000.** O seletor fica com 31/08, 30/09 e 31/12/2017 (31/07 tem 379; 30/06 tem 0). O backtest de referência de 4 fotos continua como comparação de **ordem** entre métodos, com a linha da curva limpa ao lado | D1 (ajuste), D5, CA6 |
| 2 | A chance é apresentada como histórico, não como previsão; o valor ponderado é critério de ordem | **Sim.** Frase: "Entre os negócios que chegaram a essa idade, X de cada 10 viraram venda". O "Como funciona" mostra a calibração. A visão do gestor mostra o valor em funil por situação, e não soma o valor ponderado como previsão | D5, CA4 |
| 3 | Novo argumento da D3, e o "% parado por vendedor" na visão do gestor | **Sim** | D3, incremento 4 |
| 4 | Mensagem e CA3: "a idade decide a lista, o preço a ordem, a chance explica"; o CA3 exige o ganho sobre "só preço" com IC | **Sim** | CA3, README |
| 5 | Piso não cortável do CA16: três tabelas, sem gráfico | **Sim.** Gráficos e seletor continuam cortáveis | D25, CA16 |
| 6 | O AGENTS §2.2 ganha os trechos literais do enunciado (K5 e P12); a D3 é reescrita; a tabela do §7 aponta para D18–D26 | **Sim.** Aplico com o seu ok, porque mexe no AGENTS | AGENTS |
| 7 | Corrigir o `critico.md` (seção 6 → 7) | **Sim.** Está em `.claude/` e precisa do seu ok | `.claude/` |
| 8 | Commit do `00-leitura-do-problema.md` | quando você avisar, faço um commit só com ele | — |

## G1 (09/10/2026): respostas do Bruno e o que foi feito

As respostas estão em `decisoes.md` (D27–D32). A leitura do Bruno (`00-leitura-do-problema.md`) foi criticada e versionada sem alteração (commit `a2fb335`). As hipóteses dela vieram do material de partida, como o próprio texto diz. A revisão confirmou as três primeiras (funil inflado, viés da taxa só com concluídos, "sem empresa" vazando o desfecho) e corrigiu a quarta: o vendedor não muda a taxa de ganho, mas muda quanto do funil fica parado.

**1. Coorte limpa, com o backtest refeito** (`auditoria-ts.md`, "Regra final (G1)").

| Regra | Datas disponíveis (IC de no máximo ±5 p.p. em toda faixa) | Valor ponderado − só preço | Valor ponderado − situação e preço |
|---|---|---|---|
| Limpa (regra final) | só 30/09; 31/08 fica fora por ±5,01 p.p. | +18,69 p.p. (IC 12,28 a 25,57) | +5,58 p.p. (IC 1,82 a 9,50; p = 0,008) |
| Entrada tardia | 31/07, 31/08, 30/09 | +7,66 p.p. (IC 3,49 a 12,62) | +0,12 p.p. (IC −1,51 a 2,11; p = 0,90) |
| Sem correção (preparação) | as 4 | +8,23 p.p. (IC 4,58 a 12,67) | +1,25 p.p. (p = 0,13) |

- **Por que ±5 p.p.:** é a pergunta "a faixa tem dados para afirmar a chance com uma casa de 10 de margem?". Com a coorte limpa, o corte cai entre 379 negócios (31/07: ±8,6 p.p.) e 1.258 (31/08: ±5,01 p.p.), o que equivale aos "≥ 1.000". O critério fica no código (`hasEnoughHistory`).
- **Evidência:** com a regra limpa, o ganho sobre "só preço" é forte, mas vem de **uma** foto. 31/08 cai por 0,013 p.p., o que mostra que o limite é frágil exatamente nessa data. Por isso, a entrada tardia também foi calculada, como pedido.
- **Calibração:** as duas regras superestimam a chance. Em 31/08, a limpa previa 45,3%, a tardia 47,7%, e se realizaram 34,3%.
- **Os 34% de 31/08 estão pouco subestimados.** Só 81 dos 1.857 negócios (4,4%) ainda podiam concluir depois de 31/12. Mesmo que todos virassem venda, o realizado subiria no máximo para 38,7%. Na prática, eles já tinham de 122 a 138 dias em 31/12, idade em que a chance histórica fica entre 4% e 20%. Isso não muda a conclusão e entra no "Como funciona" como nota de rodapé da calibração.

**Recomendação: entrada tardia.** É o tratamento padrão para dados cortados no início. Ela usa todos os negócios observados, sem o viés dos sobreviventes, porque cada um entra na conta só nas idades em que a base o enxergava. Ela mantém 3 fotos de backtest em vez de 1, e com IC mais estreito. O custo é uma hipótese a mais: que o corte foi exatamente "negócios concluídos antes de 01/03/2017 saíram da base". O que sustenta essa hipótese: nenhuma conclusão antes de 01/03 e os inícios crescendo de 7 para cerca de 800 por mês. Se o Bruno preferir não depender dela, a limpa fica, com o aviso de que a validação vem de uma única data.

**2. A frase como histórico.** D28 registrada. A frase será gerada no núcleo no incremento 4, com N igual ao início da faixa.

**3. A fração parada por vendedor como situação do funil.** D29 registrada. Será feita no incremento 4, com o aviso sobre vendedor, carteira e região.

**4. Três negócios reais em que as duas ordens divergem** (31/12/2017, coorte limpa; são 309 pares assim):

| Vendedor | Valor ponderado põe primeiro | "Situação e preço" põe primeiro | Leitura |
|---|---|---|---|
| Rosalina Dieter | **1LY8CAXD**, GTK 500, US$ 26.768, 95 dias (esfriando), chance 25,6% → ponderado US$ 6.846 | **OHOWVHYX**, MG Advanced, US$ 3.393, 81 dias (no prazo), chance 38,6% → US$ 1.310 | Uma chance em quatro de US$ 26,8 mil vale cinco vezes mais que quatro em dez de US$ 3,4 mil. O valor ponderado acerta, e "situação e preço" mandaria a vendedora trabalhar o negócio pequeno primeiro |
| Hayden Neloms | **7GDSUY9K**, GTX Plus Pro, US$ 5.482, 117 dias, chance 13,5% → US$ 740 | **HB740BLB**, MG Special, US$ 55, 11 dias, chance 47,3% → US$ 26 | O negócio de US$ 55 não paga uma ligação. Mas o 7GDSUY9K tem 21 dias até ficar parado, e a chance cai para 4,3% aos 120 dias. Valor ponderado com custo de esperar |
| Daniell Hammack | **LFI3BGEE**, GTX Plus Pro, US$ 5.482, 100 dias, chance 25,6% → US$ 1.402 | **JIEO87ZV**, MG Advanced, US$ 3.393, 86 dias, chance 38,6% → US$ 1.310 | Quase empate. Mas o JIEO87ZV cruza os 90 dias em 4 dias e cai para 25,6%, ou US$ 868. Aqui "situação e preço" capta algo real: **agir antes de esfriar** |

**Recomendação: manter o valor ponderado (D5)** e levar o que "situação e preço" tem de certo para o painel de motivo, na forma do **custo de esperar** ("em 4 dias, a chance cai de 4 para 3 em cada 10"). No backtest, o valor ponderado empata com "situação e preço" (entrada tardia, p = 0,90) ou ganha (limpa, p = 0,008). Os exemplos mostram que ele evita o erro grosseiro do primeiro caso.

**5–7.** Aplicados: o piso do CA16 (D31), o AGENTS §2.2 com os trechos literais, a D3 reescrita, a tabela do §7, o `critico.md` (seção 7), o CA3 (ganho sobre "só preço" com IC, fixado em `reference.test.ts`), o CA4 (frase), o CA6 (critério de IC) e o CA16 (piso).

### Pendentes com o Bruno

| # | Decisão | Recomendação |
|---|---|---|
| G1-a | Coorte limpa (1 foto de validação) ou entrada tardia (3 fotos)? | **Entrada tardia** |
| G1-b | Os 3 exemplos convenceram? A "Foque agora" fica no valor ponderado, com o custo de esperar no painel? | **Sim, valor ponderado mais custo de esperar** |

### Respostas do Bruno (09/10/2026)

- **G1-a: entrada tardia**, com três condições, todas aplicadas:
  - a coorte limpa fica como análise de sensibilidade. O "Como funciona" e o README mostram que as duas chegam à mesma conclusão: o valor ponderado ganha de "só preço" (+7,66 p.p. em 3 datas com entrada tardia; +18,69 p.p. na única data da limpa);
  - a hipótese da entrada tardia vai para as Limitações, com o método numa frase;
  - a D27 registra por que a limpa perdeu: validação numa data só, e 31/08 excluída por 0,01 p.p. do limite de IC.
- **G1-b: valor ponderado.** O custo de esperar entra **sem prever queda de chance**. Os saltos (de 13,5% para 4,3% em 3 dias) vêm dos limites das faixas, não de uma queda real dia a dia, e mostrá-los como fato contradiz a D28. Ficam só "Esfria em N dias" (até 90) e "Fica parado em N dias" (até 138), como selo e como linha no painel de motivo, sem mudar a ordem (D30). **A frase que este arquivo recomendou no item 4 ("em 4 dias, a chance cai de 4 para 3 em cada 10") foi recusada por esse motivo.**
- **Leitura do problema:** o README não a apresenta como previsão dos resultados. Conta o que a revisão confirmou e o que corrigiu.

Aplicação no código: o padrão passou a ser `DEFAULT_TRUNCATION = "lateEntry"` (`rules.ts`, também usado por `backtest.ts`); `reference.test.ts` fixa as duas coortes; `npm run auditoria` foi refeito. Efeito colateral registrado: com a regra final, dos 10 primeiros por valor ponderado, em média 88,6% também estão entre os 10 mais caros, contra 85,7% com a limpa (H10).
