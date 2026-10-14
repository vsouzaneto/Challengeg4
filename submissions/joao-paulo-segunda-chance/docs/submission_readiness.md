# Conferência antes da futura submissão

Conferido no repositório oficial em 12/10/2026:
- [Challenge 001](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/challenges/data-001-churn/README.md), blob `ec1da6059e6a2dc535af8edefe27fd1680be86ee`.
- [Guia](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/submission-guide.md), blob `0e8cfc81719246bc05b485206292ab854892511c`.
- [Template](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/templates/submission-template.md), blob `f3f8c4c0185ba2d87fa1070fade521ec9abc5289`.
- [CONTRIBUTING](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/CONTRIBUTING.md), blob `2262c883e05cc023c5000d8d5cde20af72bf49df`.

| Critério | Evidência / situação |
|---|---|
| Diagnóstico executivo | `solution/diagnostico_executivo.md` e site. Explica diferenças demonstráveis; não inventa causa raiz. |
| Cruzamento das cinco fontes | Auditoria, joins por chaves, manifestos, snapshots e detalhe de conta. |
| Segmentos e contas identificáveis | Tabela no diagnóstico; filtro e detalhe no site com IDs. Ordenação por exposição contratual para investigação, sem risco previsto. |
| Ações concretas e impacto | Plano priorizado no diagnóstico; volumes observados e cenário de capacidade separados de impacto financeiro não identificável. |
| Correlação versus causalidade | Limites explícitos e resultado de ação sem atribuição causal automática. |
| Processo de IA | [Índice consolidado](../process-log/README.md), decisões de autenticação/modelos e referências às conversas de construção/revisão; registros por etapa, testes e commits. Links de compartilhamento do ChatGPT fornecidos por mim. |
| README oficial / setup | Seções do template e instruções Python, frontend, banco e Edge. |
| Alterações só na pasta | Conferir diff antes de qualquer PR; nenhum arquivo externo deve ser incluído. |
| Login | Concluí a aceitação completa em 13/10/2026. |
| Gestão de usuários | Site v10, permissões e proteção do proprietário implementados. Testes automatizados aprovados; cadastro/redefinição reais no navegador ainda não exercitados. [Guia](user_management.md). |
| Revisão geral | Correções funcionais e documentação: [registro](../process-log/review_2026-10-13.md). |
| Reprodução e demonstração | [Guia consolidado](reproduction.md), com testes locais separados das operações que gravam no ambiente. |
| Validação visual em navegador real | Concluí a revisão em navegador/celular em 13/10/2026, incluindo o assistente. [Registro](../process-log/documentation_review_2026-10-13.md). |
| Acesso da banca | [Comentário preparado](pr_access_comment.md), com site e login Raven; a senha vigente será publicada apenas no comentário da PR, conforme autorizado, sem ser versionada. |
| Nova PR da segunda chance | Abertura aprovada. Destino conferido: `Gestao-Quatro-Ponto-Zero/ai-master-challenge:main`, partindo de `amadojoao2/ai-master-challenge-segunda-chance:submission/joao-paulo-segunda-chance`; conferir o diff final. |

O modelo preditivo é um diferencial opcional. O guia aceita narrativa escrita e Git history; screenshot, gravação e export completo são formatos alternativos, não exigências cumulativas. Os logs não alegam ser export integral.

A especificação pede causas, segmentos e impacto. A resposta honesta identifica o que é demonstrável e o que não é identificável com as fontes; a engenharia do site não deve ser apresentada como substituto de evidência analítica.
