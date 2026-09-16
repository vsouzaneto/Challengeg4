# Estado atual

**15/09/2026 — fase de análise.**

## Onde paramos

Dhiego definiu que hoje é dedicado a entender o problema, tirar dúvidas e provocar a análise. Amanhã será dedicado à construção, depois de fechar o plano de solução.

**Próxima ação:** discutir a [análise preliminar de CX](solution/analise-preliminar-cx.md) com Dhiego: urgência versus criticidade, repetição de contato, pendência e qualidade da resposta. Apresentar um problema de cada vez e registrar suas perguntas e decisões antes de escolher solução.

## Concluído

- Auditoria integral dos dois CSVs e registro dos hashes.
- Exploração orientada às provocações de CX: cruzamentos descritivos, sinais textuais, identidade e inspeção de resoluções. Nenhuma inferência de causalidade ou churn.
- Qualidade separada por pergunta e sensibilidade à exclusão de identidade ambígua; ADR 0003. Motivos distintos de espera pelo cliente documentados como dado necessário, sem inferir sua frequência.
- Revisão crítica do plano inicial.
- Princípio de separar regras determinísticas de inferência por IA.
- Decisão de deixar flags avançadas, priorização e acompanhamento como propostas futuras.
- Organização do pacote inicial para Git, sem código ou dados empresariais privados.

## Aberto

- Entendimento do diagnóstico pelo candidato e escolha final da intervenção.
- Stack: FastAPI/Jinja/HTMX/Docker em discussão; Streamlit foi a proposta inicial. Banco e publicação ainda não definidos.
- Se existe tarefa útil que justifique LLM/OpenRouter; nenhuma chave foi configurada.
- Critérios de sucesso e política de encaminhamento.

## Ainda não realizado

Treinamento, avaliação de classificador, protótipo de produto, integração, deploy e submissão. O script de auditoria é código de análise.

## Retomada

Ler este arquivo → roadmap → process log → ADRs. Atualizar o estado após as decisões reais. Não tratar proposta como implementada.
