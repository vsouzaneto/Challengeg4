# Process log — percurso da segunda chance

Consolidado em 13/10/2026, horário de Brasília. Este índice reúne as decisões humanas, o uso de IA, as implementações, os problemas encontrados e as evidências da segunda submissão. Os registros de cada etapa conservam o estado observado quando foram escritos; as notas posteriores e este índice esclarecem o estado atual.

## Objetivo e decisões

A proposta evoluiu de uma auditoria do diagnóstico de churn para uma mesa de decisão: leitura executiva, investigação por conta, decisões com evidência, atualização por CSV/Excel e assistente de consultas. Retirei ML como diferencial, preservei os princípios de arquitetura da primeira entrega e exigi que as conclusões respeitassem as limitações das fontes.

As decisões sobre autenticação e distribuição dos modelos de IA estão em [Decisões de autenticação e uso dos modelos](decisions_2026-10-13.md). A implementação final usa e-mail/senha pelo Supabase Auth, gestão administrativa de usuários e permissões, sem convites por e-mail e mantendo o plano Free. O login das contas existentes foi integralmente aceito por mim em 13/10/2026.

## Conversas de desenvolvimento e revisão

Links fornecidos por mim em 13/10/2026:

- [Conversa de construção do projeto](https://chatgpt.com/share/6ace5036-066c-83e9-b0d3-5e354cafe70c).
- [Conversa de revisão do projeto](https://chatgpt.com/share/6acee7f6-8718-83ea-8307-90efcbc8dd47).

São links de compartilhamento do ChatGPT fornecidos por mim para a banca, substituindo os endereços internos das conversas. A disponibilidade e o conteúdo dos links não foram verificados nesta atualização. A narrativa e as evidências presentes no repositório permitem acompanhar o processo independentemente dos links; não se apresentam como export integral do chat.

## Etapas e evidências

| Ordem | Etapa | Entrega e registro |
|---|---|---|
| 1 | Reavaliação e auditoria | Leitura da PR anterior e do desafio; distinção entre ausência de qualquer evento e ausência de cancelamento; investigação das cinco fontes. [Registro inicial](session_2026-10-12.md). |
| 2 | Fundação de dados | Contratos, preservação de origem, normalização, versões, snapshots, imutabilidade e acesso. [Fundação](foundation_2026-10-12.md). |
| 3 | Aplicação web | Painel, detalhe de conta, importação com prévia, decisões e ações. [Implementação web](web_2026-10-12.md). |
| 4 | Aceitação de importação e ações | Publicação efetiva da segunda versão com os mesmos fatos; correção de mensagens e conflito SQL. [Aceitação](acceptance_2026-10-12.md) e [evidências](evidence/acceptance_results.json). |
| 5 | Escopos de decisão | Conta, segmento, carteira e qualidade; prévia e evidência congelada; recuperação de implantação. [Escopos](decision_scopes_2026-10-12.md) e [evidências](evidence/decision_scope_results.json). |
| 6 | Preparação de autenticação | SDK, identidade, autoria e bloqueio das rotas antigas. [Preparação](authentication_2026-10-12.md) e [evidências](evidence/authentication_results.json). |
| 7 | Ativação do login | Associação das duas contas reais, Site v6 e exigência de autenticação. [Ativação e aceite posterior](authentication_activation_2026-10-12.md) e [evidências](evidence/authentication_activation_results.json). |
| 8 | Organização da visão executiva | Contexto da versão e comparação antes dos filtros; Site v7. [Layout](executive_layout_2026-10-12.md). |
| 9 | Assistente de consultas | Consultas tipadas, histórico privado, limites e diagnóstico real do provedor; Site v8. [Assistente](assistant_2026-10-12.md) e [evidências](evidence/assistant_results.json). |
| 10 | Revisão geral | Recuperação de conexão, exploração de evidências, tickets, leitura executiva, legibilidade e diagnóstico; Site v9. [Revisão](review_2026-10-13.md). |
| 11 | Usuários e permissões | Superadministrador protegido, administrador, permissões, senha inicial e troca obrigatória; Site v10. [Gestão de usuários](user_management_2026-10-13.md). |
| 12 | Consolidação documental | Índice, decisões de autenticação/modelos, links das conversas e notas posteriores sobre login e formatos de evidência. Este índice e [decisões](decisions_2026-10-13.md). |
| 13 | Transferência para o fork oficial | Importação do histórico para o fork diretamente ligado à G4; referências aos commits originais e conteúdo conferido, conforme registro abaixo. |
| 14 | Revisão documental para a banca | Findings com dados, recomendações de negócio, narrativa em primeira pessoa, conclusão da revisão visual e preparação do acesso da banca. [Registro](documentation_review_2026-10-13.md). |
| 15 | Segurança do assistente | Separação entre instruções e dados, respostas fixas, fim da explicação livre e testes adversariais. [Registro](assistant_security_2026-10-13.md). |
| 16 | Conferência do recorte explícito | Comparação de setor/país escrito na pergunta com a consulta tipada antes do SQL; esclarecimento de divergências e nomes múltiplos. [Registro](assistant_filter_guard_2026-10-14.md). |

## Problemas encontrados e correções

Os registros detalham testes que falharam antes ou durante a implementação e a verificação após as correções. Exemplos relevantes:

- A interpretação inicial de churn não separava adequadamente ausência de eventos de ausência de cancelamento. A orientação humana levou à distinção das populações e à preservação do estado indeterminado.
- O parser web rejeitava datas sem horário presentes no suporte. Foi alinhado ao contrato Python; os 89 resultados de qualidade tiveram contagens e denominadores comparados.
- A materialização de uma versão recém-carregada apresentava plano SQL lento. A análise de EXPLAIN orientou ajustes restritos à função, preservando os fatos e o ponteiro ativo até a publicação.
- Um conflito de revisão usava SQLSTATE 40001 e gerava retries pelo PostgREST. Passou a usar PT409/HTTP 409, com novo teste e aceitação HTTP.
- Erros de ação ficavam atrás do modal e o detalhe de conta permanecia carregando após falhar. Testes de componentes reproduziram e confirmaram as correções.
- A implantação dos escopos falhou com erro interno. O empacotamento canônico em JavaScript foi aceito; a causa interna não foi presumida.
- A revisão final melhorou recuperação do assistente, filtros de exploração, tickets, denominadores e legibilidade. A gestão de usuários acrescentou autorização no servidor e remoção de dados não permitidos das respostas.

## Validação por etapa

As quantidades abaixo pertencem às respectivas rodadas. Não devem ser somadas como testes únicos: várias suítes foram ampliadas e reexecutadas ao longo do projeto. As 89 verificações de qualidade são resultados da auditoria e não representam a quantidade de testes de software.

| Etapa | Verificação registrada | Alcance |
|---|---|---|
| Auditoria inicial | 17 testes Python | Domínio/integração local com fontes sintéticas e auditoria das fontes fornecidas. |
| Fundação | 26 testes Python e guardas SQL | Contratos, publicação, idempotência, imutabilidade e acesso, conforme registro da etapa. |
| Aceitação web | 26 Python + 12 domínio web + 8 componentes | 46 testes dessas suítes; SQL/HTTP separados. Importação e ações QA exercitadas por HTTP real. |
| Escopos | 18 domínio web + 13 componentes + 4 adaptadores | Testes locais e SQL com rollback; leitura e gravação QA verificadas por HTTP. |
| Preparação do login | 20 domínio web + 17 componentes + 6 adaptadores | Auth/API simulados nos componentes; bloqueios reais por SQL/HTTP. |
| Login existente | Concluí a aceitação completa em 13/10/2026 | Aceitação após a ativação das contas existentes. |
| Layout executivo | 17 componentes + 6 adaptadores e builds | 23 testes; conferência de fonte, sem revisão visual real. |
| Assistente | 7 Specs + 20 componentes + 9 adaptadores | 36 testes JS nessa aceitação; SQL real com rollback e bloqueios HTTP. Diagnóstico do provedor: quatro respostas reais com fixture sintético; não é conversa integral de CEO. |
| Revisão geral | 26 Python + 27 domínio/referência web + 36 componentes/adaptadores | 89 testes aprovados, zero skips; comparação dos 89 resultados de qualidade com o banco. |
| Gestão de usuários | 47 componentes/adaptadores, SQL isolado e 4 guardas HTTP | Zero falhas/skips; SQL em PGlite local e preflight real com rollback. Cadastro/redefinição HTTP com conta legítima ainda não exercitados. |
| Conferência de filtros do assistente | 12 domínio + 47 componentes/adaptadores, TypeScript e pacote Edge | Divergências e nomes múltiplos bloqueiam SQL em testes simulados; gateway v8 ativo com JWT. Guardas HTTP anônimos verificados separadamente. |

Componentes em Happy DOM e adaptadores com API simulada não equivalem a navegador real. O SQL local de gestão de usuários cria somente identidades sintéticas em memória; suas fixtures não devem ser aplicadas no Supabase compartilhado. Comandos e dependências em [Reprodução](../docs/reproduction.md) e [Gestão de usuários](../docs/user_management.md).

## Estado e limites para a avaliação

- [Site v10 publicado](https://challenge-g4-ravenstack.early-hake-5665.chatgpt.site/), com login ativo; dados e duas versões publicadas preservados.
- Login das contas existentes concluído por meu aceite. Cadastro/redefinição e primeiro acesso do novo módulo ainda precisam de validação integral com conta legítima.
- Concluí a revisão visual em navegador/celular em 13/10/2026, incluindo o assistente. Os registros de testes automatizados mantêm o escopo de cada rodada; a revisão visual não amplia retroativamente a cobertura desses testes.
- Ausência de eventos ou telemetria não é automaticamente zero; exposição contratual não é perda prevista ou caixa; causa raiz e receita recuperável não são afirmadas sem evidência.
- Narrativa escrita e histórico Git são os formatos de evidência adotados. Screenshots, gravação e export integral são alternativas opcionais, conforme [conferência do guia](../docs/submission_readiness.md).
- Alterações restritas à pasta e branch da segunda chance. Aprovei a abertura da nova PR, com destino à `main` de `Gestao-Quatro-Ponto-Zero/ai-master-challenge`.

## Consolidação de 13/10/2026

Aprovei as mudanças documentais e forneci os links das conversas de construção e revisão. A atualização acrescenta este índice e o registro das decisões, completa o README e anota desdobramentos nos registros históricos sem substituir resultados observados na época. A comparação de eficiência entre modelos é atribuída ao meu relato, sem benchmark inventado ou medição retroativa de tokens.

A conferência desta rodada é documental: referências locais, consistência de estados e escopo dos arquivos no GitHub. Não representa nova execução dos testes de aplicação ou alteração da plataforma.

## Transferência para o fork oficial — 13/10/2026

O GitHub identificou o repositório anterior, `amadojoao2/ai-master-challenge`, como fork de `BarryBits/ai-master-challenge`. Sua base coincidia com a main oficial, mas a comparação entre redes retornava 404. Criei [amadojoao2/ai-master-challenge-segunda-chance](https://github.com/amadojoao2/ai-master-challenge-segunda-chance) diretamente de [Gestao-Quatro-Ponto-Zero/ai-master-challenge](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge) e incluí o novo fork no acesso da conexão GitHub.

A branch `submission/joao-paulo-segunda-chance` foi importada em 19 etapas. A API não aceitava referenciar os IDs do histórico anterior na nova rede; as etapas foram recriadas com IDs e datas de commit novos. Cada mensagem mantém referência ao commit original, autoria original e data original. Os commits originais continuam disponíveis no repositório anterior. Isso preserva a sequência de conteúdo sem apresentar os novos IDs como commits originais.

A primeira tentativa foi interrompida por limite de uso durante a revisão automática, antes da criação da branch. Na retomada, os arquivos já importados foram recuperados e o encadeamento foi reconstruído, com progresso salvo a cada etapa e publicação gradual da branch. Não houve alteração da aplicação ou do banco nesta transferência.

Antes deste registro documental, a árvore final de arquivos da importação, `03184a0412479399d2459b1ffcbee89249e1a99c`, era idêntica à do [último commit original](https://github.com/amadojoao2/ai-master-challenge/commit/0f75b87000594b5a3409df6ef5e75da6015ad6e4). Todas as 19 etapas usam as mesmas árvores de arquivos das etapas originais. A comparação real com a main oficial passou: 19 commits à frente, zero atrás e 144 arquivos exclusivamente em `submissions/joao-paulo-segunda-chance/`.

Este registro acrescenta um commit documental após as 19 etapas importadas. A [branch no fork oficial](https://github.com/amadojoao2/ai-master-challenge-segunda-chance/tree/submission/joao-paulo-segunda-chance) é o ponto de continuidade da segunda chance. A main dos repositórios e a PR anterior permanecem preservadas. Nenhuma nova PR foi aberta; o título planejado é `[Submission] João Paulo — Challenge 001 (Segunda Chance)` e sua abertura depende da minha aprovação.
