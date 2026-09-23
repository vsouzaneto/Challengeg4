# Diário de processo — Challenge 002: Redesign de Suporte

## I01 — Briefing absorvido com leitura em loop — 2026-09-21 14:27 BRT

- **Objetivo:** compreender integralmente o Challenge 002 antes de pesquisar dados, escolher ferramentas ou construir a solução.
- **IA/ferramenta:** Codex, GitHub CLI e Git; usados para ler os documentos oficiais, conferir a versão avaliada e reavaliar requisitos por lentes diferentes.
- **Ação ou prompt:** Luis definiu um gate próprio: reler o briefing até obter pelo menos duas passadas consecutivas sem novos achados. Essa decisão criativa é contribuição humana, não sugestão da IA.
- **Resultado:** cinco passadas concluídas; as passadas 4 e 5 não produziram descobertas novas, atingindo o critério de saturação 2/2.
- **Julgamento humano:** aceito por Luis como método permanente para reduzir construção prematura baseada em compreensão parcial.
- **Verificação:** README do desafio com blob Git `6c873eb7dd1955ebccfb730bcd98143373cbaab2`, 5.320 bytes e SHA-256 `8574dbc68bdf81d2cb77bfbf84ddeb98f7d3392b9110d37a17de1bd3954cdf20`.
- **Evidência:** este ledger e os documentos oficiais vinculados abaixo.
- **Limitação:** esta iteração valida a absorção do briefing, não a qualidade, licença ou conteúdo real dos datasets; isso será verificado na etapa de pesquisa.

### Ledger das passadas

| Passada | Lente | Novos achados |
|---|---|---|
| 1 | leitura literal do desafio e dos documentos vinculados | três resultados pedidos pelo diretor; diagnóstico, automação e demonstração funcional; dois datasets complementares; process log obrigatório |
| 2 | entregáveis, critérios e métricas | “cruzar” significa combinar evidências, não fabricar união entre linhas; custo é opcional e exige premissas; o protótipo deve ser avaliado fora dos exemplos usados na construção |
| 3 | leitura adversarial e limites | o pedido executivo torna a demonstração funcional necessária; `92%` é exemplo de especificidade, não meta; PII não entra em features ou evidências; economia deve partir de horas observáveis e custo apenas como cenário explícito |
| 4 | conferência contra todos os entregáveis, critérios e regras do PR | nenhum |
| 5 | conferência final do conteúdo e da versão do arquivo | nenhum |

**Resultado:** duas passadas consecutivas sem descoberta nova. Goal de absorção atingido.

### Compreensão consolidada

O desafio exige uma entrega única com três partes conectadas: diagnóstico operacional quantificado no Dataset 1, fronteira explícita entre automação e julgamento humano usando evidências dos dois datasets e um protótipo funcional testado em dados reais não escolhidos para favorecer o resultado.

Os datasets são complementares, mas representam contextos e taxonomias diferentes e não oferecem chave comum. Portanto, não haverá join por linha nem transferência silenciosa de categorias. O Dataset 1 sustenta gargalos, satisfação e desperdício; o Dataset 2 pode sustentar a avaliação de classificação em oito tópicos. A integração válida ocorre no desenho do processo futuro e nas decisões de automação.

“Influenciar satisfação” será tratado como associação observada, não causalidade provada. “Desperdício recuperável” não será igualado automaticamente ao tempo total de resolução. Sem custo operacional fornecido, qualquer valor financeiro será cenário identificado por premissas, enquanto horas permanecem a unidade verificável principal.

O protótipo precisa facilitar o trabalho diário do agente, expor categoria, prioridade, confiança, justificativa e fallback humano quando aplicável. Automatizar 100% é incompatível com o briefing; exemplos dos dados deverão justificar onde a IA para e a pessoa assume.

### Fontes oficiais lidas

- [Challenge 002 — Redesign de Suporte](https://github.com/luisroquette/ai-master-challenge/tree/main/challenges/process-002-support)
- [README geral](https://github.com/luisroquette/ai-master-challenge)
- [Guia de submissão](https://github.com/luisroquette/ai-master-challenge/blob/main/submission-guide.md)
- [Regras do Pull Request](https://github.com/luisroquette/ai-master-challenge/blob/main/CONTRIBUTING.md)

## I02 — Adoção de Spec-Driven Development — 2026-09-21 14:32 BRT

- **Objetivo:** conduzir a solução do Challenge 002 por uma especificação verificável antes de implementar análise, automação ou interface.
- **IA/ferramenta:** plugin SDD `3.6.0` do Context Engineering Kit para Claude Code, com os componentes `add-task`, `plan-task`, `implement-task`, `brainstorm` e `create-ideas`.
- **Ação ou prompt:** Luis decidiu usar Spec-Driven Development como metodologia do desafio e indicou o recurso `https://claudecowork.im/resources/sdd` e o repositório `NeoLabHQ/context-engineering-kit`.
- **Resultado:** marketplace `context-engineering-kit` adicionado; plugin `sdd@context-engineering-kit` instalado no escopo do usuário, habilitado e conferido pelo inventário do Claude Code.
- **Julgamento humano:** a escolha metodológica é de Luis. O fluxo adotado será: preservar a intenção em uma tarefa, refinar a especificação e seus critérios, revisar a especificação humana e só então implementar e verificar por fases.
- **Verificação:** `claude plugin details sdd@context-engineering-kit` retornou versão `3.6.0`, cinco skills, oito agentes e status habilitado em `claude plugin list`.
- **Evidência:** [repositório oficial](https://github.com/NeoLabHQ/context-engineering-kit), [documentação SDD](https://neolab.gitbook.io/cek/plugins/sdd) e saída terminal registrada nesta sessão.
- **Limitação:** o comando publicado pelo diretório externo, `npx skills add ... --skill sdd`, não encontrou a skill porque o repositório atual distribui SDD como plugin. A instalação foi corrigida pelo fluxo oficial de marketplace do Claude Code. A nova sessão do Claude Code deve ser reiniciada para carregar o plugin.

### Regra de convivência com o briefing

SDD organiza o trabalho, mas não substitui os gates já definidos. A pesquisa comparativa e a reprodução mínima de candidatos continuam antes de qualquer implementação. A especificação deve manter os dois datasets separados no nível de linha, explicitar premissas de custo, proteger PII, reservar fallback humano e exigir validação fora dos exemplos de construção.

## I03 — Correção: SDD executado no Codex — 2026-09-21 14:36 BRT

- **Objetivo:** garantir que a metodologia SDD seja executada neste agente Codex, sem depender de uma sessão do Claude Code.
- **IA/ferramenta:** skills nativas do Codex em `~/.codex/skills`: `add-task`, `plan-task`, `implement-task`, `brainstorm` e `create-ideas`.
- **Ação ou prompt:** Luis corrigiu explicitamente a interpretação anterior: “é para usar aqui, no CODEX!”.
- **Resultado:** os cinco componentes foram detectados no catálogo ativo do Codex e seus arquivos `SKILL.md` foram verificados localmente. O Challenge 002 usará esses componentes nesta sessão e nas próximas etapas.
- **Julgamento humano:** a execução no Claude Code foi uma interpretação incorreta da IA causada pelo argumento `--agent claude-code` do comando publicado. Luis definiu o Codex como executor correto.
- **Verificação:** `npx skills list -g --agent codex --json` reconheceu os cinco componentes com agente `Codex`; os arquivos existem em `/Users/luisroquette/.codex/skills/`.
- **Evidência:** catálogo ativo desta sessão e hashes locais dos cinco `SKILL.md`.
- **Limitação:** a cópia instalada no Claude Code não será usada neste desafio; sua presença não altera arquivos ou execução do worktree.

## I04 — Documentar é parte central da entrega — 2026-09-21 14:39 BRT

- **Objetivo:** tratar o diário como parte da qualidade da submissão, com importância igual ou superior à entrega final.
- **Ação ou prompt:** Luis definiu: registrar continuamente o processo em fragmentos curtos, objetivos e diretos, destacando especialmente os pontos que ele indicar na conversa. Corrigir o português antes de incorporar qualquer texto ao diário.
- **Resultado:** cada marco relevante passará a deixar evidência contemporânea de decisão, hipótese, erro, correção, validação e contribuição humana, sem reconstrução retroativa.
- **Julgamento humano:** “Ganha quem documenta.” Como referência criativa, Luis citou Silvio Santos: “Você sabe por que o ovo de galinha vende mais do que o de pata? Porque a galinha canta quando bota.”
- **Verificação:** regra registrada neste diário antes da próxima etapa do SDD.
- **Limitação:** concisão não pode apagar evidência necessária; o diário não incluirá raciocínio interno oculto, segredos, credenciais ou dados pessoais.

## I05 — Descoberta socrática antes da SPEC — 2026-09-21 14:41 BRT

- **Objetivo:** discutir exaustivamente o projeto e arquitetar a solução sobre decisões explícitas antes de criar ou revisar qualquer especificação.
- **IA/ferramenta:** skill `brainstorm` da metodologia SDD no Codex, aplicada como método socrático de ondas adaptativas.
- **Ação ou prompt:** Luis identificou corretamente que ainda não existe SPEC e que o projeto sequer foi discutido. Ele definiu um mínimo de cinco ondas de perguntas; cada onda posterior deve depender das respostas anteriores e aprofundar lacunas, conflitos e escolhas descobertas.
- **Resultado esperado:** uma direção validada para problema, usuário, fluxo operacional, evidência, fronteira humano/IA, arquitetura, riscos e critérios de sucesso. Esses temas orientam as ondas, mas não formam um questionário rígido: as respostas determinam a próxima pergunta.
- **Julgamento humano:** o método de ondas adaptativas é uma decisão criativa de Luis. O Codex fará uma pergunta por vez, registrará os destaques de cada resposta e não antecipará a solução.
- **Verificação:** após pelo menos cinco ondas, o desenho será apresentado em seções curtas para validação incremental. Somente depois a skill `add-task` criará a SPEC inicial; `plan-task` fará o refinamento e `implement-task` só poderá começar com a especificação aprovada.
- **Evidência:** respostas desta conversa, síntese validada e futura SPEC vinculada neste diário.
- **Limitação:** cinco ondas são o piso, não o teto. Novas ondas serão abertas enquanto houver decisão material, contradição ou hipótese sem resposta.
- **Formato corrigido por Luis:** todas as ondas usarão perguntas de múltipla escolha, uma por vez. As alternativas posteriores serão adaptadas às respostas anteriores; Luis poderá complementar a opção escolhida com contexto livre.

### Sequência SDD acordada

`brainstorm socrático → síntese validada → add-task → plan-task → revisão humana da SPEC → implement-task`

## I06 — Ledger de perguntas e respostas — 2026-09-21 14:50 BRT

- **Objetivo:** preservar as decisões tomadas durante toda a descoberta socrática, não apenas a síntese final.
- **Regra definida por Luis:** registrar no diário cada pergunta, suas alternativas, a resposta escolhida e a interpretação usada para adaptar a onda seguinte. Corrigir o português sem alterar o sentido da resposta.
- **Formato:** entradas curtas, cronológicas e contemporâneas à conversa.

### Onda 1 — Foco principal do protótipo

**Pergunta:** qual deve ser o foco principal do protótipo?

- **A — Triagem inteligente:** categoria, prioridade, confiança, roteamento e fallback humano.
- **B — Controle de gargalos:** painel com atrasos, desperdício recuperável e ações por impacto.
- **C — Resposta assistida:** sugestões baseadas em tickets semelhantes, com revisão humana.

**Resposta de Luis:** A + B + C.

**Interpretação para a próxima onda:** a solução precisa integrar diagnóstico, decisão operacional e assistência ao agente. A próxima escolha deve definir como esses três resultados formam um único produto demonstrável, sem virar três protótipos desconectados.

### Onda 2 — Forma do produto integrado

**Pergunta:** como triagem inteligente, controle de gargalos e resposta assistida devem formar um único produto?

- **A — Pipeline integrado:** ticket entra, a IA classifica e prioriza, sugere uma resposta, o humano aprova ou assume e o resultado alimenta o painel.
- **B — Três módulos independentes:** triagem, respostas e dashboard funcionam separadamente sobre os mesmos dados.
- **C — Central de comando:** o dashboard é a interface principal; triagem e respostas aparecem como ações dentro dele.

**Resposta de Luis:** A — Pipeline integrado.

**Interpretação para a próxima onda:** o protótipo será uma fatia vertical demonstrável do processo, não uma coleção de telas. A próxima decisão precisa definir os pontos exatos de autonomia da IA e intervenção humana dentro desse pipeline.

### Onda 3 — Fronteira entre IA e humano

**Pergunta:** qual autonomia a IA deve ter no pipeline?

- **A — Copiloto conservador:** a IA recomenda tudo; o humano confirma categoria, prioridade, rota e resposta.
- **B — Autonomia por risco:** a IA roteia automaticamente casos seguros e confiáveis; respostas externas continuam como rascunho; baixa confiança ou tema sensível vai para o humano.
- **C — Automação de casos simples:** a IA também envia respostas automaticamente em FAQs de alta confiança; exceções seguem para o humano.

**Resposta de Luis:** B — Autonomia por risco.

**Interpretação para a próxima onda:** a arquitetura precisa separar decisões internas reversíveis de comunicação externa. Roteamento pode ocorrer automaticamente sob critérios verificáveis; respostas não serão enviadas sem revisão humana. A próxima escolha deve definir como risco e confiança serão combinados no gate.

### Onda 4 — Gate de automação

**Pergunta:** como o gate decide se a IA pode rotear automaticamente?

- **A — Confiança + regras de risco:** exige confiança calibrada e bloqueia temas sensíveis, prioridade crítica, PII ou ambiguidade.
- **B — Apenas confiança do modelo:** automatiza acima de um limite estatístico; abaixo dele, envia ao humano.
- **C — Apenas regras operacionais:** usa palavras-chave, categoria e prioridade; a confiança do modelo serve somente como informação.

**Resposta de Luis:** A — Confiança + regras de risco.

**Interpretação para a próxima onda:** o gate será híbrido e auditável. Um score alto não poderá superar bloqueios explícitos de segurança; a confiança deverá ser calibrada e o motivo da decisão ficará visível. A próxima escolha deve definir como provar, com métricas, que esse equilíbrio produz valor sem esconder risco.

### Onda 5 — Evidência prioritária

**Pergunta:** o que a demonstração precisa provar prioritariamente?

- **A — Segurança:** nenhum caso sensível ou crítico é roteado automaticamente de forma indevida; cobertura vem depois.
- **B — Eficiência:** redução mensurável de trabalho manual e horas recuperáveis; risco aparece como limite.
- **C — Evidência equilibrada:** qualidade e calibração do classificador, cobertura segura da automação e economia operacional rastreável.

**Resposta de Luis:** C — Evidência equilibrada.

**Interpretação para a próxima onda:** a validação não poderá ser resumida a acurácia. Ela deverá conectar desempenho preditivo, confiabilidade das probabilidades, proporção de tickets elegíveis à automação segura e impacto operacional calculado com premissas visíveis. O mínimo de cinco ondas foi cumprido, mas a descoberta continua porque ainda existem decisões materiais de usuário, interface, dados e arquitetura.

### Onda 6 — Usuário principal

**Pergunta:** para quem a experiência principal deve ser desenhada?

- **A — Agente de suporte:** workspace diário com ticket, classificação, risco, resposta sugerida e decisão humana; painel gerencial compacto.
- **B — Gestor de operações:** central de gargalos, métricas e economia; ticket individual como demonstração secundária.
- **C — Duas experiências equivalentes:** cockpit completo do agente e painel completo do gestor, conectados pelo mesmo pipeline.

**Resposta de Luis:** A — Agente de suporte.

**Interpretação para a próxima onda:** a unidade central da interface será o ticket em trabalho. Métricas gerenciais devem nascer das decisões registradas nesse fluxo, sem criar um segundo produto do mesmo tamanho. A próxima escolha deve definir como o agente entra e percorre esse workspace na demonstração.

### Onda 7 — Entrada no workspace

**Pergunta:** como o agente começa o trabalho?

- **A — Fila diária priorizada:** tickets reais de validação ordenados por risco e urgência; o agente abre, revisa e decide.
- **B — Ticket individual:** o agente cola um texto e recebe categoria, prioridade, confiança, rota e resposta sugerida.
- **C — Fila + entrada manual:** combina operação diária com uma caixa para testar novos tickets.

**Resposta de Luis:** A — Fila diária priorizada.

**Interpretação para a próxima onda:** o protótipo deve provar utilidade em uma sequência de trabalho, não apenas em uma inferência isolada. A fila usará dados separados da construção e permitirá rastrear decisão e resultado por ticket. A próxima escolha deve definir o princípio de ordenação da atenção humana.

### Onda 8 — Ordenação da fila humana

**Pergunta:** o que coloca um ticket no topo da fila humana?

- **A — Risco:** temas sensíveis, prioridade crítica e baixa confiança aparecem primeiro.
- **B — Urgência operacional:** maior risco de atraso e descumprimento do atendimento aparece primeiro.
- **C — Prioridade composta e explicável:** combina risco, urgência e incerteza usando somente campos validados nos dados; mostra os motivos do ranking.

**Resposta de Luis:** C — Prioridade composta e explicável.

**Interpretação para a próxima onda:** o ranking não será uma caixa-preta nem dependerá de campos presumidos. Cada ticket exibirá os fatores que elevaram sua posição; a fórmula final dependerá da auditoria dos datasets. A próxima escolha deve definir a origem e o nível de automação da resposta sugerida.

### Onda 9 — Origem da resposta sugerida

**Pergunta:** como a resposta sugerida deve ser produzida?

- **A — Recuperação de casos similares:** busca resoluções históricas semelhantes, mostra as fontes e produz um rascunho editável; só entra se a qualidade dos textos for validada.
- **B — Templates por categoria:** usa respostas padronizadas e regras, sem geração livre.
- **C — Modelo generativo local:** cria resposta fundamentada em casos similares, sem API paga, com maior complexidade e risco de alucinação.

**Resposta de Luis:** A — Recuperação de casos similares.

**Interpretação para a próxima onda:** a resposta assistida será fundamentada e rastreável, não geração livre. A auditoria do campo `Resolution` decidirá se ele é utilizável; baixa similaridade ou histórico inadequado exigirá fallback humano. A próxima escolha deve definir quais decisões e correções humanas retornam ao sistema.

### Onda 10 — Feedback humano

**Pergunta:** o que o sistema deve aprender com a decisão humana?

- **A — Feedback auditável:** registra aprovação, edição ou rejeição, motivo e diferença entre sugestão e resposta final; usa isso somente em avaliações e versões futuras.
- **B — Feedback mínimo:** registra apenas aprovação ou rejeição para métricas.
- **C — Aprendizado automático imediato:** cada decisão altera o comportamento do sistema em produção.

**Resposta de Luis:** A — Feedback auditável.

**Interpretação para a próxima onda:** o protótipo preservará a trilha entre recomendação, intervenção humana e resultado, mas não fará aprendizado online. Isso evita mudanças não validadas e cria dados para melhoria posterior. A próxima escolha deve impedir que o painel confunda métricas históricas observadas com resultados simulados ou projetados do protótipo.

### Onda 11 — Separação das evidências

**Pergunta:** como o painel deve apresentar evidências?

- **A — Duas camadas separadas:** diagnóstico histórico observado e avaliação ou projeção do protótipo aparecem em blocos distintos, com premissas visíveis.
- **B — Somente histórico:** mostra gargalos e satisfação do Dataset 1; métricas do protótipo ficam fora do painel.
- **C — Visão unificada:** mistura histórico, simulação e projeções em uma única sequência operacional.

**Resposta de Luis:** A — Duas camadas separadas.

**Interpretação para a próxima onda:** o painel diferenciará fatos, resultados de teste e cenários. Nenhuma projeção de horas ou custo poderá parecer observação real. A próxima escolha deve definir o formato executável da entrega sem antecipar o framework antes da pesquisa técnica.

### Onda 12 — Formato executável

**Pergunta:** qual deve ser o formato executável da entrega?

- **A — Aplicação web local e autocontida:** roda com um comando, sem API paga; o framework será decidido após pesquisa e reprodução de candidatos.
- **B — Notebook interativo:** combina análise, modelo e demonstração no mesmo arquivo.
- **C — Aplicação hospedada:** acesso por URL pública, com infraestrutura e deploy incluídos no escopo.

**Resposta de Luis:** A — Aplicação web local e autocontida.

**Interpretação para a próxima onda:** a solução deve ser reproduzível sem credenciais, serviços externos ou custo variável. A pesquisa escolherá a menor tecnologia capaz de entregar a experiência. A próxima decisão deve definir a filosofia de seleção do classificador sem fixar prematuramente um algoritmo.

### Onda 13 — Seleção do classificador

**Pergunta:** como o classificador deve ser escolhido?

- **A — Baseline primeiro:** comparar regras simples e modelo textual leve; só adotar embeddings ou modelo maior se houver ganho mensurável.
- **B — Semântico primeiro:** começar com embeddings para capturar significado além de palavras-chave.
- **C — Zero-shot primeiro:** usar um modelo pronto sem treinamento específico e medir sua aderência às oito categorias.

**Resposta de Luis:** A — Baseline primeiro.

**Interpretação para a próxima onda:** o algoritmo não será escolhido por novidade. A pesquisa reproduzirá candidatos e o baseline mais simples permanecerá se alternativas mais complexas não melhorarem métricas relevantes. A próxima decisão deve explicitar qual erro operacional é mais caro, orientando calibração e abstinência.

### Onda 14 — Custo assimétrico do erro

**Pergunta:** qual erro operacional é mais caro?

- **A — Automação indevida:** é pior rotear automaticamente um caso errado ou sensível; o sistema prefere encaminhar dúvidas ao humano.
- **B — Excesso de fallback:** é pior mandar tickets seguros demais ao humano; o sistema aceita mais risco para ampliar cobertura.
- **C — Custos equivalentes:** falsos roteamentos e fallbacks humanos recebem o mesmo peso.

**Resposta de Luis:** A — Automação indevida.

**Interpretação para a próxima onda:** os thresholds serão conservadores e avaliados por risco seletivo, não apenas por cobertura. Abstinência é comportamento correto quando a confiança ou as regras não sustentam automação. A próxima escolha deve definir como transformar cobertura segura em horas e custo sem fabricar ROI.

### Onda 15 — Estimativa de economia

**Pergunta:** como estimar economia sem fabricar ROI?

- **A — Calculadora de cenários:** mostra horas observáveis e permite ajustar tempo por tarefa e custo por hora; separa cenários conservador, base e otimista.
- **B — Somente horas:** quantifica tempo recuperável, sem converter para dinheiro.
- **C — Um valor executivo:** apresenta uma única estimativa mensal de economia baseada em premissas fixas.

**Resposta de Luis:** A — Calculadora de cenários.

**Interpretação para a próxima onda:** horas derivadas dos dados permanecerão separadas de parâmetros fornecidos pelo usuário. Valores financeiros serão cenários, nunca fatos observados. A próxima escolha deve definir se as decisões humanas e sua trilha de auditoria sobrevivem ao encerramento da aplicação local.

### Onda 16 — Persistência do feedback

**Pergunta:** como preservar o feedback humano?

- **A — Persistência local auditável:** salva decisões, edições e motivos em armazenamento local simples; permite exportar o histórico.
- **B — Somente durante a sessão:** mantém o feedback em memória e permite baixar um arquivo antes de fechar.
- **C — Banco externo:** persiste tudo em serviço remoto, exigindo configuração e credenciais.

**Resposta de Luis:** A — Persistência local auditável.

**Interpretação para a próxima onda:** a trilha de auditoria será persistida localmente com tecnologia nativa ou já instalada, escolhida após a pesquisa. Nenhuma credencial ou infraestrutura remota será necessária. PII deverá ser removida antes da persistência. A próxima escolha deve limitar o painel gerencial ao conjunto mínimo de decisões úteis.

### Onda 17 — Primeira visão gerencial

**Pergunta:** o que o gestor deve ver primeiro?

- **A — Scorecard decisório:** gargalo principal, fatores associados à satisfação, cobertura segura da automação e horas ou economia por cenário.
- **B — Explorador analítico:** muitos filtros, cruzamentos e gráficos para investigação livre.
- **C — Narrativa executiva:** conclusões e recomendações em texto, com poucos indicadores.

**Resposta de Luis:** A — Scorecard decisório.

**Interpretação para a próxima onda:** a camada gerencial responderá quatro decisões e oferecerá evidência detalhada sob demanda, sem virar um BI genérico. A próxima escolha deve tornar explícito o limite do MVP e impedir integrações especulativas de consumirem o tempo da demonstração principal.

### Onda 18 — Limite do MVP

**Pergunta:** qual deve ser o limite do MVP?

- **A — Demonstração local completa:** pipeline funcional com dados reais, sem integração com helpdesk, envio real de mensagens, autenticação, multiempresa ou aprendizado online.
- **B — Integração real:** conectar o protótipo a um helpdesk ou canal de atendimento.
- **C — Plataforma extensível:** incluir API, autenticação e estrutura para múltiplas empresas desde o início.

**Pedido de Luis:** o Codex deve decidir após revisar novamente o repositório oficial, sem transferir essa avaliação ao usuário.

**Decisão do Codex:** A — Demonstração local completa.

**Confirmação de Luis:** decisão aceita; seguir com esse limite de MVP.

**Verificação:** reavaliação do fork em `main` no commit `4aed364d572fabe0f1fff1f0c6f32960b30fe575`; README do Challenge 002 no blob `6c873eb7dd1955ebccfb730bcd98143373cbaab2`, além do README geral, guia de submissão e regras do PR.

**Fundamento:** o desafio pede diagnóstico, proposta de automação e algo funcional rodando com dados reais; fornece orçamento de 4–6 horas e aceita código ou aplicação com instruções de setup. Não exige integração com helpdesk, envio real, autenticação, multiempresa, API pública ou deploy. Construir B ou C consumiria o prazo em infraestrutura não avaliada e reduziria a profundidade das evidências obrigatórias.

**Interpretação para a próxima onda:** o MVP termina em uma aplicação local reproduzível que demonstra o pipeline ponta a ponta, persiste decisões localmente e exporta evidências. Integrações externas serão descritas apenas como evolução, não implementadas.

### Onda 19 — Validação do classificador

**Pergunta:** como validar o classificador sem favorecer o resultado?

- **A — Teste congelado + validação cruzada:** separa uma amostra estratificada intocável; usa validação cruzada no restante; mede por classe, calibração e cobertura segura.
- **B — Um único holdout:** separa treino e teste uma vez e reporta o resultado.
- **C — Amostra demonstrativa:** avalia manualmente um conjunto pequeno de tickets representativos.

**Resposta de Luis:** A — Teste congelado + validação cruzada.

**Interpretação para a próxima onda:** seleção de algoritmo e threshold ocorrerá sem consultar o teste final. O resultado reportará métricas globais e por classe, confiabilidade das probabilidades e trade-off entre cobertura e erro seletivo. A próxima escolha deve definir uma avaliação igualmente séria para a recuperação de respostas.

### Onda 20 — Validação das respostas recuperadas

**Pergunta:** como validar as respostas recuperadas?

- **A — Rubrica humana em tickets não vistos:** avalia relevância, correção, segurança e necessidade de edição; registra concordância e falhas reais.
- **B — Similaridade automática:** considera o score de similaridade como medida principal de qualidade.
- **C — Casos ilustrativos:** apresenta exemplos bons e ruins sem avaliação estruturada.

**Resposta de Luis:** A — Rubrica humana em tickets não vistos.

**Interpretação para a próxima onda:** similaridade será apenas um sinal de recuperação, não prova de resposta adequada. A avaliação preservará exemplos de falha e esforço de edição. A próxima escolha deve definir o comportamento seguro quando nenhum caso histórico satisfizer a rubrica ou o threshold mínimo.

### Onda 21 — Fallback da resposta assistida

**Pergunta:** o que acontece quando não há resolução histórica segura?

- **A — Sem sugestão + escalonamento:** explica a insuficiência de evidência e entrega o ticket ao humano.
- **B — Template neutro:** oferece uma resposta genérica de recebimento, claramente identificada como template.
- **C — Geração local:** produz um rascunho mesmo sem precedente suficientemente similar.

**Resposta de Luis:** A — Sem sugestão + escalonamento.

**Interpretação para a próxima onda:** abstinência também vale para respostas. O produto deve mostrar ausência de evidência em vez de preencher o espaço com texto plausível. A próxima escolha precisa reconciliar os dois datasets dentro da mesma arquitetura sem inventar join, taxonomia comum ou transferência de domínio.

### Onda 22 — Convivência dos dois datasets

**Pergunta:** como usar os dois datasets sem inventar conexão?

- **A — Motor comum, modelos separados:** mesma interface e mesmos gates; Dataset 1 sustenta operação e respostas, Dataset 2 sustenta classificação IT em sua própria taxonomia.
- **B — Transferência explícita:** treina no Dataset 2 e aplica ao Dataset 1 como experimento de mudança de domínio, exibindo a perda de qualidade.
- **C — Taxonomia unificada:** combina categorias dos dois datasets em um único modelo criado manualmente.

**Resposta de Luis:** A — Motor comum, modelos separados.

**Interpretação para a próxima onda:** componentes de classificação, calibração, abstinência e auditoria serão reutilizados, mas cada domínio manterá seus próprios dados, rótulos, métricas e limitações. A próxima escolha deve definir como essa separação aparece na navegação sem transformar o produto em duas aplicações.

### Onda 23 — Navegação entre domínios

**Pergunta:** como mostrar os dois domínios na aplicação?

- **A — Operação principal + laboratório IT:** Dataset 1 alimenta o workspace diário; Dataset 2 aparece em uma área de validação do classificador.
- **B — Seletor de domínio:** o agente alterna entre Customer Support e IT, com filas equivalentes.
- **C — Operação única:** a aplicação mostra apenas Dataset 1; os resultados do Dataset 2 aparecem somente no relatório técnico.

**Resposta de Luis:** A — Operação principal + laboratório IT.

**Interpretação para a próxima onda:** o workspace do agente permanece coeso e orientado ao Dataset 1. O laboratório IT prova a capacidade de classificação no segundo dataset sem simular continuidade operacional inexistente. A próxima onda confrontará seis arquiteturas completas antes da síntese incremental do desenho.

### Onda 24 — Arquitetura completa

**Pergunta:** qual das seis arquiteturas deve seguir para a síntese?

- **A — Support Decision Copilot:** fila do agente, gate de risco, resposta recuperada, feedback auditável, scorecard e laboratório IT.
- **B — Plataforma modular por domínio:** Customer Support e IT como módulos equivalentes sobre um motor compartilhado.
- **C — Control Tower operacional:** diagnóstico e ROI como núcleo; atendimento individual como função secundária.
- **D — Analytics + classificador separado:** dashboard e ferramenta de classificação sem fluxo integrado.
- **E — Agente autônomo generativo:** automatiza respostas e roteamento com mínima intervenção humana.
- **F — Plataforma enterprise integrada:** helpdesk, autenticação, APIs e multiempresa no MVP.

**Pedido de Luis:** o Codex deve confrontar as opções com o desafio oficial e decidir com segurança, sem devolver a escolha ao usuário.

**Decisão do Codex:** A — Support Decision Copilot.

**Verificação:** reconsulta do Challenge 002 no blob `6c873eb7dd1955ebccfb730bcd98143373cbaab2`, no commit `4aed364d572fabe0f1fff1f0c6f32960b30fe575` da `main`.

**Fundamento:** A é a única arquitetura que cobre simultaneamente o diagnóstico obrigatório, a proposta realista de automação, a demonstração funcional, os dois datasets, o trabalho diário do agente, a fronteira humano/IA e a estimativa de horas ou ROI. B dilui o caso de uso principal; C rebaixa o protótipo operacional; D fragmenta a proposta; E viola o alerta contra automação total; F excede o orçamento de 4–6 horas com infraestrutura não solicitada.

**Resultado:** arquitetura escolhida para a síntese incremental do desenho e futura SPEC.

## I07 — Síntese incremental da arquitetura — 2026-09-21 16:39 BRT

- **Objetivo:** validar o desenho do Support Decision Copilot em seções curtas antes de criar a SPEC.
- **Método:** apresentar uma seção de 200–300 palavras por vez, oferecer validação de múltipla escolha e registrar aprovação ou correção antes de avançar.
- **Estado inicial:** nenhuma SPEC criada; arquitetura A selecionada após 24 ondas socráticas.

### Seção 1 — Arquitetura e fluxo principal — proposta

O Support Decision Copilot será uma aplicação web local e autocontida com duas áreas claramente separadas: **Operação de Suporte** e **Laboratório IT**. A área principal usa o Dataset 1. Uma preparação offline remove PII, audita qualidade e produz métricas observadas. A fila diária recebe somente tickets reservados para validação, evitando demonstrar o sistema nos mesmos exemplos usados na construção.

Cada ticket percorre um pipeline único: classificação e prioridade sugeridas, confiança calibrada, regras explícitas de risco, decisão de roteamento e resposta assistida. A ordenação combina apenas sinais validados nos dados e mostra por que cada item subiu na fila. O roteamento automático exige simultaneamente confiança suficiente e ausência de bloqueios; caso sensível, crítico, ambíguo ou incerto vai para revisão humana.

A resposta assistida recupera resoluções semelhantes somente do conjunto permitido para referência, exibe os casos usados e entrega um rascunho editável. Sem similaridade segura, o sistema se abstém. O agente aprova, edita, rejeita ou escalona; a decisão, o motivo e a diferença entre sugestão e resposta final entram em uma trilha local auditável e exportável.

O scorecard gerencial deriva desse fluxo, mas separa três naturezas de evidência: histórico observado, desempenho medido do protótipo e cenários de horas ou custo. O Laboratório IT usa o Dataset 2, sua taxonomia de oito categorias e seu próprio modelo. Ele reutiliza classificação, calibração e abstinência, mas nunca mistura registros ou rótulos com o Dataset 1. Framework, algoritmo e armazenamento serão escolhidos somente após pesquisa e reprodução técnica.

**Pergunta de validação:** esta arquitetura e este fluxo principal estão corretos para avançar?

**Validação de Luis:** A — Seção 1 aprovada sem ajustes.

### Seção 2 — Componentes e fronteiras dos dados — proposta

A solução terá componentes pequenos, com arquivos de entrada e saída explícitos. O **preparador de dados** valida schemas, mede ausências e duplicidades, remove PII, normaliza tempos e cria manifests reproduzíveis de treino, validação e teste. Cada dataset terá seu próprio adaptador; nenhuma função aceitará registros dos dois domínios como se compartilhassem a mesma taxonomia. Dados brutos não serão publicados. Scripts e instruções permitirão baixá-los das fontes oficiais e regenerar artefatos derivados seguros.

O **motor analítico** processa o Dataset 1 e gera tabelas rastreáveis para gargalos, satisfação e desperdício recuperável. Ele salva resultados estruturados consumidos pelo scorecard, evitando recalcular regras de negócio na interface. Associações serão identificadas como associações; horas observadas, premissas ajustáveis e valores financeiros permanecerão em campos diferentes.

O **motor de decisão** expõe a mesma interface para modelos separados de Customer Support e IT: classe, probabilidades calibradas, confiança, versão do artefato e explicação. Um **gate de risco determinístico** recebe essa saída e regras auditáveis, retornando `auto_route` ou `human_review` com códigos de motivo. Thresholds vêm da validação, nunca de ajuste visual na demonstração.

O **recuperador de respostas** indexa apenas descrições e resoluções sanitizadas do conjunto permitido. Ele devolve casos similares, scores e identificadores de origem; abaixo do limite, devolve abstinência. A **aplicação web** apenas orquestra esses componentes, exibe artefatos e registra decisões humanas em persistência local simples. A interface não treina modelos nem altera thresholds. Um comando reproduz análise e modelos; outro inicia a aplicação. Frameworks, bibliotecas e formato de persistência continuam abertos até a pesquisa técnica provar a opção mínima adequada.

**Pergunta de validação:** estes componentes e limites de dados estão corretos para avançar?

**Validação de Luis:** A — Seção 2 aprovada sem ajustes.

### Seção 3 — Segurança, abstinência e falhas — proposta

O sistema adotará **falha segura** como padrão. Schema incompatível, coluna obrigatória ausente, artefato corrompido ou versão divergente interrompe apenas a função afetada e informa arquivo, causa e correção. Conversões inválidas de datas, tempos ou notas não serão silenciosamente transformadas em zero: ficarão isoladas, quantificadas e visíveis no relatório de qualidade. A aplicação nunca iniciará roteamento com modelo ou calibração ausentes.

Qualquer erro no classificador, no cálculo de confiança ou no gate produz `human_review`. Regras de risco têm precedência sobre probabilidade. Temas sensíveis serão definidos a partir da inspeção dos dados e de uma política documentada; nenhum rótulo será inventado antes dessa análise. PII será removida na preparação e mascarada novamente na apresentação como defesa adicional. Dados exportados não incluirão nome ou email do cliente.

O recuperador só sugere resposta quando o histórico sanitizado, a similaridade e a rubrica mínima sustentarem o uso. Índice indisponível, resolução vazia, fonte inadequada ou score insuficiente resultam em abstinência explicada. O sistema não preenche esse vazio com geração livre. O agente sempre pode rejeitar, editar ou escalonar, e nenhuma resposta é enviada externamente.

A persistência local deverá gravar cada decisão de modo atômico e manter o registro anterior se ocorrer falha. A interface distinguirá estado carregando, função indisponível e artefato desatualizado. Cada exportação carregará versão dos dados, modelo, threshold e regras usadas. Não haverá credenciais ou chamadas externas. Se o Dataset 1 ou o Dataset 2 não sustentar uma função planejada, a função será removida ou rebaixada a hipótese, e a limitação será registrada em vez de ser simulada.

**Pergunta de validação:** esta política de segurança e falhas está correta para avançar?

**Validação de Luis:** A — Seção 3 aprovada sem ajustes.

### Seção 4 — Validação, testes e evidências — proposta

A validação começará antes dos modelos. Checks de dados confirmarão schema, tipos, unicidade, ausências, duplicidades, faixas, cardinalidades e remoção de PII. Cada exclusão ou coerção terá contagem. O diagnóstico operacional terá testes de denominador e reconciliação: totais por canal, prioridade e tipo precisam retornar ao universo correto; comparações de satisfação e tempo deverão informar amostra, dispersão e dados ausentes, não apenas médias.

Cada classificador será comparado com baselines simples. A seleção usará validação cruzada somente no conjunto de desenvolvimento. O teste estratificado permanecerá congelado até modelo, calibração, regras e thresholds estarem definidos. A avaliação reportará macro-F1, precisão e recall por classe, matriz de confusão, qualidade da calibração e curva de risco versus cobertura. O gate terá testes diretos de fronteira: regra sensível vence confiança alta; confiança insuficiente gera revisão; entrada inválida nunca autoriza automação.

A recuperação de respostas será avaliada em tickets não vistos, sem resoluções do teste dentro do índice. Uma rubrica humana medirá relevância, correção, segurança e esforço de edição. Casos sem precedente adequado testarão explicitamente a abstinência. Exemplos bons e ruins serão preservados como evidência, sem substituir as métricas agregadas.

O fluxo ponta a ponta validará fila, explicação, decisão humana, persistência, exportação e scorecard usando uma amostra definida antes de observar resultados. Os artefatos incluirão relatório de qualidade, tabelas analíticas, métricas versionadas, decisões do gate, avaliação da recuperação, log exportado e screenshot real da aplicação. Comandos documentados regenerarão tudo. Uma lógica não trivial só será considerada pronta com teste reproduzível; qualquer falha conhecida bloqueia a alegação correspondente.

**Pergunta de validação:** esta estratégia de testes e evidências está correta para avançar?

**Validação de Luis:** A — Seção 4 aprovada sem ajustes.

### Seção 5 — Experiência e hierarquia da interface — proposta

A aplicação abrirá na **Fila de hoje**, não em um dashboard abstrato. Cada linha mostrará posição, prioridade composta, categoria sugerida, confiança, estado do gate e até três motivos objetivos. A ordenação será compreensível sem depender de cor; rótulos, ícones e texto manterão acessibilidade. PII permanecerá mascarada em lista, detalhe, screenshots e exportações.

Ao abrir um ticket, o agente verá três zonas. O contexto sanitizado fica em primeiro plano. Ao lado, o painel de decisão apresenta classificação, prioridade, probabilidades calibradas, regras acionadas e veredito `auto_route` ou `human_review`. A área de resposta mostra casos similares com identificadores rastreáveis, score e resolução histórica, seguida do rascunho editável. Sem evidência suficiente, ela mostra abstinência e motivo, nunca uma caixa vazia que sugira erro.

As ações serão poucas: **aprovar**, **editar e aprovar**, **rejeitar** ou **escalonar**. Rejeição e escalonamento pedem motivo curto. Após salvar, a interface confirma a gravação e exibe o evento na trilha auditável. Nenhuma ação envia mensagem real. Filtros essenciais permitem focar revisão humana, risco, categoria e prioridade; busca e customizações extensas ficam fora do MVP.

Uma navegação secundária leva ao **Scorecard**, dividido visualmente em Diagnóstico Observado, Avaliação do Protótipo e Cenários. A calculadora mostra premissas editáveis e nunca mistura projeção com histórico. O **Laboratório IT** exibe métricas, matriz de confusão, calibração e casos do teste congelado em sua própria taxonomia. Uma área de **Evidências** oferece versões, comandos de reprodução e exportações. O desenho será desktop-first, responsivo o suficiente para leitura, com estados de carregamento, indisponibilidade e erro explícitos.

**Pergunta de validação:** esta experiência e hierarquia estão corretas para avançar?

**Validação de Luis:** A — Seção 5 aprovada sem ajustes.

### Seção 6 — Entregáveis, limites e definição de pronto — proposta

A entrega pública ficará inteiramente em `submissions/luis-roquette/`. Ela conterá um README executivo com achados, decisões e instruções; a aplicação e os scripts reproduzíveis em `solution/002-support/`; a pesquisa de soluções existentes em `research/002-support.md`; o diário contemporâneo; e evidências como tabelas, métricas, exportações e screenshot real. Dados brutos, PII, credenciais e artefatos sem licença de redistribuição não entrarão no PR.

Antes de implementar, a Regra Zero pesquisará GitHub, Reddit e documentação oficial, comparará pelo menos três candidatos quando existirem e reproduzirá a menor prova do melhor candidato. A escolha de framework, classificador, calibração, recuperação e persistência ficará registrada. SDD transformará o desenho aprovado em tarefa, análise, arquitetura e passos verificáveis; Ponytail removerá qualquer componente que não sustente um critério do desafio.

O desafio estará pronto somente quando os dois datasets forem usados dentro de seus limites; o diagnóstico gerar números rastreáveis; o pipeline local rodar com um comando; classificação, calibração, gate e recuperação forem avaliados fora dos dados de construção; a fronteira humano/IA aparecer na interface; feedback persistir e exportar; horas e cenários financeiros mostrarem premissas; testes passarem; e a aplicação real estiver documentada por screenshot. Limitações e hipóteses rejeitadas serão entregáveis, não notas escondidas.

Ficam fora do MVP: helpdesk real, envio de mensagens, APIs pagas, autenticação, multiempresa, deploy obrigatório, aprendizado online, taxonomia unificada e afirmações causais não sustentadas. Se os dados invalidarem classificação, resposta assistida ou ROI, a função será reduzida e a evidência da invalidação terá prioridade sobre o plano. Após esta seção ser aprovada, `add-task` criará a primeira SPEC; nenhuma implementação começará antes de `plan-task` e da revisão humana dessa SPEC.

**Pergunta de validação:** estes entregáveis, limites e critérios de pronto estão corretos para encerrar o desenho e criar a SPEC?

**Validação de Luis:** A — Seção 6 aprovada; autorizado encerrar a exploração e criar a SPEC.

## I08 — Fechamento da exploração e autorização da SPEC — 2026-09-21 16:49 BRT

- **Objetivo:** encerrar formalmente a descoberta antes de transformar decisões em especificação.
- **Método executado:** 24 ondas socráticas adaptativas, comparação de seis arquiteturas e síntese incremental em seis seções de 200–300 palavras.
- **Resultado:** arquitetura **Support Decision Copilot** escolhida; arquitetura, componentes, fluxo de dados, segurança, falhas, testes, interface, entregáveis, limites e definição de pronto foram aprovados sem ajustes.
- **Julgamento humano:** Luis aprovou cada seção e autorizou explicitamente a criação da SPEC somente após o fechamento completo da exploração.
- **Verificação:** ledger das Ondas 1–24 e Seções 1–6 preservado neste diário; worktree limpo antes da criação do artefato SDD.
- **Evidência:** `.specs/tasks/draft/implement-support-decision-copilot.feature.md` dentro do diretório permitido do Challenge 002.
- **Limitação:** a SPEC criada por `add-task` ainda é um rascunho; pesquisa, análise e refinamento por `plan-task` continuam obrigatórios antes de qualquer implementação.

**Decisão:** exploração encerrada e SPEC inicial autorizada.

## I09 — Fechamento da SPEC inicial e abertura do plano — 2026-09-21 17:05 BRT

- **Etapa encerrada:** criação da SPEC inicial do Support Decision Copilot com requisitos, limites, critérios de validação e gates de processo aprovados.
- **Artefato:** `solution/002-support/.specs/tasks/draft/implement-support-decision-copilot.feature.md`.
- **Estado:** SPEC em `draft`; nenhuma implementação iniciada.
- **Próximo método:** criar e otimizar o plano de implementação com a skill `writing-plans`, mantendo a SPEC como fonte de verdade.
- **Loop de qualidade:** revisar o plano em cascata até obter pelo menos duas passadas consecutivas sem melhorias ou otimizações substanciais; qualquer melhoria substancial reinicia a contagem.
- **Registro:** cada passada documentará foco, achados, alterações e estado da sequência.

**Decisão:** SPEC inicial encerrada como insumo aprovado; planejamento detalhado autorizado, sem autorização para implementar o produto.

## I10 — Loop de otimização do plano — Passada 1 — 2026-09-21 17:28 BRT

- **Foco:** cobertura integral da SPEC e executabilidade do fluxo.
- **Achados substanciais:** faltavam um comando único de demonstração, features e alvos explícitos por domínio, identificador estável para o Dataset 2 e critérios objetivos para thresholds de classificação e recuperação.
- **Correções:** incluído `make demo`; fixados textos/alvos por dataset; definido `row_id` por SHA-256; definidos thresholds por erro seletivo e rubrica humana, com falha segura.
- **Sequência sem melhoria substancial:** 0 de 2.

## I11 — Loop de otimização do plano — Passada 2 — 2026-09-21 17:34 BRT

- **Foco:** falha segura, qualidade mínima dos modelos e completude da auditoria.
- **Achados substanciais:** o plano ainda poderia automatizar com ganho irrelevante sobre o baseline, aceitar intervalos negativos e exportar decisões sem todas as versões nem diferença de edição.
- **Correções:** automação desativada quando o ganho de macro-F1 for menor que 0,02; intervalos inválidos passam a ser isolados e contados; trilha ganhou versões de dados/regras e `edit_ratio`.
- **Sequência sem melhoria substancial:** 0 de 2.

## I12 — Loop de otimização do plano — Passada 3 — 2026-09-21 17:41 BRT

- **Foco:** reprodução a partir de checkout limpo e rastreabilidade das regras.
- **Achados substanciais:** o comando único ainda pressupunha dados colocados manualmente; regras sensíveis e `rules_version` não tinham artefato explícito.
- **Correções:** `make demo` passou a encadear setup, download público, reprodução e app; criado `risk-policy.json` com categorias humanas, fórmula, versão e justificativa.
- **Sequência sem melhoria substancial:** 0 de 2.

## I13 — Loop de otimização do plano — Passada 4 — 2026-09-21 17:49 BRT

- **Foco:** buildabilidade dos comandos e ausência de placeholders.
- **Achado substancial:** assinaturas abreviadas com reticências contrariavam o gate de plano completo; o smoke test com `timeout` terminaria em código 124 mesmo quando saudável.
- **Correções:** contratos foram descritos sem corpo fictício; smoke test agora consulta o endpoint de saúde, encerra o processo e valida a saída esperada.
- **Sequência sem melhoria substancial:** 0 de 2.

## I14 — Loop de otimização do plano — Passada 5 — 2026-09-21 17:56 BRT

- **Foco:** cobertura dos estados de falha, cenários executivos e avaliação final da recuperação.
- **Achados substanciais:** faltavam tratamento verificável de artefatos ausentes/corrompidos/desatualizados, os três cenários pedidos e uma rubrica separada no teste congelado.
- **Correções:** adicionados testes e mensagens de recuperação de artefatos; presets conservador/base/otimista; amostras independentes de 50 consultas para calibração e teste da recuperação.
- **Sequência sem melhoria substancial:** 0 de 2.

## I15 — Loop de otimização do plano — Passada 6 — 2026-09-21 18:03 BRT

- **Foco:** ordem executável da avaliação humana de recuperação.
- **Achado substancial:** havia dependência circular entre escolher o threshold e gerar a amostra que seria avaliada.
- **Correção:** pipeline em passagens idempotentes: gera template de calibração com drafts bloqueados, consome a rubrica concluída para travar o threshold, gera template de teste e só então publica métricas finais.
- **Sequência sem melhoria substancial:** 0 de 2.

## I16 — Loop de otimização do plano — Passada 7 — 2026-09-21 18:11 BRT

- **Foco:** comandos reais do orquestrador de Codespaces.
- **Achado substancial:** o plano usava `run` com um nome inexistente e tentava validar conteúdo ainda ausente no remoto.
- **Correção:** comandos agora usam `create-run luisroquette/ai-master-challenge submission/luis-roquette-002-support`; checkpoints intermediários são testados localmente, commitados e enviados antes da validação remota.
- **Evidência:** `codespace-manager list` confirmou que não existe Codespace reutilizável desse repositório; `--help` confirmou a interface `create-run`.
- **Sequência sem melhoria substancial:** 0 de 2.

## I17 — Loop de otimização do plano — Passada 8 — 2026-09-21 18:18 BRT

- **Foco:** compatibilidade dos comandos Git com as regras reais do repositório.
- **Achado substancial:** `.gitignore` raiz ignora `submissions/`; `git add` comum não incluiria arquivos novos do plano.
- **Correção:** todos os comandos de inclusão pública usam `git add -f` com caminhos explícitos dentro de `submissions/luis-roquette/`; nenhuma regra global foi afrouxada.
- **Correção editorial:** Passadas 1–8 ordenadas cronologicamente.
- **Sequência sem melhoria substancial:** 0 de 2.

## I18 — Loop de otimização do plano — Passada 9 — 2026-09-21 18:22 BRT

- **Foco:** validade do primeiro gate local em checkout sem testes.
- **Achado substancial:** `pytest` sairia com código 5 porque os testes só seriam criados na etapa seguinte.
- **Correção:** o checkpoint inicial agora usa `python -m compileall -q app.py`; pytest começa somente após existir o primeiro arquivo de teste.
- **Sequência sem melhoria substancial:** 0 de 2.

## I19 — Loop de otimização do plano — Passada 10 — 2026-09-21 18:28 BRT

- **Foco:** reprodutibilidade do ambiente Python.
- **Achado substancial:** registrar versões no manifesto não impedia resolução futura de dependências diferentes.
- **Correção:** primeiro setup gera `requirements.lock` completo; execuções seguintes instalam o lock e o pacote local sem resolver dependências novamente.
- **Sequência sem melhoria substancial:** 0 de 2.

## I20 — Loop de otimização do plano — Passada 11 — 2026-09-21 18:35 BRT

- **Foco:** compatibilidade entre a versão Python definida e a máquina de trabalho.
- **Achado substancial:** o Mac expõe Python 3.14, não 3.12; gerar o lock localmente invalidaria o ambiente declarado.
- **Correção:** o checkpoint inicial sobe sem lock; `bootstrap-lock` roda uma única vez no Codespace com Python 3.12, valida o Streamlit, commita o lock na branch e exige `git pull --ff-only` antes da etapa seguinte.
- **Sequência sem melhoria substancial:** 0 de 2.

## I21 — Loop de otimização do plano — Passada 12 — 2026-09-21 18:47 BRT

- **Foco:** coerência entre a SPEC-fonte e o plano derivado.
- **Achado substancial:** a SPEC ainda continha o placeholder de descrição e não referenciava pesquisa nem plano.
- **Correção:** descrição preenchida com objetivo, público, escopo e exclusões; links relativos adicionados para pesquisa e plano de implementação.
- **Nota SDD:** o pacote Codex instalado de `plan-task` contém apenas `SKILL.md`; os agentes, prompts e scripts exigidos pelo workflow não foram instalados. O plano atual foi criado com `writing-plans`; a promoção SDD por `plan-task` permanece bloqueada até instalar o pacote completo e continua obrigatória antes de `implement-task`.
- **Sequência sem melhoria substancial:** 0 de 2.

## I22 — Loop de otimização do plano — Passada 13 — 2026-09-21 18:54 BRT

- **Foco:** cobertura da SPEC, buildabilidade, placeholders, comandos, gates e rastreabilidade.
- **Resultado:** nenhuma melhoria ou otimização substancial identificada.
- **Verificação:** `git diff --check` limpo; nove tarefas, dez checkpoints de commit e dez resultados esperados; nenhum marcador `TODO`, `TBD`, `FIXME` ou placeholder residual.
- **Sequência sem melhoria substancial:** 1 de 2.

## I23 — Loop de otimização do plano — Passada 14 — 2026-09-21 18:59 BRT

- **Foco:** documentação contemporânea durante a futura execução.
- **Achado substancial:** o plano concentrava a atualização do diário no fechamento, contrariando a regra de que documentar é tão importante quanto o resultado.
- **Correção:** cada tarefa agora exige entrada curta no diário antes do commit e inclui o process log no mesmo checkpoint.
- **Sequência sem melhoria substancial:** 0 de 2.

## I24 — Loop de otimização do plano — Passada 15 — 2026-09-21 19:03 BRT

- **Foco:** comandos, links, cobertura, checkpoints Git e registro contemporâneo.
- **Resultado:** nenhuma melhoria ou otimização substancial identificada.
- **Verificação:** `git diff --check` limpo; nove comandos `git add -f`; dez referências ao diário; links relativos da SPEC resolvem para arquivos existentes.
- **Sequência sem melhoria substancial:** 1 de 2.

## I25 — Loop de otimização do plano — Passada 16 — 2026-09-21 19:08 BRT

- **Foco:** ordem TDD da interface.
- **Achado substancial:** a tarefa de UI implementava páginas antes de criar testes que demonstrassem falha nos fluxos essenciais.
- **Correção:** `AppTest` passa a cobrir página inicial, artefato desatualizado, motivo obrigatório, persistência e separação de projeções antes da implementação.
- **Sequência sem melhoria substancial:** 0 de 2.

## I26 — Loop de otimização do plano — Passada 17 — 2026-09-21 19:12 BRT

- **Foco:** completude por tarefa, TDD, validação, commit e diário.
- **Resultado:** nenhuma melhoria ou otimização substancial identificada.
- **Verificação:** nove tarefas, nove blocos de arquivos, nove checkpoints de tarefa e referência ao diário em todos os checkpoints aplicáveis; nenhum placeholder residual.
- **Sequência sem melhoria substancial:** 1 de 2.

## I27 — Loop de otimização do plano — Passada 18 — 2026-09-21 19:16 BRT

- **Foco:** segurança, Ponytail/YAGNI, privacidade, evidência e aderência ao Challenge 002.
- **Resultado:** nenhuma melhoria ou otimização substancial identificada.
- **Verificação:** dependências mínimas; nenhum serviço pago; automação limitada ao roteamento elegível; risco prevalece; PII, dados brutos, modelos e banco local excluídos do Git; ambos os datasets preservam fronteiras próprias.
- **Sequência sem melhoria substancial:** 2 de 2 — meta atingida.

## I28 — Fechamento do planejamento otimizado — 2026-09-21 19:17 BRT

- **Artefato principal:** `solution/002-support/docs/superpowers/plans/2026-09-21-support-decision-copilot.md`.
- **Método:** skill `writing-plans`, 18 passadas críticas em cascata e reinício da contagem após cada melhoria substancial.
- **Resultado:** duas passadas consecutivas finais sem novos achados substanciais; plano considerado otimizado para revisão humana.
- **Pesquisa incorporada:** comparação de interface, modelagem, calibração, recuperação e persistência; inspeção real confirmou 8.469 linhas no Dataset 1 e 47.837 no Dataset 2, além das limitações temporais do Dataset 1.
- **Estado:** planejamento concluído; implementação não iniciada.
- **Gate pendente:** o workflow completo de `plan-task` exige assets ausentes da instalação Codex atual e segue obrigatório, junto da aprovação humana, antes de `implement-task`.

**Decisão:** encerrar o loop de otimização em 2/2 passadas consecutivas sem melhorias substanciais.

## I29 — Reabertura da auditoria contra o repositório canônico — 2026-09-21 19:34 BRT

- **Solicitação:** rever o repositório do desafio e garantir cobertura integral do avaliador e da stack, sem gargalos conhecidos.
- **Fonte verificada:** `upstream/main` no SHA `4aed364d572fabe0f1fff1f0c6f32960b30fe575`; challenge, README raiz, guia de submissão, CONTRIBUTING e template oficial relidos integralmente.
- **Gaps encontrados:** README obrigatório estava planejado dentro da solução, não na raiz da submissão; desperdício não tinha fórmula fechada; satisfação não tinha teste multivariado/fallback; Dataset 1 precisava de proteção explícita contra texto fraco; Laboratório IT não recebia texto livre.
- **Correções adicionais:** matriz de oportunidade entre os datasets sem unir registros; `make doctor`; pisos compatíveis da stack; orçamento de 320 minutos; gate do diff contra `upstream/main`; título oficial do PR.
- **Evidência:** `solution/002-support/docs/reports/2026-09-21-plan-compliance-audit.md`.

**Decisão:** fechamento anterior reaberto corretamente; nova conclusão depende de duas passadas finais desta auditoria sem gap material.

## I30 — Auditoria de stack e reinício da sequência — 2026-09-21 19:46 BRT

- **Achado:** o piso `streamlit>=1.42` não garantia o `AppTest` multipágina planejado; a documentação dessa versão declara incompatibilidade com `st.navigation` e `st.Page`.
- **Correção:** piso elevado para `streamlit>=1.64,<2`, versão cuja API documenta `AppTest.switch_page()`; lock exato continua obrigatório no Codespace.
- **Verificação adjacente:** `scikit-learn>=1.6,<2` cobre `FrozenEstimator`; Python 3.12 permanece suportado.
- **Sequência sem gap material:** reiniciada em 0 de 2.

**Decisão:** incompatibilidade eliminada antes da implementação; as duas passadas finais serão refeitas desde zero.

## I31 — Auditoria final, passada 1 — Requisitos do avaliador — 2026-09-21 19:51 BRT

- **Escopo relido:** challenge, guia de submissão, CONTRIBUTING e template no SHA canônico registrado.
- **Verificação:** diagnóstico, satisfação, desperdício, ambos os datasets, automação e limites humanos, fluxo prático, protótipo real, anti-cherry-picking, process log, README oficial, setup, pasta autorizada e título do PR possuem entrega e gate explícitos no plano.
- **Resultado:** nenhum gap material novo.
- **Sequência sem gap material:** 1 de 2.

**Decisão:** manter o plano sem expansão; seguir para a passada independente de stack e execução.

## I32 — Auditoria de stack, achados operacionais — 2026-09-21 20:02 BRT

- **Achados:** faltava política explícita de reuso/cota de Codespaces; Task 7 executaria suíte completa no Mac; o smoke do Streamlit ficaria bloqueado; o preflight final antecedia arquivos ainda não criados.
- **Correções:** reuso e cota viraram pré-condições; teste local foi reduzido ao arquivo focal; smoke ganhou health check e encerramento; evidências e READMEs agora precedem commit, push e preflight do SHA final.
- **Sequência sem gap material:** reiniciada em 0 de 2.

**Decisão:** os quatro gargalos foram eliminados no plano; reiniciar ambas as passadas finais.

## I33 — Auditoria final reiniciada, gap de comunicação — 2026-09-21 20:07 BRT

- **Achado:** o fluxo prático existia na arquitetura e no app, mas o plano não obrigava o README final a narrá-lo ponta a ponta para o avaliador.
- **Correção:** Task 9 agora exige a sequência explícita de entrada, validação, modelo, gate, recuperação/abstenção, decisão humana e auditoria.
- **Sequência sem gap material:** reiniciada em 0 de 2.

**Decisão:** implementação e comunicação passam a provar o mesmo fluxo operacional.

## I34 — Auditoria final, passada 1 — Cobertura do avaliador — 2026-09-21 20:10 BRT

- **Verificação:** matriz automatizada de 18 exigências contra o plano e releitura das quatro fontes canônicas no SHA `4aed364d572fabe0f1fff1f0c6f32960b30fe575`.
- **Resultado:** 18 de 18 exigências cobertas; nenhum gap material novo.
- **Sequência sem gap material:** 1 de 2.

**Decisão:** preservar o escopo e executar a passada independente de stack, comandos e ciclo de vida.

## I35 — Auditoria final, passada 2 — Stack e execução — 2026-09-21 20:13 BRT

- **Verificação:** nove tarefas e nove contratos de interface; 45 passos; pisos compatíveis; nenhuma suíte completa local; reuso/cota de Codespaces; dois smokes limitados; gate do SHA final; diff restrito à submissão; `git diff --check` limpo.
- **Resultado:** nenhum gap material novo.
- **Sequência sem gap material:** 2 de 2 — meta atingida.

**Decisão:** auditoria encerrada. O plano cobre 100% dos requisitos publicados e não mantém gargalo conhecido de arquitetura, stack ou execução; prontidão funcional permanece condicionada à implementação e aos gates previstos.

## I36 — Fechamento da construção socrática e auditoria pré-implementação — 2026-09-21 20:20 BRT

- **Construção preservada:** o ledger I06 registra integralmente as 24 ondas adaptativas, sempre com pergunta, alternativas de múltipla escolha, resposta, interpretação e dependência da onda seguinte.
- **Síntese preservada:** I07 registra as seis seções incrementais da arquitetura; I08 registra a aprovação humana que autorizou a SPEC.
- **Última etapa:** I29–I35 registram a reauditoria do repositório canônico, os gaps encontrados, as correções e duas passadas consecutivas finais sem novo gap material.
- **Resultado:** 18 de 18 exigências publicadas possuem entrega e gate explícitos; stack, comandos, ciclo de Codespaces e SHA final foram reconciliados.

**Decisão:** encerrar formalmente descoberta, síntese, SPEC e planejamento; iniciar implementação somente pelo workflow SDD validado.

## I37 — Metodologia obrigatória de implementação: Feedback Looping — 2026-09-21 20:21 BRT

- **Autoria:** metodologia definida por Luis; o registro é parte obrigatória e tão importante quanto o resultado final.
- **Fluxo cronológico:** `Planejamento → Revisão → Execução → Teste`.
- **Loop:** cada fase produz reports quase em tempo real para a própria IA; os achados determinam se o trabalho é reforçado no mesmo estágio ou se pode avançar.
- **Gate:** uma fase somente termina quando validada. Falha em revisão ou teste retorna ao planejamento da própria fase, seguido de nova revisão, execução e teste.
- **Cascata:** os loops menores validam passos; os loops maiores validam fases; o `/goal` permanece ativo até todos os critérios de pronto passarem.
- **SDD:** `plan-task` refina e decompõe a SPEC; `implement-task` executa uma etapa por agente, revisa cada fase e verifica a definição de pronto ao final.
- **Limitação técnica registrada:** os `SKILL.md` de SDD estão instalados no Codex, mas os scripts, prompts e agentes nomeados do pacote Claude não estão presentes. O Codex seguirá o mesmo contrato com os agentes e ferramentas disponíveis, sem simular artefatos ausentes.

**Decisão:** avançar automaticamente fase a fase; repetir qualquer etapa reprovada e nunca promover trabalho não validado.

## I38 — SDD `plan-task`: refinamento e decomposição validados — 2026-09-21 21:18 BRT

- **Configuração:** task complexa; qualidade mínima `3,5/5`; até três iterações; tier equivalente a `opus`; sem checkpoints humanos intermediários porque Luis já autorizou seguir para implementação.
- **Fase 2a — pesquisa:** 16 recursos; skill reutilizável criada; juiz `4,70/5`.
- **Fase 2b — impacto:** 28 criações e três modificações estimadas; risco alto; juiz `4,565/5`.
- **Fase 2c — negócio:** 20 critérios, cinco checks, cinco rubricas e 42 casos; juiz `4,405/5`.
- **Fase 3 — arquitetura:** primeira revisão `4,395/5`; dois contratos P1 corrigidos em loop — transporte de OOD e bloqueio de drafts por sinais; segunda revisão `4,65/5`, sem P1/P2.
- **Fase 4 — decomposição:** dez subtarefas em três fases; primeira revisão `4,609/5`; três ambiguidades corrigidas em loop — reprodução dupla, corrida de teste e propriedade documental; segunda revisão `4,742/5`, sem novo achado.
- **Adaptação registrada:** `prompts/judge.md`, scripts e agentes Claude do pacote não existem na instalação Codex; juízes independentes aplicaram as rubricas integrais contidas no `SKILL.md` instalado.

**Decisão:** promover a SPEC de `draft` para `todo`; planejamento e revisão SDD estão validados, permitindo iniciar `implement-task`.

## I39 — Step 01: início da prova de ambiente — 2026-09-21 21:35 BRT

- **Aprovação e escopo:** a autorização humana da SPEC foi confirmada em I38. O step limita-se à prova sintética de ambiente; não implementa dados, modelos ou domínio.
- **Estado inicial:** branch `submission/luis-roquette-002-support`, commit `ee01252b3bf0799ba1508b1c2cad7fbc923bc7ec`, árvore limpa e nenhum workflow de CI presente.
- **Decisão:** manter Streamlit, após comparar os três candidatos já registrados — Streamlit, Gradio e Dash — e reproduzir navegação, formulário editado, transação SQLite, releitura por nova conexão e CSV persistido.
- **Arquivos em preparação:** pacote Python 3.12, comandos Make reais, configuração Streamlit offline, prova em `app.py`, teste focal e README técnico inicial.
- **Gate:** versões exatas só serão registradas após instalação e teste no Codespace gerenciado com o diff deste checkpoint. `make reproduce` falha explicitamente enquanto o pipeline de step posterior não existe.
- **Validação local leve:** `python3 -m compileall -q app.py src tests` e `git diff --check` concluíram com status 0. Instalação, lock e pytest permanecem pendentes do ambiente Python 3.12 gerenciado.
- **Erro e correção:** o primeiro bootstrap selecionou o `python3` padrão 3.14.2 e foi bloqueado como previsto; `/usr/bin/python3.12` foi localizado e passado por `PYTHON`. Na execução seguinte, Ruff encontrou uma linha de 104 caracteres e o `doctor` revelou que seu `echo` final mascarava a falha da sondagem HTTP por `HEAD`. A linha foi quebrada, a sondagem passou a usar GET parcial com redirects e o retorno de erro foi preservado explicitamente.
- **Erro e correção:** com Ruff e `doctor` verdes, o pytest falhou na coleta porque `pythonpath = ["src"]` corretamente expõe o pacote, mas não transforma `app.py` em módulo importável. O teste passou a carregar esse arquivo explicitamente com `runpy`, preservando o package discovery definido.
- **Erro e correção:** o AppTest 1.64 não materializou links para páginas definidas por callables, portanto contar `page_link` não provava navegação. A página de limites foi reduzida a `pages/limits.py`, permitindo usar `AppTest.switch_page()` e validar a troca pelo título renderizado.

## I40 — Step 01: ambiente e prova mínima validados — 2026-09-21 23:24 BRT

- **Ambiente reproduzido:** Codespace `codex-preflight-657v7q4ggx7f5557`, Python 3.12, branch `submission/luis-roquette-002-support` e SHA de código `e1c348557b81278ac1894a1dc068b4dd28ed2615`.
- **Instalação limpa:** `make PYTHON=/usr/bin/python3.12 setup` criou uma nova `.venv` a partir de `requirements.lock`; `import support_copilot` confirmou a versão `0.1.0` sem resolução adicional do pacote local.
- **Versões centrais comprovadas:** Streamlit 1.64.0, pandas 2.3.3, scikit-learn 1.9.1, joblib 1.6.0, pytest 8.4.2 e Ruff 0.16.8.
- **Validação:** `make doctor` passou; `make lint` passou; `make test` concluiu `3 passed`; a prova navegou para a página de limites, editou e submeteu o formulário, confirmou a linha SQLite por nova conexão e comparou byte a byte o conteúdo oferecido ao download com o arquivo CSV persistido.
- **Gate futuro:** `make reproduce` retornou status 2 e explicou que `scripts/reproduce.py` pertence a step posterior; nenhum placeholder retornou sucesso.
- **Smoke real:** o servidor Streamlit respondeu `ok` em `/_stcore/health` e encerrou deliberadamente com status 0. A prova é identificada como sintética e não usa API paga, credencial nem dado pessoal.
- **Ciclo do Codespace:** a sessão do step foi interrompida após os gates porque outro `codespace-manager run` passou a usar o mesmo ambiente. O inventário confirmou branch limpa e estado `Available`; o Codespace não foi apagado nem interrompido para preservar a sessão concorrente.

## I41 — Step 02: contratos de dados e quarentena conservadora — 2026-09-21 20:45 BRT

- **Relógio:** horário obtido nesta execução por `date` no fuso America/Sao_Paulo; os horários anteriores foram preservados como registrados, mesmo com divergência de ordenação.
- **Fontes reais:** download público sem credenciais confirmou 8.469 linhas Customer, schema de 17 colunas; 47.837 linhas IT, colunas `Document`/`Topic_group` e as oito categorias previstas. Arquivos brutos permaneceram em `data/raw/`, ignorado pelo Git; nenhum exemplo bruto foi registrado no diário.
- **Decisão de privacidade:** colunas pessoais/demográficas são descartadas, identificadores conhecidos são mascarados e suspeitas residuais causam quarentena da linha inteira. Entidades capitalizadas desconhecidas também são recusadas, aceitando falsos positivos. Datas ilegíveis mantêm somente uma sentinela inválida; notas inválidas viram nulo, nunca zero. Não se alega anonimização universal; amostras públicas continuam bloqueadas até revisão humana.
- **Contratos:** `data.py` entrega frames independentes por domínio, hashes/qualidade, agrupamento canônico, representante por menor ID e quarentena de rótulos conflitantes. Splits seeded usam 60/20/20 por classe, com arredondamento documentado e mínimo de dez representantes por classe. Calibração se divide uma única vez; `DatasetSplit.test` contém apenas IDs/grupos, sem features/rótulos finais.
- **Implementação:** pipeline inicial publica JSON finito e atômico de treino/calibração e manifesto por último; modelos, fila e assistência futura ficam explicitamente indisponíveis. README e Makefile documentam fontes, destino manual e retomada sem fallback sintético.
- **Loop de teste:** seis testes focados passaram localmente em 0,27 s usando Python 3.12 e dependências existentes no cache. O primeiro lint identificou cinco linhas acima do limite; foram quebradas sem mudança funcional e o Ruff passou. `git diff --check` também passou.
- **Gate remoto iniciado:** o Codespace inicialmente estava ativo e foi preservado. Após confirmar `Shutdown` e árvore limpa, `codespace-manager run` iniciou validação em worktree temporário, com snapshot tar de SHA-256 `272bf723ce0eca9de71d41eba8cdfaf20ec028d8344dbd21688b62a4310663b1`. A reprodução real e suas contagens ainda não foram declaradas aprovadas neste registro.
- **Correção do registro do gate:** a primeira tentativa foi recusada com status 73 porque o estado passou a `ShuttingDown` antes da execução. A segunda iniciou o ambiente, mas o comando não chegou a executar: uma linha base64 longa ultrapassou o transporte do PTY e deixou o shell aguardando fechamento de aspas. Somente os processos dessa tentativa foram encerrados; o checkout permaneceu limpo. O reenvio usará linhas curtas e o snapshot atualizado `226aa25155a34a372816faeb4140391c925289c5a62f984f25386918febc2fd4`, que inclui validação estrutural adicional do manifesto, novamente coberta pelos seis testes verdes.
- **Terceira tentativa e limite:** o transporte com linhas curtas funcionou e criou `/tmp/support-step02.udisVV` sobre a base remota `e1c3485`. A verificação falhou antes de extrair o snapshot: `echo` acrescentou um terceiro espaço entre hash e caminho; `sha256sum` interpretou esse espaço como parte do filename. Correção identificada: usar `printf '%s  %s\n' HASH CAMINHO`. Após três tentativas sem gate concluído, as novas tentativas foram interrompidas conforme `AGENTS.md`; a hipótese duvidosa era o transporte/conferência do snapshot pelo PTY, não o resultado dos testes locais. Nenhum lint, teste ou pipeline remoto deste step recebeu alegação de aprovação.
- **Estado entregue ao orquestrador:** seis testes de dados verdes, Ruff verde nos três arquivos Python novos, compilação e `git diff --check` verdes. Fontes reais/schema/IDs/taxonomia foram inspecionados, mas contagens completas de sanitização/deduplicação, reprodução remota e revisão humana de amostras continuam pendentes. O worktree remoto temporário contém o arquivo de transporte e não foi apagado automaticamente.

## I42 — Step 02: retomada pelo commit da branch — 2026-09-21 20:55 BRT

- **Correção de processo:** o orquestrador autorizou abandonar o transporte artesanal por PTY e validar somente arquivos da branch publicados em commit intermediário. Nenhuma nova função ou etapa foi adicionada.
- **Inspeção:** apenas os seis arquivos do step e o registro contemporâneo estavam alterados; nenhum workflow de CI/configuração de deploy existe no repositório e a branch não possui PR aberto. O push intermediário de feature está autorizado pela regra global; não substitui o gate remoto.
- **Gates repetidos:** seis testes focados passaram em 0,42 s; Ruff passou; `git diff --check` passou. O cache local serve apenas aos testes focados; o lock do ambiente gerenciado continua sendo a referência de reprodução.
- **Próxima execução:** commit/push na branch `submission/luis-roquette-002-support`; reuso apenas de Codespace parado e limpo, atualização por Git e conferência do SHA exato antes de lint, testes e reprodução real.

## I43 — Jornada construtiva: o diário como entrega — 2026-09-21

- **Definição de Luis:** o process log é o diário oficial da construção. Deve mostrar como o arquiteto desenha e como o engenheiro constrói.
- **O que registrar:** decisões, hipóteses, critérios, feedback, erros, correções, validação e motivo para avançar ou repetir. Fragmentos curtos, escritos durante o trabalho; uma etapa não avança apenas porque um arquivo foi concluído.
- **Pivot do step 02:** snapshot/PTTY falhou em três tentativas. A premissa do transporte artesanal foi revista; commit e push do SHA exato substituíram esse caminho. O código foi publicado em `497ab03962f6f23481e580dfebb3c483ab55b190`, depois de seis testes focados, lint e verificação de whitespace aprovados.
- **Concorrência preservada:** o Codespace voltou a `Available` por uma execução concorrente de `lead-step01-manifest`. Nenhum processo dessa sessão foi interrompido. O suporte aguarda `Shutdown` e checkout limpo antes de executar seus gates.
- **Critério para avançar:** validar o SHA publicado no ambiente gerenciado, concluir os gates de dados e registrar resultados reais. Falha de código retorna ao ciclo correção → teste focado → commit/push → novo gate; ausência de evidência permanece explícita.

## I44 — Step 02: reprodução real validada — 2026-09-21 20:59 BRT

- **SHA conferido:** `69d15f60c4f10aa4b2a0f82989a80364b5414734`, obtido por fetch/fast-forward da branch publicada no Codespace `codex-preflight-657v7q4ggx7f5557`. O checkout estava limpo antes e depois; nenhum snapshot foi usado.
- **Gates reais:** `make lint` passou; `make test` concluiu `9 passed` em 12,92 s; `make data` obteve as duas fontes públicas; `make reproduce` executou duas vezes. Os manifestos foram iguais após remover somente `generated_at`; o comparador emitiu `REPRODUCIBILITY_OK`.
- **Customer:** 8.469 linhas de origem, 7.077 em quarentena de privacidade, 1.392 sanitizadas; 255 linhas de 29 grupos com rótulos conflitantes e uma duplicata foram excluídas do split. Restaram 1.136 representantes: 679 treino, 225 calibração e 232 teste lacrado.
- **IT:** 47.837 linhas de origem, 21.365 em quarentena e 26.472 representantes, sem duplicata/conflito canônico detectado. Splits independentes mantiveram as oito classes; ambos os domínios registraram `ready`.
- **Limitação para o diagnóstico:** 1.358 das 1.392 linhas Customer sanitizadas não têm nota de satisfação. A seleção conservadora de privacidade reduz e pode enviesar a amostra; o próximo step deve exibir esses denominadores e retornar insuficiência quando aplicável. Revisão humana de exemplos públicos continua pendente e nenhuma amostra foi publicada.
- **Motivo para avançar:** contratos e reprodução real foram exercitados com fontes efetivas, resultados determinísticos e teste final sem features/rótulos exportados. O step 03 pode consumir o desenvolvimento sanitizado, mantendo explícitas as exclusões e limitações.

## I45 — Step 03: diagnóstico operacional construído — 2026-09-21 21:21 BRT

- **Hipótese:** o intervalo realmente observável é `Time to Resolution - First Response Time`; ele pode sustentar gargalos e um proxy de excesso, mas não mede espera até primeira resposta nem resolução total.
- **Decisão:** analisar somente representantes Customer sanitizados de treino + calibração. O teste permanece lacrado. O relatório preserva o funil de 8.469 linhas brutas, 1.392 sanitizadas e 1.136 representantes, além do subconjunto efetivamente usado no desenvolvimento.
- **Satisfação:** apenas 34 linhas sanitizadas na fonte possuem nota. A análise registra ausências e seleção conservadora; compara Ridge com baseline de mediana usando pré-processamento dentro dos folds e publica importância somente com ganho de MAE de pelo menos 2%. Associação não é causalidade.
- **Cenários:** volume, fração endereçável, minutos e custo/hora são premissas editáveis. Projeções não alteram o histórico nem convertem excesso observado em economia realizada. A oportunidade IT permanece indisponível porque não existe desfecho operacional nem chave entre registros.
- **Erro e correção:** o primeiro patch de teste apontou por engano para `submissions/luisroquette/`. O arquivo vazio e toda a árvore criada foram removidos imediatamente; o teste foi recriado somente em `submissions/luis-roquette/`.
- **Teste local focado:** Ruff passou nos seis arquivos tocados; `pytest tests/test_analytics.py tests/test_workflow.py -q` concluiu 13 testes em 26,40 s; compilação, `git diff --check`, casos 29/30, timestamps inválidos, corte de 2%, cenários inválidos e invariância histórica passaram.
- **Motivo para repetir antes de avançar:** os relatórios reais e suas contagens ainda precisam ser produzidos no Codespace pelo SHA exato. Resultado local focado não substitui `make test && make lint && make reproduce` no ambiente gerenciado.

## I46 — Step 03: diagnóstico real validado — 2026-09-21 21:34 BRT

- **Primeira tentativa remota:** bloqueada antes dos gates porque a conferência usou um SHA completo digitado incorretamente. O SHA foi obtido novamente do Git, sem inferir o sufixo: `5eeb981a5b65bf24205d0d472bfe656f635c288f`.
- **Segunda tentativa remota:** o gerenciador recusou corretamente o Codespace em `ShuttingDown`. A sessão não foi interferida; a execução aguardou `Shutdown` e reutilizou o mesmo ambiente limpo.
- **Gate no SHA correto:** `make lint` passou; `make test` concluiu 19 testes em 23,16 s; `make reproduce` passou duas vezes. Manifestos iguais após remover somente `generated_at`; os seis relatórios esperados existem e estão registrados no manifesto. O checkout permaneceu limpo.
- **Resultado real:** 904 representantes sanitizados compõem treino + calibração; somente quatro intervalos pós-primeira-resposta são válidos. Há 21 notas válidas no desenvolvimento, contra 34 em todas as 1.392 linhas sanitizadas da fonte. Ridge não obteve ganho de MAE de 2%, portanto o estado é `no_reliable_signal` e nenhuma importância multivariada é publicada.
- **Oportunidade:** nenhum par tipo/prioridade alcança 30 intervalos válidos; todos permanecem `insufficient_support`, sem estimativa de excesso. O relatório IT declara ausência de desfecho operacional e de chave entre registros.
- **Motivo para avançar:** o marco executável funciona e os resultados negativos permanecem visíveis. Não há justificativa para relaxar privacidade, abrir o teste ou fabricar economia para preencher o painel.

## I47 — Step 03: correções da revisão da Fase 1 — 2026-09-21 21:44 BRT

- **Hipótese testada:** ausência total de intervalos em um fold não pode virar zero observado. O pipeline agora omite a feature temporal somente naquele fold quando o treino não contém valor; categóricas, baseline e demais folds permanecem intactos. O relatório conta em quantos folds a feature foi realmente usada.
- **Correção temporal:** `pandas.to_datetime(format="mixed", utc=True)` passa a aceitar ISO válido com e sem microssegundos independentemente da ordem das linhas, sem aceitar timestamps ilegíveis.
- **Correção de escassez:** tabelas vazias de gargalos e desperdício preservam headers. O resumo retorna `status=insufficient_support`, métricas nulas e `reason=no_sanitized_development_representatives` quando sanitização/deduplicação não sustenta split.
- **Regressões permanentes:** avaliações suficientes com zero intervalo; um único intervalo ausente do treino de um fold; precisões temporais mistas nas duas ordens; reprodução completa após split insuficiente, incluindo manifesto, resumo JSON e CSVs vazios tipados.
- **Erro e correção:** o primeiro teste tentou importar `scripts.reproduce` como pacote. Como `scripts/` não é pacote e não precisa virar um, o teste passou a carregar o script por `runpy`, repetindo o padrão mínimo já usado no workflow.
- **Teste local focado:** Ruff passou; `pytest tests/test_analytics.py tests/test_workflow.py -q` concluiu 18 testes em 2,44 s; `git diff --check` passou.
- **Motivo para repetir:** suíte completa e reprodução real ainda precisam confirmar no Codespace que o SHA corrigido conserva as contagens honestas anteriores e não reabre os defeitos da revisão.

## I48 — Step 03: correções validadas no ambiente gerenciado — 2026-09-21 21:49 BRT

- **SHA corrigido:** `ca17ede6b79ce0640fd62865543d363c87d466c5`, conferido após fetch/fast-forward em checkout remoto limpo.
- **Concorrência preservada:** a primeira tentativa foi recusada em `ShuttingDown`; nenhum processo externo foi interrompido. A execução aguardou `Shutdown` e reutilizou o Codespace limpo.
- **Gates:** Ruff passou; suíte completa concluiu 24 testes em 24,61 s; `make reproduce` passou com as duas fontes reais; assertions dos relatórios passaram. O checkout remoto permaneceu limpo.
- **Regressão real:** o diagnóstico continua com 904 linhas de desenvolvimento, quatro intervalos válidos, 21 notas, `no_reliable_signal` e zero grupos elegíveis para excesso. O ganho é robustez nos casos escassos, não criação de sinal novo.
- **Decisão:** os três achados High/Medium da revisão estão fechados sem alterar contratos de dados dos steps 01/02, relaxar privacidade ou ampliar o escopo funcional.

## I49 — Phase 1: Feedback Looping fechado — 2026-09-21 22:00 BRT

- **Arquiteto:** definiu o marco como diagnóstico executável sobre dados sanitizados, com teste lacrado, denominadores reconciliáveis, ausência de sinal visível e capacidades futuras indisponíveis.
- **Engenheiro:** entregou os steps 01–03 — ambiente reproduzível, contratos de dados/privacidade e diagnóstico operacional com relatórios, cenários e página mínima.
- **Juiz, primeira revisão:** `3,5/5`; encontrou dois High e um Medium, todos localizados no step 03. O blast radius foi confirmado como local: folds sem intervalos, parsing temporal misto e split insuficiente. Steps 01/02 permaneceram intactos.
- **Correção em loop:** cada achado ganhou um reproduzidor permanente, correção mínima, teste focado, suíte completa e reprodução real no SHA publicado. Nenhuma correção relaxou privacidade, abriu o teste ou fabricou sinal.
- **Prova:** SHA funcional `ca17ede6b79ce0640fd62865543d363c87d466c5`; Ruff verde, 24 testes e reprodução real verde. O diário e o estado final foram sincronizados em `328c429390e94efcebe9c47073c951a5727f7575` e revalidados no mesmo gate.
- **Juiz, segunda revisão:** `4,0/5`, sem issues. O ciclo `arquiteto → engenheiro → juiz → correção → prova` encerrou a Phase 1 com Feedback Looping completo.
- **Estado SDD:** steps 01, 02 e 03 marcados `[DONE]`; `Phase 1 [REVIEWED]`. A barreira de fase foi satisfeita antes de qualquer implementação da Phase 2.

## I50 — Padrão autoral de Luis: redundância e lapidação — 2026-09-22

- **Lugar na jornada construtiva:** Luis definiu as duas etapas abaixo como seu padrão autoral, executadas após a implementação integral e a verificação da Definition of Done (DoD), antes do fechamento final. Este registro documenta a decisão metodológica; não afirma que essas auditorias já começaram ou foram concluídas.
- **Redundância Necessária:** usar `/goal` em cascatas de `/loop` para auditar exaustivamente o trabalho implementado. Qualquer erro, falha, lacuna, melhoria ou otimização relevante exige tratamento e reinicia a contagem de passadas limpas. Encerrar somente após pelo menos duas passadas consecutivas sem achados relevantes. O objetivo definido por Luis é provar a assimilação integral e a ausência de lacunas no arcabouço, sustentando a conclusão pelas evidências de cada passada.
- **Lapidação e melhoria/otimização:** depois de sanar os erros e bugs pela Redundância Necessária, auditar exaustivamente gargalos, melhorias, otimizações e refinamentos em técnica, layout, design, UI/UX, código e segurança. Implementar os achados relevantes e reiniciar a contagem. Encerrar somente após duas rodadas consecutivas sem necessidade de correção ou otimização relevante.
- **Registro de cada rodada:** quando essas etapas começarem, documentar contemporaneamente o foco, os achados, as correções realizadas e a sequência de rodadas limpas: `0/2` após um achado relevante ou sua correção, `1/2` após a primeira rodada limpa e `2/2` após a segunda rodada limpa consecutiva. Cada etapa mantém sua própria contagem; um novo achado relevante interrompe a sequência e a reinicia em `0/2`.

## I51 — Step 05: auditoria transacional e export persistido — 2026-09-22

- **Decisão de implementação:** reutilizar SQLite da biblioteca padrão e o sanitizador de `data.py`, sem ORM ou nova dependência. `store.py` registra as quatro ações, valida snapshots, mantém versões indisponíveis nulas, calcula diferença de edição sobre textos sanitizados e usa UUID único para impedir duplicação. Banco e exports permanecem em runtime ignorado; nenhum evento público foi fabricado.
- **Risco e correção de desenho:** `rename` comum pode sobrescrever um destino existente no Unix. A publicação usa temporário irmão sincronizado, `os.link` exclusivo e remoção do temporário: equivalente atômico sem sobrescrita, inclusive sob disputa pelo destino. A limitação de suporte a hard links está documentada; falha não anuncia export salvo. O retorno contém os bytes efetivamente lidos do arquivo persistido.
- **Erros e ajustes:** os primeiros testes passaram, mas Ruff encontrou duas linhas acima do limite; ambas foram corrigidas. A conferência do contrato do step 04 identificou motivos `category:<taxonomia>` e `text:<regex>`, que passaram a ser preservados exatamente. Regressões recusam risco explícito combinado com draft ou roteamento automático, sem bloquear draft seguro apenas por confiança abaixo do limiar de roteamento.
- **Validação focada realizada:** `pytest tests/test_store.py -q` concluiu 63 testes em 0,52 s; Ruff e `git diff --check` passaram. Os testes cobrem rollback, reinício por nova conexão, UUID concorrente/idempotente/divergente, schema desconhecido preservado, sanitização e quarentena, quatro ações, round-trip de todos os campos, fórmulas com whitespace/controles e falhas de gravação/publicação. Banco e exports runtime foram confirmados no ignore.
- **Limites e sequência:** os resultados acima pertencem a fixtures sintéticas e testes focados locais. Integração da UI com releitura por nova conexão, suíte consolidada no ambiente gerenciado e abertura real do CSV em planilha continuam pendentes das próximas etapas. README e diário foram atualizados nesta serialização; nenhuma evidência final, commit ou push foi produzido por este registro.

## I52 — Step 04: retomada da calibração e gate adversarial — 2026-09-22

- **Retomada e diagnóstico:** o agente anterior encerrou por limite de uso deixando implementação parcial de modelos, regras e testes. A retomada preservou esse trabalho e os arquivos do step 05. A primeira execução focada apresentou 35 testes aprovados, duas falhas e seis erros: no scikit-learn 1.9.1, `CalibratedClassifierCV` ainda recebia o CV padrão de cinco folds mesmo com `FrozenEstimator`, incompatível com as pequenas amostras de calibração das fixtures.
- **Correção e prova de independência:** mantido `FrozenEstimator` sobre o pipeline ajustado somente no treino; uma partição explícita usa o holdout integral para ajustar apenas o sigmoid. Spy comprovou exatamente 20 ajustes dos quatro candidatos nos cinco folds e um ajuste final, sem refit na calibração, preservando o mesmo estimador e IDF. A seleção de threshold usa a outra metade disjunta da calibração e a mesma derivação de sinais/gate da inferência.
- **Reforços de segurança e evidência:** regressões cobrem ganho 0,019/0,020, empate inclusivo de 0,01, OOD escalar/lote e medição indisponível, confiança adversarial de 0,99, cada categoria sensível, Critical e prioridade desconhecida. O gate recalcula ambiguidade e detecta remoção de regras obrigatórias; risco precede modelo desativado e confiança. Locks incorporam threshold à versão de regras e rejeitam retuning; métricas indefinidas são nulas com motivo, denominadores e bins explícitos.
- **Validação focada realizada:** `pytest tests/test_modeling.py tests/test_decision.py -q --tb=short` concluiu 51 testes em 1,51 s; Ruff dos quatro arquivos passou. A avaliação final foi exercitada somente com fixtures sintéticas; o teste real permaneceu lacrado. Contagens e IDs de exemplos de risco vêm apenas do treino. Regras lexicais e vetor TF-IDF zero detectam somente parte da sensibilidade/OOD e não constituem garantia de segurança ou desempenho real.
- **Critério para avançar:** o step 06 consome contratos de predição/sinais e persistência dos steps 04/05; por isso aguarda o checkpoint combinado desses dois steps, com validação do estado integrado. Testes focados isolados não comprovam integração nem substituem o gate consolidado no ambiente gerenciado. Geração real dos artefatos permanece na etapa 07; este registro não declara o checkpoint combinado concluído e não executa add, commit ou push.

## I53 — Step 06: precedentes seguros e revisão independente — 2026-09-22

- Decisão: TF-IDF/cosseno já instalado, ajustado somente em descrições de treino Customer fechado com resolução sanitizada não vazia. Manifesto de split, IDs/grupos canônicos e hashes de fonte/configuração são obrigatórios; referência retida nunca entra no índice. Suggest consome TicketSignals centrais e bloqueia draft internamente por qualquer risco, mesmo com similaridade 1,0; PII/invalidez bloqueiam também as fontes.
- Protocolo: pacotes seeded de 30 consultas distintas, proporcionais por tipo e independentes do score; menos de 30 registra insufficient_evidence, sem duplicação/relaxamento. CSV exige quatro escalas 1–5, pseudônimo, timestamp, packet ID e fontes exatas; ausência de candidato exige reconhecimento sem notas numéricas. A grade 0,20–0,90 seleciona apenas subconjunto não vazio com médias de correção/segurança ≥4 e nenhum safety <3.
- Integridade: JSONs selados vinculam índice/fonte/split/configuração e são publicados atomicamente sem sobrescrita, inclusive concorrente. Abertura do teste exige locks dos dois domínios e decisão de recuperação; marcador persistido impede habilitação posterior da mesma versão. Resultado final pode desativar assistência e nunca altera o threshold. CLI aceita políticas JSON para modelos indisponíveis, sem fabricar binário ou sinal OOD.
- Erros/correções: Ruff encontrou linhas um caractere acima do limite; foram quebradas. A primeira fixture do CLI trouxe distribuição com somente uma classe e foi recusada por Prediction; a fixture passou a declarar toda a taxonomia, sem alterar o validador. Autocrítica acrescentou validação da versão/estado do lock, rejeição de notas que ainda exigem sanitização e publicação exclusiva contra disputa concorrente.
- Prova focada: pytest tests/test_retrieval.py -q --tb=short: 44 aprovados em 2,11 s; Ruff dos dois arquivos e checks de whitespace dos arquivos novos passaram. As avaliações são exclusivamente fixtures sintéticas identificadas; nenhum CSV humano real foi preenchido, nenhum teste real foi aberto, nenhuma API paga ou suíte completa/Codespace foi acionada.
- Motivo para avançar: o protocolo e os bloqueios agora têm regressões executáveis para a integração do step 07. CK-12 e evidência final permanecem pendentes de população elegível suficiente e avaliação humana independente; os testes não substituem essas provas. Documentação do protocolo está exclusivamente no docstring/ajuda CLI de retrieval.py.

## I54 — Step 07: integração iniciada — 2026-09-22

- Estado conferido: worktree exclusivo `002-support`, branch `submission/luis-roquette-002-support`, HEAD `2862333`, sem alterações anteriores. Os contratos existentes cobrem modelos possivelmente indisponíveis, políticas JSON, precedentes e SQLite; a UI ainda era uma prova sintética e o pipeline somente diagnóstico.
- Hipótese: os módulos podem compor o fluxo sem novo framework nem dependência; o teste real continua lacrado até decisão explícita e locks de ambos os domínios. O Codespace do mesmo repositório está parado e limpo; nenhuma sessão concorrente será reutilizada.
- Riscos identificados antes da mudança: `make demo` reinstalava dependências; a UI diagnóstica não validava manifesto; o timestamp de pacote de revisão variava entre reproduções. A correção precisa manter a comparação estrita de todos os valores, excluindo nominalmente apenas `manifest.generated_at`, sem esconder timestamps adicionais.
- Próxima prova: fixtures autocontidas executam quatro ações, falhas isoladas, revisão pendente e duas reproduções; nenhuma fixture representa atendimento, métrica ou rubrica humana real da entrega.
- Decisão de reprodução: `configuration.json` registra o início real desta avaliação, `2026-09-22T10:40:27Z`, como entrada explícita congelada. `created_at` dos pacotes deriva desse marco (não é recibo da execução); integra configuração, hashes e comparação estrita. Somente `manifest.generated_at` representa horário variável de publicação e é excluído nominalmente. Alterar a configuração invalida os locks anteriores, sem retuning silencioso.
- Falhas úteis: hash genérico de objeto joblib divergiu após load; substituído por vocabulário/IDF, parâmetros aprendidos, sigmoids e matriz esparsa canônicos, sem tolerância. CSV de revisão precisava preservar células vazias, enquanto relatório analítico usa nulos; tipos distintos agora preservam ambos. AppTest copia o corpo de funções sem seus globals: testes passaram a navegar nas páginas reais registradas pelo entrypoint. Uma fixture insuficiente removeu sete classes IT e foi corretamente recusada; corrigida para conservar uma linha de cada classe.
- Correção de raiz: CLI e UI reutilizam a mesma leitura de bytes verificados, validando schema, caminhos/dependências, configuração, lock, runtime e hash antes de joblib. Desserialização usa os bytes já verificados para impedir troca entre checagem e abertura. Sem cache persistente; código/configuração alterados tornam o estado stale. Revisão final que desativa recuperação invalida a política antiga exibida na UI.
- Preparação Git: repositório não possui workflow CI/provedor aplicável; API informou `main` sem branch protection (HTTP 404), lacuna registrada. O trabalho permanece em branch de feature sem PR; push intermediário autorizado antecede o gate pesado remoto, sem merge/publicação da entrega. Ruff e diff-check estão verdes; suíte focada é repetida após a última correção antes do checkpoint.
- Primeiro gate remoto no SHA `466ca4ee468365ba63c76ba7056e9ebab63764df`: doctor aprovado, 207 testes em 40,98 s e Ruff aprovados. Reprodução real falhou em `privacy_quarantine:suspected_name`; nenhum sucesso de reprodução foi declarado. Diagnóstico somente de sanitização (sem treino local) encontrou três textos Customer aceitos na ingestão que falhavam ao reaplicar o sanitizador; IT não apresentou essa divergência.
- Causa raiz reproduzida sem texto real: `Technical\nIssue` passava pelos detectores e só depois virava `Technical Issue`, que era recusado na próxima fronteira. Normalização de whitespace passou a ocorrer antes das validações finais; o detector continua conservador, sem allowlist adicional. Versão do sanitizador incrementada para `conservative-v2`, invalidando dados/modelos/locks anteriores. Regressão autocontida comprova quarentena na ingestão e idempotência do texto aceito; gate remoto completo será repetido no novo SHA.
- Gate corrigido: SHA `78526face7a72d02f339f80f6d5ebf9082c17263`, conferido no Codespace limpo `codex-preflight-657v7q4ggx7f5557` (4 cores, idle timeout 5 minutos), somente via gerenciador. Doctor, 208 testes em 37,32 s, Ruff e reprodução real passaram. Todos os artefatos registrados como ready foram carregados pelo validador; teste continuou lacrado, comprovado pela ausência do marcador de abertura. Fontes reais: Customer 8.469 linhas/1.389 sanitizadas; IT 47.837/26.472. Ambos classificadores ficaram supported; isso não autoriza drafts nem representa desempenho final de teste.
- Limitação real preservada: pacote de recuperação com zero consultas elegíveis e `insufficient_evidence`; nenhuma rubrica humana foi preenchida, nenhum lock de demonstração foi criado para abrir teste e nenhuma aprovação real foi fabricada. A Phase 3 deverá registrar essa impossibilidade se a população continuar insuficiente; não pode cumprir CK-12 por relaxamento ou duplicação.
- S07 candidato, aguardando revisão da Phase 2: cópia byte a byte, permissão somente leitura, em `data/runtime/validation/phase2-a8bcafccdc24fe18ca14e1b896bcf2b5d18467844bc33e2970ecba9ef69b3f6e/test_workflow.py`. SHA-256 `a8bcafccdc24fe18ca14e1b896bcf2b5d18467844bc33e2970ecba9ef69b3f6e`; comparação `cmp` passou, ignore confirmado, teste isolado de reprodução a partir da solution passou em 2,25 s. Candidato anterior `cc289ff...` fica supersedido, sem alegação de selo. O orquestrador confirma o selo somente após a revisão; nada da Phase 3 foi executado.
- Fingerprints do código/configuração/lock: `fc2aea85da793da5f383928368a6f153d6dcc8b36f18137a7dfe5149f9acfeaf` / `9458e1bd6b316f12fd63cec14b3f8f5831196600ca84acb9b8f9fe24ba8d7dce` / `0e9db579cfac4b14d713a3b76c2dab10a11d35cc13b2f6afef65d0847eda82fd`. O código/configuração não inclui runtime ou diário; hash separado do workflow protege S07. Próximo checkpoint repete os gates no commit documental que contém este registro, antes de entregar ao revisor da fase.
- Autocrítica antes da revisão: a fixture provava confiança 1,0, mas não explicitava similaridade máxima. Agora consulta uma descrição exatamente presente no índice e exige similaridade 1,0 no caso Critical, sem draft/aprovação; para PII exige fontes vazias porque a consulta inteira é bloqueada. Os 30 testes workflow passaram em 8,38 s. Código/configuração/lock permanecem iguais; somente prova e diário mudaram.
- Candidato S07 atualizado e supersedente: `data/runtime/validation/phase2-1cc3083e5483f4a3482bda8ddffa7a34fa39ef438464ae2db8fa6b10092e2aa3/test_workflow.py`, SHA-256 `1cc3083e5483f4a3482bda8ddffa7a34fa39ef438464ae2db8fa6b10092e2aa3`. Os candidatos anteriores permanecem imutáveis como histórico, sem selo definitivo. A revisão Phase 2 deve validar este último hash, com os mesmos fingerprints acima, antes do paralelo 08/09.

## I55 — Phase 2: correções focalizadas da revisão 3,9 — 2026-09-22

- Revisão da fase retornou `3,9/5`; blast radius localizado nos steps 05/07. O checkpoint começou em `1ce1564cbdbcd63cae3a51534e5998af00b238e6` com exatamente cinco arquivos alterados: `store.py`, `test_store.py`, `scripts/reproduce.py`, `ui.py` e `test_workflow.py`. Steps 04/06 e status da task permaneceram intactos; o diário é a única alteração documental adicional.
- Step 05, causa/correção: armazenamento aceitava motivos contraditórios com `auto_route`, preservando um snapshot semanticamente inválido. A fronteira agora exige exatamente `validated_threshold` para `auto_route` e o recusa em `human_review`. Regressões cobrem dez contradições, preservação da transação anterior e quatro saídas reais do gate persistidas sem alteração após reinício.
- Step 07, causa/correção CK-17: faltava dependência do modelo Customer no manifesto da fila, e a UI escondia seu estado específico. Fila de modelo suportado agora depende de `models.customer`; modelo corrompido deixa a fila stale e mostra arquivo/causa/`make reproduce`, preservando diagnóstico e IT. Modelo legitimamente unsupported conserva política JSON e revisão manual, sem inventar um binário obrigatório.
- Step 07, correção Low CK-2: estados e tabela Evidências passam a carregar somente caminhos relativos validados. Manifesto ausente, recurso não registrado e caminho absoluto rejeitado usam `manifest.json`; diretório pessoal não é refletido na interface. Regressões AppTest verificam bloqueio da fila e continuidade das evidências válidas, incluindo ausência da raiz absoluta nos avisos e tabela.
- Prova combinada leve: `pytest tests/test_store.py tests/test_workflow.py -q --tb=short` concluiu 109 testes em 5,52 s. Ruff integral e `git diff --check` passaram. Nenhuma rubrica foi preenchida ou teste real aberto; suíte completa/reprodução real seguem para o SHA publicado deste checkpoint via gerenciador.
- Novo candidato S07: `data/runtime/validation/phase2-57ae4fd072bb4812acc27d903990c9656677d925cffa5121f4c66293bbb80be0/test_workflow.py`, SHA-256 `57ae4fd072bb4812acc27d903990c9656677d925cffa5121f4c66293bbb80be0`. Cópia byte a byte (`cmp` aprovado), somente leitura, ignore confirmado; teste isolado de reprodução aprovado a partir da solution. Candidatos anteriores permanecem imutáveis e supersedidos; selagem formal aguarda nova revisão Phase 2.
- Fingerprints atuais código/configuração/lock: `a6d82b833a38aa114aa117b83d1f1672dbcd1415012ed7d6cece4706f0c741af` / `9458e1bd6b316f12fd63cec14b3f8f5831196600ca84acb9b8f9fe24ba8d7dce` / `0e9db579cfac4b14d713a3b76c2dab10a11d35cc13b2f6afef65d0847eda82fd`. O motivo para repetir o gate é validar a integridade conjunta do armazenamento e do grafo de dependências, não ampliar o escopo ou iniciar Phase 3.

## I56 — Phase 2 aprovada e S07 selado — 2026-09-22

- Parecer consolidado da nova revisão: `combined_score=4.5`, `issues=[]`; o orquestrador aprovou a Phase 2. Confirmadas as correções focalizadas 05/07: coerência dos motivos no armazenamento, dependência do modelo Customer na fila e diagnóstico com caminhos relativos seguros. A task recebe exclusivamente `[DONE]` nas rows 04–07 e `[REVIEWED]` no heading Phase 2, sem notas de revisão ou conclusão antecipada da Phase 3.
- Gate do checkpoint `ae53f343287d0ec319023ded19521b88226eac05`, via `codespace-manager`: doctor, 224 testes (43,71 s), Ruff, reprodução real e validação dos artefatos aprovados, exit 0. Customer: 8.469 fontes/1.389 sanitizados; IT: 47.837/26.472; diagnóstico ready e teste real lacrado. Local: 109 testes focados; nenhuma rubrica humana preenchida, nenhum lock de revisão fabricado. A aprovação permite avançar porque os contratos da fase foram comprovados, não porque a avaliação humana final já ocorreu.
- **S07 formalmente selado após a revisão:** `data/runtime/validation/phase2-57ae4fd072bb4812acc27d903990c9656677d925cffa5121f4c66293bbb80be0/test_workflow.py`, SHA-256 `57ae4fd072bb4812acc27d903990c9656677d925cffa5121f4c66293bbb80be0`. O candidato aprovado foi preservado sem reescrita: cópia byte a byte confirmada por `cmp`, permissão `0444`, ignore confirmado. Hash conferido antes/depois do teste isolado `test_reproduce_twice_same_inputs`, aprovado em 1,41 s a partir da solution. Este arquivo não deve ser editado na Phase 3; step 08 usa somente o snapshot, e step 10 valida o workflow final consolidado.
- Fingerprints selados, reconferidos sem mudança: código `a6d82b833a38aa114aa117b83d1f1672dbcd1415012ed7d6cece4706f0c741af`; configuração `9458e1bd6b316f12fd63cec14b3f8f5831196600ca84acb9b8f9fe24ba8d7dce`; lock `0e9db579cfac4b14d713a3b76c2dab10a11d35cc13b2f6afef65d0847eda82fd`. Fechamento exclusivamente documental: nenhum código, configuração, lock, dado ou rubrica foi alterado; Ruff e diff-check leves passaram. O gate completo acima pertence ao SHA explícito, não é alegado como execução no commit documental seguinte.
- Decisão: barreira Phase 2 encerrada; steps 08/09 podem ser despachados pelo orquestrador respeitando S07 e a separação de arquivos. Nenhum step da Phase 3 foi executado neste fechamento. Acompanhamento do Codespace do reviewer é somente leitura até `Shutdown`, preservando todas as sessões concorrentes.

## I57 — Step 09: documentação executiva e reprodução — 2026-09-22

- Decisão editorial: o README executivo segue o template oficial e responde diretamente
  onde a operação perde tempo, o que pode ser automatizado e como o fluxo funciona. O
  README técnico concentra setup, comandos, retomada manual dos CSVs, arquitetura,
  privacidade, exportação e o protocolo humano cuja fonte normativa continua sendo o
  docstring de `retrieval.py`.
- Honestidade preservada: quatro intervalos válidos, nenhum grupo elegível de desperdício,
  ausência de sinal confiável de satisfação e zero consultas elegíveis são limitações, não
  resultados favoráveis. Screenshot, export correlacionado e gate final permanecem
  marcados como pendentes; nenhuma métrica, avaliação humana ou publicação foi inventada.
- Contrato documental: novo teste confere os sete comandos canônicos, as três naturezas de
  evidência, as três respostas executivas, links locais existentes e ausência de links para
  `raw`, `runtime` ou `artifacts` como evidência pública.
- Verificação: teste documental isolado passou; no checkpoint conjunto, os testes dos
  steps 08/09 somaram 67 aprovações em 3,21 s. Ruff dos três testes e `git diff --check`
  passaram. O README executivo é novo e oculto pelo ignore raiz; seu staging deve ser
  explícito e restrito a esse arquivo.

## I58 — Step 08: avaliação real, freeze e evidência negativa — 2026-09-22

- Base imutável: step iniciado no commit
  `9f55bc9a56a0236ccbe99a7b37e775b71b899607`, usando o S07 formalmente selado. O teste
  isolado de reprodução passou remotamente em 5,38 s; hash antes/depois permaneceu
  `57ae4fd072bb4812acc27d903990c9656677d925cffa5121f4c66293bbb80be0`, wrapper terminou
  com exit 0, worktree remoto ficou limpo e o Codespace voltou a `Shutdown`.
- Resultados de desenvolvimento, não finais: Customer escolheu regressão logística com
  macro-F1 CV `0,1822` contra dummy `0,0721`, ganho `0,1101`, mas automação permaneceu
  desativada e sem threshold. IT escolheu LinearSVC com macro-F1 CV `0,8390` contra dummy
  `0,0548`, ganho `0,7841` e threshold de desenvolvimento `0,55`. O teste final continuou
  lacrado; esses valores não são métricas do teste congelado.
- Avaliação de recuperação: população de calibração `224`, elegíveis `0`, amostra `0` e
  revisados `0`. Os dois CSVs públicos conservam somente o cabeçalho da rubrica. Não houve
  relaxamento, duplicação, preenchimento sintético ou avaliação humana fabricada;
  `CK-12` permanece explicitamente pendente e drafts continuam bloqueados.
- Evidência operacional: 8.469 linhas Customer de origem, 1.389 sanitizadas, 1.133
  representantes e 902 linhas de desenvolvimento; quatro intervalos válidos, 21 notas de
  satisfação, `no_reliable_signal` e zero grupos de desperdício com suporte mínimo. IT
  manteve 47.837 linhas de origem e 26.472 sanitizadas. Associação não virou causalidade e
  excesso/projeção não virou economia realizada.
- Integridade acrescentada: regressões garantem taxonomia completa e denominadores por
  domínio no teste congelado, impedem reaproveitar lock com provenance stale e preservam
  byte a byte lock, marcador e pacote após a revisão final. Reprodução real e 66 testes
  focados sustentaram o step; o checkpoint conjunto repetiu os 66 testes em 2,30 s, Ruff,
  diff-check e S07 isolado em 1,28 s, mantendo o mesmo hash selado.

## I59 — Step 10: demonstração real e fechamento dos gates — 2026-09-22

- **Quatro falhas de ambiente, sem bypass:** a primeira tentativa usou o Python padrão em
  vez de 3.12; a segunda encontrou `python3.12-venv` ausente; a terceira chegou ao
  `make doctor` sem os CSVs reais ignorados; no gate do diff, o outro Codespace tinha
  `.venv`, mas não as dependências do lock (`altair` ausente). As correções foram
  declarar `PYTHON=python3.12`, instalar o módulo de venv somente no Codespace e executar
  o `make data` público previsto; o gate do diff é repetido desde `make setup`. Nenhum
  teste ou check foi removido.
- **Gate base gerenciado:** no commit `67de949e57538a80cf6e63f0d9dd7f7ccba7edcf`,
  `make doctor`, 229 testes, Ruff, reprodução dos dois datasets e 33 testes de workflow
  passaram. Fontes e sanitização permaneceram Customer `8.469 → 1.389` e IT
  `47.837 → 26.472`.
- **Decisão honesta de abertura:** zero consultas elegíveis impediram qualquer rubrica
  humana. O lock explícito `disabled` manteve drafts desligados, threshold nulo e status
  `insufficient_evidence`; a reprodução abriu o teste congelado sem alterar a política.
  `CK-12` continua incompleto. Customer final: macro-F1 `0,1394`, log loss `1,6124`, ECE
  `0,0328`, n=231; IT: `0,8351`, `0,4578`, `0,0414`, n=5.301.
- **Demonstração persistida:** a fila real abriu com 231 casos e aprovação/edição
  bloqueadas. Um escalonamento sanitizado foi salvo como `audit_id=1`; após reiniciar o
  Streamlit, o mesmo evento reapareceu e gerou CSV persistido SHA-256
  `ac24e4baa5e188b6470ea411819aef2bd051e56051a5f91d2998c98d5aa8ad96`. Scorecard e
  Laboratório IT também foram exercitados; o texto IT retornou Hardware com confiança
  `0,5464` e revisão humana abaixo do threshold `0,55`.
- **Correção de captura:** uma primeira captura de tela inteira incluiu outra janela e foi
  eliminada imediatamente, sem versionamento. A captura final ficou restrita à aba da
  aplicação, sanitizada, em `evidence/screenshot.png`, SHA-256
  `4c909dd7fce6c7d9a51e7350c7917aa463d5c7c7012ef1e7b9061d6bd9a6a1d2`; o arquivo
  eliminado não é recuperável, mas foi substituído pela evidência correta.
- **Primeira repetição do diff:** o teste final correlacionou bytes/hash da imagem e do
  CSV, audit IDs, ações e estado de CK-12. No Python 3.12 gerenciado, 230 testes passaram
  em 18,46 s, Ruff passou, a reprodução preservou as quatro contagens e os 34 testes de
  workflow passaram em 12,89 s. O shell do gerenciador foi suspenso antes do diff-check;
  esse ciclo parcial não foi aceito como gate terminal, o patch foi revertido e o
  Codespace foi parado limpo.
- **Fechamento exigido:** a mesma sequência será repetida sobre este registro final,
  incluindo `git diff --cached --check` e a prova de que todos os arquivos permanecem em
  `submissions/luis-roquette/`. CK-12 continuará pendente mesmo com o gate técnico verde.

## I60 — Phase 3: revisão 3,7 e correção focalizada do scorecard — 2026-09-22

- **Revisão e blast radius:** `combined_score=3.7`; decisão do orquestrador: FAIL. Quatro achados: (1) High, CK-12 incompleto — rubricas somente com cabeçalho, `eligible=0`, `reviewed=0`, `ck_12_complete=false`; (2) High, falta aprovação/edição real persistida — export contém somente `audit_id=1`, ação `escalate`, enquanto o DoD exige approve/edit e escalonamento após reinício; (3) High, gate terminal ainda não fechado no SHA final `eeee151008016441f6fcf1641c4b9510066acb39` — diário registra ciclo parcial e metrics referencia `67de949`; (4) Medium, scorecard afirmava teste lacrado apesar de `test_opened=true`. Blast radius: Steps 08/10 para os bloqueios de evidência/gate e Step 07 para a mensagem da UI; não há autorização para afrouxar contratos.
- **Causa e correção implementada:** a legenda do scorecard era literal e não consultava o lifecycle publicado. `ui.py` agora usa `models.metrics` validado para distinguir teste lacrado, aberto após locks e estado não verificável; `retrieval.metrics` mantém separados revisão pendente, assistência desativada e evidência insuficiente. Validação cruzada permanece explicitamente de desenvolvimento e associação não implica causalidade. Abrir teste não é apresentado como aprovação humana ou autorização de drafts.
- **Prova do bloqueio CK-12:** a inspeção factual comunicada pelo orquestrador encontrou 224/224 consultas de calibração excluídas como `ambiguous`, somente cinco resoluções seguras no índice e mínimo contratual de 30 consultas elegíveis. A versão/política está congelada e o teste já foi aberto. Não se pode retunar essa versão após observar o teste, inventar rubricas, transformar ausência de evidência em aprovação ou liberar drafts para produzir uma demonstração de approve/edit. Os achados High (1)/(2) permanecem bloqueados; o evento real de escalonamento não substitui os eventos ausentes.
- **Verificação focalizada:** diff inicial restrito a `src/support_copilot/ui.py` e `tests/test_workflow.py`; sete cenários novos cobrem sealed/opened/disabled/insufficient/pending/unknown/corrupt, mais uma regressão de UI após abertura real do pipeline de fixtures. Os 41 testes de workflow passaram em 5,84 s; Ruff e diff-check passaram. S07 permaneceu sem edição, somente leitura (`0444`) e ignorado: `data/runtime/validation/phase2-57ae4fd072bb4812acc27d903990c9656677d925cffa5121f4c66293bbb80be0/test_workflow.py`, SHA-256 `57ae4fd072bb4812acc27d903990c9656677d925cffa5121f4c66293bbb80be0`. A regressão atual é distinta do snapshot selado da Phase 2.
- **Decisão e próximo gate:** publicar a correção de UI e este registro contemporâneo, sem modificar task status, evidence ou READMEs. O Medium está corrigido; o High (3) exige novo gate remoto completo terminal no SHA exato publicado, sem atribuir o resultado anterior a este diff. Os High (1)/(2) não serão fabricados nem escondidos: continuarão explícitos até decisão do dono sobre o bloqueio contratual. Nenhuma rubrica, versão congelada ou política de segurança foi alterada neste checkpoint.

## I61 — Correção canônica Data + Analytics contra o briefing — 2026-09-22

- **Revisão do critério:** a releitura do briefing obrigatório (`challenges/process-002-support/README.md`, linhas 62–68) confirmou que este checkpoint deve provar gargalos, associações com satisfação e desperdício do Dataset 1. Exigir CK-12 completo e eventos approve/edit como condição do diagnóstico foi sobre-especificação: esses controles continuam relevantes para assistência e decisão humana, mas sua ausência não autoriza invalidar a análise nem fabricar avaliações ou aprovações.
- **Gap real encontrado:** o diagnóstico anterior reutilizava a lane textual depois da quarentena de privacidade, deduplicação e split. Das 8.469 linhas brutas, a lane textual preserva 1.389 e 1.133 representantes; somente train + calibration entravam na análise: 902 linhas, quatro intervalos válidos e 21 avaliações. Assim, a proteção correta para texto descartava observações estruturadas úteis e tornava o diagnóstico operacional não representativo.
- **Hipótese e decisão two-lane:** separar finalidades preservaria simultaneamente privacidade e cobertura. A lane textual permanece inalterada para modelos/retrieval e seus splits; a nova `structured_operational-v1` relê a fonte bruta, mantém somente campos operacionais allowlisted, nenhum texto, contato, demografia, produto ou resolução, e é proibida de entrar em `make_split`. O manifest registra fonte, versão, qualidade e dependência própria para impedir mistura silenciosa.
- **Prova real:** a lane estruturada analisa 8.469/8.469 linhas, com 1.404 intervalos pós-resposta válidos e 2.769 avaliações. Os maiores gargalos unidimensionais são Chat (mediana 6,52 h), High (7,12 h) e Product inquiry (6,98 h); a pior combinação é Chat / Low / Technical issue (13,23 h; n=15). O proxy histórico soma 4.047,83 h acima das medianas dos pares em 20 grupos suportados; Refund request / High lidera com 274,17 h. Custo e moeda não existem na fonte e permanecem premissas explícitas, nunca resultado observado.
- **Satisfação e limitação causal:** nos 1.404 pares com intervalo, Spearman é `0,00264`; Ridge teve MAE `1,2026` contra `1,1867` do baseline, piora relativa de `1,34%`. A conclusão canônica é `no_reliable_signal`: diferenças descritivas por canal, prioridade e tipo não provam influência causal. Também permanecem explícitos o viés de 5.700 avaliações ausentes, a baixa cobertura temporal e o fato de excesso observado não ser economia realizada.
- **Erros e correções do próprio loop:** a primeira integração fez reprodução e UI calcularem hashes de configuração diferentes após versionar a lane; o scorecard rejeitou artefatos válidos como stale. `current_environment()` passou a espelhar `analytics_schema`, e o mesmo conjunto foi repetido. No checkpoint, uma invocação do pytest desde a raiz do monorepo também falhou porque `test_workflow.py` ancora fixtures em `Path.cwd()`; o comando foi corrigido para partir da solução, sem alterar teste. Resultado local final: 35 testes focados, incluindo fonte real, reprodução determinística, lifecycle e scorecard; Ruff e diff-check verdes. O avanço para publicação ocorre porque denominadores, proveniência, privacidade e conclusões negativas agora são testados, não porque CK-12 foi relaxado.

## I62 — Correção da autoridade canônica na SPEC e documentação — 2026-09-22

- **Autoridade corrigida:** o Challenge 002 e o guia de submissão são a fonte máxima. Eles
  exigem diagnóstico concreto do Dataset 1, uso dos dois datasets, proposta explícita do
  que automatizar e não automatizar, fluxo prático, protótipo real e process log. Não
  exigem 60 avaliações humanas nem uma aprovação/edição real quando nenhum draft seguro
  existe.
- **Erro da SPEC:** a arquitetura transformou CK-12 — uma validação interna desejável da
  recuperação — e uma evidência real de approve/edit em blockers da Phase 3 e do DoD. Essa
  sobre-especificação confundiu um gate para habilitar respostas sugeridas com um gate do
  challenge inteiro. O diário anterior permanece intacto para mostrar como o erro surgiu e
  foi detectado; nenhuma revisão anterior foi reescrita.
- **Correção:** CK-12 passa a evolução opcional futura. Zero consultas elegíveis continua
  bloqueando drafts, sem relaxar privacidade, risco, freeze, abstinência ou precedência
  humana. O escalonamento real, persistido após reinício e exportado com audit ID, demonstra
  a intervenção humana pedida pelo briefing. Aprovação/edição real só é exigível quando
  houver draft seguro; seus controles continuam testados.
- **Diagnóstico reintegrado aos READMEs:** 8.469 linhas estruturadas; 1.404 intervalos e
  2.769 ratings. Chat `6,52 h` (`355/2.073`), High `7,12 h` (`355/2.085`), Product inquiry
  `6,98 h` (`257/1.641`) e Chat / Low / Technical issue `13,23 h` (`n=15`). O proxy soma
  `4.047,83 h` em 20 grupos; Refund request / High lidera com `274,17 h`.
- **Satisfação e ROI:** Spearman `0,00264` em 1.404 pares; Ridge MAE `1,2026` contra
  baseline `1,1867`, logo `no_reliable_signal`. A fonte não contém custo, moeda ou salário;
  cenários permanecem parametrizados e o proxy não é economia realizada. Phase 3 não foi
  marcada como reviewed/done neste alinhamento; o próximo gate deve revisar o estado
  corrigido, não reutilizar o parecer baseado na SPEC sobre-especificada.

## I63 — Step 10: fechamento canônico e demonstração real — 2026-09-22

- **Autoridade e escopo:** a validação final voltou ao Challenge 002 e ao guia de
  submissão. CK-12, S07 e approve/edit são extensões opcionais, não blockers do briefing.
  Os controles de segurança permanecem: `eligible=0`, `reviewed=0`, threshold nulo,
  drafts desativados e nenhuma rubrica ou aprovação fabricada.
- **Reprodução desde zero:** no commit
  `6ebd9e89799c8ae49f474d859b4a6d4f11c009b3`, o Codespace limpo removeu somente
  `.venv`, `artifacts`, `data/raw` e `data/runtime`, todos ignorados e não rastreados.
  `make setup`, `make data`, checksums, `make doctor` e `make reproduce` passaram.
  Customer: `b06a9cde...bf8bea`; IT: `044fdace...dd4d4`. O tar transferido teve SHA-256
  `4425cfed...a602a`, sem alteração rastreada.
- **Abertura segura para demo:** o fluxo documentado `lock-review --decision disabled`
  congelou a política como `insufficient_evidence`, `drafts_enabled=false` e
  `threshold=null`; nova reprodução liberou a fila final sem S07. Estado real:
  `released_after_locks`, Customer `n=231`, IT `n=5.301`, população de recuperação 224 e
  zero elegíveis. O pacote transportado teve SHA-256 `e11a2179...d4a6a9`.
- **Demonstração operacional real:** a fila abriu com 231 tickets e os botões de
  aprovação/edição corretamente bloqueados. O escalonamento de `customer:2787` foi
  persistido e relido como `audit_id=1`; após reiniciar o Streamlit, reapareceu no banco e
  no painel. O export persistido possui uma linha, ação `escalate`, e SHA-256
  `5d832e99...357e5b`. O Laboratório IT classificou o texto sanitizado como Hardware,
  confiança `0,9701`, e `auto_route` no threshold `0,55`.
- **Prova visual e diagnóstico:** a captura restrita à aba, sem dados pessoais, registra o
  scorecard real em `2832×974`, PNG SHA-256 `bea793bc...6428cc`: 8.469 linhas, 1.404
  intervalos e mediana pós-resposta de `6,34 h`, além dos gargalos já documentados. O CSV,
  a imagem e os números foram vinculados em `evidence/metrics.json`; o resumo operacional
  publicado deriva byte a byte de `artifacts/analytics/operational-summary.json`.
- **Falhas e correções do loop:** o primeiro preflight encontrou Python diferente de 3.12;
  o runtime 3.12 foi instalado somente no Codespace. Em seguida, as fontes estavam
  ausentes; `make data` restaurou-as com checksums verificados. Uma asserção auxiliar
  consultou o campo errado (`models.customer.status`); foi corrigida para o contrato real
  (`status=released_after_locks`, `domains.customer.status=evaluated`), sem mudar produto.
  Na demo, o primeiro motivo em português foi recusado pela quarentena conservadora; a
  tentativa não gravou linha e foi repetida com `Critical priority requires human review.`,
  que passou pela mesma sanitização. Nenhum gate foi relaxado.
- **Limitações preservadas:** CK-12 continua opcional e incompleto; nenhuma avaliação
  humana independente existe e nenhum draft seguro foi habilitado. A captura prova a UI
  local, não envio externo. O proxy de excesso não é economia realizada; custo e moeda não
  são observados. O gate integral do novo SHA publicado será registrado somente após
  executar setup, dados, doctor, suíte, Ruff, reprodução, workflow, documentação e diff
  no Codespace limpo.

## I64 — Phase 3 aprovada pela matriz canônica — 2026-09-22

- **Matriz aplicada:** a revisão voltou à autoridade máxima do Challenge 002 e do guia de
  submissão: diagnóstico concreto do Dataset 1; uso independente dos dois datasets;
  automação, não automação e fluxo prático; protótipo real; process log; números e ROI
  transparentes. CK-12, S07 e approve/edit real permanecem extensões opcionais e não
  substituem os critérios do briefing.
- **Resultado:** `combined_score=4,7`, sem issue bloqueadora. O diagnóstico estruturado,
  modelos por domínio, gate conservador, escalonamento persistido/exportado, screenshot,
  scorecard, Laboratório IT e diário sustentam a Phase 3. A insuficiência de recuperação
  continua explícita e mantém drafts desligados; nenhuma rubrica ou aprovação foi
  fabricada.
- **Sobre-especificações removidas:** 60 avaliações humanas e approve/edit real deixaram
  de ser blockers do DoD quando não existe draft seguro. A segurança não foi relaxada:
  zero elegíveis, threshold nulo, abstinência e intervenção humana continuam preservados.
- **Low corrigido:** os READMEs não repetem mais as contagens antigas `229/33` e `230/34`.
  A evidência técnica mais recente disponível registra 242 testes completos, 41 testes de
  workflow e 2 testes de documentação/evidência aprovados.
- **Limite do gate:** por instrução do owner, o preflight terminal do SHA final foi pulado
  e não é marcado como verde. A aprovação 4,7 não converte esse comando não executado em
  evidência. Decisão SDD: marcar somente steps 08–10 `[DONE]` e Phase 3 `[REVIEWED]`, sem
  antecipar o DoD geral; avançar agora para sua verificação específica.

## I65a — Correção factual do README no DoD — 2026-09-22

- O verificador retornou DoD `4/5`: o README técnico ainda descrevia uma execução IT antiga
  (`0,5464`, revisão humana), divergente da demonstração final persistida.
- Correção restrita à documentação: Hardware, confiança `0,9701`, `auto_route` no threshold
  `0,55`, conforme a evidência final. Nenhum código, teste, evidence ou checkbox do DoD foi
  alterado; o item deve ser reavaliado após este checkpoint.

## I65 — Definition of Done verificada — 2026-09-22

- **Primeira rodada:** o verificador independente encontrou `4/5` itens aprovados. O único
  desvio era factual e documental: o README técnico descrevia a observação IT anterior de
  `0,5464` com revisão humana, enquanto a demonstração final registrava Hardware com
  confiança `0,9701` e `auto_route` no threshold `0,55`.
- **Correção e nova rodada:** I65a alinhou somente o README à evidência final. A
  reverificação no SHA `9f5acae66ed3fd6b1b01f1d6d186d0bb426589ea` confirmou `5/5` itens
  do DoD: evidência canônica, domínios independentes, escalonamento persistido, entrega
  pública sanitizada e processo SDD aprovado.
- **Checks da reverificação:** os dois testes de documentação/evidência passaram em
  `1,41 s`; os links locais são verificados pelo contrato documental; Ruff do teste e
  `git diff --check` passaram. Os hashes públicos permaneceram `bea793bc...6428cc` para
  o screenshot e `5d832e99...357e5b` para o CSV; o diff continua restrito a
  `submissions/luis-roquette/` e nenhum raw, runtime, modelo gerado ou banco foi rastreado.
- **Limites preservados:** CK-12 continua opcional, com zero consultas elegíveis e drafts
  desativados. O preflight terminal do SHA final foi pulado por instrução do owner e não é
  declarado verde; essa decisão permanece visível, sem ocultar gate ou simular execução.
- **Resultado:** os cinco checkboxes do DoD foram marcados `[X]`. A task permanece em
  `in-progress`; movimentação para `done`, PR ou publicação não fazem parte deste checkpoint.

## I66 — Redundância Necessária R1: NOT CLEAN — 2026-09-22

- **Resultado da rodada:** `NOT CLEAN`, com `1 High / 2 Medium`; streak reiniciado em
  `0/2`. O High era a contradição entre o bypass explícito do owner e CK-20 ainda tratar
  preflight terminal verde como bloqueador. Os Medium eram setup incompleto para clone
  limpo e legenda da screenshot atribuindo persistência que ela não mostra.
- **Decisão do owner preservada:** o preflight terminal foi pulado por instrução explícita.
  A task agora exige integridade documental: registrar `não executado/não verde`, sem
  transformar resultados de outro SHA em aprovação. O DoD permanece `[X]` porque o
  briefing canônico não exige esse preflight e a decisão não foi ocultada.
- **Setup corrigido:** clone limpo executa setup/dados/doctor, primeira reprodução,
  `prepare-review`; quando `eligible=0`, congela `lock-review --decision disabled`, repete
  `make reproduce` e só então abre `make app`. Com elegíveis, usa rubrica real em vez do
  lock disabled.
- **Evidência corrigida:** a screenshot é identificada somente como Scorecard. Persistência
  e `audit_id=1` são sustentados exclusivamente por `decisions-demo.csv` e seu SHA-256
  `5d832e99...357e5b` registrado em metrics. Nenhuma captura ou evidência foi recriada.
- **Próximo critério:** executar nova rodada completa de Redundância. Esta correção encerra
  R1 em `0/2`; somente duas rodadas limpas consecutivas fecham a etapa.

## I67 — Redundância Necessária R2: CLEAN — 2026-09-22

- **Base auditada:** SHA `ed67f5cadb5a5103b87c7cb03f2d6c41c2ea05bf`.
- **Resultado:** `CLEAN`; a regressão dos três achados de R1 confirmou CK-20 coerente com a
  decisão do owner, setup completo para clone limpo e separação correta entre screenshot
  de Scorecard e CSV/hash de persistência. Nenhum novo erro, gap ou otimização necessária.
- **Verificação:** 2 testes de documentação/evidência e `git diff --check` passaram. O
  preflight terminal continua explicitamente `não executado/não verde`.
- **Ponytail:** revisão não encontrou código, dependência ou abstração a remover; nenhum
  corte foi feito porque os contratos existentes são necessários para os gates seguros.
- **Streak:** `1/2`; falta uma rodada limpa consecutiva para encerrar a Redundância.

## I75 — Lapidação R1: NOT CLEAN — 2026-09-22

- **Resultado da rodada:** `NOT CLEAN`, com `3 Medium / 1 Low`; streak da Lapidação
  reiniciado em `0/2`.
- **Correções publicadas:** o SHA `c4ab1074a75555939f7412b7491ba41d58ebba6a`
  incorpora as três correções de UI: preservação segura do rascunho por ticket na sessão,
  localização/apresentação em PT-BR e hierarquia legível do scorecard. A validação focada
  concluiu 44 testes; Ruff e `git diff --check` passaram.
- **Melhoria visual opcional:** a nova screenshot da fila não foi executada por ordem do
  owner de manter o bypass e não iniciar Codespace. A tentativa não iniciou ambiente nem
  realizou mutação. Nenhuma captura ou alegação de evidência nova foi produzida.
- **Evidência preservada:** a screenshot pública atual continua sendo apenas o Scorecard e
  permanece corretamente rotulada como tal; ela não é apresentada como captura da fila.
- **Próximo critério:** a streak permanece em `0/2`; são necessárias duas rodadas limpas
  consecutivas para encerrar a Lapidação.

## I76 — Lapidação R2: CLEAN — 2026-09-22

- **Base auditada:** SHA `d0b89ecc15a430055904f5c06fea7c5de4a65b35`.
- **Resultado:** `CLEAN`; a regressão da UI não encontrou nova correção, melhoria ou
  otimização relevante.
- **Verificação:** 4 testes passaram e Ruff passou; `git diff --check` permaneceu sem
  erros no checkpoint documental.
- **Boundary preservado:** nenhum preflight remoto nem navegador foi executado nesta
  rodada; nenhuma alegação de evidência visual ou gate verde foi acrescentada.
- **Streak:** `1/2`; falta uma rodada limpa consecutiva para encerrar a Lapidação.

## I77 — Lapidação R3: CLEAN — 2026-09-22

- **Base auditada:** SHA `1a569740051dffcf498ef9ce6221c38621f65f38`.
- **Correção do parecer:** a suposta duplicação em I73 era falso positivo; existe uma única
  frase `Streak e encerramento`, quebrada visualmente em duas linhas. Nada foi removido.
- **Resultado:** `CLEAN`; a regressão da UI e a verificação de consistência não encontraram
  nova correção, melhoria ou otimização relevante.
- **Boundary preservado:** nenhum preflight, navegador ou `make reproduce` foi executado;
  nenhuma alegação de gate remoto, prova visual nova ou reprodução foi acrescentada.
- **Streak e encerramento:** `2/2` rodadas limpas consecutivas. A etapa de Lapidação está
  encerrada.

## I78 — Envio obrigatório por PR — 2026-09-22

- **Canal de submissão:** PR
  [#141](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/pull/141)
  aberto com o título exato `[Submission] Luis Roquette — Challenge 002`, estado `OPEN` e
  SHA inicial `7bea6aa02ae9a4a63987e1d1367a5342332e74d7`.
- **Estado observado:** `mergeStateStatus=CLEAN`; `statusCheckRollup=[]`, portanto nenhum
  check automático estava registrado no momento da consulta.
- **Limites preservados:** o preflight final foi pulado por decisão do owner e continua
  não executado/não verde. PR aberto não significa aprovação nem merge; nenhum merge foi
  presumido.

## I74 — Lapidação R1: checkpoint de UI, NOT CLEAN — 2026-09-22

- **Resultado da rodada:** `NOT CLEAN`, com `3 Medium / 1 Low`; streak da Lapidação `0/2`. Este checkpoint corrige a UI, não encerra a rodada nem substitui nova inspeção visual. A captura atualizada continua pendente para o agente de evidence; nenhum screenshot foi produzido ou alterado aqui.
- **Correções de interação:** resposta final, motivo, UUID e confirmação ficam associados ao ticket em `st.session_state`. Widgets fora do formulário permitem capturar a edição antes da troca; alterações não persistidas são preservadas e recebem aviso claro ao selecionar outro ticket. Retornar recupera o conteúdo; falha de gravação mantém tentativa/UUID; persistência confirmada limpa o dirty state e impede duplicação. A preservação é da sessão Streamlit, não uma alegação de persistência de rascunhos após sessão nova.
- **Correções de apresentação:** estados, motivos, categorias e encaminhamentos apresentados em PT-BR; tabelas usam rótulos de coluna, percentuais e nulos legíveis, em cópias de apresentação. JSON e códigos brutos ficam em `Detalhes técnicos`. O scorecard usa título de página (`st.title`). Valores internos, políticas fail-closed, banco e export permanecem inalterados.
- **Verificação:** 44 testes focados de workflow passaram em 5,98 s; Ruff e diff-check passaram. As regressões cobrem troca imediata/retorno, falha e sucesso de gravação, limpeza do dirty state, labels, separação dos detalhes técnicos, formatos e heading. A primeira execução local encontrou `setuptools` ausente; foi instalado somente `setuptools==84.0.0`, já fixado no lock, via uv na `.venv` existente, sem mudar o lock. O gate remoto terminal continua não executado neste checkpoint; não se infere sucesso remoto dos checks locais.
- **Escopo e snapshot:** somente `ui.py`, `test_workflow.py` e este diário entram no commit; evidence, READMEs e task permanecem intactos. S07 não está presente no runtime local atual; é opcional para este checkpoint de lapidação e não foi reconstruído a partir do workflow mutável nem apresentado como evidência recém-verificada. O próximo passo é atualizar a captura pelo agente de evidence e realizar nova rodada; streak permanece `0/2`.

## I73 — Redundância Necessária R8: CLEAN — 2026-09-22

- **Base auditada:** SHA `a687ec26b203b8785940d58aa57f0bbd16407bf4`.
- **Resultado:** `CLEAN`; nenhuma nova correção, melhoria ou otimização relevante foi
  encontrada na regressão da rodada.
- **Verificação:** 4 testes passaram; Ruff e `git diff --check` passaram. O doctor local
  detectou ambiente divergente e orientou corretamente executar o setup, sem alegar que o
  ambiente local estava pronto.
- **Limites preservados:** preflight terminal não executado/não verde; PR obrigatório de
  submissão ainda pendente; CK-12 permanece validação futura opcional, com drafts bloqueados.
- **Streak e encerramento:** `2/2` rodadas limpas consecutivas. A etapa de Redundância
  Necessária está encerrada.

## I68 — Redundância Necessária R3: NOT CLEAN — 2026-09-22

- **Resultado da rodada:** `NOT CLEAN`, com um único achado Low; streak reiniciado em
  `0/2`.
- **Causa:** as três fases estavam `[REVIEWED]`, os dez steps `[DONE]` e o DoD `5/5 [X]`,
  mas a task permanecia fisicamente em `.specs/tasks/in-progress/`, divergindo do ciclo de
  vida obrigatório da skill `implement-task`.
- **Correção:** movimentação rastreada por `git mv` para
  `.specs/tasks/done/implement-support-decision-copilot.feature.md`. Nenhum link interno
  exigiu ajuste; os subtasks permanecem no diretório estável previsto pela metodologia.
- **Escopo preservado:** nenhum código ou evidence foi alterado. Uma nova rodada completa
  é necessária; somente duas rodadas limpas consecutivas encerram a Redundância.

### Correção contemporânea de I68

- A frase “Nenhum link interno exigiu ajuste” estava incorreta. A movimentação da task
  revelou dez campos `Task File` nos subtasks e referências ativas na análise e no plano
  que ainda apontavam para `tasks/draft`. R4 corrige esses ponteiros sem apagar o registro
  original e distingue requisitos históricos da autoridade canônica atual.

## I69 — Redundância Necessária R4: NOT CLEAN — 2026-09-22

- **Resultado da rodada:** `NOT CLEAN`, com `1 Medium / 1 Low`; streak reiniciado em
  `0/2`.
- **Medium:** os dez subtasks ainda apontavam para a task em `draft`; análise, plano e
  auditoria de conformidade também mantinham referências ou bloqueadores pré-implementação
  conflitantes sobre rubricas, preflight verde e PR.
- **Low:** I68 afirmou incorretamente que nenhum link interno exigia ajuste. A correção
  contemporânea acima preserva a história e explicita o erro.
- **Correções:** os dez `Task File` agora apontam para `tasks/done`; análise e plano usam
  a task concluída como referência canônica e rotulam claims antigos como históricos e
  superseded; a auditoria preserva seu contexto, mas aponta o estado atual e o bypass do
  owner. Nenhum Regular Check foi marcado.
- **Escopo preservado:** nenhum código ou evidence foi alterado. A streak permanece em
  `0/2`; uma nova rodada completa e limpa é necessária.

## I70 — Redundância Necessária R5: NOT CLEAN — 2026-09-22

- **Resultado da rodada:** `NOT CLEAN`, com `1 Medium / 1 Low`; streak reiniciado em
  `0/2`.
- **Medium:** a auditoria, a análise e o plano tratavam o PR como requisito superseded ou
  não canônico. O guia de submissão e o CONTRIBUTING, porém, definem o PR como único canal
  obrigatório de envio.
- **Low:** a task concluída ainda dizia, no presente, que não havia aplicação, Makefile ou
  testes, embora esse fosse apenas o inventário pré-implementação.
- **Correções:** PR voltou a ser requisito obrigatório de submissão, ainda não aberto nem
  presumido durante a construção; o preflight continua pulado pelo owner e não verde, e o
  CI do futuro PR deverá ser acompanhado. O inventário da task foi rotulado como histórico
  e distingue o estado final. RC-2 permaneceu desmarcado.
- **Escopo preservado:** nenhum código ou evidence foi alterado. A streak permanece em
  `0/2`; uma nova rodada completa e limpa é necessária.

## I71 — Redundância Necessária R6: NOT CLEAN — 2026-09-22

- **Resultado da rodada:** `NOT CLEAN`, com `1 Medium / 1 Low`; streak reiniciado em
  `0/2`.
- **Medium:** `make setup` instalava o lock e depois abria um ambiente PEP 517 isolado;
  `setuptools>=75` podia resolver uma versão fora do lock enquanto o README sugeria setup
  sem resolução ou rede.
- **Low:** os fallbacks de dados diziam para baixar uma URL de ZIP e salvar o CSV no path
  final, instrução ambígua que poderia gravar bytes compactados com extensão `.csv`.
- **Correções:** `setuptools==84.0.0` está fixado no `pyproject.toml` e no lock; bootstrap e
  editable reutilizam esse backend com `--no-build-isolation`. README e mensagens agora
  declaram a rede/cache exigida no primeiro setup e mandam baixar o ZIP, extrair o CSV
  esperado e movê-lo ao caminho exato. Testes de regressão cobrem os dois contratos.
- **Validação:** 13 testes focados passaram; Ruff e `git diff --check` passaram sem erros.
- **Escopo preservado:** nenhuma task ou evidence foi alterada. A streak permanece em
  `0/2`; uma nova rodada completa e limpa é necessária.

## I72 — Redundância Necessária R7: CLEAN — 2026-09-22

- **Base auditada:** SHA `d5664a1b754e3650b751cb0d6fc9c4b33446450e`.
- **Resultado:** `CLEAN`; a regressão dos achados de R1–R6 não encontrou novo erro, falha,
  gap, melhoria ou otimização relevante.
- **Verificação:** 4 testes passaram; Ruff e `git diff --check` passaram. O preflight
  terminal continua pulado por decisão do owner e explicitamente `não executado/não verde`.
- **Streak:** `1/2`; falta uma rodada limpa consecutiva para encerrar a Redundância.

## I73 — Deploy público de demonstração — 2026-09-22

- **Decisão do owner:** publicar o output para inspeção, sem concluir nem enviar a entrega
  aos avaliadores.
- **Destino:** Streamlit Community Cloud, branch
  `submission/luis-roquette-002-support`, entrypoint `deploy_app.py`.
- **Falha encontrada:** o bootstrap lia todas as versões de `requirements.lock`, mas o
  deploy instalava somente quatro dependências. A correção fez `requirements.txt`
  consumir o lock completo.
- **Evidência:** a demo pública carregou Fila diária, Scorecard, Laboratório IT e
  Evidências. Uma entrada sem PII foi classificada como Armazenamento, com confiança de
  `95,31%` e encaminhamento automático.
- **Limite observado:** o primeiro boot levou cerca de 10 minutos e sofreu redução
  temporária de CPU na camada gratuita; depois disso, a aplicação permaneceu funcional.
- **URL:** https://support-decision-copilot-luis.streamlit.app/
- **Entrega:** PR permanece aberto; nenhum merge ou envio final aos avaliadores foi feito.

## I74 — Redesign UI/UX com Frontend Design — 2026-09-22

- **Diagnóstico do owner:** a interface funcional ainda estava visualmente muito aquém do
  produto; esta rodada passa a tratar UI/UX como parte explícita da qualidade da entrega.
- **Método:** aplicação da skill `frontend-design`, preservando o fluxo e os contratos já
  testados. Direção escolhida: central de operações editorial, com fundo marfim técnico,
  navegação escura, verde-lima como sinal operacional e coral para alertas.
- **Implementação:** sistema visual responsivo e acessível, hierarquia editorial, heróis,
  indicadores, seções numeradas, estados de foco, tabelas, filtros e ações reorganizados
  nas quatro superfícies: Fila diária, Scorecard, Laboratório IT e Evidências.
- **Validação local leve:** `py_compile`, Ruff e `git diff --check` passaram; os 45 testes
  focados de workflow e deploy passaram em 8,09 segundos.
- **Commit publicado:** `d480e92 feat(support): redesign Streamlit operations cockpit`.
  O preflight pesado permanece deliberadamente não executado/não verde por decisão do
  owner. O PR segue aberto, sem merge e sem entrega final aos avaliadores.
- **Evidência visual:** a checagem do deploy público foi iniciada; a validação final das
  quatro telas será registrada assim que a versão publicada estiver visível no navegador.
- **Falha de deploy encontrada na validação:** após o reinício no SHA `d480e92`, as páginas
  secundárias falharam com `ModuleNotFoundError: support_copilot`. O runner multipágina do
  Streamlit não preservou o `sys.path` preparado pelo entrypoint; a correção passa a
  inicializar `src` em cada página e inclui teste de regressão desse contrato.
- **Gap visual encontrado no browser:** o seletor de acessibilidade que ocultava o título
  nativo do Streamlit também alcançava o `<h1>` do hero. O título visual foi convertido em
  heading ARIA próprio, preservando semântica e tornando a hierarquia visível.
- **Evidência visual ao vivo:** após o rebuild, Fila diária, Scorecard, Laboratório IT e
  Evidências renderizaram com a nova navegação, hierarquia, KPIs, tabelas e formulários.
  A revisão ocorreu no browser contra o deploy público; nenhum merge ou envio final foi
  realizado.
- **Fechamento visual:** o reboot final iniciado às `20:46 UTC` carregou o commit
  `72f485a`; os títulos “Fila diária” e “Diagnóstico operacional” foram confirmados
  visíveis no hero do deploy público. O primeiro carregamento levou cerca de 17 minutos
  sob limitação temporária de CPU do Streamlit, sem traceback ou falha funcional.

## I75 — Avaliação da pergunta central e plano para nota ≥ 9,5 — 2026-09-22

- **Decisão do owner:** tratar como prioridade central a resposta ao Diretor de Operações:
  onde há perda de tempo, o que pode ser automatizado com IA e qual prova funcional
  demonstra que a proposta funciona. O redesign visual, isoladamente, não encerra o
  desafio.
- **Avaliação exigente do estado atual:** nota média estimada em `8,0/10`, com intervalo
  provável de `7,6–8,4`. Diagnóstico: `8,8`; automação: `7,2`; prova funcional: `8,5`.
  Cobertura total estimada entre `80%` e `85%` da pergunta central.
- **Forças comprovadas:** diagnóstico numérico e honesto; `4.047,83 h` de excesso
  histórico; pior combinação explicitada; ausência de sinal confiável de satisfação
  documentada; modelo IT com macro-F1 `0,8351`; aplicação pública, gate de risco,
  persistência e export reais.
- **Gaps que impedem 9,5:** a resposta executiva está fragmentada; o modelo Customer tem
  macro-F1 `0,1394` e automação desativada; não há percentual seguro e atual de tickets
  Customer automatizáveis; o simulador abre com volume zero; não existe piloto com metas
  e critérios de aprovação; a prova é um protótipo isolado, sem integração ou mensuração
  antes/depois.
- **Plano — Frente 1, resposta única ao Diretor:** criar uma tela inicial executiva com
  as três respostas, números principais, qualidade da evidência, recomendação e próximo
  experimento. Torná-la a rota padrão, preservando Fila, Scorecard, Laboratório IT e
  Evidências como aprofundamentos.
- **Plano — Frente 2, robustez do diagnóstico:** mostrar cobertura `1.404/8.469`, tamanho
  de amostra e incerteza por achado; separar ranking suportado de achados exploratórios;
  não apresentar grupos pequenos, como `n=15`, sem alerta ou intervalo de confiança.
- **Plano — Frente 3, automação Customer verificável:** executar análise de erros e novas
  candidatas congeladas sem vazamento; medir curva risco-cobertura e percentual realmente
  elegível. Só habilitar roteamento se superar baseline, calibração e erro seletivo máximo;
  caso contrário, declarar `0% seguro hoje` e demonstrar o copiloto humano como decisão
  correta, sem maquiar o resultado.
- **Plano — Frente 4, impacto e piloto:** preencher um cenário executivo, explicitamente
  projetado, usando o contexto de aproximadamente `30 mil tickets/ano`; mostrar horas por
  mês/ano e custo somente quando a premissa for informada. Definir piloto shadow de duas
  semanas, amostra, baseline, métricas, guardrails e critérios go/no-go.
- **Plano — Frente 5, prova e gate final:** demonstrar no navegador a narrativa completa,
  incluindo classificação, bloqueio seguro, decisão persistida, reinício e export;
  atualizar evidências e matriz de rastreabilidade do briefing; executar testes focados e
  o preflight canônico remoto antes da entrega final, sem usar o Mac para gates pesados.
- **Critério de encerramento ≥ 9,5:** três respostas compreensíveis em menos de 90 segundos;
  toda afirmação marcada como observada, medida ou projetada; automação Customer com
  cobertura e risco quantificados, ainda que resulte em zero; cenário anual acionável;
  piloto executável; demo pública e evidências reproduzíveis no mesmo SHA.
- **Limite desta etapa:** somente planejamento e documentação foram alterados. Nenhum
  código, threshold, métrica ou evidência foi modificado para elevar artificialmente a
  avaliação.

## I76 — Goal ≥ 9,5 · Frente 1: resposta executiva única — 2026-09-22

- **Implementação:** “Resposta ao Diretor” tornou-se a rota inicial. A tela reúne, antes
  dos detalhes técnicos, onde há perda de tempo, o que automatizar e qual prova já roda.
  Fila diária passou a ser aprofundamento separado, sem perda funcional.
- **Decisão explícita:** a tela afirma `0% Customer seguro hoje`; não usa a qualidade do
  modelo IT para autorizar automação Customer e recomenda piloto shadow sem envio externo.
- **Evidência apresentada:** `4.047,83 h` de excesso observado, cobertura temporal,
  macro-F1 IT no teste congelado e cadeia de diagnóstico, teste, fila e recuperação.
- **Validação:** 45 testes de workflow passaram em `7,43 s`; Ruff e `py_compile` passaram.
- **Medição após a frente:** diagnóstico `9,0`, automação `7,7`, prova funcional `8,8`;
  média simples `8,5/10`. Crescimento: `+0,5`. O Goal ainda não foi atingido.

## I77 — Goal ≥ 9,5 · Frente 2: confiabilidade diagnóstica — 2026-09-22

- **Implementação:** o Scorecard agora expõe cobertura válida, tamanho de amostra,
  intervalo de confiança de 95% da mediana e situação de suporte de cada combinação.
- **Decisão metodológica:** achados com `n ≥ 30` sustentam o ranking principal; grupos
  menores aparecem separados como exploratórios. O pior grupo observado com `n=15`
  deixou de ser apresentado como conclusão operacional suportada.
- **Evidência:** o intervalo é calculado deterministicamente por estatísticas de ordem;
  amostras com menos de cinco observações não recebem falsa precisão.
- **Validação:** `61` testes de analytics e workflow passaram em `7,96 s`; Ruff,
  `py_compile` e `git diff --check` passaram.
- **Medição após a frente:** diagnóstico `9,5`, automação `7,7`, prova funcional `8,8`;
  média simples `8,7/10`. Crescimento: `+0,2`. O Goal ainda não foi atingido.

## I78 — Goal ≥ 9,5 · Frente 3: limite verificável da automação — 2026-09-22

- **Implementação:** a resposta executiva agora compara Customer e IT no mesmo quadro,
  sempre sobre o teste final congelado: amostra, macro-F1, ECE, limiar travado, cobertura,
  risco seletivo e decisão operacional.
- **Resultado Customer:** `n=231`, macro-F1 `13,94%`, ECE `3,28%` e cobertura `0%`;
  automação autônoma permanece bloqueada.
- **Resultado IT:** `n=5.301`, macro-F1 `83,51%`, ECE `4,14%`; no limiar travado de
  `0,55`, cobertura `37,43%` e risco seletivo `10,64%`. Como o risco supera o teto de
  `10%`, IT permanece em shadow com revisão humana; não houve ajuste pós-teste do limiar.
- **Escopo autorizado:** priorização, fila, classificação assistida e auditoria. Resposta
  externa, alteração de conta, reembolso e roteamento Customer autônomo ficam bloqueados.
- **Validação:** `45` testes de workflow passaram em `7,95 s`; Ruff, `py_compile` e
  `git diff --check` passaram. A tabela também foi conferida contra os JSONs congelados.
- **Medição após a frente:** diagnóstico `9,5`, automação `9,2`, prova funcional `9,0`;
  média simples `9,2/10`. Crescimento: `+0,5`. O Goal ainda não foi atingido.

## I79 — Goal ≥ 9,5 · Frente 4: impacto e contrato do piloto — 2026-09-22

- **Implementação do impacto:** os três cenários agora partem do contexto explícito do
  briefing, `~30.000 tickets/ano`, e mostram horas mensais e anuais. O custo continua
  indisponível até o Diretor informar uma premissa monetária.
- **Projeções, não economia realizada:** conservador `150 h/ano`; base `625 h/ano`;
  otimista `1.600 h/ano`. Fração endereçável e minutos poupados permanecem editáveis.
- **Contrato do piloto:** duas semanas, shadow, mínimo de `1.000` tickets estratificados,
  baseline do tempo manual e comparação de cada sugestão com a decisão humana; nenhuma
  alteração no helpdesk e nenhuma resposta automática.
- **Go/no-go cumulativo:** macro-F1 `≥75%`, recall por classe `≥65%`, ECE `≤5%`, risco
  seletivo `≤10%` com cobertura `≥20%`, zero escape sensível/crítico e redução `≥20%`
  no tempo mediano de triagem. Falhou um critério: mantém revisão humana e repete o piloto.
- **Validação:** `61` testes de analytics e workflow passaram em `8,21 s`; Ruff e
  `git diff --check` passaram.
- **Medição após a frente:** diagnóstico `9,5`, automação `9,5`, prova funcional `9,3`;
  média simples `9,4/10`. Crescimento: `+0,2`. O Goal ainda não foi atingido.

## I80 — Goal ≥ 9,5 · Frente 5: prova final e fechamento — 2026-09-22

- **Rastreabilidade:** READMEs e relatório de medição foram atualizados com a resposta
  executiva, confiabilidade, risco-cobertura, cenários e contrato do piloto.
- **Gate remoto:** no SHA de aplicação `1dddf03e3bc07464c2574ec43eb1b74f02fa9c2d`, o
  Codespace reproduziu `8.469` linhas Customer e `47.837` IT; `251` testes passaram em
  `23,23 s` e Ruff passou sem falhas.
- **Deploy público:** reboot iniciado às `21:44 UTC`; a aplicação concluiu após cerca de
  16 minutos sob redução de CPU. “Resposta ao Diretor” abriu como rota inicial.
- **Prova visual:** navegador confirmou `4.047,83 h`, `0% Customer`, macro-F1 IT
  `83,51%`, cobertura IT `37,43%`, risco `10,64%`, piloto de `1.000` tickets e todos os
  critérios go/no-go. Scorecard confirmou cobertura/IC95% e cenário base `625 h/ano`.
- **Medição final:** diagnóstico `9,6`, automação `9,5`, prova funcional `9,7`; média
  simples `9,6/10`. Crescimento total desde o baseline: `+1,6`. **Goal ≥9,5 atingido.**
- **Limite preservado:** nota é avaliação interna baseada na rubrica registrada, não nota
  prometida pelo avaliador. PR `#141` permanece aberto; não houve merge nem submissão final.

## I81 — Check de segurança: parecer inicial — 2026-09-22

- **Decisão do owner:** tratar segurança como checklist, primeiro com parecer completo e
  depois com correções isoladas, uma por vez.
- **Escopo auditado:** código, configuração, histórico Git da pasta e arquitetura pública;
  nenhum controle privado do provedor foi presumido.
- **Parecer:** risco alto para operação e aceitável somente como demo sanitizada. O app não
  possui login, cadastro, e-mail, API paga ou banco remoto; controles desses fluxos são
  não aplicáveis hoje, não “implementados”.
- **P0 encontrado:** qualquer visitante pode registrar decisões e exportar o SQLite
  compartilhado; não há autenticação/autorização servidor-side nem restrição por ator.
- **P0 encontrado:** `data/runtime/decisions.sqlite3` é efêmero, ignorado e sem backup ou
  restore testado. Artefatos podem ser reproduzidos; decisões humanas não.
- **Controles parciais existentes:** sanitização de PII, SQL parametrizado, schema fechado,
  validação de campos, UUID idempotente, escrita transacional e hashes de artefatos.
- **Segredos:** nenhum candidato encontrado no checkout ou na busca histórica por padrões
  conhecidos; resultado não é certificação porque `gitleaks` não está instalado.
- **Próxima correção recomendada:** autenticação servidor-side + autorização de mutações e
  export. Nenhum código foi alterado nesta fase de parecer.

## I82 — Segurança 01: autenticação e autorização fail-closed — 2026-09-22

- **Decisão:** preservar diagnóstico público para avaliação, mas exigir identidade OIDC
  autorizada para qualquer decisão, leitura do SQLite ou export.
- **Autorização:** comparação exata de `issuer` e `subject` contra allowlists server-side;
  e-mail e aliases não concedem acesso. Nenhum segredo ou token vai para o frontend.
- **Falha segura:** sem configuração OIDC, o produto permanece somente leitura; a página
  Evidências não inicializa o banco e nenhuma das quatro ações pode ser executada.
- **Higiene:** `.streamlit/secrets.toml` e arquivos `.env` passaram a ser ignorados; um
  exemplo sem credenciais documenta as chaves necessárias no cofre do provedor.
- **Regressão local:** `50` testes de workflow passaram em `7,23 s`; Ruff, `py_compile`
  e `git diff --check` passaram.
- **Pendente externo:** cadastrar cliente no IdP, guardar secrets no Streamlit Cloud e
  informar os `sub` autorizados. Nenhuma credencial foi criada ou inferida.
- **Publicação:** commit `0f98402c1108c5a65d3617a27b5edf9981ad2f58` enviado à branch
  da submissão e carregado por reboot explícito no Streamlit Community Cloud.
- **Prova no navegador:** a página executiva permaneceu pública; `/queue` exibiu o aviso
  de acesso somente leitura, desabilitou Aprovar, Editar e aprovar, Rejeitar e Escalonar,
  além dos campos de resposta e motivo; `/evidence` mostrou a mesma restrição e não
  expôs decisões persistidas nem o export operacional.
- **Gate remoto:** o preflight completo tentou usar exclusivamente
  `codespace-manager`, mas não obteve vaga no semáforo compartilhado após mais de seis
  minutos. Aplicou-se a válvula de congestionamento autorizada; o gate remoto não é
  declarado verde. Permanecem verdes os `50` testes locais e Ruff.
- **Limite operacional observado:** o Streamlit aplicou redução temporária de CPU durante
  o bootstrap; o sistema concluiu a reprodução e voltou a renderizar sem erro.

## I83 — OIDC adiado no protótipo público — 2026-09-22

- **Decisão:** não configurar o provedor OIDC antes da avaliação. Trata-se de um
  protótipo público; exigir login criaria atrito para o avaliador sem ampliar a prova
  central do desafio.
- **Compensação vigente:** o diagnóstico permanece público, mas toda mutação, leitura do
  banco de decisões e export operacional continua bloqueada em modo fail-closed.
- **Pendência explícita:** antes de qualquer uso operacional ou com dados reais, instalar
  `Authlib>=1.3.2`, cadastrar o cliente no IdP, guardar os segredos no cofre do deploy e
  preencher as allowlists exatas de `iss` e `sub`.
- **Provedor recomendado para a próxima fase:** Google Identity para poucos operadores ou
  contas Google Workspace; Microsoft Entra ID passa a ser preferível se a organização
  operar no Microsoft 365.
- **Limite:** esta decisão adia a ativação; não classifica autenticação como desnecessária
  nem autoriza liberar escrita anônima.

## I84 — Backup adiado sem estado operacional — 2026-09-22

- **Constatação:** sem OIDC configurado, nenhum visitante cria, lê ou exporta decisões; o
  teste de regressão comprova que o SQLite nem sequer é criado no modo anônimo.
- **Estado preservado:** o CSV demonstrativo é sanitizado e versionado no Git; os
  artefatos analíticos são reproduzíveis a partir das fontes públicas. Não há decisão
  operacional mutável no deploy que possa ser legitimamente chamada de backup.
- **Decisão:** não criar cópia de um SQLite efêmero e vazio. Isso adicionaria mecanismo
  sem dado recuperável e produziria uma garantia enganosa.
- **Bloqueador futuro:** OIDC e escrita operacional só podem ser ativados depois de mover
  decisões para armazenamento durável gerenciado, definir retenção, automatizar backups
  e executar um teste documentado de restauração.
- **Risco residual:** aceito apenas para o protótipo público e somente leitura; continua
  crítico para qualquer uso real.

## I85 — Segurança mínima: higiene de credenciais — 2026-09-22

- **Prioridade:** tratar somente controles indispensáveis ao protótipo. Login, cadastro,
  e-mail, banco remoto, cookies próprios, WAF, CAPTCHA e APIs pagas não existem e não
  justificam infraestrutura preventiva nesta fase.
- **Varredura atual:** nenhum padrão de token, chave privada, credencial cloud ou JWT foi
  encontrado no código, configuração ou diário do Challenge 002.
- **Varredura histórica:** a busca restrita ao Challenge 002 encontrou somente o commit
  que adicionou `.streamlit/secrets.example.toml`; inspeção confirmou placeholders
  `SET_IN_STREAMLIT_CLOUD`, sem valor secreto.
- **Falso positivo descartado:** a busca ampla inicialmente confundiu o trecho textual
  `task-...` do Challenge 004 com prefixo `sk-`; o achado não era credencial e estava fora
  do escopo.
- **Proteção vigente:** `.env`, `.env.*` e `.streamlit/secrets.toml` são ignorados; o
  exemplo versionado contém somente nomes e placeholders. Nenhuma reescrita de histórico
  é necessária.
- **Limite:** a prova é uma varredura por padrões conhecidos, não certificação por scanner
  especializado. Scanner dedicado passa a ser obrigatório se uma credencial real existir.

## I86 — Fechamento do hardening indispensável — 2026-09-22

- **Critério:** implementar agora somente controles que protegem uma superfície existente
  no protótipo; controles dependentes de login, escrita, dados reais, banco remoto, e-mail,
  senha, API paga ou domínio próprio permanecem gates condicionais.
- **Implementado/verificado:** autorização fail-closed, bloqueio de leitura/export de
  decisões, validação fechada contra adulteração e higiene de credenciais/histórico.
- **Adiado até existir operação:** rate limit de login, auditoria central, banco durável,
  backup/restore, RLS, criptografia gerenciada e validação de cookies autenticados.
- **Não aplicável:** cadastro/CAPTCHA, envio de e-mail/aliases, chave de banco e senha
  local. O frontend continua sem segredo.
- **Não justificado agora:** Cloudflare/WAF, Sentry e alertas de custo; não existe domínio
  próprio, tráfego operacional, API paga ou dado privado que compense complexidade e novo
  compartilhamento de telemetria.
- **Conclusão:** nenhum outro código de segurança é indispensável antes da avaliação. O
  sistema permanece aceitável somente como demonstração pública, sanitizada e sem escrita.

## I87 — Materiais finais consolidados — 2026-09-22

- **Decisão:** manter poucos arquivos e concentrar a entrada do avaliador no README.
- **Vídeo:** a gravação legendada do método construtivo foi preservada sem alteração de
  conteúdo e comprimida para `72 MB`, dentro do limite do GitHub.
- **Auditoria:** não foi encontrado vídeo demonstrativo nem Arcade específico do Challenge
  002; materiais de outros desafios não foram reutilizados como evidência.

## I88 — Pacote local organizado — 2026-09-22

- **Salvaguarda:** entregáveis e réplica funcional foram copiados para
  `~/Desktop/Challenge-002-Entrega-Final`.
- **Estrutura:** documentos e vídeos em `01-entregaveis`; código, dados, artefatos e testes
  em `02-sistema`; `.venv` e caches foram excluídos por serem reproduzíveis.
- **Verificação:** pacote com `136 MB`; os dois vídeos foram comparados byte a byte com as
  fontes. O arquivo `LEIA-ME.md` concentra links e instruções de execução.

## I89 — Entregáveis visuais obrigatórios — 2026-09-22

- **Correção de escopo:** a entrega não está completa sem materiais específicos do Challenge
  002 no NotebookLM e no Arcade; ativos dos Challenges 003 e 004 não serão reutilizados.
- **NotebookLM:** gerar vídeo explicativo, mapa mental e infográfico a partir de uma fonte
  consolidada da metodologia construtiva.
- **Arcade:** criar um wizard guiado do Support Decision Copilot, mostrando a resposta ao
  Diretor, o diagnóstico, a fila, o gate de risco e as evidências.
- **Formatos textuais:** entregar o mesmo resumo metodológico em Markdown, texto simples e
  DOCX, preservando leitura humana e ingestão por IA.

## I90 — Entregáveis NotebookLM e Arcade concluídos — 2026-09-22

- **NotebookLM:** criado o notebook `Challenge 002 — Support Decision Copilot | Construção
  e entrega` a partir da síntese metodológica consolidada.
- **Vídeo:** gerado e baixado o resumo explicativo em português brasileiro, com `6:42`,
  cobrindo método, evolução, métricas e limites do produto.
- **Mapa mental:** gerado e exportado com as oito etapas construtivas e o resultado final.
- **Infográfico:** a primeira geração foi rejeitada por erros de texto; uma segunda versão
  concisa foi gerada, inspecionada e aprovada.
- **Arcade:** publicado o wizard de quatro etapas com cenas e callouts para resposta ao
  Diretor, diagnóstico, automação segura e evidências/limites:
  `https://app.arcade.software/share/pn7KXHGNY23CVj5A2zHE`.
- **Verificação:** o link público carregou com o título correto; vídeo, mapa e infográfico
  foram baixados e validados localmente antes de integrar o pacote.
