# Diário de processo: otimização do plano em loop

- **Início:** 21 de setembro de 2026
- **Skill:** `superpowers:writing-plans` 6.2.0
- **Goal:** encerrar somente após duas passadas consecutivas sem melhoria ou otimização substancial
- **Plano-alvo:** `solution/001-churn/docs/superpowers/plans/2026-09-21-ravenstack-churn-diagnostic.md`
- **SPEC de referência:** `solution/001-churn/.specs/tasks/in-progress/implement-churn-diagnostic.feature.md` (promovida após o fechamento do plano)
- **Estado:** concluído; goal atingido em 20 passadas

## Protocolo

Cada passada verifica cobertura da SPEC, ausência de placeholders, consistência de arquivos e interfaces, buildabilidade, decomposição, testes, comandos e respeito ao escopo oficial. Uma passada só conta como “sem melhoria substancial” quando não encontra lacuna capaz de fazer a implementação travar, produzir resultado incorreto ou descumprir requisito. Ajustes cosméticos não zeram a sequência; correções materiais zeram.

## Pré-loop: realidade dos dados

Antes de escrever o plano, baixamos o dataset público para uma pasta temporária e conferimos os CSVs e o README original. Isso evitou planejar schemas inventados e revelou contradições que alteram a arquitetura:

- 500 contas, 5.000 assinaturas, 25.000 eventos de uso, 2.000 tickets e 600 eventos de churn;
- 21 grupos de `usage_id` duplicados com conteúdo conflitante;
- 19.142 usos anteriores ao início da assinatura e 13.198 usos anteriores ao cadastro da conta;
- 1.077 tickets anteriores ao cadastro;
- 339 contas com churn não reativação, enquanto somente 110 contas possuem `accounts.churn_flag=True`.

O README do dataset afirma temporalidade validada, mas os dados contradizem essa afirmação. Portanto, o plano não poderá bloquear toda a execução diante de datas impossíveis nem escolher silenciosamente um único rótulo de churn. A SPEC draft foi corrigida para exigir flags de qualidade, reconciliação de rótulos e análise de sensibilidade entre timestamps observados e cronologia válida.

### Incidente de ferramenta

A primeira tentativa de limpar a pasta temporária foi bloqueada pela política contra `rm -rf`. Nenhum arquivo do projeto foi alterado. Repetimos a inspeção sem remoção destrutiva; a cópia temporária permaneceu em `/tmp/churn-plan.V2WnJK`.

## Passada 1 — melhorias substanciais encontradas

**Resultado:** sequência de estabilidade reiniciada para `0/2`.

- Tornamos explícito que comandos de implementação rodam na pasta da solução e comandos Git na raiz do repositório.
- Criamos as fixtures que os testes já citavam; antes, o plano não era executável task a task.
- Separamos os cutoffs rotulados até `2024-11-30` do snapshot operacional sem rótulo de `2024-12-31`.
- Definimos o cálculo da próxima renovação anual, o tratamento conservador de reativações e a fórmula exata da sensibilidade `observed` versus `strict`.
- Fixamos `setuptools==84.0.0`, removemos o placeholder de Codespace e declaramos a interface ausente de `apply_model_gate`.

Também tornamos determinísticas a corroboração entre tabelas e a origem dos textos de ação. Estas mudanças evitam vazamento temporal, testes que falham por infraestrutura inexistente e recomendações geradas sem trilha de auditoria.

## Passada 2 — melhorias substanciais encontradas

**Resultado:** sequência de estabilidade reiniciada para `0/2`.

A releitura do briefing oficial mostrou que o plano precisava caber no orçamento declarado de 4–6 horas. Adicionamos um timebox de `5 h 25 min`; o modelo deixa de ser publicado se consumir seu orçamento, e o deploy público permanece fora do caminho crítico.

A inspeção das assinaturas revelou outra lacuna material: quase todas as contas possuem várias assinaturas simultaneamente, muitas com planos e frequências diferentes. O plano agora:

- soma MRR e assentos uma única vez por `subscription_id` ativo;
- usa `mixed` para plano ou frequência conflitante, sem escolher uma linha arbitrária;
- calcula a renovação anual mais próxima entre contratos anuais ativos;
- define MRR perdido como a receita ativa no dia anterior ao churn terminal;
- exige limiar numérico para a corroboração retrospectiva por `reason_code`.

Sem essas regras, o principal indicador financeiro e os segmentos poderiam mudar conforme a ordem das linhas do CSV.

## Passada 3 — melhoria substancial encontrada

**Resultado:** sequência de estabilidade reiniciada para `0/2`.

O plano ainda orientava instalação e suíte completa no Mac, em conflito com a regra operacional global. A convenção agora exige `codespace-manager` para instalação, testes, reprodução e Streamlit; o Mac fica restrito a inspeção e Git.

Também removemos um gate manual impreciso do dashboard. O AppTest passa a verificar as três visões, aplicar um filtro real, produzir o download e comparar as contas mostradas com o CSV canônico. A revisão visual fica vinculada somente ao deploy público opcional.

## Passada 4 — melhorias substanciais encontradas

**Resultado:** sequência de estabilidade reiniciada para `0/2`.

Os snippets de teste citavam `pytest`, `pandas` e funções do pacote sem imports completos. Isso impediria copiar e executar os passos como exige `superpowers:writing-plans`; os imports foram adicionados em cada módulo de teste.

Também substituímos a promessa genérica de cobertura por uma matriz explícita ligando cada requisito oficial à task e à evidência executável correspondente. A API de AppTest foi conferida na documentação oficial do Streamlit; o teste verifica a tabela filtrada contra o CSV e a presença do download, sem alegar acesso a bytes que o harness não expõe.

## Passada 5 — melhorias substanciais encontradas

**Resultado:** sequência de estabilidade reiniciada para `0/2`.

O plano dizia que as ações seriam fixas, mas não fixava seus textos, donos nem métricas. Incluímos um mapa revisável para produto, suporte e comercial, evitando recomendações livres geradas durante a execução.

Também especificamos o caso em que nenhuma hipótese passa os gates: relatório e dashboard declaram evidência insuficiente, a fila mantém apenas os cabeçalhos e nenhum score preditivo vira recomendação por conta própria. Um teste protege esse comportamento. Declarar “inconclusivo” agora é um caminho executável, não apenas um princípio.

## Passada 6 — melhorias substanciais encontradas

**Resultado:** sequência de estabilidade reiniciada para `0/2`.

Modelos estatísticos podem falhar com variância zero, separação perfeita, matriz singular, não convergência ou apenas uma classe no período de teste. O plano agora converte esses casos em finding inconclusivo ou modelo não publicado, registra uma razão estável e continua o diagnóstico. Um teste específico cobre o candidato sem variância.

## Passada 7 — melhoria substancial encontrada

**Resultado:** sequência de estabilidade reiniciada para `0/2`.

O deploy público e o Pull Request alteram estado externo. O plano agora exige autorização explícita no momento da execução, mesmo depois do preflight verde. Sem autorização, a entrega local permanece válida e o status é documentado, sem push ou publicação automática.

## Passada 8 — melhorias substanciais encontradas

**Resultado:** sequência de estabilidade reiniciada para `0/2`.

As janelas 7/30/90 ainda permitiam mais de uma fórmula, e a fila não definia quando uma conta estava exposta a um driver contínuo. Fixamos comparações de taxas em janelas não sobrepostas, divisão segura, seis operadores/thresholds de exposição e a regra de auto-renovação. Também fixamos byte a byte a fórmula SHA-256 do split de contas. Assim, dois implementadores produzem a mesma fila e a mesma divisão de avaliação.

## Passada 9 — melhoria substancial encontrada

**Resultado:** sequência de estabilidade reiniciada para `0/2`.

“Cobertura” ainda não tinha denominador operacional. Agora uma janela de suporte exige vida completa da conta; uma janela de uso também exige assinatura mapeada durante todo o período. Janela incompleta vira nulo, não zero. Campos medidos em tickets possuem cobertura própria, e o gate de 70% usa valores não nulos sobre linhas elegíveis do snapshot. Um teste-sentinela protege a diferença entre ausência de evento e ausência de observação.

## Passada 10 — sem melhoria substancial

**Resultado:** estabilidade em `1/2`.

Reavaliamos o briefing oficial, a SPEC, a matriz de rastreabilidade, todos os snippets, fixtures, fórmulas, gates, comandos e limites de autorização. A busca por placeholders não encontrou pendências; `git diff --check` permaneceu limpo. Nenhuma lacuna capaz de bloquear a implementação, alterar uma conclusão ou descumprir o desafio foi encontrada. Ajustes apenas editoriais não foram feitos.

## Passada 11 — melhoria substancial encontrada

**Resultado:** sequência de estabilidade reiniciada para `0/2`.

Uma verificação do repositório mostrou que `.gitignore` ignora toda a pasta `submissions/`. Os arquivos antigos estavam rastreados, mas novos códigos, dados, artefatos, plano e diário não entrariam com `git add` comum. Todos os commits planejados agora usam `git add -f` e incluem as alterações incrementais de `tests/conftest.py`.

## Passada 12 — melhoria substancial encontrada

**Resultado:** sequência de estabilidade reiniciada para `0/2`.

O uso amplo de `git add -f` resolveria o ignore, mas também poderia incluir `.venv`. Restringimos os dois comandos amplos a listas explícitas de código, dados públicos, documentação e artefatos canônicos. Os demais comandos forçam apenas diretórios controlados como `src`, `tests` e `.streamlit`.

## Passada 13 — melhoria substancial encontrada

**Resultado:** sequência de estabilidade reiniciada para `0/2`.

O `make check` regenerava os artefatos versionados. Como o manifesto contém timestamp e SHA de origem, o próprio preflight poderia sujar o worktree e invalidar sua prova. Agora o gate reproduz em `/tmp`, compara todo conteúdo substantivo com os artefatos comprometidos e ignora somente metadados obrigatoriamente variáveis. O status de testes só vira `passed` quando o Makefile acabou de executar pytest, e o Codespace prova worktree limpo depois do gate.

## Passada 14 — sem melhoria substancial

**Resultado:** estabilidade em `1/2`.

A revisão percorreu o fluxo completo de dados, painel, diagnóstico, modelo opcional, publicação, interface, Git e Codespace. Conferimos 9 tasks, 74 passos, blocos Markdown balanceados, ausência de placeholders reais, comandos de stage restritos e `git diff --check` limpo. Nenhuma mudança material foi indicada.

## Passada 15 — melhoria substancial encontrada

**Resultado:** sequência de estabilidade reiniciada para `0/2`.

O critério oficial de leitura executiva em cinco minutos estava refletido no design, mas não possuía aceite. Adicionamos um gate com revisor não técnico, cronômetro e cinco respostas verificáveis: decisão, significado do MRR exposto, ação de uma semana, ação de 30–90 dias e limitação principal. O resultado e eventuais correções serão registrados no diário.

## Passada 16 — melhoria substancial encontrada

**Resultado:** sequência de estabilidade reiniciada para `0/2`.

O modelo prometia uma lista fixa de atributos sem enumerá-la. Fixamos 20 colunas conhecidas no cutoff e adicionamos um teste que proíbe flags, data, motivo, texto e reembolso de churn. IDs, nomes, datas brutas e campos pós-corte também ficam explicitamente fora do pipeline.

## Passada 17 — melhoria substancial encontrada

**Resultado:** sequência de estabilidade reiniciada para `0/2`.

O modelo ainda consumiria o painel `observed`, embora os dados contenham milhares de eventos anteriores ao ciclo de vida. Alteramos treino, avaliação e scoring para o painel `strict`. A visão `observed` continua útil como sensibilidade do diagnóstico, mas não alimenta previsão.

## Passada 18 — melhoria substancial encontrada

**Resultado:** sequência de estabilidade reiniciada para `0/2`.

O arquivo indicado no pedido ainda encerrava com o placeholder de descrição da SPEC. Preenchemos a descrição, os seis critérios de aceite e o link para o plano canônico de execução. A SPEC continua curta; detalhes operacionais permanecem em uma única fonte, sem duplicação divergente.

## Passada 19 — sem melhoria substancial

**Resultado:** estabilidade em `1/2`.

Relemos em conjunto briefing oficial, SPEC, plano canônico e diário. Confirmamos o link entre os artefatos, nove tasks completas, ausência de placeholders, escopo restrito e diff sem erros de whitespace. Nenhuma otimização material foi identificada.

## Passada 20 — sem melhoria substancial

**Resultado:** estabilidade em `2/2`; goal atingido.

Uma nova revisão começou do briefing, sem reutilizar a conclusão da rodada anterior. O plano permaneceu com 9 tasks, 75 passos, matriz de rastreabilidade completa e zero marcadores abertos. Interfaces, fixtures, thresholds, cronologia, artefatos, comandos, autorização externa e critérios de aceite continuaram consistentes. Nenhuma otimização substancial foi apontada.

## Fechamento do loop

Foram necessárias 20 passadas. Melhorias materiais apareceram até a Passada 18; as Passadas 19 e 20 foram consecutivas e estáveis. O plano está pronto para o gate SDD seguinte, ainda sem implementação da solução.

## Auditoria final pós-loop — aderência ao avaliador e à stack

**Data:** 21 de setembro de 2026
**Resultado:** cobertura integral confirmada após correções; implementação ainda não iniciada.

Reconsultamos pela internet o fork e o upstream do desafio. Ambos apontavam para o mesmo `main`, commit `4aed364d572fabe0f1fff1f0c6f32960b30fe575`, e mantinham os mesmos requisitos: relatório diagnóstico, cinco tabelas, causa, segmentos e contas, ações priorizadas com impacto, separação entre correlação e causalidade, leitura executiva e process log obrigatório.

### Gargalos encontrados e eliminados

- A versão atual da skill `writing-plans` exige `Spec` e `Review Focus`; ambos foram adicionados com cinco riscos ligados a testes nomeados.
- O plano não obrigava uma resposta direta às duas contradições do CEO. Adicionamos `claim_checks.csv`, com uso e satisfação no agregado versus a coorte de churn em 30 dias, além de presença obrigatória no relatório e dashboard.
- `.streamlit/config.toml` dentro da solução seria ignorado no Community Cloud, que inicializa a aplicação na raiz do repositório. Removemos esse arquivo planejado, migramos layout/estilo para `app.py` e fixamos caminhos a partir de `__file__`.
- O deploy não possuía o arquivo de dependências recomendado ao lado do entrypoint. Adicionamos `requirements.txt`, teste de igualdade com as dependências runtime do `pyproject.toml` e smoke test executado a partir da raiz do repositório.
- A instalação agora usa apenas wheels (`--only-binary=:all:`), eliminando compilação nativa e a necessidade de `packages.txt`.

### Stack verificada

Consultamos os metadados oficiais do PyPI para NumPy `2.5.3`, pandas `3.0.6`, SciPy `1.18.1`, statsmodels `0.15.0`, scikit-learn `1.9.1`, Streamlit `1.64.0`, Plotly `7.1.0`, pytest `9.1.1`, Ruff `0.16.8` e setuptools `84.0.0`. Todas as versões existem, não estão revogadas e aceitam Python 3.12; bibliotecas compiladas possuem wheel Linux x86-64 e as demais possuem wheel universal ou próprio de plataforma.

O Streamlit Community Cloud documenta Python 3.12 como padrão atual, recomenda `requirements.txt` ao lado do entrypoint e executa o app a partir da raiz do repositório. O plano agora testa exatamente esse cenário e não depende de segredo, API paga, banco ou pacote apt.

Fontes verificadas: [Challenge 001](https://github.com/luisroquette/ai-master-challenge/tree/main/challenges/data-001-churn), [guia de submissão](https://github.com/luisroquette/ai-master-challenge/blob/main/submission-guide.md), [dependências do Streamlit Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies) e [organização de arquivos no Streamlit Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization).

### Incidentes da auditoria

A primeira consulta em lote ao PyPI falhou porque `zsh` não separou pares escritos com espaço; repetimos com delimitador `@` e obtivemos todos os metadados. Um patch foi rejeitado por conter duas operações para o mesmo arquivo; reaplicamos como uma única operação. Nenhum incidente alterou arquivos fora da submissão.

Uma checagem adicional improvisada do download Kaggle falhou três vezes sem testar o fluxo real: `HEAD` retornou 404, `status` era variável reservada do `zsh` e um template de `mktemp` com sufixo foi inválido. Interrompemos a repetição. O comando planejado usa `GET` e `mktemp -d`, combinação já executada com sucesso na inspeção inicial; além disso, os cinco CSVs verificados serão versionados, então reprodução e avaliação não dependerão da disponibilidade futura do Kaggle.

### Capacidade externa antes da implementação

O semáforo listou cinco Codespaces, todos de outros repositórios, e nenhum reutilizável para este challenge. O candidato mais antigo, `codex-preflight-vr7p79qv66whw4g9`, está limpo, sem commits locais e corresponde ao commit `d73cbea`, já integrado no PR `luisroquette/swen.ia.br-claude#320`. Uma inspeção remota acionou pager, interrompeu o comando e deixou o ambiente ativo; ele foi explicitamente parado, sem exclusão nem alteração de arquivos.

Esse era o único gargalo externo remanescente. Solicitamos autorização explícita antes da ação destrutiva; o proprietário autorizou a exclusão permanente do ambiente indicado.

### Liberação da capacidade de Codespaces

Excluímos exclusivamente o Codespace `codex-preflight-vr7p79qv66whw4g9`, que estava parado e limpo. O disco efêmero do ambiente não é recuperável, mas o código permanece preservado no commit `d73cbea`, já integrado no PR `luisroquette/swen.ia.br-claude#320`.

Após a exclusão, `codespace-manager list` confirmou quatro ambientes, todos em estado `Shutdown`. O teto global voltou a ter uma vaga disponível para criar ou reutilizar um Codespace do Challenge 001. Não há gargalo conhecido de capacidade antes da implementação; a validação real da stack continua sendo um gate da fase de execução, pois a solução ainda não foi implementada.

## Epílogo — confronto do plano com a implementação

**Data:** 21 de setembro de 2026
**Resultado:** o plano foi executado até a documentação e sofreu três correções operacionais, sem mudança de arquitetura.

- O exemplo do `AppTest` resolvia `app.py` a partir de `tests/`; a implementação passou a usar caminho absoluto e manteve um smoke iniciado pela raiz.
- O `Makefile` previa `cli compare`, mas o subcomando ainda não estava implementado. A lacuna foi detectada antes do fechamento, coberta por teste e validada com duas execuções equivalentes.
- A `.venv` criada por `uv` não continha `pip`; `make setup` agora aciona `ensurepip` somente quando necessário.

O contrato final local, autorizado por bypass explícito do Codespace, concluiu `make setup`, `make reproduce` e `make check`. Foram 29 testes, Ruff verde, 8 artefatos protegidos e comparação `artifact_sets=equal`. O diário `003-implementacao-feedback-looping.md` contém o relato cronológico integral da execução.
