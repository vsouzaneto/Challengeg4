# Spec 00 — O Início

**Rota:** `/#/inicio`
**Papel:** onboarding da demonstração; não é uma sétima lente analítica.

## Objetivo

Dar a um gestor, avaliador ou agente sem conhecimento técnico um ponto de partida único. A tela explica os dois datasets, o significado dos estados, a ordem da demonstração e os limites que precisam ser ditos em voz alta. Ela também registra, em primeira pessoa, o raciocínio de produto e as escolhas técnicas que levaram à solução. Ela não calcula métricas novas nem cria uma sessão.

## Conteúdo e ações

| Bloco | O que a pessoa entende/faz |
|---|---|
| Status do corpus | Confere que o catálogo carregou e vê as contagens verificadas de DS1 e DS2. |
| Linha de raciocínio | Conhece o caminho Hermes → prompt robusto → Codex → planejamento de specs/sprints → implementação, além das escolhas de linguagem, infraestrutura, NLP e modelo. |
| Execução local | Copia o comando do servidor, abre `http://127.0.0.1:8000/#/inicio` e entende como gerar o build e encerrar o processo. |
| Caminho recomendado | Percorre oito passos: corpus → diagnóstico → estratégia → ticket novo → Copilot → Graph → replay → limites. |
| Seis lentes | Abre cada rota com dataset e origem compatíveis, preservando o contexto global. |
| Como ler um resultado | Diferencia histórico, simulação, entrada manual, confiança, revisão humana e indisponibilidade. |

Os botões **Começar pelo diagnóstico** e **Testar um ticket** são atalhos; os cartões das seis lentes repetem os destinos com uma explicação curta. O comando local inicia a mesma API que serve o frontend compilado e mantém os dados derivados disponíveis para a demonstração.

## Limites comunicados

- A ordem e os horários do Live Replay são simulados, embora o texto venha dos arquivos.
- FRT/TTR permanecem indisponíveis porque falta uma data de abertura válida.
- O Graph é uma rede semântica de embeddings, não uma visualização dos neurônios do classificador.
- Confiança, similaridade, cluster e posição 2D são medidas diferentes.
- A demonstração não envia mensagens, fecha tickets, altera CSVs ou substitui revisão humana.
- A narrativa técnica é uma explicação do processo de desenvolvimento; os números de qualidade continuam sustentados pelos artefatos e testes registrados.

## Checkpoints

- [x] `INI-01`: rota carregada pelo shell, com dataset e sessão preservados na navegação.
- [x] `INI-02`: roteiro explica as seis lentes e a distinção entre dados observados, hipóteses e simulação.
- [x] `INI-03`: contagens vêm do catálogo compartilhado e ausência de catálogo não é tratada como métrica zero.
- [x] `INI-04`: links abrem destinos reais por teclado e o conteúdo não depende do Graph.
- [x] `INI-05`: narrativa em primeira pessoa explica Hermes, Codex, planejamento, stack, NLP, treinamento e política de revisão.
- [x] `INI-06`: card de execução local mostra comando, URL, build opcional e encerramento do servidor.
- [x] `INI-07`: card de checklist da entrevista removido sem deixar uma ação fictícia no onboarding.
- [x] `INI-08`: Graph informa clique para isolar, novo clique/fundo para restaurar e arraste individual dos nós.
- [ ] `INI-09`: ensaio dedicado em 320 CSS px, zoom 200% e leitor de tela.
