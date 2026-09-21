# Estado atual

**21/09/2026 — retomada; análise lida, solução em definição.**

## Onde paramos

Dhiego retomou e informou que leu toda a análise visual. A leitura está concluída; isso não implica concordância com todas as interpretações nem escolha de solução.

**Histórico:** pausa em 15/09 antes da leitura. A meta pessoal original de 16/09 passou; não houve nova data combinada. Prazo oficial de entrega continua desconhecido.

**Próxima ação:** discutir o [recorte proposto](docs/recorte-proposto.md), ouvir a interpretação de Dhiego e confrontar alternativas na revisão multimodelo antes da escolha final.

## Concluído

- Análise visual interativa gerada dos quatro relatórios, com fontes e limites explícitos. Identidade baseada nas referências oficiais do G4; navegação conferida em desktop e celular. Recaps preparados para discussão, sem inferência ao vivo.
- Auditoria integral dos dois CSVs e registro dos hashes.
- Exploração orientada às provocações de CX: cruzamentos descritivos, sinais textuais, identidade e inspeção de resoluções. Nenhuma inferência de causalidade ou churn.
- Qualidade separada por pergunta e sensibilidade à exclusão de identidade ambígua; ADR 0003. Motivos distintos de espera pelo cliente documentados como dado necessário, sem inferir sua frequência.
- Revisão crítica do plano inicial.
- Princípio de separar regras determinísticas de inferência por IA.
- Decisão de deixar flags avançadas, priorização e acompanhamento como propostas futuras.
- Organização do pacote inicial para Git, sem código ou dados empresariais privados.

## Aberto

- Entendimento do diagnóstico pelo candidato e escolha final da intervenção.
- Revisão com Claude, Grok e Codex solicitada por Dhiego: [protocolo proposto](docs/revisao-multimodelo.md). Prevista após discussão inicial e antes de fechar o escopo; acesso aos modelos ainda a verificar, sem execução nesta pausa.
- Stack: FastAPI/Jinja/HTMX/Docker em discussão; Streamlit foi a proposta inicial. Banco e publicação ainda não definidos.
- Se existe tarefa útil que justifique LLM/OpenRouter; nenhuma chave foi configurada.
- Critérios de sucesso e política de encaminhamento.
- Se o recap assistido merece entrar no recorte: há indícios de cadeias de email em alguns textos do D2, mas não mensagens estruturadas. Ver `solution/contexto-e-recap.md`. Sugestões de resposta exigem revisão; sem envio automático.

## Ainda não realizado

Treinamento, avaliação de classificador, protótipo de produto, integração, deploy e submissão. O script de auditoria é código de análise.

## Retomada

Ler este arquivo → roadmap → process log → ADRs. Atualizar o estado após as decisões reais. Não tratar proposta como implementada.

1. Consultar `docs/recorte-proposto.md`; a análise visual já foi lida por Dhiego e continua disponível em `solution/visual/index.html`.
2. Ouvir suas conclusões, dúvidas e prioridade de intervenção; executar a revisão multimodelo com o mesmo material.
3. Registrar divergências e conclusões. Separar evidência do dataset, hipótese e experiência anterior do candidato.
4. Escolher intervenção e como medir se funciona; só então definir stack e iniciar construção.

Análise visual registrada no commit `746f9fb`. Até esta pausa, os commits são locais; não houve push nem submissão de PR. Não retomar pesquisa de outros candidatos. Nenhuma tarefa de implementação foi deixada em execução autônoma.
