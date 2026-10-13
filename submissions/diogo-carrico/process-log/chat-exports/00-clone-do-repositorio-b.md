# Sessão 0b: clone do repositório

> Exportado do Claude Code e limpo automaticamente: chaves, tokens, e-mail e caminhos pessoais removidos; saídas de ferramentas, raciocínio interno e avisos do sistema omitidos. Cada ferramenta usada aparece numa linha, com a descrição que a IA deu ao chamá-la.


## Diogo · 2026-10-13 18:29

https://github.com/codessentia/ai-master-challenge clone this repository

## Claude

I'll clone the repository into the current working directory.

- _ferramenta: Bash — List directory and clone the repository_
- _ferramenta: Bash — Verify clone and list repository contents_
The repository is cloned to [ai-master-challenge/](ai-master-challenge/) and the working directory now points at it.

It contains a README, contributing guide, submission guide, a `challenges` folder with four challenges, and a `templates` folder. The latest commit switches submissions to pull requests only.


## Diogo · 2026-10-13 18:30

de uma revisada geral no que precisa ser feito.

## Claude

Vou ler o README, os guias e os quatro desafios para resumir o que precisa ser feito.

- _ferramenta: Bash — Read top-level docs and list challenge files_
- _ferramenta: Bash — Read challenge index and challenges 001 and 002_
- _ferramenta: Bash — Read challenges 003 and 004 and the submission template_
Li todos os arquivos do repositório. Resumo do que precisa ser feito, em português.

**O que é**

É o processo seletivo do G4 para a vaga de "AI Master". Você escolhe um dos quatro desafios, resolve usando IA, e entrega a solução mais a evidência do processo via Pull Request. Tempo sugerido: 4 a 6 horas.

**Os quatro desafios** (escolha um)

- **001 Churn** (Dados): cruzar 5 tabelas de uma SaaS fictícia e entregar um relatório com causa raiz do churn, segmentos em risco e ações priorizadas. Formato livre. Dados no Kaggle.
- **002 Suporte** (Operações): diagnosticar gargalos em 30K tickets, propor o que automatizar e o que não automatizar, e idealmente construir um protótipo que rode. Usa dois datasets do Kaggle.
- **003 Lead Scorer** (Vendas, build): construir uma ferramenta que rode de verdade com os dados reais de um CRM, com lógica de scoring explicável e interface que um vendedor use. Pede setup, lógica e limitações documentados.
- **004 Social Media** (Marketing): analisar 52K posts, comparar orgânico vs. patrocinado de forma justa, e entregar uma estratégia priorizada. Dashboard ou modelo preditivo como diferencial.

**Entrega obrigatória** (vale para todos)

1. A solução em si, dentro de `submissions/seu-nome/solution/`.
2. Um README seguindo [templates/submission-template.md](templates/submission-template.md), com executive summary, abordagem, resultados, recomendações e limitações.
3. **Process log** em `process-log/`: screenshots, exports de chat, git history ou narrativa mostrando quais ferramentas usou, onde a IA errou, o que você corrigiu e o que você adicionou. Sem isso a submissão é desclassificada.

**Como submeter**

1. Fork do repositório no GitHub (este clone aponta para o original, então o remote precisa trocar para o seu fork).
2. Branch `submission/seu-nome`.
3. Só mexer dentro de `submissions/seu-nome/`. Alterar qualquer outro arquivo rejeita o PR.
4. PR para `main` com título no formato `[Submission] Seu Nome — Challenge XXX`.

**O que eles avaliam de verdade**

O README avisa que já rodaram cada brief em Claude, GPT e Gemini como baseline. Uma resposta parecida com o que a IA produz sozinha não passa. Eles querem ver julgamento humano: dados cruzados e verificados, distinção entre correlação e causalidade, recomendações que alguém executa na segunda-feira, e um process log com iteração real, não um prompt único.

**Próximos passos sugeridos**

1. Escolher o desafio. Pelo índice: 001 ou 004 para quem é forte em dados, 002 para processos, 003 para quem constrói software.
2. Fazer o fork e ajustar o remote deste clone.
3. Baixar os dados do Kaggle do desafio escolhido.
4. Registrar o processo desde o início, porque a evidência é parte da nota.

