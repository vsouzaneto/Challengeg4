# Estado atual

**15/09/2026 — fase de análise.**

## Onde paramos

Dhiego definiu que hoje é dedicado a entender o problema, tirar dúvidas e provocar a análise. Amanhã será dedicado à construção, depois de fechar o plano de solução.

**Pausa em 15/09:** análise visual v1 entregue, mas Dhiego ainda não teve oportunidade de lê-la. Não registrar como revisada ou aprovada, nem considerar F0 concluída. Retomar pela discussão dos dados antes de implementar. Meta pessoal de conclusão até 16/09; prazo oficial de entrega desconhecido.

**Próxima ação:** percorrer a [análise visual v1](solution/visual/index.html) com Dhiego: qualidade por pergunta, urgência, repetição de contato, pendência e exemplos de recap. Registrar suas perguntas e decisões antes de escolher solução.

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
- Stack: FastAPI/Jinja/HTMX/Docker em discussão; Streamlit foi a proposta inicial. Banco e publicação ainda não definidos.
- Se existe tarefa útil que justifique LLM/OpenRouter; nenhuma chave foi configurada.
- Critérios de sucesso e política de encaminhamento.
- Se o recap assistido merece entrar no recorte: há indícios de cadeias de email em alguns textos do D2, mas não mensagens estruturadas. Ver `solution/contexto-e-recap.md`. Sugestões de resposta exigem revisão; sem envio automático.

## Ainda não realizado

Treinamento, avaliação de classificador, protótipo de produto, integração, deploy e submissão. O script de auditoria é código de análise.

## Retomada

Ler este arquivo → roadmap → process log → ADRs. Atualizar o estado após as decisões reais. Não tratar proposta como implementada.

1. Abrir `solution/visual/index.html` no navegador. O arquivo está versionado e não depende de o servidor local da sessão anterior continuar rodando. Instruções em `solution/REPRODUZIR.md`.
2. Apresentar qualidade por pergunta, depois canais/pendências e exemplos de tickets; discutir um problema por vez com Dhiego.
3. Registrar dúvidas e conclusões. Separar evidência do dataset, hipótese e experiência anterior do candidato.
4. Escolher intervenção e como medir se funciona; só então definir stack e iniciar construção.

Análise visual registrada no commit `746f9fb`. Até esta pausa, os commits são locais; não houve push nem submissão de PR. Não retomar pesquisa de outros candidatos. Nenhuma tarefa de implementação foi deixada em execução autônoma.
