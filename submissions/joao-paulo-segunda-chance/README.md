# Submissão — João Paulo — Challenge 001 (Segunda Chance)

## Sobre mim

- **Nome:** João Paulo
- **LinkedIn:** https://www.linkedin.com/in/joao-pauloborges
- **Challenge escolhido:** Challenge 001 — Diagnóstico de Churn
- **Estado:** Site v10 publicado com login, gestão de usuários e permissões; aceitação do login e revisão visual concluídas em 13/10/2026. Entrega documentada nesta pasta.

## Executive Summary

Construí uma mesa de decisão para investigar churn, atualizar dados por CSV/Excel e acompanhar ações com evidências preservadas no Supabase. Na base histórica, identifiquei 36 contas com flag de churn sem cancelamento registrado, inconsistências temporais de uso e cobertura parcial de satisfação. Recomendo reconciliar essas contas por exposição contratual e validar telemetria e denominadores antes de orientar ações comerciais. O site reúne painel, investigação por conta, decisões, assistente executivo e gestão de usuários, com login e permissões.

**[Acessar o site](https://challenge-g4-ravenstack.early-hake-5665.chatgpt.site)** · [Aplicação e reprodução](web/README.md) · [Status e limites](docs/web_status.md) · [Diagnóstico executivo](solution/diagnostico_executivo.md).

## Leitura para a banca

1. [Diagnóstico executivo](solution/diagnostico_executivo.md): achados, motivos declarados, prioridades e limites.
2. [Roteiro de demonstração e reprodução](docs/reproduction.md): comandos, dependências, ordem de implantação e limites dos testes.
3. [Índice do process log](process-log/README.md): decisões, conversas de construção/revisão, evolução e evidências por etapa.
4. [Implementação da revisão](process-log/review_2026-10-13.md): mudanças e verificação desta rodada.

## Solução

### Abordagem

Preservei DDD, TDD, Clean Architecture, Bounded Contexts e Specifications da primeira entrega. Priorizei a reconciliação das cinco fontes e a definição dos indicadores antes da interface. Com apoio da IA, implementei contratos de dados, versões imutáveis, regras com estado indeterminado e decisões vinculadas a evidências. Ver [plano de implementação](docs/implementation_plan.md), [contratos de dados](docs/data_contracts.md) e [fundação implementada](docs/foundation_status.md).

### Resultados / Findings

Na base original, com corte em **31/12/2024**, encontrei três prioridades de investigação. A data de recebimento dos arquivos em 2026 não transforma esses fatos históricos em dados atuais.

| Achado | Evidência | Implicação para a decisão |
|---|---|---|
| Cadastro e cancelamentos não se reconciliam | Das 500 contas, 110 têm flag de churn; 36 dessas 110 não têm cancelamento registrado: 35 sem qualquer evento e uma apenas com reativação. | Reconciliar cadastro, eventos e contratos antes de atribuir motivo, data ou receita perdida. Os 22% de flags são proporção cadastral, não taxa mensal de churn. |
| Telemetria tem inconsistências temporais | 19.142 dos 25.000 registros de uso antecedem o início da assinatura; 21 IDs duplicados envolvem 42 linhas. | Validar a origem e a elegibilidade temporal antes de interpretar adoção ou desengajamento. |
| Satisfação tem cobertura parcial | Na janela elegível de 30 dias, média de 3,85/5 em 53 avaliações, para 88 tickets encerrados: cobertura de 60,2%. | Mostrar média e cobertura juntas; notas ausentes não equivalem a zero nem representam toda a carteira. |

As 36 contas a reconciliar somam **684.915 de MRR contratual**, na unidade da fonte, cuja moeda não foi informada. Esse valor orienta a ordem de investigação; não é perda prevista nem receita recuperável. FinTech e HealthTech concentram 20 dessas contas e 61,2% dessa exposição. O [diagnóstico executivo](solution/diagnostico_executivo.md) detalha os segmentos, motivos declarados, critérios e limitações.

Construí uma aplicação para transformar esses achados em investigação e acompanhamento:

| Entrega | O que permite fazer | Evidência e acesso |
|---|---|---|
| Painel e investigação de contas | Comparar cadastro, contratos, eventos, uso e suporte, com filtros, referência histórica e denominadores explícitos. | [Site publicado](https://challenge-g4-ravenstack.early-hake-5665.chatgpt.site/) · [Roteiro da banca](docs/reproduction.md) |
| Atualização por CSV/Excel | Inspecionar, mapear, validar e publicar uma fonte com prévia; preservar versões e histórico. Duas versões com os mesmos fatos demonstram a atualização sem perda da anterior. | [Contrato operacional](docs/web_status.md) · [Aceitação da importação](process-log/acceptance_2026-10-12.md) |
| Decisões e ações | Registrar decisões por conta, segmento, carteira ou qualidade, com evidência congelada, responsável, prazo e resultado. | [Escopos e evidências](docs/decision_scopes.md) |
| Assistente executivo | Consultar métricas calculadas no banco, com versão, definição, limitações e histórico privado por usuário. | [Arquitetura e operação](docs/assistant.md) |
| Acesso e gestão de usuários | Entrar por e-mail/senha e administrar perfis/permissões, com superadministrador protegido e cadastro sem convite por e-mail. | [Login](docs/authentication.md) · [Gestão de usuários](docs/user_management.md) |

As verificações de software, SQL e HTTP e a evolução das publicações estão no [process log](process-log/README.md#validação-por-etapa).

### Recomendações

1. **Dados + Financeiro: reconciliar as 36 contas com flag sem cancelamento.** Começar pela maior exposição contratual e conferir contratos, eventos e definição de churn por conta/assinatura. Registrar a conclusão e sua evidência antes de propor retenção ou contabilizar perda.
2. **Engenharia de Dados + Produto: validar a telemetria.** Investigar os 19.142 registros anteriores ao início da assinatura e os 21 IDs duplicados; definir elegibilidade e cobertura antes de usar variações de uso como sinal comercial.
3. **CS + Dados: revisar a cobertura de satisfação.** Validar datas e critérios de elegibilidade e acompanhar os 35 tickets elegíveis sem nota. Publicar sempre média, respondentes e denominador, sem extrapolar a amostra para todos os clientes.

O [plano no diagnóstico](solution/diagnostico_executivo.md) descreve responsáveis, entregas e cenário de capacidade. Impacto financeiro depende da reconciliação; não atribuí receita recuperável ou causa raiz sem evidência.

### Limitações

Uma maior data observada não comprova completude da extração. Ausência de histórico de mudança impede retroprojetar atributos, e ausência de vínculo entre churn e assinatura limita a atribuição de perda financeira. A auditoria é investigação inicial, não garantia de ausência de outros problemas.

### Estado da entrega

Site v10 publicado. Concluí a aceitação completa do login e a revisão visual em navegador/celular, incluindo o assistente executivo, em 13/10/2026. O estado das verificações técnicas e os limites de cada rodada estão no [process log](process-log/README.md). A nova PR da segunda chance parte do fork `amadojoao2/ai-master-challenge-segunda-chance`, branch `submission/joao-paulo-segunda-chance`, para a `main` de `Gestao-Quatro-Ponto-Zero/ai-master-challenge`.

## Process Log — Como usei IA

### Ferramentas usadas

| Ferramenta | Para que usou |
|---|---|
| ChatGPT / Codex | Revisão da PR anterior, planejamento, auditoria reproduzível, testes e documentação |

### Decisões sobre autenticação e modelos

A proposta inicial de login Google evoluiu para e-mail/senha pelo Supabase Auth, com provisionamento administrativo e permissões, permitindo cadastrar avaliadores de diferentes provedores. A evolução inclui uma fase intermediária de acesso livre, posteriormente encerrada. Cadastro sem convites por e-mail e permanência no plano Free foram decisões minhas.

Segundo meu relato, GPT-6.1 Sol Ultra foi priorizado em grande parte do desenvolvimento pela eficiência percebida em projetos anteriores e pelos limites disponíveis em minha conta ChatGPT Plus; Astra foi reservado para revisões finais e auditorias gerais. Não se trata de benchmark ou contabilidade completa de tokens. O assistente integrado à aplicação usa GPT-6 Luna. [Contexto e consequências das decisões](process-log/decisions_2026-10-13.md).

### Workflow

1. Ler a PR #66, comentários e critérios oficiais.
2. Retirar ML como diferencial e priorizar critérios verificáveis.
3. Verificar o projeto Supabase por consulta somente leitura.
4. Inspecionar as cinco fontes e ampliar a reconciliação anterior.
5. Escrever testes de domínio antes da implementação; observar falha inicial.
6. Implementar regras puras e auditoria exploratória; acrescentar testes de integração.
7. Executar auditoria e suíte; documentar a arquitetura e versionar o código no fork, sem PR.
8. Aplicar contratos e migrações, carregar fontes, testar permissões e publicar uma versão completa.
9. Implementar a fase inicial de acesso livre, site, importador e operações; comparar auditorias, validar publicação com rollback e publicar o site.
10. Ampliar escopos de decisão e substituir acesso livre por login autenticado, cuja aceitação concluí.
11. Reorganizar a visão executiva e integrar o assistente de consultas com histórico e evidências.
12. Revisar funcionamento, dados e UX/UI; implementar gestão de usuários e permissões.
13. Consolidar decisões, resultados e limites no process log antes da futura submissão.

### Onde a IA errou e como corrigi

Reforcei a diferença entre ausência de qualquer evento e ausência de evento de cancelamento. A auditoria passou a distinguir essas populações, incluindo contas que possuem apenas reativação. Também evita classificar automaticamente divergência entre histórico e cadastro como erro da fonte. Na fase web, o primeiro contrato de timestamp rejeitava datas sem horário presentes na fonte; foi alinhado ao contrato Python. O teste de nova versão revelou um plano SQL lento, corrigido com evidência de EXPLAIN e configuração restrita à função analítica.

### O que eu adicionei que a IA sozinha não faria

Defini que o site permitisse decisões e atualizações, retirei ML como diferencial, exigi continuidade dos princípios arquiteturais e reforcei a lacuna já encontrada na primeira tentativa. Também estabeleci versionamento contínuo no GitHub, com revisão somente quando a entrega estiver pronta.

## Evidências

- [Índice, conversas e validação por etapa](process-log/README.md).
- [Decisões de autenticação e utilização dos modelos](process-log/decisions_2026-10-13.md).
- [Registro parcial desta sessão](process-log/session_2026-10-12.md).
- [Implementação da fundação](process-log/foundation_2026-10-12.md).
- [Implementação web e resultados de testes](process-log/web_2026-10-12.md).
- [Aceitação efetiva, correções e evidências](process-log/acceptance_2026-10-12.md).
- [Implementação e aceitação dos escopos](process-log/decision_scopes_2026-10-12.md).
- [Implementação do login e limites de validação](process-log/authentication_2026-10-12.md).
- [Ativação do login e verificação dos bloqueios](process-log/authentication_activation_2026-10-12.md).
- [Reorganização do contexto da visão executiva](process-log/executive_layout_2026-10-12.md).
- [Implementação e validação do assistente](process-log/assistant_2026-10-12.md).
- [Revisão geral e correções](process-log/review_2026-10-13.md).
- [Gestão de usuários, permissões e senhas iniciais](process-log/user_management_2026-10-13.md).
- [Revisão documental para a banca](process-log/documentation_review_2026-10-13.md).
- [Segurança do assistente contra prompt injection](process-log/assistant_security_2026-10-13.md) e [validação do recorte explícito](process-log/assistant_filter_guard_2026-10-14.md).
- [Conferência dos requisitos oficiais](docs/submission_readiness.md).
- Scripts, testes com dados sintéticos e histórico de commits desta branch.
- Narrativa escrita, dados agregados, site publicado e histórico Git compõem as evidências da entrega.

## Reproduzir a auditoria

Requer Python 3.12. Obtenha as cinco fontes CSV do dataset especificado no [desafio oficial](../../challenges/data-001-churn/README.md) e coloque-as em uma pasta local. Para reproduzir os resultados de uma rodada específica, use os arquivos exatos identificados pelo manifesto daquela rodada.

```bash
python -m pip install -r requirements-audit.txt
python -m unittest discover -s tests -v
python scripts/audit_data.py --data-dir /caminho/para/os/csv --output-dir reports
```

O adaptador de auditoria usa pandas; o domínio não depende de pandas. Os relatórios gerados são ignorados pelo Git para evitar publicação acidental de IDs, linhas de origem e dados derivados. O código não modifica os arquivos de entrada.

_Atualizado em: 13/10/2026 (horário de Brasília)._

